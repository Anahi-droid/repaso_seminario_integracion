# app/materias.py — primera parte
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import HABITACIONES
from app.esquemas import Habitacion, HabitacionActualizar, HabitacionCrear

router = APIRouter(prefix="/habitaciones", tags=["habitaciones"])


def obtener_habitacion(codigo: str) -> dict:
    """Devuelve el diccionario de la habitacion o lanza 404."""
    for habitacion in HABITACIONES:
        if habitacion["codigo"] == codigo.upper():
            return habitacion
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la habitacion '{codigo}'",
    )


HabitacionEncontrada = Annotated[dict, Depends(obtener_habitacion)]

# app/materias.py — segunda parte: el CRUD

@router.get("", response_model=list[Habitacion])
def listar_habitaciones(
    piso: Annotated[int | None, Query(ge=1, le=20)] = None,
    solo_con_balcon: bool = False,
) -> list[dict]:
    resultado = HABITACIONES
    if piso is not None:
        resultado = [h for h in resultado if h["piso"] == piso]
    if solo_con_balcon:
        resultado = [h for h in resultado if h["con_balcon"]]
    return resultado

@router.post("", response_model=Habitacion, status_code=status.HTTP_201_CREATED)
def crear_habitacion(nueva: HabitacionCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in HABITACIONES):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La habitacion '{nueva.codigo}' ya existe",
        )
    HABITACIONES.append(nueva.model_dump())
    return HABITACIONES[-1]


@router.get("/{codigo}", response_model=Habitacion)
def ver_habitacion(habitacion: HabitacionEncontrada) -> dict:
    return habitacion


@router.put("/{codigo}", response_model=Habitacion)
def actualizar_habitacion(cambios: HabitacionActualizar, habitacion: HabitacionEncontrada) -> dict:
    habitacion.update(cambios.model_dump(exclude_unset=True))
    return habitacion


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_habitacion(habitacion: HabitacionEncontrada) -> None:
    HABITACIONES.remove(habitacion)


# app/materias.py — ¡ANTES de la ruta /{codigo}!


@router.get("/cotizacion")
def cotizacion(
    noches: Annotated[int, Query(ge=1, le=30)],
    piso: Annotated[int | None, Query(ge=1, le=20)] = None,
) -> dict:
    seleccion = [h for h in HABITACIONES if piso is None or h["piso"] == piso]
    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay habitaciones en el piso {piso}",
        )

    suma_tarifas = sum(h["tarifa_noche"] for h in seleccion)
    con_balcon = sum(1 for h in seleccion if h["con_balcon"])

    ingreso_base = suma_tarifas * noches
    descuento_aplicado = noches >= 7
    ingreso_estimado = round(ingreso_base * 0.9, 2) if descuento_aplicado else ingreso_base

    return {
        "habitaciones": len(seleccion),
        "noches": noches,
        "tarifa_promedio": round(suma_tarifas / len(seleccion), 2),
        "ingreso_base": ingreso_base,
        "descuento_aplicado": descuento_aplicado,
        "ingreso_estimado": ingreso_estimado,
        "porcentaje_con_balcon": round(con_balcon * 100 / len(seleccion), 1),
    }

@router.get("/disponibilidad")
def disponibilidad(
    ocupadas: Annotated[list[str] | None, Query()] = None,
) -> dict:
    if not HABITACIONES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay habitaciones registradas",
        )

    codigos_ocupados = {c.upper() for c in (ocupadas or [])}

    total = 0
    cantidad_ocupadas = 0
    libres = 0
    ingreso_potencial_libres = 0
    mas_economica_libre = None
    tarifa_minima = None

    for h in HABITACIONES:
        total += 1
        if h["codigo"] in codigos_ocupados:
            cantidad_ocupadas += 1
        else:
            libres += 1
            ingreso_potencial_libres += h["tarifa_noche"]
            if tarifa_minima is None or h["tarifa_noche"] < tarifa_minima:
                tarifa_minima = h["tarifa_noche"]
                mas_economica_libre = h["codigo"]

    return {
        "total": total,
        "ocupadas": cantidad_ocupadas,
        "libres": libres,
        "porcentaje_ocupacion": round(cantidad_ocupadas * 100 / total, 1),
        "ingreso_potencial_libres": ingreso_potencial_libres,
        "mas_economica_libre": mas_economica_libre,
    }