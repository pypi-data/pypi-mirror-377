"""
This module provides basic mathematical functions. Use it to perform calculations.
"""

import sys

from minimcp_servers.modules.math import (
    abs,
    add,
    clamp,
    divide,
    floor_divide,
    maximum,
    minimum,
    modulo,
    multiply,
    power,
    round,
    sign,
    subtract,
)

__version__ = sys.version

__all__ = [
    "add",
    "subtract",
    "multiply",
    "divide",
    "modulo",
    "floor_divide",
    "power",
    "minimum",
    "maximum",
    "sign",
    "clamp",
    "round",
    "abs",
]
