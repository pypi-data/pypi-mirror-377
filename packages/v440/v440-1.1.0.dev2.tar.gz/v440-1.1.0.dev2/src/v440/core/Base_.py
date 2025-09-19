from __future__ import annotations

from typing import *

from catchlib import Catcher
from datarepr import datarepr

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.VList import VList
from v440.core.Release import Release
from v440.core.VersionError import VersionError

__all__ = ["Base_"]


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
    v: Any = Pattern.EPOCH.bound.search(value)
    v = v.group("n")
    if v is None:
        v = 0
    else:
        v = int(v)
    return v


class Base_(VList):

    __slots__ = ("_epoch", "_release")

    data: list
    epoch: int
    release: Release

    def __init__(self: Self, data: Any = None) -> None:
        self._epoch = 0
        self._release = Release()
        self.data = data

    def __setattr__(self: Self, name: str, value: Any) -> Any:
        if name not in type(self).__annotations__.keys():
            return object.__setattr__(self, name, value)
        backup: list = utils.clone(self)
        exc: BaseException
        try:
            object.__setattr__(self, name, value)
        except BaseException as exc:
            self.data = backup
            if isinstance(exc, VersionError):
                raise
            msg: str = "%r is an invalid value for %r"
            msg %= (value, type(self).__name__ + "." + name)
            raise VersionError(msg)

    def __str__(self: Self) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += str(self.release)
        return ans

    @property
    def data(self: Self) -> list:
        return [self.epoch, self.release]

    @data.setter
    def data(self: Self, value: Any) -> None:
        self.epoch, self.release = parse_data(value)

    @property
    def epoch(self: Self) -> Optional[int]:
        return self._epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        self._epoch = parse_epoch(value)

    @property
    def release(self: Self) -> Release:
        return self._release

    @release.setter
    def release(self: Self, value: Any) -> None:
        self._release.data = value

    _data = data
