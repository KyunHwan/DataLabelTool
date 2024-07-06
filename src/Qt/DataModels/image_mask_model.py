import numpy as np

class ImageMaskViewModel:
    def __init__(self, num_seg_ids):
        # Original data on the backend
        # Number of segmentation ids (16 for upper/lower respectively)
        self.num_seg_ids = num_seg_ids

        self.seg_palette = {}
        self._generateSegIdPalette()
        self._cur_segId = 1

        # Work on cur_qmask on the UI side and commit so that it can be written into id_mask
        self._id_mask = None # H x W
        self._qmask = None # H x W x C, where C is the number of masks
        
        # Image data. 
        self._image = None # H x W x 3
        self.h = None
        self.w = None
    
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
    def shape2D(self):
        return self.h, self.w

    @property
    def qmask_slice(self):
        return self.cur_segId - 1
    
    def _generateSegIdPalette(self):
        for i in range(1, self.num_seg_ids+1):
            newColor = np.uint8(np.random.choice(range(256), size=3))
            self.seg_palette[i] = newColor

    def set_empty_masks(self, h, w):
        self._id_mask = np.zeros(shape=(h, w), dtype=np.uint8)
        self._qmask = np.zeros(shape=(h, w, self.num_seg_ids), dtype=np.uint8)
    
    def set_uint8_rgb_imageData(self, image):
        self._image = np.asarray(image.convert('RGB'), dtype=np.uint8) # Loaded image could be RGBA
        self.h, self.w, _ = self._image.shape
        print(self._image.shape)
    
    def set_uint8_rgb_imageData_empty_masks(self, image):
        self.set_uint8_rgb_imageData(image)
        self.set_empty_masks(h=self._image.shape[0],
                             w=self._image.shape[1])
        
    def update_id_mask(self):
        valid_idx = (self._qmask[:, :, self._cur_segId] > 0)
        self._id_mask[valid_idx] = self._qmask[:, :, self._cur_segId][valid_idx]

    def brush_qmask(self, y, x):
        self._qmask[y][x][self.qmask_slice] = self.cur_segId