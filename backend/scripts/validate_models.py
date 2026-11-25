"""
Check the two transformer models on hand-picked examples and print their raw outputs.

Usage (from the backend directory; downloads ~300 MB of weights on first run):
    python -m scripts.validate_models

It prints the raw label scores for each example so the fake/real label mapping
(FAKE_NEWS_FAKE_LABEL, default LABEL_1) can be confirmed by eye, and reports how many examples
match their expected label. The examples are illustrative, not a benchmark: no accuracy figure
from this script should be reported as model performance.
"""
import json

from services import ai_service

FAKE_NEWS_EXAMPLES = [
    # (text, expected) — style-typical examples; the model was trained on full-length articles.
    ("WASHINGTON (Reuters) - The U.S. Senate on Tuesday passed a bill to fund the government through "
     "December, sending the measure to the House, congressional aides said.", "real"),
    ("BREAKING: Obama secretly signed an order to confiscate every gun in America before leaving office, "
     "insiders reveal. The liberal media will never tell you this SHOCKING truth! Share before it is deleted!", "fake"),
    ("LONDON (Reuters) - British inflation rose to 3.1 percent in November, the Office for National "
     "Statistics said on Wednesday, the highest rate in almost six years.", "real"),
    ("You won't believe what Hillary was caught doing on camera - the video that the mainstream media "
     "is desperately trying to hide from the American people!", "fake"),
]
SENTIMENT_EXAMPLES = [
    ("The rescue team saved all the passengers and the community celebrated their bravery.", "positive"),
    ("The earthquake destroyed hundreds of homes and left thousands without shelter.", "negative"),
]


def main() -> None:
    hits = 0
    print(f"Fake-news model: {ai_service.FAKE_NEWS_MODEL} (fake label = {ai_service.FAKE_LABEL})")
    pipe = ai_service._load("fake_news")
    if pipe is None:
        print("Model unavailable:", ai_service.model_status())
        return
    for text, expected in FAKE_NEWS_EXAMPLES:
        raw = ai_service._run(pipe, text)
        res = ai_service.classify_fake_news(text)
        hits += res["predicted_label"] == expected
        print(json.dumps({"expected": expected, "predicted": res["predicted_label"], "raw_scores": raw}), "\n ", text[:90])
    print(f"Fake-news examples matching expectation: {hits}/{len(FAKE_NEWS_EXAMPLES)}")
    print("If most examples are inverted, set FAKE_NEWS_FAKE_LABEL=LABEL_0 and FAKE_NEWS_REAL_LABEL=LABEL_1.\n")

    s_hits = 0
    for text, expected in SENTIMENT_EXAMPLES:
        res = ai_service.classify_sentiment(text)
        got = "positive" if (res["positive_probability"] or 0) >= 0.5 else "negative"
        s_hits += got == expected
        print(json.dumps({"expected": expected, "positive_probability": res["positive_probability"]}))
    print(f"Sentiment examples matching expectation: {s_hits}/{len(SENTIMENT_EXAMPLES)}")


if __name__ == "__main__":
    main()
