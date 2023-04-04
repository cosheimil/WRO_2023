import cv2 as cv

from camera_calibration.calibration import ChessboardFinder
from stereo_vision.camera import StereoCam


class CameraChessboardSaver(StereoCam, ChessboardFinder):
    def __init__(self, video_capture, mode, path: str):
        super().__init__(video_capture, mode)
        self.path = path

    def show_frames(self, rectify=False, wait=0):
        left, right = self.get_frames()
        ret = True
        try:
            self._show_corners(left, "left")
        except:
            cv.imshow("left", left)
            ret = False
        try:
            self._show_corners(right, "right")
        except:
            cv.imshow("right", right)
            ret = False

        cv.waitKey(wait)
        for window in self.windows:
            cv.destroyWindow(window)
        return ret

    def show_videos(self):
        c = 0
        while True:
            ret = self.show_frames(wait=1)
            if cv.waitKey(1) == ord("a") and ret:
                cv.imwrite(f"{c}", self.get_raw_frame())
                c += 1
            elif cv.waitKey(1) == ord("q"):
                break
