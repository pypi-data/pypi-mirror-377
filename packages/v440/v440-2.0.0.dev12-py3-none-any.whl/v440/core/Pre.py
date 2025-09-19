from __future__ import annotations

from typing import *

import keyalias

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.WList import WList

__all__ = ["Pre"]


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


parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> list:
    return [None, None]


@parse_data.overload(list)
def parse_data(value: list) -> Any:
    l: Any
    n: Any
    l, n = list(map(utils.segment, value))
    if [l, n] == [None, None]:
        return [None, None]
    l = PHASEDICT[l]
    if not isinstance(n, int):
        raise TypeError
    return [l, n]


@parse_data.overload(str)
def parse_data(value: str) -> list:
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


@keyalias.keyalias(phase=0, subphase=1)
class Pre(WList):

    __slots__ = ("_phase", "_subphase")

    data: list
    phase: Optional[str]
    subphase: Optional[int]

    def __init__(self: Self, data: Any = None) -> None:
        self._phase = None
        self._subphase = None
        self.data = data

    def __str__(self: Self) -> str:
        ans: str = ""
        if not self.isempty():
            ans += self.phase
            ans += str(self.subphase)
        return ans

    @property
    def _data(self: Self) -> tuple:
        return self._phase, self._subphase

    @_data.setter
    def _data(self: Self, value: Any) -> None:
        self._phase, self._subphase = parse_data(value)

    def isempty(self: Self) -> bool:
        return set(self._data) == {None}
