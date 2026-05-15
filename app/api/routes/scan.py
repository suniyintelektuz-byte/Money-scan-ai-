from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.ai_scanner import scanner_service
from app.services.storage import upload_image
import uuid

router = APIRouter(prefix="/api/scan", tags=["scan"])

@router.post("/")
async def scan_dollar(
    file: UploadFile = File(...),
    source: str = "web",
    user_id: int = None,
    db: Session = Depends(get_db),
):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Faqat JPG, PNG, WEBP qabul qilinadi")
    image_bytes = await file.read()
    result = scanner_service.analyze(image_bytes)
    filename = f"{uuid.uuid4()}.jpg"
    image_url = upload_image(image_bytes, filename)
    scan = models.ScanResult(
        user_id=user_id,
        image_url=image_url,
        is_genuine=result["is_genuine"],
        confidence=result["confidence"],
        denomination=result["denomination"],
        serial_number=result["serial_number"],
        year=result["year"],
        notes=result["notes"],
        source=source,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return {"scan_id": scan.id, "image_url": image_url, **result}

@router.get("/history")
def get_history(user_id: int = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(models.ScanResult)
    if user_id:
        query = query.filter(models.ScanResult.user_id == user_id)
    return query.order_by(models.ScanResult.created_at.desc()).limit(limit).all()

@router.get("/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(models.ScanResult).filter(models.ScanResult.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan topilmadi")
    return scan
