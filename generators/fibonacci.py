from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero


class GeneradorFibonacci:
    def __init__(self, semilla_x0: int, semilla_x1: int, modulo: int):
        self.semilla_x0 = semilla_x0
        self.semilla_x1 = semilla_x1
        self.modulo = modulo

    @staticmethod
    def validar(texto_x0: str, texto_x1: str, texto_m: str) -> tuple[int, int, int]:
        x0 = validar_entero(texto_x0, "X0")
        x1 = validar_entero(texto_x1, "X1")
        m = validar_entero(texto_m, "Módulo m")

        if m <= 1:
            raise ValueError("El módulo m debe ser mayor que 1.")
        if x0 < 0 or x0 >= m or x1 < 0 or x1 >= m:
            raise ValueError("Las semillas deben cumplir 0 <= Xi < m.")
        if x0 == 0 and x1 == 0:
            raise ValueError("Las semillas X0 y X1 no pueden ser ambas 0.")

        return x0, x1, m

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        filas: list[list[str]] = []
        valores_u: list[float] = []
        advertencias: list[str] = []
        vistos: dict[int | tuple[int, ...], int] = {(self.semilla_x0, self.semilla_x1): 0}
        anterior = self.semilla_x0
        actual = self.semilla_x1
        ciclo_reportado = False

        for indice in range(1, cantidad + 1):
            siguiente = (anterior + actual) % self.modulo
            ui = siguiente / self.modulo

            filas.append([str(indice), str(anterior), str(actual), str(siguiente), f"{ui:.6f}"])
            valores_u.append(ui)

            estado = (actual, siguiente)
            if not ciclo_reportado:
                mensaje = detectar_estado_repetido(estado, vistos, indice)
                if mensaje:
                    advertencias.append(mensaje)
                    ciclo_reportado = True

            anterior, actual = actual, siguiente

        return ResultadoGenerador(
            metodo="Fibonacci",
            parametros={"X0": self.semilla_x0, "X1": self.semilla_x1, "m": self.modulo},
            encabezados=["i", "Xi-2", "Xi-1", "Xi", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
