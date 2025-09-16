from .symdb import (
    Language,
    SymbolType,
    Symbol,
    Location,
    ImmideateSymbolDatabase,
    LazySymbolDatabase,
)

# Backward compatibility alias
SymbolDatabase = ImmideateSymbolDatabase

__version__ = "1.2.0"
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
