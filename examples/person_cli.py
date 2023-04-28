import typer

from examples.models import Person
from pydantic_typer import expand_pydantic_args

app = typer.Typer(
    name="pydantic_typer",
    help="a demo app",
)


@app.callback()
def main() -> None:
    return


@app.command()
@expand_pydantic_args(typer=True)
def get_person(person: Person, thing: str, another: str = "this") -> Person:
    """Get a person's information."""
    from rich import print

    print(thing)
    print(another)

    print(person)


if __name__ == "__main__":
    typer.run(get_person)