import pandas as pd
from typing import Any

__all__ = ["pd_sign", "pd_nvl", "pd_nvl2", "pd_noneif", "pd_decode", "pd_coalesce"]

# Sentinel to detect whether default was actually provided in pd_decode
_MISSING = object()


def pd_sign(series: pd.Series) -> pd.Series:
    out = pd.Series(index=series.index, dtype="object")

    out.loc[series > 0] = 1
    out.loc[series == 0] = 0
    out.loc[series < 0] = -1

    # Keep None for missing inputs (NaN/None)
    out.loc[series.isna()] = None
    return out


def pd_nvl(series: pd.Series, default: Any) -> pd.Series:
    """
    Replace nulls (NaN/None) with `default`.
    """
    return series.fillna(default)


def pd_nvl2(series: pd.Series, value_if_not_null: Any, value_if_null: Any) -> pd.Series:
    mask = series.notna()
    out = pd.Series(value_if_null, index=series.index, dtype="object")
    out.loc[mask] = value_if_not_null
    return out


def pd_noneif(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    # Consider NaN == NaN as equal
    equal_mask = series_a.eq(series_b) | (series_a.isna() & series_b.isna())

    out = series_a.astype("object").copy()
    out.loc[equal_mask] = None
    return out


def pd_decode(series: pd.Series, *pairs: Any, default: Any = _MISSING) -> pd.Series:
    n = len(pairs)

    if n == 0:
        # No pairs given: fill entirely with explicit default if provided, else None
        fill_value = None if default is _MISSING else default
        return pd.Series([fill_value] * len(series), index=series.index, dtype="object")

    # Detect implicit default (odd number of args)
    implicit_default = _MISSING
    if n % 2 == 1:
        implicit_default = pairs[-1]
        pairs = pairs[:-1]
        n -= 1

    if n % 2 != 0:
        raise ValueError("pd_decode() requires (search, result) pairs.")

    # Determine base/default value with clear precedence
    if default is not _MISSING:
        base_value = default
    elif implicit_default is not _MISSING:
        base_value = implicit_default
    else:
        base_value = None

    # out = pd.Series(base_value, index=series.index, dtype="object")
    out = pd.Series([base_value] * len(series), index=series.index, dtype="object")

    # Apply each (search, result) pair in order
    for i in range(0, n, 2):
        search = pairs[i]
        result = pairs[i + 1]

        # Match rule: direct equality OR both sides null
        matches = (series == search) | (series.isna() & pd.isna(search))
        out.loc[matches] = result

    return out


def pd_coalesce(*series_list: pd.Series) -> pd.Series:
    """
    Return a Series where each element is the first non-null value across the given input Series.
    """
    if not series_list:
        raise ValueError("pd_coalesce requires at least one Series")

    # Start with the first series
    result = series_list[0].astype("object").copy()

    for s in series_list[1:]:
        if not isinstance(s, pd.Series):
            raise TypeError("pd_coalesce expects only pandas Series arguments")
        mask = result.isna()
        result.loc[mask] = s[mask].astype("object")

    return result
