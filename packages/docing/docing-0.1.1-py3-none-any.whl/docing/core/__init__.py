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
        for a, b in self.data["classical-patterns-by-name-prefix"].items():
            for c, d in self.data["classical-operators-by-name"].items():
                ans[a + c] = "implements %s" % (b % d)
        for a, b in self.data["atypical-magic-implements-by-name"].items():
            ans[a] = "implements %s" % b
        for a, b in self.data["atypical-magic-explanations-by-name"].items():
            ans[a] = b
        return ans


def easy(target: Any) -> Any:
    target.__doc__ = Util.util.lookup[str(target.__name__)]
    return target
