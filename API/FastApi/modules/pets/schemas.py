# TODO(pets): PetCreate/PetUpdate/PetResponse, siguiendo FastApi/modules/users/schemas.py
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PetBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    species: str = Field(min_length=2, max_length=50)
    breed: str = Field(min_length=2, max_length=50)
    age: int = Field(gt=0)

class PetCreate(PetBase):
    user_id: uuid.UUID

class PetCreateResponse(PetBase):
    created_at: datetime= Field(default_factory=datetime.utcnow)
    message: str = Field(default="Pet created successfully")

class PetUpdateResponse(PetBase):
     Updated_at: datetime= Field(default_factory=datetime.utcnow)
     message: str = Field(default="Pet updated successfully")

