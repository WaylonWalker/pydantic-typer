from pydantic_typer.console import console


def verbose_callback(value: bool) -> None:
    if value:
        console.quiet = False
