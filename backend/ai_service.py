import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def parse_food_text(text:str)->dict:
    prompt = f"""
            You are a nutrition parser for a food tracking app.

            Convert this user text into JSON:
            "{text}"

            Rules:
            - Estimate calories and protein if not provided.
            - meal_type must be one of: breakfast, lunch, dinner, snack.
            - source must be "ai".
            - Return only valid JSON.
            """
    response=client.models.generate_content(
                  model="gemini-2.5-flash",
                  contents=prompt,
                  config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema={
                              "type":"object",
                              "properties":{
                                    "food_name":{"type":"string"},
                                    "quantity":{"type":"string"},
                                    "meal_type":{"type":"string"},
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
                  ),
    )
    return json.loads(response.text)