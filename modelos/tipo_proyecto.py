from dataclasses import dataclass
from typing import Optional

@dataclass
class TipoProyecto:
    id: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    color: str = "#3498db"
