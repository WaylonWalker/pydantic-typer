"""Example usage of expand_pydantic_args with the Person model.

SPDX-FileCopyrightText: 2023-present Waylon S. Walker <waylon@waylonwalker.com>

SPDX-License-Identifier: MIT
"""

import inspect

from pydantic_typer import expand_pydantic_args

from . import models

# this one is broken
# def test_no_pydantic() -> None:
#     @expand_pydantic_args()
#     def get_person(alpha) -> None:
#         """Mydocstring."""
#         from rich import print

#         print(str(thing))
#         print(person)

#     sig = inspect.signature(get_person)
#     params = sig.parameters

#     for field in models.Alpha.__fields__.values():
#         assert field.name in params


def test_single_signature() -> None:
    @expand_pydantic_args()
    def get_person(alpha: models.Alpha) -> None:
        """Mydocstring."""
        return alpha

    sig = inspect.signature(get_person)
    params = sig.parameters

    for field in models.Alpha.__fields__.values():
        assert field.name in params

    assert get_person(a=1) == models.Alpha(a=1)
