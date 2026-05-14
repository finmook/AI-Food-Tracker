import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def parse_food_text(text: str) -> dict:
    prompt = f"""
You are a nutrition parser for a food tracker app.

Convert this user text into JSON:
"{text}"

Rules:
- Extract the main food name.
- Extract quantity.
- Detect meal_type: breakfast, lunch, dinner, or snack.
- Estimate calories and protein based on the quantity.
- source must be "ai".
- If the text contains multiple foods, return each food as a separate item in items.
- Return only valid JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "food_name": {"type": "string"},
                                "quantity": {"type": "string"},
                                "meal_type": {"type": "string"},
                                "calories": {"type": "integer"},
                                "protein": {"type": "number"},
                                "source": {"type": "string"},
                            },
                            "required": [
                                "food_name",
                                "quantity",
                                "meal_type",
                                "calories",
                                "protein",
                                "source",
                            ],
                        },
                    }
                },
                "required": ["items"],
            }
        ),
    )

    return json.loads(response.text)