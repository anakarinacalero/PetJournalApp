from uuid import UUID
from pydantic import BaseModel
from datetime import date, datetime



class Pet(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    species: str
    breed: str
    birth_date: date
    gender: str
    current_weight: float