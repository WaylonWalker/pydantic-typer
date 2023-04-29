"""Models defines a set of classes for representing people and their hair.

Classes:

* `Alpha`: A class for representing an alpha value.
* `Color`: A class for representing a color.
* `Hair`: A class for representing hair.
* `Person`: A class for representing a person.

"""

from typing import Optional

from pydantic import BaseModel, Field


class Alpha(BaseModel):

    """A class for representing an alpha value."""

    a: int = Field(
        ...,
        description="The alpha value.",
    )


class Color(BaseModel):

    """A class for representing a color."""

    r: int = Field(
        ...,
        description="The red component of the color.",
    )
    g: int = Field(
        ...,
        description="The green component of the color.",
    )
    b: int = Field(
        ...,
        description="The blue component of the color.",
    )
    alpha: Alpha = Field(
        ...,
        description="The alpha value of the color.",
    )


class Hair(BaseModel):

    """A class for representing hair."""

    color: Color = Field(
        ...,
        description="The color of the hair.",
    )
    length: int = Field(
        ...,
        description="The length of the hair.",
    )


class Person(BaseModel):

    """A class for representing a person."""

    name: str = Field(
        ...,
        description="The name of the person.",
    )
    other_name: Optional[str] = Field(
        None,
        description="An optional other name for the person.",
    )
    age: int = Field(
        ...,
        description="The age of the person.",
    )
    email: Optional[str] = Field(
        None,
        description="An optional email address for the person.",
    )
    pet: str = Field(
        "dog",
        description="The person's pet.",
    )
    address: str = Field(
        "123 Main St",
        description="Where the person calls home.",
    )
    hair: Hair = Field(
        ...,
        description="The person's hair.",
    )
