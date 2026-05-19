from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero

# - ResultadoGenerador: estructura para almacenar los resultados
# - detectar_estado_repetido: función para identificar ciclos
# - validar_entero: función para validar entrada de números

class GeneradorCuadradosMedios:
    def __init__(self, digitos: int, semilla_x0: int):
        """
        Inicializa el generador con parámetros
            digitos: cantidad de dígitos para la semilla y extracción
            semilla_x0: valor inicial (X0) con 'digitos' dígitos
        """
        self.digitos = digitos
        self.semilla_x0 = semilla_x0
        # Módulo = 10^n, usado para normalizar: Ui = Xi / 10^n
        self.modulo = 10**digitos

    @staticmethod
    def validar(texto_digitos: str, texto_x0: str) -> tuple[int, int]:
        """
        Valida los parámetros ingresados por el usuario.

        """
        # Convierte y valida la cantidad de dígitos
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

        # Convierte a número entero
        x0 = int(semilla)
        
        if x0 <= 0:
            raise ValueError("La semilla X0 debe ser positiva y no puede ser 0.")

        return digitos, x0

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        """
        Args:
            cantidad: número de iteraciones (default: 1000)
            
        Returns:
            ResultadoGenerador con filas, valores normalizados y advertencias
        """
        # Inicializa estructuras de datos
        filas: list[list[str]] = []  # Almacena cada fila de la tabla de resultados
        valores_u: list[float] = []  # Almacena los valores normalizados [0,1)
        # Nota: este método tiende a degenerarse (llegar a 0), lo advierte
        advertencias = ["Nota: los cuadrados se completan con ceros a la izquierda cuando es necesario."]
        vistos: dict[int | tuple[int, ...], int] = {self.semilla_x0: 0}  # Detecta ciclos
        xi = self.semilla_x0  # Semilla actual
        degeneracion_reportada = False  # Bandera para reportar degeneración una sola vez
        ciclo_reportado = False  # Bandera para reportar ciclo una sola vez

        # Bucle principal: genera 'cantidad' números
        for indice in range(1, cantidad + 1):
            # PASO 1: Elevar Xi al cuadrado
            cuadrado = xi**2
            
            # PASO 2: Rellenar con ceros a la izquierda
            # El resultado debe tener 2*n dígitos (si Xi tiene n dígitos)
            # Ej: si n=4 y Xi=1234, Xi^2=1,522,756 → rellena a 01522756
            cuadrado_rellenado = str(cuadrado).zfill(2 * self.digitos)
            
            # PASO 3: Extraer los n dígitos centrales
            # Calcula el índice de inicio para extraer
            inicio = (len(cuadrado_rellenado) - self.digitos) // 2
            # Extrae los dígitos del centro
            digitos_centrales = cuadrado_rellenado[inicio : inicio + self.digitos]
            # Convierte a entero
            siguiente = int(digitos_centrales)
            
            # PASO 4: Normalizar a [0,1)
            ui = siguiente / self.modulo
            
            # Almacena fila de resultados para la tabla
            filas.append(
                [
                    str(indice),                           # Número de iteración
                    str(xi).zfill(self.digitos),          # Xi (rellenado)
                    str(cuadrado),                         # Xi^2 (sin rellenar)
                    cuadrado_rellenado,                    # Xi^2 (rellenado con ceros)
                    digitos_centrales,                     # Dígitos centrales extraídos
                    str(siguiente).zfill(self.digitos),   # Xi+1 (siguiente semilla)
                    f"{ui:.6f}",                           # Ui (normalizado)
                ]
            )
            valores_u.append(ui)

            # PASO 5: Detecta degeneración (cuando llega a 0)
            # Problema: si Xi+1 = 0, todas las iteraciones futuras serán 0
            if siguiente == 0 and not degeneracion_reportada:
                advertencias.append(f"Advertencia: degeneración a 0 en la iteración {indice}.")
                degeneracion_reportada = True
            
            # Detecta ciclos (cuando Xi+1 ya fue visto)
            if not ciclo_reportado:
                mensaje = detectar_estado_repetido(siguiente, vistos, indice)
                if mensaje:
                    advertencias.append(mensaje)
                    ciclo_reportado = True

            # Actualiza semilla para la próxima iteración
            xi = siguiente

        # Retorna objeto con todos los datos generados
        return ResultadoGenerador(
            metodo="Cuadrados Medios",
            parametros={"dígitos": self.digitos, "X0": str(self.semilla_x0).zfill(self.digitos)},
            encabezados=["i", "Xi", "Xi^2", "Xi^2 con ceros", "Dígitos centrales", "Xi+1", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
