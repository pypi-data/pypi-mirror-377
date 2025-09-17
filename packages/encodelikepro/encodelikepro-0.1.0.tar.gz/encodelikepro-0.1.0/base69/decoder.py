"""Base69 decoder implementation."""

import string

BASE69_CHARSET = string.ascii_letters + string.digits + "!@#$%^&"


class Base69Decoder:
    """Decoder for Base69 format."""
    
    def __init__(self):
        self.charset = BASE69_CHARSET
        self.base = len(self.charset)
        self.char_to_value = {char: idx for idx, char in enumerate(self.charset)}
    
    def decode(self, encoded: str) -> bytes:
        """Decode Base69 string to bytes."""
        if not encoded:
            return b""
        
        # Convert from base69 to integer
        num = 0
        for char in encoded:
            if char not in self.char_to_value:
                raise ValueError(f"Invalid character in Base69 string: {char}")
            num = num * self.base + self.char_to_value[char]
        
        # Convert integer to bytes
        if num == 0:
            return b"\x00"
        
        # Calculate required byte length
        byte_length = (num.bit_length() + 7) // 8
        return num.to_bytes(byte_length, byteorder='big')


def decode(encoded: str) -> bytes:
    """Convenience function to decode Base69 to bytes."""
    decoder = Base69Decoder()
    return decoder.decode(encoded)