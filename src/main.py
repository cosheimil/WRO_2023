import cv2 as cv
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
    while count < image_counts:

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        video_l, video_r = ps_cam.read_gray()
        
        cornersR, cornersL = np.array([]), np.array([])

        retL, retR = False, False

        if (cv.waitKey(1)  == enter_key) or scan:
            if not scan:
                print(f'Start_scanning: {count}')

            scan = True

            retR, cornersR = cv.findChessboardCorners(
                video_r, search_pattern, cv.CALIB_CB_NORMALIZE_IMAGE
            )

            retL, cornersL = cv.findChessboardCorners(
                video_l, search_pattern, cv.CALIB_CB_NORMALIZE_IMAGE
            )

            print(f'retL: {retL} | retR: {retR}')

            if retL and retR:
                obj_pts.append(objp)
                cv.cornerSubPix(video_r, cornersR, (11, 11), (-1, -1), criteria)
                cv.cornerSubPix(video_l, cornersL, (11, 11), (-1, -1), criteria)

                video_l, video_r = ps_cam.read_color()
                cv.drawChessboardCorners(video_r, search_pattern, cornersR, retR)
                cv.drawChessboardCorners(video_l, search_pattern, cornersL, retL)

                print(f'Pattern have found, count: {count}')

                count += 1
                scan = False

                img_ptsL.append(cornersL)
                img_ptsR.append(cornersR)

                # left_camera
                # print(video_l.shape)
                print('Left Camera')
                ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(obj_pts, img_ptsL,
                    video_l.shape[:2], None, None)
                print('Left camera matrix:')
                print(mtx)
                # right camera
                print('Right Camera')
                ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(obj_pts, img_ptsR, 
                    video_r.shape[:2], None, None)

                print('Left camera matrix:')
                print(mtx)

        cv.imshow("cornersR", video_r)
        cv.imshow("cornersL", video_l)

        if retL and retR:
            cv.waitKey(0)

    ps_cam.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
