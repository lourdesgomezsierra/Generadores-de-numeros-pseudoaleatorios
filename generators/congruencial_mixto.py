from math import gcd

from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero


def factores_primos(numero: int) -> list[int]:
    factores: list[int] = []
    divisor = 2
    while divisor * divisor <= numero:
        if numero % divisor == 0:
            factores.append(divisor)
            while numero % divisor == 0:
                numero //= divisor
        divisor += 1 if divisor == 2 else 2
    if numero > 1:
        factores.append(numero)
    return factores


class GeneradorCongruencialMixto:
    def __init__(self, semilla_x0: int, multiplicador: int, constante: int, modulo: int):
        self.semilla_x0 = semilla_x0
        self.multiplicador = multiplicador
        self.constante = constante
        self.modulo = modulo

    @staticmethod
    def validar(texto_x0: str, texto_a: str, texto_c: str, texto_m: str) -> tuple[int, int, int, int]:
        x0 = validar_entero(texto_x0, "X0")
        a = validar_entero(texto_a, "Multiplicador a")
        c = validar_entero(texto_c, "Constante c")
        m = validar_entero(texto_m, "Módulo m")

        if m <= 1:
            raise ValueError("El módulo m debe ser mayor que 1.")
        if x0 < 0 or x0 >= m:
            raise ValueError("X0 debe cumplir 0 <= X0 < m.")
        if a <= 0:
            raise ValueError("El multiplicador a debe ser mayor que 0.")
        if c < 0 or c >= m:
            raise ValueError("La constante c debe cumplir 0 <= c < m.")

        return x0, a, c, m

    @staticmethod
    def validar_hull_dobell(multiplicador: int, constante: int, modulo: int) -> tuple[bool, list[str]]:
        errores: list[str] = []

        if gcd(constante, modulo) != 1:
            errores.append("mcd(c, m) debe ser 1.")

        for factor in factores_primos(modulo):
            if (multiplicador - 1) % factor != 0:
                errores.append(f"a - 1 debe ser divisible por el factor primo {factor} de m.")

        if modulo % 4 == 0 and (multiplicador - 1) % 4 != 0:
            errores.append("si m es múltiplo de 4, a - 1 también debe ser múltiplo de 4.")

        return len(errores) == 0, errores

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        filas: list[list[str]] = []
        valores_u: list[float] = []
        advertencias: list[str] = []
        vistos: dict[int | tuple[int, ...], int] = {self.semilla_x0: 0}
        xi = self.semilla_x0
        ciclo_reportado = False

        for indice in range(1, cantidad + 1):
            operacion = self.multiplicador * xi + self.constante
            siguiente = operacion % self.modulo
            ui = siguiente / self.modulo

            filas.append([str(indice), str(xi), str(operacion), str(siguiente), f"{ui:.6f}"])
            valores_u.append(ui)

            if not ciclo_reportado:
                mensaje = detectar_estado_repetido(siguiente, vistos, indice)
                if mensaje:
                    advertencias.append(mensaje)
                    ciclo_reportado = True

            xi = siguiente

        return ResultadoGenerador(
            metodo="Congruencia Lineal Mixto",
            parametros={"X0": self.semilla_x0, "a": self.multiplicador, "c": self.constante, "m": self.modulo},
            encabezados=["i", "Xi", "a * Xi + c", "Xi+1", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
