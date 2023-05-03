import cv2 as cv
from PIL import ImageEnhance, Image


video = cv.VideoCapture(0)
ret, frame = video.read()
im = Image.fromarray(frame)
enh = ImageEnhance.Contrast(im)
cv.imshow("View", frame)
enh.enhance(1.1).show("%10 more contrast")
cv.waitKey(0)