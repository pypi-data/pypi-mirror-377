import enum
import functools
import tomllib
from importlib import resources
from typing import *

__all__ = ["easy"]


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        text: str = resources.read_text("docing.core", "cfg.toml")
        data: dict = tomllib.loads(text)
        return data

    @functools.cached_property
    def lookup(self: Self) -> dict[str, str]:
        ans: dict = dict()
        a: str
        b: str
        x: str
        y: str
        for a, b in self.magicmethodsdict.items():
            x = "__%s__" % a
            y = "This magic method %s." % b
            ans[x] = y
        return ans

    @functools.cached_property
    def magicmethodsdict(self: Self) -> dict[str, str]:
        ans: dict = dict()
        a: str
        b: str
        c: str
        d: str
        for a, b in self.data["magic-method"]["operations"].items():
            for c, d in self.data["magic-method"]["operators"].items():
                ans[a + c] = "implements %s" % (b % d)
        for a, b in self.data["magic-method"]["implements"].items():
            ans[a] = "implements %s" % b
        for a, b in self.data["magic-method"]["explanations"].items():
            ans[a] = b
        return ans


def easy(target: Any) -> Any:
    target.__doc__ = geteasydoc(target.__name__)
    return target


def geteasydoc(name: Any) -> str:
    return Util.util.lookup[str(name)]
