"""
feature_engineering.py

Handles:
- Feature creation (time-based climate features)
- Scaling of model features

Author: TerraScore
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler


# =====================================================
# ------------------ CONFIG ----------------------------
# =====================================================

RAIN_COL = "PRECTOTCORR"
TEMP_COL = "T2M"
EVAP_COL = "EVPTRNS"


# =====================================================
# ------------------ FEATURE ENGINEERING ---------------
# =====================================================

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived climate features for ML model.

    Features:
    - Rolling rainfall (7 & 30 days)
    - Rainfall variability (std deviation)
    - Temperature moving average
    - Drought index (target variable)

    Parameters:
        df (pd.DataFrame): Cleaned climate dataset

    Returns:
        pd.DataFrame: Dataset with new features
    """

    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty")

    df_feats = df.copy()

    # ---------- Ensure date column ----------
    if "date" not in df_feats.columns:
        raise ValueError("Missing 'date' column")

    df_feats = df_feats.sort_values(by="date")

    # ---------- Rainfall Features ----------
    df_feats["rainfall_7_days"] = df_feats[RAIN_COL].rolling(7, min_periods=1).sum()
    df_feats["rainfall_30_days"] = df_feats[RAIN_COL].rolling(30, min_periods=1).sum()

    df_feats["rainfall_variability"] = (
        df_feats[RAIN_COL]
        .rolling(30, min_periods=1)
        .std()
        .fillna(0)
    )

    # ---------- Temperature Features ----------
    df_feats["temp_7_days_avg"] = (
        df_feats[TEMP_COL]
        .rolling(7, min_periods=1)
        .mean()
    )

    # ---------- Target Variable ----------
    # Avoid division instability
    df_feats["drought_index"] = df_feats[RAIN_COL] / (df_feats[EVAP_COL] + 1)

    return df_feats


# =====================================================
# ------------------ SCALING ---------------------------
# =====================================================

def scale_features(df: pd.DataFrame, features: list, scaler=None):
    """
    Scale features using StandardScaler.

    Parameters:
        df (pd.DataFrame): Input dataset
        features (list): Feature column names
        scaler (StandardScaler): Optional pre-fitted scaler

    Returns:
        df_scaled (pd.DataFrame), scaler
    """

    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty")

    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns for scaling: {missing_cols}")

    df_scaled = df.copy()

    # ---------- Fit or Transform ----------
    if scaler is None:
        scaler = StandardScaler()
        df_scaled[features] = scaler.fit_transform(df_scaled[features])
    else:
        df_scaled[features] = scaler.transform(df_scaled[features])

    return df_scaled, scaler