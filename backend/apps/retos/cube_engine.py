"""Motor del cubo de Rubik: calcula el estado a partir de una secuencia de movimientos.

El cubo se modela con los 26 cubies visibles (posiciones en {-1, 0, 1}).
Cada cubie guarda su posicion actual y una lista de stickers ``(normal, cara)``,
donde ``cara`` es la letra de la cara a la que pertenece en el estado resuelto.

Un movimiento rota la posicion y las normales de los cubies de su capa.

Notacion soportada (Singmaster): U, R, F, D, L, B con sufijos
``"", "'", "2"`` -> 18 movimientos.

Este modulo es Python puro (sin Django) para poder probarlo de forma aislada.
"""
from __future__ import annotations

import math

CARAS = ("U", "R", "F", "D", "L", "B")
SUFIJOS = ("", "'", "2")
MOVIMIENTOS = tuple(cara + sufijo for cara in CARAS for sufijo in SUFIJOS)

# cara -> (eje de rotacion, signo de la capa)
_EJE_CARA = {
    "U": ("y", 1),
    "D": ("y", -1),
    "R": ("x", 1),
    "L": ("x", -1),
    "F": ("z", 1),
    "B": ("z", -1),
}

_INDICE_EJE = {"x": 0, "y": 1, "z": 2}

_NORMAL_CARA = {
    (1, 0, 0): "R",
    (-1, 0, 0): "L",
    (0, 1, 0): "U",
    (0, -1, 0): "D",
    (0, 0, 1): "F",
    (0, 0, -1): "B",
}


def _rotacion(eje: str, grados: int):
    radianes = math.radians(grados)
    c = round(math.cos(radianes))
    s = round(math.sin(radianes))
    if eje == "x":
        return ((1, 0, 0), (0, c, -s), (0, s, c))
    if eje == "y":
        return ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def _matriz_vector(matriz, vector):
    return (
        matriz[0][0] * vector[0] + matriz[0][1] * vector[1] + matriz[0][2] * vector[2],
        matriz[1][0] * vector[0] + matriz[1][1] * vector[1] + matriz[1][2] * vector[2],
        matriz[2][0] * vector[0] + matriz[2][1] * vector[1] + matriz[2][2] * vector[2],
    )


def _cubies_iniciales():
    cubies = []
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == 0 and y == 0 and z == 0:
                    continue
                stickers = []
                for normal in ((x, 0, 0), (0, y, 0), (0, 0, z)):
                    if normal != (0, 0, 0):
                        stickers.append([normal, _NORMAL_CARA[normal]])
                cubies.append({"posicion": (x, y, z), "stickers": stickers})
    return cubies


def analizar_movimiento(movimiento: str):
    """Devuelve (cara, sufijo) o lanza ValueError."""
    if not movimiento:
        raise ValueError("Movimiento vacio")
    cara = movimiento[0].upper()
    sufijo = movimiento[1:]
    if cara not in _EJE_CARA or sufijo not in SUFIJOS:
        raise ValueError(f"Movimiento invalido: {movimiento!r}")
    return cara, sufijo


def _angulo(cara: str, sufijo: str) -> int:
    _, signo = _EJE_CARA[cara]
    # Giro horario visto desde fuera de la cara.
    base = -90 if signo > 0 else 90
    if sufijo == "'":
        return -base
    if sufijo == "2":
        return 180
    return base


def _aplicar(cubies, movimiento: str) -> None:
    cara, sufijo = analizar_movimiento(movimiento)
    eje, signo = _EJE_CARA[cara]
    rotacion = _rotacion(eje, _angulo(cara, sufijo))
    indice = _INDICE_EJE[eje]
    for cubie in cubies:
        if cubie["posicion"][indice] == signo:
            cubie["posicion"] = _matriz_vector(rotacion, cubie["posicion"])
            for sticker in cubie["stickers"]:
                sticker[0] = _matriz_vector(rotacion, sticker[0])


def _coordenadas_celda(cara: str, posicion):
    x, y, z = posicion
    if cara == "U":
        return z + 1, x + 1
    if cara == "D":
        return 1 - z, x + 1
    if cara == "F":
        return 1 - y, x + 1
    if cara == "B":
        return 1 - y, 1 - x
    if cara == "R":
        return 1 - y, 1 - z
    if cara == "L":
        return 1 - y, z + 1
    raise ValueError(f"Cara desconocida: {cara}")


def _renderizar(cubies):
    caras = {cara: [[None, None, None] for _ in range(3)] for cara in CARAS}
    for cubie in cubies:
        for normal, color in cubie["stickers"]:
            cara = _NORMAL_CARA[normal]
            fila, columna = _coordenadas_celda(cara, cubie["posicion"])
            caras[cara][fila][columna] = color
    return caras


def estado_desde_movimientos(movimientos) -> dict:
    """Aplica la secuencia de movimientos desde el estado resuelto."""
    cubies = _cubies_iniciales()
    for movimiento in movimientos:
        _aplicar(cubies, movimiento)
    return _renderizar(cubies)


def celdas(movimientos) -> str:
    """Representacion plana (54 caracteres) del estado del cubo."""
    caras = estado_desde_movimientos(movimientos)
    return "".join("".join(fila) for cara in CARAS for fila in caras[cara])


def esta_resuelto(movimientos) -> bool:
    caras = estado_desde_movimientos(movimientos)
    for filas in caras.values():
        centro = filas[1][1]
        if any(color != centro for fila in filas for color in fila):
            return False
    return True


def invertir_movimiento(movimiento: str) -> str:
    """Devuelve el movimiento inverso (R -> R', R' -> R, R2 -> R2)."""
    cara, sufijo = analizar_movimiento(movimiento)
    if sufijo == "2":
        return movimiento
    if sufijo == "'":
        return cara
    return cara + "'"


def invertir_secuencia(movimientos):
    """Invierte una secuencia completa (invierte cada giro y el orden)."""
    return [invertir_movimiento(m) for m in reversed(list(movimientos))]
