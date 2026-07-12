from contextlib import asynccontextmanager

from fastapi import FastAPI

from FastApi.infrastructure.db import Base, engine
from FastApi.modules.users.router import router as users_router

# from FastApi.modules.pets.router import router as pets_router            # TODO: activar cuando se implemente
# from FastApi.modules.health.router import router as health_router        # TODO: activar cuando se implemente
# from FastApi.modules.reminders.router import router as reminders_router  # TODO: activar cuando se implemente
# from FastApi.modules.ai.router import router as ai_router                # TODO: activar cuando se implemente


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="PetCare Journal API", lifespan=lifespan)
app.include_router(users_router, prefix="/api/v1")
