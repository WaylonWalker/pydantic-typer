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
