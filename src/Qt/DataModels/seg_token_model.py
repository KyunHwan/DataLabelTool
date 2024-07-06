class SegmentationTokenModel:
    def __init__(self):
        self.seg_point_coords = []
        self.background_point_coords = []

    def clear(self):
        self.seg_point_coords.clear()
        self.background_point_coords.clear()
    
    def add_seg_point(self, point):
        self.seg_point_coords.append(point)
    
    def add_background_point(self, point):
        self.background_point_coords.append(point)

    def get_seg_tokens(self):
        """ 
        This is for SAM model, specifically point coords token
        """
        point_background = [0 for i in range(len(self.background_point_coords))]
        point_label = [1 for i in range(len(self.seg_point_coords))]
        point_labels = point_label.extend(point_background)
        point_coords = self.background_point_coords.extend(self.background_point_coords)
        return point_labels, point_coords