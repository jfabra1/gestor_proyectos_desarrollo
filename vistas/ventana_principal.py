from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QMenuBar,
    QMenu, QStatusBar, QMessageBox, QProgressDialog, QLabel,
    QPushButton, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QAction, QPalette, QColor
from PySide6.QtWidgets import QApplication
from bd.conexion import ConexionBD
from modelos.tipo_proyecto import TipoProyecto
from modelos.proyecto import Proyecto
from modelos.servicio import Servicio
from servicios.gestor_procesos import ProcesoServicio
from servicios.gestor_puertos import GestorPuertos
from servicios.gestor_recursos import GestorRecursos
from servicios.gestor_logs import GestorLogs
from recursos.temas import TEMA_CLARO, TEMA_OSCURO
from vistas.widget_proyecto import WidgetProyecto
from vistas.widget_terminal import WidgetTerminal
from vistas.dialog_editar import (
    DialogEditarTipoProyecto, DialogEditarProyecto, DialogEditarServicio
)
import sys

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Proyectos")
        self.setMinimumSize(1200, 800)
        
        self._bd = ConexionBD.obtener_instancia()
        self._gestor_logs = GestorLogs()
        self._procesos: dict = {}
        self._tema_oscuro = self._detectar_tema_sistema()
        
        self._inicializar_ui()
        self._inicializar_menu()
        self._inicializar_temporizador()
        self._aplicar_tema()
        self._cargar_datos()
    
    def _detectar_tema_sistema(self) -> bool:
        paleta = self.palette()
        color_fondo = paleta.color(QPalette.Window)
        luminosidad = (color_fondo.red() * 0.299 + 
                      color_fondo.green() * 0.587 + 
                      color_fondo.blue() * 0.114)
        return luminosidad < 128
    
    def _inicializar_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        self._divisor = QSplitter(Qt.Horizontal)
        layout_principal.addWidget(self._divisor)
        
        panel_lateral = QWidget()
        panel_lateral.setMinimumWidth(250)
        panel_lateral.setMaximumWidth(400)
        layout_lateral = QVBoxLayout(panel_lateral)
        layout_lateral.setContentsMargins(8, 8, 8, 8)
        
        self._etiqueta_titulo = QLabel("Proyectos")
        self._etiqueta_titulo.setObjectName("titulo")
        layout_lateral.addWidget(self._etiqueta_titulo)
        
        self._arbol_proyectos = QTreeWidget()
        self._arbol_proyectos.setHeaderHidden(True)
        self._arbol_proyectos.itemClicked.connect(self._on_proyecto_seleccionado)
        self._arbol_proyectos.setContextMenuPolicy(Qt.CustomContextMenu)
        self._arbol_proyectos.customContextMenuRequested.connect(self._menu_contextual_arbol)
        layout_lateral.addWidget(self._arbol_proyectos)
        
        layout_botones_lateral = QHBoxLayout()
        
        self._boton_agregar_tipo = QPushButton("Tipo")
        self._boton_agregar_tipo.clicked.connect(self._agregar_tipo)
        layout_botones_lateral.addWidget(self._boton_agregar_tipo)
        
        self._boton_agregar_proyecto = QPushButton("Proyecto")
        self._boton_agregar_proyecto.clicked.connect(self._agregar_proyecto)
        layout_botones_lateral.addWidget(self._boton_agregar_proyecto)
        
        layout_lateral.addLayout(layout_botones_lateral)
        
        self._divisor.addWidget(panel_lateral)
        
        panel_contenido = QWidget()
        layout_contenido = QVBoxLayout(panel_contenido)
        layout_contenido.setContentsMargins(0, 0, 0, 0)
        
        self._divisor_contenido = QSplitter(Qt.Vertical)
        layout_contenido.addWidget(self._divisor_contenido)
        
        self._widget_contenido = QStackedWidget()
        
        self._widget_bienvenida = QWidget()
        layout_bienvenida = QVBoxLayout(self._widget_bienvenida)
        layout_bienvenida.setAlignment(Qt.AlignCenter)
        etiqueta_bienvenida = QLabel("Selecciona un proyecto para comenzar")
        etiqueta_bienvenida.setObjectName("subtitulo")
        layout_bienvenida.addWidget(etiqueta_bienvenida)
        
        self._widget_contenido.addWidget(self._widget_bienvenida)
        self._divisor_contenido.addWidget(self._widget_contenido)
        
        self._widget_terminal = WidgetTerminal()
        self._divisor_contenido.addWidget(self._widget_terminal)
        self._divisor_contenido.setSizes([600, 200])
        
        self._divisor.addWidget(panel_contenido)
        self._divisor.setSizes([300, 900])
        
        self._barra_estado = QStatusBar()
        self.setStatusBar(self._barra_estado)
        self._barra_estado.showMessage("Listo")
    
    def _inicializar_menu(self):
        barra_menu = self.menuBar()
        
        menu_archivo = barra_menu.addMenu("Archivo")
        
        accion_salir = QAction("Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)
        
        menu_ver = barra_menu.addMenu("Ver")
        
        self._accion_tema = QAction("Cambiar Tema", self)
        self._accion_tema.triggered.connect(self._alternar_tema)
        menu_ver.addAction(self._accion_tema)
        
        menu_ayuda = barra_menu.addMenu("Ayuda")
        
        accion_acerca = QAction("Acerca de", self)
        accion_acerca.triggered.connect(self._mostrar_acerca_de)
        menu_ayuda.addAction(accion_acerca)
    
    def _inicializar_temporizador(self):
        self._temporizador_recursos = QTimer(self)
        self._temporizador_recursos.timeout.connect(self._actualizar_recursos)
        self._temporizador_recursos.start(5000)
    
    def _aplicar_tema(self):
        if self._tema_oscuro:
            self.setStyleSheet(TEMA_OSCURO)
        else:
            self.setStyleSheet(TEMA_CLARO)
    
    def _alternar_tema(self):
        self._tema_oscuro = not self._tema_oscuro
        self._aplicar_tema()
    
    def _cargar_datos(self):
        self._arbol_proyectos.clear()
        
        with self._bd.conectar() as cursor:
            cursor.execute("SELECT * FROM tipos_proyecto ORDER BY nombre")
            tipos = cursor.fetchall()
            
            for tipo in tipos:
                item_tipo = QTreeWidgetItem([tipo['nombre']])
                item_tipo.setData(0, Qt.UserRole, {'tipo': 'tipo', 'id': tipo['id']})
                
                cursor.execute(
                    "SELECT * FROM proyectos WHERE tipo_id = ? ORDER BY nombre",
                    (tipo['id'],)
                )
                proyectos = cursor.fetchall()
                
                for proyecto in proyectos:
                    item_proyecto = QTreeWidgetItem([proyecto['nombre']])
                    item_proyecto.setData(0, Qt.UserRole, {
                        'tipo': 'proyecto',
                        'id': proyecto['id'],
                        'nombre': proyecto['nombre'],
                        'ruta': proyecto['ruta']
                    })
                    item_tipo.addChild(item_proyecto)
                
                self._arbol_proyectos.addTopLevelItem(item_tipo)
        
        self._arbol_proyectos.expandAll()
    
    def _agregar_tipo(self):
        dialog = DialogEditarTipoProyecto(self)
        if dialog.exec():
            datos = dialog.obtener_datos()
            with self._bd.conectar() as cursor:
                cursor.execute(
                    "INSERT INTO tipos_proyecto (nombre, descripcion, color) VALUES (?, ?, ?)",
                    (datos['nombre'], datos['descripcion'], datos['color'])
                )
            self._cargar_datos()
            self._barra_estado.showMessage(f"Tipo '{datos['nombre']}' creado")
    
    def _agregar_proyecto(self):
        item_seleccionado = self._arbol_proyectos.currentItem()
        tipo_id = None
        
        if item_seleccionado:
            datos = item_seleccionado.data(0, Qt.UserRole)
            if datos and datos['tipo'] == 'tipo':
                tipo_id = datos['id']
        
        dialog = DialogEditarProyecto(self, tipo_id_inicial=tipo_id)
        if dialog.exec():
            datos = dialog.obtener_datos()
            with self._bd.conectar() as cursor:
                cursor.execute(
                    "INSERT INTO proyectos (nombre, ruta, tipo_id, descripcion) VALUES (?, ?, ?, ?)",
                    (datos['nombre'], datos['ruta'], datos['tipo_id'], datos['descripcion'])
                )
            self._cargar_datos()
            self._barra_estado.showMessage(f"Proyecto '{datos['nombre']}' creado")
    
    def _menu_contextual_arbol(self, posicion):
        item = self._arbol_proyectos.itemAt(posicion)
        if not item:
            return
        
        datos = item.data(0, Qt.UserRole)
        if not datos:
            return
        
        menu = QMenu(self)
        
        if datos['tipo'] == 'tipo':
            accion_editar = menu.addAction("Editar Tipo")
            accion_eliminar = menu.addAction("Eliminar Tipo")
            
            accion_seleccionada = menu.exec(self._arbol_proyectos.mapToGlobal(posicion))
            if accion_seleccionada == accion_editar:
                self._editar_tipo(datos['id'])
            elif accion_seleccionada == accion_eliminar:
                self._eliminar_tipo(datos['id'])
        
        elif datos['tipo'] == 'proyecto':
            accion_editar = menu.addAction("Editar Proyecto")
            accion_eliminar = menu.addAction("Eliminar Proyecto")
            
            accion_seleccionada = menu.exec(self._arbol_proyectos.mapToGlobal(posicion))
            if accion_seleccionada == accion_editar:
                self._editar_proyecto_desde_sidebar(datos['id'])
            elif accion_seleccionada == accion_eliminar:
                self._eliminar_proyecto(datos['id'])
    
    def _editar_tipo(self, tipo_id):
        with self._bd.conectar() as cursor:
            cursor.execute("SELECT * FROM tipos_proyecto WHERE id = ?", (tipo_id,))
            fila = cursor.fetchone()
        
        if not fila:
            return
        
        tipo = TipoProyecto(
            id=fila['id'],
            nombre=fila['nombre'],
            descripcion=fila['descripcion'] or "",
            color=fila['color'] or "#3498db"
        )
        
        dialog = DialogEditarTipoProyecto(self, tipo=tipo)
        if dialog.exec():
            datos = dialog.obtener_datos()
            with self._bd.conectar() as cursor:
                cursor.execute(
                    "UPDATE tipos_proyecto SET nombre=?, descripcion=?, color=? WHERE id=?",
                    (datos['nombre'], datos['descripcion'], datos['color'], tipo_id)
                )
            self._cargar_datos()
            self._barra_estado.showMessage(f"Tipo '{datos['nombre']}' actualizado")
    
    def _eliminar_tipo(self, tipo_id):
        with self._bd.conectar() as cursor:
            cursor.execute("SELECT nombre FROM tipos_proyecto WHERE id = ?", (tipo_id,))
            fila = cursor.fetchone()
            
            if not fila:
                return
            
            nombre = fila['nombre']
            
            cursor.execute("SELECT COUNT(*) as total FROM proyectos WHERE tipo_id = ?", (tipo_id,))
            total_proyectos = cursor.fetchone()['total']
        
        mensaje = f"¿Eliminar el tipo '{nombre}'?"
        if total_proyectos > 0:
            mensaje += f"\n\nEste tipo tiene {total_proyectos} proyecto(s) asociado(s).\nLos proyectos quedarán sin tipo asignado."
        
        respuesta = QMessageBox.question(
            self, "Confirmar eliminación", mensaje,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            with self._bd.conectar() as cursor:
                cursor.execute("UPDATE proyectos SET tipo_id = NULL WHERE tipo_id = ?", (tipo_id,))
                cursor.execute("DELETE FROM tipos_proyecto WHERE id = ?", (tipo_id,))
            self._cargar_datos()
            self._barra_estado.showMessage(f"Tipo '{nombre}' eliminado")
    
    def _editar_proyecto_desde_sidebar(self, proyecto_id):
        with self._bd.conectar() as cursor:
            cursor.execute("SELECT * FROM proyectos WHERE id = ?", (proyecto_id,))
            fila = cursor.fetchone()
        
        if not fila:
            return
        
        proyecto = Proyecto(
            id=fila['id'],
            nombre=fila['nombre'],
            ruta=fila['ruta'],
            tipo_id=fila['tipo_id'],
            descripcion=fila['descripcion'] or ""
        )
        
        dialog = DialogEditarProyecto(self, proyecto=proyecto)
        if dialog.exec():
            datos = dialog.obtener_datos()
            with self._bd.conectar() as cursor:
                cursor.execute(
                    "UPDATE proyectos SET nombre=?, ruta=?, tipo_id=?, descripcion=? WHERE id=?",
                    (datos['nombre'], datos['ruta'], datos['tipo_id'], datos['descripcion'], proyecto_id)
                )
            
            for i in range(self._widget_contenido.count()):
                widget = self._widget_contenido.widget(i)
                if isinstance(widget, WidgetProyecto) and widget.proyecto_id == proyecto_id:
                    widget.proyecto.nombre = datos['nombre']
                    widget.proyecto.ruta = datos['ruta']
                    widget.proyecto.descripcion = datos['descripcion']
                    widget._etiqueta_nombre.setText(datos['nombre'])
                    widget._etiqueta_ruta.setText(f"Ruta: {datos['ruta']}")
                    if hasattr(widget, '_etiqueta_descripcion') and widget._etiqueta_descripcion:
                        widget._etiqueta_descripcion.setText(datos['descripcion'])
                    break
            
            self._cargar_datos()
            self._barra_estado.showMessage(f"Proyecto '{datos['nombre']}' actualizado")
    
    def _eliminar_proyecto(self, proyecto_id):
        with self._bd.conectar() as cursor:
            cursor.execute("SELECT nombre FROM proyectos WHERE id = ?", (proyecto_id,))
            fila = cursor.fetchone()
            
            if not fila:
                return
            
            nombre = fila['nombre']
        
        respuesta = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar el proyecto '{nombre}'?\n\nSe eliminarán también todos sus servicios.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            for i in range(self._widget_contenido.count()):
                widget = self._widget_contenido.widget(i)
                if isinstance(widget, WidgetProyecto) and widget.proyecto_id == proyecto_id:
                    for servicio_id, proceso in list(widget._procesos.items()):
                        if proceso.ejecutando:
                            proceso.detener()
                    self._widget_contenido.removeWidget(widget)
                    widget.deleteLater()
                    break
            
            with self._bd.conectar() as cursor:
                cursor.execute("DELETE FROM proyectos WHERE id = ?", (proyecto_id,))
            
            self._cargar_datos()
            self._widget_contenido.setCurrentWidget(self._widget_bienvenida)
            self._barra_estado.showMessage(f"Proyecto '{nombre}' eliminado")
    
    def _on_proyecto_seleccionado(self, item, columna):
        datos = item.data(0, Qt.UserRole)
        if not datos or datos['tipo'] != 'proyecto':
            return
        
        proyecto_id = datos['id']
        
        for i in range(self._widget_contenido.count()):
            widget = self._widget_contenido.widget(i)
            if isinstance(widget, WidgetProyecto) and widget.proyecto_id == proyecto_id:
                self._widget_contenido.setCurrentIndex(i)
                return
        
        with self._bd.conectar() as cursor:
            cursor.execute("SELECT * FROM proyectos WHERE id = ?", (proyecto_id,))
            fila_proyecto = cursor.fetchone()
            
            cursor.execute(
                "SELECT * FROM servicios WHERE proyecto_id = ? ORDER BY orden",
                (proyecto_id,)
            )
            filas_servicios = cursor.fetchall()
        
        proyecto = Proyecto(
            id=fila_proyecto['id'],
            nombre=fila_proyecto['nombre'],
            ruta=fila_proyecto['ruta'],
            tipo_id=fila_proyecto['tipo_id'],
            descripcion=fila_proyecto['descripcion']
        )
        
        servicios = [Servicio.desde_fila(f) for f in filas_servicios]
        
        widget_proyecto = WidgetProyecto(
            proyecto, servicios, self._bd, self._gestor_logs, self
        )
        widget_proyecto.terminal_solicitada.connect(self._mostrar_terminal)
        widget_proyecto.log_solicitado.connect(self._mostrar_log)
        
        self._widget_contenido.addWidget(widget_proyecto)
        self._widget_contenido.setCurrentWidget(widget_proyecto)
    
    def _mostrar_terminal(self, proyecto_id: int, servicio_id: int):
        if servicio_id in self._procesos:
            self._widget_terminal.mostrar_terminal(proyecto_id, servicio_id, self._procesos[servicio_id])
    
    def _mostrar_log(self, servicio_id: int):
        self._widget_terminal.mostrar_log(servicio_id, self._gestor_logs)
    
    def _actualizar_recursos(self):
        for i in range(self._widget_contenido.count()):
            widget = self._widget_contenido.widget(i)
            if isinstance(widget, WidgetProyecto):
                widget.actualizar_recursos()
    
    def _mostrar_acerca_de(self):
        QMessageBox.about(
            self,
            "Acerca de Gestor de Proyectos",
            "Gestor de Proyectos v1.0\n\n"
            "Aplicación para administrar múltiples servicios\n"
            "de desarrollo (backends, frontends, etc.)\n\n"
            "Desarrollado con PySide6"
        )
    
    def closeEvent(self, evento):
        procesos_activos = [
            sid for sid, proc in self._procesos.items() if proc.ejecutando
        ]
        
        if procesos_activos:
            respuesta = QMessageBox.question(
                self,
                "Confirmar cierre",
                f"Hay {len(procesos_activos)} servicio(s) en ejecución.\n"
                "¿Deseas detenerlos y cerrar la aplicación?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if respuesta == QMessageBox.No:
                evento.ignore()
                return
            
            progreso = QProgressDialog(
                "Deteniendo servicios...", "Cancelar", 0, 0, self
            )
            progreso.setWindowTitle("Cerrando aplicación")
            progreso.setWindowModality(Qt.WindowModal)
            progreso.setMinimumDuration(0)
            progreso.setCancelButton(None)
            progreso.show()
            
            for servicio_id in procesos_activos:
                proceso = self._procesos[servicio_id]
                proceso.detener()
            
            tiempo_max = 7000
            espera = 0
            while espera < tiempo_max:
                QThread.msleep(200)
                QApplication.processEvents()
                espera += 200
                
                activos = sum(1 for sid in procesos_activos 
                             if sid in self._procesos and self._procesos[sid].ejecutando)
                progreso.setLabelText(f"Deteniendo servicios... ({activos} restantes)")
                
                if activos == 0:
                    break
            
            for servicio_id in procesos_activos:
                if servicio_id in self._procesos and self._procesos[servicio_id].ejecutando:
                    self._procesos[servicio_id].forzar_detencion()
            
            progreso.close()
        
        self._limpiar_y_cerrar()
        evento.accept()
    
    def _limpiar_y_cerrar(self):
        self._temporizador_recursos.stop()
        self._gestor_logs.cerrar()
        self._procesos.clear()
        ConexionBD.cerrar()
