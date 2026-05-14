#not use due to false matching
import os
import requests
from dotenv import load_dotenv

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")


def get_nutrition_from_food_name(food_name: str) -> dict:
    if not USDA_API_KEY:
        raise RuntimeError("Missing USDA_API_KEY in .env")

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        "api_key": USDA_API_KEY,
        "query": food_name,
        "pageSize": 5
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(f"USDA API error: {response.text}")

    data = response.json()
    foods = data.get("foods", [])

    if not foods:
        raise RuntimeError(f"No food found from USDA for: {food_name}")

    food = foods[0]
    nutrients = food.get("foodNutrients", [])

    calories = 0
    protein = 0

    for n in nutrients:
        nutrient_name = str(
            n.get("nutrientName") or n.get("name") or ""
        ).lower()

        unit_name = str(n.get("unitName", "")).lower()

        value = n.get("value")
        if value is None:
            value = n.get("amount", 0)

        value = value or 0

        if "energy" in nutrient_name and unit_name in ["kcal", "calorie"]:
            calories = value

        if "protein" in nutrient_name:
            protein = value

    return {
        "food_name": food.get("description", food_name),
        "quantity": "100 g",
        "calories": round(calories),
        "protein": round(protein, 2),
    }