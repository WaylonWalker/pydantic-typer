# SPDX-FileCopyrightText: 2023-present Waylon S. Walker <waylon@waylonwalker.com>
##
# SPDX-License-Identifier: MIT

from functools import wraps
import inspect
from typing import Callable, Optional

from pydantic import BaseModel, Field
import typer

__all__ = ["typer"]


class Person(BaseModel):
    name: str
    other_name: Optional[str] = None
    age: int
    email: Optional[str]
    pet: str = "dog"
    address: str = Field("123 Main St", description="Where the person calls home.")


def make_person(name: str, age: int) -> Person:
    return Person(name=name, age=age)


def make_annotation(name, field):

    annotation = (
        field.annotation.__name__
        if str(field.annotation).startswith("<")
        else str(field.annotation)
    )

    if field.default is None and not field.required:
        default = "None"
        default = f' = typer.Option(None, help="{field.field_info.description or ""}", rich_help_panel="Person")'
    elif field.default is not None:
        default = f'"{field.default}"'
        default = f' = typer.Option("{field.default}", help="{field.field_info.description or ""}", rich_help_panel="Person")'
    else:
        default = ""
        default = f' = typer.Option(..., help="{field.field_info.description or ""}", rich_help_panel="Person", prompt=True)'

    #  if not typer
    # return f"{name}: {annotation}{default}"
    return f"{name}: {annotation}{default}"


def make_signature(func, wrapper):
    sig = inspect.signature(func)
    more_args = []
    for name, param in sig.parameters.items():
        if hasattr(param.annotation, "__fields__"):
            more_args.extend(param.annotation.__fields__)

    wrapper.__doc__ = (
        func.__doc__ or ""
    ) + f"\nalso accepts {more_args} in place of person model"
    fields = Person.__fields__
    raw_args = [make_annotation(name, field) for name, field in fields.items()]
    args = ", ".join([arg for arg in raw_args if not "=" in arg])
    kwargs = ", ".join([arg for arg in raw_args if "=" in arg])

    call_args = ",".join([f"{name}={name}" for name, field in fields.items()])

    new_func = f"""
import typing
def {func.__name__}({args}{', ' if args else ''}{kwargs}):
    '''{func.__doc__}'''
    return wrapper({call_args})
    """
    # new_func_sig = f"""{func.__name__}({args}{', ' if args else ''}{kwargs})"""
    # import typing

    # from makefun import create_function

    # __all__ = ["typing"]

    # new_func = create_function(new_func_sig, func, inject_as_first_arg=True)

    # signature = inspect.Signature()
    # signature.add("a", inspect.Parameter(default=1))
    # signature.add("b", inspect.Parameter(default=2))
    # signature.return_annotation = int
    # func.signature = signature
    # signature = inspect.Signature(
    #     a=Parameter(default=1), b=Parameter(default=2), return_annotation=int
    # )
    exec(new_func, locals(), globals())
    return globals()[func.__name__]


def expand_pydantic_args(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        import inspect

        sig = inspect.signature(func)

        instances = {}
        for name, value in kwargs.items():
            if name in sig.parameters:
                instances[name] = value

        for name, param in sig.parameters.items():
            # func wants this directly
            # this should check isinstance, but it's not working
            if name in kwargs and repr(param.annotation) == repr(kwargs[name]):
                instances[name] = kwargs[name]

            # an instance was not passed in, create one with kwargs passed in
            elif hasattr(param.annotation, "__fields__"):
                instances[name] = param.annotation(**kwargs)

        return func(**instances)

    return make_signature(func, wrapper)


# @expand_pydantic_args
# def get_person(person: Person) -> Person:
#    """mydocstring"""
#    from rich import print

#    print(person)


def get_person_vanilla(person: Person) -> Person:
    from rich import print

    print(person)
    return person


@expand_pydantic_args
def get_person(person: Person, thing: str = None) -> Person:
    """mydocstring"""
    from rich import print

    print(person)
    # return person


# get_person(name="me", age=1)
