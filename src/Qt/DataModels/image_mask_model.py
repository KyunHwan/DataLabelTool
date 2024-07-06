class ImageMaskModel:
    def __init__(self):
        # Original data on the backend
        self.id_mask = None # C x H x W
        self.image = None # 3 x H x W
        
        # Data to be seen on the UI side. 
        # Work on cur_qmask on the UI side and commit so that it can be written into id_mask
        self.cur_qmask = None # C x H x W, where C is the number of masks
        self.cur_qimg = None # 3 x H x W