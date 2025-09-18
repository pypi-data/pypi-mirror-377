from __future__ import annotations

import dataclasses
from typing import *

from v440._utils import utils
from v440._utils.Pattern import Pattern


class QualifierParser: ...


@dataclasses.dataclass(frozen=True)
class SimpleQualifierParser(QualifierParser):
    keysforlist: tuple = ()
    keysforstr: tuple = ()
    allow_len_1: bool = False

    __call__ = utils.Digest("__call__")

    @__call__.overload()
    def __call__(self: Self) -> Optional[list]:
        pass

    @__call__.overload(int)
    def __call__(self: Self, value: int) -> Any:
        if value < 0:
            raise ValueError
        return value

    @__call__.overload(list)
    def __call__(self: Self, value: list) -> Any:
        v: list = list(map(utils.segment, value))
        n = self.nbylist(v)
        if isinstance(n, str):
            raise TypeError
        return n

    @__call__.overload(str)
    def __call__(self: Self, value: str) -> Optional[int | list]:
        v: str = value
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        m: Any = Pattern.PARSER.bound.search(v)
        l, n = m.groups()
        if l not in self.keysforstr:
            raise ValueError
        if n is None:
            return None
        else:
            return int(n)

    def __post_init__(self: Self) -> None:
        if type(self.allow_len_1) is not bool:
            raise TypeError
        if type(self.keysforlist) is not tuple:
            raise TypeError
        if type(self.keysforstr) is not tuple:
            raise TypeError
        keys = self.keysforlist + self.keysforstr
        for k in keys:
            if k is None:
                continue
            if type(k) is str:
                continue
            raise TypeError

    def nbylist(self: Self, value: Any, /) -> Any:
        if len(value) == 2:
            l, n = value
            if l not in self.keysforlist:
                raise ValueError
            return n
        if len(value) == 1:
            n = value[0]
            if not self.allow_len_1:
                raise ValueError
            return n
        raise ValueError


class PhasedQualifierParser(QualifierParser):
    __slots__ = ("_phasedict",)

    phasedict: dict

    __call__ = utils.Digest("__call__")

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


POST = SimpleQualifierParser(
    keysforlist=("post", "rev", "r", ""),
    keysforstr=(None, "post", "rev", "r"),
    allow_len_1=True,
)
DEV = SimpleQualifierParser(
    keysforlist=("dev",),
    keysforstr=(None, "dev"),
)
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
