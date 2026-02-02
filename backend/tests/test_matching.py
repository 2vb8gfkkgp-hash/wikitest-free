from datetime import date

from app.models import Claim, Source, Interview
from app.services.matching import match_claim


def test_match_claim_scores_sources():
    claim = Claim(id=1, project_id=1, text="The city budget increased by 5% in 2023.")
    sources = [
        Source(
            id=1,
            project_id=1,
            url="https://example.com/report",
            title="City budget report",
            publisher="City Hall",
            author="Finance Dept",
            published_date=date.today(),
            source_type="report",
            notes="The budget increased by 5% in 2023 after council vote.",
        )
    ]
    interviews = [Interview(id=1, project_id=1, person="Mayor", transcript="Budget up by 5%.")]

    matches, flags = match_claim(claim, sources, interviews)
    assert matches
    assert flags == [] or "stale_sources" not in flags
    assert matches[0].match_score > 0
