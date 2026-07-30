"""Downloadable PDF reports for owned prediction records."""

from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.farm import Farm
from backend.models.prediction import Prediction
from backend.models.report import Report
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.pdf_service import pdf_service


router = APIRouter(tags=["reports"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/report/{prediction_id}", summary="Download prediction PDF report", responses={404: {"description": "Prediction not found"}, 503: {"description": "PDF service unavailable"}})
def report(prediction_id: int, user: CurrentUser, db: DatabaseSession) -> StreamingResponse:
    prediction = db.get(Prediction, prediction_id)
    if prediction is None or prediction.user_id != user.id:
        raise HTTPException(status_code=404, detail="Prediction not found")
    farm = db.get(Farm, prediction.farm_id) if prediction.farm_id else None
    location = f"{farm.farm_name} ({farm.latitude:.4f}, {farm.longitude:.4f})" if farm else f"{prediction.latitude:.4f}, {prediction.longitude:.4f}"
    try:
        content = pdf_service.build_prediction_report(farmer_name=user.full_name or user.email, farm_location=location, prediction=prediction)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    db.add(Report(user_id=user.id, farm_id=prediction.farm_id, prediction_id=prediction.id, report_type="prediction_pdf", status="generated"))
    db.commit()
    return StreamingResponse(BytesIO(content), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="terrascore-prediction-{prediction.id}.pdf"'})
