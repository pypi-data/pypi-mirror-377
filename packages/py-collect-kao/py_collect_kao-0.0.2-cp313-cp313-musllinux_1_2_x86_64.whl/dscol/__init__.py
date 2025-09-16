# src/dscol/__init__.py
try:
    from ._version import __version__   # ✅ 正確：不加 .py
except Exception:
    __version__ = "0.0.0"

try:
    from ._dscol import Vector       # 確保擴充模組名為 _dscol
except ImportError as e:
    raise ImportError(
        "Failed to import compiled extension 'dscol._dscol'. "
        "Check your wheel contains the compiled module and the name matches."
    ) from e

__all__ = ["IntVector", "__version__"]
