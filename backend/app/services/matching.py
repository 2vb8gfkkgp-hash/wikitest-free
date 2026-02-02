import math
import os
import re
from collections import Counter
from datetime import date
from typing import List, Optional, Tuple

from ..models import Claim, Source, Interview, ClaimSourceMatch

WORD_RE = re.compile(r"[a-zA-Z0-9%$']+")


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def tf(tokens: List[str]) -> Counter:
    return Counter(tokens)


def idf(documents: List[List[str]]) -> dict:
    N = len(documents)
    df = Counter()
    for doc in documents:
        df.update(set(doc))
    return {term: math.log((1 + N) / (1 + count)) + 1 for term, count in df.items()}


def tfidf_vector(tokens: List[str], idf_map: dict) -> dict:
    term_freq = tf(tokens)
    return {term: count * idf_map.get(term, 0.0) for term, count in term_freq.items()}


def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    common = set(vec_a) & set(vec_b)
    numerator = sum(vec_a[t] * vec_b[t] for t in common)
    denom_a = math.sqrt(sum(v * v for v in vec_a.values()))
    denom_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return numerator / (denom_a * denom_b)


def keyword_overlap(tokens_a: List[str], tokens_b: List[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    overlap = len(set(tokens_a) & set(tokens_b))
    return overlap / max(len(set(tokens_a)), 1)


def highlight_overlap(text: str, overlap_terms: List[str]) -> str:
    highlighted = text
    for term in sorted(set(overlap_terms), key=len, reverse=True):
        highlighted = re.sub(rf"\b({re.escape(term)})\b", r"**\1**", highlighted, flags=re.IGNORECASE)
    return highlighted


def build_match(claim: Claim, source: Optional[Source] = None, interview: Optional[Interview] = None) -> Tuple[ClaimSourceMatch, float, List[str]]:
    content = ""
    if source:
        content = " ".join(filter(None, [source.title, source.notes, source.excerpts]))
    if interview:
        content = " ".join(filter(None, [interview.transcript, interview.extracted_quotes]))

    claim_tokens = tokenize(claim.text)
    content_tokens = tokenize(content)
    idf_map = idf([claim_tokens, content_tokens])
    claim_vec = tfidf_vector(claim_tokens, idf_map)
    content_vec = tfidf_vector(content_tokens, idf_map)
    similarity = cosine_similarity(claim_vec, content_vec)
    overlap_score = keyword_overlap(claim_tokens, content_tokens)
    score = (similarity * 0.7) + (overlap_score * 0.3)

    overlap_terms = list(set(claim_tokens) & set(content_tokens))
    overlap_preview = highlight_overlap(content[:400], overlap_terms)

    match = ClaimSourceMatch(
        claim_id=claim.id,
        source_id=source.id if source else None,
        interview_id=interview.id if interview else None,
        match_score=round(score, 3),
        overlap=overlap_preview,
        needs_review=score < 0.35,
    )
    return match, score, overlap_terms


def match_claim(claim: Claim, sources: List[Source], interviews: List[Interview]) -> Tuple[List[ClaimSourceMatch], List[str]]:
    # TODO: Add optional embeddings similarity if an embeddings provider is configured.
    matches = []
    scored: List[Tuple[ClaimSourceMatch, float]] = []
    for source in sources:
        match, score, _ = build_match(claim, source=source)
        scored.append((match, score))
    for interview in interviews:
        match, score, _ = build_match(claim, interview=interview)
        scored.append((match, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    matches = [item[0] for item in scored[:3]]

    flags = []
    if not matches:
        flags.append("no_sources_found")
    if len(matches) == 1 and matches[0].match_score < 0.5:
        flags.append("only_one_weak_source")

    stale_years = int(os.getenv("STALE_YEARS", "5"))
    cutoff = date.today().replace(year=date.today().year - stale_years)
    for source in sources:
        if source.published_date and source.published_date < cutoff and not source.is_historical:
            flags.append("stale_sources")
            break

    if any(source.author is None or source.author == "" for source in sources):
        flags.append("sources_missing_author")
    if any(source.published_date is None for source in sources):
        flags.append("sources_missing_date")

    return matches, flags


def confidence_explanation(match_score: float) -> str:
    if match_score > 0.75:
        return "High overlap on key terms and phrasing."
    if match_score > 0.5:
        return "Moderate overlap on key terms; review context carefully."
    if match_score > 0.3:
        return "Weak overlap; likely needs additional evidence."
    return "Minimal overlap; claim likely unsupported."
