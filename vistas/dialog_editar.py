from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QSpinBox, QFormLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QColorDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from bd.conexion import ConexionBD
from modelos.proyecto import Proyecto
from modelos.servicio import Servicio
import json

class DialogEditarTipoProyecto(QDialog):
    def __init__(self, padre=None, tipo=None):
        super().__init__(padre)
        self._tipo = tipo
        self.setWindowTitle("Editar Tipo de Proyecto" if tipo else "Nuevo Tipo de Proyecto")
        self.setMinimumWidth(400)
        self._inicializar_ui()
        if tipo:
            self._cargar_datos()
    
    def _inicializar_ui(self):
        layout = QVBoxLayout(self)
        
        formulario = QFormLayout()
        
        self._campo_nombre = QLineEdit()
        formulario.addRow("Nombre:", self._campo_nombre)
        
        self._campo_descripcion = QTextEdit()
        self._campo_descripcion.setMaximumHeight(80)
        formulario.addRow("Descripción:", self._campo_descripcion)
        
        layout_color = QHBoxLayout()
        self._campo_color = QLineEdit("#3498db")
        layout_color.addWidget(self._campo_color)
        self._boton_color = QPushButton("Elegir...")
        self._boton_color.clicked.connect(self._elegir_color)
        layout_color.addWidget(self._boton_color)
        formulario.addRow("Color:", layout_color)
        
        layout.addLayout(formulario)
        
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        boton_guardar = QPushButton("Guardar")
        boton_guardar.setObjectName("boton_exito")
        boton_guardar.clicked.connect(self._guardar)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
    
    def _elegir_color(self):
        color = QColorDialog.getColor(QColor(self._campo_color.text()), self)
        if color.isValid():
            self._campo_color.setText(color.name())
    
    def _cargar_datos(self):
        if self._tipo:
            self._campo_nombre.setText(self._tipo.nombre)
            self._campo_descripcion.setText(self._tipo.descripcion)
            self._campo_color.setText(self._tipo.color)
    
    def _guardar(self):
        if not self._campo_nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        self.accept()
    
    def obtener_datos(self):
        return {
            'nombre': self._campo_nombre.text().strip(),
            'descripcion': self._campo_descripcion.toPlainText().strip(),
            'color': self._campo_color.text()
        }

class DialogEditarProyecto(QDialog):
    def __init__(self, padre=None, proyecto=None, tipo_id_inicial=None):
        super().__init__(padre)
        self._proyecto = proyecto
        self._tipo_id_inicial = tipo_id_inicial
        self._bd = ConexionBD.obtener_instancia()
        self.setWindowTitle("Editar Proyecto" if proyecto else "Nuevo Proyecto")
        self.setMinimumWidth(500)
        self._inicializar_ui()
        if proyecto:
            self._cargar_datos()
    
    def _inicializar_ui(self):
        layout = QVBoxLayout(self)
        
        formulario = QFormLayout()
        
        self._campo_nombre = QLineEdit()
        formulario.addRow("Nombre:", self._campo_nombre)
        
        layout_ruta = QHBoxLayout()
        self._campo_ruta = QLineEdit()
        layout_ruta.addWidget(self._campo_ruta)
        boton_examinar = QPushButton("Examinar...")
        boton_examinar.clicked.connect(self._examinar_ruta)
        layout_ruta.addWidget(boton_examinar)
        formulario.addRow("Ruta:", layout_ruta)
        
        self._campo_tipo = QComboBox()
        self._cargar_tipos()
        formulario.addRow("Tipo:", self._campo_tipo)
        
        self._campo_descripcion = QTextEdit()
        self._campo_descripcion.setMaximumHeight(80)
        formulario.addRow("Descripción:", self._campo_descripcion)
        
        layout.addLayout(formulario)
        
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        boton_guardar = QPushButton("Guardar")
        boton_guardar.setObjectName("boton_exito")
        boton_guardar.clicked.connect(self._guardar)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
    
    def _cargar_tipos(self):
        self._campo_tipo.clear()
        with self._bd.conectar() as cursor:
            cursor.execute("SELECT id, nombre FROM tipos_proyecto ORDER BY nombre")
            tipos = cursor.fetchall()
            for tipo in tipos:
                self._campo_tipo.addItem(tipo['nombre'], tipo['id'])
        
        if self._tipo_id_inicial:
            idx = self._campo_tipo.findData(self._tipo_id_inicial)
            if idx >= 0:
                self._campo_tipo.setCurrentIndex(idx)
    
    def _examinar_ruta(self):
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta del proyecto")
        if ruta:
            self._campo_ruta.setText(ruta)
    
    def _cargar_datos(self):
        if self._proyecto:
            self._campo_nombre.setText(self._proyecto.nombre)
            self._campo_ruta.setText(self._proyecto.ruta)
            self._campo_descripcion.setText(self._proyecto.descripcion)
            if self._proyecto.tipo_id:
                idx = self._campo_tipo.findData(self._proyecto.tipo_id)
                if idx >= 0:
                    self._campo_tipo.setCurrentIndex(idx)
    
    def _guardar(self):
        if not self._campo_nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        if not self._campo_ruta.text().strip():
            QMessageBox.warning(self, "Error", "La ruta es obligatoria")
            return
        if self._campo_tipo.currentIndex() < 0:
            QMessageBox.warning(self, "Error", "Debes seleccionar un tipo de proyecto")
            return
        self.accept()
    
    def obtener_datos(self):
        return {
            'nombre': self._campo_nombre.text().strip(),
            'ruta': self._campo_ruta.text().strip(),
            'tipo_id': self._campo_tipo.currentData(),
            'descripcion': self._campo_descripcion.toPlainText().strip()
        }

class DialogEditarServicio(QDialog):
    def __init__(self, padre=None, servicio=None, orden_inicial=0):
        super().__init__(padre)
        self._servicio = servicio
        self._orden_inicial = orden_inicial
        self.setWindowTitle("Editar Servicio" if servicio else "Nuevo Servicio")
        self.setMinimumWidth(600)
        self._inicializar_ui()
        if servicio:
            self._cargar_datos()
    
    def _inicializar_ui(self):
        layout = QVBoxLayout(self)
        
        grupo_basico = QGroupBox("Información Básica")
        layout_basico = QFormLayout(grupo_basico)
        
        self._campo_nombre = QLineEdit()
        layout_basico.addRow("Nombre:", self._campo_nombre)
        
        self._campo_tipo = QComboBox()
        self._campo_tipo.addItems(["npm", "python", "docker", "otro"])
        layout_basico.addRow("Tipo:", self._campo_tipo)
        
        self._campo_comando = QLineEdit()
        self._campo_comando.setPlaceholderText("ej: npm run dev, python manage.py runserver")
        layout_basico.addRow("Comando:", self._campo_comando)
        
        layout_ruta = QHBoxLayout()
        self._campo_ruta = QLineEdit()
        self._campo_ruta.setPlaceholderText("Dejar vacío para usar la ruta del proyecto")
        layout_ruta.addWidget(self._campo_ruta)
        boton_examinar = QPushButton("Examinar...")
        boton_examinar.clicked.connect(self._examinar_ruta)
        layout_ruta.addWidget(boton_examinar)
        layout_basico.addRow("Ruta trabajo:", layout_ruta)
        
        self._campo_orden = QSpinBox()
        self._campo_orden.setRange(0, 999)
        self._campo_orden.setValue(self._orden_inicial)
        layout_basico.addRow("Orden:", self._campo_orden)
        
        layout.addWidget(grupo_basico)
        
        grupo_puertos = QGroupBox("Puertos")
        layout_puertos = QVBoxLayout(grupo_puertos)
        
        layout_puertos_entrada = QHBoxLayout()
        self._campo_puerto = QSpinBox()
        self._campo_puerto.setRange(1, 65535)
        layout_puertos_entrada.addWidget(self._campo_puerto)
        boton_agregar_puerto = QPushButton("Agregar")
        boton_agregar_puerto.clicked.connect(self._agregar_puerto)
        layout_puertos_entrada.addWidget(boton_agregar_puerto)
        boton_eliminar_puerto = QPushButton("Eliminar")
        boton_eliminar_puerto.setObjectName("boton_peligro")
        boton_eliminar_puerto.clicked.connect(self._eliminar_puerto)
        layout_puertos_entrada.addWidget(boton_eliminar_puerto)
        layout_puertos_entrada.addStretch()
        layout_puertos.addLayout(layout_puertos_entrada)
        
        self._tabla_puertos = QTableWidget(0, 1)
        self._tabla_puertos.setHorizontalHeaderLabels(["Puerto"])
        self._tabla_puertos.setMaximumHeight(100)
        self._tabla_puertos.setSelectionBehavior(QTableWidget.SelectRows)
        layout_puertos.addWidget(self._tabla_puertos)
        
        layout.addWidget(grupo_puertos)
        
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        boton_guardar = QPushButton("Guardar")
        boton_guardar.setObjectName("boton_exito")
        boton_guardar.clicked.connect(self._guardar)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
    
    def _examinar_ruta(self):
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de trabajo")
        if ruta:
            self._campo_ruta.setText(ruta)
    
    def _agregar_puerto(self):
        puerto = self._campo_puerto.value()
        fila = self._tabla_puertos.rowCount()
        self._tabla_puertos.insertRow(fila)
        self._tabla_puertos.setItem(fila, 0, QTableWidgetItem(str(puerto)))
    
    def _eliminar_puerto(self):
        fila_seleccionada = self._tabla_puertos.currentRow()
        if fila_seleccionada >= 0:
            self._tabla_puertos.removeRow(fila_seleccionada)
    
    def _cargar_datos(self):
        if self._servicio:
            self._campo_nombre.setText(self._servicio.nombre)
            idx = self._campo_tipo.findText(self._servicio.tipo_comando)
            if idx >= 0:
                self._campo_tipo.setCurrentIndex(idx)
            self._campo_comando.setText(self._servicio.comando)
            self._campo_ruta.setText(self._servicio.ruta_trabajo)
            self._campo_orden.setValue(self._servicio.orden)
            
            for puerto in self._servicio.puertos:
                fila = self._tabla_puertos.rowCount()
                self._tabla_puertos.insertRow(fila)
                self._tabla_puertos.setItem(fila, 0, QTableWidgetItem(str(puerto)))
    
    def _guardar(self):
        if not self._campo_nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        if not self._campo_comando.text().strip():
            QMessageBox.warning(self, "Error", "El comando es obligatorio")
            return
        self.accept()
    
    def obtener_datos(self):
        puertos = []
        for fila in range(self._tabla_puertos.rowCount()):
            item = self._tabla_puertos.item(fila, 0)
            if item:
                try:
                    puertos.append(int(item.text()))
                except ValueError:
                    pass
        
        return {
            'nombre': self._campo_nombre.text().strip(),
            'tipo_comando': self._campo_tipo.currentText(),
            'comando': self._campo_comando.text().strip(),
            'ruta_trabajo': self._campo_ruta.text().strip(),
            'puertos': puertos,
            'puertos_json': json.dumps(puertos),
            'variables_entorno': {},
            'variables_json': '{}',
            'orden': self._campo_orden.value()
        }
