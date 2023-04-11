import glob

import cv2 as cv
import numpy as np


def calibrate_chessboard(dir_path, image_format, square_size, width, height):
    """Calibrate a camera using chessboard images."""
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
    objp = np.zeros((height * width, 3), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

    objp = objp * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    images = images = glob.glob(f"{dir_path}/*.{image_format}")
    # Iterate through all images
    for fname in images:
        img = cv.imread(fname)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (width, height), None)

        # If found, add object points, image points (after refining them)
        if ret:
            print("Yes!")
            objpoints.append(objp)

            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            cv.drawChessboardCorners(img, (7, 6), corners2, ret)
            cv.imshow("img", img)
            cv.waitKey(500)

    # Calibrate camera
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
        objpoints, imgpoints, (gray.shape[::-1]), None, None
    )

    return [ret, mtx, dist, rvecs, tvecs]


def save_coefficients(mtx, dist, path):
    """Save the camera matrix and the distortion coefficients to given path/file."""
    cv_file = cv.FileStorage(path, cv.FILE_STORAGE_WRITE)
    cv_file.write("K", mtx)
    cv_file.write("D", dist)
    cv_file.release()


def load_coefficients(path):
    """Loads camera matrix and distortion coefficients."""
    # FILE_STORAGE_READ
    cv_file = cv.FileStorage(path, cv.FILE_STORAGE_READ)

    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    camera_matrix = cv_file.getNode("K").mat()
    dist_matrix = cv_file.getNode("D").mat()

    cv_file.release()
    return [camera_matrix, dist_matrix]


def main():
    IMAGES_DIR = "img/chess_boards"
    IMAGES_FORMAT = "png"
    SQUARE_SIZE = 1.6
    WIDTH = 7
    HEIGHT = 4

    # Calibrate
    ret, mtx, dist, rvecs, tvecs = calibrate_chessboard(
        IMAGES_DIR, IMAGES_FORMAT, SQUARE_SIZE, WIDTH, HEIGHT
    )

    # Save coefficients into a file
    save_coefficients(mtx, dist, "calibration_chessboard.yml")


if __name__ == "__main__":
    main()
