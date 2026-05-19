from dataclasses import dataclass


@dataclass
class ResultadoGenerador:
    """Estructura que almacena los resultados de un generador"""
    metodo: str  # Nombre del generador (Fibonacci, Mixto, etc)
    parametros: dict[str, int | str]  # Parámetros usados (X0, a, c, m, etc)
    encabezados: list[str]  # Nombres de columnas
    filas: list[list[str]]  # Datos de cada iteración
    valores_u: list[float]  # Números normalizados [0,1)
    advertencias: list[str]  # Ciclos o degeneraciones detectadas


def validar_entero(texto: str, nombre: str) -> int:
    """Convierte string a int, valida que no esté vacío"""
    valor = texto.strip()
    if not valor:
        raise ValueError(f"{nombre} no puede estar vacío.")
    try:
        return int(valor)
    except ValueError as exc:
        raise ValueError(f"{nombre} debe ser un número entero.") from exc


def detectar_estado_repetido(
    estado: int | tuple[int, ...],
    vistos: dict[int | tuple[int, ...], int],
    indice: int,
) -> str | None:
    """Detecta ciclos: si un estado ya fue visto, hay ciclo"""
    if estado in vistos:  # Si el estado existe, hay ciclo
        return f"Advertencia: se detectó un ciclo desde la iteración {vistos[estado]} hasta la {indice}."
    vistos[estado] = indice  # Registra este estado
    return None  # Sin ciclo
