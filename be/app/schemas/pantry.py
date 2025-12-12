from pydantic import BaseModel
from typing import Optional

class PantryItemCreate(BaseModel):
    user_id: int
    fdc_id: int
    description: str
    category: Optional[str] = None
    quantity: float = 1.0
    unit_name: str = "unit"

class PantryItemOut(BaseModel):
    id: int
    user_id: int
    fdc_id: int
    description: str
    category: Optional[str]
    quantity: float
    unit_name: str

    class Config:
        orm_mode = True
