import cv2 as cv
from PIL import ImageEnhance, Image
import numpy as np

factor = 1

def nah(x):
    pass

video = cv.VideoCapture(0)
cv.namedWindow('Video')
cv.createTrackbar('Contrast', 'Video', factor, 999, nah)
ret, frame = video.read()
while True:
    if cv.waitKey(1) == ord('a'):
        break
    ret, frame = video.read()
    print(type(frame))
    