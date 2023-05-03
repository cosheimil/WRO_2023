import cv2 as cv

class PS5Cam:
    def __init__(self, mode: str, video_capture: int = 2) -> None:
        self.video_capture = video_capture
        self.mode = mode

    @classmethod
    def set_mode(self):
        ...

    def get_pairs(self):
        """
        Get (left_img, right_img)
        """
        ...
    
    def get_left_eye(self):
        """
        Get left image
        """
        ...
    
    def get_right_eye(self):
        """
        Get right image
        """
        ...
    