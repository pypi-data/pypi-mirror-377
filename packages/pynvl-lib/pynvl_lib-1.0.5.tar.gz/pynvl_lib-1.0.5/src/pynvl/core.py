from typing import Any, Final

__all__: Final = ("nvl", "decode", "sign", "noneif", "nvl2", "coalesce")


def nvl(expr, default):
    """
    - nvl means None Value and is a nod to Oracle nvl (Null value)
    """
    if expr is None:
        return default
    else:
        return expr


_MISSING = object()  # Sentinel to distinguish "not provided" from None


def decode(expr: Any, *pairs: Any, default: Any = _MISSING) -> Any:
    """
    - Check expr and find which matching pair it belongs to.
    - Returns default if no matches found.
    - NOTE: To stay consistent with Oracle we let None equal None.
    """
    implicit_default = _MISSING
    n = len(pairs)

    if n == 0:
        return None if default is _MISSING else default

    # If odd count, last is implicit default.  Strip it from pairs
    if n % 2 == 1:
        implicit_default = pairs[-1]
        pairs = pairs[:-1]

    # Iterate search/result pairs
    it = iter(pairs)
    # Zip iterator with itself to consume items in twos.
    for search, result in zip(it, it):
        # For consistency with Oracle None equals None
        if expr == search or (expr is None and search is None):
            return result

    # Choose default: explicit overrides implicit; else None
    if default is not _MISSING:
        return default
    if implicit_default is not _MISSING:
        return implicit_default
    return None


def sign(n: float | int) -> int:
    if n < 0:
        return -1
    elif n > 0:
        return 1
    else:
        return 0


def _nullif(a: Any, b: Any) -> Any:
    if a == b:
        return None
    else:
        return a


def noneif(a: Any, b: Any) -> Any:
    return _nullif(a, b)


def nvl2(expr: Any, value_if_not_null: Any, value_if_null: Any) -> Any:
    if expr is not None:
        return value_if_not_null
    else:
        return value_if_null


def coalesce(*args: Any) -> Any:
    for item in args:
        if item is not None:
            return item
    return None
