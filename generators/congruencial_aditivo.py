from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero


class GeneradorCongruencialAditivo:
    def __init__(self, semillas: list[int], modulo: int):
        self.semillas = semillas
        self.modulo = modulo

    @staticmethod
    def validar(texto_semillas: str, texto_m: str) -> tuple[list[int], int]:
        if not texto_semillas.strip():
            raise ValueError("Debe ingresar las semillas iniciales separadas por coma.")

        partes = [valor.strip() for valor in texto_semillas.split(",") if valor.strip()]
        if len(partes) < 2:
            raise ValueError("El método aditivo requiere al menos 2 semillas iniciales.")

        try:
            semillas = [int(valor) for valor in partes]
        except ValueError as exc:
            raise ValueError("Las semillas deben ser números enteros separados por coma.") from exc

        modulo = validar_entero(texto_m, "Módulo m")
        if modulo <= 1:
            raise ValueError("El módulo m debe ser mayor que 1.")
        if any(semilla < 0 or semilla >= modulo for semilla in semillas):
            raise ValueError("Todas las semillas deben cumplir 0 <= Xi < m.")
        if all(semilla == 0 for semilla in semillas):
            raise ValueError("No todas las semillas pueden ser 0.")

        return semillas, modulo

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        filas: list[list[str]] = []
        valores_u: list[float] = []
        advertencias: list[str] = []
        valores_x = self.semillas.copy()
        k = len(self.semillas)
        vistos: dict[int | tuple[int, ...], int] = {tuple(valores_x): 0}
        ciclo_reportado = False

        for indice in range(1, cantidad + 1):
            x_rezagado = valores_x[-k]
            x_anterior = valores_x[-1]
            siguiente = (x_anterior + x_rezagado) % self.modulo
            ui = siguiente / self.modulo

            filas.append([str(indice), str(x_rezagado), str(x_anterior), str(siguiente), f"{ui:.6f}"])
            valores_x.append(siguiente)
            valores_u.append(ui)

            estado = tuple(valores_x[-k:])
            if not ciclo_reportado:
                mensaje = detectar_estado_repetido(estado, vistos, indice)
                if mensaje:
                    advertencias.append(mensaje)
                    ciclo_reportado = True

        parametros: dict[str, int | str] = {"cantidad_semillas": k, "m": self.modulo}
        parametros.update({f"X{indice}": semilla for indice, semilla in enumerate(self.semillas)})

        return ResultadoGenerador(
            metodo="Congruencial Aditivo",
            parametros=parametros,
            encabezados=["i", f"Xi-{k}", "Xi-1", "Xi", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
