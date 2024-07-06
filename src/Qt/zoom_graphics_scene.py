from PySide6.QtWidgets import QWidget, QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PySide6.QtGui import QPen, QColor, QPixmap, QImage
from PySide6.QtCore import Qt, Signal, QPointF

class ZoomGraphicsScene(QGraphicsScene):

    sigMovePositionL = Signal(QPointF) 
    sigPressedPositionL = Signal(QPointF)
    sigMovePositionR = Signal(QPointF)
    #sigReleasePosition = Signal(QPointF) 

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.mouseStartPnt = event.scenePos()
        elif event.button() == Qt.LeftButton:
            self.sigPressedPositionL.emit(event.scenePos())
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.RightButton:
            self.sigMovePositionR.emit(event.scenePos())
        else:
            self.sigMovePositionL.emit(event.scenePos())

        # elif event.buttons() & Qt.LeftButton:
        #     self.sigMovePositionL.emit(event.scenePos())

        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        # if event.button() == Qt.RightButton:
        #     self.sigReleasePosition.emit(event.scenePos())

        super().mouseReleaseEvent(event)