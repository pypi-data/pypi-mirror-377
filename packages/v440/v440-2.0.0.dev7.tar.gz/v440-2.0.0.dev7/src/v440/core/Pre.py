from __future__ import annotations

from typing import *

import keyalias

from v440._utils import PhasedQualifierParser
from v440._utils.WList import WList

__all__ = ["Pre"]


@keyalias.keyalias(phase=0, subphase=1)
class Pre(WList):

    __slots__ = ("_phase", "_subphase")

    data: list
    phase: Any
    subphase: Any

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
    def data(self: Self) -> list:
        return [self._phase, self._subphase]

    @data.setter
    def data(self: Self, value: Any) -> None:
        self._phase, self._subphase = PhasedQualifierParser.PRE(value)

    def isempty(self: Self) -> bool:
        return self._data == [None, None]

    _data = data
