from pathlib import Path
import math
import numpy as np
from datetime import datetime
import pandas as pd

import xarray as xr

from .types import RadarInfoType
from gfatpy.utils.io import read_yaml

""" MODULE For General Lidar Utilities
"""

# RADAR SYSTEM INFO
INFO_FILE = Path(__file__).parent.absolute() / "info.yml"
RADAR_INFO: RadarInfoType = read_yaml(INFO_FILE)

INFO_PLOT_FILE = Path(__file__).parent.absolute() / "plot" / "info.yml"
RADAR_PLOT_INFO = read_yaml(INFO_PLOT_FILE)











