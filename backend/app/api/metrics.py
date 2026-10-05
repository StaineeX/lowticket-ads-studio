from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.app.db import get_db_session
from backend.app.domain.campaigns import Platform
from backend.app.services.metrics_import import MetricImporter


router = APIRouter(prefix="/api")


@router.post("/metrics/import")
async def import_metrics(
    platform: Platform = Query(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
) -> dict:
    content = await file.read()
    result = MetricImporter().import_csv(content, platform)
    session.add_all(record.to_row() for record in result.records)
    session.commit()
    return {
        "imported": result.imported,
        "errors": [{"row": error.row, "message": error.message} for error in result.errors],
    }
