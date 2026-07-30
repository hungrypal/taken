"""
lst.py

Fetch Land Surface Temperature (LST) from Google Earth Engine
and convert it to Celsius.

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

# Initialize Earth Engine
ee.Initialize(project=PROJECT_ID)


# =====================================================
# ------------------ MAIN FUNCTION ---------------------
# =====================================================

def get_lst_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch LST data from MODIS satellite.

    Parameters:
        lat (float): Latitude
        lon (float): Longitude
        start_date (str): YYYY-MM-DD
        end_date (str): YYYY-MM-DD

    Returns:
        pd.DataFrame: date, lst (°C), lat, lon
    """

    try:
        # ---------- Geometry ----------
        point = ee.Geometry.Point([lon, lat])

        # ---------- Image Collection ----------
        collection = (
            ee.ImageCollection("MODIS/061/MOD11A2")
            .filterDate(start_date, end_date)
            .filterBounds(point)
            .select("LST_Day_1km")
        )

        # ---------- Extract Function ----------
        def extract(image):
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=1000
            )

            return ee.Feature(None, {
                "date": image.date().format("YYYY-MM-dd"),
                "lst": stats.get("LST_Day_1km")
            })

        # ---------- Convert to FeatureCollection ----------
        fc = ee.FeatureCollection(collection.map(extract))
        fc_info = fc.getInfo()

        # ---------- Safety Check ----------
        if "features" not in fc_info:
            return pd.DataFrame(columns=["date", "lst", "lat", "lon"])

        features = fc_info["features"]

        # ---------- Extract Data ----------
        data = []

        for f in features:
            props = f.get("properties", {})
            val = props.get("lst")

            if val is not None:
                # Convert Kelvin → Celsius
                lst_c = (val * 0.02) - 273.15

                data.append({
                    "date": props.get("date"),
                    "lst": lst_c
                })

        # ---------- DataFrame ----------
        df = pd.DataFrame(data)

        if df.empty:
            return df

        df["date"] = pd.to_datetime(df["date"])
        df["lat"] = lat
        df["lon"] = lon

        return df

    except Exception as e:
        print("LST FETCH ERROR:", str(e))
        return pd.DataFrame(columns=["date", "lst", "lat", "lon"])