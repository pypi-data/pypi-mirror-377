"""
pynvl: Oracle-inspired functions for Python.
Core: nvl, decode, sign, noneif, nvl2, coalesce
Pandas (optional): pd_sign, pd_nvl, pd_nvl2, pd_noneif, pd_decode, pd_coalesce
"""

from importlib.metadata import PackageNotFoundError, version as _version

# ---- Package metadata ----
try:
    __version__ = _version("pynvl-lib")
except PackageNotFoundError:
    __version__ = "0.dev0"

__url__ = "https://betterinfotech.github.io/pynvl_project/"

# ---- Core re-exports (top-level import convenience) ----
from .core import coalesce, decode, noneif, nvl, nvl2, sign

# ---- Public API list (single assignment; no mutation) ----
__all__ = (
    "nvl",
    "decode",
    "sign",
    "noneif",
    "nvl2",
    "coalesce",
    "pd_sign",
    "pd_nvl",
    "pd_nvl2",
    "pd_noneif",
    "pd_decode",
    "pd_coalesce",
)

# ---- Pandas helpers: real if pandas is installed, stubs otherwise ----
try:
    from .pandas_ext import pd_decode, pd_noneif, pd_nvl, pd_nvl2, pd_sign
except Exception:

    def _requires_pandas(*_args, **_kwargs):
        raise ImportError(
            "pandas is required for pd_* helpers. Install with pip install pandas"
        )

    pd_sign = _requires_pandas
    pd_nvl = _requires_pandas
    pd_nvl2 = _requires_pandas
    pd_noneif = _requires_pandas
    pd_decode = _requires_pandas
    pd_coalesce = _requires_pandas()
