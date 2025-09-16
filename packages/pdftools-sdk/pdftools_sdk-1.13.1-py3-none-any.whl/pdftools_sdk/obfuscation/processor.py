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

if TYPE_CHECKING:
    from pdftools_sdk.pdf.document import Document
    from pdftools_sdk.obfuscation.profiles.profile import _Profile
    from pdftools_sdk.pdf.output_options import OutputOptions

else:
    Document = "pdftools_sdk.pdf.document.Document"
    _Profile = "pdftools_sdk.obfuscation.profiles.profile._Profile"
    OutputOptions = "pdftools_sdk.pdf.output_options.OutputOptions"


class _Processor(_NativeObject):
    """
    Processor to obfuscate PDF documents.


    """
    def __init__(self):
        """


        """
        _lib.PdfToolsObfuscation_Processor_New.argtypes = []
        _lib.PdfToolsObfuscation_Processor_New.restype = c_void_p
        ret_val = _lib.PdfToolsObfuscation_Processor_New()
        if ret_val is None:
            _NativeBase._throw_last_error(False)
        super()._initialize(ret_val)


    def _process_document(self, in_doc: Document, out_stream: io.IOBase, profile: _Profile, out_options: Optional[OutputOptions] = None) -> Document:
        """
        Obfuscate the document



        Args:
            inDoc (pdftools_sdk.pdf.document.Document): 
                The input PDF document.

            outStream (io.IOBase): 
                The stream to which the output PDF is written.

            profile (pdftools_sdk.obfuscation.profiles.profile._Profile): 
                The profile defining the processing settings.

            outOptions (Optional[pdftools_sdk.pdf.output_options.OutputOptions]): 
                Optional PDF output options.
                If `None`, default options are used.



        Returns:
            pdftools_sdk.pdf.document.Document: 
                 
                The obfuscated result PDF, which can be used
                as a new input for further processing.
                 
                Note that, this object must be disposed before the output stream
                object (method argument `outStream`).



        Raises:
            pdftools_sdk.license_error.LicenseError:
                The license check has failed.

            pdftools_sdk.processing_error.ProcessingError:
                The processing has failed.

            OSError:
                Writing to the output PDF has failed.

            pdftools_sdk.unsupported_feature_error.UnsupportedFeatureError:
                The input PDF is a collection (portfolio) and :attr:`pdftools_sdk.obfuscation.profiles.e_bill._EBill._remove_embedded_files`  is `True`.

            pdftools_sdk.unsupported_feature_error.UnsupportedFeatureError:
                The input PDF contains unrendered XFA form fields.
                See :attr:`pdftools_sdk.pdf.document.Document.xfa`  for more information on how to detect and handle XFA documents.

            pdftools_sdk.generic_error.GenericError:
                A generic error occurred.

            pdftools_sdk.conformance_error.ConformanceError:
                The input document's conformance is not supported:
                 
                - :attr:`pdftools_sdk.obfuscation.profiles.e_bill._EBill._obfuscate_text`  is `True` but the input document is not PDF/A.
                 


        """
        from pdftools_sdk.pdf.document import Document
        from pdftools_sdk.obfuscation.profiles.profile import _Profile
        from pdftools_sdk.pdf.output_options import OutputOptions

        if not isinstance(in_doc, Document):
            raise TypeError(f"Expected type {Document.__name__}, but got {type(in_doc).__name__}.")
        if not isinstance(out_stream, io.IOBase):
            raise TypeError(f"Expected type {io.IOBase.__name__}, but got {type(out_stream).__name__}.")
        if not isinstance(profile, _Profile):
            raise TypeError(f"Expected type {_Profile.__name__}, but got {type(profile).__name__}.")
        if out_options is not None and not isinstance(out_options, OutputOptions):
            raise TypeError(f"Expected type {OutputOptions.__name__} or None, but got {type(out_options).__name__}.")

        _lib.PdfToolsObfuscation_Processor_ProcessDocument.argtypes = [c_void_p, c_void_p, POINTER(pdftools_sdk.internal.streams._StreamDescriptor), c_void_p, c_void_p]
        _lib.PdfToolsObfuscation_Processor_ProcessDocument.restype = c_void_p
        ret_val = _lib.PdfToolsObfuscation_Processor_ProcessDocument(self._handle, in_doc._handle, _StreamDescriptor(out_stream), profile._handle, out_options._handle if out_options is not None else None)
        if ret_val is None:
            _NativeBase._throw_last_error(False)
        return Document._create_dynamic_type(ret_val)



    @staticmethod
    def _create_dynamic_type(handle):
        return _Processor._from_handle(handle)


    @classmethod
    def _from_handle(cls, handle):
        """
        Internal factory method for constructing an instance using an internal handle.
        This method creates an instance of the class by bypassing the public constructor.
        """
        instance = _Processor.__new__(cls)  # Bypass __init__
        instance._initialize(handle)
        return instance

    def _initialize(self, handle):
        super()._initialize(handle)
