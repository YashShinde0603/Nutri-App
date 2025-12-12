# app/services/nutrition_planner.py
from typing import Dict, List, Tuple, Optional
from app.services.usda_client import USDAClient

# nutrient keys we'll extract and normalize (values are grams or kcal per reference weight)
NUTRIENT_KEY_ALIASES = {
    "energy": ["energy", "energy (kcal)", "energy (kcal)"],
    "protein": ["protein", "protein, total"],
    "fat": ["total lipid", "total lipid (fat)", "fat", "total fat"],
    "carbs": ["carbohydrate", "carbohydrate, by difference", "carbohydrate, total"]
}

def _match_nutrient_name(name: str) -> Optional[str]:
    if not name:
        return None
    n = name.strip().lower()
    # quick mapping heuristics
    if "energy" in n and ("kcal" in n or "kcal" in name.lower() or "calorie" in n):
        return "energy"
    if "protein" in n:
        return "protein"
    if "lipid" in n or "fat" in n:
        return "fat"
    if "carbohydrate" in n or "carb" in n:
        return "carbs"
    return None

def extract_nutrients_from_usda(food_json: dict) -> Dict[str, Optional[float]]:
    """
    Returns nutrient dict with keys: calories (kcal), protein_g, fat_g, carbs_g
    Interpretation rules:
    - If foodNutrients list is present, we attempt to parse relevant nutrients.
    - Values are treated as 'per 100g' unless the nutrient data or foodPortions indicate otherwise.
    """
    # defaults
    out = {"calories": None, "protein_g": None, "fat_g": None, "carbs_g": None, "per_gram_multiplier": 0.01}
    # find nutrients
    nutrients = food_json.get("foodNutrients") or food_json.get("labelNutrients") or []
    for n in nutrients:
        name = n.get("nutrientName") or n.get("name") or n.get("nutrient", {}).get("name", "")
        amount = n.get("amount")
        unit = n.get("unitName") or n.get("unitName") or (n.get("nutrient", {}) or {}).get("unitName")
        if amount is None:
            continue
        key = _match_nutrient_name(name)
        if not key:
            continue
        # amount is typically per 100 g for foodNutrients in many datasets
        if key == "energy":
            # unit might be 'KCAL' or 'kcal'
            out["calories"] = float(amount)
        elif key == "protein":
            out["protein_g"] = float(amount)
        elif key == "fat":
            out["fat_g"] = float(amount)
        elif key == "carbs":
            out["carbs_g"] = float(amount)
    # if we have foodPortions with a gramWeight for a named portion, capture it
    gram_portion = None
    portions = food_json.get("foodPortions") or []
    for p in portions:
        gw = p.get("gramWeight")
        if gw and isinstance(gw, (int, float)):
            # pick the first reasonable gramWeight ( >5 g)
            if gw > 5:
                gram_portion = gw
                break
    # default multiplier: values found are likely per 100 g -> per gram multiplier = 0.01
    if gram_portion:
        out["portion_gram"] = gram_portion
    else:
        out["portion_gram"] = 100.0
    # ensure numeric values exist (if missing, leave None)
    return out

def estimate_nutrients_for_pantry_item(pantry_item: dict, usda_client: USDAClient) -> Dict:
    """
    pantry_item: object with keys: fdc_id, quantity, unit_name, description
    returns: dict with estimated total nutrients available from that pantry entry:
      {
          "fdc_id": ...,
          "description": ...,
          "available_grams": float,
          "per_100g": {calories, protein_g, fat_g, carbs_g},
          "total": {calories, protein_g, fat_g, carbs_g}
      }
    Interpretation rules for available_grams:
      - If USDA foodPortions exist and we have a gramWeight, then available_grams = quantity * gramWeight
      - Else assume quantity counts of 100 g units -> available_grams = quantity * 100
    """
    fdc_id = pantry_item.fdc_id
    food = usda_client.get_food(fdc_id)
    nutrients = extract_nutrients_from_usda(food)
    # determine grams available from pantry quantity
    qty = pantry_item.quantity or 1.0
    portion_gram = nutrients.get("portion_gram", 100.0)
    # treat pantry quantity as number of portions if portion_gram present
    available_grams = qty * portion_gram
    # compute per 100g baseline
    per_100g = {
        "calories": nutrients.get("calories"),
        "protein_g": nutrients.get("protein_g"),
        "fat_g": nutrients.get("fat_g"),
        "carbs_g": nutrients.get("carbs_g"),
    }
    # convert to totals given available grams (if per_100g values present)
    factor = available_grams / 100.0
    total = {}
    for k in ["calories", "protein_g", "fat_g", "carbs_g"]:
        v = per_100g.get(k)
        total[k] = round(v * factor, 2) if v is not None else None
    return {
        "fdc_id": fdc_id,
        "description": pantry_item.description,
        "available_grams": available_grams,
        "per_100g": per_100g,
        "total": total,
        "portion_gram": portion_gram
    }

def aggregate_pantry_nutrients(pantry_items: List, usda_client: USDAClient) -> Dict:
    """
    Return aggregated nutrients across the given pantry items.
    """
    agg = {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0}
    breakdown = []
    for p in pantry_items:
        info = estimate_nutrients_for_pantry_item(p, usda_client)
        tot = info["total"]
        for k in agg:
            val = tot.get(k)
            if val is not None:
                agg[k] += val
        breakdown.append(info)
    # round totals
    agg = {k: round(v, 2) for k, v in agg.items()}
    return {"totals": agg, "breakdown": breakdown}

def plan_daily_from_targets(targets: dict, pantry_breakdown: List[dict], meals_per_day: int = 3) -> Tuple[Dict, List]:
    """
    Simple greedy allocator:
      - For each day: for each meal, pick pantry items in rotation and allocate a portion (portion_gram)
        until we approximate the calorie target for that day.
    Returns:
      - day_plan: structure with per-day items and estimated totals & remaining inventory (simulated)
    This is intentionally simple and conservative.
    """
    daily_cal = targets.get("nutrition", {}).get("calories") or targets.get("calories") or 2000
    # copy available grams to simulate local inventory
    inventory = []
    for b in pantry_breakdown:
        inventory.append({
            "fdc_id": b["fdc_id"],
            "description": b["description"],
            "available_grams": b["available_grams"],
            "per_100g": b["per_100g"],
            "portion_gram": b["portion_gram"]
        })
    plan = []
    for day in range(7):
        day_used = []
        day_totals = {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0}
        # try to reach daily_cal by assigning up to meals_per_day * 2 portions (two portions per meal max)
        portion_goal = daily_cal
        attempts = 0
        # rotate through inventory
        inv_index = day % max(1, len(inventory))
        while day_totals["calories"] < portion_goal and attempts < len(inventory) * 4:
            item = inventory[inv_index % len(inventory)]
            inv_index += 1
            attempts += 1
            if item["available_grams"] < 1.0:
                continue
            # propose one portion
            pg = item["portion_gram"] or 100.0
            take_grams = min(pg, item["available_grams"])
            # compute nutrient contribution
