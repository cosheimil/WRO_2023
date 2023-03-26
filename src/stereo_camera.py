import cv2 as cv
import numpy as np

# from matplotlib import pyplot as plt


class PS5_Cam:
    width = 1280
    height = 376
    fps = 120
    _delemiter = width // 2
    video_capture = None

    def __init__(self, *args, **kwargs):
        self.video_capture = cv.VideoCapture(args[0], cv.CAP_V4L)

        self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
        self.video_capture.set(cv.CAP_PROP_FPS, self.fps)
        self.video_capture.set(cv.CAP_PROP_AUTO_WB, 0.0)
        self.set_wb()

    def set_fps(self, fps):
        self.fps = fps
        self.video_capture.set(cv.CAP_PROP_FPS, fps)

    def set_height(self, height):
        self.height = height
        self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, height)

    def set_width(self, width):
        self.width = width
        self._delemiter = width // 2
        self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, width)

    def read_color(self):
        ret, frame = self.video_capture.read()
        video_r, video_l = frame[:, : self._delemiter], frame[:, self._delemiter :]

        return video_l, video_r

    def read_gray(self):
        video_l, video_r = self.read_color()
        video_l = cv.cvtColor(video_l, cv.COLOR_BGR2GRAY)
        video_r = cv.cvtColor(video_r, cv.COLOR_BGR2GRAY)

        return video_l, video_r

    def set_wb(self, temp=5200):
        self.video_capture.set(cv.CAP_PROP_WB_TEMPERATURE, temp)

    def release(self):
        self.video_capture.release()


def main():
    ps_cam = PS5_Cam(2)
    cv.namedWindow("Left")
    # cv.namedWindow('Right')
    cv.createTrackbar("balance", "Left", 2_800, 11_000, lambda x: x)
    # cv.createTrackbar('balance', "Right", 2800, 3700, lambda x: x)
    while True:
        l, r = ps_cam.read_color()
        cv.imshow("Left", l)
        cv.imshow("Right", r)

        ps_cam.set_wb(cv.getTrackbarPos("balance", "Left"))

        # # cv.imshow("Right", video_r)
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    # After the loop release the cap object
    ps_cam.release()
    # Destroy all the windows
    cv.destroyAllWindows()
    return 0


if __name__ == "__main__":
    print(main())
