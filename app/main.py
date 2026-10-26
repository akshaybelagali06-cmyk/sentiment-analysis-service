from contextlib import asynccontextmanager
from typing import Callable

from fastapi import Depends, FastAPI, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import SentimentRecord
from app.schemas import (
    SentimentRecordResponse,
    SentimentRequest,
    SentimentResponse,
)


# Load the AI model only when a prediction is requested.
# This allows tests to run without downloading or loading the model.
def get_predictor():
    from app.sentiment import predict

    return predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables when the application starts.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sentiment Analysis Service",
    description="Analyze text sentiment and store review history.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "Sentiment Analysis Service is running."
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze", response_model=SentimentResponse)
def analyze_sentiment(
    request: SentimentRequest,
    db: Session = Depends(get_db),
    predictor: Callable[[str], dict] = Depends(get_predictor),
):
    # Generate a sentiment prediction.
    prediction = predictor(request.text)

    # Store the prediction in the database.
    record = SentimentRecord(
        review=request.text,
        sentiment=prediction["sentiment"],
        confidence=prediction["confidence"],
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@app.get(
    "/history",
    response_model=list[SentimentRecordResponse],
)
def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    statement = (
        select(SentimentRecord)
        .order_by(SentimentRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()
