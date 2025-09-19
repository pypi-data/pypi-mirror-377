from __future__ import annotations

from typing import *

import packaging.version

from v440._utils.Digest import Digest
from v440._utils.WList import WList
from v440.core.Base import Base
from v440.core.Local import Local
from v440.core.Pre import Pre
from v440.core.Public import Public
from v440.core.Qualification import Qualification
from v440.core.Release import Release

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
    if "+" in value:
        return value.split("+")
    else:
        return [value, None]


class Version(WList):
    __slots__ = ("_public", "_local")
    base: Base
    data: list
    dev: Optional[int]
    epoch: int
    local: Local
    post: Optional[int]
    pre: Pre
    public: Public
    qualification: Qualification
    release: Release

    def __init__(self: Self, data: Any = "0", /, **kwargs: Any) -> None:
        self._public = Public()
        self._local = Local()
        self.data = data
        self.update(**kwargs)

    def __str__(self: Self) -> str:
        return self.format()

    @property
    def _data(self: Self) -> tuple:
        return (self.public, self.local)

    @_data.setter
    def _data(self: Self, value: Any) -> None:
        self.public, self.local = parse_data(value)

    @property
    def base(self: Self) -> Base:
        return self.public.base

    @base.setter
    def base(self: Self, value: Any) -> None:
        self.base.data = value

    @property
    def dev(self: Self) -> Optional[int]:
        return self.qualification.dev

    @dev.setter
    def dev(self: Self, value: Any) -> None:
        self.qualification.dev = value

    @property
    def epoch(self: Self) -> int:
        return self.base.epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        self.base.epoch = value

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = self.public.format(cutoff)
        if self.local:
            ans += "+%s" % self.local
        return ans

    def isdevrelease(self: Self) -> bool:
        return self.qualification.isdevrelease()

    def isprerelease(self: Self) -> bool:
        return self.qualification.isprerelease()

    def ispostrelease(self: Self) -> bool:
        return self.qualification.ispostrelease()

    @property
    def local(self: Self) -> Local:
        return self._local

    @local.setter
    def local(self: Self, value: Any) -> None:
        self.local.data = value

    def packaging(self: Self) -> packaging.version.Version:
        return packaging.version.Version(str(self))

    @property
    def post(self: Self) -> Optional[int]:
        return self.qualification.post

    @post.setter
    def post(self: Self, value: Any) -> None:
        self.qualification.post = value

    @property
    def pre(self: Self) -> Pre:
        return self.qualification.pre

    @pre.setter
    def pre(self: Self, value: Any) -> None:
        self.qualification.pre = value

    @property
    def public(self: Self) -> Self:
        return self._public

    @public.setter
    def public(self: Self, value: Any) -> None:
        self.public.data = value

    @property
    def qualification(self: Self) -> Qualification:
        return self.public.qualification

    @qualification.setter
    def qualification(self: Self, value: Any) -> None:
        self.qualification.data = value

    @property
    def release(self: Self) -> Release:
        return self.base.release

    @release.setter
    def release(self: Self, value: Any) -> None:
        self.base.release = value

    def update(self: Self, **kwargs: Any) -> None:
        a: Any
        m: str
        x: Any
        y: Any
        for x, y in kwargs.items():
            a = getattr(type(self), x)
            if isinstance(a, property):
                setattr(self, x, y)
                continue
            m: str = "%r is not a property"
            m %= x
            raise AttributeError(m)
