import uuid

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from FastApi.core.auth_service import AuthService
from FastApi.infrastructure.db import get_db

from FastApi.modules.pets.repository import PetRepository
from FastApi.modules.pets.schemas import PetCreate, PetResponse, PetUpdate


class PetService:
    def __init__(self, db: AsyncSession):
        self.repo = PetRepository(db)

    async def get_pets_by_user(self, user_id: uuid.UUID) -> list[PetResponse]:
        owner_pets = await self.repo.get_by_user_id(user_id)
        return owner_pets
    
    def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
        return AuthService(db)

    async def get_by_id(self, pet_id: uuid.UUID) -> PetResponse:
        pet = await self.repo.get_by_id(pet_id)
        if pet is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pet not found")
        return PetResponse.model_validate(pet)

    async def create(self, data: PetCreate) -> PetResponse:
        owner_pets = await self.repo.get_by_user_id(data.user_id)
        if data.name in [p.name for p in owner_pets]:
            raise HTTPException(status.HTTP_409_CONFLICT, "Pet name already registered for this user")

        pet = await self.repo.create(
            name=data.name,
            species=data.species,
            breed=data.breed,
            birth_date=data.birth_date,
            sex=data.sex,
            user_id=data.user_id,
        )
        return PetResponse.model_validate(pet)

    async def update(self, pet_id: uuid.UUID, data: PetUpdate) -> PetResponse:
        pet = await self.repo.get_by_id(pet_id)
        if pet is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pet not found")

        fields = data.model_dump(exclude_unset=True)
        if "name" in fields:
            owner_pets = await self.repo.get_by_user_id(pet.user_id)
            if fields["name"] in [p.name for p in owner_pets if p.id != pet.id]:
                raise HTTPException(status.HTTP_409_CONFLICT, "Pet name already registered for this user")

        updated_pet = await self.repo.update(pet, **fields)
        return PetResponse.model_validate(updated_pet)

    async def delete(self, pet_id: uuid.UUID) -> None:
        pet = await self.repo.get_by_id(pet_id)
        if pet is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pet not found")
        await self.repo.delete(pet)
