import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from FastApi.core.security import get_current_user
from FastApi.infrastructure.db import get_db
from FastApi.modules.pets.schemas import PetCreate
from FastApi.modules.pets.service import PetService
router = APIRouter()

# TODO(pets): implementar endpoints de mascotas siguiendo
# FastApi/modules/users/router.py como referencia (router delgado -> Depends(service)).


def get_pet_service(db: AsyncSession = Depends(get_db)) -> PetService:
    return PetService(db)


@router.get("/pets/me")
async def get_my_pets(
    current_user=Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    return await service.get_by_user_id(current_user.id)

@router.post("/pet")
async def create_pet(
    payload: PetCreate,
    current_user=Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    return await service.create(current_user.id, payload)


@router.get("/pet/{id}")
async def get_pet(
    id: uuid.UUID,
    current_user=Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    pet = await service.get_by_id(id)
    if pet.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your resource")
    return pet

@router.put("/pet/{id}")
async def update_pet(
    id: uuid.UUID,
    payload: PetCreate,
    current_user=Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    pet = await service.get_by_id(id)
    if pet.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your resource")
    return await service.update(id, payload)


@router.delete("/pet/{id}")
async def delete_pet(
    id: uuid.UUID,
    current_user=Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    pet = await service.get_by_id(id)
    if pet.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your resource")
    await service.delete(id)
    return {"message": "Pet deleted successfully"}  