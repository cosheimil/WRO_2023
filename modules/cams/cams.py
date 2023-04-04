import cv2 as cv
import numpy as np  # For typing


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
            mode (str): permitted modes to work with PS5 Cam
        """
        return self._mode

    @get_mode.setter
    def set_mode(self, mode: str):
        """Set the camera mode.

        Args:
        ----
            mode (str): _description_

        Raises:
        ------
            ValueError: _description_
        """
        if mode in self._valid_modes:
            width, height, fps = mode
            cv.self.video_capture.set(cv.CAP_PROP_FPS, fps)
            self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, width)
            self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        else:
            raise ValueError(f"Not permitted mode! Given: {mode}")

    def get_frame(self) -> np.ndarray:
        """Get colored frame from PS5 Camera.

        Raises
        ------
            ValueError: Error while reading frame. Incorrect Camera Index

        Returns
        -------
            np.ndarray: image in BGR
        """
        ret, frame = self.video_capture.read()
        if ret:
            return frame
        else:
            raise ValueError(
                f"Not opened camera! Given: {self._video_capture_number}, please verify correct camera number"
            )

    def get_frame_gray(self) -> np.ndarray:
        """Get gray frame from PS5 Camera.

        Raises
        ------
            ValueError: Error while reading frame. Incorrect Camera Index

        Returns
        -------
            np.ndarray: image in gray
        """
        try:
            frame_colored = self.get_frame()
            frame_grayed = cv.cvtColor(frame_colored, cv.COLOR_BGR2GRAY)
            return frame_grayed
        except:
            raise ValueError(
                f"Not opened camera! Given: {self._video_capture_number}, please verify correct camera number"
            )

    def view_frame(self):
        """View colored frame from PS5 Cam.

        Raises
        ------
            ValueError: Error while reading frame. Incorrect Camera Index
        """
        try:
            frame_colored = self.get_frame()
            cv.imshow("PS5 Colored", frame_colored)
        except:
            raise ValueError(
                f"Not opened camera! Given: {self._video_capture_number}, please verify correct camera number"
            )

    def view_frame_gray(self):
        """Get gray frame from PS5 Camera.

        Raises
        ------
            ValueError: Error while reading frame. Incorrect Camera Index
        """
        try:
            frame_gray = self.get_frame_gray()
            cv.imshow("PS5 Gray", frame_gray)
        except:
            raise ValueError(
                f"Not opened camera! Given: {self._video_capture_number}, please verify correct camera number"
            )

    def view_video(self):
        """Get colored video from PS5 Camera.

        Raises
        ------
            ValueError: Error while reading frame. Incorrect Camera Index
        """
        try:
            frame_colored = self.view_frame()
        except:
            ValueError(
                f"Not opened camera! Given: {self._video_capture_number}, please verify correct camera number"
            )

        while True and frame_colored:
            frame_colored = self.view_frame()
            cv.imshow("PS5 Colored", frame_colored)
            cv.waitKey(10)
            if cv.waitKey(0) & 0xFF == ord("q"):
                break
        self.realese_camera()

    def view_video_gray(self):
        """Get gray video from PS5 Camera.

        Raises
        ------
            ValueError: Error while reading frame. Incorrect Camera Index
        """
        try:
            frame_gray = self.view_frame_gray()
        except:
            ValueError(
                f"Not opened camera! Given: {self._video_capture_number}, please verify correct camera number"
            )

        while True and frame_gray:
            frame_gray = self.view_frame_gray()
            cv.imshow("PS5 Colored", frame_gray)
            cv.waitKey(10)
            if cv.waitKey(0) & 0xFF == ord("q"):
                break
        self.realese_camera()

    def realese_camera(self):
        self.video_capture.release()

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
