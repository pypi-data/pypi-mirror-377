from __future__ import annotations

import dataclasses
from typing import *

import packaging.version
from catchlib import Catcher

from v440._utils.Base import Base
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440.core.Base_ import Base_
from v440.core.Local import Local
from v440.core.Pre import Pre
from v440.core.Qualification import Qualification
from v440.core.Release import Release
from v440.core.VersionError import VersionError


@dataclasses.dataclass(order=True)
class _Version:
    base_: Base_ = dataclasses.field(default_factory=Base_)
    qualification: Qualification = dataclasses.field(default_factory=Qualification)
    local: Local = dataclasses.field(default_factory=Local)

    def copy(self: Self) -> Self:
        return dataclasses.replace(self)

    def todict(self: Self) -> dict:
        return dataclasses.asdict(self)


class Version(Base):
    base: Self
    base_: Base_
    data: str
    dev: Optional[int]
    epoch: int
    local: Local
    post: Optional[int]
    pre: Pre
    public: Self
    qualification: Qualification
    release: Release

    def __bool__(self: Self) -> bool:
        return self._data != _Version()

    def __init__(self: Self, data: Any = "0", /, **kwargs: Any) -> None:
        object.__setattr__(self, "_data", _Version())
        self.data = data
        self.update(**kwargs)

    def __le__(self: Self, other: Any) -> bool:
        return self._data <= type(self)(other)._data

    def __setattr__(self: Self, name: str, value: Any) -> None:
        a: dict = dict()
        b: dict = dict()
        catcher: Catcher = Catcher()
        x: Any
        y: Any
        for x, y in self._data.todict().items():
            with catcher.catch(AttributeError):
                a[x] = y.data
            if catcher.caught is not None:
                b[x] = y
        try:
            Base.__setattr__(self, name, value)
        except VersionError:
            for x, y in a.items():
                getattr(self._data, x).data = y
            for x, y in b.items():
                setattr(self._data, x, y)
            raise

    def __str__(self: Self) -> str:
        return self.data

    _data_fset: Digest = Digest("_data_fset")

    @_data_fset.overload()
    def _data_fset(self: Self) -> None:
        self.public = None
        self.local = None

    @_data_fset.overload(int)
    def _data_fset(self: Self, value: int) -> None:
        self.public = value
        self.local = None

    @_data_fset.overload(str)
    def _data_fset(self: Self, value: str) -> None:
        if "+" in value:
            self.public, self.local = value.split("+", 1)
        else:
            self.public, self.local = value, None

    @property
    def base(self: Self) -> Self:
        return type(self)(str(self.base_))

    @base.setter
    def base(self: Self, value: Any) -> None:
        self.base_ = value

    @property
    def base_(self: Self) -> Base_:
        return self._data.base_

    @base_.setter
    def base_(self: Self, value: Any) -> None:
        self.base_.data = value

    def clear(self: Self) -> None:
        self.data = None

    def copy(self: Self) -> Self:
        return type(self)(self)

    @property
    def data(self: Self) -> str:
        return self.format()

    data = data.setter(_data_fset)

    @property
    def dev(self: Self) -> Optional[int]:
        return self.qualification.dev

    @dev.setter
    def dev(self: Self, value: Any) -> None:
        self.qualification.dev = value

    @property
    def epoch(self: Self) -> int:
        return self.base_.epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        self.base_.epoch = value

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        ans += str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        if self.local:
            ans += "+%s" % self.local
        return ans

    def isdevrelease(self: Self) -> bool:
        return self.qualification.isdevrelease()

    def isprerelease(self: Self) -> bool:
        return self.qualification.isprerelease()

    def ispostrelease(self: Self) -> bool:
        return self.qualification.ispostrelease()

    @property
    def local(self: Self) -> Local:
        return self._data.local

    @local.setter
    def local(self: Self, value: Any) -> None:
        self._data.local.data = value

    def packaging(self: Self) -> packaging.version.Version:
        return packaging.version.Version(str(self))

    @property
    def post(self: Self) -> Optional[int]:
        return self.qualification.post

    @post.setter
    def post(self: Self, value: Any) -> None:
        self.qualification.post = value

    @property
    def pre(self: Self) -> Pre:
        return self.qualification.pre

    @pre.setter
    def pre(self: Self, value: Any) -> None:
        self.qualification.pre = value

    _public_fset: Digest = Digest("_public_fset")

    @_public_fset.overload()
    def _public_fset(self: Self) -> None:
        self.base = None
        self.pre = None
        self.post = None
        self.dev = None

    @_public_fset.overload(int)
    def _public_fset(self: Self, value: int) -> None:
        self.base = value
        self.pre = None
        self.post = None
        self.dev = None

    @_public_fset.overload(str)
    def _public_fset(self: Self, value: str) -> None:
        match: Any = Pattern.PUBLIC.leftbound.search(value)
        self.base = value[: match.end()]
        self.qualification = value[match.end() :]

    @property
    def public(self: Self) -> Self:
        ans: Self = self.copy()
        ans.local = None
        return ans

    public = public.setter(_public_fset)

    @property
    def qualification(self: Self) -> Qualification:
        return self._data.qualification

    @qualification.setter
    def qualification(self: Self, value: Any) -> None:
        self._data.qualification.data = value

    @property
    def release(self: Self) -> Release:
        return self.base_.release

    @release.setter
    def release(self: Self, value: Any) -> None:
        self.base_.release = value

    def update(self: Self, **kwargs: Any) -> None:
        a: Any
        m: str
        x: Any
        y: Any
        for x, y in kwargs.items():
            a = getattr(type(self), x)
            if isinstance(a, property):
                setattr(self, x, y)
                continue
            m: str = "%r is not a property"
            m %= x
            raise AttributeError(m)
