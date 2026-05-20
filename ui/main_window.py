from collections.abc import Callable
from dataclasses import dataclass

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
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
from statistics_tests import (
    calcular_chi_cuadrado,
    calcular_correlacion_serial,
    generar_scatter,
)

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
        self.alerta_scipy_mostrada = False

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
        boton_pruebas = QPushButton("Pruebas estadísticas")
        boton_pruebas.setObjectName("secundario")
        boton_pruebas.clicked.connect(self._abrir_pruebas_estadisticas)
        boton_cambiar = QPushButton("Cambiar método")
        boton_cambiar.setObjectName("secundario")
        boton_cambiar.clicked.connect(self._volver_categoria)
        boton_menu = QPushButton("Volver al menú")
        boton_menu.setObjectName("secundario")
        boton_menu.clicked.connect(self._volver_inicio)
        barra.addWidget(self.titulo_metodo)
        barra.addStretch()
        barra.addWidget(boton_pruebas)
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
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas, stretch=2)
        self._dibujar_histograma([])
        return panel

        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        divisor_vertical = QSplitter(Qt.Orientation.Vertical)
        divisor_vertical.setChildrenCollapsible(False)
        layout.addWidget(divisor_vertical)

        divisor_vertical.addWidget(self._crear_seccion_resultados_generacion())
        divisor_vertical.addWidget(self._crear_seccion_histograma())
        divisor_vertical.addWidget(self._crear_panel_pruebas_estadisticas())
        divisor_vertical.setSizes([260, 270, 340])
        return panel

    def _crear_seccion_resultados_generacion(self) -> QFrame:
        seccion = QFrame()
        seccion.setObjectName("panelSecundario")
        layout = QVBoxLayout(seccion)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        titulo = QLabel("Resultados generados")
        titulo.setObjectName("seccion")
        layout.addWidget(titulo)

        resumen = QHBoxLayout()
        self.parametros_label = QLabel("Parámetros: -")
        self.parametros_label.setWordWrap(True)
        self.advertencias_label = QLabel("Advertencias: sin datos generados.")
        self.advertencias_label.setWordWrap(True)
        resumen.addWidget(self.parametros_label, 1)
        resumen.addWidget(self.advertencias_label, 1)
        layout.addLayout(resumen)

        self.tabla = QTableWidget(0, 0)
        self.tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self.tabla, stretch=1)
        return seccion

    def _crear_seccion_histograma(self) -> QFrame:
        seccion = QFrame()
        seccion.setObjectName("panelSecundario")
        layout = QVBoxLayout(seccion)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        titulo = QLabel("Histograma principal")
        titulo.setObjectName("seccion")
        layout.addWidget(titulo)

        self.figura = Figure(figsize=(9, 3.8), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas, stretch=1)
        self._dibujar_histograma([])
        return seccion

    def _crear_panel_resultados_anterior(self) -> QFrame:
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

        layout.addWidget(self._crear_panel_pruebas_estadisticas(), stretch=3)

        return panel

    def _crear_panel_pruebas_estadisticas(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panelSecundario")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        encabezado = QHBoxLayout()
        titulo = QLabel("Pruebas estadísticas")
        titulo.setObjectName("seccion")
        descripcion = QLabel("χ²: uniformidad | Correlación serial: independencia")
        descripcion.setObjectName("ayuda")
        descripcion.setToolTip("χ² evalúa uniformidad. Correlación serial evalúa independencia entre Ui y Ui+h.")
        self.alpha_pruebas = QLineEdit("0.05")
        self.alpha_pruebas.setFixedWidth(80)
        self.alpha_pruebas.setToolTip("Nivel de significación α. Valor por defecto: 0.05.")
        self.alpha_pruebas.editingFinished.connect(self._actualizar_pruebas_estadisticas)

        encabezado.addWidget(titulo)
        encabezado.addWidget(descripcion)
        encabezado.addStretch()
        encabezado.addWidget(QLabel("α"))
        encabezado.addWidget(self.alpha_pruebas)
        boton_volver = QPushButton("Volver atrás")
        boton_volver.setObjectName("secundario")
        boton_volver.clicked.connect(self.close)
        encabezado.addWidget(boton_volver)
        layout.addLayout(encabezado)

        self.advertencia_pruebas = QLabel("Genere una serie para calcular las pruebas.")
        self.advertencia_pruebas.setObjectName("ayuda")
        self.advertencia_pruebas.setWordWrap(True)
        layout.addWidget(self.advertencia_pruebas)

        self.tabs_pruebas = QTabWidget()
        self.tabs_pruebas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs_pruebas.addTab(self._crear_tab_chi(), "Chi-Cuadrado")
        self.tabs_pruebas.addTab(self._crear_tab_correlacion(), "Correlación Serial")
        self.tabs_pruebas.addTab(self._crear_tab_resumen(), "Resumen")
        layout.addWidget(self.tabs_pruebas, stretch=1)

        self._dibujar_grafico_chi([], 0)
        self._dibujar_scatter([])
        return panel

    def _crear_tab_chi(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        bloque_tabla = QVBoxLayout()
        self.estado_chi = QLabel("χ²: pendiente")
        self.estado_chi.setObjectName("ayuda")
        self.resumen_chi = QLabel("χ² calculado: - | χ² tabla: -")
        self.resumen_chi.setObjectName("ayuda")
        self.tabla_chi = QTableWidget(0, 0)
        self._configurar_tabla_prueba(self.tabla_chi)
        bloque_tabla.addWidget(self.estado_chi)
        bloque_tabla.addWidget(self.resumen_chi)
        bloque_tabla.addWidget(self.tabla_chi, stretch=1)

        self.figura_chi = Figure(figsize=(5.5, 3.2), dpi=100)
        self.canvas_chi = FigureCanvas(self.figura_chi)
        self.canvas_chi.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addLayout(bloque_tabla, 3)
        layout.addWidget(self.canvas_chi, 2)
        return tab

    def _crear_tab_correlacion(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        bloque_tabla = QVBoxLayout()
        self.estado_correlacion = QLabel("Correlación serial: pendiente")
        self.estado_correlacion.setObjectName("ayuda")
        self.tabla_correlacion = QTableWidget(0, 0)
        self._configurar_tabla_prueba(self.tabla_correlacion)
        bloque_tabla.addWidget(self.estado_correlacion)
        bloque_tabla.addWidget(self.tabla_correlacion, stretch=1)

        self.figura_scatter = Figure(figsize=(5.5, 3.2), dpi=100)
        self.canvas_scatter = FigureCanvas(self.figura_scatter)
        self.canvas_scatter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addLayout(bloque_tabla, 2)
        layout.addWidget(self.canvas_scatter, 3)
        return tab

    def _crear_tab_resumen(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.resumen_estadistico_label = QLabel("Genere una serie para ver el resumen.")
        self.resumen_estadistico_label.setWordWrap(True)
        self.resumen_estadistico_label.setObjectName("ayuda")
        self.conclusion_estadistica_label = QLabel("Conclusión: pendiente")
        self.conclusion_estadistica_label.setWordWrap(True)
        self.conclusion_estadistica_label.setObjectName("ayuda")

        layout.addWidget(self.resumen_estadistico_label)
        layout.addWidget(self.conclusion_estadistica_label)
        layout.addStretch()
        return tab

    def _crear_panel_pruebas_estadisticas_anterior(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panelSecundario")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        encabezado = QHBoxLayout()
        titulo = QLabel("Pruebas estadísticas")
        titulo.setObjectName("seccion")
        descripcion = QLabel("χ²: uniformidad | Correlación serial: independencia")
        descripcion.setObjectName("ayuda")
        descripcion.setToolTip("χ² evalúa uniformidad. Correlación serial evalúa independencia entre Ui y Ui+h.")
        self.alpha_pruebas = QLineEdit("0.05")
        self.alpha_pruebas.setFixedWidth(80)
        self.alpha_pruebas.setToolTip("Nivel de significación α. Valor por defecto: 0.05.")
        self.alpha_pruebas.editingFinished.connect(self._actualizar_pruebas_estadisticas)

        encabezado.addWidget(titulo)
        encabezado.addWidget(descripcion)
        encabezado.addStretch()
        encabezado.addWidget(QLabel("α"))
        encabezado.addWidget(self.alpha_pruebas)
        boton_volver = QPushButton("Volver atrás")
        boton_volver.setObjectName("secundario")
        boton_volver.clicked.connect(self.close)
        encabezado.addWidget(boton_volver)
        layout.addLayout(encabezado)

        self.advertencia_pruebas = QLabel("Genere una serie para calcular las pruebas.")
        self.advertencia_pruebas.setObjectName("ayuda")
        self.advertencia_pruebas.setWordWrap(True)
        layout.addWidget(self.advertencia_pruebas)

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(12)
        layout.addLayout(cuerpo)

        bloque_chi = QVBoxLayout()
        self.estado_chi = QLabel("χ²: pendiente")
        self.estado_chi.setObjectName("ayuda")
        self.resumen_chi = QLabel("χ² calculado: - | χ² tabla: -")
        self.resumen_chi.setObjectName("ayuda")
        self.tabla_chi = QTableWidget(0, 0)
        self._configurar_tabla_prueba(self.tabla_chi)
        self.figura_chi = Figure(figsize=(4.3, 2.25), dpi=100)
        self.canvas_chi = FigureCanvas(self.figura_chi)
        bloque_chi.addWidget(self.estado_chi)
        bloque_chi.addWidget(self.resumen_chi)
        bloque_chi.addWidget(self.tabla_chi, stretch=2)
        bloque_chi.addWidget(self.canvas_chi, stretch=1)

        bloque_correlacion = QVBoxLayout()
        self.estado_correlacion = QLabel("Correlación serial: pendiente")
        self.estado_correlacion.setObjectName("ayuda")
        self.tabla_correlacion = QTableWidget(0, 0)
        self._configurar_tabla_prueba(self.tabla_correlacion)
        self.figura_scatter = Figure(figsize=(4.3, 2.25), dpi=100)
        self.canvas_scatter = FigureCanvas(self.figura_scatter)
        bloque_correlacion.addWidget(self.estado_correlacion)
        bloque_correlacion.addWidget(self.tabla_correlacion, stretch=2)
        bloque_correlacion.addWidget(self.canvas_scatter, stretch=1)

        cuerpo.addLayout(bloque_chi, 1)
        cuerpo.addLayout(bloque_correlacion, 1)

        self._dibujar_grafico_chi([], 0)
        self._dibujar_scatter([])
        return panel

    def _configurar_tabla_prueba(self, tabla: QTableWidget) -> None:
        tabla.setAlternatingRowColors(True)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.verticalHeader().setVisible(False)
        tabla.verticalHeader().setDefaultSectionSize(24)

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
            eje.hist(valores, bins=10, range=(0, 1), color="#a876e8", edgecolor="#172026")
        else:
            eje.text(0.5, 0.5, "Sin datos generados", ha="center", va="center", color="#6b7680")

        self.figura.tight_layout()
        self.canvas.draw()

    def _actualizar_pruebas_estadisticas(self) -> None:
        if self.resultado_actual is None:
            return

        self._actualizar_resumen_estadistico(None, None)
        try:
            alpha = self._leer_alpha()
            if not self._scipy_disponible():
                self._mostrar_error_scipy()
                self._limpiar_resultados_pruebas()
                return
            resultado_chi = calcular_chi_cuadrado(self.resultado_actual.valores_u, alpha)
            resultado_correlacion = calcular_correlacion_serial(self.resultado_actual.valores_u, alpha)
        except ValueError as error:
            self.advertencia_pruebas.setText(str(error))
            self._limpiar_tabla(self.tabla_chi)
            self._limpiar_tabla(self.tabla_correlacion)
            self._dibujar_grafico_chi([], 0)
            self._dibujar_scatter([])
            self.resumen_chi.setText("χ² calculado: - | χ² tabla: -")
            self.estado_chi.setText("χ²: no calculado")
            self.estado_correlacion.setText("Correlación serial: no calculada")
            self._aplicar_estado_label(self.estado_chi, False)
            self._aplicar_estado_label(self.estado_correlacion, False)
            return

        if self._serie_no_representativa(self.resultado_actual):
            self.advertencia_pruebas.setText(
                "La serie presenta degeneración o período corto; los resultados estadísticos pueden no ser representativos."
            )
        else:
            self.advertencia_pruebas.setText("Pruebas calculadas con la serie Ui generada.")

        self._cargar_tabla_generica(self.tabla_chi, resultado_chi.encabezados, resultado_chi.filas)
        self.resumen_chi.setText(
            f"χ² calculado: {resultado_chi.chi_calculado:.6f} | χ² tabla: {resultado_chi.chi_tabla:.6f}"
        )
        self.estado_chi.setText(f"χ²: {resultado_chi.decision}")
        self._aplicar_estado_label(self.estado_chi, resultado_chi.acepta_h0)
        self._dibujar_grafico_chi(self.resultado_actual.valores_u, resultado_chi.frecuencia_esperada)

        self._cargar_tabla_generica(self.tabla_correlacion, resultado_correlacion.encabezados, resultado_correlacion.filas)
        correlacion_aprobada = all(fila[-1] == "pasa" for fila in resultado_correlacion.filas)
        self.estado_correlacion.setText(
            "Correlación serial: se acepta H0 en h = 1, 2 y 3"
            if correlacion_aprobada
            else "Correlación serial: al menos un h rechaza H0"
        )
        self._aplicar_estado_label(self.estado_correlacion, correlacion_aprobada)
        self._dibujar_scatter(self.resultado_actual.valores_u)
        self._actualizar_resumen_estadistico(resultado_chi.acepta_h0, correlacion_aprobada)

    def _scipy_disponible(self) -> bool:
        try:
            import scipy
            import scipy.stats
        except ModuleNotFoundError:
            return False
        return True

    def _mostrar_error_scipy(self) -> None:
        self.advertencia_pruebas.setText("SciPy no está instalado. Las pruebas estadísticas quedan pendientes.")
        if self.alerta_scipy_mostrada:
            return
        self.alerta_scipy_mostrada = True
        QMessageBox.warning(self, "Falta SciPy", "Instale scipy con: pip install scipy")

    def _limpiar_resultados_pruebas(self) -> None:
        self._limpiar_tabla(self.tabla_chi)
        self._limpiar_tabla(self.tabla_correlacion)
        self._dibujar_grafico_chi([], 0)
        self._dibujar_scatter([])
        self.resumen_chi.setText("χ² calculado: - | χ² tabla: -")
        self.estado_chi.setText("χ²: no calculado")
        self.estado_correlacion.setText("Correlación serial: no calculada")
        self._aplicar_estado_label(self.estado_chi, False)
        self._aplicar_estado_label(self.estado_correlacion, False)

    def _actualizar_resumen_estadistico(self, chi_aprobado: bool | None, correlacion_aprobada: bool | None) -> None:
        if self.resultado_actual is None:
            self.resumen_estadistico_label.setText("Genere una serie para ver el resumen.")
            self.conclusion_estadistica_label.setText("Conclusión: pendiente")
            self.conclusion_estadistica_label.setStyleSheet("")
            return

        valores = self.resultado_actual.valores_u
        media = sum(valores) / len(valores)
        varianza = sum((valor - media) ** 2 for valor in valores) / len(valores)
        periodo = self._periodo_estimado(valores)
        degeneracion = self._tiene_degeneracion(self.resultado_actual)
        periodo_texto = str(periodo) if periodo is not None else "no detectado en la muestra"

        self.resumen_estadistico_label.setText(
            f"Media: {media:.6f}\n"
            f"Varianza: {varianza:.6f}\n"
            f"Período estimado: {periodo_texto}\n"
            f"Degeneración detectada: {'sí' if degeneracion else 'no'}"
        )

        if chi_aprobado is None or correlacion_aprobada is None:
            self.conclusion_estadistica_label.setText("Conclusión: pendiente de pruebas estadísticas.")
            self.conclusion_estadistica_label.setStyleSheet("")
            return

        buena_calidad = chi_aprobado and correlacion_aprobada and not self._serie_no_representativa(self.resultado_actual)
        self.conclusion_estadistica_label.setText(
            "Conclusión: La serie presenta buena calidad estadística"
            if buena_calidad
            else "Conclusión: La serie presenta mala calidad estadística"
        )
        self._aplicar_estado_label(self.conclusion_estadistica_label, buena_calidad)

    def _periodo_estimado(self, valores: list[float]) -> int | None:
        vistos: dict[float, int] = {}
        for indice, valor in enumerate(valores):
            if valor in vistos:
                return indice - vistos[valor]
            vistos[valor] = indice
        return None

    def _tiene_degeneracion(self, resultado: ResultadoGenerador) -> bool:
        return "degener" in " ".join(resultado.advertencias).lower()

    def _leer_alpha(self) -> float:
        texto = self.alpha_pruebas.text().strip().replace(",", ".")
        if not texto:
            raise ValueError("Ingrese un valor para α.")
        try:
            return float(texto)
        except ValueError as exc:
            raise ValueError("α debe ser un valor numérico decimal.") from exc

    def _cargar_tabla_generica(self, tabla: QTableWidget, encabezados: list[str], filas: list[list[str]]) -> None:
        tabla.clear()
        tabla.setColumnCount(len(encabezados))
        tabla.setRowCount(len(filas))
        tabla.setHorizontalHeaderLabels(encabezados)

        for fila_indice, fila in enumerate(filas):
            for columna_indice, valor in enumerate(fila):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabla.setItem(fila_indice, columna_indice, item)

        encabezado = tabla.horizontalHeader()
        encabezado.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        encabezado.setStretchLastSection(True)

    def _limpiar_tabla(self, tabla: QTableWidget) -> None:
        tabla.clear()
        tabla.setRowCount(0)
        tabla.setColumnCount(0)

    def _aplicar_estado_label(self, label: QLabel, aprobado: bool) -> None:
        color_fondo = "#dcefe7" if aprobado else "#fde2df"
        color_texto = "#1f6f4a" if aprobado else "#9f2d24"
        label.setStyleSheet(
            f"background: {color_fondo}; color: {color_texto}; border-radius: 8px; padding: 7px; font-weight: 700;"
        )

    def _serie_no_representativa(self, resultado: ResultadoGenerador) -> bool:
        texto_advertencias = " ".join(resultado.advertencias).lower()
        if "degener" in texto_advertencias or "ciclo" in texto_advertencias:
            return True
        return len(set(resultado.valores_u)) < min(100, len(resultado.valores_u) // 2)

    def _dibujar_grafico_chi(self, valores: list[float], frecuencia_esperada: float) -> None:
        self.figura_chi.clear()
        eje = self.figura_chi.add_subplot(111)
        eje.set_title("Frecuencias observadas vs esperadas")
        eje.set_xlabel("Intervalos")
        eje.set_ylabel("Frecuencia")
        eje.grid(axis="y", alpha=0.25)

        if valores:
            frecuencias = [0] * 10
            for valor in valores:
                indice = min(int(valor * 10), 9)
                frecuencias[indice] += 1
            posiciones = list(range(10))
            eje.bar(posiciones, frecuencias, color="#2f7d7e", edgecolor="#172026")
            eje.axhline(frecuencia_esperada, color="#d96c5f", linewidth=2, label="Frecuencia esperada")
            eje.set_xticks(posiciones)
            eje.set_xticklabels([f"{i / 10:.1f}" for i in posiciones])
            eje.legend(loc="upper right", fontsize=8)
        else:
            eje.text(0.5, 0.5, "Sin datos", ha="center", va="center", color="#6b7680")

        self.figura_chi.tight_layout()
        self.canvas_chi.draw()

    def _dibujar_scatter(self, valores: list[float]) -> None:
        self.figura_scatter.clear()
        eje = self.figura_scatter.add_subplot(111)
        eje.set_title("Scatter Ui vs Ui+1")
        eje.set_xlabel("Ui")
        eje.set_ylabel("Ui+1")
        eje.set_xlim(0, 1)
        eje.set_ylim(0, 1)
        eje.grid(alpha=0.25)

        if len(valores) > 1:
            x, y = generar_scatter(valores)
            eje.scatter(x, y, s=10, alpha=0.55, color="#2f7d7e", edgecolors="none")
        else:
            eje.text(0.5, 0.5, "Sin datos", ha="center", va="center", color="#6b7680")

        self.figura_scatter.tight_layout()
        self.canvas_scatter.draw()

    def _actualizar_tabla_desde_selector(self) -> None:
        if self.resultado_actual:
            self._cargar_tabla(self.resultado_actual)

    def _abrir_pruebas_estadisticas(self) -> None:
        if self.resultado_actual is None:
            QMessageBox.information(self, "Sin serie generada", "Primero genere una serie para calcular las pruebas estadísticas.")
            return

        dialogo = PruebasEstadisticasDialog(self.resultado_actual, self)
        dialogo.exec()

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
        if not hasattr(self, "advertencia_pruebas"):
            return
        self.advertencia_pruebas.setText("Genere una serie para calcular las pruebas.")
        self.estado_chi.setText("χ²: pendiente")
        self.estado_chi.setStyleSheet("")
        self.resumen_chi.setText("χ² calculado: - | χ² tabla: -")
        self.estado_correlacion.setText("Correlación serial: pendiente")
        self.estado_correlacion.setStyleSheet("")
        self.estado_chi.setText("χ²: pendiente")
        self.resumen_chi.setText("χ² calculado: - | χ² tabla: -")
        self.estado_correlacion.setText("Correlación serial: pendiente")
        self.resumen_estadistico_label.setText("Genere una serie para ver el resumen.")
        self.conclusion_estadistica_label.setText("Conclusión: pendiente")
        self.conclusion_estadistica_label.setStyleSheet("")
        self._limpiar_tabla(self.tabla_chi)
        self._limpiar_tabla(self.tabla_correlacion)
        self._dibujar_grafico_chi([], 0)
        self._dibujar_scatter([])

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


class PruebasEstadisticasDialog(QDialog):
    def __init__(self, resultado: ResultadoGenerador, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.resultado = resultado
        self.setWindowTitle("Pruebas estadísticas")
        self.resize(1050, 720)
        self.setMinimumSize(850, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        encabezado = QHBoxLayout()
        titulo = QLabel("Pruebas estadísticas")
        titulo.setObjectName("titulo")
        descripcion = QLabel("χ²: uniformidad | Correlación serial: independencia")
        descripcion.setObjectName("ayuda")
        descripcion.setToolTip("χ² evalúa uniformidad. Correlación serial evalúa independencia entre Ui y Ui+h.")
        self.alpha_pruebas = QLineEdit("0.05")
        self.alpha_pruebas.setFixedWidth(90)
        self.alpha_pruebas.editingFinished.connect(self._actualizar_pruebas)
        encabezado.addWidget(titulo)
        encabezado.addWidget(descripcion)
        encabezado.addStretch()
        encabezado.addWidget(QLabel("α"))
        encabezado.addWidget(self.alpha_pruebas)
        boton_volver = QPushButton("Volver atrás")
        boton_volver.setObjectName("secundario")
        boton_volver.clicked.connect(self.close)
        encabezado.addWidget(boton_volver)
        layout.addLayout(encabezado)

        self.mensaje = QLabel("Pruebas calculadas con la serie Ui generada.")
        self.mensaje.setObjectName("ayuda")
        self.mensaje.setWordWrap(True)
        layout.addWidget(self.mensaje)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._crear_tab_uniformidad(), "Uniformidad")
        self.tabs.addTab(self._crear_tab_independencia(), "Independencia")
        self.tabs.addTab(self._crear_tab_resumen(), "Resumen")
        layout.addWidget(self.tabs, stretch=1)

        self._actualizar_pruebas()

    def _crear_tab_uniformidad(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        bloque = QVBoxLayout()
        self.estado_chi = QLabel("χ²: pendiente")
        self.estado_chi.setObjectName("ayuda")
        self.resumen_chi = QLabel("χ² calculado: - | χ² tabla: -")
        self.resumen_chi.setObjectName("ayuda")
        self.tabla_chi = QTableWidget(0, 0)
        self._configurar_tabla(self.tabla_chi)
        bloque.addWidget(self.estado_chi)
        bloque.addWidget(self.resumen_chi)
        bloque.addWidget(self.tabla_chi, stretch=1)

        self.figura_chi = Figure(figsize=(5.8, 4.2), dpi=100)
        self.canvas_chi = FigureCanvas(self.figura_chi)
        self.canvas_chi.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addLayout(bloque, 3)
        layout.addWidget(self.canvas_chi, 2)
        return tab

    def _crear_tab_independencia(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        bloque = QVBoxLayout()
        self.estado_correlacion = QLabel("Correlación serial: pendiente")
        self.estado_correlacion.setObjectName("ayuda")
        self.tabla_correlacion = QTableWidget(0, 0)
        self._configurar_tabla(self.tabla_correlacion)
        bloque.addWidget(self.estado_correlacion)
        bloque.addWidget(self.tabla_correlacion, stretch=1)

        self.figura_scatter = Figure(figsize=(6.2, 4.2), dpi=100)
        self.canvas_scatter = FigureCanvas(self.figura_scatter)
        self.canvas_scatter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addLayout(bloque, 2)
        layout.addWidget(self.canvas_scatter, 3)
        return tab

    def _crear_tab_resumen(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.resumen_estadistico = QLabel()
        self.resumen_estadistico.setObjectName("ayuda")
        self.resumen_estadistico.setWordWrap(True)
        self.conclusion = QLabel()
        self.conclusion.setObjectName("ayuda")
        self.conclusion.setWordWrap(True)
        layout.addWidget(self.resumen_estadistico)
        layout.addWidget(self.conclusion)
        layout.addStretch()
        return tab

    def _configurar_tabla(self, tabla: QTableWidget) -> None:
        tabla.setAlternatingRowColors(True)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.verticalHeader().setVisible(False)
        tabla.verticalHeader().setDefaultSectionSize(26)

    def _actualizar_pruebas(self) -> None:
        if not self._scipy_disponible():
            QMessageBox.warning(self, "Falta SciPy", "Instale scipy con: pip install scipy")
            self.mensaje.setText("SciPy no está instalado. Las pruebas estadísticas quedan pendientes.")
            return

        try:
            alpha = float(self.alpha_pruebas.text().strip().replace(",", "."))
            resultado_chi = calcular_chi_cuadrado(self.resultado.valores_u, alpha)
            resultado_correlacion = calcular_correlacion_serial(self.resultado.valores_u, alpha)
        except ValueError as error:
            self.mensaje.setText(str(error))
            return

        self._cargar_tabla(self.tabla_chi, resultado_chi.encabezados, resultado_chi.filas)
        self.resumen_chi.setText(f"χ² calculado: {resultado_chi.chi_calculado:.6f} | χ² tabla: {resultado_chi.chi_tabla:.6f}")
        self.estado_chi.setText(f"χ²: {resultado_chi.decision}")
        self._aplicar_estado(self.estado_chi, resultado_chi.acepta_h0)
        self._dibujar_grafico_chi(resultado_chi.frecuencia_esperada)

        self._cargar_tabla(self.tabla_correlacion, resultado_correlacion.encabezados, resultado_correlacion.filas)
        correlacion_aprobada = all(fila[-1] == "pasa" for fila in resultado_correlacion.filas)
        self.estado_correlacion.setText(
            "Correlación serial: se acepta H0 en h = 1, 2 y 3"
            if correlacion_aprobada
            else "Correlación serial: al menos un h rechaza H0"
        )
        self._aplicar_estado(self.estado_correlacion, correlacion_aprobada)
        self._dibujar_scatter()
        self._actualizar_resumen(resultado_chi.acepta_h0, correlacion_aprobada)

    def _scipy_disponible(self) -> bool:
        try:
            import scipy
            import scipy.stats
        except ModuleNotFoundError:
            return False
        return True

    def _cargar_tabla(self, tabla: QTableWidget, encabezados: list[str], filas: list[list[str]]) -> None:
        tabla.clear()
        tabla.setColumnCount(len(encabezados))
        tabla.setRowCount(len(filas))
        tabla.setHorizontalHeaderLabels(encabezados)
        for fila_indice, fila in enumerate(filas):
            for columna_indice, valor in enumerate(fila):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabla.setItem(fila_indice, columna_indice, item)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        tabla.horizontalHeader().setStretchLastSection(True)

    def _dibujar_grafico_chi(self, frecuencia_esperada: float) -> None:
        self.figura_chi.clear()
        eje = self.figura_chi.add_subplot(111)
        frecuencias = [0] * 10
        for valor in self.resultado.valores_u:
            frecuencias[min(int(valor * 10), 9)] += 1
        posiciones = list(range(10))
        eje.bar(posiciones, frecuencias, color="#2f7d7e", edgecolor="#172026")
        eje.axhline(frecuencia_esperada, color="#d96c5f", linewidth=2, label="Frecuencia esperada")
        eje.set_title("Frecuencias observadas vs esperadas")
        eje.set_xlabel("Intervalos")
        eje.set_ylabel("Frecuencia")
        eje.set_xticks(posiciones)
        eje.grid(axis="y", alpha=0.25)
        eje.legend(loc="upper right", fontsize=8)
        self.figura_chi.tight_layout()
        self.canvas_chi.draw()

    def _dibujar_scatter(self) -> None:
        self.figura_scatter.clear()
        eje = self.figura_scatter.add_subplot(111)
        x, y = generar_scatter(self.resultado.valores_u)
        eje.scatter(x, y, s=10, alpha=0.55, color="#2f7d7e", edgecolors="none")
        eje.set_title("Scatter Ui vs Ui+1")
        eje.set_xlabel("Ui")
        eje.set_ylabel("Ui+1")
        eje.set_xlim(0, 1)
        eje.set_ylim(0, 1)
        eje.grid(alpha=0.25)
        self.figura_scatter.tight_layout()
        self.canvas_scatter.draw()

    def _actualizar_resumen(self, chi_aprobado: bool, correlacion_aprobada: bool) -> None:
        valores = self.resultado.valores_u
        media = sum(valores) / len(valores)
        varianza = sum((valor - media) ** 2 for valor in valores) / len(valores)
        periodo = self._periodo_estimado(valores)
        degeneracion = "degener" in " ".join(self.resultado.advertencias).lower()
        periodo_texto = str(periodo) if periodo is not None else "no detectado en la muestra"
        self.resumen_estadistico.setText(
            f"Media: {media:.6f}\n"
            f"Varianza: {varianza:.6f}\n"
            f"Período estimado: {periodo_texto}\n"
            f"Degeneración detectada: {'sí' if degeneracion else 'no'}"
        )
        buena = chi_aprobado and correlacion_aprobada and not degeneracion
        self.conclusion.setText(
            "Conclusión: La serie presenta buena calidad estadística"
            if buena
            else "Conclusión: La serie presenta mala calidad estadística"
        )
        self._aplicar_estado(self.conclusion, buena)

    def _periodo_estimado(self, valores: list[float]) -> int | None:
        vistos: dict[float, int] = {}
        for indice, valor in enumerate(valores):
            if valor in vistos:
                return indice - vistos[valor]
            vistos[valor] = indice
        return None

    def _aplicar_estado(self, label: QLabel, aprobado: bool) -> None:
        color_fondo = "#dcefe7" if aprobado else "#fde2df"
        color_texto = "#1f6f4a" if aprobado else "#9f2d24"
        label.setStyleSheet(
            f"background: {color_fondo}; color: {color_texto}; border-radius: 8px; padding: 7px; font-weight: 700;"
        )
