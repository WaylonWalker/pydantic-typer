# SPDX-FileCopyrightText: 2023-present Waylon S. Walker <waylon@waylonwalker.com>
##
# SPDX-License-Identifier: MIT

from functools import wraps
import inspect
from typing import Callable, Optional

from pydantic import BaseModel, Field
import typer

__all__ = ["typer"]


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


def make_annotation(name, field, names):
    panel_name = names[name]
    next_name = panel_name
    while next_name is not None:
        next_name = names.get(next_name)
        if next_name is not None:
            panel_name = f"{next_name}.{panel_name}"

    annotation = (
        field.annotation.__name__
        if str(field.annotation).startswith("<")
        else str(field.annotation)
    )

    if field.default is None and not field.required:
        default = "None"
        default = f' = typer.Option(None, help="{field.field_info.description or ""}", rich_help_panel="{panel_name}")'
    elif field.default is not None:
        default = f'"{field.default}"'
        default = f' = typer.Option("{field.default}", help="{field.field_info.description or ""}", rich_help_panel="{panel_name}")'
    else:
        default = ""
        default = f' = typer.Option(..., help="{field.field_info.description or ""}", rich_help_panel="{panel_name}", prompt=True)'

    #  if not typer
    # return f"{name}: {annotation}{default}"
    return f"{name}: {annotation}{default}"


def make_signature(func, wrapper, more_args={}):
    sig = inspect.signature(func)
    names = {}
    for name, param in sig.parameters.items():
        if hasattr(param.annotation, "__fields__"):
            more_args = {**more_args, **param.annotation.__fields__}
            for field in param.annotation.__fields__:
                names[field] = param.annotation.__name__

    while any(
        [hasattr(param.annotation, "__fields__") for name, param in more_args.items()]
    ):
        keys_to_remove = []
        for name, param in more_args.items():
            if hasattr(param.annotation, "__fields__"):
                # model parent lookup
                names[param.annotation.__name__] = names[name]

                if name not in param.annotation.__fields__.keys():
                    keys_to_remove.append(name)
                more_args = {**more_args, **param.annotation.__fields__}
                # names[name] = param.annotation.__name__
                for field in param.annotation.__fields__:
                    names[field] = param.annotation.__name__

        for key in keys_to_remove:
            del more_args[key]

    wrapper.__doc__ = (
        func.__doc__ or ""
    ) + f"\nalso accepts {more_args.keys()} in place of person model"
    # fields = Person.__fields__
    raw_args = [
        make_annotation(name, field, names) for name, field in more_args.items()
    ]
    aargs = ", ".join([arg for arg in raw_args if "=" not in arg])
    kwargs = ", ".join([arg for arg in raw_args if "=" in arg])

    call_args = ",".join([f"{name}={name}" for name, field in more_args.items()])

    new_func_str = f"""
import typing
def {func.__name__}({aargs}{', ' if aargs else ''}{kwargs}):
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
    exec(new_func_str, locals(), globals())
    new_func = globals()[func.__name__]

    sig = inspect.signature(new_func)
    for name, param in sig.parameters.items():
        if hasattr(param.annotation, "__fields__"):
            return make_signature(new_func, wrapper, more_args=more_args)
    return new_func


def _expand_param(param, kwargs, models=None):
    models = {}
    for field_name, field in param.annotation.__fields__.items():
        if hasattr(field.annotation, "__fields__"):
            models[field_name] = _expand_param(field, kwargs, models)
    return param.annotation(**kwargs, **models)


def _expand_kwargs(func, kwargs):
    sig = inspect.signature(func)
    updated_kwargs = {}
    for name, value in kwargs.items():
        if name in sig.parameters:
            updated_kwargs[name] = value

    for name, param in sig.parameters.items():
        # func wants this directly
        # this should check isinstance, but it's not working
        if name in kwargs and repr(param.annotation) == repr(kwargs[name]):
            updated_kwargs[name] = kwargs[name]

        # an instance was not passed in, create one with kwargs passed in
        elif hasattr(param.annotation, "__fields__"):
            updated_kwargs[name] = _expand_param(param, kwargs)
        # its something else so pass it
        else:
            updated_kwargs[name] = kwargs[name]
    return updated_kwargs


def expand_pydantic_args(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):

        return func(**_expand_kwargs(func, kwargs))

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
