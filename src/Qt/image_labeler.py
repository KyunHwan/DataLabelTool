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
    
class MainWidget(QWidget):
    def __init__(self, imageSegModel=None):
        super(MainWidget, self).__init__()

        self.model = imageSegModel

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.sliceScene = ZoomGraphicsScene()
        self.sliceItem = QGraphicsPixmapItem()
        self.sliceItem.setTransformationMode(Qt.SmoothTransformation)
        self.sliceScene.addItem(self.sliceItem)        
        self.sliceView = ZoomGraphicsView()
        self.sliceView.setScene(self.sliceScene)
        self.ui.verticalLayout.addWidget(self.sliceView)
        self.ui.pushButton_loadImage.clicked.connect(self.loadImage)  
        self.ui.pushButton_autoSeg.clicked.connect(self.segment_image)
        #self.ui.pushButton_saveMasks.clicked.connect(self.saveMasks)

        #self.sliceScene.sigMovePositionL.connect(self.show_pixel_seg_id)
        #self.sliceScene.sigMovePositionR.connect(self.paint_slice)

        #self.ui.spinBox_segId.valueChanged.connect(self.spinBox_segId_changed)
        #self.ui.checkBox_overlaySegMask.toggled.connect(self.checkBox_overlaySegMask_changed)
        #self.ui.listWidget_segIdPaletteList.itemSelectionChanged.connect(self.listWidget_segIdPaletteList_changed)
        #self.ui.pushButton_updateBlobID.clicked.connect(self.pushButton_updateBlobID_clicked)

        self.id_mask = None
        self.cur_qimg = None
        self.image = None
        #self.selected_blob_id = -1
        #self.generateSegIdPalette()

    def loadImage(self):
        init_path = os.getcwd()
        fileName = QFileDialog.getOpenFileName(self, 'Select file to open', init_path, 'png file(*.png)')[0]
        with Image.open(fileName) as image:
            self.image = np.asarray(image.convert('RGB'), dtype=np.uint8)
        height, width, _ = self.image.shape

        # Load image
        # Create mask data
        # Get the image token from SAM for segmentation processes down the line
        if self.model is not None and self.image is not None: self.model.set_image(self.image)
        self.id_mask = np.zeros(shape=(height, width), dtype=np.uint8)
        self.cur_qimg = QImage(bytes(self.image.data), width, height, width*3, QImage.Format.Format_RGB888)
        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))
        self.resetToFit()

    def segment_image(self):
        if self.model is not None and self.image is not None:
            # Outputs C x H x W numpy array
            masks, _, _ = self.model.predict(point_coords=np.array([[100, 100],[150, 150]]),
                                             point_labels=np.array([1, 0]),
                                             multimask_output=False)
        else:
            print("Either model doesn't exist or image doesn't exist!\n")
        
    """
    def spinBox_segId_changed(self, value): 
        if self.seg_palette.get(value) is None:
            newColor = np.uint8(np.random.choice(range(256), size=3))
            self.seg_palette[value] = newColor
            #print(f'color added = id : {value}, color : {newColor}')

    def generateSegIdPalette(self):
        self.seg_palette = { 0 : np.zeros((3, ), dtype=np.uint8) }
        for i in range(50):
            self.spinBox_segId_changed(i)
            item = QListWidgetItem(f'seg_id : {i}')
            bgColor = QColor(self.seg_palette[i][0], self.seg_palette[i][1], self.seg_palette[i][2])
            item.setBackground( bgColor )
            self.ui.listWidget_segIdPaletteList.insertItem(i, item)

    def listWidget_segIdPaletteList_changed(self):
        self.selected_blob_id = self.ui.listWidget_segIdPaletteList.currentRow()
        self.ui.spinBox_curBlobID.setValue(self.selected_blob_id)
        
        print(f'selected_id = {self.selected_blob_id}')
        self.updateQImageSlice(self.getCurSliceNum())

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
        self.updateQImageSlice(cur_slice_num)

    def checkBox_overlaySegMask_changed(self, state):
        self.updateQImageSlice(self.getCurSliceNum())

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
    """
    # mask id를 seg color로 map하는 과정이 꽤 느리니 빠른 피드백을 원하는 함수에서 자주 부르지 말것. (ex. paint_slice 함수)
    def convert_gray_to_seg_color_qimg(self, gray_img, id_mask):
        h, w = gray_img.shape
        RGB = np.repeat(gray_img[..., np.newaxis], 3, axis=-1) # img (h,w) --> RGB (h,w,3)

        if self.ui.checkBox_overlaySegMask.isChecked():
            # # seg id to color
            # gray_img_py11 = sfmrect.vector_uchar(gray_img.reshape(-1))    
            # id_mask_py11 = sfmrect.vector_uchar(id_mask.reshape(-1))
            # out_flattened = np.uint8(sfmrect.blendSegColorToImage(gray_img_py11, id_mask_py11, w, h, self.seg_palette))
            # RGB = out_flattened.reshape(h, w, 3)

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
        qimg = QImage(bytes(RGBA), w, h, QImage.Format.Format_RGBA8888)
        return qimg
    
    def mix_pixel_with_seg_color(self, qimg, cur_x, cur_y, org_den, seg_id): 
        try:
            seg_color = self.seg_palette[seg_id]            
            out_pixel = np.array([org_den, org_den, org_den], dtype=np.uint8)
            if seg_id > 0: # seg_id > 0 일때만 블렌딩한다.
                out_pixel = out_pixel / 2 + seg_color / 2                     
            mix_color = QColor(out_pixel[0], out_pixel[1], out_pixel[2])
            qimg.setPixelColor(cur_x, cur_y, mix_color)
        except KeyError:
            print(f"seg_id : {seg_id} does not exist in the dictionary.")

    def show_pixel_seg_id(self, point):
        if self.id_mask is not None:
            x = int(point.x())
            y = int(point.y())     
            id_mask = self.getIdMasks()
            cur_num = self.getCurSliceNum()
            if x >= 0 and x < id_mask.shape[2] and y >= 0 and y < id_mask.shape[1]:
                self.ui.label_curPos.setText(f'Pos ({x}, {y})')
                self.ui.label_curSegID.setText(f'Seg ID = {id_mask[cur_num][y][x]}')
    
    def paint_slice(self, point):
        pos_x = int(point.x())
        pos_y = int(point.y())
        #print(f'point = {pos_x}, {pos_y}')
        slices = self.getSlices()
        id_mask = self.getIdMasks()
        cur_num = self.getCurSliceNum()
        brush_size = self.ui.spinBox_brushSize.value()
        seg_id = self.ui.spinBox_segId.value()
        for y in range(brush_size):
            for x in range(brush_size):                                
                cur_x = pos_x + x
                cur_y = pos_y + y
                if cur_x >= 0 and cur_x < self.cur_qimg.width() and cur_y >= 0 and cur_y < self.cur_qimg.height(): 
                    id_mask[cur_num][cur_y][cur_x] = seg_id # update seg id
                    org_den = slices[cur_num][cur_y][cur_x]
                    self.mix_pixel_with_seg_color(self.cur_qimg, cur_x, cur_y, org_den, seg_id)
        
        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))        
    
    def getIdMasks(self):

    def updateQImageSlice(self, slice_num):             
        slices = self.getSlices()
        id_mask = self.getIdMasks()
        print(f'slices.shape = {slices.shape}')

        self.cur_qimg = self.convert_gray_to_seg_color_qimg(slices[slice_num], id_mask[slice_num])
        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))
    """
    def resetToFit(self):
        # reset to fit
        if self.cur_qimg is not None:
            self.sliceView.resetTransform()
            self.sliceView.setSceneRect(0, 0, self.cur_qimg.width(), self.cur_qimg.height())
            self.sliceView.fitInView(0, 0, self.cur_qimg.width(), self.cur_qimg.height(), Qt.KeepAspectRatio)
    
    def saveMasks(self):
        print('saveMasks clicked')
