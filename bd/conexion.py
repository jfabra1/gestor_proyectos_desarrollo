import sqlite3
from pathlib import Path
from contextlib import contextmanager

class ConexionBD:
    _instancia = None
    _ruta_bd = None
    
    @classmethod
    def inicializar(cls, ruta_bd=None):
        if ruta_bd is None:
            directorio_datos = Path.home() / ".gestor_proyectos"
            directorio_datos.mkdir(exist_ok=True)
            cls._ruta_bd = directorio_datos / "proyectos.db"
        else:
            cls._ruta_bd = Path(ruta_bd)
        
        cls._instancia = cls()
        cls._instancia._crear_tablas()
    
    @classmethod
    def obtener_instancia(cls):
        if cls._instancia is None:
            raise RuntimeError("Base de datos no inicializada. Llamar a inicializar() primero.")
        return cls._instancia
    
    def __init__(self):
        self._conexion = None
    
    def _crear_tablas(self):
        with self.conectar() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tipos_proyecto (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT,
                    color TEXT DEFAULT '#3498db'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyectos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    ruta TEXT NOT NULL,
                    tipo_id INTEGER,
                    descripcion TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tipo_id) REFERENCES tipos_proyecto(id) ON DELETE SET NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS servicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proyecto_id INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    tipo_comando TEXT NOT NULL,
                    comando TEXT NOT NULL,
                    ruta_trabajo TEXT,
                    puertos TEXT DEFAULT '[]',
                    variables_entorno TEXT DEFAULT '{}',
                    orden INTEGER DEFAULT 0,
                    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT
                )
            """)
    
    @contextmanager
    def conectar(self):
        conexion = sqlite3.connect(str(self._ruta_bd))
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON")
        try:
            yield conexion.cursor()
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()
    
    @classmethod
    def cerrar(cls):
        if cls._instancia:
            cls._instancia = None
