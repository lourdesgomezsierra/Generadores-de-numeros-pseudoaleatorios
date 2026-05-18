from dataclasses import dataclass


@dataclass
class ResultadoGenerador:
    metodo: str
    parametros: dict[str, int | str]
    encabezados: list[str]
    filas: list[list[str]]
    valores_u: list[float]
    advertencias: list[str]


def validar_entero(texto: str, nombre: str) -> int:
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
    if estado in vistos:
        return f"Advertencia: se detectó un ciclo desde la iteración {vistos[estado]} hasta la {indice}."
    vistos[estado] = indice
    return None
