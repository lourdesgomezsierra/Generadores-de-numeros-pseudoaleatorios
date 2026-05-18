from collections.abc import Callable
from dataclasses import dataclass

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from generators import (
    GeneradorCongruencialAditivo,
    GeneradorCongruencialMixto,
    GeneradorCongruencialMultiplicativo,
    GeneradorCuadradosMedios,
    GeneradorFibonacci,
    GeneradorProductoMedio,
)
from generators.resultado import ResultadoGenerador

CANTIDAD_GENERADA = 1000


@dataclass(frozen=True)
class CampoFormulario:
    clave: str
    etiqueta: str
    placeholder: str = ""
    valor_inicial: str = ""
    opciones: tuple[str, ...] = ()


@dataclass(frozen=True)
class DefinicionMetodo:
    clave: str
    nombre: str
    categoria: str
    descripcion: str
    campos: tuple[CampoFormulario, ...]
    crear_resultado: Callable[[dict[str, str]], ResultadoGenerador]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Generadores pseudoaleatorios")
        self.resize(1180, 760)
        self.setMinimumSize(1000, 650)

        self.metodos = self._crear_definiciones_metodos()
        self.categoria_actual = ""
        self.metodo_actual: DefinicionMetodo | None = None
        self.resultado_actual: ResultadoGenerador | None = None
        self.entradas: dict[str, QLineEdit | QComboBox] = {}

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pantalla_inicio = self._crear_pantalla_inicio()
        self.pantalla_categoria = self._crear_pantalla_categoria()
        self.pantalla_generador = self._crear_pantalla_generador()

        self.stack.addWidget(self.pantalla_inicio)
        self.stack.addWidget(self.pantalla_categoria)
        self.stack.addWidget(self.pantalla_generador)

    def _crear_definiciones_metodos(self) -> dict[str, DefinicionMetodo]:
        return {
            "mixto": DefinicionMetodo(
                clave="mixto",
                nombre="Congruencia Lineal Mixto",
                categoria="congruenciales",
                descripcion="Genera Xi+1 = (a * Xi + c) mod m.",
                campos=(
                    CampoFormulario("x0", "Semilla X0"),
                    CampoFormulario("a", "Multiplicador a"),
                    CampoFormulario("c", "Constante c"),
                    CampoFormulario("m", "Módulo m"),
                ),
                crear_resultado=lambda datos: GeneradorCongruencialMixto(
                    *GeneradorCongruencialMixto.validar(datos["x0"], datos["a"], datos["c"], datos["m"])
                ).generar(CANTIDAD_GENERADA),
            ),
            "multiplicativo": DefinicionMetodo(
                clave="multiplicativo",
                nombre="Congruencial Multiplicativo",
                categoria="congruenciales",
                descripcion="Genera Xi+1 = (a * Xi) mod m.",
                campos=(
                    CampoFormulario("x0", "Semilla X0"),
                    CampoFormulario("a", "Multiplicador a"),
                    CampoFormulario("m", "Módulo m"),
                ),
                crear_resultado=lambda datos: GeneradorCongruencialMultiplicativo(
                    *GeneradorCongruencialMultiplicativo.validar(datos["x0"], datos["a"], datos["m"])
                ).generar(CANTIDAD_GENERADA),
            ),
            "aditivo": DefinicionMetodo(
                clave="aditivo",
                nombre="Congruencial Aditivo",
                categoria="congruenciales",
                descripcion="Usa varias semillas y combina Xi-1 con Xi-k módulo m.",
                campos=(
                    CampoFormulario("semillas", "Semillas iniciales"),
                    CampoFormulario("m", "Módulo m"),
                ),
                crear_resultado=lambda datos: GeneradorCongruencialAditivo(
                    *GeneradorCongruencialAditivo.validar(datos["semillas"], datos["m"])
                ).generar(CANTIDAD_GENERADA),
            ),
            "cuadrados": DefinicionMetodo(
                clave="cuadrados",
                nombre="Cuadrados Medios",
                categoria="no_congruenciales",
                descripcion="Eleva la semilla al cuadrado y toma sus dígitos centrales.",
                campos=(
                    CampoFormulario("digitos", "Número de dígitos de la semilla", opciones=("4", "6")),
                    CampoFormulario("x0", "Semilla X0"),
                ),
                crear_resultado=lambda datos: GeneradorCuadradosMedios(
                    *GeneradorCuadradosMedios.validar(datos["digitos"], datos["x0"])
                ).generar(CANTIDAD_GENERADA),
            ),
            "producto": DefinicionMetodo(
                clave="producto",
                nombre="Producto Medio",
                categoria="no_congruenciales",
                descripcion="Multiplica dos semillas consecutivas y toma los dígitos centrales.",
                campos=(
                    CampoFormulario("digitos", "Número de dígitos de la semilla", opciones=("4", "6")),
                    CampoFormulario("x0", "Semilla X0"),
                    CampoFormulario("x1", "Semilla X1"),
                ),
                crear_resultado=lambda datos: GeneradorProductoMedio(
                    *GeneradorProductoMedio.validar(datos["digitos"], datos["x0"], datos["x1"])
                ).generar(CANTIDAD_GENERADA),
            ),
            "fibonacci": DefinicionMetodo(
                clave="fibonacci",
                nombre="Fibonacci",
                categoria="no_congruenciales",
                descripcion="Genera Xi = (Xi-1 + Xi-2) mod m.",
                campos=(
                    CampoFormulario("x0", "Semilla X0"),
                    CampoFormulario("x1", "Semilla X1"),
                    CampoFormulario("m", "Módulo m"),
                ),
                crear_resultado=lambda datos: GeneradorFibonacci(
                    *GeneradorFibonacci.validar(datos["x0"], datos["x1"], datos["m"])
                ).generar(CANTIDAD_GENERADA),
            ),
        }

    def _crear_pantalla_inicio(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(46, 38, 46, 38)
        layout.setSpacing(22)

        titulo = QLabel("Generadores pseudoaleatorios")
        titulo.setObjectName("titulo")
        subtitulo = QLabel(
            "Aplicación para generar y analizar 1000 valores normalizados con métodos congruenciales y no congruenciales."
        )
        subtitulo.setObjectName("subtitulo")
        subtitulo.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(12)

        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(18)
        tarjetas.addWidget(
            self._crear_tarjeta_menu(
                "Métodos congruenciales",
                "Lineal mixto, multiplicativo y aditivo.",
                lambda: self._mostrar_categoria("congruenciales"),
            )
        )
        tarjetas.addWidget(
            self._crear_tarjeta_menu(
                "Métodos no congruenciales",
                "Cuadrados medios, producto medio y Fibonacci.",
                lambda: self._mostrar_categoria("no_congruenciales"),
            )
        )
        layout.addLayout(tarjetas)
        layout.addStretch()

        return pagina

    def _crear_pantalla_categoria(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(46, 38, 46, 38)
        layout.setSpacing(18)

        barra = QHBoxLayout()
        self.titulo_categoria = QLabel()
        self.titulo_categoria.setObjectName("titulo")
        boton_volver = QPushButton("Volver al menú")
        boton_volver.setObjectName("secundario")
        boton_volver.clicked.connect(self._volver_inicio)
        barra.addWidget(self.titulo_categoria)
        barra.addStretch()
        barra.addWidget(boton_volver)
        layout.addLayout(barra)

        self.descripcion_categoria = QLabel()
        self.descripcion_categoria.setObjectName("subtitulo")
        self.descripcion_categoria.setWordWrap(True)
        layout.addWidget(self.descripcion_categoria)

        self.layout_metodos = QGridLayout()
        self.layout_metodos.setSpacing(18)
        layout.addLayout(self.layout_metodos)
        layout.addStretch()

        return pagina

    def _crear_pantalla_generador(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        barra = QHBoxLayout()
        self.titulo_metodo = QLabel()
        self.titulo_metodo.setObjectName("titulo")
        boton_cambiar = QPushButton("Cambiar método")
        boton_cambiar.setObjectName("secundario")
        boton_cambiar.clicked.connect(self._volver_categoria)
        boton_menu = QPushButton("Volver al menú")
        boton_menu.setObjectName("secundario")
        boton_menu.clicked.connect(self._volver_inicio)
        barra.addWidget(self.titulo_metodo)
        barra.addStretch()
        barra.addWidget(boton_cambiar)
        barra.addWidget(boton_menu)
        layout.addLayout(barra)

        self.descripcion_metodo = QLabel()
        self.descripcion_metodo.setObjectName("subtitulo")
        self.descripcion_metodo.setWordWrap(True)
        layout.addWidget(self.descripcion_metodo)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, stretch=1)

        panel_formulario = self._crear_panel_formulario()
        panel_resultados = self._crear_panel_resultados()
        splitter.addWidget(panel_formulario)
        splitter.addWidget(panel_resultados)
        splitter.setSizes([360, 780])

        return pagina

    def _crear_panel_formulario(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        etiqueta = QLabel("Parámetros")
        etiqueta.setObjectName("seccion")
        layout.addWidget(etiqueta)

        self.formulario_layout = QVBoxLayout()
        self.formulario_layout.setSpacing(9)
        layout.addLayout(self.formulario_layout)

        self.combo_filas = QComboBox()
        self.combo_filas.addItems(["20", "50", "75", "100"])
        self.combo_filas.currentTextChanged.connect(self._actualizar_tabla_desde_selector)
        layout.addWidget(QLabel("Resultados visibles"))
        layout.addWidget(self.combo_filas)

        botones = QHBoxLayout()
        boton_generar = QPushButton("Generar")
        boton_generar.clicked.connect(self._generar)
        boton_limpiar = QPushButton("Limpiar")
        boton_limpiar.setObjectName("peligro")
        boton_limpiar.clicked.connect(self._limpiar)
        botones.addWidget(boton_generar)
        botones.addWidget(boton_limpiar)
        layout.addLayout(botones)

        ayuda = QLabel("Cada ejecución genera exactamente 1000 valores. La tabla solo cambia la cantidad de filas visibles.")
        ayuda.setObjectName("ayuda")
        ayuda.setWordWrap(True)
        layout.addWidget(ayuda)
        layout.addStretch()

        return panel

    def _crear_panel_resultados(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        resumen = QHBoxLayout()
        self.parametros_label = QLabel("Parámetros: -")
        self.parametros_label.setWordWrap(True)
        self.advertencias_label = QLabel("Advertencias: sin datos generados.")
        self.advertencias_label.setWordWrap(True)
        resumen.addWidget(self.parametros_label, 1)
        resumen.addWidget(self.advertencias_label, 1)
        layout.addLayout(resumen)

        self.tabla = QTableWidget(0, 0)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self.tabla, stretch=3)

        self.figura = Figure(figsize=(6, 3), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        layout.addWidget(self.canvas, stretch=2)
        self._dibujar_histograma([])

        return panel

    def _crear_tarjeta_menu(self, titulo: str, descripcion: str, accion: Callable[[], None]) -> QFrame:
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setMinimumHeight(170)
        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("seccion")
        texto = QLabel(descripcion)
        texto.setObjectName("subtitulo")
        texto.setWordWrap(True)
        boton = QPushButton("Seleccionar")
        boton.clicked.connect(lambda _checked=False: accion())

        layout.addWidget(etiqueta)
        layout.addWidget(texto)
        layout.addStretch()
        layout.addWidget(boton)
        return tarjeta

    def _mostrar_categoria(self, categoria: str) -> None:
        self.categoria_actual = categoria
        es_congruencial = categoria == "congruenciales"
        self.titulo_categoria.setText("Métodos congruenciales" if es_congruencial else "Métodos no congruenciales")
        self.descripcion_categoria.setText(
            "Seleccione el método congruencial que desea ejecutar."
            if es_congruencial
            else "Seleccione el método no congruencial que desea ejecutar."
        )

        self._vaciar_layout(self.layout_metodos)
        metodos = [metodo for metodo in self.metodos.values() if metodo.categoria == categoria]
        for indice, metodo in enumerate(metodos):
            tarjeta = self._crear_tarjeta_menu(metodo.nombre, metodo.descripcion, lambda m=metodo: self._mostrar_metodo(m))
            self.layout_metodos.addWidget(tarjeta, indice // 2, indice % 2)

        self.stack.setCurrentWidget(self.pantalla_categoria)

    def _mostrar_metodo(self, metodo: DefinicionMetodo) -> None:
        self.metodo_actual = metodo
        self.resultado_actual = None
        self.titulo_metodo.setText(metodo.nombre)
        self.descripcion_metodo.setText(metodo.descripcion)
        self._crear_campos_metodo(metodo)
        self._limpiar_resultados()
        self.stack.setCurrentWidget(self.pantalla_generador)

    def _crear_campos_metodo(self, metodo: DefinicionMetodo) -> None:
        self._vaciar_layout(self.formulario_layout)
        self.entradas = {}

        for campo in metodo.campos:
            etiqueta = QLabel(campo.etiqueta)
            if campo.opciones:
                entrada = QComboBox()
                entrada.addItems(campo.opciones)
            else:
                entrada = QLineEdit()
                entrada.setPlaceholderText(campo.placeholder)
                entrada.setText(campo.valor_inicial)
            self.formulario_layout.addWidget(etiqueta)
            self.formulario_layout.addWidget(entrada)
            self.entradas[campo.clave] = entrada

    def _generar(self) -> None:
        if self.metodo_actual is None:
            return

        datos = {clave: self._valor_campo(entrada) for clave, entrada in self.entradas.items()}
        try:
            if self.metodo_actual.clave == "mixto":
                resultado = self._generar_mixto_con_advertencia_hull(datos)
            else:
                resultado = self.metodo_actual.crear_resultado(datos)
        except ValueError as error:
            QMessageBox.warning(self, "Error de validación", str(error))
            return

        if resultado is None:
            return

        self.resultado_actual = resultado
        self._mostrar_resultado(resultado)

    def _generar_mixto_con_advertencia_hull(self, datos: dict[str, str]) -> ResultadoGenerador | None:
        x0, a, c, m = GeneradorCongruencialMixto.validar(datos["x0"], datos["a"], datos["c"], datos["m"])
        hull_valido, errores = GeneradorCongruencialMixto.validar_hull_dobell(a, c, m)

        if not hull_valido:
            mensaje = (
                "Los parámetros no cumplen las condiciones de Hull-Dobell:\n\n"
                + "\n".join(f"- {error}" for error in errores)
                + "\n\n¿Desea continuar igualmente con la generación?"
            )
            respuesta = QMessageBox.question(
                self,
                "Advertencia Hull-Dobell",
                mensaje,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if respuesta != QMessageBox.StandardButton.Yes:
                return None

        resultado = GeneradorCongruencialMixto(x0, a, c, m).generar(CANTIDAD_GENERADA)
        if not hull_valido:
            resultado.advertencias.insert(0, "Advertencia: no se cumplen las condiciones de Hull-Dobell.")
        return resultado

    def _valor_campo(self, campo: QLineEdit | QComboBox) -> str:
        if isinstance(campo, QComboBox):
            return campo.currentText()
        return campo.text()

    def _mostrar_resultado(self, resultado: ResultadoGenerador) -> None:
        parametros = " | ".join(f"{clave}: {valor}" for clave, valor in resultado.parametros.items())
        self.parametros_label.setText(f"Parámetros: {parametros}")
        self.advertencias_label.setText(
            "Advertencias: " + " ".join(resultado.advertencias)
            if resultado.advertencias
            else "Advertencias: no se detectaron ciclos ni degeneración en la muestra."
        )
        self._cargar_tabla(resultado)
        self._dibujar_histograma(resultado.valores_u)

    def _cargar_tabla(self, resultado: ResultadoGenerador) -> None:
        cantidad_visible = int(self.combo_filas.currentText())
        filas = resultado.filas[:cantidad_visible]

        self.tabla.clear()
        self.tabla.setColumnCount(len(resultado.encabezados))
        self.tabla.setRowCount(len(filas))
        self.tabla.setHorizontalHeaderLabels(resultado.encabezados)

        for fila_indice, fila in enumerate(filas):
            for columna_indice, valor in enumerate(fila):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(fila_indice, columna_indice, item)

        encabezado = self.tabla.horizontalHeader()
        encabezado.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        encabezado.setStretchLastSection(True)

    def _dibujar_histograma(self, valores: list[float]) -> None:
        self.figura.clear()
        eje = self.figura.add_subplot(111)
        eje.set_title("Histograma de frecuencias")
        eje.set_xlabel("Valores normalizados Ui")
        eje.set_ylabel("Frecuencia")
        eje.set_xlim(0, 1)
        eje.grid(axis="y", alpha=0.25)

        if valores:
            eje.hist(valores, bins=10, range=(0, 1), color="#2f7d7e", edgecolor="#172026")
        else:
            eje.text(0.5, 0.5, "Sin datos generados", ha="center", va="center", color="#6b7680")

        self.figura.tight_layout()
        self.canvas.draw()

    def _actualizar_tabla_desde_selector(self) -> None:
        if self.resultado_actual:
            self._cargar_tabla(self.resultado_actual)

    def _limpiar(self) -> None:
        if self.metodo_actual:
            self._crear_campos_metodo(self.metodo_actual)
        self._limpiar_resultados()

    def _limpiar_resultados(self) -> None:
        self.resultado_actual = None
        self.parametros_label.setText("Parámetros: -")
        self.advertencias_label.setText("Advertencias: sin datos generados.")
        self.tabla.clear()
        self.tabla.setRowCount(0)
        self.tabla.setColumnCount(0)
        self._dibujar_histograma([])

    def _volver_inicio(self) -> None:
        self.stack.setCurrentWidget(self.pantalla_inicio)

    def _volver_categoria(self) -> None:
        if self.categoria_actual:
            self.stack.setCurrentWidget(self.pantalla_categoria)
        else:
            self._volver_inicio()

    def _vaciar_layout(self, layout: QVBoxLayout | QHBoxLayout | QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            if child_layout is not None:
                self._vaciar_layout(child_layout)
