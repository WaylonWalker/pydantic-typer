from rich.console import Console
import typer

from pydantic_typer.cli.common import verbose_callback
from pydantic_typer.config import config as configuration

config_app = typer.Typer()


@config_app.callback()
def config(
    verbose: bool = typer.Option(
        False,
        callback=verbose_callback,
        help="show the log messages",
    ),
):
    "configuration cli"


@config_app.command()
def show(
    verbose: bool = typer.Option(
        False,
        callback=verbose_callback,
        help="show the log messages",
    ),
):
    Console().print(configuration)
