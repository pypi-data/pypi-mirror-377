from typing import *

__all__ = ["easy"]

_DICT = {
    "__add__": "This magic method implements self+other.",
    "__and__": "This magic method implements self&other.",
    "__call__": "This magic method implements calling self.",
    "__divmod__": "This magic method implements divmod(self, other).",
    "__floordiv__": "This magic method implements self//other.",
    "__ge__": "This magic method implements self>=other.",
    "__gt__": "This magic method implements self>other.",
    "__init__": "This magic method initializes self.",
    "__le__": "This magic method implements self<=other.",
    "__lshift__": "This magic method implements self<<other.",
    "__lt__": "This magic method implements self<other.",
    "__matmul__": "This magic method implements self@other.",
    "__mod__": "This magic method implements self%other.",
    "__mul__": "This magic method implements self*other.",
    "__or__": "This magic method implements self|other.",
    "__pow__": "This magic method implements pow(self, other).",
    "__radd__": "This magic method implements other+self.",
    "__rand__": "This magic method implements other&self.",
    "__rdivmod__": "This magic method implements divmod(other, self).",
    "__rfloordiv__": "This magic method implements other//self.",
    "__rlshift__": "This magic method implements other<<self.",
    "__rmatmul__": "This magic method implements other@self.",
    "__rmod__": "This magic method implements other%self.",
    "__rmul__": "This magic method implements other*self.",
    "__ror__": "This magic method implements other|self.",
    "__rpow__": "This magic method implements pow(other, self).",
    "__rrshift__": "This magic method implements other>>self.",
    "__rshift__": "This magic method implements self>>other.",
    "__rsub__": "This magic method implements other-self.",
    "__rtruediv__": "This magic method implements other/self.",
    "__rxor__": "This magic method implements other^self.",
    "__sub__": "This magic method implements self-other.",
    "__truediv__": "This magic method implements self/other.",
    "__xor__": "This magic method implements self^other.",
}


def easy(target: Any) -> Any:
    target.__doc__ = _DICT[target.__name__]
    return target
