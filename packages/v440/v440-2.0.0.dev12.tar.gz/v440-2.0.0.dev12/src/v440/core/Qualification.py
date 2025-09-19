from __future__ import annotations

from typing import *

from v440._utils import SimpleQualifierParser
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.WList import WList
from v440.core.Pre import Pre

__all__ = ["Qualification"]


parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> list:
    return [None, None, None]


@parse_data.overload(int)
def parse_data(value: int) -> list:
    return [None, abs(value), None]


@parse_data.overload(list)
def parse_data(value: list) -> list:
    return value


@parse_data.overload(str)
def parse_data(value: str) -> list:
    v = value
    pre: Any = None
    post: Any = None
    dev: Any = None
    m: Any
    x: Any
    y: Any
    while v:
        m = Pattern.QUALIFIERS.leftbound.search(v)
        v = v[m.end() :]
        if m.group("N"):
            post = m.group("N")
            continue
        x = m.group("l")
        y = m.group("n")
        if x == "dev":
            dev = y
            continue
        if x in ("post", "r", "rev"):
            post = y
            continue
        pre = (x, y)
    return [pre, post, dev]


class Qualification(WList):

    __slots__ = ("_pre", "_post", "_dev")

    data: list
    pre: Pre
    post: Optional[int]
    dev: Optional[int]

    def __init__(self: Self, data: Any = None) -> None:
        self._pre = Pre()
        self._post = None
        self._dev = None
        self.data = data

    def __le__(self: Self, other: Any) -> bool:
        return self._cmpkey() <= type(self)(other)._cmpkey()

    def __str__(self: Self) -> str:
        ans: str = str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

    def _cmpkey(self: Self) -> tuple:
        ans = self.data
        if not ans[0].isempty():
            ans[0] = tuple(ans[0])
        elif ans[1] is not None:
            ans[0] = "z", float("inf")
        elif ans[2] is None:
            ans[0] = "z", float("inf")
        else:
            ans[0] = "", -1
        if ans[1] is None:
            ans[1] = -1
        if ans[2] is None:
            ans[2] = float("inf")
        return ans

    @property
    def _data(self: Self) -> tuple:
        return self.pre, self.post, self.dev

    @_data.setter
    def _data(self: Self, value: Any) -> None:
        self.pre, self.post, self.dev = parse_data(value)

    @property
    def dev(self: Self) -> Optional[int]:
        return self._dev

    @dev.setter
    def dev(self: Self, value: Any) -> None:
        self._dev = SimpleQualifierParser.DEV(value)

    def isdevrelease(self: Self) -> bool:
        return self.dev is not None

    def isempty(self: Self) -> bool:
        return self.data == [None, None, None]

    def isprerelease(self: Self) -> bool:
        return self.isdevrelease() or not self.pre.isempty()

    def ispostrelease(self: Self) -> bool:
        return self.post is not None

    @property
    def post(self: Self) -> Optional[int]:
        return self._post

    @post.setter
    def post(self: Self, value: Any) -> None:
        self._post = SimpleQualifierParser.POST(value)

    @property
    def pre(self: Self) -> Pre:
        return self._pre

    @pre.setter
    def pre(self: Self, value: Any) -> None:
        self._pre.data = value
