import os

import cv2

import numpy as np
from PySide6.QtWidgets import QWidget, QGraphicsPixmapItem, QListWidgetItem, QFileDialog
from PySide6.QtGui import QPen, QColor, QPixmap, QImage
from PySide6.QtCore import QT_TR_NOOP_UTF8
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
        # Temporary containers for clicked points that will be used as tokens to SAM model
        self.seg = SegmentationViewModel(segmentation_model=imageSegModel)
        # Image & Mask data
        self.imgMask = ImageMaskViewModel(num_seg_ids=num_seg_ids)

        # image rendered on the UI side
        self.cur_qimg = None
        self.cur_qimg_modified = False
        self.image_loaded = False

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

        # Load image onto UI side
        self.ui.pushButton_loadImage.clicked.connect(self.loadImage)
        # Automatically segment image for the particular seg id chosen  
        self.ui.pushButton_autoSeg.clicked.connect(self.auto_segment_image)
        # This shows cursor location
        self.sliceScene.sigMovePositionL.connect(self.show_pixel_seg_id)
        # Update UI 
        self.ui.checkBox_overlaySegMask.toggled.connect(self.checkBox_overlaySegMask_changed)
        self.ui.spinBox_segId.valueChanged.connect(self.spinBox_segId_changed)
        self.sliceScene.sigMovePositionR.connect(self.paint_slice)

        # Updates the qmask slice that is viewed on UI
        # clear the segTokens
        
        
        
        
        
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

    def loadImage(self):
        # Find image
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

    def auto_segment_image(self):
        if self.image_loaded:
            point_coords, point_labels = self.seg.prompts
            # Outputs 1 x H x W numpy array
            """
            masks = self.seg.predict(point_coords=np.array(point_coords),
                                    point_labels=np.array(point_labels),
                                    multimask_output=False)
            """
            masks = self.seg.predict(point_coords=np.array([[128, 60],]),
                                    point_labels=np.array([0]),
                                    multimask_output=False)[0]
            
            # Update self.imgMask._qmask 
            self.
            self._updateQImage()
        else:
            print("Either model doesn't exist or image doesn't exist!\n")
        self.seg.clear_tokens()
            
    def show_pixel_seg_id(self, point):
        if self.image_loaded and self.imgMask.id_mask_exists:
            x = int(point.x())
            y = int(point.y())   
            height, width = self.imgMask.shape2D  
            if x >= 0 and x < width and \
               y >= 0 and y < height:
                self.ui.label_curPos.setText(f'Pos ({x}, {y})')
                self.ui.label_curSegID.setText(f'Seg ID = {self.imgMask.id_mask[y][x]}') 

    def _updateQImage(self):
            #self.convert_gray_to_seg_color_qimg(slices[slice_num], id_mask[slice_num])
            self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))

    def checkBox_overlaySegMask_changed(self, state):
        if self.image_loaded: self._updateQImage()

    def spinBox_segId_changed(self, segId):
        if self.cur_qimg_modified:
            self.imgMask.update_id_mask()
            self.cur_qimg_modified = False
        if self.image_loaded:
            self.seg.clear_tokens()
            self.imgMask.cur_segId = segId
            self._updateQImage()

    # mask id를 seg color로 map하는 과정이 꽤 느리니 빠른 피드백을 원하는 함수에서 자주 부르지 말것. (ex. paint_slice 함수)
    def convert_gray_to_seg_color_qimg(self, gray_img, id_mask):
        if self.image_loaded:
            h, w = gray_img.shape
            RGB = np.repeat(gray_img[..., np.newaxis], 3, axis=-1) # img (h,w) --> RGB (h,w,3)

            if self.ui.checkBox_overlaySegMask.isChecked():
                # seg id to color
                valid_idx = (id_mask > 0)
                RGB_selected = RGB[valid_idx]
                if RGB_selected.size != 0: # id > 0 인 mask 픽셀 있을때만 블렌딩한다.
                    mask_arr = id_mask[valid_idx]
                    pix_cnt = len(mask_arr)                
                    #seg_colors = np.array(list(map(lambda id: self.seg_palette[id], mask_arr)), dtype=np.uint8)
                    seg_colors = np.array([self.seg_palette[mask_arr[id]] for id in range(pix_cnt)], dtype=np.uint8)
                    RGB[valid_idx] = RGB_selected / 2 +  seg_colors / 2

                # selected blob 은 highlight_color 로 다시 덧칠하자..
                blob_idx = (id_mask == self.selected_blob_id)
                blob_selected = RGB[blob_idx]
                highlight_color = np.array([255, 0, 0], dtype=np.uint8)
                if blob_selected.size != 0:                
                    #RGB[blob_idx] = blob_selected / 4 +  3 * highlight_color / 4
                    RGB[blob_idx] = highlight_color
            
            RGBA = np.zeros((h, w, 4), dtype=np.uint8)
            RGBA[:,:,:3] = RGB
            RGBA[:,:,3] = 255
            self.cur_qimg = QImage(bytes(RGBA), w, h, QImage.Format.Format_RGBA8888)
    
    def mix_pixel_with_seg_color(self, qimg, cur_x, cur_y):#, org_den, seg_id): 
        try:
            seg_color = self.imgMask.seg_palette[self.imgMask.cur_segId]            
            out_pixel = self.imgMask.image[cur_y][cur_x]#np.array([org_den, org_den, org_den], dtype=np.uint8)
            #print(f"Output pixel is in shape: {out_pixel.shape}")
            updated_pixel = (out_pixel / 2) + (seg_color / 2)  
            print(updated_pixel.shape)                   
            mix_color = QColor(updated_pixel[0], updated_pixel[1], updated_pixel[2])
            qimg.setPixelColor(cur_x, cur_y, mix_color)
        except KeyError:
            print(f"seg_id : {self.imgMask.cur_segId} does not exist in the dictionary.")

    def paint_slice(self, point):
        self.cur_qimg_modified = True
        pos_x = int(point.x())
        pos_y = int(point.y())
        brush_size = self.ui.spinBox_brushSize.value()
        for y in range(brush_size):
            for x in range(brush_size):                                
                cur_x = pos_x + x
                cur_y = pos_y + y
                if cur_x >= 0 and cur_x < self.cur_qimg.width() and cur_y >= 0 and cur_y < self.cur_qimg.height(): 
                    self.imgMask.brush_qmask(cur_y, cur_x)#id_mask[cur_num][cur_y][cur_x] = seg_id # update seg id
                    #org_den = self.imgMask[cur_num][cur_y][cur_x]
                    self.mix_pixel_with_seg_color(self.cur_qimg, cur_x, cur_y)#, org_den)
        
        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))  
    """
    
    """
    """
    
    """
    """
    
    """
    """
    

    
    
    """
    
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

    

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Minus:
            value = self.ui.spinBox_brushSize.value() - 1
            if (value >= self.ui.spinBox_brushSize.minimum()):
                self.ui.spinBox_brushSize.setValue(value)
                print(f"brush_size : {value}")
        elif e.key() == Qt.Key_Equal:
            value = self.ui.spinBox_brushSize.value() + 1
            if (value <= self.ui.spinBox_brushSize.maximum()):
                self.ui.spinBox_brushSize.setValue(value)
                print(f"brush_size : {value}")
        elif e.key() == Qt.Key_BracketLeft:
            value = self.ui.spinBox_segId.value() - 1
            if (value >= self.ui.spinBox_segId.minimum()):
                self.ui.spinBox_segId.setValue(value)
                print(f"seg_id : {value}")
        elif e.key() == Qt.Key_BracketRight:
            value = self.ui.spinBox_segId.value() + 1
            if (value <= self.ui.spinBox_segId.maximum()):
                self.ui.spinBox_segId.setValue(value)
                print(f"seg_id : {value}")
        elif e.key() == Qt.Key_Semicolon:
            value = self.ui.slider_sliceNum.value() - 1
            if (value >= self.ui.slider_sliceNum.minimum()):
                self.ui.slider_sliceNum.setValue(value)
                print(f"slider_sliceNum : {value}")
        elif e.key() == Qt.Key_Apostrophe:
            value = self.ui.slider_sliceNum.value() + 1
            if (value <= self.ui.slider_sliceNum.maximum()):
                self.ui.slider_sliceNum.setValue(value)
                print(f"slider_sliceNum : {value}")
        elif e.key() == Qt.Key_Return:
            self.ui.checkBox_overlaySegMask.toggle()
            print(f"Overlay seg mask : {self.ui.checkBox_overlaySegMask.isChecked()}")
        
        
    """
    def resetToFit(self):
        # reset to fit
        if self.cur_qimg is not None:
            self.sliceView.resetTransform()
            self.sliceView.setSceneRect(0, 0, self.cur_qimg.width(), self.cur_qimg.height())
            self.sliceView.fitInView(0, 0, self.cur_qimg.width(), self.cur_qimg.height(), Qt.KeepAspectRatio)
    
    def saveMasks(self):
        print('saveMasks clicked')
