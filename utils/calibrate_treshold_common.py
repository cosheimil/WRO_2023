import cv2 as cv
from PIL import Image, ImageEnhance
import numpy as np

contrast = 1
block_size = 11
c = 1

def nah(x):
    pass

def enhance(frame, contrast):
    image_pil = Image.fromarray(frame)
    enhanced_image = ImageEnhance.Contrast(image_pil).enhance(contrast)
    enhanced = np.array(enhanced_image)
    return enhanced

def filter_frame_adaptive(
        image: np.ndarray,
        max_: int,
        type_adaptive=cv.ADAPTIVE_THRESH_MEAN_C,
        type_=cv.THRESH_BINARY,
        block_size=11,
        c=1,
    ):
        """Calculate threshold to frame by standard algos.

        Args:
        ----
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
        ------
            ValueError: If cannot calculate thresh

        Returns:
        -------
            np.array: image
        """
        if block_size % 2 == 0:
            block_size += 1

        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        thresh = cv.adaptiveThreshold(image, max_, type_adaptive, type_, block_size, c)
        return thresh

video = cv.VideoCapture(0)
cv.namedWindow("Tune")
cv.createTrackbar("Contrast", "Tune", contrast, 1_000, nah)
cv.createTrackbar("Block Size", "Tune", block_size, 100, nah)
cv.createTrackbar("Constant", "Tune", c, 1_000, nah)

ret, frame = video.read()
while True:
    if cv.waitKey(1) == ord("a"):
        break
    ret, frame = video.read()

    contrast = cv.getTrackbarPos("Contrast", "Tune")
    block_size = cv.getTrackbarPos("Block Size", "Tune")
    block_size = max(2, block_size)
    c = cv.getTrackbarPos("Constant", "Tune")
    left, right = frame[:, :frame.shape[1] // 2, :], frame[:, frame.shape[1] // 2:, :]
    left, right = enhance(left, 1 + contrast / 1000), enhance(right, 1 + contrast / 1_000)

    thr_l = filter_frame_adaptive(left, 255, block_size=block_size, c=c)
    thr_r = filter_frame_adaptive(right, 255, block_size=block_size, c=c)

    cv.imshow("Left", thr_l)
    cv.imshow("Right", thr_r)

    # print(type(frame))
