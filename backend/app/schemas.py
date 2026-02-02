from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    title: str
    topic: str
    audience: Optional[str] = None
    deadline: Optional[date] = None
    owner_id: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class DraftUpdate(BaseModel):
    content: Optional[str] = None


class Draft(BaseModel):
    id: int
    content: Optional[str] = None

    class Config:
        from_attributes = True


class SourceBase(BaseModel):
    url: str
    title: str
    publisher: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[date] = None
    source_type: str = Field(..., description="news/report/study/blog/interview")
    notes: Optional[str] = None
    excerpts: Optional[str] = None
    is_primary: bool = False
    is_historical: bool = False


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    id: int

    class Config:
        from_attributes = True


class InterviewBase(BaseModel):
    person: str
    role: Optional[str] = None
    interview_date: Optional[date] = None
    transcript: Optional[str] = None
    extracted_quotes: Optional[str] = None


class InterviewCreate(InterviewBase):
    pass


class Interview(InterviewBase):
    id: int

    class Config:
        from_attributes = True


class ClaimBase(BaseModel):
    text: str
    category: str = "claim"
    claim_type: Optional[str] = None
    status: str = "needs_review"
    confidence: float = 0.0
    notes: Optional[str] = None


class ClaimCreate(ClaimBase):
    pass


class Claim(ClaimBase):
    id: int

    class Config:
        from_attributes = True


class ClaimSourceMatch(BaseModel):
    id: int
    claim_id: int
    source_id: Optional[int] = None
    interview_id: Optional[int] = None
    match_score: float
    overlap: Optional[str] = None
    needs_review: bool

    class Config:
        from_attributes = True


class EthicsChecklistBase(BaseModel):
    right_of_reply: bool = False
    separate_fact_opinion: bool = False
    avoid_sensational: bool = False
    quote_integrity: bool = False


class EthicsChecklistUpdate(EthicsChecklistBase):
    pass


class EthicsChecklist(EthicsChecklistBase):
    id: int

    class Config:
        from_attributes = True


class ClaimExtractionResponse(BaseModel):
    claims: List[Claim]


class MatchResponse(BaseModel):
    claim_id: int
    matches: List[ClaimSourceMatch]
    flags: List[str]


class EvidenceItem(BaseModel):
    claim: Claim
    matches: List[ClaimSourceMatch]
    confidence_explanation: str


class EvidenceReport(BaseModel):
    project_id: int
    items: List[EvidenceItem]


class SearchResult(BaseModel):
    title: str
    url: str
    domain: str
    snippet: str
    published_date: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    mode: str
