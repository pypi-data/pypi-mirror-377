from __future__ import annotations
from provide.foundation.utils.env.getters import get_bool, get_dict, get_float, get_int, get_list, get_path, get_str, require
from provide.foundation.utils.env.parsers import parse_duration, parse_size
from provide.foundation.utils.env.prefix import EnvPrefix

__all__ = [
    "get_bool",
    "get_dict",
    "get_float",
    "get_int",
    "get_list",
    "get_path",
    "get_str",
    "require",
    "parse_duration",
    "parse_size",
    "EnvPrefix",
]

"""Environment variable utilities with type coercion and prefix support.

Provides utilities for safely reading and parsing environment variables with
automatic type detection, prefix-based namespacing, and default value handling.
"""




# Re-export all public functions and classes from submodules

__all__ = [
    "EnvPrefix",
    "get_bool",
    "get_dict",
    "get_float",
    "get_int",
    "get_list",
    "get_path",
    "get_str",
    "parse_duration",
    "parse_size",
    "require",
]