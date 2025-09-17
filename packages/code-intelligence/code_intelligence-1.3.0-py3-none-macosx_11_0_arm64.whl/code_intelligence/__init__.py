from .symdb import (
    Language,
    SymbolType,
    Symbol,
    Location,
    ImmediateSymbolDatabase,
    LazySymbolDatabase,
)

# Backward compatibility alias
SymbolDatabase = ImmediateSymbolDatabase

__version__ = "1.3.0"
__version_info__ = tuple(int(i) for i in __version__.split('.'))

__all__ = [
    "Language",
    "SymbolType",
    "Symbol",
    "Location",
    "ImmediateSymbolDatabase",
    "LazySymbolDatabase",
    "SymbolDatabase",
]
