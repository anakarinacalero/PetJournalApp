# TODO(pets): PetService, siguiendo FastApi/modules/users/service.py
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from FastApi.modules.pets.repository import PetRepository
from FastApi.modules.pets.schemas import PetCreate, PetCreateResponse, PetUpdateResponse

class PetService:
    def __init__(self, db:AsyncSession):
        self.repo = PetRepository(db)

    async def get_by_id(self, pet_id: uuid.UUID):
        pet = await self.repo.get_by_id(pet_id)
        if pet is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pet not found")
        return pet
    
    async def create(self, pet: PetCreate)->PetCreateResponse:    
        owner_pets = await self.repo.get_by_user_id(pet.user_id)
        
        if pet.name in [p.name for p in owner_pets]:
            raise HTTPException(status.HTTP_409_CONFLICT, "Pet name already registered for this user")
        return await self.repo.create(pet=pet)
    

    async def update(self, pet_data: PetCreate) -> PetUpdateResponse:
        pet = await self.repo.get_by_id(pet_data.id)
        if pet is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pet not found")
        owner_pets = await self.repo.get_by_user_id(pet.user_id)
        if pet_data.name in [p.name for p in owner_pets if p.id != pet.id]:
            raise HTTPException(status.HTTP_409_CONFLICT, "Pet name already registered for this user")
        updated_pet = await self.repo.update(pet, **pet_data.model_dump(exclude_unset=True))
        return PetUpdateResponse.model_validate(updated_pet)
    
    async def delete(self, pet_id: uuid.UUID) -> None:
        pet = await self.repo.get_by_id(pet_id)
        if pet is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pet not found")
        await self.repo.delete(pet)