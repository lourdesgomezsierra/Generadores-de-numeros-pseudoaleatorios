from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero


class GeneradorCongruencialMultiplicativo:
    def __init__(self, semilla_x0: int, multiplicador: int, modulo: int):
        self.semilla_x0 = semilla_x0
        self.multiplicador = multiplicador
        self.modulo = modulo

    @staticmethod
    def validar(texto_x0: str, texto_a: str, texto_m: str) -> tuple[int, int, int]:
        x0 = validar_entero(texto_x0, "X0")
        a = validar_entero(texto_a, "Multiplicador a")
        m = validar_entero(texto_m, "Módulo m")

        if x0 <= 0:
            raise ValueError("X0 debe ser mayor que 0.")
        if a <= 0:
            raise ValueError("El multiplicador a debe ser mayor que 0.")
        if m <= 1:
            raise ValueError("El módulo m debe ser mayor que 1.")
        if x0 >= m:
            raise ValueError("X0 debe ser menor que m.")

        return x0, a, m

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        filas: list[list[str]] = []
        valores_u: list[float] = []
        advertencias: list[str] = []
        vistos: dict[int | tuple[int, ...], int] = {self.semilla_x0: 0}
        xi = self.semilla_x0
        degeneracion_reportada = False
        ciclo_reportado = False

        for indice in range(1, cantidad + 1):
            operacion = self.multiplicador * xi
            siguiente = operacion % self.modulo
            ui = siguiente / self.modulo

            filas.append([str(indice), str(xi), str(operacion), str(siguiente), f"{ui:.6f}"])
            valores_u.append(ui)

            if siguiente == 0 and not degeneracion_reportada:
                advertencias.append(f"Advertencia: degeneración a 0 en la iteración {indice}.")
                degeneracion_reportada = True
            if not ciclo_reportado:
                mensaje = detectar_estado_repetido(siguiente, vistos, indice)
                if mensaje:
                    advertencias.append(mensaje)
                    ciclo_reportado = True

            xi = siguiente

        return ResultadoGenerador(
            metodo="Congruencial Multiplicativo",
            parametros={"X0": self.semilla_x0, "a": self.multiplicador, "m": self.modulo},
            encabezados=["i", "Xi", "a * Xi", "Xi+1", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
