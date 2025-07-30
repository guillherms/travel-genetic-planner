
from prompt import get_system_instructions 
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

class OpenAi:
    def __init__(self, place_name:str, start_date:datetime, end_date:datetime):
        self.place_name = place_name
        self.start_date = start_date
        self.end_date = end_date
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model="gpt-4"
    
    def generate_suggestion_tourist_points(self):
        trip_days = self._count_number_of_days()
        return self._get_places_tourist_points(trip_days)
    
    def _count_number_of_days(self)-> int:
        start_date = self.start_date
        end_date = self.end_date
        delta = end_date - start_date
        return delta.days + 1
        
    def _get_places_tourist_points(self, trip_days:int):
        resposta = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": get_system_instructions(trip_days)
                },
                {
                    "role": "user",
                    "content": self.place_name
                }
            ],
            model=self.model
        )
        return resposta.choices[0].message.content