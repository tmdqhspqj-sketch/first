import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    admins_router,
    approvals_router,
    auth_router,
    internal_router,
    messages_router,
    rooms_router,
    users_router,
)
from app.seed import run_seed
from app.services.purge import purge_loop


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if os.environ.get("VERCEL") != "1":
        run_seed()
    task = None
    if os.environ.get("VERCEL") != "1":
        task = asyncio.create_task(purge_loop())
    yield
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Hong ERP", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(admins_router.router)
app.include_router(users_router.router)
app.include_router(approvals_router.router)
app.include_router(rooms_router.router)
app.include_router(messages_router.router)
app.include_router(internal_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
