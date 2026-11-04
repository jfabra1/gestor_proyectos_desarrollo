from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from bd.conexion import ConexionBD
from modelos.proyecto import Proyecto
from modelos.servicio import Servicio
from servicios.gestor_procesos import ProcesoServicio
from servicios.gestor_puertos import GestorPuertos
from servicios.gestor_recursos import GestorRecursos
from servicios.gestor_logs import GestorLogs
from vistas.widget_servicio import WidgetServicio
from vistas.dialog_editar import DialogEditarServicio, DialogEditarProyecto

class WidgetProyecto(QWidget):
    terminal_solicitada = Signal(int, int)
    log_solicitado = Signal(int)
    
    def __init__(self, proyecto: Proyecto, servicios: list, bd, gestor_logs: GestorLogs, ventana_padre=None):
        super().__init__()
        self.proyecto = proyecto
        self.proyecto_id = proyecto.id
        self._servicios = servicios
        self._bd = bd
        self._gestor_logs = gestor_logs
        self._ventana_padre = ventana_padre
        self._widgets_servicio: dict = {}
        self._procesos: dict = {}
        
        self._inicializar_ui()
    
    def _inicializar_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        
        layout_encabezado = QHBoxLayout()
        
        layout_info = QVBoxLayout()
        self._etiqueta_nombre = QLabel(self.proyecto.nombre)
        self._etiqueta_nombre.setObjectName("titulo")
        layout_info.addWidget(self._etiqueta_nombre)
        
        self._etiqueta_ruta = QLabel(f"Ruta: {self.proyecto.ruta}")
        self._etiqueta_ruta.setObjectName("subtitulo")
        layout_info.addWidget(self._etiqueta_ruta)
        
        if self.proyecto.descripcion:
            self._etiqueta_descripcion = QLabel(self.proyecto.descripcion)
            layout_info.addWidget(self._etiqueta_descripcion)
        
        layout_encabezado.addLayout(layout_info)
        layout_encabezado.addStretch()
        
        layout_botones = QVBoxLayout()
        
        self._boton_iniciar_todo = QPushButton("Iniciar Todo")
        self._boton_iniciar_todo.setObjectName("boton_exito")
        self._boton_iniciar_todo.clicked.connect(self._iniciar_todo)
        layout_botones.addWidget(self._boton_iniciar_todo)
        
        self._boton_detener_todo = QPushButton("Detener Todo")
        self._boton_detener_todo.setObjectName("boton_peligro")
        self._boton_detener_todo.clicked.connect(self._detener_todo)
        self._boton_detener_todo.setEnabled(False)
        layout_botones.addWidget(self._boton_detener_todo)
        
        self._boton_editar_proyecto = QPushButton("Editar Proyecto")
        self._boton_editar_proyecto.clicked.connect(self._editar_proyecto)
        layout_botones.addWidget(self._boton_editar_proyecto)
        
        layout_encabezado.addLayout(layout_botones)
        layout_principal.addLayout(layout_encabezado)
        
        area_scroll = QScrollArea()
        area_scroll.setWidgetResizable(True)
        area_scroll.setFrameShape(QFrame.NoFrame)
        
        contenedor_servicios = QWidget()
        self._layout_servicios = QVBoxLayout(contenedor_servicios)
        self._layout_servicios.setSpacing(8)
        
        for servicio in self._servicios:
            widget_servicio = WidgetServicio(servicio, self._ventana_padre)
            widget_servicio.iniciar_solicitado.connect(lambda s=servicio: self._iniciar_servicio(s))
            widget_servicio.detener_solicitado.connect(lambda s=servicio: self._detener_servicio(s))
            widget_servicio.terminal_solicitada.connect(lambda sid=servicio.id: self.terminal_solicitada.emit(self.proyecto_id, sid))
            widget_servicio.log_solicitado.connect(lambda sid=servicio.id: self.log_solicitado.emit(sid))
            widget_servicio.editar_solicitado.connect(lambda s=servicio: self._editar_servicio(s))
            widget_servicio.eliminar_solicitado.connect(lambda s=servicio: self._eliminar_servicio(s))
            
            self._layout_servicios.addWidget(widget_servicio)
            self._widgets_servicio[servicio.id] = widget_servicio
        
        self._layout_servicios.addStretch()
        
        layout_botones_servicios = QHBoxLayout()
        self._boton_agregar_servicio = QPushButton("+ Agregar Servicio")
        self._boton_agregar_servicio.clicked.connect(self._agregar_servicio)
        layout_botones_servicios.addWidget(self._boton_agregar_servicio)
        layout_botones_servicios.addStretch()
        self._layout_servicios.addLayout(layout_botones_servicios)
        
        area_scroll.setWidget(contenedor_servicios)
        layout_principal.addWidget(area_scroll)
    
    def _iniciar_todo(self):
        puertos_a_verificar = []
        for servicio in self._servicios:
            for puerto in servicio.puertos:
                puertos_a_verificar.append((servicio.nombre, puerto))
        
        if puertos_a_verificar:
            puertos_ocupados = []
            for nombre, puerto in puertos_a_verificar:
                if not GestorPuertos.puerto_disponible(puerto):
                    puertos_ocupados.append((nombre, puerto))
            
            if puertos_ocupados:
                mensaje = "Los siguientes puertos están ocupados:\n\n"
                for nombre, puerto in puertos_ocupados:
                    pid, nombre_proc = GestorPuertos.obtener_pid_puerto(puerto)
                    mensaje += f"  - {nombre}: puerto {puerto} (PID {pid}, {nombre_proc})\n"
                mensaje += "\n¿Deseas matar esos procesos e iniciar tus servicios?"
                
                respuesta = QMessageBox.question(
                    self, "Puertos ocupados", mensaje,
                    QMessageBox.Yes | QMessageBox.No
                )
                if respuesta == QMessageBox.No:
                    return
                
                for _, puerto in puertos_ocupados:
                    GestorPuertos.matar_proceso_puerto(puerto)
        
        for servicio in self._servicios:
            self._iniciar_servicio(servicio)
        
        self._boton_iniciar_todo.setEnabled(False)
        self._boton_detener_todo.setEnabled(True)
    
    def _detener_todo(self):
        for servicio in self._servicios:
            self._detener_servicio(servicio)
        
        self._boton_iniciar_todo.setEnabled(True)
        self._boton_detener_todo.setEnabled(False)
    
    def _iniciar_servicio(self, servicio: Servicio):
        if servicio.id in self._procesos and self._procesos[servicio.id].ejecutando:
            return
        
        if servicio.puertos:
            disponibles, ocupados = GestorPuertos.verificar_puertos(servicio.puertos)
            if ocupados:
                puerto = ocupados[0]
                pid, nombre_proc = GestorPuertos.obtener_pid_puerto(puerto)
                
                respuesta = QMessageBox.question(
                    self, "Puerto ocupado",
                    f"El puerto {puerto} requerido por '{servicio.nombre}' "
                    f"está ocupado por {nombre_proc} (PID {pid}).\n\n"
                    f"¿Matarlo e iniciar tu servicio?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if respuesta == QMessageBox.No:
                    return
                
                exito, mensaje = GestorPuertos.matar_proceso_puerto(puerto)
                if not exito:
                    QMessageBox.warning(self, "Error", f"No se pudo matar el proceso:\n{mensaje}")
                    return
        
        proceso = ProcesoServicio(self)
        proceso.salida_disponible.connect(
            lambda linea, sid=servicio.id: self._on_salida(sid, linea)
        )
        proceso.estado_cambiado.connect(
            lambda estado, sid=servicio.id: self._on_estado_cambiado(sid, estado)
        )
        
        ruta_trabajo = servicio.ruta_trabajo or self.proyecto.ruta
        proceso.iniciar(servicio.comando, ruta_trabajo, servicio.variables_entorno)
        
        self._procesos[servicio.id] = proceso
        
        if self._ventana_padre:
            self._ventana_padre._procesos[servicio.id] = proceso
        
        self.terminal_solicitada.emit(self.proyecto_id, servicio.id)
    
    def _detener_servicio(self, servicio: Servicio):
        if servicio.id in self._procesos:
            self._procesos[servicio.id].detener()
    
    def _on_salida(self, servicio_id: int, linea: str):
        self._gestor_logs.guardar_log(servicio_id, linea)
    
    def _on_estado_cambiado(self, servicio_id: int, estado: str):
        if servicio_id in self._widgets_servicio:
            self._widgets_servicio[servicio_id].actualizar_estado(estado)
    
    def actualizar_recursos(self):
        for servicio_id, proceso in self._procesos.items():
            if proceso.ejecutando and proceso.pid:
                recursos = GestorRecursos.obtener_recursos(proceso.pid)
                
                if servicio_id in self._widgets_servicio:
                    self._widgets_servicio[servicio_id].actualizar_recursos(
                        recursos['cpu'], recursos['memoria_mb']
                    )
    
    def _agregar_servicio(self):
        orden_max = max([s.orden for s in self._servicios], default=-1) + 1
        dialog = DialogEditarServicio(self, orden_inicial=orden_max)
        if dialog.exec():
            datos = dialog.obtener_datos()
            with self._bd.conectar() as cursor:
                cursor.execute(
                    """INSERT INTO servicios 
                    (proyecto_id, nombre, tipo_comando, comando, ruta_trabajo, puertos, variables_entorno, orden)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (self.proyecto_id, datos['nombre'], datos['tipo_comando'],
                     datos['comando'], datos['ruta_trabajo'],
                     datos['puertos_json'], datos['variables_json'], datos['orden'])
                )
                nuevo_id = cursor.lastrowid
            
            nuevo_servicio = Servicio(
                id=nuevo_id,
                proyecto_id=self.proyecto_id,
                nombre=datos['nombre'],
                tipo_comando=datos['tipo_comando'],
                comando=datos['comando'],
                ruta_trabajo=datos['ruta_trabajo'],
                puertos=datos['puertos'],
                variables_entorno=datos['variables_entorno'],
                orden=datos['orden']
            )
            self._servicios.append(nuevo_servicio)
            
            widget_servicio = WidgetServicio(nuevo_servicio, self._ventana_padre)
            widget_servicio.iniciar_solicitado.connect(lambda s=nuevo_servicio: self._iniciar_servicio(s))
            widget_servicio.detener_solicitado.connect(lambda s=nuevo_servicio: self._detener_servicio(s))
            widget_servicio.terminal_solicitada.connect(lambda sid=nuevo_servicio.id: self.terminal_solicitada.emit(self.proyecto_id, sid))
            widget_servicio.log_solicitado.connect(lambda sid=nuevo_servicio.id: self.log_solicitado.emit(sid))
            widget_servicio.editar_solicitado.connect(lambda s=nuevo_servicio: self._editar_servicio(s))
            widget_servicio.eliminar_solicitado.connect(lambda s=nuevo_servicio: self._eliminar_servicio(s))
            
            self._layout_servicios.insertWidget(self._layout_servicios.count() - 2, widget_servicio)
            self._widgets_servicio[nuevo_servicio.id] = widget_servicio
    
    def _editar_servicio(self, servicio: Servicio):
        dialog = DialogEditarServicio(self, servicio=servicio)
        if dialog.exec():
            datos = dialog.obtener_datos()
            with self._bd.conectar() as cursor:
                cursor.execute(
                    """UPDATE servicios SET nombre=?, tipo_comando=?, comando=?,
                    ruta_trabajo=?, puertos=?, variables_entorno=?, orden=?
                    WHERE id=?""",
                    (datos['nombre'], datos['tipo_comando'], datos['comando'],
                     datos['ruta_trabajo'], datos['puertos_json'],
                     datos['variables_json'], datos['orden'], servicio.id)
                )
            
            servicio.nombre = datos['nombre']
            servicio.tipo_comando = datos['tipo_comando']
            servicio.comando = datos['comando']
            servicio.ruta_trabajo = datos['ruta_trabajo']
            servicio.puertos = datos['puertos']
            servicio.variables_entorno = datos['variables_entorno']
            servicio.orden = datos['orden']
            
            if servicio.id in self._widgets_servicio:
                self._widgets_servicio[servicio.id].actualizar_datos(servicio)
    
    def _eliminar_servicio(self, servicio: Servicio):
        respuesta = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar el servicio '{servicio.nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            if servicio.id in self._procesos and self._procesos[servicio.id].ejecutando:
                self._procesos[servicio.id].detener()
            
            with self._bd.conectar() as cursor:
                cursor.execute("DELETE FROM servicios WHERE id = ?", (servicio.id,))
            
            if servicio.id in self._widgets_servicio:
                widget = self._widgets_servicio.pop(servicio.id)
                self._layout_servicios.removeWidget(widget)
                widget.deleteLater()
            
            self._servicios = [s for s in self._servicios if s.id != servicio.id]
    
    def _editar_proyecto(self):
        dialog = DialogEditarProyecto(self, proyecto=self.proyecto)
        if dialog.exec():
            datos = dialog.obtener_datos()
            with self._bd.conectar() as cursor:
                cursor.execute(
                    "UPDATE proyectos SET nombre=?, ruta=?, tipo_id=?, descripcion=? WHERE id=?",
                    (datos['nombre'], datos['ruta'], datos['tipo_id'], datos['descripcion'], self.proyecto_id)
                )
            
            self.proyecto.nombre = datos['nombre']
            self.proyecto.ruta = datos['ruta']
            self.proyecto.descripcion = datos['descripcion']
            
            self._etiqueta_nombre.setText(self.proyecto.nombre)
            self._etiqueta_ruta.setText(f"Ruta: {self.proyecto.ruta}")
            if self.proyecto.descripcion:
                self._etiqueta_descripcion.setText(self.proyecto.descripcion)
