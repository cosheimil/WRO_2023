import cv2 as cv
import numpy as np
import subprocess

subprocess.check_call("v4l2-ctl -d /dev/video2 -c exposure_time_absolute=9", shell=True)
subprocess.check_call("v4l2-ctl -d /dev/video2 -c saturation=10", shell=True)
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
width, height = 1280, 376
search_pattern = (6, 7)

objp = np.zeros((search_pattern[0] * search_pattern[1], 3), np.float32)
objp[:, :2] = np.mgrid[0 : search_pattern[0], 0 : search_pattern[1]].T.reshape(-1, 2)

img_ptsL = []
img_ptsR = []
obj_pts = []


def main():
    cap = cv.VideoCapture(2, cv.CAP_V4L)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv.CAP_PROP_FPS, 20)
    count = 0
    while count <= 3:
        ret, frame = cap.read()
        video_l, video_r = frame[:, : width // 2], frame[:, width // 2 :]
        imgL_gray = cv.cvtColor(video_l, cv.COLOR_BGR2GRAY)
        imgR_gray = cv.cvtColor(video_r, cv.COLOR_BGR2GRAY)
        outputR = video_r.copy()
        outputL = video_l.copy()
        cornersR, cornersL = np.array([]), np.array([])
        retR, cornersR = cv.findChessboardCorners(
            video_r, search_pattern, cv.CALIB_CB_NORMALIZE_IMAGE
        )
        retL, cornersL = cv.findChessboardCorners(
            video_l, search_pattern, cv.CALIB_CB_NORMALIZE_IMAGE
        )
        if retL and retR:
            count += 1
            obj_pts.append(objp)
            cv.cornerSubPix(imgR_gray, cornersR, (11, 11), (-1, -1), criteria)
            cv.cornerSubPix(imgL_gray, cornersL, (11, 11), (-1, -1), criteria)
            cv.drawChessboardCorners(outputR, search_pattern, cornersR, retR)
            cv.drawChessboardCorners(outputL, search_pattern, cornersL, retL)
            cv.imshow("cornersR", outputR)
            cv.imshow("cornersL", outputL)
            cv.waitKey(0)

            img_ptsL.append(cornersL)
            img_ptsR.append(cornersR)
        cv.imshow("cornersR", video_r)
        cv.imshow("cornersL", video_l)

        # Calibrating left camera
    retL, mtxL, distL, rvecsL, tvecsL = cv.calibrateCamera(
        obj_pts, img_ptsL, imgL_gray.shape[::-1], None, None
    )
    hL, wL = imgL_gray.shape[:2]
    new_mtxL, roiL = cv.getOptimalNewCameraMatrix(mtxL, distL, (wL, hL), 1, (wL, hL))

    # Calibrating right camera
    retR, mtxR, distR, rvecsR, tvecsR = cv.calibrateCamera(
        obj_pts, img_ptsR, imgR_gray.shape[::-1], None, None
    )
    hR, wR = imgR_gray.shape[:2]
    new_mtxR, roiR = cv.getOptimalNewCameraMatrix(mtxR, distR, (wR, hR), 1, (wR, hR))

    flags = 0
    flags |= cv.CALIB_FIX_INTRINSIC
    # Here we fix the intrinsic camara matrixes so that only Rot, Trns, Emat and Fmat are calculated.
    # Hence intrinsic parameters are the same

    criteria_stereo = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # This step is performed to transformation between the two cameras and calculate Essential and Fundamenatl matrix
    retS, new_mtxL, distL, new_mtxR, distR, Rot, Trns, Emat, Fmat = cv.stereoCalibrate(
        obj_pts,
        img_ptsL,
        img_ptsR,
        new_mtxL,
        distL,
        new_mtxR,
        distR,
        imgL_gray.shape[::-1],
        criteria_stereo,
        flags,
    )

    rectify_scale = 1
    rect_l, rect_r, proj_mat_l, proj_mat_r, Q, roiL, roiR = cv.stereoRectify(
        new_mtxL,
        distL,
        new_mtxR,
        distR,
        imgL_gray.shape[::-1],
        Rot,
        Trns,
        rectify_scale,
        (0, 0),
    )

    Left_Stereo_Map = cv.initUndistortRectifyMap(
        new_mtxL, distL, rect_l, proj_mat_l, imgL_gray.shape[::-1], cv.CV_16SC2
    )
    Right_Stereo_Map = cv.initUndistortRectifyMap(
        new_mtxR, distR, rect_r, proj_mat_r, imgR_gray.shape[::-1], cv.CV_16SC2
    )

    print("Saving parameters ......")
    print(Left_Stereo_Map)
    cv_file = cv.FileStorage("improved_params2.xml", cv.FILE_STORAGE_WRITE)
    cv_file.write("Left_Stereo_Map_x", Left_Stereo_Map[0])
    cv_file.write("Left_Stereo_Map_y", Left_Stereo_Map[1])
    cv_file.write("Right_Stereo_Map_x", Right_Stereo_Map[0])
    cv_file.write("Right_Stereo_Map_y", Right_Stereo_Map[1])
    cv_file.release()


if __name__ == "__main__":
    main()
