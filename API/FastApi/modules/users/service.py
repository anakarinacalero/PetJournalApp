import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from FastApi.core.security import create_access_token, hash_password, verify_password
from FastApi.modules.users.repository import UserRepository
from FastApi.modules.users.schemas import Token, UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> UserResponse:
        if await self.repo.get_by_username(data.username):
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already registered")
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        user = await self.repo.create(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
        )
        return UserResponse.model_validate(user)

    async def authenticate(self, username: str, password: str) -> Token:
        user = await self.repo.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return Token(access_token=create_access_token(subject=str(user.id)))

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return UserResponse.model_validate(user)

    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        fields = data.model_dump(exclude_unset=True)
        if "password" in fields:
            fields["password_hash"] = hash_password(fields.pop("password"))
        if "email" in fields:
            existing = await self.repo.get_by_email(fields["email"])
            if existing is not None and existing.id != user_id:
                raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        user = await self.repo.update(user, **fields)
        return UserResponse.model_validate(user)

    async def delete(self, user_id: uuid.UUID) -> None:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        await self.repo.delete(user)
