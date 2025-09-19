from __future__ import annotations

import dataclasses
from typing import *

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern

__all__ = ["SimpleQualifierParser"]


@dataclasses.dataclass(frozen=True)
class SimpleQualifierParser:
    keysforlist: tuple = ()
    keysforstr: tuple = ()
    allow_len_1: bool = False

    __call__ = Digest("__call__")

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


POST = SimpleQualifierParser(
    keysforlist=("post", "rev", "r", ""),
    keysforstr=(None, "post", "rev", "r"),
    allow_len_1=True,
)
DEV = SimpleQualifierParser(
    keysforlist=("dev",),
    keysforstr=(None, "dev"),
)
