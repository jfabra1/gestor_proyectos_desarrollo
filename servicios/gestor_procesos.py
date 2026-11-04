from PySide6.QtCore import QProcess, QObject, Signal, QTimer
from typing import Optional, List, Dict
import os
import shutil
import psutil

class ProcesoServicio(QObject):
    salida_disponible = Signal(str)
    error_disponible = Signal(str)
    proceso_iniciado = Signal(int)
    proceso_terminado = Signal(int, QProcess.ExitStatus)
    estado_cambiado = Signal(str)
    
    def __init__(self, padre=None):
        super().__init__(padre)
        self._proceso: Optional[QProcess] = None
        self._pid: Optional[int] = None
        self._ejecutando = False
        self._logs: List[str] = []
        self._max_logs = 5000
    
    @property
    def ejecutando(self) -> bool:
        return self._ejecutando
    
    @property
    def pid(self) -> Optional[int]:
        return self._pid
    
    @property
    def logs(self) -> List[str]:
        return self._logs
    
    def iniciar(self, comando: str, ruta_trabajo: str = "", variables_entorno: Dict[str, str] = None):
        if self._ejecutando:
            return
        
        self._proceso = QProcess(self)
        self._proceso.setProcessChannelMode(QProcess.MergedChannels)
        
        if ruta_trabajo and os.path.isdir(ruta_trabajo):
            self._proceso.setWorkingDirectory(ruta_trabajo)
        
        entorno = QProcess.systemEnvironment()
        if variables_entorno:
            for clave, valor in variables_entorno.items():
                entorno.append(f"{clave}={valor}")
        self._proceso.setEnvironment(entorno)
        
        self._proceso.readyReadStandardOutput.connect(self._leer_salida)
        self._proceso.readyReadStandardError.connect(self._leer_error)
        self._proceso.started.connect(self._on_iniciado)
        self._proceso.finished.connect(self._on_terminado)
        self._proceso.errorOccurred.connect(self._on_error)
        
        self._logs.clear()
        
        partes_comando = self._parsear_comando(comando)
        if len(partes_comando) > 0:
            ejecutable = shutil.which(partes_comando[0]) or partes_comando[0]
            argumentos = partes_comando[1:] if len(partes_comando) > 1 else []
            self._proceso.start(ejecutable, argumentos)
    
    def _parsear_comando(self, comando: str) -> List[str]:
        partes = []
        actual = ""
        en_comillas = False
        caracter_comilla = None
        
        for caracter in comando:
            if caracter in ('"', "'") and not en_comillas:
                en_comillas = True
                caracter_comilla = caracter
            elif caracter == caracter_comilla and en_comillas:
                en_comillas = False
                caracter_comilla = None
            elif caracter == ' ' and not en_comillas:
                if actual:
                    partes.append(actual)
                    actual = ""
            else:
                actual += caracter
        
        if actual:
            partes.append(actual)
        
        return partes
    
    def _leer_salida(self):
        if self._proceso:
            datos = self._proceso.readAllStandardOutput().data().decode('utf-8', errors='replace')
            for linea in datos.splitlines():
                self._agregar_log(linea)
                self.salida_disponible.emit(linea)
    
    def _leer_error(self):
        if self._proceso:
            datos = self._proceso.readAllStandardError().data().decode('utf-8', errors='replace')
            for linea in datos.splitlines():
                self._agregar_log(linea)
                self.salida_disponible.emit(linea)
    
    def _agregar_log(self, linea: str):
        self._logs.append(linea)
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]
    
    def _on_iniciado(self):
        self._ejecutando = True
        if self._proceso:
            self._pid = self._proceso.processId()
        mensaje = f"=== Proceso iniciado (PID: {self._pid}) ==="
        self._agregar_log(mensaje)
        self.salida_disponible.emit(mensaje)
        self.estado_cambiado.emit('ejecutando')
        self.proceso_iniciado.emit(self._pid or 0)
    
    def _on_terminado(self, codigo_salida, estado_salida):
        self._ejecutando = False
        self._pid = None
        mensaje = f"=== Proceso terminado (código: {codigo_salida}) ==="
        self._agregar_log(mensaje)
        self.salida_disponible.emit(mensaje)
        self.estado_cambiado.emit('detenido')
        self.proceso_terminado.emit(codigo_salida, estado_salida)
    
    def _on_error(self, error):
        mensajes_error = {
            QProcess.FailedToStart: "Error: No se pudo iniciar el proceso (comando no encontrado o sin permisos)",
            QProcess.Crashed: "Error: El proceso se detuvo inesperadamente",
            QProcess.Timedout: "Error: Tiempo de espera agotado",
            QProcess.ReadError: "Error de lectura del proceso",
            QProcess.WriteError: "Error de escritura al proceso",
            QProcess.UnknownError: "Error desconocido en el proceso"
        }
        mensaje = mensajes_error.get(error, f"Error en el proceso (código {error})")
        self._agregar_log(mensaje)
        self.salida_disponible.emit(mensaje)
        self._ejecutando = False
        self._pid = None
        self.estado_cambiado.emit('detenido')
        self.error_disponible.emit(mensaje)
    
    def detener(self):
        if self._proceso and self._ejecutando:
            self.estado_cambiado.emit('deteniendo')
            self._proceso.terminate()
            QTimer.singleShot(5000, self._forzar_detencion_si_sigue)
    
    def _forzar_detencion_si_sigue(self):
        if self._proceso and self._ejecutando:
            mensaje = "=== Forzando detención... ==="
            self._agregar_log(mensaje)
            self.salida_disponible.emit(mensaje)
            self._matar_arbol_procesos(self._proceso.processId())
            self._proceso.kill()
    
    def forzar_detencion(self):
        if self._proceso and self._ejecutando:
            self._matar_arbol_procesos(self._proceso.processId())
            self._proceso.kill()
    
    def _matar_arbol_procesos(self, pid):
        try:
            padre = psutil.Process(pid)
            for hijo in padre.children(recursive=True):
                try:
                    hijo.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    def escribir(self, datos: str):
        if self._proceso and self._ejecutando:
            self._proceso.write(datos.encode('utf-8'))
    
    def limpiar_logs(self):
        self._logs.clear()
