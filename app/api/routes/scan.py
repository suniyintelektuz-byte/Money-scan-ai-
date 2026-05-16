from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import random

router = APIRouter()

# Boya xato bergan get_db ni database faylidan olamiz
from app.database import get_db

@router.post("/scan/")
async def scan_bill(
    file: UploadFile = File(...),
    source: str = Form("telegram"),
    db: Session = Depends(get_db)
):
    # Bu yerda og'ir model yuklanmaydi, server crash bo'lmaydi!
    # Bot ishlab turishi uchun vaqtincha Random (tavakkal) natija qaytaramiz
    
    is_genuine_mock = random.choice([True, False])
    confidence_mock = random.uniform(0.85, 0.99)
    denomination_mock = random.choice([50, 100])
    serial_mock = "AB" + str(random.randint(10000000, 99999999)) + "C"
    year_mock = random.choice([2013, 2017, 2021])

    return {
        "is_genuine": is_genuine_mock,
        "denomination": denomination_mock,
        "serial_number": serial_mock,
        "year": year_mock,
        "confidence": confidence_mock
    }
    
