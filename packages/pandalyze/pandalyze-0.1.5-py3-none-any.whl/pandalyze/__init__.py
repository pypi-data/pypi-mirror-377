"""
pandalyze - a pandas performance profiler
"""

from .analyze import analyze
from .detectantipatterns import detectantipatterns

__all__ = ["analyze", "detectantipatterns"]
__version__ = "0.1.0"
