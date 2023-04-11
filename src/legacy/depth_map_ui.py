import json
from glob import glob
from itertools import cycle
from pathlib import Path

import cv2 as cv
import numpy as np
from stereo_camera import PS5_Cam


def nah(x):
    ...


def main():
    # Setup
    print("1 - видео, 2 - с фото")
    mode = int(input("Читать с видео или с файла по пути WRO_2023/img/images/"))
    cam = PS5_Cam(2)
    if mode != 1 or mode != 2:
        print("Error!")
        return
    path_photos_l = Path(__file__).parent.parent / "img/images/imgL"
    path_photos_r = Path(__file__).parent.parent / "img/images/imgR"
    left_photos = glob(str(path_photos_l))
    right_photos = glob(str(path_photos_r))
    if mode == 2:
        print("Все фото: ")
        print(f"Левые: {left_photos}")
        print(f"Правые: {right_photos}")
        left_photos = cycle(left_photos)
        right_photos = cycle(right_photos)

    with open("params.json") as params:
        data = json.loads(json.load(params))
        (
            num_disp_start,
            block_size_start,
            prefilter_type_start,
            prefilter_size_start,
            prefilter_cap_start,
            texture_threshold_start,
            uniqueness_ratio_start,
            speckle_range_start,
            speckle_window_size_start,
            disp12_max_diff_start,
            min_disparity_start,
        ) = data.values()
    # Read values from file - xml!
    xml_file = Path(__file__).parent.parent / "camera_files/stereoMap.xml"

    cv_file = cv.FileStorage(str(xml_file), cv.FILE_STORAGE_READ)
    Left_Stereo_Map_x = cv_file.getNode("stereoMapL_x").mat()
    Left_Stereo_Map_y = cv_file.getNode("stereoMapL_y").mat()
    Right_Stereo_Map_x = cv_file.getNode("stereoMapR_x").mat()
    Right_Stereo_Map_y = cv_file.getNode("stereoMapR_y").mat()

    cv_file.release()

    # Make Window to comb depth map :)
    cv.namedWindow("depth", cv.WINDOW_NORMAL)
    cv.resizeWindow("depth", 1000, 1000)

    cv.createTrackbar("Num Disp", "depth", num_disp_start, 100, nah)
    cv.createTrackbar("Block Size", "depth", block_size_start, 100, nah)
    cv.createTrackbar("PreFilter Type", "depth", prefilter_type_start, 1, nah)
    cv.createTrackbar("PreFilter Size", "depth", prefilter_size_start, 50, nah)
    cv.createTrackbar("PreFilter Cap", "depth", prefilter_cap_start, 100, nah)
    cv.createTrackbar("Texture Threshold", "depth", texture_threshold_start, 255, nah)
    cv.createTrackbar("Uniqueness Ratio", "depth", uniqueness_ratio_start, 100, nah)
    cv.createTrackbar("Speckle Range", "depth", speckle_range_start, 100, nah)
    cv.createTrackbar(
        "Speckle Window Size", "depth", speckle_window_size_start, 50, nah
    )
    cv.createTrackbar("disp12MaxDiff", "depth", disp12_max_diff_start, 25, nah)
    cv.createTrackbar("Min Disparity", "depth", min_disparity_start, 25, nah)

    # Create stereo cam
    stereo = cv.StereoBM_create()
    c = 0
    while True:
        if cv.waitKey(13) == ord("q"):
            break

        if mode == 1 and c == 0:
            c += 1
            left_c, right_c = cam.read_color()
            left_gr, right_gr = cv.cvtColor(left_c, cv.COLOR_BGR2GRAY), cv.cvtColor(
                right_c, cv.COLOR_BGR2GRAY
            )

        if mode == 2 and c == 0:
            c += 1
            left_c = cv.imread(left_photos)
            right_c = cv.imread(right_photos)
            if cv.waitKey(33) == ord("a"):
                left_c = cv.imread(next(left_photos))
                right_c = cv.imread(next(right_photos))
            left_gr, right_gr = cv.cvtColor(left_c, cv.COLOR_BGR2GRAY), cv.cvtColor(
                right_c, cv.COLOR_BGR2GRAY
            )

        # Apply camera matrix
        left = cv.remap(
            left_gr,
            Left_Stereo_Map_x,
            Left_Stereo_Map_y,
            cv.INTER_LANCZOS4,
            cv.BORDER_CONSTANT,
            0,
        )

        right = cv.remap(
            right_gr,
            Right_Stereo_Map_x,
            Right_Stereo_Map_y,
            cv.INTER_LANCZOS4,
            cv.BORDER_CONSTANT,
            0,
        )

        # cv.imshow('Left', left)
        # cv.imshow('Right', right)

        # Getting Values from bars
        num_disp = cv.getTrackbarPos("Num Disp", "depth") * 16
        block_size = cv.getTrackbarPos("Block Size", "depth") * 2 + 1
        prefilter_type = cv.getTrackbarPos("PreFilter Type", "depth")
        prefilter_size = cv.getTrackbarPos("PreFilter Size", "depth") * 2 + 5
        prefilter_cap = cv.getTrackbarPos("PreFilter Cap", "depth")
        texture_threshold = cv.getTrackbarPos("Texture Threshold", "depth")
        uniqueness_ratio = cv.getTrackbarPos("Uniqueness Ratio", "depth")
        speckle_range = cv.getTrackbarPos("Speckle Range", "depth")
        speckle_window_size = cv.getTrackbarPos("Speckle Window Size", "depth") * 2
        disp12_max_diff = cv.getTrackbarPos("disp12MaxDiff", "depth")
        min_disparity = cv.getTrackbarPos("Min Disparity", "depth")

        data = {
            "Number Disparity": max(1, num_disp // 16),
            "Block Size": max(2, (block_size - 1) // 2),
            "Prefilter Type": prefilter_type,
            "Prefilter Size": (prefilter_size - 5) // 2,
            "Prefilter Cap": max(1, prefilter_cap),
            "Texture Threshold": texture_threshold,
            "Uniqueness Ratio": uniqueness_ratio,
            "Speckle Range": speckle_range,
            "Speckle Window Size": speckle_window_size // 2,
            "Disp12 Max Difference": disp12_max_diff,
            "Min Disparity": max(1, min_disparity),
        }

        json_string = json.dumps(data)

        with open("params.json", "w") as out:
            json.dump(json_string, out)

        # Let's apply them
        stereo.setNumDisparities(num_disp)
        stereo.setBlockSize(block_size)
        stereo.setPreFilterType(prefilter_type)
        stereo.setPreFilterSize(prefilter_size)
        stereo.setPreFilterCap(prefilter_cap)
        stereo.setTextureThreshold(texture_threshold)
        stereo.setUniquenessRatio(uniqueness_ratio)
        stereo.setSpeckleRange(speckle_range)
        stereo.setSpeckleWindowSize(speckle_window_size)
        stereo.setDisp12MaxDiff(disp12_max_diff)
        stereo.setMinDisparity(min_disparity)

        # Calculate Disparity
        disparity = stereo.compute(left, right)

        # Calculate Depth Map
        # denoise step 1
        denoised = ((disparity.astype(np.float32) / 16) - min_disparity) / num_disp
        dispc = (denoised - denoised.min()) * 255
        dispC = dispc.astype(np.uint8)

        # denoise step 2
        kernel = np.ones((5, 5), np.uint8)
        denoised = cv.morphologyEx(dispC, cv.MORPH_CLOSE, kernel)

        # apply color map
        disp_Color = cv.applyColorMap(denoised, cv.COLORMAP_OCEAN)

        f = 30  # 30cm focal length
        new_h, new_w = left.shape
        Q = np.float32(
            [
                [1, 0, 0, -0.5 * new_w],
                [0, -1, 0, 0.5 * new_h],  # turn points 180 deg around x-axis,
                [0, 0, 0, f],  # so that y-axis looks up
                [0, 0, 1, 0],
            ]
        )
        points = cv.reprojectImageTo3D(disparity, Q)

        z_values = points[:, :, 2]
        z_values = z_values.flatten()
        z_values.argsort()

        # visualize
        cv.imshow("depth", disp_Color)
        # cv.putText(color_depth, "minimum: " + str(round(min_distance,1)),(5, 20),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2,cv.LINE_AA)
        # cv.putText(color_depth, "average: " + str(round(avg_distance,1)),(5, 40),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2,cv.LINE_AA)
        # cv.putText(color_depth, "maximum: " + str(round(max_distance,1)),(5, 60),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2,cv.LINE_AA)
        # cv.putText(color_depth, "FPS: " + str(round(fps)),(5, 80),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2,cv.LINE_AA)

        # cv.imshow("color & Depth", color_depth)


if __name__ == "__main__":
    main()
