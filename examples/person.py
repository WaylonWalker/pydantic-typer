
from examples.models import Person
from pydantic_typer import expand_pydantic_args


@expand_pydantic_args()
def get_person(person: Person, thing: str = None) -> Person:
    """mydocstring"""
    from rich import print

    print(str(thing))

    print(person)
