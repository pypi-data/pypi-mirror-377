from __future__ import annotations

import operator
import string
from typing import *

from keyalias import keyalias
from overloadable import Overloadable

from v440._utils import utils
from v440._utils.VList import VList


@keyalias(major=0, minor=1, micro=2, patch=2)
class Release(VList):
    data: list[int]
    major: int
    minor: int
    micro: int
    patch: int

    def __add__(self: Self, other: Any, /) -> Self:
        opp: Self = type(self)(other)
        ans: Self = self.copy()
        ans._data += opp._data
        return ans

    @Overloadable
    def __delitem__(self: Self, key: Any) -> bool:
        return type(key) is slice

    @__delitem__.overload(False)
    def __delitem__(self: Self, key: SupportsIndex) -> None:
        i: int = operator.index(key)
        if i < len(self):
            del self._data[i]

    @__delitem__.overload(True)
    def __delitem__(self: Self, key: Any) -> None:
        r: range = utils.torange(key, len(self))
        l: list = [k for k in r if k < len(self)]
        l.sort(reverse=True)
        for k in l:
            del self._data[k]

    @Overloadable
    def __getitem__(self: Self, key: Any) -> bool:
        return type(key) is slice

    @__getitem__.overload(False)
    def __getitem__(self: Self, key: Any) -> int:
        i: int = operator.index(key)
        ans: int = self._getitem_int(i)
        return ans

    @__getitem__.overload(True)
    def __getitem__(self: Self, key: Any) -> list:
        r: range = utils.torange(key, len(self))
        m: map = map(self._getitem_int, r)
        ans: list = list(m)
        return ans

    @Overloadable
    def __setitem__(self: Self, key: Any, value: Any) -> bool:
        return type(key) is slice

    @__setitem__.overload(False)
    def __setitem__(self: Self, key: SupportsIndex, value: Any) -> Any:
        i: int = operator.index(key)
        self._setitem_int(i, value)

    @__setitem__.overload(True)
    def __setitem__(self: Self, key: SupportsIndex, value: Any) -> Any:
        k: range = utils.torange(key, len(self))
        self._setitem_range(k, value)

    def __str__(self: Self) -> str:
        return self.format()

    def _getitem_int(self: Self, key: int) -> int:
        if key < len(self):
            return self._data[key]
        else:
            return 0

    def _setitem_int(self: Self, key: int, value: Any) -> Any:
        v: int = utils.numeral(value)
        n: int = len(self)
        if n > key:
            self._data[key] = v
            return
        if v == 0:
            return
        self._data.extend([0] * (key - n))
        self._data.append(v)

    @Overloadable
    def _setitem_range(self: Self, key: range, value: Any) -> bool:
        return key.step == 1

    @_setitem_range.overload(False)
    def _setitem_range(self: Self, key: range, value: Any) -> Any:
        key = list(key)
        value = self._tolist(value, slicing=len(key))
        if len(key) != len(value):
            e = "attempt to assign sequence of size %s to extended slice of size %s"
            e %= (len(value), len(key))
            raise ValueError(e)
        maximum = max(*key)
        ext = max(0, maximum + 1 - len(self))
        data = self.data
        data += [0] * ext
        for k, v in zip(key, value):
            data[k] = v
        while len(data) and not data[-1]:
            data.pop()
        self._data = data

    @_setitem_range.overload(True)
    def _setitem_range(self: Self, key: range, value: Any) -> Any:
        data: list = self.data
        ext: int = max(0, key.start - len(data))
        data += ext * [0]
        l: list = self._tolist(value, slicing="always")
        data = data[: key.start] + l + data[key.stop :]
        while len(data) and not data[-1]:
            data.pop()
        self._data = data

    @Overloadable
    @staticmethod
    def _tolist(value: Any, *, slicing: Any) -> list:
        if value is None:
            return
        if isinstance(value, int):
            return int
        if hasattr(value, "__iter__") and not isinstance(value, str):
            return list
        return str

    @_tolist.overload()
    def _tolist(value: None, *, slicing: Any) -> list:
        return list()

    @_tolist.overload(int)
    def _tolist(value: int, *, slicing: Any) -> list:
        return [utils.numeral(value)]

    @_tolist.overload(list)
    def _tolist(value: int, *, slicing: Any) -> list:
        return list(map(utils.numeral, value))

    @_tolist.overload(str)
    def _tolist(value: Any, *, slicing: Any) -> list:
        s: Any
        if isinstance(value, str):
            s = slicing
        else:
            s = "never"
        v: str = str(value)
        if v == "":
            return list()
        if "" == v.strip(string.digits) and s in (len(v), "always"):
            return list(map(int, v))
        v = v.lower().strip()
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        if v.startswith("v") or v.startswith("."):
            v = v[1:]
        l: list = v.split(".")
        if "" in l:
            raise ValueError
        l = list(map(utils.numeral, l))
        return l

    def bump(self: Self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        i: int = operator.index(index)
        a: int = operator.index(amount)
        x: int = self._getitem_int(i) + a
        self._setitem_int(i, x)
        if i != -1:
            self.data = self.data[: i + 1]

    @property
    def data(self: Self) -> list:
        return list(self._data)

    @data.setter
    def data(self: Self, value: Any) -> None:
        v: list = self._tolist(value, slicing="always")
        while v and v[-1] == 0:
            v.pop()
        self._data = v

    def format(self: Self, cutoff: Any = None) -> str:
        s: str = str(cutoff) if cutoff else ""
        i: Optional[int] = int(s) if s else None
        l: list = self[:i]
        if len(l) == 0:
            l += [0]
        l = list(map(str, l))
        ans: str = ".".join(l)
        return ans
