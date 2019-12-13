# from typing import Number
from numbers import Number


def sign(val: float) -> int:
    """Return 1 or -1 to represent the sign of the given value"""
    return -1 if val < 0 else 1
