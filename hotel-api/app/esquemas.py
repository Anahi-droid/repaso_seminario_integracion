# app/esquemas.py
from pydantic import BaseModel, Field


class HabitacionBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=60)
    tarifa_noche: int = Field(ge=10, le=1000)
    piso: int = Field(ge=1, le=20)
    con_balcon: bool = False


class HabitacionCrear(HabitacionBase):
    # Tres letras mayúsculas + tres dígitos: MAT101, PRG201...
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$")


class HabitacionActualizar(BaseModel):
    # Todos opcionales: en un PUT parcial, lo que no se envía no se toca.
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    tarifa_noche: int | None = Field(default=None, ge=10, le=1000)
    piso: int | None = Field(default=None, ge=1, le=20)
    con_balcon: bool | None = None


class Habitacion(HabitacionCrear):
    """Lo que la API devuelve: los cinco campos completos."""