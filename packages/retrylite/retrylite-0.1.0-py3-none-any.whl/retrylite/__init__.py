"""retrylite – Zero-dependency retry decorator (sync & async)."""

__version__ = "0.1.0"

from ._async import aretry
from ._sync import retry

__all__ = ["retry", "aretry"]
