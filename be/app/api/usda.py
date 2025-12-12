from fastapi import APIRouter, HTTPException, Query
from app.services.usda_client import USDAClient

router = APIRouter(prefix="/usda", tags=["usda"])
client = USDAClient()


@router.get("/search")
def search_usda(q: str = Query(..., min_length=1), pageSize: int = 25, pageNumber: int = 1):
    try:
        data = client.search_foods(q, page_size=pageSize, page_number=pageNumber)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/food/{fdc_id}")
def get_food(fdc_id: int):
    try:
        data = client.get_food(fdc_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
