from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.api.metrics import router as metrics_router
from backend.app.api.offers import router as offers_router
from backend.app.api.campaigns import router as campaigns_router
from backend.app.api.operations import router as operations_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(offers_router)
app.include_router(metrics_router)
app.include_router(campaigns_router)
app.include_router(operations_router)
app.include_router(recommendations_router)
