from fastapi import FastAPI
from pydantic import BaseModel
from typing import List,Optional
from datetime import datetime
class FoodTextInput(BaseModel):
    text:str

class FoodItem(BaseModel):
    food_name:str
    quantity:str
    meal_type:Optional[str]="snack"
    calories: int
    protein:float
    source: str="manual"

class FoodLog(FoodItem):
    id: int
    eaten_at:str

class WeeklySummaryItem(BaseModel):
    day:str
    total_calories:int
    total_protein: float


app=FastAPI(
    title="AI Food Tracker API",
    version="0.1.0"
)

food_logs = [
    {
        "id": 1,
        "food_name": "Boiled egg",
        "quantity": "2 pcs",
        "meal_type": "breakfast",
        "calories": 140,
        "protein": 12.0,
        "source": "manual",
        "eaten_at": "2026-05-13T08:00:00"
    },
    {
        "id": 2,
        "food_name": "Rice",
        "quantity": "1 bowl",
        "meal_type": "lunch",
        "calories": 220,
        "protein": 4.0,
        "source": "manual",
        "eaten_at": "2026-05-13T12:00:00"
    }
]

@app.get("/")
def root():
    return {"message":"AI Food Tracker API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Food Tracker API is running"
    }

@app.post("/analyze-food")
def analyze_food(data: FoodTextInput):
    return {
        "original_text":data.text,
        "items":[
            {
                "food_name":"Boiled egg",
                "quantity":"2 pcs",
                "calories": 140,
                "protein":12.0,
                "source":"ai_estimate"
            },
            {
                "food_name":"Rice",
                "quantity":"1 bowl",
                "calories": 220,
                "protein":4.0,
                "source": "ai_estimate"
            }
        ]

    }

@app.post("/food-logs")
def create_food_log(item: FoodItem):
    new_log={
        "id":len(food_logs)+1,
        "food_name": item.food_name,
        "quantity":item.quantity,
        "meal_type":item.meal_type,
        "calories":item.calories,
        "protein":item.protein,
        "source":item.source,
        "eaten_at": datetime.now().isoformat()
    }

    food_logs.append(new_log)

    return {
        "message":"Food log saved",
        "data":new_log
    }

@app.get("/food-logs/today")
def get_today_logs():
    return food_logs

@app.get("/food-logs/weekly")
def get_weekly_summary():
    return [
        {"day": "2026-05-07", "total_calories": 1800, "total_protein": 90},
        {"day": "2026-05-08", "total_calories": 2100, "total_protein": 105},
        {"day": "2026-05-09", "total_calories": 1900, "total_protein": 95},
        {"day": "2026-05-10", "total_calories": 2300, "total_protein": 120},
        {"day": "2026-05-11", "total_calories": 1750, "total_protein": 85},
        {"day": "2026-05-12", "total_calories": 2000, "total_protein": 100},
        {"day": "2026-05-13", "total_calories": 360, "total_protein": 16},
    ]

@app.delete("/food-logs/{log_id}")
def delete_food_log(log_id:int):
    global food_logs
    food_logs=[log for log in food_logs if log["id"] != log_id]
    return {"message":"Food log deleted"}

@app.put("/food-logs/{log_id}")
def update_food_log(log_id:int,item:FoodItem):
    for log in food_logs:
        if log["id"]==log_id:
            log.pudate({
                "food_name":item.food_name,
                "quantity":item.quantity,
                "meal_type":item.meal_type,
                "calories":item.calories,
                "protein": item.protein,
                "source":item.source
            })
            return {"message":"Food log updated","data":log}
    return {"message":"Food log not found"}
