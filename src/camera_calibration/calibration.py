import os

import cv2 as cv
import numpy as np


class ChessboardFinder(object):
    rows, columns = 0, 0
    # criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    def _get_corners(self, image):
        """Find subpixel chessboard corners in image."""
        temp = image

        if image.ndim == 3:
            temp = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        ret, corners = cv.findChessboardCorners(temp, (self.rows, self.columns))
        if not ret:
            raise ChessboardNotFoundError("No chessboard could be found.")

        cv.cornerSubPix(temp, corners, (11, 11), (-1, -1), self.criteria)
        return corners

    def _show_corners(self, image, window_name="Chessboard"):
        """Show chessboard corners found in image."""
        temp = image
        
        corners = self._get_corners(image)
        cv.drawChessboardCorners(temp, (self.rows, self.columns), corners, True)
        cv.imshow(window_name, temp)
        if cv.waitKey(0):
            cv.destroyWindow(window_name)


class Calibration(object):
    def __str__(self):
        output = ""
        for key, item in self.__dict__.items():
            output += key + ":\n"
            output += str(item) + "\n"
        return output

    def _copy_calibration(self, calibration):
        """Copy another ``StereoCalibration`` object's values."""
        for key, item in calibration.__dict__.items():
            self.__dict__[key] = item

    def _interact_with_folder(self, output_folder, action):
        """
        Export/import matrices as *.npy files to/from an output folder.
        ``action`` is a string. It determines whether the method reads or writes
        to disk. It must have one of the following values: ('r', 'w').
        """
        if action not in ("r", "w"):
            raise ValueError("action must be either 'r' or 'w'.")
        for key, item in self.__dict__.items():
            if isinstance(item, dict):
                for side in ("left", "right"):
                    filename = os.path.join(
                        output_folder, "{}_{}.npy".format(key, side)
                    )
                    if action == "w":
                        np.save(filename, self.__dict__[key][side])
                    else:
                        self.__dict__[key][side] = np.load(filename)
            else:
                filename = os.path.join(output_folder, "{}.npy".format(key))
                if action == "w":
                    np.save(filename, self.__dict__[key])
                else:
                    self.__dict__[key] = np.load(filename)

    def load(self, input_folder):
        """Load values from ``*.npy`` files in ``input_folder``."""
        self._interact_with_folder(input_folder, "r")

    def export(self, output_folder):
        """Export matrices as ``*.npy`` files to an output folder."""
        print(f'Saving: {output_folder}')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        self._interact_with_folder(output_folder, "w")


class CameraCalibration(Calibration):
    def __init__(self, calibration=None, input_folder=None):
        self.rmse = np.inf
        self.mtx = None
        self.dist = None
        self.rvecs = None
        self.tvecs = None

        if calibration:
            self._copy_calibration(calibration)
        elif input_folder:
            self.load(input_folder)


class CameraCalibrator(ChessboardFinder):
    def add_corners(self, image, show_results=False):
        # img_size = [self.image_size[0] * 2, (self.image_size[1] // 2 )* 2]

        # resized = image
        # img_size = img_size[::-1]
        # print(self.image_size, img_size)
        # resized = cv.resize(image, img_size, interpolation=cv.INTER_LINEAR)
        try:
            corners = self._get_corners(resized)
            # map(lambda x: x / 2, corners)
        except ChessboardNotFoundError:
            raise ChessboardNotFoundError("No chessboard could be found.")
            return

        if show_results:
            self._show_corners(resized)

        self.image_count += 1
        self.image_points.append(corners.reshape(-1, 2))
        self.object_points.append(self.corner_coordinates)

    def __init__(self, pattern_size, square_size, image_size):
        #: Number of calibration images
        self.image_count = 0
        #: Number of inside corners in the chessboard's rows
        self.rows = pattern_size[0]
        #: Number of inside corners in the chessboard's columns
        self.columns = pattern_size[1]
        #: Size of chessboard squares in cm
        self.square_size = square_size
        #: Size of calibration images in pixels
        self.image_size = image_size

        corner_coordinates = np.zeros((np.prod(pattern_size), 3), np.float32)
        corner_coordinates[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
        corner_coordinates *= self.square_size

        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        #: Real world corner coordinates found in each image
        self.corner_coordinates = corner_coordinates
        #: Array of real world corner coordinates to match the corners found
        self.object_points = []
        #: Array of found corner coordinates from calibration image
        self.image_points = []

    def calibrate_camera(self):
        calib = CameraCalibration()

        (
            calib.rmse,
            calib.mtx,
            calib.dist,
            calib.rvecs,
            calib.tvecs,
        ) = cv.calibrateCamera(
            self.object_points, self.image_points, self.image_size, None, None
        )

        return calib


class StereoCalibration(Calibration):
    def __init__(self, calibration=None, input_folder=None):
        """
        Initialize camera calibration.
        If another calibration object is provided, copy its values. If an input
        folder is provided, load ``*.npy`` files from that folder. An input
        folder overwrites a calibration object.
        """
        self.rmse = np.inf
        #: Camera matrices (M)
        self.cam_mats = {"left": np.array([]), "right": np.array([])}
        #: Distortion coefficients (D)
        self.dist_coefs = {"left": np.array([]), "right": np.array([])}
        #: Rotation matrix (R)
        self.rot_mat = np.array([])
        #: Translation vector (T)
        self.trans_vec = np.array([])
        #: Essential matrix (E)
        self.e_mat = np.array([])
        #: Fundamental matrix (F)
        self.f_mat = np.array([])
        #: Rectification transforms (3x3 rectification matrix R1 / R2)
        self.rect_trans = {"left": np.array([]), "right": np.array([])}
        #: Projection matrices (3x4 projection matrix P1 / P2)
        self.proj_mats = {"left": np.array([]), "right": np.array([])}
        #: Disparity to depth mapping matrix (4x4 matrix, Q)
        self.disp_to_depth_mat = np.array([])
        #: Bounding boxes of valid pixels
        self.valid_boxes = {"left": np.array([]), "right": np.array([])}
        #: Undistortion maps for remapping
        self.undistortion_map = {"left": np.array([]), "right": np.array([])}
        #: Rectification maps for remapping
        self.rectification_map = {"left": np.array([]), "right": np.array([])}

        if calibration:
            self._copy_calibration(calibration)
        elif input_folder:
            self.load(input_folder)

    def rectify(self, frames):
        """
        Rectify frames passed as (left, right) pair of OpenCV Mats.
        Remapping is done with nearest neighbor for speed.
        """
        new_frames = []
        for i, side in enumerate(("left", "right")):
            new_frames.append(
                cv.remap(
                    frames[i],
                    self.undistortion_map[side],
                    self.rectification_map[side],
                    cv.INTER_NEAREST,
                )
            )
        return new_frames


class StereoCalibrator(ChessboardFinder):

    """A class that calibrates stereo cameras by finding chessboard corners."""

    def add_corners(self, image_pair, show_results=False):
        """
        Record chessboard corners found in an image pair.

        The image pair should be an iterable composed of two CvMats ordered
        (left, right).
        """
        side = "left"

        corners_dict = {"left": None, "right": None}
        for image in image_pair:
            try:
                corners = self._get_corners(image)
            except ChessboardNotFoundError:
                raise ChessboardNotFoundError("No chessboard could be found.")
                return

            if show_results:
                self._show_corners(image, corners)

            corners_dict[side] = corners.reshape(-1, 2)
            
            side = "right"

        for side in ["left", "right"]:
            self.image_points[side].append(corners_dict[side])

        self.object_points.append(self.corner_coordinates)
        self.image_count += 1

    def __init__(
        self,
        rows,
        columns,
        square_size,
        image_size,
        cam_calib_left=None,
        cam_calib_right=None,
        alpha=-1,
    ):
        """
        Store variables relevant to the camera calibration.
        ``corner_coordinates`` are generated by creating an array of 3D
        coordinates that correspond to the actual positions of the chessboard
        corners observed on a 2D plane in 3D space.
        """
        self.alpha = alpha
        #: Number of calibration images
        self.image_count = 0
        #: Number of inside corners in the chessboard's rows
        self.rows = rows
        #: Number of inside corners in the chessboard's columns
        self.columns = columns
        #: Size of chessboard squares in cm
        self.square_size = square_size
        #: Size of calibration images in pixels
        self.image_size = image_size

        self.cameras_calibration = {"left": cam_calib_left, "right": cam_calib_right}

        pattern_size = (self.rows, self.columns)
        corner_coordinates = np.zeros((np.prod(pattern_size), 3), np.float32)
        corner_coordinates[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
        corner_coordinates *= self.square_size

        # print(corner_coordinates)
        #: Real world corner coordinates found in each image
        self.corner_coordinates = corner_coordinates
        #: Array of real world corner coordinates to match the corners found
        self.object_points = []
        #: Array of found corner coordinates from calibration images for left
        #: and right camera, respectively
        self.image_points = {"left": [], "right": []}

        self.criteria = (cv.TERM_CRITERIA_MAX_ITER + cv.TERM_CRITERIA_EPS, 100, 1e-5)

    def calibrate_cameras(self):
        """Calibrate cameras based on found chessboard corners."""

        # flags = (cv.CALIB_FIX_ASPECT_RATIO + cv.CALIB_ZERO_TANGENT_DIST +
        #          cv.CALIB_SAME_FOCAL_LENGTH + cv.CALIB_CB_ADAPTIVE_THRESH +
        #          cv.CALIB_USE_INTRINSIC_GUESS + cv.CALIB_FIX_K3)

        calib = StereoCalibration()

        sides = ["left", "right"]

        for side in sides:
            calib.cam_mats[side] = self.cameras_calibration[side].mtx

        stereocalibration_flags = cv.CALIB_FIX_INTRINSIC


        print( len(self.object_points),
            len(self.image_points["left"]),
            len(self.image_points["right"]))
        (
            calib.rmse,
            calib.cam_mats["left"],
            calib.dist_coefs["left"],
            calib.cam_mats["right"],
            calib.dist_coefs["right"],
            calib.rot_mat,
            calib.trans_vec,
            calib.e_mat,
            calib.f_mat,
        ) = cv.stereoCalibrate(
            self.object_points,
            self.image_points["left"],
            self.image_points["right"],
            calib.cam_mats["left"],
            calib.dist_coefs["left"],
            calib.cam_mats["right"],
            calib.dist_coefs["right"],
            self.image_size,
            criteria=self.criteria,
            flags=stereocalibration_flags,
        )

        (
            calib.rect_trans["left"],
            calib.rect_trans["right"],
            calib.proj_mats["left"],
            calib.proj_mats["right"],
            calib.disp_to_depth_mat,
            calib.valid_boxes["left"],
            calib.valid_boxes["right"],
        ) = cv.stereoRectify(
            calib.cam_mats["left"],
            calib.dist_coefs["left"],
            calib.cam_mats["right"],
            calib.dist_coefs["right"],
            self.image_size,
            calib.rot_mat,
            calib.trans_vec,
            alpha=self.alpha,
            flags=0,
        )

        for side in ("left", "right"):
            (
                calib.undistortion_map[side],
                calib.rectification_map[side],
            ) = cv.initUndistortRectifyMap(
                calib.cam_mats[side],
                calib.dist_coefs[side],
                calib.rect_trans[side],
                calib.proj_mats[side],
                self.image_size,
                cv.CV_32FC1,
            )

        return calib

    def check_calibration(self, calibration):
        """
        Check calibration quality by computing average reprojection error.
        First, undistort detected points and compute epilines for each side.
        Then compute the error between the computed epipolar lines and the
        position of the points detected on the other side for each point and
        return the average error.
        """
        sides = "left", "right"
        which_image = {sides[0]: 1, sides[1]: 2}
        undistorted, lines = {}, {}
        for side in sides:
            undistorted[side] = cv.undistortPoints(
                np.concatenate(self.image_points[side]).reshape(-1, 1, 2),
                calibration.cam_mats[side],
                calibration.dist_coefs[side],
                P=calibration.cam_mats[side],
            )
            lines[side] = cv.computeCorrespondEpilines(
                undistorted[side], which_image[side], calibration.f_mat
            )
        total_error = 0
        this_side, other_side = sides
        for side in sides:
            for i in range(len(undistorted[side])):
                total_error += abs(
                    undistorted[this_side][i][0][0] * lines[other_side][i][0][0]
                    + undistorted[this_side][i][0][1] * lines[other_side][i][0][1]
                    + lines[other_side][i][0][2]
                )
            other_side, this_side = sides
        total_points = self.image_count * len(self.object_points)
        return total_error / total_points


class ChessboardNotFoundError(Exception):
    """No chessboard could be found in searched image."""
