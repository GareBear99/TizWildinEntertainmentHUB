from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes import router
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="TizWildin Hub ARC", version="0.1.0", lifespan=lifespan)
app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "TizWildin Hub ARC",
        "status": "ok",
        "message": "ARC authority layer for plugin hub"
    }
