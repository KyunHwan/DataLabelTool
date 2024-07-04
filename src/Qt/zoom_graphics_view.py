from PySide6.QtWidgets import QWidget, QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PySide6.QtGui import QPen, QColor, QPixmap, QImage, QWheelEvent
from PySide6.QtCore import Qt, QRectF

class ZoomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True) # 마우스 왼쪽 무브 트래킹 필요시!

    def enterEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QApplication.restoreOverrideCursor()
        super().leaveEvent(event)

    def wheelEvent(self, event):
        numDegrees = -event.angleDelta().y() / 8.0
        numSteps = numDegrees / 15.0
        factor = pow(1.125, numSteps)
        self.scale(factor, factor)
        super().wheelEvent(event)
