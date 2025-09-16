"""
Code Intelligence Library

A lightweight, fast Tree-sitter based code intelligence library.
Provides symbol database functionality for code analysis.
"""

from .symdb import (
    Language,
    SymbolType,
    Symbol,
    Location,
    ImmideateSymbolDatabase,
    LazySymbolDatabase,
)

# Backward compatibility alias - defaults to copying backend
SymbolDatabase = ImmideateSymbolDatabase

__version__ = "1.1.0"
__version_info__ = tuple(int(i) for i in __version__.split('.'))

__all__ = [
    "Language",
    "SymbolType",
    "Symbol",
    "Location",
    "ImmideateSymbolDatabase",
    "LazySymbolDatabase",
    "SymbolDatabase",
]
