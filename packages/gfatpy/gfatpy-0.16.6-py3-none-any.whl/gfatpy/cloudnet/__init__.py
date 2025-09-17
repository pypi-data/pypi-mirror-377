import pathlib

import matplotlib

import matplotlib.pyplot as plt

from gfatpy.utils.io import read_yaml

# LIDAR SYSTEM INFO
CLOUDNET_INFO_FILE = pathlib.Path(__file__).parent.absolute() / "info.yml"
CLOUDNET_INFO = read_yaml(CLOUDNET_INFO_FILE)
