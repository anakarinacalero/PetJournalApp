import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from FastApi.infrastructure.db import Base

if TYPE_CHECKING:
    from FastApi.modules.pets.models import Pet


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

    #Un usuario puede tener muchas mascotas, por lo que se establece una relación uno a muchos con la tabla de mascotas.
    pets:Mapped[list["Pet"]] =relationship("Pet", passive_deletes=True, back_populates="user", cascade="all, delete-orphan")
