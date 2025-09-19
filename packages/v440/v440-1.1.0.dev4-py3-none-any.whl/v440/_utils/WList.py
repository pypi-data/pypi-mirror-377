from typing import *

from v440._utils import utils
from v440._utils.VList import VList
from v440.core.VersionError import VersionError

__all__ = ["WList"]


class WList(VList):
    def __setattr__(self: Self, name: str, value: Any) -> Any:
        if name not in type(self).__annotations__.keys():
            return object.__setattr__(self, name, value)
        backup: list = utils.clone(self)
        exc: BaseException
        try:
            object.__setattr__(self, name, value)
        except BaseException as exc:
            self.data = backup
            if isinstance(exc, VersionError):
                raise
            msg: str = "%r is an invalid value for %r"
            msg %= (value, type(self).__name__ + "." + name)
            raise VersionError(msg)
