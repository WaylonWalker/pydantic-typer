"""pydantic_typer.

SPDX-FileCopyrightText: 2023-present Waylon S. Walker <waylon@waylonwalker.com>

SPDX-License-Identifier: MIT
"""
import inspect
from functools import wraps
from typing import Any, Callable, Dict, Optional

import typer
from pydantic.fields import ModelField

__all__ = ["typer"]


def _make_annotation(
    name: str,
    field: ModelField,
    names: Dict[str, str],
    *,
    typer: bool = False,
) -> str:
    panel_name = names.get(name)
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

    if "=" not in repr(field) and not hasattr(field, "required"):
        default = "=None"
    elif not hasattr(field, "required"):
        default = f'="{field.default}"'
    elif field.default is None and not getattr(field, "required", False):
        if typer:
            default = f' = typer.Option(None, help="{field.field_info.description or ""}", rich_help_panel="{panel_name}")'
        else:
            default = "=None"
    elif field.default is not None:
        if typer:
            default = f' = typer.Option("{field.default}", help="{field.field_info.description or ""}", rich_help_panel="{panel_name}")'
        else:
            default = f'="{field.default}"'
    elif typer:
        default = f' = typer.Option(..., help="{field.field_info.description or ""}", rich_help_panel="{panel_name}", prompt=True)'
    else:
        default = ""
    if typer:
        return f"{name}: {annotation}{default}"
    return f"{name}: {annotation}{default}"


def _make_signature(
    func: Callable,
    wrapper: Callable,
    *,
    typer: bool = False,
    more_args: Optional[Dict] = None,
):
    if more_args is None:
        more_args = {}
    sig = inspect.signature(func)
    names = {}
    for name, param in sig.parameters.items():
        if hasattr(param.annotation, "__fields__"):
            more_args = {**more_args, **param.annotation.__fields__}
            for field in param.annotation.__fields__:
                names[field] = param.annotation.__name__
        else:
            more_args[name] = param

    while any(
        hasattr(param.annotation, "__fields__") for name, param in more_args.items()
    ):
        keys_to_remove = []
        for name, param in more_args.items():
            if hasattr(param.annotation, "__fields__"):
                # model parent lookup
                names[param.annotation.__name__] = names[name]

                if name not in param.annotation.__fields__.keys():
                    keys_to_remove.append(name)
                more_args = {**more_args, **param.annotation.__fields__}
                for field in param.annotation.__fields__:
                    names[field] = param.annotation.__name__

        for key in keys_to_remove:
            del more_args[key]

    wrapper.__doc__ = (
        func.__doc__ or ""
    ) + f"\nalso accepts {more_args.keys()} in place of person model"
    raw_args = [
        _make_annotation(
            name,
            field,
            names=names,
            typer=typer,
        )
        for name, field in more_args.items()
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
    exec(new_func_str, locals(), globals())  # noqa: S102
    new_func = globals()[func.__name__]

    sig = inspect.signature(new_func)
    for param in sig.parameters.values():
        if hasattr(param.annotation, "__fields__"):
            return _make_signature(new_func, wrapper, typer=typer, more_args=more_args)
    return new_func


def _expand_param(
    param: inspect.Parameter,
    kwargs: Dict[str, Any],
    models: Optional[Dict[str, str]] = None,
) -> Any:
    """Further expands params with a Pydantic annotation, given a param.

    Recursively creates an instance of any param.annotation that has __fields__
    using the expanded kwargs.y:
    using the expanded kwargs.
    """
    models = {}
    for field_name, field in param.annotation.__fields__.items():
        if hasattr(field.annotation, "__fields__"):
            models[field_name] = _expand_param(field, kwargs, models)
    return param.annotation(**kwargs, **models)


def _expand_kwargs(func: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Expand kwargs with Pydantic annotations given a function.

    Inspects the arguments of the func and expands any of the kwargs with a
    Pydantic annotation, to add its fields to the kwargs.
    """
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
    return updated_kwargs


def expand_pydantic_args(*, typer: bool = False) -> Callable:
    """Expand Pydantic keyword arguments.

    Decorator function to expand arguments of pydantic models to accept the
    individual fields of Models.
    """

    def decorator(func: Callable) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **_expand_kwargs(func, kwargs))

        return _make_signature(func, wrapper, typer=typer)

    return decorator
