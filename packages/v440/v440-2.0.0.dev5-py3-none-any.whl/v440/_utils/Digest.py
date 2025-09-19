from __future__ import annotations

import functools
import types
from typing import *


class Digest:
    __slots__ = ("__dict__", "lookup", "name", "kind")
    lookup: dict
    name: str
    kind: Any

    def __call__(self: Self, *args: Any, **kwargs: Any) -> Any:
        "This magic method implements self(*args, **kwargs)."
        return self.wrapped(*args, **kwargs)

    def __get__(
        self: Self,
        *args: Any,
        **kwargs: Any,
    ) -> types.FunctionType | types.MethodType:
        "This magic method implements getting as an attribute from a class or an object."
        return self.wrapped.__get__(*args, **kwargs)

    def __init__(
        self: Self,
        name: str = "",
        kind: Any = None,
    ) -> None:
        "This magic method sets up self."
        self.lookup = dict()
        self.name = name
        self.kind = kind

    @classmethod
    def _getkey(cls: type, value: Any) -> Any:
        if value is None:
            return
        if isinstance(value, int):
            return int
        if isinstance(value, str):
            return str
        try:
            value.__iter__
        except AttributeError:
            return str
        else:
            return list

    def _overload(self: Self, key: Any, value: Any) -> Self:
        self.lookup[key] = value
        overload(value)
        return self

    def overload(self: Self, key: Any = None) -> functools.partial:
        return functools.partial(type(self)._overload, self, key)

    @functools.cached_property
    def wrapped(self: Self) -> Any:
        def new(*args: Any, **kwargs: Any) -> Any:
            args0: list = list(args)
            value: Any = args0.pop()
            key: Any = self._getkey(value)
            if key is int:
                args0.append(int(value))
            if key is str:
                args0.append(str(value).lower().strip())
            if key is list:
                args0.append(list(value))
            ans: Any = self.lookup[key](*args0, **kwargs)
            return ans

        new.__name__ = self.name
        if self.kind is not None:
            new = self.kind(new)
        return new
