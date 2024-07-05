import os

import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QGraphicsPixmapItem, QListWidgetItem, QGraphicsLineItem
from PySide6.QtGui import QPen, QColor, QPixmap, QImage
from PySide6.QtCore import QT_TR_NOOP_UTF8
from .ui_segmentation_refine_form import Ui_Form
from .zoom_graphics_scene import *
from .zoom_graphics_view import *

#import qimage2ndarray # https://hmeine.github.io/qimage2ndarray/
import glob
from PIL import Image
#import sfmrect
    
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
        self.ui.pushButton_loadSlices.clicked.connect(self.loadSlices)  
        self.ui.pushButton_saveMasks.clicked.connect(self.saveMasks)
        self.ui.spinBox_sliceNum.valueChanged.connect(self.spinBox_sliceNum_changed)
        self.ui.slider_sliceNum.valueChanged.connect(self.slider_sliceNum_changed)  
        self.ui.radioButton_xDir.clicked.connect(self.sliceDirRadioBtn_clicked)
        self.ui.radioButton_yDir.clicked.connect(self.sliceDirRadioBtn_clicked)
        self.ui.radioButton_zDir.clicked.connect(self.sliceDirRadioBtn_clicked)
        self.sliceScene.sigMovePositionL.connect(self.show_pixel_seg_id)
        self.sliceScene.sigMovePositionR.connect(self.paint_slice)
        #self.sliceScene.sigReleasePosition.connect(self.updateCurrentSlice)
        self.ui.spinBox_segId.valueChanged.connect(self.spinBox_segId_changed)
        self.ui.checkBox_overlaySegMask.toggled.connect(self.checkBox_overlaySegMask_changed)
        self.ui.listWidget_segIdPaletteList.itemSelectionChanged.connect(self.listWidget_segIdPaletteList_changed)
        self.ui.checkBox_showAxis.toggled.connect(self.checkBox_showAxis_changed)        
        self.ui.pushButton_updateBlobID.clicked.connect(self.pushButton_updateBlobID_clicked)

        self.slices = None
        self.id_masks = None
        self.cur_qimg = None
        self.slice_dir = 0 # default zDir
        self.cur_slice_num_x = 0
        self.cur_slice_num_y = 0
        self.cur_slice_num_z = 0
        self.selected_blob_id = -1
        self.generateSegIdPalette()

        self.ui.radioButton_xDir.setStyleSheet('Color : red')
        self.ui.radioButton_yDir.setStyleSheet('Color : green')
        self.ui.radioButton_zDir.setStyleSheet('Color : cyan')
        self.line1 = QGraphicsLineItem()
        self.line2 = QGraphicsLineItem()        
        self.sliceScene.addItem(self.line1)
        self.sliceScene.addItem(self.line2)

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

    def checkBox_showAxis_changed(self, state):
        self.line1.setVisible(state)
        self.line2.setVisible(state)

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
        if self.id_masks is not None:
            x = int(point.x())
            y = int(point.y())     
            id_masks = self.getIdMasks()
            cur_num = self.getCurSliceNum()
            if x >= 0 and x < id_masks.shape[2] and y >= 0 and y < id_masks.shape[1]:
                self.ui.label_curPos.setText(f'Pos ({x}, {y})')
                self.ui.label_curSegID.setText(f'Seg ID = {id_masks[cur_num][y][x]}')

    def paint_slice(self, point):
        pos_x = int(point.x())
        pos_y = int(point.y())
        #print(f'point = {pos_x}, {pos_y}')
        slices = self.getSlices()
        id_masks = self.getIdMasks()
        cur_num = self.getCurSliceNum()
        brush_size = self.ui.spinBox_brushSize.value()
        seg_id = self.ui.spinBox_segId.value()
        for y in range(brush_size):
            for x in range(brush_size):                                
                cur_x = pos_x + x
                cur_y = pos_y + y
                if cur_x >= 0 and cur_x < self.cur_qimg.width() and cur_y >= 0 and cur_y < self.cur_qimg.height(): 
                    id_masks[cur_num][cur_y][cur_x] = seg_id # update seg id
                    org_den = slices[cur_num][cur_y][cur_x]
                    self.mix_pixel_with_seg_color(self.cur_qimg, cur_x, cur_y, org_den, seg_id)
        
        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))        

    def spinBox_sliceNum_changed(self, value):
        self.ui.slider_sliceNum.blockSignals(True)
        self.ui.slider_sliceNum.setValue(value)
        self.setCurSliceNum(value)
        self.ui.slider_sliceNum.blockSignals(False)    

        self.updateQImageSlice(value)

    def slider_sliceNum_changed(self, value):     
        self.ui.spinBox_sliceNum.blockSignals(True)        
        self.ui.spinBox_sliceNum.setValue(value)
        self.setCurSliceNum(value)
        self.ui.spinBox_sliceNum.blockSignals(False)

        self.updateQImageSlice(value)

    def updateAxisLines(self):
        penRed = QPen(QColor(255,0,0,80))
        penGreen = QPen(QColor(0,255,0,80))
        penBlue = QPen(QColor(0,0,255,80))    
        if self.slice_dir == 0: # along Z (blue plane)
            self.line1.setPen(penRed)
            line1_x = self.cur_slice_num_x
            self.line1.setLine(line1_x, 0, line1_x, self.slices.shape[1]-1)
            self.line2.setPen(penGreen)
            line2_y = self.cur_slice_num_y
            self.line2.setLine(0, line2_y, self.slices.shape[2]-1, line2_y)
        elif self.slice_dir == 1: # along Y (green plane)
            self.line1.setPen(penRed)
            line1_x = self.cur_slice_num_x
            self.line1.setLine(line1_x, 0, line1_x, self.slices.shape[0]-1)
            self.line2.setPen(penBlue)
            line2_y = self.cur_slice_num_z
            self.line2.setLine(0, line2_y, self.slices.shape[2]-1, line2_y)
        elif self.slice_dir == 2: # along X (red plane)
            self.line1.setPen(penGreen)
            line1_x = self.cur_slice_num_y
            self.line1.setLine(line1_x, 0, line1_x, self.slices.shape[0]-1)
            self.line2.setPen(penBlue)
            line2_y = self.cur_slice_num_z
            self.line2.setLine(0, line2_y, self.slices.shape[1]-1, line2_y)
        
    def sliceDirRadioBtn_clicked(self):   
        if self.ui.radioButton_zDir.isChecked():
            self.slice_dir = 0
        elif self.ui.radioButton_yDir.isChecked():
            self.slice_dir = 1
        elif self.ui.radioButton_xDir.isChecked():
            self.slice_dir = 2

        if self.slices is not None:
            cur_slice_num = self.getCurSliceNum()
            max_slice_num = self.slices.shape[self.slice_dir] - 1
            print(f'slice_dir = {self.slice_dir}, cur_slice_num = {cur_slice_num}')            
            self.updateAxisLines()
            self.updateSliceUI(cur_slice_num, max_slice_num)

    def setCurSliceNum(self, cur_num):
        if self.slice_dir == 0: # along Z
            self.cur_slice_num_z = cur_num
        elif self.slice_dir == 1: # along Y
            self.cur_slice_num_y = cur_num
        elif self.slice_dir == 2: # along X
            self.cur_slice_num_x = cur_num

    def getCurSliceNum(self):
        cur_num = 0
        if self.slice_dir == 0: # along Z
            cur_num = self.cur_slice_num_z
        elif self.slice_dir == 1: # along Y
            cur_num = self.cur_slice_num_y
        elif self.slice_dir == 2: # along X
            cur_num = self.cur_slice_num_x
        return cur_num

    def getSlices(self):
        if self.slice_dir == 0: # along Z
            slices = self.slices # no transpose
        elif self.slice_dir == 1: # along Y
            slices = self.slices.transpose(1, 0, 2)
        elif self.slice_dir == 2: # along X
            slices = self.slices.transpose(2, 0, 1)                
        return slices
    
    def getIdMasks(self):
        if self.slice_dir == 0: # along Z
            id_masks = self.id_masks # no transpose
        elif self.slice_dir == 1: # along Y
            id_masks = self.id_masks.transpose(1, 0, 2)
        elif self.slice_dir == 2: # along X
            id_masks = self.id_masks.transpose(2, 0, 1)                
        return id_masks

    def updateQImageSlice(self, slice_num):             
        slices = self.getSlices()
        id_masks = self.getIdMasks()
        print(f'slices.shape = {slices.shape}')

        self.cur_qimg = self.convert_gray_to_seg_color_qimg(slices[slice_num], id_masks[slice_num])
        self.sliceItem.setPixmap(QPixmap.fromImage(self.cur_qimg))

    def resetToFit(self):
        # reset to fit
        if self.cur_qimg is not None:
            self.sliceView.resetTransform()
            self.sliceView.setSceneRect(0, 0, self.cur_qimg.width(), self.cur_qimg.height())
            self.sliceView.fitInView(0, 0, self.cur_qimg.width(), self.cur_qimg.height(), Qt.KeepAspectRatio)

    def updateSliceUI(self, cur_val, max_val):
        self.ui.spinBox_sliceNum.blockSignals(True)
        self.ui.spinBox_sliceNum.setMaximum(max_val)
        self.ui.spinBox_sliceNum.setValue(cur_val) 
        self.ui.spinBox_sliceNum.blockSignals(False)
        self.ui.slider_sliceNum.blockSignals(True)
        self.ui.slider_sliceNum.setMaximum(max_val)
        self.ui.slider_sliceNum.setValue(cur_val) 
        self.ui.slider_sliceNum.blockSignals(False)
        # qimg update
        self.updateQImageSlice(cur_val)

        self.resetToFit()

    def loadSlices(self):
        # https://blog.naver.com/reto1210/223057895936

        data_folder = './ToothFairy2F_001_0000'

        img_list = sorted(glob.glob(data_folder + '/*.jpg') + glob.glob(data_folder + '/*.png'))
        img_cnt = len(img_list)
        if img_cnt == 0:
            return                               

        for i, cur_path in enumerate(img_list):    
            gray_img = cv2.imread(cur_path, cv2.IMREAD_GRAYSCALE)         

            mask_path = data_folder + '_masks/' + os.path.basename(cur_path).replace('.jpg', '.png')
            #mask_path2 = data_folder + '_masks2/' + os.path.basename(cur_path).replace('.jpg', '.png')

            # https://stackoverflow.com/questions/61952256/why-does-reading-image-with-cv2-has-different-behavior-from-pil
            # openCV 는 png 팔레트 정보 제대로 못읽는듯. pillow 로 open 하면 팔레트 안먹인 org seg id 값으로 읽어온다.            
            mask_img = Image.open(mask_path) # Image.open(mask_path).convert('P')
            mask_img = np.array(mask_img)

            #cv2.imwrite(mask_path2, mask_img) # 팔레트 적용안된 상태로 다시 저장하자..

            if i == 0: # 속도를 위해 첫 이미지 로딩때 전체 볼륨 공간 할당해 놓자.
                self.slices = np.zeros((img_cnt, gray_img.shape[0], gray_img.shape[1]), dtype=np.uint8)
                self.id_masks = np.zeros((img_cnt, gray_img.shape[0], gray_img.shape[1]), dtype=np.uint8)
            
            self.slices[i] = gray_img                           
            print('image read = ', cur_path)

            if mask_img.size != 0:
                self.id_masks[i] = mask_img                           
                print('mask read = ', mask_path)
        
        # 초기값은 각 축방향 슬라이스 중간값으로.
        self.cur_slice_num_x = int(self.slices.shape[2] / 2)
        self.cur_slice_num_y = int(self.slices.shape[1] / 2)
        self.cur_slice_num_z = int(self.slices.shape[0] / 2)

        #print('self.slices.shape = ', self.slices.shape)
        print(f'np.unique(self.id_mask) = {np.unique(self.id_masks)}')

        # set ui values
        self.ui.radioButton_zDir.setChecked(True)
        self.sliceDirRadioBtn_clicked() # radiobtn clicked 에 slot 연결해놔서 이거 따로 호출필요.

    def saveMasks(self):
        print('saveMasks clicked')

