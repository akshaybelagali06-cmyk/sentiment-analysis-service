from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be empty or whitespace.")
        return value


class SentimentResponse(BaseModel):
    id: int
    review: str
    sentiment: str
    confidence: float
    created_at: datetime


class SentimentRecordResponse(BaseModel):
    id: int
    review: str
    sentiment: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}
