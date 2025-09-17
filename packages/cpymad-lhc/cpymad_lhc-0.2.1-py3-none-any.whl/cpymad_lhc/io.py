"""
Input/Output Tools
------------------

Tools to enable easy input and output operations with cpymad.
"""
from __future__ import annotations


class PathContainer:
    """ Class for easy access to stored paths and conversion to strings. """
    @classmethod
    def get(cls, key, *args):
        return getattr(cls, key).joinpath(*args)

    @classmethod
    def str(cls, key, *args):
        return str(cls.get(key, *args))