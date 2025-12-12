from typing import Dict

def calc_bmi(weight_kg: float, height_cm: float) -> float:
    if not height_cm or height_cm <= 0:
        return 0.0
    h_m = height_cm / 100.0
    return weight_kg / (h_m * h_m)

def bmr_mifflin_segor(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    # Mifflin-St Jeor
    s = 5 if gender and gender.lower() == "male" else -161
    return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + s

def activity_multiplier(level: str) -> float:
    level = (level or "").lower()
    return {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725
    }.get(level, 1.2)

def calorie_target(bmr: float, activity_level: str, goal: str = "maintain") -> float:
    cal = bmr * activity_multiplier(activity_level)
    if goal == "lose":
        return cal - 500
    elif goal == "gain":
        return cal + 300
    return cal

def macros_from_calories(calories: float, protein_pct=0.25, fat_pct=0.25, carbs_pct=0.5) -> Dict[str, float]:
    # calories to grams: protein 4 kcal/g, carbs 4 kcal/g, fat 9 kcal/g
    protein_g = (calories * protein_pct) / 4
    fat_g = (calories * fat_pct) / 9
    carbs_g = (calories * carbs_pct) / 4
    return {"calories": round(calories,1), "protein_g": round(protein_g,1), "fat_g": round(fat_g,1), "carbs_g": round(carbs_g,1)}

def nutrition_profile_from_user(user: dict, goal: str = "maintain"):
    # user dict must contain weight_kg, height_cm, age, gender, activity_level
    weight = user.get("weight_kg")
    height = user.get("height_cm")
    age = user.get("age", 30)
    gender = user.get("gender", "male")
    activity = user.get("activity_level", "sedentary")
    bmi = calc_bmi(weight, height)
    bmr = bmr_mifflin_segor(weight, height, age, gender)
    calories = calorie_target(bmr, activity, goal)
    macros = macros_from_calories(calories)
    return {"bmi": round(bmi,1), "bmr": round(bmr,1), "nutrition": macros}
