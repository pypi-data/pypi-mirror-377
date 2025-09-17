import sys
import pkg_resources

import typer
from loguru import logger

from .lidar.main import app as lidar_app

app = typer.Typer(
    name="GFATPy CLI",
    help="A console interface for the GFATPy utilities.",
    no_args_is_help=True,
)

app.add_typer(
    lidar_app,
    name="lidar",
    help="Lidar utilities to convert, read and plot lidar data.",
)


def version_callback(value: bool) -> None:
    if value:
        version = pkg_resources.get_distribution("gfatpy").version
        typer.echo(version)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Shows gfatpy version information",
    ),
    verbose: bool = typer.Option(False, "--verbose"),
):
    if verbose:
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")
