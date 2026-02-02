import re
from typing import List, Tuple

CLAIM_CATEGORIES = ["claim", "opinion", "background", "needs_evidence"]


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def detect_claim_type(sentence: str) -> str:
    lowered = sentence.lower()
    if re.search(r"\b\d+(?:\.\d+)?%|\$\d+|\b\d{1,3}(?:,\d{3})+\b", sentence):
        return "statistic"
    if re.search(r"\".+?\"|“.+?”|'.+?'", sentence) or "said" in lowered:
        return "quote"
    if re.search(r"\balleged|accused|suspected|claimed|allegedly\b", lowered):
        return "allegation"
    if re.search(r"\bmost|least|best|worst|largest|smallest|first|only\b", lowered):
        return "comparison"
    return "general"


def classify_sentence(sentence: str) -> Tuple[str, str]:
    claim_type = detect_claim_type(sentence)
    if re.search(r"\bI think|I believe|in my opinion|should\b", sentence, re.IGNORECASE):
        category = "opinion"
    elif re.search(r"\bbackground|history|context\b", sentence, re.IGNORECASE):
        category = "background"
    elif claim_type in {"statistic", "allegation", "comparison", "quote"}:
        category = "claim"
    else:
        category = "needs_evidence"
    return category, claim_type


def extract_claims(text: str) -> List[dict]:
    claims = []
    for sentence in split_sentences(text):
        category, claim_type = classify_sentence(sentence)
        claims.append({
            "text": sentence,
            "category": category,
            "claim_type": claim_type,
            "status": "needs_review",
            "confidence": 0.0,
        })
    return claims
