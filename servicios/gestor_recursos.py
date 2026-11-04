import psutil
from typing import Optional, Dict

class GestorRecursos:
    _valores_cpu: Dict[int, float] = {}
    
    @staticmethod
    def obtener_recursos(pid: int) -> Dict[str, float]:
        try:
            proceso = psutil.Process(pid)
            if not proceso.is_running():
                return {'cpu': 0.0, 'memoria_mb': 0.0, 'estado': 'desconocido'}
            
            cpu = proceso.cpu_percent(interval=None)
            
            if pid not in GestorRecursos._valores_cpu:
                GestorRecursos._valores_cpu[pid] = 0.0
            else:
                GestorRecursos._valores_cpu[pid] = cpu
            
            memoria_mb = proceso.memory_info().rss / (1024 * 1024)
            
            for hijo in proceso.children(recursive=True):
                try:
                    if hijo.is_running():
                        memoria_mb += hijo.memory_info().rss / (1024 * 1024)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'cpu': round(GestorRecursos._valores_cpu.get(pid, cpu), 2),
                'memoria_mb': round(memoria_mb, 2),
                'estado': proceso.status()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            GestorRecursos._valores_cpu.pop(pid, None)
            return {'cpu': 0.0, 'memoria_mb': 0.0, 'estado': 'desconocido'}
    
    @staticmethod
    def limpiar_cache(pid: int = None):
        if pid:
            GestorRecursos._valores_cpu.pop(pid, None)
        else:
            GestorRecursos._valores_cpu.clear()
