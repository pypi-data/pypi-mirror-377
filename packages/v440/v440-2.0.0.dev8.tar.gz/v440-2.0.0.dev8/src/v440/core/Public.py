from __future__ import annotations

from typing import *

from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.WList import WList
from v440.core.Base import Base
from v440.core.Qualification import Qualification

__all__ = ["Public"]


parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> list:
    return [None, None]


@parse_data.overload(int)
def parse_data(value: int) -> list:
    return [value, None]


@parse_data.overload(list)
def parse_data(value: list) -> list:
    return value


@parse_data.overload(str)
def parse_data(value: str) -> list:
    match: Any = Pattern.PUBLIC.leftbound.search(value)
    return value[: match.end()], value[match.end() :]


class Public(WList):

    __slots__ = ("_base", "_qualification")

    data: list
    base: Base
    qualification: Qualification

    def __init__(self: Self, data: Any = None) -> None:
        self._base = Base()
        self._qualification = Qualification()
        self.data = data

    def __str__(self: Self) -> str:
        return self.format()

    @property
    def base(self: Self) -> Base:
        return self._base

    @base.setter
    def base(self: Self, value: Any) -> None:
        self.base.data = value

    @property
    def data(self: Self) -> list:
        return [self.base, self.qualification]

    @data.setter
    def data(self: Self, value: Any) -> None:
        self.base, self.qualification = parse_data(value)

    def format(self: Self, cutoff: Any = None) -> str:
        return self.base.format(cutoff) + str(self.qualification)

    @property
    def qualification(self: Self) -> Qualification:
        return self._qualification

    @qualification.setter
    def qualification(self: Self, value: Any) -> None:
        self.qualification.data = value

    _data = data
