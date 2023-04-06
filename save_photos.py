import sys

sys.path.append("src")
from camera_calibration.photos_take import *
from stereo_vision.camera import *

pattern = (5, 7)

def main():
    print(PS5CameraModes.default.value)
    camera = CameraChessboardSaver(2, PS5CameraModes.dci_2k.value, "ps5_calib_2", pattern[0], pattern[1])
    # camera = StereoCam(2, PS5CameraModes.default.value)
    camera.show_videos()


if __name__ == "__main__":
    main()
