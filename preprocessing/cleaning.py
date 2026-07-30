"""
cleaning.py

Handles:
- Missing values from NASA API
- Interpolation
- Data consistency

Author: TerraScore
"""

import pandas as pd
import numpy as np


# =====================================================
# ------------------ CONFIG ----------------------------
# =====================================================

MISSING_VALUE = -999.0


# =====================================================
# ------------------ CLEAN FUNCTION --------------------
# =====================================================

def clean_climate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean climate dataset.

    Steps:
    1. Replace NASA missing values (-999.0) with NaN
    2. Interpolate missing numeric values
    3. Forward & backward fill edge cases

    Parameters:
        df (pd.DataFrame): Raw climate data

    Returns:
        pd.DataFrame: Cleaned dataset
    """

    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty")

    df_clean = df.copy()

    # ---------- Step 1: Replace invalid values ----------
    df_clean.replace(MISSING_VALUE, np.nan, inplace=True)

    # ---------- Step 2: Select numeric columns ----------
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) == 0:
        return df_clean

    # ---------- Step 3: Interpolation ----------
    df_clean[numeric_cols] = df_clean[numeric_cols].interpolate(
        method='linear',
        limit_direction='both'
    )

    # ---------- Step 4: Final fallback ----------
    df_clean[numeric_cols] = df_clean[numeric_cols].bfill().ffill()

    return df_clean