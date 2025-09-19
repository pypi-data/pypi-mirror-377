from __future__ import annotations

from typing import *

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern

__all__ = ["PRE"]

PHASEDICT: dict = dict(
    alpha="a",
    a="a",
    beta="b",
    b="b",
    preview="rc",
    pre="rc",
    c="rc",
    rc="rc",
)


PRE = Digest("PRE")


@PRE.overload()
def PRE() -> list:
    return [None, None]


@PRE.overload(list)
def PRE(value: list) -> Any:
    l: Any
    n: Any
    l, n = list(map(utils.segment, value))
    if [l, n] == [None, None]:
        return [None, None]
    l = PHASEDICT[l]
    if not isinstance(n, int):
        raise TypeError
    return [l, n]


@PRE.overload(str)
def PRE(value: str) -> list:
    if value == "":
        return [None, None]
    v: str = value
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    l: Any
    n: Any
    l, n = m.groups()
    l = PHASEDICT[l]
    n = 0 if (n is None) else int(n)
    return [l, n]
