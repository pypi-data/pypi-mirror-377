from __future__ import annotations

from typing import *

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern

__all__ = ["PhasedQualifierParser"]


class PhasedQualifierParser:
    __slots__ = ("_phasedict",)

    phasedict: dict

    __call__ = Digest("__call__")

    @__call__.overload()
    def __call__(self: Self) -> list:
        return [None, None]

    @__call__.overload(list)
    def __call__(self: Self, value: list) -> Any:
        l: Any
        n: Any
        l, n = list(map(utils.segment, value))
        if [l, n] == [None, None]:
            return [None, None]
        l = self.phasedict[l]
        if not isinstance(n, int):
            raise TypeError
        return [l, n]

    @__call__.overload(str)
    def __call__(self: Self, value: str) -> list:
        if value == "":
            return [None, None]
        v: str = value
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        m: Any = Pattern.PARSER.bound.search(v)
        l: Any
        n: Any
        l, n = m.groups()
        l = self.phasedict[l]
        n = 0 if (n is None) else int(n)
        return [l, n]

    def __init__(self: Self, **kwargs: Any) -> None:
        self._phasedict = dict()
        x: Any
        y: Any
        for x, y in kwargs.items():
            self._phasedict[str(x)] = str(y)

    def nbylist(self: Self, value: Any, /) -> Any:
        raise ValueError

    @property
    def phasedict(self: Self) -> dict:
        return dict(self._phasedict)


PRE = PhasedQualifierParser(
    alpha="a",
    a="a",
    beta="b",
    b="b",
    preview="rc",
    pre="rc",
    c="rc",
    rc="rc",
)
