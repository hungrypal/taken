"""
drought_model.py

Handles:
- Training ML model
- Saving/loading model
- Prediction pipeline

Uses:
- XGBoost Regressor
- StandardScaler
"""

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
import joblib
import os

from preprocessing.feature_engineering import scale_features


# =====================================================
# ------------------ CONFIG ----------------------------
# =====================================================

FEATURE_COLUMNS = [
    'PRECTOTCORR',
    'rainfall_7_days',
    'rainfall_30_days',
    'rainfall_variability',
    'temp_7_days_avg',
    'T2M',
    'RH2M',
    'EVPTRNS',
    'ndvi'
]

TARGET_COLUMN = "drought_index"

SCALER_PATH = "models/scaler.joblib"
DEFAULT_MODEL_PATH = "models/drought_xgboost.joblib"


# =====================================================
# ------------------ TRAIN MODEL -----------------------
# =====================================================

def train_model(df, model_path=DEFAULT_MODEL_PATH):
    """
    Train XGBoost model on climate data

    Steps:
    1. Drop NA values
    2. Scale features
    3. Split data
    4. Train model
    5. Evaluate performance
    6. Save model & scaler
    """

    # ---------- Clean Data ----------
    df = df.dropna()

    if len(df) == 0:
        raise ValueError("No data available after cleaning.")

    # ---------- Features & Target ----------
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # ---------- Scaling ----------
    X_scaled, scaler = scale_features(X, FEATURE_COLUMNS)

    # Save scaler
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)

    # ---------- Train/Test Split ----------
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # ---------- Model ----------
    model = XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5
    )

    model.fit(X_train, y_train)

    # ---------- Evaluation ----------
    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    # ---------- Save Model ----------
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)

    metrics = {
        "mse": float(mse),
        "r2": float(r2)
    }

    return model, metrics


# =====================================================
# ------------------ LOAD MODEL ------------------------
# =====================================================

def load_model(model_path=DEFAULT_MODEL_PATH):
    """Load trained model from disk"""
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None


# =====================================================
# ------------------ PREDICT ---------------------------
# =====================================================

def predict(model, df):
    """
    Generate predictions using trained model

    Steps:
    1. Validate features
    2. Load scaler
    3. Scale input data
    4. Predict output
    """

    # ---------- Check Missing Features ----------
    missing_cols = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing features: {missing_cols}")

    # ---------- Load Scaler ----------
    if not os.path.exists(SCALER_PATH):
        raise ValueError("Scaler not found. Train model first.")

    scaler = joblib.load(SCALER_PATH)

    # ---------- Scale Data ----------
    df_scaled, _ = scale_features(df, FEATURE_COLUMNS, scaler)

    # ---------- Predict ----------
    predictions = model.predict(df_scaled[FEATURE_COLUMNS])

    return predictions