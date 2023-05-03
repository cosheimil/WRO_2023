import cv2 as cv
import enum
from PIL import Image, ImageEnhance
import numpy as np

class PS5Cam:
    _frame_size = ()
    _delimiter = 0
    _fps = 0

    windows = ["{} camera".format(side) for side in ("Left", "Right")]

    def __init__(self, mode, video_capture: int = 2) -> None:
        """__init__

        Args:
            mode (PS5CameraModes): mode for camera capturing
            video_capture (int, optional): /dev/video*. Defaults to 2.
        """
        self.video_capture = cv.VideoCapture(video_capture, cv.CAP_V4L2)
        self.mode = mode

    def set_wb(self, temp: int = 5200):
        self.video_capture.set(cv.CAP_PROP_WB_TEMPERATURE, temp)

    @property
    def get_frame_size(self):
        """Get frame size

        Returns:
            tuple: (width, height)
        """
        return self._frame_size

    @get_frame_size.setter
    def set_frame_size(self, frame_size: tuple(int, int)):
        """Set Frame Size of video capture

        Args:
            frame_size (int): (width, height)
        """
        self._frame_size = frame_size

        self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, self._frame_size[0])
        self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, self._frame_size[1])
        self._delimiter = frame_size[0] // 2

    @property
    def get_fps(self):
        """Get fps

        Returns:
            int: fraps per second of Video Capture
        """
        return self._fps

    @get_frame_size.setter
    def set_fps(self, fps: int):
        """Set fps rate to camera.

        Args:
        ----
            fps (int): fraps per second
        """
        self._fps = fps
        self.video_capture.set(cv.CAP_PROP_FPS, self._fps)

    @property
    def get_mode(self):
        """Return mode of Video Capture

        Returns:
            ((int, int), int): ((width, height), fps)
        """
        return (self._frame_size, self._fps)

    @get_mode.setter
    def set_mode(self, mode):
        """Set mode of Video Capture

        Args:
            mode (PS5CameraModes): mode of Video Capture by PS5CameraModes
        """
        self.fps = mode[1]
        self.frame_size = mode[0]

    def get_raw_frame(self):
        ret, frame = self.video_capture.read()
        if not ret:
            raise ValueError("Cannot open video capture")
        return frame

    def get_raw_frame_gray(self):
        """Get glued frame with left and right eyes

        Returns:
            np.ndarray: image
        """
        frame = self.get_raw_frame()
        return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    def get_frames(self):
        """Read color frames from camera.

        Returns
        -------
            frame_l, frame_r: np.ndarray, np.ndarray
        """
        frame = self.get_raw_frame()
        frames = [frame[:, : self._delimiter, :], frame[:, self._delimiter :, :]]
        return frames

    def get_frames_gray(self):
        """Read gray-scaled frames from camera.

        Returns
        -------
            frame_l, frame_r: np.ndarray, np.ndarray
        """
        frame_l, frame_r = self.get_frames()
        if frame_l.ndim == 3:
            frame_l = self.convert_to_grayscale(frame_l)
        if frame_r.ndim == 3:
            frame_r = self.convert_to_grayscale(frame_r)

        return [frame_l, frame_r]

    def show_frames(self, wait: int = 0):
        """
        Show current frames from cameras.

        ``wait`` is the wait interval in milliseconds before the window closes.
        """
        for window, frame in zip(self.windows, self.get_frames()):
            cv.imshow(window, frame)
        cv.waitKey(wait)

    def show_frames_gray(self, wait: int = 0):
        """
        Show current frames from cameras.

        ``wait`` is the wait interval in milliseconds before the window closes.
        """
        for window, frame in zip(self.windows, self.get_frames_gray()):
            cv.imshow(window, frame)
        cv.waitKey(wait)

    def show_videos(self):
        """
        Show video
        """
        while True:
            self.show_frames(wait=1)
            if cv.waitKey(1) & 0xFF == ord("q"):
                break

    def convert_to_grayscale(self, image: np.ndarray):
        """Convert image from RGB to GrayScale

        Args:
            image (np.ndarray): any image but in 3 channels

        Returns:
            image (np.ndarray): given image but in gray
        """
        return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    def filter_frame(self, min_: int, max_: int, image:np.ndarray, type_=cv.THRESH_BINARY):
        """Calculate threshold to frame by standard algos

        Args:
            min_ (int): minimum pixel
            max_ (int): maximum pixel
            image (np.ndarray): image
            type_ (filters from cv, optional): Can be:
            - cv.THRESH_BINARY
            - cv.THRESH_BINARY_INV
            - cv.THRESH_TRUNC
            - cv.THRESH_TOZERO
            - cv.THRESH_TOZERO_INV
            - Defaults to cv.THRESH_BINARY.

        Raises:
            ValueError: If cannot calculate thresh

        Returns:
            np.array: image
        """
        image = self.convert_to_grayscale(image)
        ret, thresh = cv.threshold(image, min_, max_, type_)
        if not ret:
            raise ValueError("Cannot calculate threshold. Check types!")
        return thresh

    def filter_frame_adaptive(self, max_: int, image: np.ndarray, type_adaptive=cv.ADAPTIVE_THRESH_MEAN_C, \
                              type_=cv.THRESH_BINARY, block_size=11, c=1):
        """Calculate threshold to frame by standard algos

        Args:
            max_ (int): maximum pixel
            image (np.ndarray): image
            type_ (cv.THRESH_*, optional) Can be:
            - cv.THRESH_BINARY
            - cv.THRESH_BINARY_INV
            - cv.THRESH_TRUNC
            - cv.THRESH_TOZERO
            - cv.THRESH_TOZERO_INV
            - Defaults is cv.THRESH_BINARY.
            type_adaptive(cv.ADAPTIVE_THRESH_*, optional) Can be:
            - cv.ADAPTIVE_THRESH_MEAN_C
            - cv.ADAPTIVE_THRESH_GAUSSIAN_C
            - Defaults is cv.ADAPTIVE_THRESH_MEAN_C

        Raises:
            ValueError: If cannot calculate thresh

        Returns:
            np.array: image
        """
        if block_size % 2 == 0:
            block_size += 1

        image = self.convert_to_grayscale(image)
        thresh = cv.adaptiveThreshold(image, max, type_adaptive, type_, block_size, c)
        return thresh

    def enhance_frame(self, frame: np.ndarray, contrast: float = 1.2):
        """Enhance frame by contrast

        Args:
            frame (np.ndarray): image from one of the eyes
            contrast (float, optional): Contrast constant. Defaults to 1.2.

        Returns:
            frame (np.ndarray): Enhanced frame
        """
        image_pil = Image.fromarray(frame)
        enhanced_image = ImageEnhance.Contrast(image_pil).enhance(contrast)
        enhanced = np.array(enhanced_image)
        return enhanced


class PS5CameraModes(enum.Enum):
    """Supported modes for PS5 camera:
    fhd: ((1920, 1080), 30),
    hd: ((1280, 800), 60),
    2k: ((2560, 800), 60),
    default: ((1280, 376), 120).
    """

    fhd = ((1920, 1080), 30)
    hd = ((1280, 800), 60)
    dci_2k = ((2560, 800), 60)
    default = ((1280, 376), 120)