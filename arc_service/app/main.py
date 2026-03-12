from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="TizWildin Hub ARC", version="0.1.0")
app.include_router(router)

@app.get("/")
def root():
    return {
        "service": "TizWildin Hub ARC",
        "status": "ok",
        "message": "ARC authority layer for plugin hub"
    }
