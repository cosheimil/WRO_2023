import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from stereo_camera import PS5_Cam

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

img_ptsL = []
img_ptsR = []
obj_pts = []

enter_key = 13

ps_cam = PS5_Cam(3)
ps_cam.set_fps(60)

search_pattern = (5, 7)
objp = np.zeros((search_pattern[0] * search_pattern[1], 3), np.float32)
objp[:, :2] = np.mgrid[0 : search_pattern[0], 0 : search_pattern[1]].T.reshape(-1, 2)

image_counts = 1


def main():
    scan = False
    count = 0
    matrix_l = np.zeros((3, 3))
    matrix_r = np.zeros((3, 3))
    mtx_l, mtx_r = np.zeros((3, 3)), np.zeros((3, 3))
    dist_l, dist_r = np.zeros((1, 5)), np.zeros((1, 5))
    roi_l, roi_r = np.zeros((4,)), np.zeros((4,))

    while count < image_counts:
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

        video_l, video_r = ps_cam.read_gray()

        cornersR, cornersL = np.array([]), np.array([])

        retL, retR = False, False

        if (cv.waitKey(1) == enter_key) or scan:
            if not scan:
                print(f"Start_scanning: {count}")

            scan = True

            retR, cornersR = cv.findChessboardCorners(
                video_r, search_pattern, cv.CALIB_CB_NORMALIZE_IMAGE
            )

            retL, cornersL = cv.findChessboardCorners(
                video_l, search_pattern, cv.CALIB_CB_NORMALIZE_IMAGE
            )

            print(f"retL: {retL} | retR: {retR}")

            if retL and retR:
                obj_pts.append(objp)
                cv.cornerSubPix(video_r, cornersR, (11, 11), (-1, -1), criteria)
                cv.cornerSubPix(video_l, cornersL, (11, 11), (-1, -1), criteria)

                video_l, video_r = ps_cam.read_color()
                cv.drawChessboardCorners(video_r, search_pattern, cornersR, retR)
                cv.drawChessboardCorners(video_l, search_pattern, cornersL, retL)

                print(f"Pattern have found, count: {count}")

                count += 1
                scan = False

                img_ptsL.append(cornersL)
                img_ptsR.append(cornersR)

                # left_camera
                # print(video_l.shape)
                print("Left Camera")
                ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
                    obj_pts, img_ptsL, video_l.shape[:2], None, None
                )

                mtx_l += mtx
                dist_l += dist
                # print('Left camera matrix:')
                print("found left")

                w, h = ps_cam.width // 2, ps_cam.height
                m, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
                matrix_l += m
                roi_l += roi

                # right camera
                print("Right Camera")
                ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
                    obj_pts, img_ptsR, video_r.shape[:2], None, None
                )
                mtx_r += mtx
                dist_r += dist
                # print('Right camera matrix:')
                print("found left")

                m, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
                matrix_r += m
                roi_r += roi

        cv.imshow("cornersR", video_r)
        cv.imshow("cornersL", video_l)

        if retL and retR:
            cv.waitKey(0)

    # print(f'left shape: {matrix_l.shape}, right shape: {matrix_r.shape}')
    matrix_l = matrix_l / image_counts
    matrix_r = matrix_r / image_counts
    dist_l = dist_l / image_counts
    dist_r = dist_l / image_counts
    mtx_l = mtx_l / image_counts
    mtx_r = mtx_r / image_counts
    roi_l = roi_l // image_counts
    roi_r = roi_r // image_counts
    # print(roi_l, roi_r)
    # print(f'left matrix: {matrix_l}')
    # print(f'right matrix: {matrix_r}')
    # ps_cam.release()
    cv.destroyAllWindows()

    while True:
        video_l, video_r = ps_cam.read_gray()
        dst_l = cv.undistort(video_l, mtx_l, dist_l, None, matrix_l)
        dst_r = cv.undistort(video_r, mtx_r, dist_r, None, matrix_r)

        # x, y, w, h = roi_l.astype(np.int32)
        # dst_l = dst_l[y:y+h, x:x+w]
        cv.imshow("left", dst_l)

        # x, y, w, h = roi_r.astype(np.int32)
        # dst_r = dst_r[y:y+h, x:x+w]
        cv.imshow("right", dst_r)

        stereo = cv.StereoBM_create(numDisparities=16 * 3, blockSize=13)
        disparity = stereo.compute(dst_l, dst_r)

        if cv.waitKey(1) == enter_key:
            plt.imshow(disparity, "gray")
            plt.savefig("disp.jpg")

        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    ps_cam.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
