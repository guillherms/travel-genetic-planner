import os
from openai import OpenAI
from dotenv import load_dotenv
from core.utils.file_utils import FileUtils
from core.prompt.tourist_places import SYSTEM_INSTRUCTIONS


load_dotenv()

class OpenAi:
    def __init__(self,
                 top_p:float,
                 temperature: float,
                 place_name:str,
                 trip_days:int,):
        self.top_p = top_p
        self.temperature = temperature
        self.place_name = place_name
        self.trip_days = trip_days
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model="gpt-4"
        self.file_utils = FileUtils()
        
    def get_places_tourist_points(self):
        resposta = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self._get_system_instructions()
                },
                {
                    "role": "user",
                    "content": self.place_name
                }
            ],
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        open_ai_response =  resposta.choices[0].message.content
        return self.file_utils.from_string(open_ai_response)
    
    def _get_system_instructions(self):
        """
        Generate system instructions for the travel agent based on the destination and trip duration.
        
        Args:
            nome_cidade_pais_viagem (str): The name of the city and country for the trip.
            quantidade_dias_viagem (int): The number of days for the trip.
        
        Returns:
            str: Formatted system instructions.
        """
        return SYSTEM_INSTRUCTIONS.format(
            quantidade_dias_viagem=self.trip_days
        )