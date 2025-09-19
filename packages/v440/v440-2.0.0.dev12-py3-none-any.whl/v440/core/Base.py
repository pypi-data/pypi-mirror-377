from __future__ import annotations

from typing import *

from v440._utils.Digest import Digest
from v440._utils.WList import WList
from v440.core.Release import Release

__all__ = ["Base"]


parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> list:
    return [None, None]


@parse_data.overload(int)
def parse_data(value: int) -> list:
    return [None, value]


@parse_data.overload(list)
def parse_data(value: list) -> list:
    return value


@parse_data.overload(str)
def parse_data(value: str) -> list:
    if "!" in value:
        return value.split("!")
    else:
        return [0, value]


parse_epoch: Digest = Digest("parse_epoch")


@parse_epoch.overload()
def parse_epoch() -> int:
    return 0


@parse_epoch.overload(int)
def parse_epoch(value: int) -> int:
    if value < 0:
        raise ValueError
    return value


@parse_epoch.overload(str)
def parse_epoch(value: str) -> int:
    s: str = value
    if s.endswith("!"):
        s = s[:-1]
    if s == "":
        return 0
    ans: int = int(s)
    if ans < 0:
        raise ValueError
    return ans


class Base(WList):

    __slots__ = ("_epoch", "_release")

    data: list
    epoch: int
    release: Release

    def __init__(self: Self, data: Any = None) -> None:
        self._epoch = 0
        self._release = Release()
        self.data = data

    def __str__(self: Self) -> str:
        return self.format()

    @property
    def _data(self: Self) -> tuple:
        return self.epoch, self.release

    @_data.setter
    def _data(self: Self, value: Any) -> None:
        self.epoch, self.release = parse_data(value)

    @property
    def epoch(self: Self) -> Optional[int]:
        return self._epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        self._epoch = parse_epoch(value)

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        return ans

    @property
    def release(self: Self) -> Release:
        return self._release

    @release.setter
    def release(self: Self, value: Any) -> None:
        self._release.data = value
