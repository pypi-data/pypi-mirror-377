import os
import platform
from ctypes import *

def _string_to_utf16(s):
    if s is None:
        return None
    if platform.system() == "Windows":
        return c_wchar_p(s)
    else:
        utf16le_encoded = s.encode('utf-16le') + b'\x00\x00'
        buffer = create_string_buffer(utf16le_encoded)
        return cast(buffer, c_wchar_p)

def _utf16_to_string(buffer, length=None):
    if buffer is None:
        return None
    if platform.system() == "Windows":
        if length is not None:
            s = wstring_at(buffer, length)
        else:
            s = wstring_at(buffer)
    else:
        if length is not None:
            utf16le_bytes = string_at(buffer, length * 2)
        else:
            utf16le_bytes = string_at(buffer)

        s = utf16le_bytes.decode('utf-16le')

    # Strip trailing null if present
    return s.rstrip('\x00')
