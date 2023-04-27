import typer

from pydantic_typer import Person, expand_pydantic_args
from pydantic_typer.cli.common import verbose_callback
from pydantic_typer.cli.config import config_app
from pydantic_typer.cli.tui import tui_app

app = typer.Typer(
    name="pydantic_typer",
    help="A rich terminal report for coveragepy.",
)
app.add_typer(config_app)
app.add_typer(tui_app)


def version_callback(value: bool) -> None:
    """Callback function to print the version of the pydantic-typer package.

    Args:
        value (bool): Boolean value to determine if the version should be printed.

    Raises:
        typer.Exit: If the value is True, the version will be printed and the program will exit.

    Example:
        version_callback(True)
    """
    if value:
        from pydantic_typer.__about__ import __version__

        typer.echo(f"{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(
        False,
        callback=verbose_callback,
        help="show the log messages",
    ),
) -> None:
    return


@app.command()
@expand_pydantic_args
def get_person(person: Person) -> Person:
    """mydocstring"""
    from rich import print

    print(person)


if __name__ == "__main__":
    typer.run(main)
