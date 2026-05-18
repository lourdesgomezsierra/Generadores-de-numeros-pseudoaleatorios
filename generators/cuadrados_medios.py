from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero


class GeneradorCuadradosMedios:
    def __init__(self, digitos: int, semilla_x0: int):
        self.digitos = digitos
        self.semilla_x0 = semilla_x0
        self.modulo = 10**digitos

    @staticmethod
    def validar(texto_digitos: str, texto_x0: str) -> tuple[int, int]:
        digitos = validar_entero(texto_digitos, "Cantidad de dígitos")
        semilla = texto_x0.strip()

        if digitos <= 1:
            raise ValueError("La cantidad de dígitos debe ser mayor que 1.")
        if not semilla:
            raise ValueError("Debe ingresar la semilla X0.")
        if not semilla.isdigit():
            raise ValueError("La semilla X0 debe contener solo dígitos.")
        if len(semilla) != digitos:
            raise ValueError(f"La semilla X0 debe tener exactamente {digitos} dígitos.")

        x0 = int(semilla)
        if x0 <= 0:
            raise ValueError("La semilla X0 debe ser positiva y no puede ser 0.")

        return digitos, x0

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        filas: list[list[str]] = []
        valores_u: list[float] = []
        advertencias = ["Nota: los cuadrados se completan con ceros a la izquierda cuando es necesario."]
        vistos: dict[int | tuple[int, ...], int] = {self.semilla_x0: 0}
        xi = self.semilla_x0
        degeneracion_reportada = False
        ciclo_reportado = False

        for indice in range(1, cantidad + 1):
            cuadrado = xi**2
            cuadrado_rellenado = str(cuadrado).zfill(2 * self.digitos)
            inicio = (len(cuadrado_rellenado) - self.digitos) // 2
            digitos_centrales = cuadrado_rellenado[inicio : inicio + self.digitos]
            siguiente = int(digitos_centrales)
            ui = siguiente / self.modulo

            filas.append(
                [
                    str(indice),
                    str(xi).zfill(self.digitos),
                    str(cuadrado),
                    cuadrado_rellenado,
                    digitos_centrales,
                    str(siguiente).zfill(self.digitos),
                    f"{ui:.6f}",
                ]
            )
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
            metodo="Cuadrados Medios",
            parametros={"dígitos": self.digitos, "X0": str(self.semilla_x0).zfill(self.digitos)},
            encabezados=["i", "Xi", "Xi^2", "Xi^2 con ceros", "Dígitos centrales", "Xi+1", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
