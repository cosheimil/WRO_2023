import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt


def main():
    cap = cv.VideoCapture(2, cv.CAP_V4L)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 376)
    cap.set(cv.CAP_PROP_FPS, 120)

    while True:
        ret, frame = cap.read()
        video_l, video_r = frame[:, :640], frame[:, 640:]
        video_l = cv.cvtColor(video_l, cv.COLOR_BGR2GRAY)
        video_r = cv.cvtColor(video_r, cv.COLOR_BGR2GRAY)
        # cv.imshow("Left", video_l)
        # cv.imshow("Right", video_r)

        stereo = cv.StereoBM_create(numDisparities=16, blockSize=5)
        disparity = stereo.compute(video_l, video_r)
        plt.imshow(disparity)
        plt.imshow(video_l)
        plt.colorbar()
        plt.show() # test

        # cv.imshow("Right", video_r)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv.destroyAllWindows()


if __name__ == '__main__':
    print(main())
