from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.ml import PredictResult, TrainRequest, TrainResult
from app.services.ml.ml_service import MLService

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/train/{symbol}", response_model=TrainResult)
def train_model(
    symbol: str,
    body: TrainRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        svc = MLService()
        return svc.train(
            symbol=symbol,
            start=body.start,
            end=body.end,
            model_type=body.model_type,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/predict/{symbol}", response_model=PredictResult)
def predict(
    symbol: str,
    model_type: str = Query("logistic_regression"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        svc = MLService()
        return svc.predict(symbol=symbol, model_type=model_type, db=db)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
