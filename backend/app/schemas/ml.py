from datetime import date
from typing import List

from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    start: date
    end: date
    model_type: str = "logistic_regression"


class TrainResult(BaseModel):
    symbol: str
    model_type: str
    test_accuracy: float
    test_precision: float
    test_recall: float
    num_train_samples: int
    num_test_samples: int
    feature_names: List[str]


class PredictResult(BaseModel):
    symbol: str
    prediction_date: date
    up_probability: float = Field(..., ge=0.0, le=1.0)
    direction: str  # "up" or "down"
