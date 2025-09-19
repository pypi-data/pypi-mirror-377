from __future__ import annotations

import operator
import string
from typing import *

from v440._utils.Digest import Digest
from v440.core.VersionError import VersionError


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
