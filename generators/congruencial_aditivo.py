from generators.resultado import ResultadoGenerador, detectar_estado_repetido, validar_entero
# - ResultadoGenerador: estructura para almacenar los resultados
# - detectar_estado_repetido: función para identificar ciclos
# - validar_entero: función para validar entrada de números


class GeneradorCongruencialAditivo:
    def __init__(self, semillas: list[int], modulo: int):
        """
        Inicializa el generador con parámetros.
        Args:
            semillas: lista de k semillas iniciales (mínimo 2)
            modulo: módulo m para la operación
        """
        self.semillas = semillas
        self.modulo = modulo

    @staticmethod
    def validar(texto_semillas: str, texto_m: str) -> tuple[list[int], int]:
        """
        Valida los parámetros ingresados por el usuario.
        Al menos 2 semillas (k >= 2)
        Todas son números enteros
        Módulo m > 1
        0 <= cada semilla < m
        No todas las semillas pueden ser 0 
        """
        if not texto_semillas.strip():
            raise ValueError("Debe ingresar las semillas iniciales separadas por coma.")

        # Parseea las semillas separadas por coma y elimina espacios
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
        
        #  cada semilla está en rango [0, m)
        if any(semilla < 0 or semilla >= modulo for semilla in semillas):
            raise ValueError("Todas las semillas deben cumplir 0 <= Xi < m.")
        
        if all(semilla == 0 for semilla in semillas):
            raise ValueError("No todas las semillas pueden ser 0.")

        return semillas, modulo

    def generar(self, cantidad: int = 1000) -> ResultadoGenerador:
        """
        Pasos en cada iteración:
        1. Obtener Xi-k (semilla más antigua de la ventana)
        2. Obtener Xi-1 (semilla más reciente de la ventana)
        3. Calcular: Xi = (Xi-k + Xi-1) mod m
        4. Normalizar: Ui = Xi / m
        5. Agregar Xi a la ventana (deslizante de tamaño k)
        6. Detectar ciclos verificando las últimas k semillas
        
        Args:
            cantidad: número de iteraciones (default: 1000)
            
        Returns:
            ResultadoGenerador con filas, valores normalizados y advertencias
        """
        # Inicializa estructuras de datos
        filas: list[list[str]] = []  # Tabla de resultados
        valores_u: list[float] = []  # Valores normalizados [0,1)
        advertencias: list[str] = []  # Mensajes de advertencia
        
        # Copia las semillas iniciales (mantiene una ventana deslizante)
        valores_x = self.semillas.copy()
        # k = cantidad de semillas iniciales
        k = len(self.semillas)
        
        # Diccionario para detectar ciclos: almacena tuplas de últimas k semillas
        # Clave: tupla de (X0, X1, ..., Xk-1), Valor: número de iteración
        vistos: dict[int | tuple[int, ...], int] = {tuple(valores_x): 0}
        ciclo_reportado = False

        # Bucle principal: genera 'cantidad' números
        for indice in range(1, cantidad + 1):
            # PASO 1: Obtiene la semilla más rezagada (Xi-k)
            # valores_x[-k] toma el elemento k posiciones desde el final
            x_rezagado = valores_x[-k]
            
            # PASO 2: Obtiene la semilla más reciente (Xi-1)
            # valores_x[-1] toma el último elemento
            x_anterior = valores_x[-1]
            
            # PASO 3: Calcula el siguiente valor
            # Fórmula: Xi = (Xi-k + Xi-1) mod m
            siguiente = (x_anterior + x_rezagado) % self.modulo
            
            # PASO 4: Normaliza a [0,1)
            ui = siguiente / self.modulo

            # Almacena fila de resultados
            filas.append([
                str(indice),           # Número de iteración
                str(x_rezagado),       # Xi-k (semilla rezagada)
                str(x_anterior),       # Xi-1 (semilla anterior)
                str(siguiente),        # Xi (nuevo valor calculado)
                f"{ui:.6f}",          # Ui (normalizado)
            ])
            valores_x.append(siguiente)  # Agregar a la ventana deslizante
            valores_u.append(ui)

            # PASO 5: Detecta ciclos en la ventana de últimas k semillas
            # Toma las últimas k posiciones: esto es la "ventana" actual
            estado = tuple(valores_x[-k:])
            if not ciclo_reportado:
                # Si el estado (últimas k semillas) ya fue visto, hay ciclo
                mensaje = detectar_estado_repetido(estado, vistos, indice)
                if mensaje:
                    advertencias.append(mensaje)
                    ciclo_reportado = True

        # Construye diccionario de parámetros para mostrar en resultados
        parametros: dict[str, int | str] = {"cantidad_semillas": k, "m": self.modulo}
        # Agrega cada semilla inicial: X0, X1, X2, etc.
        parametros.update({f"X{indice}": semilla for indice, semilla in enumerate(self.semillas)})

        # Retorna objeto con todos los datos generados
        return ResultadoGenerador(
            metodo="Congruencial Aditivo",
            parametros=parametros,
            # Encabezados: muestra Xi-k dinámicamente según cantidad de semillas
            encabezados=["i", f"Xi-{k}", "Xi-1", "Xi", "Ui"],
            filas=filas,
            valores_u=valores_u,
            advertencias=advertencias,
        )
