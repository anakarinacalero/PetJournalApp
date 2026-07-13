import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from FastApi.modules.pets.models import Pet


class PetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pet_id: uuid.UUID) -> Pet | None:
        result = await self.db.execute(
            select(Pet).where(Pet.id == pet_id, Pet.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Pet | None:
        result = await self.db.execute(
            select(Pet).where(Pet.name == name, Pet.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Pet]:
        result = await self.db.execute(
            select(Pet).where(Pet.user_id == user_id, Pet.deleted_at.is_(None))
        )
        return result.scalars().all()

    async def create(
        self, *, name: str, species: str, breed: str, birth_date: date, sex: str, user_id: uuid.UUID
    ) -> Pet:
        pet_obj = Pet(
            name=name, species=species, breed=breed, birth_date=birth_date, sex=sex, user_id=user_id
        )
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
        pet.deleted_at = datetime.utcnow()
        await self.db.commit()
