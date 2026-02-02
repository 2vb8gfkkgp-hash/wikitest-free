from datetime import date
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Claim, ClaimSourceMatch, Draft, EthicsChecklist, Interview, Project, Source
from .schemas import (
    Claim as ClaimSchema,
    ClaimCreate,
    ClaimExtractionResponse,
    Draft as DraftSchema,
    DraftUpdate,
    EvidenceReport,
    Interview as InterviewSchema,
    InterviewCreate,
    MatchResponse,
    Project as ProjectSchema,
    ProjectCreate,
    SearchResponse,
    Source as SourceSchema,
    SourceCreate,
    EthicsChecklist as EthicsChecklistSchema,
    EthicsChecklistUpdate,
)
from .services.claim_extraction import extract_claims
from .services.exporter import to_json, to_markdown
from .services.matching import confidence_explanation, match_claim
from .services.search import rate_limiter, search_web

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NewsroomKit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.get("/projects", response_model=List[ProjectSchema])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.post("/projects", response_model=ProjectSchema)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    checklist = EthicsChecklist(project_id=project.id)
    db.add(checklist)
    db.commit()
    return project


@app.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/projects/{project_id}/draft", response_model=DraftSchema)
def get_draft(project_id: int, db: Session = Depends(get_db)):
    draft = db.query(Draft).filter(Draft.project_id == project_id).first()
    if not draft:
        draft = Draft(project_id=project_id, content="")
        db.add(draft)
        db.commit()
        db.refresh(draft)
    return draft


@app.put("/projects/{project_id}/draft", response_model=DraftSchema)
def update_draft(project_id: int, payload: DraftUpdate, db: Session = Depends(get_db)):
    draft = db.query(Draft).filter(Draft.project_id == project_id).first()
    if not draft:
        draft = Draft(project_id=project_id, content=payload.content or "")
        db.add(draft)
    else:
        draft.content = payload.content or ""
    db.commit()
    db.refresh(draft)
    return draft


@app.get("/projects/{project_id}/sources", response_model=List[SourceSchema])
def list_sources(project_id: int, db: Session = Depends(get_db)):
    return db.query(Source).filter(Source.project_id == project_id).all()


@app.post("/projects/{project_id}/sources", response_model=SourceSchema)
def create_source(project_id: int, payload: SourceCreate, db: Session = Depends(get_db)):
    source = Source(project_id=project_id, **payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@app.get("/projects/{project_id}/interviews", response_model=List[InterviewSchema])
def list_interviews(project_id: int, db: Session = Depends(get_db)):
    return db.query(Interview).filter(Interview.project_id == project_id).all()


@app.post("/projects/{project_id}/interviews", response_model=InterviewSchema)
def create_interview(project_id: int, payload: InterviewCreate, db: Session = Depends(get_db)):
    interview = Interview(project_id=project_id, **payload.model_dump())
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@app.get("/projects/{project_id}/claims", response_model=List[ClaimSchema])
def list_claims(project_id: int, db: Session = Depends(get_db)):
    return db.query(Claim).filter(Claim.project_id == project_id).all()


@app.post("/projects/{project_id}/claims", response_model=ClaimSchema)
def create_claim(project_id: int, payload: ClaimCreate, db: Session = Depends(get_db)):
    claim = Claim(project_id=project_id, **payload.model_dump())
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@app.put("/claims/{claim_id}", response_model=ClaimSchema)
def update_claim(claim_id: int, payload: ClaimCreate, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    for key, value in payload.model_dump().items():
        setattr(claim, key, value)
    db.commit()
    db.refresh(claim)
    return claim


@app.post("/projects/{project_id}/extract-claims", response_model=ClaimExtractionResponse)
def extract_claims_endpoint(project_id: int, db: Session = Depends(get_db)):
    draft = db.query(Draft).filter(Draft.project_id == project_id).first()
    if not draft or not draft.content:
        raise HTTPException(status_code=400, detail="Draft is empty")
    claim_ids = [claim.id for claim in db.query(Claim.id).filter(Claim.project_id == project_id).all()]
    if claim_ids:
        db.query(ClaimSourceMatch).filter(ClaimSourceMatch.claim_id.in_(claim_ids)).delete()
    db.query(Claim).filter(Claim.project_id == project_id).delete()
    claims_payload = extract_claims(draft.content)
    claims = []
    for item in claims_payload:
        claim = Claim(project_id=project_id, **item)
        db.add(claim)
        claims.append(claim)
    db.commit()
    for claim in claims:
        db.refresh(claim)
    return ClaimExtractionResponse(claims=claims)


@app.post("/projects/{project_id}/match-claims", response_model=List[MatchResponse])
def match_claims(project_id: int, db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.project_id == project_id).all()
    sources = db.query(Source).filter(Source.project_id == project_id).all()
    interviews = db.query(Interview).filter(Interview.project_id == project_id).all()

    responses = []
    for claim in claims:
        db.query(ClaimSourceMatch).filter(ClaimSourceMatch.claim_id == claim.id).delete()
        matches, flags = match_claim(claim, sources, interviews)
        for match in matches:
            db.add(match)
        claim.confidence = max([m.match_score for m in matches], default=0.0)
        claim.status = "supported" if claim.confidence > 0.75 else "weakly_supported" if claim.confidence > 0.4 else "unsupported"
        db.commit()
        for match in matches:
            db.refresh(match)
        responses.append(MatchResponse(claim_id=claim.id, matches=matches, flags=flags))
    return responses


@app.get("/projects/{project_id}/report", response_model=EvidenceReport)
def get_report(project_id: int, db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.project_id == project_id).all()
    matches = db.query(ClaimSourceMatch).join(Claim).filter(Claim.project_id == project_id).all()

    items = []
    for claim in claims:
        claim_matches = [m for m in matches if m.claim_id == claim.id]
        explanation = confidence_explanation(claim.confidence)
        items.append({"claim": claim, "matches": claim_matches, "confidence_explanation": explanation})

    return EvidenceReport(project_id=project_id, items=items)


@app.get("/projects/{project_id}/export/markdown")
def export_markdown(project_id: int, db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.project_id == project_id).all()
    matches = db.query(ClaimSourceMatch).join(Claim).filter(Claim.project_id == project_id).all()
    return {"markdown": to_markdown(claims, matches)}


@app.get("/projects/{project_id}/export/json")
def export_json(project_id: int, db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.project_id == project_id).all()
    matches = db.query(ClaimSourceMatch).join(Claim).filter(Claim.project_id == project_id).all()
    return {"json": to_json(claims, matches)}


@app.get("/projects/{project_id}/checklist", response_model=EthicsChecklistSchema)
def get_checklist(project_id: int, db: Session = Depends(get_db)):
    checklist = db.query(EthicsChecklist).filter(EthicsChecklist.project_id == project_id).first()
    if not checklist:
        checklist = EthicsChecklist(project_id=project_id)
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
    return checklist


@app.put("/projects/{project_id}/checklist", response_model=EthicsChecklistSchema)
def update_checklist(project_id: int, payload: EthicsChecklistUpdate, db: Session = Depends(get_db)):
    checklist = db.query(EthicsChecklist).filter(EthicsChecklist.project_id == project_id).first()
    if not checklist:
        checklist = EthicsChecklist(project_id=project_id)
        db.add(checklist)
    for key, value in payload.model_dump().items():
        setattr(checklist, key, value)
    db.commit()
    db.refresh(checklist)
    return checklist


@app.get("/search", response_model=SearchResponse)
def search_sources(query: str, request: Request):
    client = request.client.host if request.client else "anonymous"
    if not rate_limiter.check(client):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    mode, results = search_web(query)
    return SearchResponse(query=query, results=results, mode=mode)


@app.post("/projects/{project_id}/import-source", response_model=SourceSchema)
def import_source(project_id: int, payload: SourceCreate, db: Session = Depends(get_db)):
    source = Source(project_id=project_id, **payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@app.post("/tools/clarity")
def clarity_tool(text: str):
    sentences = text.split(".")
    simplified = [s.strip().capitalize() for s in sentences if s.strip()]
    return {"result": ". ".join(simplified) + ("." if simplified else "")}


@app.post("/tools/tone")
def tone_tool(text: str, tone: str = "news"):
    return {"result": f"[{tone.upper()} TONE] {text}"}


@app.post("/tools/headline")
def headline_tool(text: str):
    words = text.split()
    headline = " ".join(words[:8]) + ("..." if len(words) > 8 else "")
    return {"headline": headline or "Draft headline", "subheading": "Add context and sourcing."}


@app.post("/tools/structure")
def structure_tool(text: str):
    return {
        "suggestions": {
            "hook": "Start with a compelling fact or scene from your sources.",
            "nut_graf": "Explain why the topic matters for your audience.",
            "transitions": "Use signposts between paragraphs to guide readers.",
            "ending": "Close with the latest verified detail or next steps.",
        }
    }
