"""
pypipe - a tiny “value-first” piping helper, inspired by Unix pipes
==================================================================

Example
-------

>>> from pypipe import pipe, _
>>> import numpy as np
>>>
>>> # Work seamlessly with NumPy
>>> result = (pipe(np.arange(5))
...           | (np.add, 10)          # value as 1st arg (default)
...           | (np.multiply, 2, _)   # value in 2nd position
...           | (np.power, _, 2))     # again in 1st (explicit)
>>> result.value
array([400, 484, 576, 676, 784])

Key rules
---------

*  **`| func`** → insert piped value as the *first* positional argument.
*  **`| (func, …)`** → tuple form lets you supply extra args/kwargs.
*  **`_`** marks the exact slot—positional or keyword—where the value goes.
*  If no `_` appears, the value is inserted as the first positional arg.
*  Everything returns a new `Pipe`, so chains are naturally composable.

Place this file as ``lapipe/__init__.py`` and you already have a fully
working PyPI-ready single-file package (add the usual *pyproject.toml* /
*README* / *LICENSE* alongside).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple, TypeVar, overload

__all__ = ["Pipe", "pipe", "_", "__version__"]

__version__ = "1.0.0"

# --------------------------------------------------------------------------- #
# Public sentinel placeholder                                                 #
# --------------------------------------------------------------------------- #

_PLACEHOLDER = object()
#: Use the plain underscore to mark where the piped value should be inserted
_ = _PLACEHOLDER  # noqa: E741 (we *want* the bare underscore here)

# --------------------------------------------------------------------------- #
# Type helpers                                                                #
# --------------------------------------------------------------------------- #

T = TypeVar("T")
R = TypeVar("R")
Func = Callable[..., R]

# --------------------------------------------------------------------------- #
# Pipe implementation                                                         #
# --------------------------------------------------------------------------- #


class Pipe:
    """
    Wrap a value so it can be threaded through an arbitrary call chain
    using the ``|`` operator.

    >>> from lapipe import pipe, _
    >>> def add(a, b): return a + b
    >>> pipe(2) | (add, 3) | (add, 10, _)
    Pipe(15)
    """

    #: module-level placeholder for convenience
    placeholder = _

    # --------------------------------------------------------------------- #
    # Construction & representation                                         #
    # --------------------------------------------------------------------- #
    def __init__(self, value: T):
        self.value: T = value

    # nice `repr` for interactive work
    def __repr__(self) -> str:  # pragma: no cover
        return f"Pipe({self.value!r})"

    # --------------------------------------------------------------------- #
    # Core piping logic                                                     #
    # --------------------------------------------------------------------- #
    def _inject(self, args: List[Any], kwargs: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Replace placeholder tokens by *self.value* and insert the value
        as the first positional argument if it has not been consumed.
        """
        # Replace in positional args
        args = [self.value if a is _ else a for a in args]

        # Replace in kwargs
        kwargs = {k: (self.value if v is _ else v) for k, v in kwargs.items()}

        # Did we consume the value?
        consumed = any(a is self.value for a in args) or any(v is self.value for v in kwargs.values())

        if not consumed:
            args.insert(0, self.value)

        return args, kwargs

    def pipe(self, func: Func, /, *args: Any, **kwargs: Any) -> "Pipe":
        """
        Low-level helper: call *func* with the current value injected
        according to ``_`` placeholders (or prepended if none present).
        """
        pos_args, kw_args = self._inject(list(args), dict(kwargs))
        return Pipe(func(*pos_args, **kw_args))

    # --------------------------------------------------------------------- #
    # Operator overloading                                                  #
    # --------------------------------------------------------------------- #
    def __or__(self, other: Any) -> "Pipe":  # noqa: D401,E501
        """
        Support two syntaxes:

        * ``| func`` - value goes in first positional arg
        * ``| (func, *args [, {k: v}])`` - tuple form, with optional
          trailing dict for keyword args (to avoid the Python syntax
          “keyword in a tuple” limitation).
        """
        if callable(other):
            return self.pipe(other)

        if isinstance(other, tuple) and other and callable(other[0]):
            func, *rest = other

            # Separate kwargs if the last element is a dict
            kwargs: Dict[str, Any] = {}
            if rest and isinstance(rest[-1], dict):
                kwargs = rest.pop()  # type: ignore[arg-type]

            return self.pipe(func, *rest, **kwargs)

        raise TypeError(
            "Right-hand side of | must be a callable or "
            "a tuple like (func, *args [, {kw: val}])."
        )


# --------------------------------------------------------------------------- #
# User-friendly constructor                                                   #
# --------------------------------------------------------------------------- #


def pipe(value: T) -> Pipe:
    """Wrap *value* in a :class:`Pipe` for chaining."""
    return Pipe(value)


# --------------------------------------------------------------------------- #
# Shorthand: allow “lapipe.pipe(value)” directly via module __call__          #
# --------------------------------------------------------------------------- #

# Note: Module __call__ feature removed due to Python compatibility issues

