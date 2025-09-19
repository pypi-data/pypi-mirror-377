from typing import *

from v440._utils.VList import VList

__all__ = ["WList"]


class WList(VList):
    @property
    def data(self: Self) -> list:
        return list(self._data)

    @data.setter
    def data(self: Self, value: Any) -> None:
        self._data = value
