import json
from typing import List

from ..models import Claim, ClaimSourceMatch


def to_markdown(claims: List[Claim], matches: List[ClaimSourceMatch]) -> str:
    lines = ["# NewsroomKit Evidence Report", ""]
    match_map = {}
    for match in matches:
        match_map.setdefault(match.claim_id, []).append(match)

    for claim in claims:
        lines.append(f"## Claim {claim.id}")
        lines.append(claim.text)
        lines.append("")
        for match in match_map.get(claim.id, []):
            source_label = f"Source {match.source_id}" if match.source_id else f"Interview {match.interview_id}"
            lines.append(f"- {source_label} (score {match.match_score:.2f})")
            if match.overlap:
                lines.append(f"  - Overlap: {match.overlap}")
        lines.append("")
    return "\n".join(lines)


def to_json(claims: List[Claim], matches: List[ClaimSourceMatch]) -> str:
    data = {
        "claims": [
            {
                "id": claim.id,
                "text": claim.text,
                "category": claim.category,
                "status": claim.status,
                "confidence": claim.confidence,
            }
            for claim in claims
        ],
        "matches": [
            {
                "claim_id": match.claim_id,
                "source_id": match.source_id,
                "interview_id": match.interview_id,
                "match_score": match.match_score,
                "overlap": match.overlap,
            }
            for match in matches
        ],
    }
    return json.dumps(data, indent=2)
