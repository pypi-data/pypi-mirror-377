"""
genius_censor package
"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
__version__ = version(__package__ or "ivcensor")

from .genius_censor import genius_censor,genius_noncensor

__all__ = ["genius_censor", "genius_noncensor"]