from typing import *

from datahold import OkayList

from v440.core.VersionError import VersionError


class VList(OkayList):
    def __eq__(self: Self, other: Any) -> bool:
        "This magic method implements self==other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except VersionError:
            ans = False
        else:
            ans = self._data == alt._data
        return ans

    def __ge__(self: Self, other: Any, /) -> bool:
        "This magic method implements self>=other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except:
            ans = self.data >= other
        else:
            ans = alt <= self
        return ans

    def __iadd__(self: Self, other: Any, /) -> Self:
        "This magic method implements self+=other."
        self.data += type(self)(other).data
        return self

    def __imul__(self: Self, other: Any, /) -> Self:
        "This magic method implements self*=other."
        self.data = self.data * other
        return self

    def __init__(self: Any, data: Any = None) -> None:
        "This magic method initializes self."
        self.data = data

    def __le__(self: Self, other: Any, /) -> bool:
        "This magic method implements self<=other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except:
            ans = self.data <= other
        else:
            ans = self._data <= alt._data
        return ans

    def __setattr__(self: Self, name: str, value: Any) -> None:
        "This magic method implements setattr(self, name, value)."
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        cls: type = type(self)
        attr: Any = getattr(cls, name)
        if type(attr) is not property:
            msg: str = "%r is not a property"
            msg %= name
            raise AttributeError(msg)
        try:
            object.__setattr__(self, name, value)
        except VersionError:
            raise
        except:
            msg: str = "%r is an invalid value for %r"
            msg %= (value, cls.__name__ + "." + name)
            raise VersionError(msg)

    def __sorted__(self: Any, /, **kwargs: Any) -> Self:
        "This magic method implements sorted(self, **kwargs)."
        ans: Any = self.copy()
        ans.sort(**kwargs)
        return ans
