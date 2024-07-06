import numpy as np

class SegmentationViewModel:
    def __init__(self, segmentation_model=None):
        self.model = segmentation_model
        self.seg_point_coords = []
        self.background_point_coords = []

    @property
    def model_exists(self):
        return self.model is not None
    
    @property
    def prompts(self):
        """ 
        This is for SAM model, specifically point coords token
        """
        point_background = [0 for i in range(len(self.background_point_coords))]
        point_label = [1 for i in range(len(self.seg_point_coords))]
        point_labels = point_label.extend(point_background)
        point_coords = self.background_point_coords.extend(self.background_point_coords)
        return point_labels, point_coords
    
    def set_image(self, image):
        self.model.set_image(image)

    def predict(self, point_coords, point_labels, multimask_output=False):
        masks, _, _ = self.model.predict(point_coords=np.array(point_coords),
                                         point_labels=np.array(point_labels),
                                         multimask_output=False)
        return masks

    def clear_tokens(self):
        self.seg_point_coords.clear()
        self.background_point_coords.clear()
    
    def manage_seg_point(self, point):
        # add background or labels
        self.seg_point_coords.append(point)
    
    def manage_background_points(self, point):
        self.background_point_coords.append(point)
