from __future__ import annotations

import functools
from typing import *

from v440._utils import utils
from v440._utils.VList import VList

__all__ = ["Local"]


class Local(VList):

    data: list[int | str]

    def __le__(self: Self, other: Iterable) -> bool:
        "This magic method implements self<=other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except ValueError:
            ans = self.data <= other
        else:
            ans = self._cmpkey() <= alt._cmpkey()
        return ans

    def __str__(self: Self) -> str:
        "This magic method implements str(self)."
        return ".".join(map(str, self))

    def _cmpkey(self: Self) -> list:
        return list(map(self._sortkey, self))

    @staticmethod
    def _sortkey(value: Any) -> Tuple[bool, Any]:
        return type(value) is int, value

    @property
    def data(self: Self) -> list[int | str]:
        return list(self._data)

    @data.setter
    @utils.digest
    class data:
        def byInt(self: Self, value: int) -> None:
            self._data = [value]

        def byList(self: Self, value: list) -> None:
            v: list = list(map(utils.segment, value))
            if None in v:
                raise ValueError
            self._data = v

        def byNone(self: Self) -> None:
            self._data = list()

        def byStr(self: Self, value: str) -> None:
            v: str = value
            if v.startswith("+"):
                v = v[1:]
            v = v.replace("_", ".")
            v = v.replace("-", ".")
            l: list = v.split(".")
            l = list(map(utils.segment, l))
            if None in l:
                raise ValueError
            self._data = l

    @functools.wraps(VList.sort)
    def sort(self: Self, /, *, key: Any = None, **kwargs: Any) -> None:
        k: Any = self._sortkey if key is None else key
        self._data.sort(key=k, **kwargs)
