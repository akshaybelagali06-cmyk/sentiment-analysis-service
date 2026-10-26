from transformers import pipeline

MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

classifier = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    device=-1,
)

def predict(text: str) -> dict:
    """Predict whether a review is positive or negative."""
    result = classifier(
        text,
        truncation=True,
        max_length=512,
    )[0]

    return {
        "sentiment": result["label"],
        "confidence": float(result["score"]),
    }
