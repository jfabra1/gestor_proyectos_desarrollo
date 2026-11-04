from pathlib import Path
from typing import Optional

def validar_ruta(ruta: str) -> bool:
    return Path(ruta).exists()

def obtener_nombre_ruta(ruta: str) -> str:
    return Path(ruta).name

def asegurar_directorio(ruta: str):
    Path(ruta).mkdir(parents=True, exist_ok=True)

def formatear_memoria(mb: float) -> str:
    if mb < 1024:
        return f"{mb:.1f} MB"
    return f"{mb/1024:.2f} GB"

def formatear_cpu(percent: float) -> str:
    return f"{percent:.1f}%"

def color_segun_cpu(percent: float) -> str:
    if percent < 50:
        return "#2ecc71"
    elif percent < 80:
        return "#f39c12"
    return "#e74c3c"
