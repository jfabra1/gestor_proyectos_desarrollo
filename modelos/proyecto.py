from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Proyecto:
    id: Optional[int] = None
    nombre: str = ""
    ruta: str = ""
    tipo_id: Optional[int] = None
    descripcion: str = ""
    fecha_creacion: Optional[datetime] = None
