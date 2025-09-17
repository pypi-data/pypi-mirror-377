import pathlib
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

import typer

from gfatpy.lidar.utils.types import LidarName, MeasurementType, Telescope
from gfatpy.lidar.reader import reader_xarray
from gfatpy.lidar.quality_assurance.rayleigh_fit import rayleigh_fit_from_file


app = typer.Typer(no_args_is_help=True)


@app.command(
    help="Converts raw lidar data to l1 data",
    no_args_is_help=True,
)

@app.command(help="QA Rayleigh fit", no_args_is_help=True)
def rayleigh_fit(
    file: Path = typer.Option(
        ..., "--file", "-f", readable=True, dir_okay=False, file_okay=True
    ),
    initial_hour: int = typer.Option(None, "--initial-hour", "-i"),
    duration: int = typer.Option(None, "--duration", "-d"),
    channels: Optional[List[str]] = typer.Option(None, "--channels", "-c"),
    reference_range: Optional[Tuple[float, float] | None] = typer.Option(
        None, "--reference-range", "-r"
    ),
    smooth_window: Optional[float | None] = typer.Option(None, "--smooth-window", "-s"),
    save_fig: bool = typer.Option(False, "--save-fig", "-g"),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        "-o",
        readable=True,
        writable=True,
        dir_okay=True,
        file_okay=False,
    ),
):
    if channels is not None:
        assert len(channels) > 0, "At least one channel is required"

    if reference_range is None:
        reference_range = (7000, 8000)

    if smooth_window is None:
        smooth_window = 250

    rayleigh_fit_from_file(
        file=file,
        initial_hour=initial_hour,
        duration=duration,
        channels=channels,
        reference_range=reference_range,
        smooth_window=smooth_window,
        output_dir=output_dir,
        save_fig=save_fig,
    )
