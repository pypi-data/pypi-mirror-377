from pathlib import Path
from importlib.metadata import version
from .config import set_logger_level
from importlib.metadata import version

set_logger_level("WARNING")

from . import lidar, utils, cloudnet, atmo, aeronet  # noqa: E402

# GET PACKAGE DIRECTORY
GFATPY_DIR = Path.cwd() / "gfatpy"

__all__ = ["lidar", "utils", "cloudnet", "atmo", "aeronet"]
__version__ = "0.16.6"

__doc__ = f"""
# What is gfatpy?
A python package for GFAT utilities {__version__}.

# Installation
You can use gfatpy either you could use the API (functions) only or maybe prefer to modify the source code. The second option requires aditional configuration.
The following are common requirements

- Python>=3.10 (Run `python3 --version` to verify)
- [Brew](https://brew.sh/) and [netCDF4](https://formulae.brew.sh/formula/netcdf#default) installed (MacOS)

## Downloading the repository
You must have access to the gfatpy [repository](https://gitlab.com/gfat1/gfatpy). Stable releases are at the `main` brach while other experimental features or work in progress is at `develop`.

## User installation
User installation is limited and could not be isolated for other system dependencies. Not recommended if you need to make changes to the code, run tests
Once the source code is downloaded, go to the directory where pyproject.toml is in shell (linux, macOS) or Powershell (Windows) and execute the following line:
```
python3 -m pip install .
```
Then, gfatpy will be available to import from your global python (or local in case you use virtualenvs)
## Development installation
This is the recommended way if changing code is needed, running the included notebooks, run the test and contribute.
You will need as aditional dependencies:
- [Poetry](https://python-poetry.org/docs/#installation)

After downloading or clonning the repository into your local machine execute `poetry install` to create the virtual environment and then `poetry shell` to activate it in the current shell.

Aditional commands:
- `gfatpy` will be available
- `pytest` will execute all the tests. Also it can recieve an argument especifying the route or file. For instance, `pytest tests/test_ecmwf.py` will execute only ECMWF related tests.

Contribution considerations:
- Merge requests or commits to develop branch on Gitlab.
- Run [pre-commit] on local by installing the git hook with `pre-commit install`

## Troubleshooting

#
"""
