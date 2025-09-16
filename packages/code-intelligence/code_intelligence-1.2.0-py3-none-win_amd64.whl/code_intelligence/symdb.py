import os
import ctypes
import platform
from enum import IntEnum
from pathlib import Path
from dataclasses import dataclass, field


class Language(IntEnum):
    # UNKNOWN = 0
    PYTHON = 1
    JAVASCRIPT = 2
    TYPESCRIPT = 3
    CPP = 4
    C = 5
    JAVA = 6
    RUST = 7
    GO = 8
    PHP = 9
    RUBY = 10
    CSHARP = 11
    KOTLIN = 12
    SWIFT = 13
    SCALA = 14
    DART = 15
    LUA = 16


class SymbolType(IntEnum):
    UNKNOWN = 0
    CLASS = 1
    FUNCTION = 2
    METHOD = 3
    VARIABLE = 4
    MODULE = 5
    IMPORT = 6
    FROM_IMPORT = 7
    CONSTANT = 8
    PROPERTY = 9
    INTERFACE = 10
    STRUCT = 11
    ENUM = 12
    NAMESPACE = 13
    PACKAGE = 14
    FIELD = 15
    PARAMETER = 16
    LOCAL = 17
    TYPE = 18

Path_Like = str | Path

@dataclass(slots=True)
class Location:
    """Source code span."""
    path: str = ""
    line: int = 0
    column: int = 0
    end_line: int = 0
    end_column: int = 0

    def __repr__(self) -> str:
        return f"Location({self.path}:{self.line}:{self.column})"

@dataclass(slots=True)
class Symbol:
    """Language-agnostic symbol record."""
    name: str = ""
    symbol_type: SymbolType = SymbolType.UNKNOWN
    definition: Location = field(default_factory=Location)
    parent: str | None = None
    signature: str | None = None
    documentation: str | None = None

    def __repr__(self) -> str:
        return f"Symbol({self.name}, {self.symbol_type.name}, {self.definition})"

    # Convenience properties for backward compatibility with TASK.md API
    @property
    def filename(self) -> str:
        return self.definition.path

    @property
    def line(self) -> int:
        return self.definition.line

    @property
    def column(self) -> int:
        return self.definition.column

    # Keep location as alias for backward compatibility
    @property
    def location(self) -> "Location":
        return self.definition

# --- Private ctypes Implementation ---

# Matches ci_location_t (field name 'path')
class _Location(ctypes.Structure):
    _fields_ = [
        ("path", ctypes.c_char_p),
        ("line", ctypes.c_uint32),
        ("column", ctypes.c_uint32),
        ("end_line", ctypes.c_uint32),
        ("end_column", ctypes.c_uint32),
    ]

# Matches ci_symbol_t (field name 'definition')
class _Symbol(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("symbol_type", ctypes.c_int),
        ("definition", _Location),
        ("parent", ctypes.c_char_p),
        ("signature", ctypes.c_char_p),
        ("documentation", ctypes.c_char_p),
    ]


CURRENT_OS = platform.system().lower()

if CURRENT_OS == "darwin":
    LIB_EXT = ".dylib"
elif CURRENT_OS == "windows":
    LIB_EXT = ".dll"
else:
    LIB_EXT = ".so"

def _load_library(name: str):
    # Try module directory first (where nob.py now puts the library)
    lib_path = Path(__file__).parent / f"{name}{LIB_EXT}"
    if not lib_path.exists():
        # Fallback to build directory for backward compatibility
        lib_path = Path(__file__).parent.parent / "build" / f"{name}{LIB_EXT}"
        if not lib_path.exists():
            # Final fallback to project root
            lib_path = Path(__file__).parent.parent / f"{name}{LIB_EXT}"
            if not lib_path.exists():
                raise ImportError(
                    f"Cannot find compiled library at {lib_path}. Please build it first using 'python nob.py lib'."
                )

    lib = ctypes.CDLL(os.fsdecode(lib_path))
    return lib

_lib = _load_library("_code_intelligence")

# C function signatures (match code_intelligence.c)
_lib.symbol_db_create.argtypes = []
_lib.symbol_db_create.restype = ctypes.c_void_p

_lib.symbol_db_destroy.argtypes = [ctypes.c_void_p]
_lib.symbol_db_destroy.restype = None

_lib.symbol_db_set_project_root.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_lib.symbol_db_set_project_root.restype = None

_lib.symbol_db_scan_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
_lib.symbol_db_scan_file.restype = ctypes.c_bool

# Batch scan
_lib.symbol_db_scan_files.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_uint32, ctypes.c_int]
_lib.symbol_db_scan_files.restype = ctypes.c_bool

_lib.symbol_db_remove_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_lib.symbol_db_remove_file.restype = ctypes.c_bool

# Update file (re-scan and replace)
_lib.symbol_db_update_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
_lib.symbol_db_update_file.restype = ctypes.c_bool

# Arrays with out_count
_lib.symbol_db_find_definitions.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
_lib.symbol_db_find_definitions.restype = ctypes.POINTER(_Symbol)

_lib.symbol_db_find_references.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
_lib.symbol_db_find_references.restype = ctypes.POINTER(_Symbol)

_lib.symbol_db_get_all_symbols.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
_lib.symbol_db_get_all_symbols.restype = ctypes.POINTER(_Symbol)

# bool return + out _Symbol
_lib.symbol_db_get_symbol.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(_Symbol)]
_lib.symbol_db_get_symbol.restype = ctypes.c_bool

# Free for arrays (void*)
_lib.symbol_array_free.argtypes = [ctypes.c_void_p]
_lib.symbol_array_free.restype = None

_lib.ci_flush_coverage.argtypes = []
_lib.ci_flush_coverage.restype = None

_lib.symbol_db_clear.argtypes = [ctypes.c_void_p, ctypes.c_int]
_lib.symbol_db_clear.restype = None

def _flush_coverage():
    try:
        _lib.ci_flush_coverage()
    except Exception:
        pass

# Helper conversions

class CStringView:
    """A view into a C string that delays decoding until needed."""
    __slots__ = ('_ptr', '_decoded')
    
    def __init__(self, c_char_p):
        self._ptr = c_char_p
        self._decoded = None
    
    def __str__(self):
        if self._decoded is None:
            if self._ptr:
                self._decoded = self._ptr.decode("utf-8", errors="replace")
            else:
                self._decoded = ""
        return self._decoded
    
    def __repr__(self):
        return f"CStringView({str(self)!r})"
    
    def __bool__(self):
        return bool(self._ptr)
    
    def __eq__(self, other):
        if isinstance(other, CStringView):
            return str(self) == str(other)
        elif isinstance(other, str):
            return str(self) == other
        return False


def _to_py_symbol_lazy(c_symbol: _Symbol) -> Symbol:
    """Convert C symbol to Python symbol with lazy string decoding."""
    definition = Location(
        path=str(CStringView(c_symbol.definition.path)),  # Decode immediately for file paths (needed for path operations)
        line=c_symbol.definition.line,
        column=c_symbol.definition.column,
        end_line=c_symbol.definition.end_line,
        end_column=c_symbol.definition.end_column,
    )
    return Symbol(
        name=str(CStringView(c_symbol.name)),  # Most accessed field, decode immediately
        symbol_type=SymbolType(c_symbol.symbol_type),
        definition=definition,
        parent=str(CStringView(c_symbol.parent)) if c_symbol.parent else None,
        signature=CStringView(c_symbol.signature) if c_symbol.signature else None,  # Keep as view
        documentation=CStringView(c_symbol.documentation) if c_symbol.documentation else None,  # Keep as view
    )


def _to_py_symbol(c_symbol: _Symbol) -> Symbol:
    definition = Location(
        path=c_symbol.definition.path.decode("utf-8", errors="replace") if c_symbol.definition.path else "",
        line=c_symbol.definition.line,
        column=c_symbol.definition.column,
        end_line=c_symbol.definition.end_line,
        end_column=c_symbol.definition.end_column,
    )
    return Symbol(
        name=c_symbol.name.decode("utf-8", errors="replace") if c_symbol.name else "",
        symbol_type=SymbolType(c_symbol.symbol_type),
        definition=definition,
        parent=c_symbol.parent.decode("utf-8", errors="replace") if c_symbol.parent else None,
        signature=c_symbol.signature.decode("utf-8", errors="replace") if c_symbol.signature else None,
        documentation=c_symbol.documentation.decode("utf-8", errors="replace") if c_symbol.documentation else None,
    )


class SymbolArrayView:
    """A view into a C symbol array that manages the C memory and provides lazy access."""
    
    def __init__(self, ptr: ctypes.POINTER(_Symbol), count: int):
        self._ptr = ptr
        self._count = count
        self._symbols = None  # Lazy converted symbols
    
    def __len__(self):
        return self._count
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            # Handle slice objects
            start, stop, step = index.indices(self._count)
            return [self[i] for i in range(start, stop, step)]
        
        if index < 0:
            index = self._count + index
        if index < 0 or index >= self._count:
            raise IndexError("Symbol array index out of range")
        
        # Lazy conversion - convert only accessed symbols
        if self._symbols is None:
            self._symbols = [None] * self._count
        
        if self._symbols[index] is None:
            self._symbols[index] = _to_py_symbol_lazy(self._ptr[index])
        
        return self._symbols[index]
    
    def __iter__(self):
        for i in range(self._count):
            yield self[i]
    
    def __del__(self):
        # Free the C array when Python object is garbage collected
        if hasattr(self, '_ptr') and self._ptr:
            _lib.symbol_array_free(self._ptr)
            self._ptr = None


def _convert_symbol_array(ptr: ctypes.POINTER(_Symbol), count: int) -> list[Symbol]:
    if not ptr or count <= 0:
        return []
    try:
        return [_to_py_symbol(ptr[i]) for i in range(count)]
    finally:
        # Free the shallow-copy array buffer
        _lib.symbol_array_free(ptr)


def _convert_symbol_array_lazy(ptr: ctypes.POINTER(_Symbol), count: int) -> SymbolArrayView:
    """Convert C symbol array to a lazy Python view without immediate copying."""
    if not ptr or count <= 0:
        if ptr:
            _lib.symbol_array_free(ptr)  # Free empty array
        return SymbolArrayView(None, 0)
    
    return SymbolArrayView(ptr, count)



# --- Backend Implementations ---

class _BaseSymbolDatabase:
    """Base class for code intelligence operations (not for direct use)."""
    def __init__(self):
        self._handle = _lib.symbol_db_create()
        if not self._handle:
            raise RuntimeError("Failed to create symbol database")

    def __del__(self):
        if hasattr(self, "_handle") and self._handle:
            _lib.symbol_db_destroy(self._handle)
            self._handle = None

    def clear(self, *, reuse_memory: bool = True):
        """Reset the database state while keeping the same Python object.

        Frees the current native database state and reinitializes it. Any
        previously scanned files, symbols, and project root are discarded.
        
        Args:
            reuse_memory: If True (default), keep allocated arena memory for reuse.
                         If False, free all memory and start fresh.
        """
        if self._handle:
            _lib.symbol_db_clear(self._handle, ctypes.c_int(1 if reuse_memory else 0))

    def set_project_root(self, path: Path_Like):
        _lib.symbol_db_set_project_root(self._handle, os.fsencode(path))

    def scan_file(self, path: Path_Like, language: Language) -> bool:
        return _lib.symbol_db_scan_file(
            self._handle,
            os.fsencode(path),
            int(language),
        )

    def scan_files(self, paths: list[Path_Like], language: Language) -> bool:
        arr = (ctypes.c_char_p * len(paths))()
        for i, p in enumerate(paths):
            arr[i] = os.fsencode(p)
        return _lib.symbol_db_scan_files(
            self._handle,
            arr,
            ctypes.c_uint32(len(paths)),
            int(language),
        )

    def init_project(self, files_by_language: dict[Language, list[Path_Like]]) -> bool:
        all_ok = True
        for lang, files in files_by_language.items():
            if not files:
                continue
            ok = self.scan_files(files, lang)
            if not ok:
                all_ok = False
        return all_ok

    def remove_file(self, path: Path_Like) -> bool:
        return _lib.symbol_db_remove_file(
            self._handle,
            os.fsencode(path),
        )

    def update_file(self, path: Path_Like, language: Language) -> bool:
        return _lib.symbol_db_update_file(
            self._handle,
            os.fsencode(path),
            int(language),
        )

    def get_symbol(self, path: Path_Like, line: int, column: int) -> Symbol | None:
        out = _Symbol()
        ok = _lib.symbol_db_get_symbol(
            self._handle,
            os.fsencode(path),
            ctypes.c_uint32(line),
            ctypes.c_uint32(column),
            ctypes.byref(out),
        )
        return _to_py_symbol(out) if ok else None


class ImmideateSymbolDatabase(_BaseSymbolDatabase):
    """Symbol database using copying (eager) backend."""
    def find_definitions(self, symbol_name: str) -> list[Symbol]:
        count = ctypes.c_uint32(0)
        ptr = _lib.symbol_db_find_definitions(
            self._handle,
            symbol_name.encode("utf-8"),
            ctypes.byref(count),
        )
        return _convert_symbol_array(ptr, int(count.value))

    def find_symbols(self, symbol_name: str) -> list[Symbol]:
        return self.find_definitions(symbol_name)

    def find_references(self, symbol_name: str) -> list[Symbol]:
        count = ctypes.c_uint32(0)
        ptr = _lib.symbol_db_find_references(
            self._handle,
            symbol_name.encode("utf-8"),
            ctypes.byref(count),
        )
        return _convert_symbol_array(ptr, int(count.value))

    def get_all_symbols(self) -> list[Symbol]:
        count = ctypes.c_uint32(0)
        ptr = _lib.symbol_db_get_all_symbols(self._handle, ctypes.byref(count))
        return _convert_symbol_array(ptr, int(count.value))


class LazySymbolDatabase(_BaseSymbolDatabase):
    """Symbol database using lazy backend."""
    def find_definitions(self, symbol_name: str) -> SymbolArrayView:
        count = ctypes.c_uint32(0)
        ptr = _lib.symbol_db_find_definitions(
            self._handle,
            symbol_name.encode("utf-8"),
            ctypes.byref(count),
        )
        return _convert_symbol_array_lazy(ptr, int(count.value))

    def find_symbols(self, symbol_name: str) -> SymbolArrayView:
        return self.find_definitions(symbol_name)

    def find_references(self, symbol_name: str) -> SymbolArrayView:
        count = ctypes.c_uint32(0)
        ptr = _lib.symbol_db_find_references(
            self._handle,
            symbol_name.encode("utf-8"),
            ctypes.byref(count),
        )
        return _convert_symbol_array_lazy(ptr, int(count.value))

    def get_all_symbols(self) -> SymbolArrayView:
        count = ctypes.c_uint32(0)
        ptr = _lib.symbol_db_get_all_symbols(self._handle, ctypes.byref(count))
        return _convert_symbol_array_lazy(ptr, int(count.value))

