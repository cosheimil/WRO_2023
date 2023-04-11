import json
from pathlib import Path

import cv2 as cv


class BlockMatcher:
    def __init__(self):
        self.stereo_bm = cv.StereoBM_create()
        self._num_disp = 1
        self._block_size = 2
        self._prefilter_type = 0
        self._prefilter_size = 0
        self._prefilter_cap = 0
        self._texture_threshold = 0
        self._uniqueness_ratio = 0
        self._speckle_range = 0
        self._speckle_window_size = 5
        self._disp12_max_diff = 0
        self._min_disparity = 0

    parameter_maxima = {
        "num_disp": 50,
        "block_size": 50,
        "prefilter_type": 1,
        "prefilter_size": 25,
        "prefilter_cap": 62,
        "texture_threshold": 50,
        "uniqueness_ratio": 50,
        # 'speckle_range': 50,
        'speckle_window_size': 255,
        # 'disp12_max_diff': 25,
        # 'min_disparity': 25,
    }


    @property
    def num_disp(self):
        return self._num_disp

    @num_disp.setter
    def num_disp(self, num_disp):
        self._num_disp = num_disp
        self.stereo_bm.setNumDisparities((num_disp + 1) * 16)

    @property
    def block_size(self):
        return self._block_size

    @block_size.setter
    def block_size(self, block_size):
        self._block_size = block_size
        self.stereo_bm.setBlockSize(5 + block_size * 2)

    @property
    def prefilter_type(self):
        return self._prefilter_type

    @prefilter_type.setter
    def prefilter_type(self, prefilter_type):
        self._prefilter_type = prefilter_type
        self.stereo_bm.setPreFilterType(prefilter_type)

    @property
    def prefilter_size(self):
        return self._prefilter_size

    @prefilter_size.setter
    def prefilter_size(self, prefilter_size):
        self._prefilter_size = prefilter_size
        self.stereo_bm.setPreFilterSize(prefilter_size * 2 + 5)

    @property
    def prefilter_cap(self):
        return self._prefilter_cap

    @prefilter_cap.setter
    def prefilter_cap(self, prefilter_cap):
        self._prefilter_cap = prefilter_cap
        self.stereo_bm.setPreFilterCap(prefilter_cap + 1)

    @property
    def texture_threshold(self):
        return self._texture_threshold

    @texture_threshold.setter
    def texture_threshold(self, texture_threshold):
        self._texture_threshold = texture_threshold
        self.stereo_bm.setTextureThreshold(texture_threshold + 1)

    @property
    def uniqueness_ratio(self):
        return self._uniqueness_ratio

    @uniqueness_ratio.setter
    def uniqueness_ratio(self, uniqueness_ratio):
        self._uniqueness_ratio = uniqueness_ratio
        self.stereo_bm.setUniquenessRatio(uniqueness_ratio + 1)

    @property
    def speckle_range(self):
        return self._speckle_range

    @speckle_range.setter
    def speckle_range(self, speckle_range):
        self._speckle_range = speckle_range
        self.stereo_bm.setSpeckleRange(speckle_range + 1)

    @property
    def speckle_window_size(self):
        return self._speckle_window_size

    @speckle_window_size.setter
    def speckle_window_size(self, speckle_window_size):
        self._speckle_window_size = speckle_window_size
        self.stereo_bm.setSpeckleWindowSize(speckle_window_size * 2)

    @property
    def disp12_max_diff(self):
        return self._disp12_max_diff

    @disp12_max_diff.setter
    def disp12_max_diff(self, disp12_max_diff):
        self._disp12_max_diff = disp12_max_diff
        self.stereo_bm.setDisp12MaxDiff(disp12_max_diff)

    @property
    def min_disparity(self):
        return self._min_disparity

    @min_disparity.setter
    def min_disparity(self, min_disparity):
        self._min_disparity = min_disparity
        self.stereo_bm.setMinDisparity(min_disparity)

    def save_to_json(self, dir_name, file_name):
        data = {
            "Number Disparity": max(1, self.num_disp),
            "Block Size": max(2, self.block_size),
            "Prefilter Type": self.prefilter_type,
            "Prefilter Size": self.prefilter_size,
            "Prefilter Cap": max(1, self.prefilter_cap),
            "Texture Threshold": self.texture_threshold,
            "Uniqueness Ratio": self.uniqueness_ratio,
            "Speckle Range": self.speckle_range,
            "Speckle Window Size": self.speckle_window_size,
            "Disp12 Max Difference": self.disp12_max_diff,
            "Min Disparity": max(1, self.min_disparity),
        }

        with open(Path(dir_name) / f"./{file_name}.json", "w") as out:
            json.dump(json.dumps(data), out)

    def load_from_json(self, dir_name, file_name):
        with open(Path(dir_name) / f"./{file_name}.json", "r") as params:
            data = json.loads(json.load(params))
            (
                self.num_disp_start,
                self.block_size_start,
                self.prefilter_type_start,
                self.prefilter_size_start,
                self.prefilter_cap_start,
                self.texture_threshold_start,
                self.uniqueness_ratio_start,
                self.speckle_range_start,
                self.speckle_window_size_start,
                self.disp12_max_diff_start,
                self.min_disparity_start,
            ) = data.values()

    @classmethod
    def get_3d(cls, disparity, disparity_to_depth_map):
        """Compute point cloud."""
        return cv.reprojectImageTo3D(disparity, disparity_to_depth_map)

    def get_disparity(self, pair):
        """
        Compute disparity from image pair (left, right).

        First, convert images to grayscale if needed. Then pass to the
        ``_block_matcher`` for stereo matching.
        """
        gray = []
        if pair[0].ndim == 3:
            for side in pair:
                gray.append(cv.cvtColor(side, cv.COLOR_BGR2GRAY))
        else:
            gray = pair

        # disp = self.stereo_bm.compute(gray[0], gray[1])
        # norm_coeff = 255 / disp.max()
        return self.stereo_bm.compute(gray[0], gray[1])
        # return disp * norm_coeff / 255


class BadBlockMatcherArgumentError(Exception):
    """Bad argument supplied for a ``BlockMatcher``."""


class StereoBMError(BadBlockMatcherArgumentError):
    """Bad argument supplied for a ``StereoBM``."""


class StereoSGBMError(BadBlockMatcherArgumentError):
    """Bad argument supplied for a ``StereoSGBM``."""


class InvalidBMPresetError(StereoBMError):
    """Invalid BM preset."""


class InvalidSearchRangeError(StereoBMError):
    """Invalid search range."""


class InvalidWindowSizeError(StereoBMError):
    """Invalid search range."""


class InvalidNumDisparitiesError(StereoSGBMError):
    """Invalid number of disparities."""


class InvalidSADWindowSizeError(StereoSGBMError):
    """Invalid search window size."""


class InvalidFirstDisparityChangePenaltyError(StereoSGBMError):
    """Invalid first disparity change penalty."""


class InvalidSecondDisparityChangePenaltyError(StereoSGBMError):
    """Invalid second disparity change penalty."""


class InvalidUniquenessRatioError(StereoSGBMError):
    """Invalid uniqueness ratio."""


class InvalidSpeckleWindowSizeError(StereoSGBMError):
    """Invalid speckle window size."""


class InvalidSpeckleRangeError(StereoSGBMError):
    """Invalid speckle range."""
