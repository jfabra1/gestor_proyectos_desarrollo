from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPlainTextEdit,
    QLineEdit, QPushButton, QLabel, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
from servicios.gestor_procesos import ProcesoServicio
from servicios.gestor_logs import GestorLogs

class TerminalWidget(QWidget):
    def __init__(self, proceso: ProcesoServicio = None, padre=None):
        super().__init__(padre)
        self._proceso = proceso
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        self._salida = QPlainTextEdit()
        self._salida.setReadOnly(True)
        self._salida.setMaximumBlockCount(10000)
        fuente = QFont("Consolas", 10)
        fuente.setStyleHint(QFont.Monospace)
        self._salida.setFont(fuente)
        layout.addWidget(self._salida)
        
        layout_entrada = QHBoxLayout()
        
        self._entrada = QLineEdit()
        self._entrada.setPlaceholderText("Escribir comando...")
        fuente_entrada = QFont("Consolas", 10)
        fuente_entrada.setStyleHint(QFont.Monospace)
        self._entrada.setFont(fuente_entrada)
        self._entrada.returnPressed.connect(self._enviar_comando)
        layout_entrada.addWidget(self._entrada)
        
        self._boton_enviar = QPushButton("Enviar")
        self._boton_enviar.clicked.connect(self._enviar_comando)
        layout_entrada.addWidget(self._boton_enviar)
        
        self._boton_limpiar = QPushButton("Limpiar")
        self._boton_limpiar.clicked.connect(self._salida.clear)
        layout_entrada.addWidget(self._boton_limpiar)
        
        layout.addLayout(layout_entrada)
        
        if proceso:
            proceso.salida_disponible.connect(self._agregar_salida)
            proceso.error_disponible.connect(self._agregar_error)
            
            for linea in proceso.logs:
                self._salida.appendPlainText(linea)
            
            barra = self._salida.verticalScrollBar()
            barra.setValue(barra.maximum())
            
            if not proceso.ejecutando and not proceso.logs:
                self._salida.appendPlainText("=== Esperando salida del proceso... ===")
    
    def _agregar_salida(self, texto: str):
        self._salida.appendPlainText(texto)
        barra = self._salida.verticalScrollBar()
        barra.setValue(barra.maximum())
    
    def _agregar_error(self, texto: str):
        formato = QTextCharFormat()
        formato.setForeground(QColor("#e74c3c"))
        cursor = self._salida.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(texto + "\n", formato)
        barra = self._salida.verticalScrollBar()
        barra.setValue(barra.maximum())
    
    def _enviar_comando(self):
        comando = self._entrada.text()
        if comando and self._proceso and self._proceso.ejecutando:
            self._proceso.escribir(comando + "\n")
            self._agregar_salida(f"$ {comando}")
            self._entrada.clear()
    
    def agregar_texto(self, texto: str):
        self._salida.appendPlainText(texto)

class WidgetTerminal(QWidget):
    def __init__(self, padre=None):
        super().__init__(padre)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._pestañas = QTabWidget()
        self._pestañas.setTabsClosable(True)
        self._pestañas.tabCloseRequested.connect(self._cerrar_pestaña)
        layout.addWidget(self._pestañas)
        
        self._terminales: dict = {}
        self._logs: dict = {}
    
    def mostrar_terminal(self, proyecto_id: int, servicio_id: int, proceso: ProcesoServicio):
        clave = f"terminal_{servicio_id}"
        
        if clave in self._terminales:
            idx = self._pestañas.indexOf(self._terminales[clave])
            if idx >= 0:
                self._pestañas.setCurrentIndex(idx)
                return
        
        terminal = TerminalWidget(proceso, self)
        self._terminales[clave] = terminal
        
        idx = self._pestañas.addTab(terminal, f"Terminal #{servicio_id}")
        self._pestañas.setCurrentIndex(idx)
    
    def mostrar_log(self, servicio_id: int, gestor_logs: GestorLogs):
        clave = f"log_{servicio_id}"
        
        if clave in self._logs:
            idx = self._pestañas.indexOf(self._logs[clave]['widget'])
            if idx >= 0:
                self._pestañas.setCurrentIndex(idx)
                self._logs[clave]['widget']._cargar_logs()
                return
        
        widget_log = WidgetLog(servicio_id, gestor_logs, self)
        self._logs[clave] = {'widget': widget_log, 'servicio_id': servicio_id}
        
        idx = self._pestañas.addTab(widget_log, f"Logs #{servicio_id}")
        self._pestañas.setCurrentIndex(idx)
    
    def _cerrar_pestaña(self, indice):
        widget = self._pestañas.widget(indice)
        
        for clave, terminal in list(self._terminales.items()):
            if terminal is widget:
                del self._terminales[clave]
                break
        
        for clave, info in list(self._logs.items()):
            if info['widget'] is widget:
                del self._logs[clave]
                break
        
        self._pestañas.removeTab(indice)
        widget.deleteLater()

class WidgetLog(QWidget):
    def __init__(self, servicio_id: int, gestor_logs: GestorLogs, padre=None):
        super().__init__(padre)
        self._servicio_id = servicio_id
        self._gestor_logs = gestor_logs
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        layout_superior = QHBoxLayout()
        
        self._busqueda = QLineEdit()
        self._busqueda.setPlaceholderText("Buscar en logs...")
        self._busqueda.textChanged.connect(self._filtrar)
        layout_superior.addWidget(self._busqueda)
        
        self._boton_recargar = QPushButton("Recargar")
        self._boton_recargar.clicked.connect(self._cargar_logs)
        layout_superior.addWidget(self._boton_recargar)
        
        self._boton_exportar = QPushButton("Exportar")
        self._boton_exportar.clicked.connect(self._exportar)
        layout_superior.addWidget(self._boton_exportar)
        
        self._boton_limpiar = QPushButton("Limpiar")
        self._boton_limpiar.clicked.connect(self._limpiar)
        layout_superior.addWidget(self._boton_limpiar)
        
        layout.addLayout(layout_superior)
        
        self._contenido = QPlainTextEdit()
        self._contenido.setReadOnly(True)
        self._contenido.setMaximumBlockCount(50000)
        fuente = QFont("Consolas", 10)
        fuente.setStyleHint(QFont.Monospace)
        self._contenido.setFont(fuente)
        layout.addWidget(self._contenido)
        
        self._cargar_logs()
    
    def _cargar_logs(self):
        lineas = self._gestor_logs.obtener_log(self._servicio_id)
        self._contenido.clear()
        for linea in lineas:
            self._contenido.appendPlainText(linea)
    
    def _filtrar(self, texto: str):
        self._cargar_logs()
        if texto:
            cursor = self._contenido.textCursor()
            documento = self._contenido.document()
            cursor = documento.find(texto, cursor)
            if not cursor.isNull():
                self._contenido.setTextCursor(cursor)
    
    def _exportar(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar log", f"log_servicio_{self._servicio_id}.txt",
            "Archivos de texto (*.txt);;Todos los archivos (*)"
        )
        if ruta:
            if self._gestor_logs.exportar_log(self._servicio_id, ruta):
                self._busqueda.setPlaceholderText(f"Exportado a {ruta}")
            else:
                self._busqueda.setPlaceholderText("Error al exportar")
    
    def _limpiar(self):
        self._gestor_logs.limpiar_log(self._servicio_id)
        self._contenido.clear()
