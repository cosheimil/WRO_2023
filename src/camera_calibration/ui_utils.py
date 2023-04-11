from functools import partial

import cv2 as cv
from src.camera_calibration.calibration import *

# from progressbar import ProgressBar, Percentage, Bar


class BMTuner(object):

    """
    A class for tuning Stereo BM settings.

    Display a normalized disparity picture from two pictures captured with a
    ``CalibratedPair`` and allow the user to manually tune the settings for the
    ``BlockMatcher``.

    The settable parameters are intelligently read from the ``BlockMatcher``,
    relying on the ``BlockMatcher`` exposing them as ``parameter_maxima``.
    """

    #: Window to show results in
    window_name = "BM Tuner"
    track_bars_created = False

    def _set_value(self, parameter, new_value):
        """Try setting new parameter on ``block_matcher`` and update map."""
        try:
            self.block_matcher.__setattr__(parameter, new_value)
        except BadBlockMatcherArgumentError:
            return

    def _initialize_trackbars(self):
        """
        Initialize trackbars by discovering ``block_matcher``'s parameters.
        """
        self.track_bars_created = False
        for parameter in self.block_matcher.parameter_maxima.keys():
            maximum = self.block_matcher.parameter_maxima[parameter]
            cv.createTrackbar(
                parameter,
                self.window_name,
                self.block_matcher.__getattribute__(parameter),
                maximum,
                partial(self._set_value, parameter),
            )
        self.track_bars_created = True

    def _save_bm_state(self):
        """Save current state of ``block_matcher``."""
        for parameter in self.block_matcher.parameter_maxima.keys():
            self.bm_settings[parameter].append(
                self.block_matcher.__getattribute__(parameter)
            )

    def __init__(self, block_matcher, calibration, image_pair):
        """
        Initialize tuner window and tune given pair.

        ``block_matcher`` is a ``BlockMatcher``, ``calibration`` is a
        ``StereoCalibration`` and ``image_pair`` is a rectified image pair.
        """
        #: Stereo calibration to find Stereo BM settings for
        self.calibration = calibration
        #: (left, right) image pair to find disparity between
        self.pair = image_pair
        #: Block matcher to be tuned
        self.block_matcher = block_matcher
        #: Shortest dimension of image
        self.shortest_dimension = min(self.pair[0].shape[:2])
        #: Settings chosen for ``BlockMatcher``
        self.bm_settings = {}
        for parameter in self.block_matcher.parameter_maxima.keys():
            self.bm_settings[parameter] = []
        cv.namedWindow(self.window_name)
        self._initialize_trackbars()
        self.tune_pair(image_pair)

    def update_disparity_map(self):
        """
        Update disparity map in GUI.

        The disparity image is normalized to the range 0-255 and then divided by
        255, because OpenCV multiplies it by 255 when displaying. This is
        because the pixels are stored as floating points.
        """
        disparity = self.block_matcher.get_disparity(self.pair)
        norm_coeff = 255 / disparity.max()
        cv.imshow(self.window_name, disparity * norm_coeff / 255)
        # cv.waitKey()

    def tune_pair(self, pair):
        """Tune a pair of images."""
        self._save_bm_state()
        self.pair = pair
        while True:
            self.update_disparity_map()
            if cv.waitKey(1) == ord("a"):
                break

        cv.destroyWindow(self.window_name)
        # print(self.track_bars_created)

    def report_settings(self, parameter):
        """
        Report chosen settings for ``parameter`` in ``block_matcher``.

        ``bm_settings`` is updated to include the latest state before work is
        begun. This state is removed at the end so that the method has no side
        effects. All settings are reported except for the first one on record,
        which is ``block_matcher``'s default setting.
        """
        self._save_bm_state()
        report = []
        settings_list = self.bm_settings[parameter][1:]
        unique_values = list(set(settings_list))
        value_frequency = {}
        for value in unique_values:
            value_frequency[settings_list.count(value)] = value
        frequencies = value_frequency.keys()
        frequencies.sort(reverse=True)
        header = "{} value | Selection frequency".format(parameter)
        left_column_width = len(header[:-21])
        right_column_width = 21
        report.append(header)
        report.append("{}|{}".format("-" * left_column_width, "-" * right_column_width))
        for frequency in frequencies:
            left_column = str(value_frequency[frequency]).center(left_column_width)
            right_column = str(frequency).center(right_column_width)
            report.append("{}|{}".format(left_column, right_column))
        # Remove newest settings
        for param in self.block_matcher.parameter_maxima.keys():
            self.bm_settings[param].pop(-1)
        return "\n".join(report)
