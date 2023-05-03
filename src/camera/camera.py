import cv2 as cv

class PS5Cam:
    _frame_size = ()
    _delemiter = 0
    _fps = 0

    windows = ["{} camera".format(side) for side in ("Left", "Right")]

    def __init__(self, mode: str, video_capture: int = 2) -> None:
        self.video_capture = cv.VideoCapture(video_capture, cv.CAP_V4L2)
        self.mode = mode

    def set_wb(self, temp=5200):
        self.video_capture.set(cv.CAP_PROP_WB_TEMPERATURE, temp)

    @property
    def get_frame_size(self):
        """Get frame size

        Returns:
            tuple: (width, height)
        """
        return self._frame_size

    @get_frame_size.setter
    def set_frame_size(self, frame_size):
        """Set Frame Size of video capture

        Args:
            frame_size (int): (width, height)
        """
        self._frame_size = frame_size

        self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, self._frame_size[0])
        self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, self._frame_size[1])
        self._delemiter = frame_size[0] // 2

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
            return ValueError("Cannot open video capture")
        return frame

    def get_raw_frame_gray(self):
        """Get glued frame with left and right eyes

        Returns:
            np.array: image
        """
        frame = self.get_raw_frame()
        return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    def get_frames(self):
        """Read color frames from camera.

        Returns
        -------
            frame_l, frame_r: np.array, np.array
        """
        frame = self.get_raw_frame()
        frames = [frame[:, : self._delemiter, :], frame[:, self._delemiter :, :]]
        return frames

    def get_frames_gray(self):
        """Read gray-scaled frames from camera.

        Returns
        -------
            frame_l, frame_r: np.array, np.array
        """
        frame_l, frame_r = self.get_frames()
        if frame_l.ndim == 3:
            frame_l = self.convert_to_grayscale(frame_l)
        if frame_r.ndim == 3:
            frame_r = self.convert_to_grayscale(frame_r)

        return [frame_l, frame_r]

    def show_frames(self, rectify=False, wait=0):
        """
        Show current frames from cameras.

        ``wait`` is the wait interval in milliseconds before the window closes.
        """
        for window, frame in zip(self.windows, self.get_frames(rectify)):
            cv.imshow(window, frame)
        cv.waitKey(wait)

    def show_frames_gray(self, wait=0):
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
    
    def convert_to_grayscale(self, image):
        """Convert image from RGB to GrayScale

        Args:
            image (np.array): any image but in 3 chanells

        Returns:
            iamge (np.array): given image but in gray
        """
        return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

