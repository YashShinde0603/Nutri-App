from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    fdc_id = Column(Integer, nullable=False)  # USDA FDC ID
    description = Column(String(512), nullable=False)
    category = Column(String(255), nullable=True)  # USDA category name
    quantity = Column(Float, default=1.0)  # user stored quantity (units flexible)
    unit_name = Column(String(64), default="unit")
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    extra = Column(Text, nullable=True)  # JSON string for nutrient snapshot if desired
