"""
ndvi.py

Fetch NDVI (Normalized Difference Vegetation Index)
from Google Earth Engine and preprocess it.

Author: TerraScore
"""

import ee
import pandas as pd
import os
from dotenv import load_dotenv


# =====================================================
# ------------------ ENV SETUP -------------------------
# =====================================================

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")

if not PROJECT_ID:
    raise ValueError("PROJECT_ID not found in .env file")

ee.Initialize(project=PROJECT_ID)


# =====================================================
# ------------------ MAIN FUNCTION ---------------------
# =====================================================

def get_ndvi_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch NDVI data from MODIS satellite.

    Parameters:
        lat (float): Latitude
        lon (float): Longitude
        start_date (str): YYYY-MM-DD
        end_date (str): YYYY-MM-DD

    Returns:
        pd.DataFrame: date, ndvi (0–1), lat, lon
    """

    try:
        # ---------- Geometry ----------
        point = ee.Geometry.Point([lon, lat])

        # ---------- Image Collection ----------
        collection = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate(start_date, end_date)
            .filterBounds(point)
            .select("NDVI")
        )

        size = collection.size().getInfo()

        if size == 0:
            print("⚠️ No NDVI data available")
            return pd.DataFrame(columns=["date", "ndvi", "lat", "lon"])

        # ---------- Extract Function ----------
        def extract(image):
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=1000,
                bestEffort=True
            )

            return ee.Feature(None, {
                "date": image.date().format("YYYY-MM-dd"),
                "ndvi": stats.get("NDVI")
            })

        # ---------- Convert to FeatureCollection ----------
        fc = ee.FeatureCollection(collection.map(extract))
        fc_info = fc.getInfo()

        if "features" not in fc_info:
            return pd.DataFrame(columns=["date", "ndvi", "lat", "lon"])

        features = fc_info["features"]

        # ---------- Extract Data ----------
        data = []

        for f in features:
            props = f.get("properties", {})
            val = props.get("ndvi")

            if val is not None:
                # Convert to real NDVI (scale factor)
                ndvi = val / 10000

                data.append({
                    "date": props.get("date"),
                    "ndvi": ndvi
                })

        # ---------- DataFrame ----------
        df = pd.DataFrame(data)

        if df.empty:
            print("⚠️ NDVI extraction returned empty data")
            return df

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        df["lat"] = lat
        df["lon"] = lon

        # ---------- Interpolate daily ----------
        if len(df) > 1:
            df = df.set_index("date").resample("D").interpolate().reset_index()

        # ---------- Safety Clamp ----------
        df["ndvi"] = df["ndvi"].clip(0, 1)

        return df

    except Exception as e:
        print("NDVI FETCH ERROR:", str(e))
        return pd.DataFrame(columns=["date", "ndvi", "lat", "lon"])