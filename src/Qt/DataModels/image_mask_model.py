import numpy as np
from src.utils.download_model_checkpoint import get_filename_from_url
from PIL import Image
import os

class ImageMaskViewModel:
    def __init__(self, num_seg_ids, cur_segId):
        # Original data on the backend
        # Number of segmentation ids (16 for upper/lower respectively)
        self.num_seg_ids = num_seg_ids

        self.seg_palette = {}
        self._generateSegIdPalette()
        self._cur_segId = cur_segId

        # Work on cur_qmask on the UI side and commit so that it can be written into id_mask
        self._id_mask = None # H x W
        self._qmask = None # H x W x C, where C is the number of masks
        
        # Image data. 
        self._image = None # H x W x 3
        self.h = None
        self.w = None
        self.loaded_image_name = None
    
    @property
    def image_exists(self):
        return self._image is not None
    
    @property
    def id_mask_exists(self):
        return self._id_mask is not None
    @property
    def id_mask(self):
        return self._id_mask
    
    @property
    def cur_segId(self):
        return self._cur_segId
    
    @cur_segId.setter
    def cur_segId(self, val):
        self._cur_segId = val

    @property
    def image(self):
        return self._image
    
    @property
    def qmask(self):
        return self._qmask
    
    @property
    def shape2D(self):
        return self.h, self.w
    
    def _generateSegIdPalette(self):
        for i in range(1, self.num_seg_ids+1):
            newColor = np.uint8(np.random.choice(range(256), size=3))
            self.seg_palette[i] = newColor

    def set_empty_masks(self, h, w):
        self._id_mask = np.zeros(shape=(h, w), dtype=np.uint8)
        self._qmask = np.zeros(shape=(h, w), dtype=np.uint8)

    def set_mask(self, mask):
        # image must have been loaded first
        # Mask shape must be available
        mask = np.asarray(mask.convert('L'), dtype=np.uint8)
        print("mask converted to numpy array!")
        print(mask.shape)
        h, w = mask.shape
        height, width = self.shape2D
        if height != h or width != w:
            print("Mask shape (Height & Width) does not equal that of the loaded image!")
        else:
            self._id_mask[:] = 0
            valid_idx = np.logical_and((mask > 0), (mask <= self.num_seg_ids))
            self._id_mask[valid_idx] = mask[valid_idx]
        
    def set_uint8_rgb_imageData(self, image):
        self._image = np.asarray(image.convert('RGB'), dtype=np.uint8) # Loaded image could be RGBA
        self.h, self.w, _ = self._image.shape
    
    def set_uint8_rgb_imageData_empty_masks(self, image):
        self.set_uint8_rgb_imageData(image)
        self.set_empty_masks(h=self._image.shape[0],
                             w=self._image.shape[1])
        
    def zero_out_qmask(self):
        self._qmask[:,:] = 0

    def change_idMask_segId(self, old_id, new_id):
        self._id_mask[(self._id_mask == old_id)] = new_id

    def update_id_mask(self):
        valid_idx = (self._qmask > 0)
        self._id_mask[valid_idx] = self._qmask[valid_idx]

    def brush_qmask(self, y, x, brush_id):
        self._qmask[y][x] = brush_id
    
    def auto_brush_qmask(self, mask):
        self._qmask[mask] = self.cur_segId

    def load_qmask_from_id_mask(self):
        valid_idx = (self._id_mask == self.cur_segId)
        self._qmask[:, :] = 0
        self._qmask[valid_idx] = self.cur_segId
        self._id_mask[valid_idx] = 0

    def get_image_copy(self):
        return self.image.copy()

    def create_qimg_using_qmask(self):
        RGB = self.get_image_copy()
        valid_idx = (self._qmask > 0)
        RGB_selected = RGB[valid_idx]
        if RGB_selected.size != 0: # id > 0 인 mask 픽셀 있을때만 블렌딩한다.
            mask_arr = self._qmask[valid_idx]
            pix_cnt = len(mask_arr)                
            seg_colors = np.array([self.seg_palette[mask_arr[id]] for id in range(pix_cnt)], dtype=np.uint8)
            RGB[valid_idx] = RGB_selected / 2 +  seg_colors / 2
        return RGB, valid_idx
    
    def update_qimg_using_id_mask(self, RGB, mask):
        mask = np.logical_and(mask, (self._id_mask > 0))
        RGB_selected = self.image[mask]
        if RGB_selected.size != 0: # id > 0 인 mask 픽셀 있을때만 블렌딩한다.
            mask_arr = self._id_mask[mask]
            pix_cnt = len(mask_arr)                
            seg_colors = np.array([self.seg_palette[mask_arr[id]] for id in range(pix_cnt)], dtype=np.uint8)
            RGB[mask] = (RGB_selected / 2) +  (seg_colors / 2)

    def qmask_pixel_is_segId(self, x, y):
        return (self._qmask[y][x] == self.cur_segId)

    def loadFileName(self, fileName):
        self.loaded_image_name = get_filename_from_url(fileName)

    def saveMask(self, saveDir):
        # push current qmask to id_mask and save
        valid_idx = (self._qmask > 0)
        self._id_mask[valid_idx] = self._qmask[valid_idx]
        print("id_mask uploaded before saving!")
        mask = Image.fromarray(self._id_mask, mode="L")
        print("mask Image fileoutput from id_mask array")
        
        mask_fileName = os.path.join(saveDir, os.path.splitext(self.loaded_image_name)[0] + '_labels.png')
        print(mask_fileName)
        mask.save(mask_fileName, "PNG")

    def clear_qmask(self):
        self._qmask[:,:] = 0


