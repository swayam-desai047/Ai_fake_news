import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Tests never download model weights or start the background scheduler.
os.environ.setdefault("ENABLE_SCHEDULER", "0")

from fastapi.testclient import TestClient  # noqa: E402

from services import ai_service  # noqa: E402


class FakePipeline:
    """Stands in for a transformers pipeline; returns fixed label scores."""

    def __init__(self, scores, raises=False):
        self.scores = scores
        self.raises = raises
        self.calls = []

    def __call__(self, text, **kwargs):
        self.calls.append((text, kwargs))
        if self.raises:
            raise RuntimeError("boom")
        return [[{"label": k, "score": v} for k, v in self.scores.items()]]


@pytest.fixture
def fake_models():
    """Install fake classifier (LABEL_1 = fake) and sentiment pipelines."""
    pipes = {
        "fake_news": FakePipeline({"LABEL_0": 0.8, "LABEL_1": 0.2}),
        "sentiment": FakePipeline({"POSITIVE": 0.1, "NEGATIVE": 0.9}),
    }
    ai_service.reset_for_tests(pipes)
    yield pipes
    ai_service.reset_for_tests()


@pytest.fixture
def no_models():
    ai_service.reset_for_tests(errors={"fake_news": "not installed", "sentiment": "not installed"})
    yield
    ai_service.reset_for_tests()


@pytest.fixture
def client():
    from main import app
    return TestClient(app)
