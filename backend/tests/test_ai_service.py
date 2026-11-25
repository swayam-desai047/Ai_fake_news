from services import ai_service
from tests.conftest import FakePipeline


def test_label_1_is_read_as_fake(fake_models):
    fake_models["fake_news"].scores = {"LABEL_0": 0.1, "LABEL_1": 0.9}
    r = ai_service.classify_fake_news("Some text")
    assert r["status"] == "ok"
    assert r["fake_probability"] == 0.9
    assert r["predicted_label"] == "fake"
    assert r["confidence"] == 0.9


def test_label_0_is_read_as_real(fake_models):
    r = ai_service.classify_fake_news("Some text")
    assert r["fake_probability"] == 0.2
    assert r["predicted_label"] == "real"
    assert r["confidence"] == 0.8


def test_truncation_is_requested(fake_models):
    ai_service.classify_fake_news("word " * 5000)
    _, kwargs = fake_models["fake_news"].calls[-1]
    assert kwargs == {"truncation": True, "max_length": 512}


def test_empty_input_is_unavailable_not_neutral(fake_models):
    r = ai_service.classify_fake_news("   ")
    assert r["status"] == "unavailable"
    assert r["fake_probability"] is None
    s = ai_service.classify_sentiment("")
    assert s["status"] == "unavailable" and s["positive_probability"] is None


def test_model_load_failure_returns_unavailable(no_models):
    r = ai_service.classify_fake_news("Some text")
    assert r["status"] == "unavailable"
    assert r["fake_probability"] is None
    assert r["error"]


def test_inference_error_is_handled():
    ai_service.reset_for_tests({"fake_news": FakePipeline({}, raises=True)})
    try:
        r = ai_service.classify_fake_news("text")
        assert r["status"] == "unavailable" and r["error"] == "Inference failed."
    finally:
        ai_service.reset_for_tests()


def test_unexpected_labels_are_rejected():
    ai_service.reset_for_tests({"fake_news": FakePipeline({"FOO": 0.7, "BAR": 0.3})})
    try:
        r = ai_service.classify_fake_news("text")
        assert r["status"] == "unavailable"
        assert "Unexpected model labels" in r["error"]
    finally:
        ai_service.reset_for_tests()


def test_sentiment_is_separate_from_fake_news(fake_models):
    s = ai_service.classify_sentiment("A terrible disaster")
    assert s == {"status": "ok", "positive_probability": 0.1, "error": None}


def test_prepare_text_joins_and_limits():
    assert ai_service.prepare_text("Title", "Body  text") == "Title. Body text"
    assert len(ai_service.prepare_text("t", "x" * 50_000)) == ai_service.MAX_INPUT_CHARS
