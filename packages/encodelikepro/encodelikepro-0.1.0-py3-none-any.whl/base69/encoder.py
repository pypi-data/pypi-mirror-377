"""Base69 encoder implementation."""

import string

BASE69_CHARSET = string.ascii_letters + string.digits + "!@#$%^&"


class Base69Encoder:
    """Encoder for Base69 format."""
    
    def __init__(self):
        self.charset = BASE69_CHARSET
        self.base = len(self.charset)
    
    def encode(self, data: bytes) -> str:
        """Encode bytes to Base69 string."""
        if not data:
            return ""
        
        # Convert bytes to integer
        num = int.from_bytes(data, byteorder='big')
        
        if num == 0:
            return self.charset[0]
        
        result = []
        while num > 0:
            result.append(self.charset[num % self.base])
            num //= self.base
        
        return ''.join(reversed(result))


def encode(data: bytes) -> str:
    """Convenience function to encode bytes to Base69."""
    encoder = Base69Encoder()
    return encoder.encode(data)