from pydantic import BaseModel

class FileSchema(BaseModel):
    places: str
    latitude: float
    longitude: float
    mon: int | str
    tue: int | str
    wed: int | str
    thu: int | str
    fri: int | str
    sat: int | str
    sun: int | str
    estimated_duration_min: int
    priority: int