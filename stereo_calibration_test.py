import sys

sys.path.append("src")

from stereo_vision.camera import *
from camera_calibration.calibration import *

chessboard_path = "images/ps5_calib_2"
photos_path = "images/ps5_calib_2"

def config_dir(dir_name):
    return Path(__file__).parent / f"./config/{dir_name}"

chess_pattern = ((7, 5), 3)

def main():
    f_cam = File_Cam(chessboard_path, img_format="png")
    
    calib_left = CameraCalibration(input_folder=config_dir("ps5_1_left"))
    calib_right = CameraCalibration(input_folder=config_dir("ps5_1_right"))

    # stereo_calib = StereoCalibration(input_folder=config_dir("ps5_1_stereo"))


    f_cam.img_names = f_cam.img_names[:5]

    # e_l, calib_left = f_cam.calibrateSingle("left", chess_pattern, dir_name=config_dir("ps5_1_left"), show_results=False)
    # e_r, calib_right = f_cam.calibrateSingle("right", chess_pattern, dir_name=config_dir("ps5_1_right"), show_results=False)
    print(f"Calibrated!\ne_l: {calib_left.rmse} | e_r: {calib_right.rmse}")

    # f_cam.img_names = f_cam.img_names[:1]
    avg_error, stereo_calib = f_cam.calibrateStereo(chess_pattern, dir_name=config_dir("ps5_1_stereo"), single_calibrations=[calib_left, calib_right])

    print(f"Calibrated Stereo!\nrmse: {stereo_calib.rmse}")

    print(avg_error)

    f_cam.calibration = stereo_calib

    for i in range(len(f_cam.img_names)):
        f_cam.img_pointer = i
        f_cam.show_frames(rectify=True)
        cv.waitKey(0)


if __name__ == "__main__":
    main()