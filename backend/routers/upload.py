"""Secure CSV/XLSX batch prediction ingestion endpoint."""

from datetime import datetime
from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.prediction import Prediction
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.ml_service import ml_service


router = APIRouter(tags=["bulk prediction"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]
REQUIRED_COLUMNS = {"latitude", "longitude", "start_date", "end_date"}


@router.post("/upload", summary="Upload farm locations and download predictions", responses={400: {"description": "Invalid spreadsheet or missing required columns"}, 422: {"description": "Invalid farm row"}})
async def upload_farms(
    user: CurrentUser,
    db: DatabaseSession,
    file: UploadFile = File(..., description="CSV or XLSX with latitude, longitude, start_date, end_date; optional farm_name and crop."),
) -> StreamingResponse:
    """Run the existing model for every validated row and return a CSV file."""
    filename = (file.filename or "").lower()
    if not (filename.endswith(".csv") or filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")
    content = await file.read()
    try:
        source = pd.read_csv(BytesIO(content)) if filename.endswith(".csv") else pd.read_excel(BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Unable to read uploaded file") from exc
    source.columns = [str(column).strip().lower() for column in source.columns]
    if not REQUIRED_COLUMNS.issubset(source.columns):
        raise HTTPException(status_code=400, detail="Required columns: latitude, longitude, start_date, end_date")
    if len(source) > 100:
        raise HTTPException(status_code=400, detail="A maximum of 100 farms may be uploaded at once")

    output: list[dict] = []
    for index, row in source.iterrows():
        try:
            latitude, longitude = float(row["latitude"]), float(row["longitude"])
            if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                raise ValueError("coordinates out of range")
            start_date = pd.to_datetime(row["start_date"]).strftime("%Y-%m-%d")
            end_date = pd.to_datetime(row["end_date"]).strftime("%Y-%m-%d")
            result = ml_service.predict(latitude, longitude, start_date, end_date)
            climate = result.get("climate", {})
            prediction = Prediction(user_id=user.id, latitude=latitude, longitude=longitude, start_date=datetime.strptime(start_date, "%Y-%m-%d").date(), end_date=datetime.strptime(end_date, "%Y-%m-%d").date(), prediction_date=datetime.strptime(result["date"], "%Y-%m-%d").date(), drought_index=result["predicted_drought_index"], ndvi=result["ndvi"], lst=result["lst"], risk_classification=result["farmer_score"], credit_score=result["credit_score"], climate=climate, recommendations=result.get("recommendations"))
            db.add(prediction)
            output.append({"row": index + 1, "status": "success", "latitude": latitude, "longitude": longitude, "drought_index": result["predicted_drought_index"], "credit_score": result["credit_score"], "risk_level": result["farmer_score"]})
        except Exception as exc:
            output.append({"row": index + 1, "status": "failed", "error": str(exc)})
    db.commit()
    stream = StringIO()
    pd.DataFrame(output).to_csv(stream, index=False)
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="terrascore-predictions.csv"'})
