import cv2 as cv
import numpy as np
# from matplotlib import pyplot as plt


class PS5_Cam():
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
        video_r, video_l = frame[:, :self._delemiter], frame[:, self._delemiter:]

        return video_l, video_r
    

    def read_gray(self):
        video_l, video_r = self.read_color()
        video_l = cv.cvtColor(video_l, cv.COLOR_BGR2GRAY)
        video_r = cv.cvtColor(video_r, cv.COLOR_BGR2GRAY)

        return video_l, video_r


    def release(self):
        self.video_capture.release()

def main():
    ps_cam = PS5_Cam(3)

    while True:
        l, r = ps_cam.read_color()
        cv.imshow("Left", l)
        cv.imshow("Right", r)

        # stereo = cv.StereoBM_create(numDisparities=16, blockSize=5)
        # disparity = stereo.compute(video_l, video_r)
        # plt.imshow(disparity)
        # plt.imshow(video_l)
        # plt.colorbar()
        # plt.show() # test

        # # cv.imshow("Right", video_r)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # After the loop release the cap object
    ps_cam.release()
    # Destroy all the windows
    cv.destroyAllWindows()
    return 0


if __name__ == '__main__':
    print(main())
