import cv2 as cv


class PS5_Camera(object):
    """
    PS5 Camera class with all functions to see in real world.
    """

    def __init__(self, video_capture: int, mode: str):
        """Init the  PS5 camera.

        Args:
        ----
            video_capture (int): the index of camera in /dev/video*
            mode (int): permitted modes to work with PS5 Cam
        """
        self.video_capture = cv.VideoCapture(video_capture, cv.CAP_V4L2)
        self.mode = mode
        self._valid_modes = PS5_Modes().__dict__.keys()
        # Only for debug!
        self._video_capture_number = video_capture

    @property
    def get_mode(self) -> str:
        """Get the camera mode.

        Returns
        -------
            mode(str): permitted modes to work with PS5 Cam
        """
        return self._mode

    @get_mode.setter
    def set_mode(self, mode: str):
        """Set the camera mode.

        Args:
        ----
            mode(str): permitted modes to work with PS5 Cam
        """
        if mode in self._valid_modes:
            width, height, fps = mode
            cv.self.video_capture.set(cv.CAP_PROP_FPS, fps)
            self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, width)
            self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        else:
            raise ValueError(f"Not permitted mode! Given: {mode}")

    def __str__(self):
        return f"PS5 Camera with settings: Video capture number - {self._video_capture_number}, Mode to see - {self.mode}"


class StereoCamera(PS5_Camera):
    ...


# @dataclass(frozen=True)
class PS5_Modes(object):
    """
    Supported modes for PS5 camera:
    fhd: ((1920, 1080), 30),
    hd: ((1280, 800), 60),
    2k: ((2560, 800), 60),
    default: ((1280, 376), 120).
    """

    def __init__(self):
        self.fhd = ((1920, 1080), 30)
        self.hd = ((1280, 800), 60)
        self.k = ((2560, 800), 60)
        self.default = ((1280, 376), 120)


a = PS5_Camera(2, "fhd")
print(a)
