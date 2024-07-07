import os

import cv2

import numpy as np
from PySide6.QtWidgets import QWidget, QGraphicsPixmapItem, QListWidgetItem, QFileDialog
from PySide6.QtGui import QPen, QColor, QPixmap, QImage
from PySide6.QtCore import QT_TR_NOOP_UTF8, QPoint
from .ui_segmentation_refine_form import Ui_Form
from .zoom_graphics_scene import *
from .zoom_graphics_view import *
from PIL import Image
from .DataModels.seg_token_model import SegmentationViewModel
from .DataModels.image_mask_model import ImageMaskViewModel
    
class MainWidget(QWidget):
    def __init__(self, imageSegModel=None, num_seg_ids=16):
        super(MainWidget, self).__init__()
        # Auto segmentation model
        
        # image rendered on the UI side
        self.cur_qimg = None
        self.image_loaded = False
        self.x = None
        self.y = None
        self.eraser_enabled = False

        # UI image viewing setup
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.sliceScene = ZoomGraphicsScene()
        self.sliceItem = QGraphicsPixmapItem()
        self.sliceItem.setTransformationMode(Qt.SmoothTransformation)
        self.sliceScene.addItem(self.sliceItem)        
        self.sliceView = ZoomGraphicsView()
        self.sliceView.setScene(self.sliceScene)
        self.ui.verticalLayout.addWidget(self.sliceView)

        self.ui.spinBox_segId.setRange(1, num_seg_ids)
        self.ui.spinBox_curBlobID.setRange(1, num_seg_ids)
        self.ui.spinBox_newBlobID.setRange(1, num_seg_ids)

        # Load image onto UI side
        self.ui.pushButton_loadImage.clicked.connect(self.loadImage)
        # Automatically segment image for the particular seg id chosen  
        self.ui.pushButton_autoSeg.clicked.connect(self.auto_segment_image)
        # This shows cursor location
        self.sliceScene.sigMovePositionL.connect(self.show_pixel_seg_id)
        #self.sliceScene.sigPressedPositionL.connect(self.place_seg_markers)
        # Update UI 
        self.ui.checkBox_overlaySegMask.toggled.connect(self.checkBox_overlaySegMask_changed)
        self.ui.spinBox_segId.valueChanged.connect(self.spinBox_segId_changed)
        self.sliceScene.sigMovePositionR.connect(self.paint_slice)
        self.ui.checkBox_eraserEnabled.toggled.connect(self.toggle_eraser_state)
        self.ui.pushButton_updateBlobID.clicked.connect(self.changeSelectedBlobSegId)
        self.ui.pushButton_loadMasks.clicked.connect(self.loadMask)

        # Temporary containers for clicked points that will be used as tokens to SAM model
        self.seg = SegmentationViewModel(segmentation_model=imageSegModel)
        # Image & Mask data
        self.imgMask = ImageMaskViewModel(num_seg_ids=num_seg_ids, cur_segId=self.ui.spinBox_segId.value())

        #self.ui.listWidget_segIdPaletteList.itemSelectionChanged.connect(self.listWidget_segIdPaletteList_changed)
        #self.ui.pushButton_updateBlobID.clicked.connect(self.pushButton_updateBlobID_clicked)

        #self.ui.pushButton_saveMasks.clicked.connect(self.saveMasks)

        #self.selected_blob_id = -1

    def _showSegIdPallete(self):
        for i in range(1, self.imgMask.num_seg_ids+1):
            item = QListWidgetItem(f'seg_id : {i}')
            bgColor = QColor(self.imgMask.seg_palette[i][0], 
                             self.imgMask.seg_palette[i][1], 
                             self.imgMask.seg_palette[i][2])
            item.setBackground( bgColor )
            self.ui.listWidget_segIdPaletteList.insertItem(i, item)

    def changeSelectedBlobSegId(self):
        cur_selected_seg_id = self.ui.spinBox_curBlobID.value()
        new_selected_seg_id = self.ui.spinBox_newBlobID.value()
        self.imgMask.update_id_mask()
        self.imgMask.zero_out_qmask()
        if not self.ui.checkBox_overlaySegMask.isChecked():
            self.ui.checkBox_overlaySegMask.toggle()
        self.imgMask.change_idMask_segId(cur_selected_seg_id, new_selected_seg_id)
        self.seg.clear_prompts()
        self._updateQImage()

    def loadImage(self):
        init_path = os.getcwd()
        try:
            fileName = QFileDialog.getOpenFileName(self, 'Select file to open', init_path, 'png file(*.png)')[0]
        
            # Open image
            with Image.open(fileName) as image:
                self.imgMask.set_uint8_rgb_imageData_empty_masks(image)
            image = self.imgMask.image
            height, width = self.imgMask.shape2D

            # Get the embedded image token from SAM for segmentation processes down the line
            if self.seg.model_exists and self.imgMask.image_exists: 
                self.seg.set_image(image) # requires HWC format
            
            # Load image to UI
            self.cur_qimg = QImage(bytes(image.data), width, height, width*3, 
                                        QImage.Format.Format_RGB888)
            self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))

            self.resetToFit()
            self._showSegIdPallete()
            self.image_loaded = True
        except: 
            print("Loading image aborted...!")

    def loadMask(self):
        if self.image_loaded:
            init_path = os.getcwd()
            try:
                fileName = QFileDialog.getOpenFileName(self, 'Select file to open', init_path, 'png file(*.png)')[0]
            
                #Load mask
                with Image.open(fileName) as mask:
                    self.set_mask(mask)
                
                # Get the embedded image token from SAM for segmentation processes down the line
                if self.imgMask.image_exists: self._updateQImage()
                print("Mask loaded!")
                
            except: 
                print("Loading mask aborted...!")
        else:
            print("Load in an image first!")

    def auto_segment_image(self):
        if self.image_loaded:
            point_coords, point_labels = self.seg.prompts
            if len(point_coords) == 0:
                print("No point prompts added!")
                return
            print(f"point_coords_shape: {point_coords.shape}")
            print(f"point_labels_shape: {point_labels.shape}")
            # Outputs 1 x H x W numpy array
            
            mask = self.seg.predict(point_coords=point_coords,
                                    point_labels=point_labels,
                                    multimask_output=False)[0]
            """
            mask = self.seg.predict(point_coords=np.array([[128, 60],]),
                                    point_labels=np.array([0]),
                                    multimask_output=False)[0]
            """
            # Update self.imgMask._qmask (ie. add the segmentation onto the slice)
            self.imgMask.auto_brush_qmask(mask=mask)
            self.seg.clear_prompts()
            self._updateQImage()
        else:
            print("Either model doesn't exist or image doesn't exist!\n")
            
    def show_pixel_seg_id(self, point):
        if self.image_loaded and self.imgMask.id_mask_exists:
            x = int(point.x())
            y = int(point.y())
            self.x = x
            self.y = y
            height, width = self.imgMask.shape2D  
            if x >= 0 and x < width and \
               y >= 0 and y < height:
                self.ui.label_curPos.setText(f'Pos ({x}, {y})')
                id = self.imgMask.qmask[y][x]
                if id == 0: id = self.imgMask.id_mask[y][x]
                self.ui.label_curSegID.setText(f'Seg ID = {id}') 

    def _updateQImage(self):
        if self.image_loaded:
            
            RGB, qmask_valid_mask = self.imgMask.create_qimg_using_qmask()

            if self.ui.checkBox_overlaySegMask.isChecked():
                self.imgMask.update_qimg_using_id_mask(RGB, ~qmask_valid_mask)

            height, width = self.imgMask.shape2D
            self.cur_qimg = QImage(bytes(RGB.data), width, height, width*3, 
                                        QImage.Format.Format_RGB888)
            self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))

    def checkBox_overlaySegMask_changed(self, state):
        if self.image_loaded: self._updateQImage()

    def spinBox_segId_changed(self, segId):
        if self.image_loaded:
            self.seg.clear_prompts()
            self.imgMask.update_id_mask()
            self.imgMask.cur_segId = segId
            self.imgMask.load_qmask_from_id_mask()
            self._updateQImage()

    def mix_pixel_with_seg_color(self, qimg, cur_x, cur_y, seg_id):#, org_den, seg_id): 
        try:
            out_pixel = self.imgMask.image[cur_y][cur_x]
            updated_pixel = None
            if seg_id != 0:
                seg_color = self.imgMask.seg_palette[seg_id]   
                updated_pixel = (out_pixel / 2) + (seg_color / 2)    
            else: updated_pixel = out_pixel
            #print(updated_pixel.shape)                   
            mix_color = QColor(updated_pixel[0], updated_pixel[1], updated_pixel[2])
            qimg.setPixelColor(cur_x, cur_y, mix_color)
        except KeyError:
            print(f"seg_id : {self.imgMask.cur_segId} does not exist in the dictionary.")

    def paint_slice(self, point):
        pos_x = int(point.x())
        pos_y = int(point.y())
        brush_size = self.ui.spinBox_brushSize.value()
        for y in range(brush_size):
            for x in range(brush_size):                                
                cur_x = pos_x + x
                cur_y = pos_y + y
                if cur_x >= 0 and cur_x < self.cur_qimg.width() and cur_y >= 0 and cur_y < self.cur_qimg.height(): 
                    if self.eraser_enabled:
                        self.imgMask.brush_qmask(cur_y, cur_x, 0)
                        self.mix_pixel_with_seg_color(self.cur_qimg, cur_x, cur_y, 0)
                    else:
                        self.imgMask.brush_qmask(cur_y, cur_x, self.imgMask.cur_segId)
                        self.mix_pixel_with_seg_color(self.cur_qimg, cur_x, cur_y, self.imgMask.cur_segId)
        
        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))  

    """
    def listWidget_segIdPaletteList_changed(self):
        self.selected_blob_id = self.ui.listWidget_segIdPaletteList.currentRow()
        self.ui.spinBox_curBlobID.setValue(self.selected_blob_id)
        
        print(f'selected_id = {self.selected_blob_id}')
        self._updateQImage(self.getCurSliceNum())

    def pushButton_updateBlobID_clicked(self):
        # 나중에는 같은 seg mask id 를 가진 blob 이라도 CCL 돌려서 개별적으로 id 업데이트해야하지만..
        # 우선은 해당 id 전체를 새 id 로 업데이트 한다.
        old_id = self.ui.spinBox_curBlobID.value()
        new_id = self.ui.spinBox_newBlobID.value()
        cur_slice_num = self.getCurSliceNum()
        id_mask = self.getIdMasks()[cur_slice_num]
        id_mask[id_mask == old_id] = new_id        
        # listWidget currentRow selection 해제해 주기.
        cur_row = self.ui.listWidget_segIdPaletteList.currentRow()
        item = self.ui.listWidget_segIdPaletteList.item(cur_row)
        self.ui.listWidget_segIdPaletteList.blockSignals(True)
        item.setSelected(False)
        self.ui.listWidget_segIdPaletteList.blockSignals(False)
        #self.selected_blob_id = -1 # 리셋 안하는게 더 편한거 같기도??

        print(f'blob id has changed from {old_id} to {new_id}')
        self._updateQImage(cur_slice_num)
    """
    def add_prompt_point(self):
        self.seg.add_seg_point([self.x, self.y])
        # Update UI
        r = 5
        for y in range(r):
            for x in range(r):                                
                cur_x = self.x + x
                cur_y = self.y + y
                if cur_x >= 0 and cur_x < self.cur_qimg.width() and cur_y >= 0 and cur_y < self.cur_qimg.height(): 
                    self.cur_qimg.setPixelColor(cur_x, cur_y, QColor(0, 0, 0))
                    self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))

    def remove_prompt_point(self):
        rm_x, rm_y = self.seg.remove_seg_point()
        if rm_x is not None:
            r = 5
            for y in range(r):
                for x in range(r):                                
                    cur_x = rm_x + x
                    cur_y = rm_y + y
                    if cur_x >= 0 and cur_x < self.cur_qimg.width() and cur_y >= 0 and cur_y < self.cur_qimg.height(): 
                        seg_id = self.imgMask.qmask[y][x]
                        if seg_id == 0: seg_id = self.imgMask.id_mask[cur_y][cur_x]
                        self.mix_pixel_with_seg_color(self.cur_qimg, cur_x, cur_y, seg_id)
                        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))

    def toggle_eraser_state(self, state):
        self.eraser_enabled = state

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Q:
            value = self.ui.spinBox_brushSize.value() - 1
            if (value >= self.ui.spinBox_brushSize.minimum()):
                self.ui.spinBox_brushSize.setValue(value)
                print(f"brush_size : {value}")
        elif e.key() == Qt.Key_W:
            value = self.ui.spinBox_brushSize.value() + 1
            if (value <= self.ui.spinBox_brushSize.maximum()):
                self.ui.spinBox_brushSize.setValue(value)
                print(f"brush_size : {value}")
        elif e.key() == Qt.Key_Z:
            value = self.ui.spinBox_segId.value() - 1
            if (value >= self.ui.spinBox_segId.minimum()):
                self.ui.spinBox_segId.setValue(value)
                print(f"seg_id : {value}")
        elif e.key() == Qt.Key_X:
            value = self.ui.spinBox_segId.value() + 1
            if (value <= self.ui.spinBox_segId.maximum()):
                self.ui.spinBox_segId.setValue(value)
                print(f"seg_id : {value}")
        elif e.key() == Qt.Key_Space:
            self.ui.checkBox_overlaySegMask.toggle()
            print(f"Overlay seg mask : {self.ui.checkBox_overlaySegMask.isChecked()}")
        elif e.key() == Qt.Key_A:
            self.add_prompt_point()
        elif e.key() == Qt.Key_S:
            self.remove_prompt_point()
        elif e.key() == Qt.Key_E:
            self.ui.checkBox_eraserEnabled.toggle()
        elif e.key() == Qt.Key_D: 
            self.auto_segment_image()
            
    def resetToFit(self):
        # reset to fit
        if self.cur_qimg is not None:
            self.sliceView.resetTransform()
            self.sliceView.setSceneRect(0, 0, self.cur_qimg.width(), self.cur_qimg.height())
            self.sliceView.fitInView(0, 0, self.cur_qimg.width(), self.cur_qimg.height(), Qt.KeepAspectRatio)
    
    def saveMasks(self):
        # push current qmask to id_mask and save
        print('saveMasks clicked')
