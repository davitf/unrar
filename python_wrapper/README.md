# Python Unrar Wrapper

This directory contains a small ctypes based wrapper around the
`libunrar` library.  It exposes minimal functionality required for
extracting archives and is intended to be usable as a backend for the
[`rarfile`](https://github.com/markokr/rarfile) Python module.

```
from unrar import UnrarArchive

with UnrarArchive('test.rar') as archive:
    archive.extract_all('output_dir')
```

The wrapper expects a compiled `libunrar.so` in the project root.  Build
it with:

```
make lib
```

The file `test_unrar.py` demonstrates simple extraction using one of the
sample archives from the `rarfile` test-suite.
