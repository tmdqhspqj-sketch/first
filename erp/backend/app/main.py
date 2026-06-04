from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import approvals_router, auth_router, messages_router, rooms_router, users_router
from app.seed import run_seed


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_seed()
    yield


app = FastAPI(title="Hong ERP", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(approvals_router.router)
app.include_router(rooms_router.router)
app.include_router(messages_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
