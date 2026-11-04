from pathlib import Path
from datetime import datetime
from typing import List, Dict
from PySide6.QtCore import QObject, QTimer

class GestorLogs(QObject):
    def __init__(self, directorio_base=None):
        super().__init__()
        if directorio_base is None:
            self._directorio = Path.home() / ".gestor_proyectos" / "logs"
        else:
            self._directorio = Path(directorio_base)
        self._directorio.mkdir(parents=True, exist_ok=True)
        self._buffer: Dict[int, list] = {}
        self._temporizador = QTimer(self)
        self._temporizador.timeout.connect(self._vaciar_buffer)
        self._temporizador.start(1000)
    
    def _vaciar_buffer(self):
        for servicio_id, lineas in list(self._buffer.items()):
            if lineas:
                self._escribir_lineas(servicio_id, lineas)
                self._buffer[servicio_id] = []
    
    def _escribir_lineas(self, servicio_id: int, lineas: list):
        archivo = self._directorio / f"servicio_{servicio_id}.log"
        try:
            with open(archivo, 'a', encoding='utf-8') as f:
                f.write('\n'.join(lineas) + '\n')
        except Exception:
            pass
    
    def guardar_log(self, servicio_id: int, linea: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"[{timestamp}] {linea}"
        if servicio_id not in self._buffer:
            self._buffer[servicio_id] = []
        self._buffer[servicio_id].append(entrada)
    
    def obtener_log(self, servicio_id: int, lineas: int = 1000) -> List[str]:
        self._vaciar_buffer_servicio(servicio_id)
        archivo = self._directorio / f"servicio_{servicio_id}.log"
        if not archivo.exists():
            return []
        with open(archivo, 'r', encoding='utf-8') as f:
            todas = f.readlines()
            return [l.strip() for l in todas[-lineas:]]
    
    def _vaciar_buffer_servicio(self, servicio_id: int):
        if servicio_id in self._buffer and self._buffer[servicio_id]:
            self._escribir_lineas(servicio_id, self._buffer[servicio_id])
            self._buffer[servicio_id] = []
    
    def limpiar_log(self, servicio_id: int):
        self._buffer.pop(servicio_id, None)
        archivo = self._directorio / f"servicio_{servicio_id}.log"
        if archivo.exists():
            archivo.write_text("")
    
    def exportar_log(self, servicio_id: int, ruta_destino: str) -> bool:
        try:
            self._vaciar_buffer_servicio(servicio_id)
            archivo_origen = self._directorio / f"servicio_{servicio_id}.log"
            if archivo_origen.exists():
                import shutil
                shutil.copy2(str(archivo_origen), ruta_destino)
                return True
            return False
        except Exception:
            return False
    
    def log_existe(self, servicio_id: int) -> bool:
        archivo = self._directorio / f"servicio_{servicio_id}.log"
        return archivo.exists() and archivo.stat().st_size > 0
    
    def cerrar(self):
        self._temporizador.stop()
        self._vaciar_buffer()
