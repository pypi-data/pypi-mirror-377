"""
FukobabaTekKral: Specification-Driven Development Framework
Built for the AI era
"""

from ._version import __version__

__author__ = "FukobabaTekKral"
__url__ = "https://github.com/fukobabatekkral"

from .core.fukobabatekkral import FukobabaTekKral
from .cli.main import main

__all__ = ["FukobabaTekKral", "main"]