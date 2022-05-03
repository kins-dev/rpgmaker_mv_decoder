#!/usr/bin/env python3
"""Utility functions"""

import sys


def int_xor(var: bytes, key: bytes) -> bytes:
    """`int_xor` integer xor

    Runs XOR on 2 bytes streams (must be less than 64 bytes)

    Args:
    - `var` (`bytes`): Input 1
    - `key` (`bytes`): Input 2

    Returns:
    - `bytes`: XOR of input 1 and input 2

    """
    key = key[: len(var)]
    int_var: int = int.from_bytes(var, sys.byteorder)
    int_key: int = int.from_bytes(key, sys.byteorder)
    int_enc: int = int_var ^ int_key
    return int_enc.to_bytes(len(var), sys.byteorder)
