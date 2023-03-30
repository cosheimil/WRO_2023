import cv2 as cv


class StereoCam:
    _frame_size = (1280, 376)
    _delemiter = _frame_size[0] // 2
    _fps = 120

    def __init__(self, *args, **kwargs):
        self.video_capture = cv.VideoCapture(args[0], cv.CAP_V4L2)
        self._set_frame_size()
        self.video_capture.set(cv.CAP_PROP_FPS, self._fps)

    @property
    def set_fps(self):
        return self._fps

    @property
    def set_frame_size(self):
        return self._frame_size

    @set_fps.setter
    def set_fps(self, fps):
        self._fps = fps
        self.video_capture.set(cv.CAP_PROP_FPS, self._fps)

    @set_frame_size.setter
    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, self._frame_size[0])
        self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, self._frame_size[1])
        self._delemiter = frame_size[0] // 2
        self._set_frame_size()

    def read_color(self):
        ret, frame = self.video_capture.read()
        video_r, video_l = frame[:, : self._delemiter], frame[:, self._delemiter :]

        return video_l, video_r

    def read_gray(self):
        video_l, video_r = self.read_color()
        video_l = cv.cvtColor(video_l, cv.COLOR_BGR2GRAY)
        video_r = cv.cvtColor(video_r, cv.COLOR_BGR2GRAY)

        return video_l, video_r

    def release(self):
        self.video_capture.release()


class PS5_Cam(StereoCam):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_mode(self, mode: str):
        modes = {"fhd": ((1920, 1080), 30)}

        _mode = modes.get(mode.lower(), "fhd")
        self.set_frame_size(_mode[0])
        self.set_fps(_mode[1])

        if mode == "FHD" or mode == "fhd":
            self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
            self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
            self.set_fps(30)

        elif mode == "HD" or mode == "hd":
            self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
            self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, 800)
            self.set_fps(60)

        elif mode == "2K" or mode == "2k":
            self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 2560)
            self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, 800)
            self.set_fps(60)

        elif mode == "default":
            self.set_frame_size((1280, 376))
            self.set_fps(120)

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
