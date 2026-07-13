# TODO(pets): PetRepository(AsyncSession), siguiendo FastApi/modules/users/repository.py
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from FastApi.modules.pets.models import Pet
from FastApi.modules.pets.schemas import PetCreate, PetCreateResponse

class PetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pet_id:uuid.UUID) -> Pet | None:
        return await self.db.get(Pet, pet_id)
    
    async def get_by_name(self, name: str) -> Pet | None:
        result = await self.db.execute(select(Pet).where(Pet.name==name))
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Pet]:
        result = await self.db.execute(select(Pet).where(Pet.user_id == user_id))
        return result.scalars().all()
    
    async def create(self, *, pet: PetCreate) -> Pet:
        pet_obj = Pet(name=pet.name, species=pet.species, breed=pet.breed, age=pet.age, user_id=pet.user_id)
        self.db.add(pet_obj)
        await self.db.commit()
        await self.db.refresh(pet_obj)
        return pet_obj
    
    async def update(self, pet: Pet, **fields) -> Pet:
        for key, value in fields.items():
            setattr(pet, key, value)
        await self.db.commit()
        await self.db.refresh(pet)
        return pet
    
    async def delete(self, pet: Pet) -> None:
        await self.db.delete(pet)
        await self.db.commit()