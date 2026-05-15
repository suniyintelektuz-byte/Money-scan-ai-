from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    telegram_id = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scans = relationship("ScanResult", back_populates="user")

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    image_url = Column(String)
    is_genuine = Column(Boolean, nullable=True)
    confidence = Column(Float, nullable=True)
    denomination = Column(Integer, nullable=True)
    serial_number = Column(String, nullable=True)
    year = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String, default="web")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="scans")
