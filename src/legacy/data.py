import json
from dataclasses import asdict, dataclass

import numpy as np


@dataclass
class Params:
    """
    Data Class to save all params using during the race.
    """

    camera_matrix: np.array
    depth_map_params: {}

    def write_to_json(self, path_to_file):
        """Write all specs to file.

        Args:
        ----
            path_to_file (Path): path to saving file with all params
        """
        with open(path_to_file) as file:
            file.write(json.dumps(asdict(self)))
