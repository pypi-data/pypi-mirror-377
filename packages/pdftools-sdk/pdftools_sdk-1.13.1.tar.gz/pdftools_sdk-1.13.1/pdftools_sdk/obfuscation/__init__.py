import pdftools_sdk.obfuscation.profiles

def _import_types():
    global _Processor
    from pdftools_sdk.obfuscation.processor import _Processor

    pdftools_sdk.obfuscation.profiles._import_types()

