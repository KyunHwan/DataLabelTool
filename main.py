from PySide6.QtWidgets import QApplication
import sys
import os
from src.Qt.image_labeler import MainWidget
from segment_anything.segment_anything import SamPredictor, sam_model_registry

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Sets the current working directory to where this file is
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    os.chdir(current_script_dir)

    app.setStyleSheet('''
    QListWidget::item:selected {
        background: red;
        color: yellow;
    }''')
    
    # Loads the Segment Anything Model
    model_checkpoint_dir = os.path.join(current_script_dir, 'segment_anything_checkpoint')
    model_checkpoint = os.path.join(model_checkpoint_dir, os.listdir(model_checkpoint_dir)[0])
    sam = sam_model_registry["default"](checkpoint=model_checkpoint)
    predictor = SamPredictor(sam)

    # Passes the Segment Anything Model to the Labeling Tool
    window = MainWidget(imageSegModel=predictor)    
    window.show()

    sys.exit(app.exec())
