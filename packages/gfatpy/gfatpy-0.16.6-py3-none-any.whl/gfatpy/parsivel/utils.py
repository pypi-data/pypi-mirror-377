from pathlib import Path
from gfatpy.utils.io import read_yaml

INFO_FILE = Path(__file__).parent.absolute() / "info.yml"
DSD_INFO = read_yaml(INFO_FILE)
