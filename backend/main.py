from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime, timedelta

from database import supabase
from ai_service import parse_food_text


class FoodTextInput(BaseModel):
    text: str


class FoodItem(BaseModel):
    food_name: str
    quantity: str
    meal_type: Optional[str] = "snack"
    calories: int
    protein: float
    source: str = "manual"


class FoodLog(FoodItem):
    id: int
    eaten_at: str


class WeeklySummaryItem(BaseModel):
    day: str
    total_calories: int
    total_protein: float


app = FastAPI(
    title="AI Food Tracker API",
    version="0.1.0"
)


def build_final_items(ai_result: dict) -> list:
    final_items = []

    for item in ai_result.get("items", []):
        final_items.append({
            "food_name": item.get("food_name", "unknown food"),
            "quantity": item.get("quantity", "1 serving"),
            "meal_type": item.get("meal_type", "snack"),
            "calories": item.get("calories", 0),
            "protein": item.get("protein", 0),
            "source": "ai_estimate",
        })

    return final_items


@app.get("/")
def root():
    return {"message": "AI Food Tracker API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Food Tracker API is running"
    }


@app.post("/analyze-food")
def analyze_food(data: FoodTextInput):
    try:
        ai_result = parse_food_text(data.text)
        final_items = build_final_items(ai_result)

        return {
            "original_text": data.text,
            "ai_result": ai_result,
            "final_items": final_items
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/food-logs")
def create_food_log(item: FoodItem):
    try:
        new_log = item.model_dump()
        new_log["eaten_at"] = datetime.now().isoformat()

        response = (
            supabase
            .table("food_logs")
            .insert(new_log)
            .execute()
        )

        return {
            "message": "Food log saved",
            "data": response.data[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/food-logs/ai")
def create_food_log_from_ai(data: FoodTextInput):
    try:
        ai_result = parse_food_text(data.text)
        final_items = build_final_items(ai_result)

        if not final_items:
            raise HTTPException(status_code=400, detail="No food items detected")

        logs_to_insert = []

        for item in final_items:
            logs_to_insert.append({
                "food_name": item["food_name"],
                "quantity": item["quantity"],
                "meal_type": item["meal_type"],
                "calories": item["calories"],
                "protein": item["protein"],
                "source": item["source"],
                "eaten_at": datetime.now().isoformat()
            })

        response = (
            supabase
            .table("food_logs")
            .insert(logs_to_insert)
            .execute()
        )

        return {
            "message": "AI food logs saved",
            "original_text": data.text,
            "ai_result": ai_result,
            "final_items": final_items,
            "data": response.data
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/food-logs")
def get_all_food_logs():
    try:
        response = (
            supabase
            .table("food_logs")
            .select("*")
            .order("eaten_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/food-logs/today")
def get_today_logs():
    try:
        today = date.today().isoformat()

        response = (
            supabase
            .table("food_logs")
            .select("id,food_name,quantity,meal_type,calories,protein,source,eaten_at,created_at")
            .gte("eaten_at", f"{today}T00:00:00")
            .lte("eaten_at", f"{today}T23:59:59")
            .order("eaten_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/food-logs/weekly")
def get_weekly_summary():
    try:
        start_date = date.today() - timedelta(days=6)

        response = (
            supabase
            .table("food_logs")
            .select("*")
            .gte("eaten_at", f"{start_date.isoformat()}T00:00:00")
            .order("eaten_at", desc=True)
            .execute()
        )

        logs = response.data
        summary = {}

        for i in range(7):
            current_day = start_date + timedelta(days=i)

            summary[current_day.isoformat()] = {
                "day": current_day.isoformat(),
                "total_calories": 0,
                "total_protein": 0
            }

        for log in logs:
            day = log["eaten_at"][:10]

            if day in summary:
                summary[day]["total_calories"] += log.get("calories", 0) or 0
                summary[day]["total_protein"] += log.get("protein", 0) or 0

        return list(summary.values())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/food-logs/{log_id}")
def delete_food_log(log_id: int):
    try:
        response = (
            supabase
            .table("food_logs")
            .delete()
            .eq("id", log_id)
            .execute()
        )

        return {
            "message": "Food log deleted",
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/food-logs/{log_id}")
def update_food_log(log_id: int, item: FoodItem):
    try:
        response = (
            supabase
            .table("food_logs")
            .update(item.model_dump())
            .eq("id", log_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Food log not found")

        return {
            "message": "Food log updated",
            "data": response.data[0]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))