"""
api.py

TerraScore Climate ML API
- Train model
- Predict drought risk
- Generate farmer credit score
"""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, field_validator
import pandas as pd
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# ------------------ IMPORTS ------------------
from backend.datacollection.climate import get_climate_data
from backend.datacollection.ndvi import get_ndvi_data
from backend.datacollection.lst import get_lst_data
from preprocessing.cleaning import clean_climate_data
from preprocessing.feature_engineering import add_features
from models.drought_model import train_model, load_model, predict
from backend.config import settings
from backend.database import SessionLocal, get_db, init_database
from backend.models.prediction import Prediction
from backend.models.farm import Farm
from backend.models.training_history import TrainingHistory
from backend.models.user import User
from backend.routers.admin import router as admin_router
from backend.routers.auth import get_optional_current_user, router as auth_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.farm import router as farm_router
from backend.routers.history import router as history_router
from backend.routers.report import router as report_router
from backend.routers.upload import router as upload_router
from backend.routers.weather import router as weather_router
from backend.services.recommendation_service import recommendation_service
from backend.utils.logger import logger
from sqlalchemy.orm import Session

# ------------------ ENV ------------------
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "drought_xgboost.joblib")

app = FastAPI(
    title="TerraScore Climate ML API",
    description="Production APIs for agricultural credit scoring, farms, weather, reports, and analytics. Authenticate with a bearer token for user-owned resources.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
_request_times: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = Lock()


@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next):
    """Apply a small process-local rate limit and persist request/error logs."""
    client = request.client.host if request.client else "unknown"
    now = monotonic()
    with _rate_lock:
        window = _request_times[client]
        while window and window[0] <= now - settings.rate_limit_window_seconds:
            window.popleft()
        if len(window) >= settings.rate_limit_requests:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        window.append(now)
    try:
        response = await call_next(request)
        logger.info("api_request method=%s path=%s status=%s client=%s", request.method, request.url.path, response.status_code, client)
        return response
    except Exception:
        logger.exception("api_error method=%s path=%s client=%s", request.method, request.url.path, client)
        raise
app.include_router(auth_router)
app.include_router(farm_router)
app.include_router(history_router)
app.include_router(weather_router)
app.include_router(report_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(upload_router)


@app.on_event("startup")
def initialize_application() -> None:
    """Validate runtime security settings and initialize persistence."""
    settings.validate_security_settings()
    init_database()


# =====================================================
# ------------------ REQUEST MODELS --------------------
# =====================================================

class BaseRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"lat": 28.4, "lon": 77.0, "start_date": "2024-01-01", "end_date": "2024-01-31"}})
    lat: float
    lon: float
    start_date: str
    end_date: str

    @field_validator("start_date", "end_date")
    def validate_date(cls, v):
        for fmt in ("%Y-%m-%d", "%Y%m%d"):
            try:
                return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
            except:
                continue
        raise ValueError("Invalid date format")


class TrainRequest(BaseRequest):
    pass


class PredictRequest(BaseRequest):
    farm_id: Optional[int] = None


# =====================================================
# ------------------ UTIL FUNCTIONS --------------------
# =====================================================

def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")


def standardize_datetime(df):
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.floor("s")
    return df


def clean_merged_columns(df, lat, lon):
    if 'ndvi_x' in df.columns:
        df['ndvi'] = df['ndvi_x']
    elif 'ndvi_y' in df.columns:
        df['ndvi'] = df['ndvi_y']

    if 'lst_x' in df.columns:
        df['lst'] = df['lst_x']
    elif 'lst_y' in df.columns:
        df['lst'] = df['lst_y']

    df = df[[c for c in df.columns if not c.endswith('_x') and not c.endswith('_y')]].copy()

    df['lat'] = lat
    df['lon'] = lon

    return df


# =====================================================
# ------------------ CORE PIPELINE ---------------------
# =====================================================

def prepare_dataset(lat, lon, start_date, end_date):

    df_climate = get_climate_data(lat, lon, format_date(start_date), format_date(end_date))
    df_ndvi = get_ndvi_data(lat, lon, start_date, end_date)
    df_lst = get_lst_data(lat, lon, start_date, end_date)

    # -------- Fallbacks --------
    if df_ndvi.empty:
        df_ndvi = pd.DataFrame({
            "date": df_climate["date"],
            "ndvi": df_climate["PRECTOTCORR"].rolling(7, min_periods=1).mean() / 10
        })

    if df_lst.empty:
        df_lst = pd.DataFrame({
            "date": df_climate["date"],
            "lst": [25] * len(df_climate)
        })

    # -------- Standardize --------
    df_climate = standardize_datetime(df_climate).sort_values("date")
    df_ndvi = standardize_datetime(df_ndvi).sort_values("date")
    df_lst = standardize_datetime(df_lst).sort_values("date")

    # -------- Merge --------
    df = pd.merge_asof(df_climate, df_ndvi, on="date", direction="nearest")
    df = pd.merge_asof(df, df_lst, on="date", direction="nearest")

    df = clean_merged_columns(df, lat, lon)

    # -------- Clean --------
    for col in ["ndvi", "lst"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].interpolate().bfill().ffill()

    df_clean = clean_climate_data(df)
    df_feats = add_features(df_clean).bfill().ffill()

    return df, df_feats


# =====================================================
# ------------------ BUSINESS LOGIC --------------------
# =====================================================

def calculate_risk(pred, ndvi):
    if pred < 2 and ndvi > 0.6:
        return "Excellent"
    elif pred < 4:
        return "Moderate Risk"
    return "High Risk"


def calculate_credit_score(pred, ndvi, lst):
    ndvi_score = ndvi * 100
    drought_score = max(0, 100 - (pred * 20))
    lst_score = max(0, 100 - (lst * 2))

    return round((0.5 * ndvi_score) + (0.3 * drought_score) + (0.2 * lst_score), 2)


# =====================================================
# ------------------ ROUTES ----------------------------
# =====================================================

@app.get("/")
def read_root():
    return {"message": "Welcome to TerraScore Climate ML API"}


def train_in_background(lat: float, lon: float, start_date: str, end_date: str) -> None:
    """Run unchanged training pipeline outside the request lifecycle."""
    db = SessionLocal()
    history = TrainingHistory(latitude=lat, longitude=lon, start_date=datetime.strptime(start_date, "%Y-%m-%d").date(), end_date=datetime.strptime(end_date, "%Y-%m-%d").date(), status="running", model_path=MODEL_PATH)
    db.add(history)
    db.commit()
    try:
        if os.path.exists(MODEL_PATH):
            history.status = "skipped"
            history.error_message = "Model already trained. Delete file to retrain."
        else:
            _, df_feats = prepare_dataset(lat, lon, start_date, end_date)
            _, metrics = train_model(df_feats, model_path=MODEL_PATH)
            history.status = "completed"
            history.metrics = metrics
        history.completed_at = datetime.utcnow()
        db.commit()
        logger.info("training_completed history_id=%s status=%s", history.id, history.status)
    except Exception as exc:
        db.rollback()
        history.status = "failed"
        history.error_message = str(exc)[:2000]
        history.completed_at = datetime.utcnow()
        db.commit()
        logger.exception("training_failed history_id=%s", history.id)
    finally:
        db.close()


@app.post("/train", status_code=202, summary="Start model training in the background")
def api_train(request: TrainRequest, background_tasks: BackgroundTasks):
    """Queue model training and return immediately without blocking clients."""
    try:
        background_tasks.add_task(train_in_background, request.lat, request.lon, request.start_date, request.end_date)
        logger.info("training_queued lat=%s lon=%s", request.lat, request.lon)
        return {"status": "Training Started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def execute_prediction(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    """Execute the original inference pipeline and enrich only its response."""
    model = load_model(MODEL_PATH)
    if model is None:
        raise HTTPException(status_code=400, detail="Model not found. Train first.")
    df, df_feats = prepare_dataset(lat, lon, start_date, end_date)
    if df_feats.empty:
        raise HTTPException(status_code=400, detail="Insufficient data")
    predictions = predict(model, df_feats)
    df_feats["predicted_drought_index"] = predictions
    latest = df_feats.iloc[-1]
    pred_val, ndvi_val, lst_val = float(latest["predicted_drought_index"]), float(latest["ndvi"]), float(latest["lst"])
    climate = {"rainfall": float(latest.get("PRECTOTCORR", 0)), "temperature": float(latest.get("T2M", lst_val)), "humidity": float(latest.get("RH2M", 0))}
    credit_score = calculate_credit_score(pred_val, ndvi_val, lst_val)
    return {"date": latest["date"].strftime("%Y-%m-%d"), "lat": lat, "lon": lon, "predicted_drought_index": pred_val, "ndvi": ndvi_val, "lst": lst_val, "farmer_score": calculate_risk(pred_val, ndvi_val), "credit_score": credit_score, "climate": climate, "recommendations": recommendation_service.generate(ndvi=ndvi_val, lst=lst_val, rainfall=climate["rainfall"], temperature=climate["temperature"], humidity=climate["humidity"], credit_score=credit_score), "ndvi_trend": [{"date": r["date"].strftime("%Y-%m-%d"), "ndvi": float(r["ndvi"])} for _, r in df[["date", "ndvi"]].dropna().iterrows()], "lst_trend": [{"date": r["date"].strftime("%Y-%m-%d"), "lst": float(r["lst"])} for _, r in df[["date", "lst"]].dropna().iterrows()]}


@app.post("/predict", summary="Run drought prediction and generate recommendations")
def api_predict(request: PredictRequest, db: Session = Depends(get_db), user: Optional[User] = Depends(get_optional_current_user)):
    try:
        result = execute_prediction(request.lat, request.lon, request.start_date, request.end_date)
        if request.farm_id is not None:
            farm = db.get(Farm, request.farm_id)
            if user is None or farm is None or farm.user_id != user.id:
                raise HTTPException(status_code=403, detail="The selected farm does not belong to this user")
        # Public compatibility is retained; unauthenticated calls are still
        # audited with a null user ID, while authenticated records appear in
        # that user's protected history.
        record = Prediction(user_id=user.id if user else None, farm_id=request.farm_id, latitude=request.lat, longitude=request.lon, start_date=datetime.strptime(request.start_date, "%Y-%m-%d").date(), end_date=datetime.strptime(request.end_date, "%Y-%m-%d").date(), prediction_date=datetime.strptime(result["date"], "%Y-%m-%d").date(), drought_index=result["predicted_drought_index"], ndvi=result["ndvi"], lst=result["lst"], climate=result["climate"], risk_classification=result["farmer_score"], credit_score=result["credit_score"], recommendations=result["recommendations"])
        db.add(record)
        db.commit()
        db.refresh(record)
        result["prediction_id"] = record.id
        logger.info("prediction_completed user_id=%s lat=%s lon=%s", user.id if user else None, request.lat, request.lon)
        return result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        logger.exception("prediction_failed")
        raise HTTPException(status_code=500, detail="Prediction could not be completed")
