import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from FastApi.core.security import get_current_user
from FastApi.infrastructure.db import get_db
from FastApi.modules.users.models import User
from FastApi.modules.users.schemas import Token, UserCreate, UserResponse, UserUpdate
from FastApi.modules.users.service import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.register(payload)


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    return await service.authenticate(form_data.username, form_data.password)


@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users/{id}", response_model=UserResponse)
async def get_user(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    if current_user.id != id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your resource")
    return await service.get_by_id(id)


@router.put("/users/{id}", response_model=UserResponse)
async def update_user(
    id: uuid.UUID,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    if current_user.id != id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your resource")
    return await service.update(id, payload)


@router.delete("/users/{id}")
async def delete_user(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    if current_user.id != id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your resource")
    await service.delete(id)
    return {"message": "User deleted successfully"}
