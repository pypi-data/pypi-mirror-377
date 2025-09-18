from __future__ import annotations

import functools
import operator
import string
import types
from typing import *

from v440.core.VersionError import VersionError


class Digest:
    __slots__ = ("lookup", "name")
    lookup: dict
    name: str

    def __call__(self: Self, *args: Any, **kwargs: Any) -> Any:
        "This magic method implements self(*args, **kwargs)."
        args0: list = list(args)
        value: Any = args0.pop()
        key: Any = self._getkey(value)
        if key is int:
            args0.append(int(value))
        if key is str:
            args0.append(str(value).lower().strip())
        if key is list:
            args0.append(list(value))
        ans: Any = self.lookup[key](*args0, **kwargs)
        return ans

    def __get__(
        self: Self,
        *args: Any,
        **kwargs: Any,
    ) -> types.FunctionType | types.MethodType:
        "This magic method implements getting as an attribute from a class or an object."

        def new(*args_: Any, **kwargs_: Any) -> Any:
            return self(*args_, **kwargs_)

        new.__name__ = self.name
        ans: Any = new.__get__(*args, **kwargs)
        return ans

    def __init__(self: Self, name: str) -> None:
        "This magic method sets up self."
        self.lookup = dict()
        self.name = name

    @classmethod
    def _getkey(cls: type, value: Any) -> Any:
        if value is None:
            return
        if isinstance(value, int):
            return int
        if isinstance(value, str):
            return str
        try:
            value.__iter__
        except AttributeError:
            return str
        else:
            return list

    def _overload(self: Self, key: Any, value: Any) -> Self:
        self.lookup[key] = value
        overload(value)
        return self

    def overload(self: Self, key: Any = None) -> functools.partial:
        return functools.partial(type(self)._overload, self, key)


def literal(value: Any, /) -> str:
    v: Any = segment(value)
    if type(v) is str:
        return v
    e: str = "%r is not a valid literal segment"
    e %= v
    raise VersionError(e)


def numeral(value: Any, /) -> int:
    v: Any = segment(value)
    if type(v) is int:
        return v
    e = "%r is not a valid numeral segment"
    e %= v
    raise VersionError(e)


def segment(value: Any, /) -> Any:
    try:
        return _segment(value)
    except:
        e = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e from None


_segment: Digest = Digest("_segment")


@_segment.overload()
def _segment():
    return


@_segment.overload(int)
def byInt(value: int, /) -> Any:
    if value < 0:
        raise ValueError
    return value


@_segment.overload(str)
def _segment(value: Any, /) -> int | str:
    if value.strip(string.ascii_lowercase + string.digits):
        raise ValueError(value)
    if value.strip(string.digits):
        return value
    elif value == "":
        return 0
    else:
        return int(value)


def torange(key: Any, length: Any) -> range:
    start: Any = key.start
    stop: Any = key.stop
    step: Any = key.step
    if step is None:
        step = 1
    else:
        step = operator.index(step)
        if step == 0:
            raise ValueError
    fwd: bool = step > 0
    if start is None:
        start = 0 if fwd else (length - 1)
    else:
        start = operator.index(start)
    if stop is None:
        stop = length if fwd else -1
    else:
        stop = operator.index(stop)
    if start < 0:
        start += length
    if start < 0:
        start = 0 if fwd else -1
    if stop < 0:
        stop += length
    if stop < 0:
        stop = 0 if fwd else -1
    ans: range = range(start, stop, step)
    return ans
