# bitmapy

[![CI](https://github.com/oparsons22/bitmapy/actions/workflows/ci.yaml/badge.svg)](https://github.com/oparsons22/bitmapy/actions/workflows/ci.yaml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/bitmapy?label=PyPI%20-%20Downloads)


A lightweight Python library for bitmap manipulation and operations.

## Features

- Create and manage bitmaps in Python
- Set, clear, and toggle bits
- Efficient bitwise operations
- Type-annotated for better development experience
- Well-tested with pytest

## Installation

You can install bitmapy using pip:

```bash
pip install bitmapy
```

Or, for local development:

```bash
git clone https://github.com/oparsons22/bitmapy.git
cd bitmapy
uv sync --all-extras --dev
```

## Usage Example

Full functionality is available when using generic `enum.IntFlag`.

```python
from enum import IntFlag, auto
from bitmapy import Bitmap

class Permission(IntFlag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

# Create a bitmap with no permissions
bitmap = Bitmap[Permission]()

# Check if WRITE permission is set
if bitmap.is_set(Permission.WRITE):
    print("WRITE permission is enabled.")

# Add EXECUTE permission
bitmap.set(Permission.EXECUTE)

# Remove READ permission
bitmap.clear(Permission.READ)

# Toggle WRITE permission
bitmap.toggle(Permission.WRITE)

# Get the current value
print(f"Current permissions: {bitmap.value}")
```

## Testing

To run tests:

```bash
uv run pytest
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests on GitHub.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
