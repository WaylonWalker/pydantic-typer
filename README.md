# pydantic-typer

pydantic-typer is a Python package that provides a decorator that can be used to write functions that accept a Pydantic model, but at runtime will allow them to pass in fields to create the models on the fly.

https://user-images.githubusercontent.com/22648375/235036031-a9dc6589-e350-4a18-9114-6568cb362f74.mp4

## Installation

pypi package to come if this works out, and I can decide
what to call it. I think its possible to do this for other
objects like dataclasses as well.

```console
pip install git+https://github.com/WaylonWalker/pydantic-typer.gi
```

## Usage

Setup your models.

```python
from typing import Optional

from pydantic import BaseModel, Field


class Alpha(BaseModel):
    a: int


class Color(BaseModel):
    r: int
    g: int
    b: int
    alpha: Alpha


class Hair(BaseModel):
    color: Color
    length: int


class Person(BaseModel):
    name: str
    other_name: Optional[str] = None
    age: int
    email: Optional[str]
    pet: str = "dog"
    address: str = Field("123 Main St", description="Where the person calls home.")
    hair: Hair
```

Now create a typer command using your models.
`expand_pydantic_args` will expand all of the typer fields
for you.

```python
import typer
from pydantic_typer import expand_pydantic_args
app = typer.Typer(
    name="pydantic_typer",
    help="a demo app",
)

@app.command()
@expand_pydantic_args
def get_person(person: Person) -> Person:
    """Get a person's information."""
    from rich import print

    print(person)
```

Get the help message.

```console
pydantic-typer get-person --help

 Usage: pydantic-typer get-person [OPTIONS]

 Get a person's information.

╭─ Options ──────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                            │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Person ───────────────────────────────────────────────────────────────────────────────╮
│ *  --name              TEXT     [default: None] [required]                             │
│    --other-name        TEXT     [default: None]                                        │
│ *  --age               INTEGER  [default: None] [required]                             │
│    --email             TEXT     [default: None]                                        │
│    --pet               TEXT     [default: dog]                                         │
│    --address           TEXT     Where the person calls home. [default: 123 Main St]    │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Person.Hair ──────────────────────────────────────────────────────────────────────────╮
│ *  --length        INTEGER  [default: None] [required]                                 │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Person.Hair.Color ────────────────────────────────────────────────────────────────────╮
│ *  --r        INTEGER  [default: None] [required]                                      │
│ *  --g        INTEGER  [default: None] [required]                                      │
│ *  --b        INTEGER  [default: None] [required]                                      │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Person.Hair.Color.Alpha ──────────────────────────────────────────────────────────────╮
│ *  --a        INTEGER  [default: None] [required]                                      │
╰────────────────────────────────────────────────────────────────────────────────────────╯
```

Calling the cli will print out a Person object.

```console
pydantic-typer get-person --name me --age 1 --r 1 --g 1 --b 1 --a 1 --length 1
```

Calling the cli while not specifying required arguments will automatically prompt for them.

```console
pydantic-typer get-person
```

## License

`pydantic-typer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
