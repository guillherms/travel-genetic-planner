from pydantic import BaseModel

class FileSchema(BaseModel):
    places: str