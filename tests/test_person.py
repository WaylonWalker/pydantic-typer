"""Example usage of expand_pydantic_args with the Person model.

SPDX-FileCopyrightText: 2023-present Waylon S. Walker <waylon@waylonwalker.com>

SPDX-License-Identifier: MIT
"""

import inspect

import pytest

from pydantic_typer import expand_pydantic_args

from . import models

# this one is broken
# def test_no_pydantic() -> None:
#     @expand_pydantic_args()
#     def get_person(alpha) -> None:
#         """Mydocstring."""


def test_single_signature() -> None:
    @expand_pydantic_args()
    def get_person(alpha: models.Alpha) -> None:
        """Mydocstring."""
        return alpha

    sig = inspect.signature(get_person)
    params = sig.parameters
    assert "a" in params

    assert "alpha" not in params


@pytest.mark.parametrize(
    "alpha",
    models.AlphaFactory().batch(size=5),
)
def test_single_instance(alpha: models.Alpha) -> None:
    @expand_pydantic_args()
    def get_person(alpha: models.Alpha) -> None:
        """Mydocstring."""
        return alpha

    assert get_person(**alpha.dict()) == alpha
    # this should maybe work
    # assert get_person(models.Alpha(a=1)) == models.Alpha(a=1)


def test_one_nest_signature() -> None:
    @expand_pydantic_args()
    def get_person(color: models.Color) -> None:
        """Mydocstring."""
        return color

    sig = inspect.signature(get_person)
    params = sig.parameters
    assert "r" in params
    assert "g" in params
    assert "b" in params
    assert "a" in params

    assert "color" not in params
    assert "alpha" not in params


@pytest.mark.parametrize(
    "color",
    models.ColorFactory().batch(size=5),
)
def test_one_nest_instance(color: models.Color) -> None:
    @expand_pydantic_args()
    def get_person(color: models.Color) -> None:
        """Mydocstring."""
        return color

    assert get_person(**color.dict(exclude={"alpha"}), **color.alpha.dict()) == color


def test_two_nest_signature() -> None:
    @expand_pydantic_args()
    def get_person(hair: models.Hair) -> None:
        """Mydocstring."""
        return hair

    sig = inspect.signature(get_person)
    params = sig.parameters
    assert "length" in params
    assert "r" in params
    assert "g" in params
    assert "b" in params
    assert "a" in params

    assert "hair" not in params
    assert "color" not in params
    assert "alpha" not in params


@pytest.mark.parametrize(
    "hair",
    models.HairFactory().batch(size=5),
)
def test_two_nest_instance(hair: models.Hair) -> None:
    @expand_pydantic_args()
    def get_person(hair: models.Hair) -> None:
        """Mydocstring."""
        return hair

    assert (
        get_person(
            **hair.dict(exclude={"color"}),
            **hair.color.dict(exclude={"alpha"}),
            **hair.color.alpha.dict()
        ) ==
        hair
    )


def test_three_nest_signature() -> None:
    @expand_pydantic_args()
    def get_person(person: models.Person) -> None:
        """Mydocstring."""
        return person

    sig = inspect.signature(get_person)
    params = sig.parameters
    assert "name" in params
    assert "alias" in params
    assert "age" in params
    assert "email" in params
    assert "pet" in params
    assert "address" in params
    assert "length" in params
    assert "r" in params
    assert "g" in params
    assert "b" in params
    assert "a" in params

    assert "person" not in params
    assert "hair" not in params
    assert "color" not in params
    assert "alpha" not in params


@pytest.mark.parametrize(
    "person",
    models.PersonFactory().batch(size=5),
)
def test_three_nest_instance(person: models.Person) -> None:
    @expand_pydantic_args()
    def get_person(person: models.Person) -> None:
        """Mydocstring."""
        return person

    assert (
        get_person(
            **person.dict(exclude={"hair"}),
            **person.hair.dict(exclude={"color"}),
            **person.hair.color.dict(exclude={"alpha"}),
            **person.hair.color.alpha.dict()
        ) ==
        person
    )
