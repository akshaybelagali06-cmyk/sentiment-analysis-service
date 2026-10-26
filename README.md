# Sentiment Analysis Service

A REST API that uses a pretrained Hugging Face Transformer model to classify English text as **POSITIVE** or **NEGATIVE** and returns a confidence score. Predictions are stored in a SQLite database for later retrieval.

## Features

- Sentiment analysis using a pretrained DistilBERT model.
- Confidence scores for predictions.
- REST API built with FastAPI.
- SQLite database for storing review history.
- Input validation for empty and whitespace-only text.
- Paginated review history.
- Automated API tests using a fake predictor.
- Docker support with persistent database storage.

## Technology Stack

- Python 3.12 (Docker image)
- FastAPI
- Hugging Face Transformers
- DistilBERT
- PyTorch (CPU)
- SQLAlchemy
- SQLite
- Pytest
- Docker

## AI Model

`distilbert/distilbert-base-uncased-finetuned-sst-2-english`

The model is trained for binary sentiment classification. It is intended for English text and may not correctly interpret every context, sarcasm, or specialized terminology.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service information |
| GET | `/health` | Health check |
| POST | `/analyze` | Analyze text and save the prediction |
| GET | `/history` | Retrieve saved reviews |

Interactive API documentation is available at `/docs`.

### Example Request

```json
{
  "text": "I absolutely
