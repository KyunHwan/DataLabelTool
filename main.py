from PySide6.QtWidgets import QApplication
import sys
from src.Qt.image_labeler import MainWidget
from .segment_anything.segment_anything.predictor import SamPredictor

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet('''
    QListWidget::item:selected {
        background: red;
        color: yellow;
    }''')

    window = MainWidget()    
    window.show()

    sys.exit(app.exec())
