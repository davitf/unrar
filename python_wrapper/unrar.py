import os
import ctypes
from ctypes import c_uint, c_char_p, c_wchar_p, c_void_p, c_long, POINTER, Structure

# Constants from dll.hpp
ERAR_SUCCESS = 0
ERAR_END_ARCHIVE = 10
ERAR_BAD_PASSWORD = 24

RAR_OM_EXTRACT = 1

RAR_SKIP = 0
RAR_TEST = 1
RAR_EXTRACT = 2

# Load library from package directory
_libname = os.path.join(os.path.dirname(__file__), '..', 'libunrar.so')
_unrar = ctypes.CDLL(os.path.abspath(_libname))

UNRARCALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_uint, c_long, c_long, c_long)

class RARHeaderDataEx(Structure):
    _fields_ = [
        ("ArcName", ctypes.c_char * 1024),
        ("ArcNameW", ctypes.c_wchar * 1024),
        ("FileName", ctypes.c_char * 1024),
        ("FileNameW", ctypes.c_wchar * 1024),
        ("Flags", c_uint),
        ("PackSize", c_uint),
        ("PackSizeHigh", c_uint),
        ("UnpSize", c_uint),
        ("UnpSizeHigh", c_uint),
        ("HostOS", c_uint),
        ("FileCRC", c_uint),
        ("FileTime", c_uint),
        ("UnpVer", c_uint),
        ("Method", c_uint),
        ("FileAttr", c_uint),
        ("CmtBuf", c_char_p),
        ("CmtBufSize", c_uint),
        ("CmtSize", c_uint),
        ("CmtState", c_uint),
        ("DictSize", c_uint),
        ("HashType", c_uint),
        ("Hash", ctypes.c_char * 32),
        ("RedirType", c_uint),
        ("RedirName", c_wchar_p),
        ("RedirNameSize", c_uint),
        ("DirTarget", c_uint),
        ("MtimeLow", c_uint),
        ("MtimeHigh", c_uint),
        ("CtimeLow", c_uint),
        ("CtimeHigh", c_uint),
        ("AtimeLow", c_uint),
        ("AtimeHigh", c_uint),
        ("ArcNameEx", c_wchar_p),
        ("ArcNameExSize", c_uint),
        ("FileNameEx", c_wchar_p),
        ("FileNameExSize", c_uint),
        ("Reserved", c_uint * 982),
    ]

class RAROpenArchiveDataEx(Structure):
    _fields_ = [
        ("ArcName", c_char_p),
        ("ArcNameW", c_wchar_p),
        ("OpenMode", c_uint),
        ("OpenResult", c_uint),
        ("CmtBuf", c_char_p),
        ("CmtBufSize", c_uint),
        ("CmtSize", c_uint),
        ("CmtState", c_uint),
        ("Flags", c_uint),
        ("Callback", UNRARCALLBACK),
        ("UserData", c_long),
        ("OpFlags", c_uint),
        ("CmtBufW", c_wchar_p),
        ("MarkOfTheWeb", c_wchar_p),
        ("Reserved", c_uint * 23),
    ]

# Function prototypes
_unrar.RAROpenArchiveEx.argtypes = [POINTER(RAROpenArchiveDataEx)]
_unrar.RAROpenArchiveEx.restype = c_void_p
_unrar.RARCloseArchive.argtypes = [c_void_p]
_unrar.RARCloseArchive.restype = ctypes.c_int
_unrar.RARReadHeaderEx.argtypes = [c_void_p, POINTER(RARHeaderDataEx)]
_unrar.RARReadHeaderEx.restype = ctypes.c_int
_unrar.RARProcessFileW.argtypes = [c_void_p, ctypes.c_int, c_wchar_p, c_wchar_p]
_unrar.RARProcessFileW.restype = ctypes.c_int
_unrar.RARSetPassword.argtypes = [c_void_p, c_char_p]
_unrar.RARSetPassword.restype = None

class UnrarArchive:
    def __init__(self, path, password=None):
        self._o = RAROpenArchiveDataEx()
        self._o.ArcNameW = path
        self._o.OpenMode = RAR_OM_EXTRACT
        self._handle = _unrar.RAROpenArchiveEx(ctypes.byref(self._o))
        if not self._handle:
            raise RuntimeError(f"cannot open archive: {self._o.OpenResult}")
        if password:
            _unrar.RARSetPassword(self._handle, password.encode('utf-8'))

    def close(self):
        if self._handle:
            _unrar.RARCloseArchive(self._handle)
            self._handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def extract_all(self, dest_dir):
        hdr = RARHeaderDataEx()
        while True:
            res = _unrar.RARReadHeaderEx(self._handle, ctypes.byref(hdr))
            if res == ERAR_END_ARCHIVE:
                break
            if res != ERAR_SUCCESS:
                raise RuntimeError(f"read header error: {res}")
            res = _unrar.RARProcessFileW(self._handle, RAR_EXTRACT, dest_dir, None)
            if res == ERAR_BAD_PASSWORD:
                raise RuntimeError("bad password")
            if res != ERAR_SUCCESS:
                raise RuntimeError(f"extract error: {res}")

__all__ = ["UnrarArchive"]
