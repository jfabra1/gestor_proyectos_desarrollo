import socket
import subprocess
import platform
from typing import List, Tuple, Optional
import psutil

class GestorPuertos:
    @staticmethod
    def puerto_disponible(puerto: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            resultado = s.connect_ex(('127.0.0.1', puerto))
            return resultado != 0
    
    @staticmethod
    def verificar_puertos(puertos: List[int]) -> Tuple[List[int], List[int]]:
        disponibles = []
        ocupados = []
        for puerto in puertos:
            if GestorPuertos.puerto_disponible(puerto):
                disponibles.append(puerto)
            else:
                ocupados.append(puerto)
        return disponibles, ocupados
    
    @staticmethod
    def obtener_proceso_puerto(puerto: int) -> str:
        try:
            if platform.system() == 'Windows':
                resultado = subprocess.run(
                    ['netstat', '-ano'],
                    capture_output=True, text=True, timeout=5
                )
                for linea in resultado.stdout.split('\n'):
                    if f':{puerto}' in linea and 'LISTENING' in linea:
                        partes = linea.split()
                        if partes:
                            return f"PID: {partes[-1]}"
            return "Desconocido"
        except Exception:
            return "Desconocido"
    
    @staticmethod
    def obtener_pid_puerto(puerto: int) -> Tuple[Optional[int], str]:
        try:
            if platform.system() == 'Windows':
                resultado = subprocess.run(
                    ['netstat', '-ano'],
                    capture_output=True, text=True, timeout=5
                )
                for linea in resultado.stdout.split('\n'):
                    if f':{puerto}' in linea and 'LISTENING' in linea:
                        partes = linea.split()
                        if partes and partes[-1].isdigit():
                            pid = int(partes[-1])
                            try:
                                proc = psutil.Process(pid)
                                nombre = proc.name()
                            except psutil.NoSuchProcess:
                                nombre = "desconocido"
                            return pid, nombre
            return None, "PID no encontrado"
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def matar_proceso_puerto(puerto: int) -> Tuple[bool, str]:
        pid, nombre = GestorPuertos.obtener_pid_puerto(puerto)
        if pid is None:
            return False, f"No se encontró proceso en el puerto {puerto}"
        try:
            proc = psutil.Process(pid)
            proc.kill()
            proc.wait(timeout=3)
            return True, f"Proceso {nombre} (PID {pid}) eliminado"
        except psutil.NoSuchProcess:
            return True, "El proceso ya no existía"
        except psutil.AccessDenied:
            return False, f"Acceso denegado al proceso {nombre} (PID {pid})"
        except Exception as e:
            return False, str(e)
