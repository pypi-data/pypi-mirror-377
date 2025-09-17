"""
genius_censor package
"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
__version__ = version(__package__ or "mawiisurv")

from .mawii_surv import mawii_censor,mawii_noncensor

__all__ = ["mawii_censor", "mawii_noncensor"]