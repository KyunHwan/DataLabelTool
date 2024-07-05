from PySide6.QtWidgets import QApplication
import sys
import os
import re
from src.Qt.image_labeler import MainWidget
from src.utils.download_model_checkpoint import get_checkpoint, get_model_type_from_model_checkpoint
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
    
    url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    model_checkpoint = get_checkpoint(current_script_dir=current_script_dir, url=url)
    if model_checkpoint is None:
        sys.exit()

    model_type = get_model_type_from_model_checkpoint(model_checkpoint=model_checkpoint)
    print("Loading model!\n")
    sam = sam_model_registry[model_type](checkpoint=model_checkpoint)
    predictor = SamPredictor(sam)
    print("Model loaded!\n")

    # Passes the Segment Anything Model to the Labeling Tool
    window = MainWidget(imageSegModel=predictor)    
    window.show()

    sys.exit(app.exec())
