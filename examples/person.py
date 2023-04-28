from pyannotate_runtime import collect_types

from examples.models import Person
from pydantic_typer import expand_pydantic_args


@expand_pydantic_args()
def get_person(person: Person, thing: str = None) -> Person:
    """Mydocstring."""
    from rich import print

    print(str(thing))
    print(person)


if __name__ == "__main__":
    collect_types.init_types_collection()
    with collect_types.collect():
        person = get_person(name="John", age=1, r=1, g=1, b=1, a=1, length=1)

    collect_types.dump_stats("type_info.json")
