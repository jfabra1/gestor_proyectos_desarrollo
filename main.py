import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from vistas.ventana_principal import VentanaPrincipal
from bd.conexion import ConexionBD

def main():
    aplicacion = QApplication(sys.argv)
    
    
    aplicacion.setApplicationName("Gestor de Proyectos")
    aplicacion.setOrganizationName("MiEmpresa")
    
    ConexionBD.inicializar()
    
    ventana = VentanaPrincipal()
    ventana.show()
    
    codigo_salida = aplicacion.exec()
    sys.exit(codigo_salida)

if __name__ == "__main__":
    main()
