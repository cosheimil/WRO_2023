import os

import cv2 as cv

from camera_calibration.calibration import ChessboardFinder
from stereo_vision.camera import StereoCam


class CameraChessboardSaver(StereoCam, ChessboardFinder):
    def __init__(self, video_capture, mode, path: str, rows, columns):
        super().__init__(video_capture, mode)
        self.path = f"images/{path}"
        self.rows = rows
        self.columns = columns
        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def show_videos(self):
        c = 9
        while True:
            key = cv.waitKey(1)

            frame = self.get_raw_frame()
            if key == ord("a"):
                # frame = self.get_raw_frame_gray()

                # frames = [frame[:, : self._delemiter], frame[:, self._delemiter :]]

                # cont = False
                # try:
                #     print("Findind corners left...")
                #     self._show_corners(frames[0], window_name="left")
                # except:
                #     print("Havent found left")
                #     cont = True

                # try:
                #     print("Findind corners right...")
                #     self._show_corners(frames[1], window_name="right")
                # except:
                #     print("Havent found right")
                #     cont = True

                # if cont:
                #     continue

                # if cv.waitKey(0) == ord("y"):
                print(f"saved: {c}")
                cv.imwrite(f"{self.path}/raw_image_{c}.png", self.get_raw_frame())
                c += 1

            elif key == ord("q"):
                break
            else:
                cv.imshow("ps5", frame)
