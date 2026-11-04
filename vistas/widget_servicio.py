from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QMenu, QFrame
)
from PySide6.QtCore import Qt, Signal
from modelos.servicio import Servicio
from utilidades.helpers import formatear_memoria, formatear_cpu, color_segun_cpu

class WidgetServicio(QFrame):
    iniciar_solicitado = Signal()
    detener_solicitado = Signal()
    terminal_solicitada = Signal()
    log_solicitado = Signal()
    editar_solicitado = Signal()
    eliminar_solicitado = Signal()
    
    def __init__(self, servicio: Servicio, ventana_padre=None):
        super().__init__()
        self._servicio = servicio
        self._ventana_padre = ventana_padre
        self._estado = "detenido"
        self._ultimo_color = ""
        
        self.setObjectName("tarjeta_servicio")
        self.setFrameShape(QFrame.StyledPanel)
        
        self._inicializar_ui()
    
    def _inicializar_ui(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(12, 8, 12, 8)
        
        layout_indicador = QVBoxLayout()
        self._indicador_estado = QLabel("●")
        self._indicador_estado.setStyleSheet("font-size: 20px; color: #95a5a6;")
        layout_indicador.addWidget(self._indicador_estado)
        layout_indicador.addStretch()
        layout_principal.addLayout(layout_indicador)
        
        layout_info = QVBoxLayout()
        
        self._etiqueta_nombre = QLabel(self._servicio.nombre)
        self._etiqueta_nombre.setObjectName("nombre_servicio")
        layout_info.addWidget(self._etiqueta_nombre)
        
        self._etiqueta_comando = QLabel(self._servicio.comando)
        self._etiqueta_comando.setObjectName("comando_servicio")
        layout_info.addWidget(self._etiqueta_comando)
        
        layout_detalle = QHBoxLayout()
        
        if self._servicio.puertos:
            puertos_texto = ", ".join(str(p) for p in self._servicio.puertos)
            self._etiqueta_puertos = QLabel(f"Puertos: {puertos_texto}")
            self._etiqueta_puertos.setObjectName("detalle_servicio")
            layout_detalle.addWidget(self._etiqueta_puertos)
        
        self._etiqueta_tipo = QLabel(f"Tipo: {self._servicio.tipo_comando}")
        self._etiqueta_tipo.setObjectName("detalle_servicio")
        layout_detalle.addWidget(self._etiqueta_tipo)
        
        layout_detalle.addStretch()
        layout_info.addLayout(layout_detalle)
        
        layout_recursos = QHBoxLayout()
        
        self._barra_cpu = QProgressBar()
        self._barra_cpu.setMaximumWidth(100)
        self._barra_cpu.setMaximumHeight(10)
        self._barra_cpu.setTextVisible(False)
        self._barra_cpu.setRange(0, 100)
        self._barra_cpu.setValue(0)
        layout_recursos.addWidget(QLabel("CPU:"))
        layout_recursos.addWidget(self._barra_cpu)
        
        self._etiqueta_memoria = QLabel("Mem: 0 MB")
        self._etiqueta_memoria.setObjectName("detalle_servicio")
        layout_recursos.addWidget(self._etiqueta_memoria)
        
        layout_recursos.addStretch()
        layout_info.addLayout(layout_recursos)
        
        layout_principal.addLayout(layout_info, stretch=1)
        
        layout_botones = QVBoxLayout()
        layout_botones.setSpacing(4)
        
        self._boton_iniciar = QPushButton("Iniciar")
        self._boton_iniciar.setObjectName("boton_exito")
        self._boton_iniciar.setFixedWidth(80)
        self._boton_iniciar.clicked.connect(self.iniciar_solicitado.emit)
        layout_botones.addWidget(self._boton_iniciar)
        
        self._boton_detener = QPushButton("Detener")
        self._boton_detener.setObjectName("boton_peligro")
        self._boton_detener.setFixedWidth(80)
        self._boton_detener.setEnabled(False)
        self._boton_detener.clicked.connect(self.detener_solicitado.emit)
        layout_botones.addWidget(self._boton_detener)
        
        layout_botones_secundarios = QHBoxLayout()
        
        self._boton_terminal = QPushButton("Terminal")
        self._boton_terminal.setFixedWidth(80)
        self._boton_terminal.clicked.connect(self.terminal_solicitada.emit)
        layout_botones_secundarios.addWidget(self._boton_terminal)
        
        self._boton_logs = QPushButton("Logs")
        self._boton_logs.setFixedWidth(80)
        self._boton_logs.clicked.connect(self.log_solicitado.emit)
        layout_botones_secundarios.addWidget(self._boton_logs)
        
        layout_botones.addLayout(layout_botones_secundarios)
        
        layout_principal.addLayout(layout_botones)
        
        self._boton_menu = QPushButton("⋮")
        self._boton_menu.setFixedSize(30, 30)
        self._boton_menu.clicked.connect(self._mostrar_menu)
        layout_principal.addWidget(self._boton_menu)
    
    def _mostrar_menu(self):
        menu = QMenu(self)
        menu.addAction("Editar", self.editar_solicitado.emit)
        menu.addAction("Eliminar", self.eliminar_solicitado.emit)
        menu.exec(self._boton_menu.mapToGlobal(self._boton_menu.rect().bottomLeft()))
    
    def actualizar_estado(self, estado: str):
        self._estado = estado
        
        if estado == 'ejecutando':
            self._indicador_estado.setStyleSheet("font-size: 20px; color: #2ecc71;")
            self._boton_iniciar.setEnabled(False)
            self._boton_detener.setEnabled(True)
        elif estado == 'deteniendo':
            self._indicador_estado.setStyleSheet("font-size: 20px; color: #f39c12;")
            self._boton_iniciar.setEnabled(False)
            self._boton_detener.setEnabled(False)
        else:
            self._indicador_estado.setStyleSheet("font-size: 20px; color: #95a5a6;")
            self._boton_iniciar.setEnabled(True)
            self._boton_detener.setEnabled(False)
            self._barra_cpu.setValue(0)
            self._etiqueta_memoria.setText("Mem: 0 MB")
    
    def actualizar_recursos(self, cpu: float, memoria_mb: float):
        self._barra_cpu.setValue(int(cpu))
        
        color = color_segun_cpu(cpu)
        if color != self._ultimo_color:
            self._ultimo_color = color
            self._barra_cpu.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 5px;
                }}
            """)
        
        self._etiqueta_memoria.setText(f"Mem: {formatear_memoria(memoria_mb)}")
    
    def actualizar_datos(self, servicio: Servicio):
        self._servicio = servicio
        self._etiqueta_nombre.setText(servicio.nombre)
        self._etiqueta_comando.setText(servicio.comando)
        self._etiqueta_tipo.setText(f"Tipo: {servicio.tipo_comando}")
        
        if servicio.puertos and hasattr(self, '_etiqueta_puertos'):
            puertos_texto = ", ".join(str(p) for p in servicio.puertos)
            self._etiqueta_puertos.setText(f"Puertos: {puertos_texto}")
