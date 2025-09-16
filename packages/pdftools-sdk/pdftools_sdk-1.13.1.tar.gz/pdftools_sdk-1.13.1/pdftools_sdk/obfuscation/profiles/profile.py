from __future__ import annotations
import io
from typing import List, Iterator, Tuple, Optional, Any, TYPE_CHECKING, Callable
from ctypes import *
from datetime import datetime
from numbers import Number
from pdftools_sdk.internal import _lib
from pdftools_sdk.internal.utils import _string_to_utf16, _utf16_to_string
from pdftools_sdk.internal.streams import _StreamDescriptor, _NativeStream
from pdftools_sdk.internal.native_base import _NativeBase
from pdftools_sdk.internal.native_object import _NativeObject

import pdftools_sdk.internal

class _Profile(_NativeObject):
    """
    A profile defines the processor's obfuscation settings.


    """
    @staticmethod
    def _create_dynamic_type(handle):
        _lib.PdfToolsObfuscationProfiles_Profile_GetType.argtypes = [c_void_p]
        _lib.PdfToolsObfuscationProfiles_Profile_GetType.restype = c_int

        obj_type = _lib.PdfToolsObfuscationProfiles_Profile_GetType(handle)
        # Create and return the object based on the type
        if obj_type == 0:
            return _Profile._from_handle(handle)
        elif obj_type == 1:
            from pdftools_sdk.obfuscation.profiles._e_bill import _EBill 
            return _EBill._from_handle(handle)
        else:
            return None


    @classmethod
    def _from_handle(cls, handle):
        """
        Internal factory method for constructing an instance using an internal handle.
        This method creates an instance of the class by bypassing the public constructor.
        """
        instance = _Profile.__new__(cls)  # Bypass __init__
        instance._initialize(handle)
        return instance

    def _initialize(self, handle):
        super()._initialize(handle)
