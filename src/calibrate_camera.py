import glob

import cv2 as cv
import numpy as np

from stereo_camera import PS5_Cam

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob("img/chess_boards/*.png")

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7, 6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (7, 6), corners2, ret)
        cv.imshow("img", img)
        cv.waitKey(500)

cv.destroyAllWindows()
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

img = cv.imread(images[0])
h, w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)

ps_cam = PS5_Cam(2)
while True:
    l, r = ps_cam.read_gray()
    cv.imshow("L", l)
    cv.imshow("R", r)
    dst_l = cv.remap(l, mapx, mapy, cv.INTER_LINEAR)
    dst_r = cv.remap(r, mapx, mapy, cv.INTER_LINEAR)
    x, y, w, h = roi
    dst_l = dst_l[y : y + h, x : x + w]
    dst_r = dst_r[y : y + h, x : x + w]
    cv.imshow("Left", dst_l)
    cv.imshow("Right", dst_r)
    if cv.waitKey(1) & 0xFF == ord("q"):
        break
# undistort

dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
# crop the image
x, y, w, h = roi
dst = dst[y : y + h, x : x + w]
cv.imwrite("calibresult.png", dst)
with open("camera_matrix.npy", "wb") as f:
    np.save(f, newcameramtx)
