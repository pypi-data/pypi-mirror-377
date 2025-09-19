"""
This module provides a diverse set of mathematical functions. Use it to perform calculations.
"""

import builtins
import math as stdlib_math
import sys

__version__ = sys.version


# Creating a custom math module as basic math operations and built-in functions
# are NOT directly provided by the standard math module. Additionally argument types from
# the standard math module are not directly compatible with the MiniMCP protocol.


# === Basic Math Functions ===


def add(a: float, b: float) -> float:
    """Return the sum of a and b"""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of a and b"""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of a and b"""
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient of a and b"""
    return a / b


def modulo(a: float, b: float) -> float:
    """Return the remainder of a divided by b"""
    return a % b


def floor_divide(a: float, b: float) -> float:
    """Return the floor division of a by b"""
    return a // b


def power(a: float, b: float) -> float:
    """Return a raised to the power of b"""
    return a**b


def minimum(a: float, b: float) -> float:
    """Return the smaller of two numbers"""
    return min(a, b)


def maximum(a: float, b: float) -> float:
    """Return the larger of two numbers"""
    return max(a, b)


def sign(x: float) -> int:
    """Return the sign of x (-1, 0, or 1)"""
    return (x > 0) - (x < 0)


def clamp(x: float, min_val: float, max_val: float) -> float:
    """Clamp x to be between min_val and max_val"""
    return max(min_val, min(x, max_val))


def round(x: float, n: int = 0) -> float:
    """Round x to n decimal places (default n is 0)"""
    return builtins.round(x, n)


# abc is available under Floating Point Functions.

# === Trigonometric Functions ===


def sin(x: float) -> float:
    """Return the sine of x (measured in radians)"""
    return stdlib_math.sin(x)


def cos(x: float) -> float:
    """Return the cosine of x (measured in radians)"""
    return stdlib_math.cos(x)


def tan(x: float) -> float:
    """Return the tangent of x (measured in radians)"""
    return stdlib_math.tan(x)


def asin(x: float) -> float:
    """Return the arc sine (measured in radians) of x. Result is between -pi/2 and pi/2"""
    return stdlib_math.asin(x)


def acos(x: float) -> float:
    """Return the arc cosine (measured in radians) of x. Result is between 0 and pi"""
    return stdlib_math.acos(x)


def atan(x: float) -> float:
    """Return the arc tangent (measured in radians) of x. Result is between -pi/2 and pi/2"""
    return stdlib_math.atan(x)


def atan2(y: float, x: float) -> float:
    """
    Return the arc tangent (measured in radians) of y/x. Unlike atan(y/x), the signs of both x and y are considered
    """
    return stdlib_math.atan2(y, x)


# === Hyperbolic Functions ===


def sinh(x: float) -> float:
    """Return the hyperbolic sine of x"""
    return stdlib_math.sinh(x)


def cosh(x: float) -> float:
    """Return the hyperbolic cosine of x"""
    return stdlib_math.cosh(x)


def tanh(x: float) -> float:
    """Return the hyperbolic tangent of x"""
    return stdlib_math.tanh(x)


def asinh(x: float) -> float:
    """Return the inverse hyperbolic sine of x"""
    return stdlib_math.asinh(x)


def acosh(x: float) -> float:
    """Return the inverse hyperbolic cosine of x"""
    return stdlib_math.acosh(x)


def atanh(x: float) -> float:
    """Return the inverse hyperbolic tangent of x"""
    return stdlib_math.atanh(x)


# === Exponential and Logarithmic Functions ===


def exp(x: float) -> float:
    """Return e raised to the power of x"""
    return stdlib_math.exp(x)


def expm1(x: float) -> float:
    """
    Return exp(x)-1. This function avoids the loss of precision involved in the
    direct evaluation of exp(x)-1 for small x
    """
    return stdlib_math.expm1(x)


def log(x: float, base: float = stdlib_math.e) -> float:
    """
    Return the logarithm of x to the given base. If the base is not specified,
    returns the natural logarithm (base e) of x
    """
    return stdlib_math.log(x, base)


def log10(x: float) -> float:
    """Return the base 10 logarithm of x"""
    return stdlib_math.log10(x)


def log2(x: float) -> float:
    """Return the base 2 logarithm of x"""
    return stdlib_math.log2(x)


def log1p(x: float) -> float:
    """
    Return the natural logarithm of 1+x (base e). The result is computed in a way
    which is accurate for x near zero
    """
    return stdlib_math.log1p(x)


# === Rounding and Integer Functions ===


def ceil(x: float) -> int:
    """Return the ceiling of x as an integer. This is the smallest integer >= x"""
    return stdlib_math.ceil(x)


def floor(x: float) -> int:
    """Return the floor of x as an integer. This is the largest integer <= x"""
    return stdlib_math.floor(x)


def trunc(x: float) -> int:
    """Truncate the real x to the nearest integer toward 0"""
    return stdlib_math.trunc(x)


# === Square Root and Power Functions ===


def sqrt(x: float) -> float:
    """Return the square root of x"""
    return stdlib_math.sqrt(x)


def isqrt(x: int) -> int:
    """Return the integer part of the square root of the input"""
    return stdlib_math.isqrt(x)


# === Special Functions ===


def factorial(x: int) -> int:
    """Find x!. Raise a ValueError if x is negative or non-integral"""
    return stdlib_math.factorial(x)


def gamma(x: float) -> float:
    """Gamma function at x"""
    return stdlib_math.gamma(x)


def lgamma(x: float) -> float:
    """Natural logarithm of absolute value of Gamma function at x"""
    return stdlib_math.lgamma(x)


def erf(x: float) -> float:
    """Error function at x"""
    return stdlib_math.erf(x)


def erfc(x: float) -> float:
    """Complementary error function at x"""
    return stdlib_math.erfc(x)


# === Number Theory Functions ===


def gcd(a: int, b: int) -> int:
    """Greatest Common Divisor of a and b"""
    return stdlib_math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Least Common Multiple of a and b"""
    return stdlib_math.lcm(a, b)


def comb(n: int, k: int) -> int:
    """
    Number of ways to choose k items from n items without repetition and without order (binomial coefficient)
    """
    return stdlib_math.comb(n, k)


def perm(n: int, k: int | None = None) -> int:
    """
    Number of ways to choose k items from n items without repetition and with order. If k is None, defaults to n
    """
    return stdlib_math.perm(n, k)


# === Floating Point Functions ===


def abs(x: float) -> float:
    """Return the absolute value of the float x"""
    return stdlib_math.fabs(x)


def copysign(x: float, y: float) -> float:
    """Return a float with the magnitude (absolute value) of x but the sign of y"""
    return stdlib_math.copysign(x, y)


def fmod(x: float, y: float) -> float:
    """Return fmod(x, y), according to platform C. x % y may differ"""
    return stdlib_math.fmod(x, y)


def frexp(x: float) -> tuple[float, int]:
    """Return the mantissa and exponent of x, as pair (m, e). m is a float and e is an int, such that x = m * 2.**e"""
    return stdlib_math.frexp(x)


def ldexp(x: float, i: int) -> float:
    """Return x * (2**i). This is essentially the inverse of frexp()"""
    return stdlib_math.ldexp(x, i)


def modf(x: float) -> tuple[float, float]:
    """Return the fractional and integer parts of x. Both results carry the sign of x and are floats"""
    return stdlib_math.modf(x)


def remainder(x: float, y: float) -> float:
    """Difference between x and the closest integer multiple of y"""
    return stdlib_math.remainder(x, y)


# === Testing Functions ===


def isclose(a: float, b: float, rel_tol: float = 1e-09, abs_tol: float = 0.0) -> bool:
    """
    Determine whether two floating point numbers are close in value.

    Args:
        a: The first floating point number
        b: The second floating point number
        rel_tol: The relative tolerance parameter
        abs_tol: The absolute tolerance parameter

    Returns:
        True if the numbers are close, False otherwise
    """
    return stdlib_math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


# === Angular Conversion Functions ===


def degrees(x: float) -> float:
    """Convert angle x from radians to degrees"""
    return stdlib_math.degrees(x)


def radians(x: float) -> float:
    """Convert angle x from degrees to radians"""
    return stdlib_math.radians(x)


# === Distance and Geometric Functions ===


def hypot(x: float, y: float) -> float:
    """
    Return the Euclidean distance, sqrt(x*x + y*y). This is the length of
    the vector from the origin to point (x, y)
    """
    return stdlib_math.hypot(x, y)


def dist(p: list[float], q: list[float]) -> float:
    """Return the Euclidean distance between two points p and q (as sequences of coordinates)"""
    return stdlib_math.dist(p, q)
