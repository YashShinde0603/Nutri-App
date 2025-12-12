# app/api/pantry.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.pantry import PantryItemCreate, PantryItemOut
from app.models.pantry import PantryItem
from app.services.usda_client import USDAClient
from typing import List, Optional
from rapidfuzz import fuzz, process

from app.services.nutrition_planner import aggregate_pantry_nutrients, plan_daily_from_targets
from app.utils.security import get_current_user

router = APIRouter(prefix="/pantry", tags=["pantry"])
client = USDAClient()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PantryItemOut)
def add_pantry_item(payload: PantryItemCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ensure user matches authenticated user
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only add items to your own pantry")

    # Optionally fetch USDA data snapshot (silent if network unreachable)
    description = payload.description
    category = payload.category
    try:
        usda = client.get_food(payload.fdc_id)
        if usda:
            description = usda.get("description") or description
            category = usda.get("foodCategory") or category
    except Exception:
        # swallow; use given description/category
        pass

    item = PantryItem(
        user_id=payload.user_id,
        fdc_id=payload.fdc_id,
        description=description,
        category=category,
        quantity=payload.quantity,
        unit_name=payload.unit_name
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=List[PantryItemOut])
def list_pantry(user_id: int = Query(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # allow only owner to fetch their pantry
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only list your own pantry")
    items = db.query(PantryItem).filter(PantryItem.user_id == user_id).all()
    return items


@router.get("/search")
def search_pantry(user_id: int = Query(...), q: str = Query(..., min_length=1), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only search your own pantry")
    # simple fuzzy search over pantry descriptions (local items)
    items = db.query(PantryItem).filter(PantryItem.user_id == user_id).all()
    choices = {str(i.id): i for i in items}
    texts = {str(i.id): i.description for i in items}
    # use rapidfuzz to get best matches
    results = process.extract(q, texts, scorer=fuzz.WRatio, limit=25)
    out = []
    for key, score, _index in results:
        if score < 30:
            continue
        out.append({"item": choices[key], "score": score})
    # return cleaned
    return [{"id": o["item"].id, "description": o["item"].description, "fdc_id": o["item"].fdc_id, "category": o["item"].category, "quantity": o["item"].quantity, "unit_name": o["item"].unit_name, "score": o["score"]} for o in out]


@router.get("/aggregate")
def aggregate_user_pantry(user_id: int = Query(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only aggregate your own pantry")
    """
    Aggregate estimated nutrients across all pantry items for the given user.
    Returns totals and a breakdown per item (estimates).
    """
    pantry = db.query(PantryItem).filter(PantryItem.user_id == user_id).all()
    if not pantry:
        raise HTTPException(status_code=400, detail="Pantry is empty.")
    aggregation = aggregate_pantry_nutrients(pantry, client)
    return aggregation


@router.get("/weekly-diet")
def weekly_diet(user_id: int = Query(...), goal: Optional[str] = "maintain", current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only request a plan for your own pantry")
    """
    Improved weekly diet planner:
     - computes user nutrition targets via pyhealthify (same as before)
     - aggregates pantry nutrients
     - uses a simple greedy planner to propose a 7-day plan and estimate per-day totals
    """
    from app.models.user import User
    from app.services.pyhealthify import nutrition_profile_from_user

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = {
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "age": user.age or 30,
        "gender": user.gender or "male",
        "activity_level": user.activity_level or "sedentary"
    }
    profile_nut = nutrition_profile_from_user(profile, goal=goal)

    pantry = db.query(PantryItem).filter(PantryItem.user_id == user_id).all()
    if not pantry:
        raise HTTPException(status_code=400, detail="Pantry is empty. Add some items first.")

    aggregation = aggregate_pantry_nutrients(pantry, client)
    pantry_breakdown = aggregation["breakdown"]
    totals = aggregation["totals"]

    planner_result = plan_daily_from_targets(profile_nut, pantry_breakdown, meals_per_day=3)

    return {
        "targets": profile_nut,
        "pantry_totals": totals,
        "planner": planner_result,
        "notes": {
            "assumptions": [
                "USDA nutrient values are interpreted per 100g when portion information is unavailable.",
                "Pantry 'quantity' is treated as number of portions when USDA portion gramWeight exists, otherwise as number of 100g units.",
                "Planner uses a greedy allocation and does not persist changes to pantry quantities.",
                "Some USDA items may not report all nutrients; missing values are shown as null and will affect accuracy."
            ]
        }
    }
