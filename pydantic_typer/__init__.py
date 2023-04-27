# SPDX-FileCopyrightText: 2023-present Waylon S. Walker <waylon@waylonwalker.com>
##
# SPDX-License-Identifier: MIT

from functools import wraps
import inspect
from typing import Callable, Optional

from pydantic import BaseModel


class Person(BaseModel):
    name: str
    age: int
    email: Optional[str]
    pet: str = "dog"


def make_person(name: str, age: int) -> Person:
    return Person(name=name, age=age)


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

    sig = inspect.signature(func)
    more_args = []
    for name, param in sig.parameters.items():
        if hasattr(param.annotation, "__fields__"):
            more_args.extend(param.annotation.__fields__)

    wrapper.__doc__ = (
        func.__doc__ + f"\nalso accepts {more_args} in place of person model"
    )
    fields = Person.__fields__
    args = ",".join(
        [
            f"{name}: {field.annotation.__name__ if str(field.annotation).startswith('<') else str(field.annotation)}=            '{field.default}'"
            for name, field in fields.items()
        ]
    )
    call_args = ",".join([f"{name}={name}" for name, field in fields.items()])

    new_func = f"""
import typing
def {func.__name__}({args}):
    '''{func.__doc__}'''
    return wrapper({call_args})
    """
    exec(new_func, locals(), globals())
    # return outter

    return globals()[func.__name__]


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
