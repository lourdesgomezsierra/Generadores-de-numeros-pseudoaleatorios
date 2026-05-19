from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero


class GeneradorProductoMedio:
    """Producto Medio: Xi = dígitos centrales de (Xi-1 * Xi)"""
    
    def __init__(self, digitos: int, semilla_x0: int, semilla_x1: int):
        self.digitos = digitos  # Cantidad de dígitos para semillas
        self.semilla_x0 = semilla_x0
        self.semilla_x1 = semilla_x1
        self.modulo = 10**digitos  # Usado para normalizar

    @staticmethod
    def validar(texto_digitos: str, texto_x0: str, texto_x1: str) -> tuple[int, int, int]:
        """Valida: dígitos > 1, semillas con 'dígitos' dígitos, ambas > 0"""
        digitos = validar_entero(texto_digitos, "Cantidad de dígitos")
        x0_texto = texto_x0.strip()
        x1_texto = texto_x1.strip()

        if digitos <= 1:
            raise ValueError("La cantidad de dígitos debe ser mayor que 1.")
        for nombre, valor in (("X0", x0_texto), ("X1", x1_texto)):
            if not valor:
                raise ValueError(f"Debe ingresar la semilla {nombre}.")
            if not valor.isdigit():
                raise ValueError(f"La semilla {nombre} debe contener solo dígitos.")
            if len(valor) != digitos:
                raise ValueError(f"La semilla {nombre} debe tener exactamente {digitos} dígitos.")

        x0 = int(x0_texto)
        x1 = int(x1_texto)
        if x0 <= 0 or x1 <= 0:
            raise ValueError("Las semillas X0 y X1 deben ser positivas y no pueden ser 0.")

        return digitos, x0, x1

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        """Genera: multiplica dos semillas, extrae dígitos centrales, normaliza. Detecta ciclos"""
        filas: list[list[str]] = []
        valores_u: list[float] = []
        advertencias = ["Nota: los productos se completan con ceros a la izquierda cuando es necesario."]
        vistos: dict[int | tuple[int, ...], int] = {(self.semilla_x0, self.semilla_x1): 0}
        anterior = self.semilla_x0  # Xi-1
        actual = self.semilla_x1    # Xi
        degeneracion_reportada = False
        ciclo_reportado = False

        for indice in range(1, cantidad + 1):
            producto = anterior * actual  # PASO 1: Multiplica
            producto_rellenado = str(producto).zfill(2 * self.digitos)  # PASO 2: Rellena con ceros
            inicio = (len(producto_rellenado) - self.digitos) // 2  # PASO 3: Calcula centro
            digitos_centrales = producto_rellenado[inicio : inicio + self.digitos]  # Extrae centrales
            siguiente = int(digitos_centrales)  # PASO 4: Nuevo Xi
            ui = siguiente / self.modulo  # Normaliza

            filas.append(
                [
                    str(indice),
                    str(anterior).zfill(self.digitos),
                    str(actual).zfill(self.digitos),
                    str(producto),
                    producto_rellenado,
                    digitos_centrales,
                    str(siguiente).zfill(self.digitos),
                    f"{ui:.6f}",
                ]
            )
            valores_u.append(ui)

            # Detecta degeneración
            if siguiente == 0 and not degeneracion_reportada:
                advertencias.append(f"Advertencia: degeneración a 0 en la iteración {indice}.")
                degeneracion_reportada = True
            # Detecta ciclos
            estado = (actual, siguiente)
            if not ciclo_reportado:
                mensaje = detectar_estado_repetido(estado, vistos, indice)
                if mensaje:
                    advertencias.append(mensaje)
                    ciclo_reportado = True

            anterior, actual = actual, siguiente  # Desplaza ventana

        return ResultadoGenerador(
            metodo="Producto Medio",
            parametros={
                "dígitos": self.digitos,
                "X0": str(self.semilla_x0).zfill(self.digitos),
                "X1": str(self.semilla_x1).zfill(self.digitos),
            },
            encabezados=["i", "Xi-1", "Xi", "Xi-1 * Xi", "Producto con ceros", "Dígitos centrales", "Xi+1", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
