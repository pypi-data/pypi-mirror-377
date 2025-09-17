# Base69

A Python package for Base69 encoding and decoding.

## Installation

```bash
pip install base69
```

## Usage

```python
from base69 import encode, decode

# Encode bytes to Base69
encoded = encode(b"Hello, World!")
print(encoded)

# Decode Base69 back to bytes
decoded = decode(encoded)
print(decoded)
```

## Development

To install for development:

```bash
pip install -e .
```

## License

MIT