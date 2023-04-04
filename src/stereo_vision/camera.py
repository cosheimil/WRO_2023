import enum
from glob import glob
from itertools import cycle
from pathlib import Path

import cv2 as cv

from camera_calibration.calibration import *
from point_cloud.point_cloud import PointCloud


class StereoCam:
    _frame_size = ()
    _delemiter = 0
    _fps = 0
    calibration = None
    block_matcher = None

    windows = ["{} camera".format(side) for side in ("Left", "Right")]

    def __init__(self, video_capture, mode, calibration=None, block_matcher=None):
        self.video_capture = cv.VideoCapture(video_capture, cv.CAP_V4L2)
        self.mode = mode

        self.calibration = calibration
        self.block_matcher = block_matcher

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.video_capture.release()

        for window in self.windows:
            cv.destroyWindow(window)

    @property
    def fps(self):
        return self._fps

    @property
    def frame_size(self):
        return self._frame_size

    @fps.setter
    def fps(self, fps: int):
        """Set fps rate to camera.

        Args:
        ----
            fps (int): fraps per second
        """
        self._fps = fps
        self.video_capture.set(cv.CAP_PROP_FPS, self._fps)

    @frame_size.setter
    def frame_size(self, frame_size):
        """Set width, height to video.

        Args:
        ----
            frame_size ((int, int)): width, height
        """
        self._frame_size = frame_size

        self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, self._frame_size[0])
        self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, self._frame_size[1])
        self._delemiter = frame_size[0] // 2

    @property
    def mode(self):
        return (self._frame_size, self._fps)

    @mode.setter
    def mode(self, mode):
        self.fps = mode[1]
        self.frame_size = mode[0]

    def get_raw_frame(self):
        ret, frame = self.video_capture.read()
        return frame

    def get_frames(self, rectify=False):
        """Read color frames from camera.

        Returns
        -------
            frame_l, frame_r: np.array, np.array
        """
        ret, frame = self.video_capture.read()
        frames = [frame[:, : self._delemiter, :], frame[:, self._delemiter :, :]]

        if rectify and self.calibration is not None:
            frames = self.calibration.rectify(frames)
        return frames

    def get_frames_gray(self, rectify=False):
        """Read gray-scaled frames from camera.

        Returns
        -------
            frame_l, frame_r: np.array, np.array
        """
        frame_l, frame_r = self.get_frames(rectify)
        if frame_l.ndim == 3:
            frame_l = cv.cvtColor(frame_l, cv.COLOR_BGR2GRAY)
        if frame_r.ndim == 3:
            frame_r = cv.cvtColor(frame_r, cv.COLOR_BGR2GRAY)

        return [frame_l, frame_r]

    def show_frames(self, rectify=False, wait=0):
        """
        Show current frames from cameras.

        ``wait`` is the wait interval in milliseconds before the window closes.
        """
        for window, frame in zip(self.windows, self.get_frames(rectify)):
            cv.imshow(window, frame)
        cv.waitKey(wait)
        for window in self.windows:
            cv.destroyWindow(window)

    def show_videos(self):
        """Show video from cameras."""
        while True:
            self.show_frames(wait=1)
            if cv.waitKey(1) & 0xFF == ord("q"):
                break

    def set_wb(self, temp=5200):
        self.video_capture.set(cv.CAP_PROP_WB_TEMPERATURE, temp)

    def get_point_cloud(self, pair):
        """Get 3D point cloud from image pair."""
        if self.block_matcher is None:
            return

        disparity = self.block_matcher.get_disparity(pair)
        points = self.block_matcher.get_3d(
            disparity, self.calibration.disp_to_depth_mat
        )
        colors = cv.cvtColor(pair[0], cv.COLOR_BGR2RGB)
        return PointCloud(points, colors)


class File_Cam(StereoCam):
    img_names = []
    img_pointer = 0

    def __init__(
        self, dir_path, img_format="jpg", calibration=None, block_matcher=None
    ):
        self.img_names = sorted(glob(f"{dir_path}/*.{img_format}"))

        frame_sizes = [cv.imread(img_name).shape[:2] for img_name in self.img_names]

        assert not frame_sizes or frame_sizes.count(frame_sizes[0]) == len(frame_sizes)

        self.frame_size = frame_sizes[0]

        self.calibration = calibration
        self.block_matcher = block_matcher

    @property
    def img_pointer(self):
        return self.img_pointer

    @img_pointer.setter
    def img_pointer(self, value):
        self.img_pointer = (value) % len(self.img_names)

    def get_raw_frame(self):
        frame = cv.imread(self.img_names[self.img_pointer])
        return frame

    def get_frames(self, rectify=False):
        frame = cv.imread(self.img_names[self.img_pointer])
        frames = list(frame[:, : self._delemiter, :], frame[:, self._delemiter :, :])

        if rectify and self.calibration is not None:
            frames = self.calibration.rectify(frames)

        return frames

    def calibrateSingle(self, side, chess_pattern, dir_name, show_results=False):
        calibrator = CameraCalibrator(
            rows=chess_pattern[0],
            columns=chess_pattern[1],
            square_size=chess_pattern[2],
            image_size=self.frame_size,
        )

        for i in range(len(self.img_names)):
            frame = None
            self.img_pointer = i
            if side == "left":
                frame = self.get_frames_gray()[0]
            elif side == "right":
                frame = self.get_frames_gray()[1]

            try:
                calibrator.add_corners(frame, show_results)
            except ChessboardNotFoundError:
                print(f"{i}: {self.img_names[i]} - can not find board!")
                self.show_frames()
            else:
                print(f"{i}: {self.img_names[i]} - have found board!")

        calibration = calibrator.calibrate_camera()
        avg_error = self.calibration.rmse

        # TODO: Нормально передавать папку для конфига, как параметр целиком
        calibration.export(Path(__file__).parent.parent / f"./config/{dir_name}")
        return avg_error, calibration

    def calibrateStereo(self, chess_pattern, dir_name, show_results=False):
        calibrator = StereoCalibrator(
            rows=chess_pattern[0],
            columns=chess_pattern[1],
            square_size=chess_pattern[2],
            image_size=self.frame_size,
        )

        for i in range(len(self.left_images)):
            try:
                calibrator.add_corners(self.get_frames_gray(), show_results)
            except ChessboardNotFoundError:
                print(f"{i}: {self.left_images[i]} - can not find board!")
                self.show_frames()
            else:
                print(f"{i}: {self.left_images[i]} - have found board!")

        self.calibration = calibrator.calibrate_cameras()
        avg_error = calibrator.check_calibration(self.calibration)

        # TODO: Нормально передавать папку для конфига, как параметр целиком
        self.calibration.export(Path(__file__).parent.parent / f"./config/{dir_name}")
        return avg_error


class PS5CameraModes(enum.Enum):
    """Supported modes for PS5 camera:
    fhd: ((1920, 1080), 30),
    hd: ((1280, 800), 60),
    2k: ((2560, 800), 60),
    default: ((1280, 376), 120)
    """

    fhd = ((1920, 1080), 30)
    hd = ((1280, 800), 60)
    dci_2k = ((2560, 800), 60)
    default = ((1280, 376), 120)


class WebCameraModes(enum.Enum):
    """Supported modes for Thinkpad x230t integrated camera
    default: ((640, 480), 30)
    """

    default = ((640, 480), 30)
