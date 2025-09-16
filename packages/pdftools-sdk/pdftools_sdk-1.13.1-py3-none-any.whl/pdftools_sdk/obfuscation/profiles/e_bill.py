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
import pdftools_sdk.obfuscation.profiles.profile

class _EBill(pdftools_sdk.obfuscation.profiles.profile._Profile):
    """
    The profile for the eBill use case.


    """
    def __init__(self):
        """


        """
        _lib.PdfToolsObfuscationProfiles_EBill_New.argtypes = []
        _lib.PdfToolsObfuscationProfiles_EBill_New.restype = c_void_p
        ret_val = _lib.PdfToolsObfuscationProfiles_EBill_New()
        if ret_val is None:
            _NativeBase._throw_last_error(False)
        super()._initialize(ret_val)


    @property
    def _remove_uri_links(self) -> bool:
        """
        Whether to remove URI links

         
        Whether to remove all links to external URIs.
        Links within the document, e.g. from the bookmaks, are preserved.
         
        The visual appearance of the document is preserved.
         
        Note that some viewers, e.g. Adobe Acrobat, identify URIs in the document's extractable text.
        Those viewers convert the detected text parts to interactive links.
        This behavior cannot be disabled.
        However, it can be made impossible by obfuscating text using the :attr:`pdftools_sdk.obfuscation.profiles.e_bill._EBill._obfuscate_text` .
         
        Default is `False`



        Returns:
            bool

        """
        _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveUriLinks.argtypes = [c_void_p]
        _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveUriLinks.restype = c_bool
        ret_val = _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveUriLinks(self._handle)
        if not ret_val:
            _NativeBase._throw_last_error()
        return ret_val



    @_remove_uri_links.setter
    def _remove_uri_links(self, val: bool) -> None:
        """
        Whether to remove URI links

         
        Whether to remove all links to external URIs.
        Links within the document, e.g. from the bookmaks, are preserved.
         
        The visual appearance of the document is preserved.
         
        Note that some viewers, e.g. Adobe Acrobat, identify URIs in the document's extractable text.
        Those viewers convert the detected text parts to interactive links.
        This behavior cannot be disabled.
        However, it can be made impossible by obfuscating text using the :attr:`pdftools_sdk.obfuscation.profiles.e_bill._EBill._obfuscate_text` .
         
        Default is `False`



        Args:
            val (bool):
                property value

        """
        if not isinstance(val, bool):
            raise TypeError(f"Expected type {bool.__name__}, but got {type(val).__name__}.")
        _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveUriLinks.argtypes = [c_void_p, c_bool]
        _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveUriLinks.restype = c_bool
        if not _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveUriLinks(self._handle, val):
            _NativeBase._throw_last_error(False)

    @property
    def _obfuscate_text(self) -> bool:
        """
        Whether to obfuscate text

         
        Obfuscated text cannot be extracted anymore,
        so copy-and-paste of text and text search are prevented.
        The visual appearance of the document is preserved.
         
        Obfuscated text reliably prevents the detection of URIs in the document (see :attr:`pdftools_sdk.obfuscation.profiles.e_bill._EBill._remove_uri_links` ).
        However, because the visual appearance of the document is preserved, the text can be made
        extractable again, e.g. using OCR technology.
         
        This feature is only available for PDF/A conforming documents. The conformance level of documents is downgraded
        to level B, because levels U (Unicode) and A (Accessibility) do not allow obfuscated text.
         
        Default is `False`



        Returns:
            bool

        """
        _lib.PdfToolsObfuscationProfiles_EBill_GetObfuscateText.argtypes = [c_void_p]
        _lib.PdfToolsObfuscationProfiles_EBill_GetObfuscateText.restype = c_bool
        ret_val = _lib.PdfToolsObfuscationProfiles_EBill_GetObfuscateText(self._handle)
        if not ret_val:
            _NativeBase._throw_last_error()
        return ret_val



    @_obfuscate_text.setter
    def _obfuscate_text(self, val: bool) -> None:
        """
        Whether to obfuscate text

         
        Obfuscated text cannot be extracted anymore,
        so copy-and-paste of text and text search are prevented.
        The visual appearance of the document is preserved.
         
        Obfuscated text reliably prevents the detection of URIs in the document (see :attr:`pdftools_sdk.obfuscation.profiles.e_bill._EBill._remove_uri_links` ).
        However, because the visual appearance of the document is preserved, the text can be made
        extractable again, e.g. using OCR technology.
         
        This feature is only available for PDF/A conforming documents. The conformance level of documents is downgraded
        to level B, because levels U (Unicode) and A (Accessibility) do not allow obfuscated text.
         
        Default is `False`



        Args:
            val (bool):
                property value

        """
        if not isinstance(val, bool):
            raise TypeError(f"Expected type {bool.__name__}, but got {type(val).__name__}.")
        _lib.PdfToolsObfuscationProfiles_EBill_SetObfuscateText.argtypes = [c_void_p, c_bool]
        _lib.PdfToolsObfuscationProfiles_EBill_SetObfuscateText.restype = c_bool
        if not _lib.PdfToolsObfuscationProfiles_EBill_SetObfuscateText(self._handle, val):
            _NativeBase._throw_last_error(False)

    @property
    def _remove_embedded_files(self) -> bool:
        """
        Whether to remove all embedded files

         
        Removing embedded files from a PDF collection (portfolio) results in an error.
        Since PDF collections are merely a collection of embedded files,
        removing them would result in an invalid PDF document.
         
        Default is `False`



        Returns:
            bool

        """
        _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveEmbeddedFiles.argtypes = [c_void_p]
        _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveEmbeddedFiles.restype = c_bool
        ret_val = _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveEmbeddedFiles(self._handle)
        if not ret_val:
            _NativeBase._throw_last_error()
        return ret_val



    @_remove_embedded_files.setter
    def _remove_embedded_files(self, val: bool) -> None:
        """
        Whether to remove all embedded files

         
        Removing embedded files from a PDF collection (portfolio) results in an error.
        Since PDF collections are merely a collection of embedded files,
        removing them would result in an invalid PDF document.
         
        Default is `False`



        Args:
            val (bool):
                property value

        """
        if not isinstance(val, bool):
            raise TypeError(f"Expected type {bool.__name__}, but got {type(val).__name__}.")
        _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveEmbeddedFiles.argtypes = [c_void_p, c_bool]
        _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveEmbeddedFiles.restype = c_bool
        if not _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveEmbeddedFiles(self._handle, val):
            _NativeBase._throw_last_error(False)

    @property
    def _remove_signature_appearances(self) -> bool:
        """
        Whether to remove signature apperances

         
        During obfuscation, the PDF is altered and hence its digital signatures are broken.
         
        If this property is set to `False` the visual appearance of the signature is preserved
        by flattening it, i.e. it is drawn as non-editable stamp onto the page.
         
        If this property is set to `True` the visual appearance of the signature is removed.
         
        Default is `False`



        Returns:
            bool

        """
        _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveSignatureAppearances.argtypes = [c_void_p]
        _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveSignatureAppearances.restype = c_bool
        ret_val = _lib.PdfToolsObfuscationProfiles_EBill_GetRemoveSignatureAppearances(self._handle)
        if not ret_val:
            _NativeBase._throw_last_error()
        return ret_val



    @_remove_signature_appearances.setter
    def _remove_signature_appearances(self, val: bool) -> None:
        """
        Whether to remove signature apperances

         
        During obfuscation, the PDF is altered and hence its digital signatures are broken.
         
        If this property is set to `False` the visual appearance of the signature is preserved
        by flattening it, i.e. it is drawn as non-editable stamp onto the page.
         
        If this property is set to `True` the visual appearance of the signature is removed.
         
        Default is `False`



        Args:
            val (bool):
                property value

        """
        if not isinstance(val, bool):
            raise TypeError(f"Expected type {bool.__name__}, but got {type(val).__name__}.")
        _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveSignatureAppearances.argtypes = [c_void_p, c_bool]
        _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveSignatureAppearances.restype = c_bool
        if not _lib.PdfToolsObfuscationProfiles_EBill_SetRemoveSignatureAppearances(self._handle, val):
            _NativeBase._throw_last_error(False)


    @staticmethod
    def _create_dynamic_type(handle):
        return _EBill._from_handle(handle)


    @classmethod
    def _from_handle(cls, handle):
        """
        Internal factory method for constructing an instance using an internal handle.
        This method creates an instance of the class by bypassing the public constructor.
        """
        instance = _EBill.__new__(cls)  # Bypass __init__
        instance._initialize(handle)
        return instance

    def _initialize(self, handle):
        super()._initialize(handle)
