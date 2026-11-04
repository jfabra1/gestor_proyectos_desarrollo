from PySide6.QtGui import QPainter, QColor, QFont, QPixmap, QIcon, QPen, QBrush
from PySide6.QtCore import Qt, QRect, QPoint
import os

TAMANO = 256

def generar_icono():
    pixmap = QPixmap(TAMANO, TAMANO)
    pixmap.fill(Qt.transparent)
    
    pintor = QPainter(pixmap)
    pintor.setRenderHint(QPainter.Antialiasing)
    
    centro_x = TAMANO // 2
    centro_y = TAMANO // 2
    radio = TAMANO // 2 - 8
    
    pintor.setBrush(QBrush(QColor("#3498db")))
    pintor.setPen(Qt.NoPen)
    pintor.drawRoundedRect(QRect(4, 4, TAMANO - 8, TAMANO - 8), 40, 40)
    
    pintor.setBrush(QBrush(QColor("#2980b9")))
    rect_interno = QRect(20, 20, TAMANO - 40, TAMANO - 40)
    pintor.drawRoundedRect(rect_interno, 30, 30)
    
    fuente = QFont("Segoe UI", 48, QFont.Bold)
    pintor.setFont(fuente)
    pintor.setPen(QColor("white"))
    pintor.drawText(QRect(0, centro_y - 60, TAMANO, 60), Qt.AlignCenter, "GP")
    
    pintor.setFont(QFont("Segoe UI", 18, QFont.Normal))
    pintor.drawText(QRect(0, centro_y, TAMANO, 40), Qt.AlignCenter, "GESTOR")
    
    pintor.end()
    
    ruta_archivo = os.path.join(os.path.dirname(__file__), "iconos", "app.ico")
    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
    
    icono = QIcon(pixmap)
    if not pixmap.save(ruta_archivo, "ICO"):
        from PySide6.QtCore import QBuffer, QByteArray
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QBuffer.WriteOnly)
        pixmap.save(buf, "PNG")
        buf.close()
        png_ruta = os.path.join(os.path.dirname(__file__), "iconos", "app.png")
        with open(png_ruta, "wb") as f:
            f.write(ba.data())
        print(f"Icono PNG guardado en: {png_ruta}")
        print("PySide6 no soporta guardar ICO directamente. Usaremos PNG como icono.")
        ruta_archivo = png_ruta
    
    print(f"Icono guardado en: {ruta_archivo}")
    return ruta_archivo

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    generar_icono()
