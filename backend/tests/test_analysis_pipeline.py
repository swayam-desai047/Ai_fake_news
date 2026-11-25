from services.analysis_pipeline import analyze_article, extractive_summary

GOOD = ("Markets rally as inflation cools",
        "Stocks rose sharply on Wednesday after new data showed inflation easing for a third month. "
        "Analysts said the figures boost hopes of a rate cut. The index gained 2% in early trading, according to exchange data.",
        "Bloomberg")


def test_complete_analysis_with_models(fake_models):
    r = analyze_article(*GOOD)
    assert r["analysis_status"] == "complete"
    assert r["analysis_method"] == "model+rules"
    # sentiment dimension comes from the model (0.1 positive -> 10) and drives the label
    assert r["dimensions"]["sentiment"] == 10
    assert r["sentiment"] == "negative"
    assert r["model_fake_probability"] == 0.2
    assert r["confidence_level"] == 0.8
    assert r["risk_score"] is not None and 0 <= r["risk_score"] <= 1
    assert r["credibility_label"] in ("Low Risk", "Moderate Risk", "High Risk")
    assert "not a calibrated probability" in r["ai_reasoning"]
    assert "bert-tiny" in r["model_version"]


def test_rules_only_when_models_unavailable(no_models):
    r = analyze_article(*GOOD)
    assert r["analysis_status"] == "partial"
    assert r["analysis_method"] == "rules"
    assert r["confidence_level"] is None
    assert r["model_fake_probability"] is None
    assert r["is_fake"] is None and r["credibility_score"] is None
    assert r["risk_score"] is not None


def test_headline_only_is_unavailable_never_low_risk(fake_models):
    r = analyze_article("Markets fall", "", "Unknown Blog")
    assert r["risk_score"] is None
    assert r["credibility_label"] is None
    assert r["analysis_status"] == "unavailable"
    assert r["needs_verification"] is True


def test_low_model_confidence_flags_verification(fake_models):
    fake_models["fake_news"].scores = {"LABEL_0": 0.52, "LABEL_1": 0.48}
    r = analyze_article(*GOOD)
    assert r["needs_verification"] is True
    assert "classifier confidence" in r["ai_reasoning"]


def test_disagreement_flags_verification(fake_models):
    fake_models["fake_news"].scores = {"LABEL_0": 0.02, "LABEL_1": 0.98}
    r = analyze_article(*GOOD)
    assert r["needs_verification"] is True
    assert "disagree" in r["ai_reasoning"]


def test_risk_is_mean_of_rules_and_model(fake_models):
    from services.dimension_service import analyse_text
    rule = analyse_text(*GOOD)["credibility"]["score"]
    r = analyze_article(*GOOD)
    assert abs(r["risk_score"] - round((rule + 0.2) / 2, 2)) <= 0.01


def test_extractive_summary_needs_three_sentences():
    assert extractive_summary("One sentence that is long enough to count here.") is None
    text = ("The council approved the new budget on Monday after a long debate. "
            "The budget increases spending on schools and hospitals across the city. "
            "Opposition members said the plan would raise local taxes for families. "
            "The mayor said the budget was balanced and responsible.")
    s = extractive_summary(text)
    assert s and s.count(".") == 2
    assert all(sent.strip() in text for sent in s.split(". ") if sent)
