from dataclasses import dataclass, field
from typing import Optional, List, Dict
import json

@dataclass
class Servicio:
    id: Optional[int] = None
    proyecto_id: Optional[int] = None
    nombre: str = ""
    tipo_comando: str = "npm"
    comando: str = "npm run dev"
    ruta_trabajo: str = ""
    puertos: List[int] = field(default_factory=list)
    variables_entorno: Dict[str, str] = field(default_factory=dict)
    orden: int = 0
    
    def puertos_json(self) -> str:
        return json.dumps(self.puertos)
    
    def variables_json(self) -> str:
        return json.dumps(self.variables_entorno)
    
    @classmethod
    def desde_fila(cls, fila):
        return cls(
            id=fila['id'],
            proyecto_id=fila['proyecto_id'],
            nombre=fila['nombre'],
            tipo_comando=fila['tipo_comando'],
            comando=fila['comando'],
            ruta_trabajo=fila['ruta_trabajo'] or "",
            puertos=json.loads(fila['puertos'] or '[]'),
            variables_entorno=json.loads(fila['variables_entorno'] or '{}'),
            orden=fila['orden']
        )
