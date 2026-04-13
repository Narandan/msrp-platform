"""ML service for training and predicting price direction."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.db.models.stock import Candle, Symbol
from app.schemas.ml import PredictResult, TrainResult
from app.schemas.stock import CandleDTO
from app.services.ml.feature_builder import FEATURE_NAMES, FeatureBuilder

MIN_SAMPLES = 50
MODEL_DIR = Path("models")


class MLService:
    def train(
        self,
        *,
        symbol: str,
        start: date,
        end: date,
        model_type: str = "logistic_regression",
        db: Session,
    ) -> TrainResult:
        ticker = symbol.strip().upper()

        sym = db.query(Symbol).filter(Symbol.ticker == ticker).one_or_none()
        if sym is None:
            raise ValueError(f"Symbol not found in DB: {ticker}. Ingest it first.")

        rows: List[Candle] = (
            db.query(Candle)
            .filter(Candle.symbol_id == sym.id)
            .filter(Candle.date >= start)
            .filter(Candle.date <= end)
            .order_by(Candle.date.asc())
            .all()
        )
        if not rows:
            raise ValueError(f"No candles available for {ticker} in range {start}..{end}")

        candles: List[CandleDTO] = [
            CandleDTO(
                date=r.date,
                open=r.open,
                high=r.high,
                low=r.low,
                close=r.close,
                volume=r.volume,
            )
            for r in rows
        ]

        fb = FeatureBuilder()
        X, y, _ = fb.build(candles)

        if len(X) < MIN_SAMPLES:
            raise ValueError(
                f"Insufficient data: need at least {MIN_SAMPLES} usable bars, got {len(X)}."
            )

        # Temporal split — no shuffling
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Scale: fit on train only
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        model = _make_model(model_type)
        model.fit(X_train_s, y_train)

        y_pred = model.predict(X_test_s)
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))

        MODEL_DIR.mkdir(exist_ok=True)
        model_path = MODEL_DIR / f"{ticker}_{model_type}.pkl"
        joblib.dump((model, scaler), model_path)

        return TrainResult(
            symbol=ticker,
            model_type=model_type,
            test_accuracy=acc,
            test_precision=prec,
            test_recall=rec,
            num_train_samples=len(X_train),
            num_test_samples=len(X_test),
            feature_names=FEATURE_NAMES,
        )

    def predict(
        self,
        *,
        symbol: str,
        model_type: str = "logistic_regression",
        db: Session,
    ) -> PredictResult:
        ticker = symbol.strip().upper()

        model_path = MODEL_DIR / f"{ticker}_{model_type}.pkl"
        if not model_path.exists():
            raise FileNotFoundError(
                f"No trained model found for {ticker} ({model_type}). Train it first."
            )

        model, scaler = joblib.load(model_path)

        # Warm-up: macd_slow + macd_signal + 10 extra
        fb = FeatureBuilder()
        warmup_bars = fb.macd_slow + fb.macd_signal + 10

        sym = db.query(Symbol).filter(Symbol.ticker == ticker).one_or_none()
        if sym is None:
            raise ValueError(f"Symbol not found in DB: {ticker}.")

        rows: List[Candle] = (
            db.query(Candle)
            .filter(Candle.symbol_id == sym.id)
            .order_by(Candle.date.desc())
            .limit(warmup_bars)
            .all()
        )
        if not rows:
            raise ValueError(f"No candles available for {ticker}.")

        # Re-order ascending
        rows = list(reversed(rows))

        candles: List[CandleDTO] = [
            CandleDTO(
                date=r.date,
                open=r.open,
                high=r.high,
                low=r.low,
                close=r.close,
                volume=r.volume,
            )
            for r in rows
        ]

        x = fb.build_latest(candles)
        x_scaled = scaler.transform(x)

        proba = model.predict_proba(x_scaled)[0]
        # class index for label=1 (up)
        classes = list(model.classes_)
        up_prob = float(proba[classes.index(1)]) if 1 in classes else 0.0

        prediction_date = candles[-1].date
        direction = "up" if up_prob >= 0.5 else "down"

        return PredictResult(
            symbol=ticker,
            prediction_date=prediction_date,
            up_probability=up_prob,
            direction=direction,
        )


def _make_model(model_type: str):
    if model_type == "logistic_regression":
        return LogisticRegression(max_iter=1000)
    elif model_type == "random_forest":
        return RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        raise ValueError(
            f"Unknown model_type '{model_type}'. Use 'logistic_regression' or 'random_forest'."
        )
