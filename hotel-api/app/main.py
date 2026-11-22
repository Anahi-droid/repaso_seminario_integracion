# app/main.py
from fastapi import FastAPI

from app.habitaciones import router

app = FastAPI(title="API de Habitaciones", version="1.0.0")
app.include_router(router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"mensaje": "Hola desde FastAPI + uv + Habitaciones"}