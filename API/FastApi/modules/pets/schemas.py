import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PetBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    species: str = Field(min_length=2, max_length=50)
    breed: str = Field(min_length=2, max_length=50)
    birth_date: date
    sex: str = Field(min_length=1, max_length=10)


class PetCreate(PetBase):
    user_id: uuid.UUID


class PetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    species: str | None = Field(default=None, min_length=2, max_length=50)
    breed: str | None = Field(default=None, min_length=2, max_length=50)
    birth_date: date | None = None
    sex: str | None = Field(default=None, min_length=1, max_length=10)


class PetResponse(PetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    deleted_at: datetime | None
