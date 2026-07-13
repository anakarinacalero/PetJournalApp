import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from FastApi.infrastructure.db import Base
from FastApi.modules.users.models import User

class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), index=True)
    species: Mapped[str] = mapped_column(String(50))
    breed: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column()
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, foreign_key="users.id",  ondelete="CASCADE")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="pets")