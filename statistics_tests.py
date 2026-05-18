from dataclasses import dataclass
from math import sqrt

import numpy as np


@dataclass
class ResultadoChiCuadrado:
    encabezados: list[str]
    filas: list[list[str]]
    chi_calculado: float
    chi_tabla: float
    frecuencia_esperada: float
    acepta_h0: bool
    decision: str


@dataclass
class ResultadoCorrelacionSerial:
    encabezados: list[str]
    filas: list[list[str]]


def _validar_alpha(alpha: float) -> None:
    if not 0 < alpha < 1:
        raise ValueError("α debe ser un valor decimal entre 0 y 1.")


def _obtener_chi2_ppf() -> object:
    try:
        from scipy.stats import chi2
    except ModuleNotFoundError as exc:
        raise RuntimeError("Falta instalar SciPy. Ejecute: pip install scipy") from exc
    return chi2.ppf


def _obtener_t_ppf() -> object:
    try:
        from scipy.stats import t
    except ModuleNotFoundError as exc:
        raise RuntimeError("Falta instalar SciPy. Ejecute: pip install scipy") from exc
    return t.ppf


def calcular_chi_cuadrado(valores_u: list[float], alpha: float = 0.05, k: int = 10) -> ResultadoChiCuadrado:
    """Calcula el test χ² de uniformidad usando 10 intervalos iguales en [0, 1]."""
    _validar_alpha(alpha)
    if not valores_u:
        raise ValueError("No hay valores Ui generados para evaluar.")

    valores = np.asarray(valores_u, dtype=float)
    n = len(valores)
    frecuencia_esperada = n / k
    if frecuencia_esperada < 5:
        raise ValueError("No se cumple la condición npi >= 5 para el test χ².")

    frecuencias, bordes = np.histogram(valores, bins=k, range=(0, 1))
    filas = generar_tabla_chi(frecuencias, bordes, frecuencia_esperada)
    chi_calculado = float(np.sum(((frecuencias - frecuencia_esperada) ** 2) / frecuencia_esperada))
    chi_tabla = float(_obtener_chi2_ppf()(1 - alpha, k - 1))
    acepta_h0 = chi_calculado < chi_tabla
    decision = (
        "Se acepta H0: la serie es uniforme"
        if acepta_h0
        else "Se rechaza H0: la serie no es uniforme"
    )

    return ResultadoChiCuadrado(
        encabezados=["Intervalo", "fi", "npi", "fi - npi", "(fi - npi)^2", "(fi - npi)^2 / npi"],
        filas=filas,
        chi_calculado=chi_calculado,
        chi_tabla=chi_tabla,
        frecuencia_esperada=frecuencia_esperada,
        acepta_h0=acepta_h0,
        decision=decision,
    )


def generar_tabla_chi(frecuencias: np.ndarray, bordes: np.ndarray, frecuencia_esperada: float) -> list[list[str]]:
    filas: list[list[str]] = []
    for indice, frecuencia in enumerate(frecuencias):
        diferencia = frecuencia - frecuencia_esperada
        diferencia_cuadrada = diferencia**2
        aporte = diferencia_cuadrada / frecuencia_esperada
        intervalo = f"[{bordes[indice]:.1f}, {bordes[indice + 1]:.1f})"
        if indice == len(frecuencias) - 1:
            intervalo = f"[{bordes[indice]:.1f}, {bordes[indice + 1]:.1f}]"
        filas.append(
            [
                intervalo,
                str(int(frecuencia)),
                f"{frecuencia_esperada:.2f}",
                f"{diferencia:.2f}",
                f"{diferencia_cuadrada:.2f}",
                f"{aporte:.4f}",
            ]
        )
    return filas


def calcular_correlacion_serial(valores_u: list[float], alpha: float = 0.05) -> ResultadoCorrelacionSerial:
    """Calcula correlación serial para h = 1, 2 y 3 con test t bilateral."""
    _validar_alpha(alpha)
    if len(valores_u) < 6:
        raise ValueError("Se requieren más valores Ui para calcular correlación serial.")

    filas: list[list[str]] = []
    n = len(valores_u)
    t_ppf = _obtener_t_ppf()

    for h in (1, 2, 3):
        rho = _calcular_rho_h(valores_u, h)
        t_calculado, t_tabla, decision, acepta_h0 = calcular_test_t(rho, n, h, alpha, t_ppf)
        filas.append(
            [
                str(h),
                f"{rho:.6f}",
                f"{t_calculado:.6f}",
                f"{t_tabla:.6f}",
                decision,
                "pasa" if acepta_h0 else "falla",
            ]
        )

    return ResultadoCorrelacionSerial(
        encabezados=["h", "ρ̂h", "t calculado", "t tabla", "Decisión", "Estado"],
        filas=filas,
    )


def _calcular_rho_h(valores_u: list[float], h: int) -> float:
    valores = np.asarray(valores_u, dtype=float)
    n = len(valores)
    promedio_productos = float(np.sum(valores[: n - h] * valores[h:]) / (n - h))
    return (promedio_productos - 0.25) / (1 / 12)


def calcular_test_t(
    rho_h: float,
    n: int,
    h: int,
    alpha: float,
    t_ppf: object | None = None,
) -> tuple[float, float, str, bool]:
    if abs(rho_h) >= 1:
        t_calculado = float("inf") if rho_h > 0 else float("-inf")
    else:
        t_calculado = rho_h * sqrt(n - h - 2) / sqrt(1 - rho_h**2)

    if t_ppf is None:
        t_ppf = _obtener_t_ppf()
    t_tabla = float(t_ppf(1 - alpha / 2, n - h - 2))
    acepta_h0 = abs(t_calculado) < t_tabla
    decision = (
        "Se acepta H0: no existe correlación"
        if acepta_h0
        else "Se rechaza H0: existe correlación"
    )
    return t_calculado, t_tabla, decision, acepta_h0


def generar_scatter(valores_u: list[float]) -> tuple[np.ndarray, np.ndarray]:
    valores = np.asarray(valores_u, dtype=float)
    return valores[:-1], valores[1:]
