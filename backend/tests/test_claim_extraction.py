from app.services.claim_extraction import extract_claims


def test_extract_claims_classifies_sentences():
    text = "The school has 1,200 students. I think uniforms help. The largest class is 30." 
    claims = extract_claims(text)
    assert len(claims) == 3
    assert claims[0]["claim_type"] == "statistic"
    assert claims[1]["category"] == "opinion"
    assert claims[2]["claim_type"] == "comparison"
