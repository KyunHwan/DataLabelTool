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
        point_labels = [1 for i in range(len(self.seg_point_coords))]
        #point_background = [0 for i in range(len(self.background_point_coords))]
        #point_labels = point_labels.extend(point_background)

        
        #point_coords = self.seg_point_coords.extend(self.background_point_coords)
        point_coords = self.seg_point_coords
        return np.array(point_coords), np.array(point_labels)
    
    def set_image(self, image):
        self.model.set_image(image)

    def predict(self, point_coords, point_labels, multimask_output=False):
        masks, _, _ = self.model.predict(point_coords=np.array(point_coords),
                                         point_labels=np.array(point_labels),
                                         multimask_output=multimask_output)
        return masks

    def clear_prompts(self):
        self.seg_point_coords.clear()
        self.background_point_coords.clear()
    
    def add_seg_point(self, point):
        self.seg_point_coords.append(point)

    def remove_seg_point(self):
        if len(self.seg_point_coords) != 0:
            return self.seg_point_coords.pop()
        else:
            return [None, None]

    def add_background_point(self, point):
        self.background_point_coords.append(point)
