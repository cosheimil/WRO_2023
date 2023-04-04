import sys

sys.path.append("src")
from camera_calibration.photos_take import *


def main():
    camera = CameraChessboardSaver(2, ((2560, 800), 60), "img/", 5, 6)
    camera.show_videos()


if __name__ == "__main__":
    main()
