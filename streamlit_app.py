"""TerraScore Streamlit dashboard for model training and drought prediction."""

from __future__ import annotations

from datetime import date, datetime
import os

import altair as alt
import pandas as pd
import requests
import streamlit as st

from backend.database.session import SessionLocal
from backend.models.training_history import TrainingHistory


st.set_page_config(
    page_title="TerraScore training and prediction",
    page_icon=":material/biotech:",
    layout="wide",
)

try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
except Exception:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8005")


def post_json(path: str, payload: dict[str, object], token: str | None = None) -> requests.Response:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{API_BASE_URL}{path}", json=payload, headers=headers, timeout=60)


@st.cache_data(ttl=15, show_spinner=False)
def load_recent_training_runs(limit: int = 5) -> pd.DataFrame:
    session = SessionLocal()
    try:
        runs = (
            session.query(TrainingHistory)
            .order_by(TrainingHistory.started_at.desc())
            .limit(limit)
            .all()
        )
        rows = []
        for run in runs:
            rows.append(
                {
                    "id": run.id,
                    "status": run.status,
                    "latitude": run.latitude,
                    "longitude": run.longitude,
                    "start_date": run.start_date,
                    "end_date": run.end_date,
                    "started_at": run.started_at,
                    "completed_at": run.completed_at,
                    "error_message": run.error_message,
                    "metrics": run.metrics,
                }
            )
        return pd.DataFrame(rows)
    finally:
        session.close()


def format_value(value: float | None, precision: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{precision}f}"


st.title("TerraScore training and prediction")
st.caption("Train the drought model and run predictions from one dashboard.")

with st.sidebar:
    st.subheader("Connection")
    st.text_input("API base URL", value=API_BASE_URL, disabled=True)
    token = st.text_input(
        "Bearer token for authenticated history",
        value="",
        type="password",
        help="Optional. Leave blank for public prediction requests.",
    )
    st.caption("Set API_BASE_URL in the environment if your backend is on a different port.")

recent_runs = load_recent_training_runs()

top_left, top_right = st.columns([2, 1], vertical_alignment="top")
with top_left:
    with st.container(border=True):
        st.subheader("Overview")
        st.write(
            "Use the training form to queue a background model build, then run a prediction to see drought, NDVI, LST, and recommendation output."
        )
        st.write(f"Backend: `{API_BASE_URL}`")

with top_right:
    with st.container(border=True):
        st.subheader("Model status")
        model_path = os.path.join("models", "drought_xgboost.joblib")
        st.metric("Model file", "present" if os.path.exists(model_path) else "missing")
        st.metric("Recent training runs", str(len(recent_runs)))

tab_train, tab_predict, tab_history = st.tabs(["Train model", "Predict drought", "Training history"])

with tab_train:
    left, right = st.columns([1, 1], vertical_alignment="top")

    with left:
        with st.container(border=True):
            st.subheader("Start training")
            with st.form("training_form"):
                train_lat = st.number_input("Latitude", value=28.4, format="%.4f")
                train_lon = st.number_input("Longitude", value=77.0, format="%.4f")
                train_start = st.date_input("Start date", value=date(2023, 1, 1))
                train_end = st.date_input("End date", value=date(2023, 12, 31))
                train_submit = st.form_submit_button("Queue training", type="primary")

            if train_submit:
                try:
                    response = post_json(
                        "/train",
                        {
                            "lat": float(train_lat),
                            "lon": float(train_lon),
                            "start_date": train_start.strftime("%Y-%m-%d"),
                            "end_date": train_end.strftime("%Y-%m-%d"),
                        },
                        token=token or None,
                    )
                    if response.status_code == 202:
                        st.success("Training queued successfully.")
                        st.json(response.json())
                        st.cache_data.clear()
                    else:
                        st.error(f"Training request failed: {response.status_code}")
                        st.code(response.text)
                except requests.RequestException as exc:
                    st.error(f"Could not reach the backend: {exc}")

    with right:
        with st.container(border=True):
            st.subheader("Training tips")
            st.markdown(
                "- Training runs in the background and returns immediately.\n"
                "- If the model file already exists, the backend may skip retraining.\n"
                "- Use a valid coordinate and a date range with enough climate data."
            )

with tab_predict:
    left, right = st.columns([1, 1], vertical_alignment="top")

    with left:
        with st.container(border=True):
            st.subheader("Run prediction")
            with st.form("prediction_form"):
                pred_lat = st.number_input("Latitude ", value=28.4, format="%.4f", key="pred_lat")
                pred_lon = st.number_input("Longitude ", value=77.0, format="%.4f", key="pred_lon")
                pred_start = st.date_input("Prediction start", value=date(2024, 1, 1), key="pred_start")
                pred_end = st.date_input("Prediction end", value=date(2024, 1, 31), key="pred_end")
                farm_id = st.number_input("Farm ID (optional)", min_value=0, value=0, step=1)
                pred_submit = st.form_submit_button("Get prediction", type="primary")

            if pred_submit:
                payload: dict[str, object] = {
                    "lat": float(pred_lat),
                    "lon": float(pred_lon),
                    "start_date": pred_start.strftime("%Y-%m-%d"),
                    "end_date": pred_end.strftime("%Y-%m-%d"),
                }
                if farm_id:
                    payload["farm_id"] = int(farm_id)

                try:
                    response = post_json("/predict", payload, token=token or None)
                    if response.ok:
                        st.session_state["last_prediction"] = response.json()
                        st.success("Prediction completed.")
                    else:
                        st.error(f"Prediction failed: {response.status_code}")
                        st.code(response.text)
                except requests.RequestException as exc:
                    st.error(f"Could not reach the backend: {exc}")

    with right:
        last_prediction = st.session_state.get("last_prediction")
        with st.container(border=True):
            st.subheader("Latest prediction")
            if not last_prediction:
                st.info("Run a prediction to see drought index, NDVI, LST, and recommendations here.")
            else:
                metric_row = st.container(horizontal=True)
                metric_row.metric("Drought index", format_value(last_prediction.get("predicted_drought_index"), 2), border=True)
                metric_row.metric("NDVI", format_value(last_prediction.get("ndvi"), 3), border=True)
                metric_row.metric("LST", f"{format_value(last_prediction.get('lst'), 2)} °C", border=True)
                metric_row.metric("Credit score", f"{format_value(last_prediction.get('credit_score'), 2)}/100", border=True)

                st.write(f"**Date:** {last_prediction.get('date', 'n/a')}")
                st.write(f"**Risk:** {last_prediction.get('farmer_score', 'n/a')}")

                climate = last_prediction.get("climate") or {}
                climate_cols = st.columns(3)
                climate_cols[0].metric("Rainfall", format_value(climate.get("rainfall"), 2))
                climate_cols[1].metric("Temperature", f"{format_value(climate.get('temperature'), 2)} °C")
                climate_cols[2].metric("Humidity", f"{format_value(climate.get('humidity'), 2)} %")

                if last_prediction.get("recommendations"):
                    st.markdown("**Recommendations**")
                    for item in last_prediction["recommendations"]:
                        st.write(f"- **{item.get('priority', 'Info')}**: {item.get('message', '')}")

                trends = pd.DataFrame(last_prediction.get("ndvi_trend", []))
                if not trends.empty:
                    trends["date"] = pd.to_datetime(trends["date"])
                    chart = (
                        alt.Chart(trends)
                        .mark_line(point=True)
                        .encode(x=alt.X("date:T", title="Date"), y=alt.Y("ndvi:Q", title="NDVI"))
                        .properties(height=220)
                    )
                    st.altair_chart(chart)

                with st.expander("Raw prediction payload"):
                    st.json(last_prediction)

with tab_history:
    left, right = st.columns([2, 1], vertical_alignment="top")
    with left:
        with st.container(border=True):
            st.subheader("Recent training runs")
            if recent_runs.empty:
                st.info("No training runs found yet.")
            else:
                display = recent_runs.copy()
                display["started_at"] = pd.to_datetime(display["started_at"])
                if "completed_at" in display:
                    display["completed_at"] = pd.to_datetime(display["completed_at"])
                st.dataframe(
                    display[["id", "status", "latitude", "longitude", "start_date", "end_date", "started_at", "completed_at", "error_message"]],
                    hide_index=True,
                    width="stretch",
                )

    with right:
        with st.container(border=True):
            st.subheader("Run details")
            if recent_runs.empty:
                st.caption("No runs to inspect yet.")
            else:
                latest_run = recent_runs.iloc[0]
                st.metric("Latest status", latest_run["status"])
                st.write(f"**Latitude:** {latest_run['latitude']}")
                st.write(f"**Longitude:** {latest_run['longitude']}")
                st.write(f"**Range:** {latest_run['start_date']} to {latest_run['end_date']}")
                if latest_run.get("metrics"):
                    st.json(latest_run["metrics"])
                if latest_run.get("error_message"):
                    st.error(latest_run["error_message"])
