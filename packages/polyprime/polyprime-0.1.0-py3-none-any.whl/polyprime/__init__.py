"""
PolyPrime - The Multi-Paradigm Programming Language
"""

__version__ = "0.1.0"
__author__ = "Michael Benjamin Crowe"
__email__ = "michael@crowelogic.com"

from .compiler import Compiler
from .runtime import Runtime

__all__ = ["Compiler", "Runtime", "__version__"]