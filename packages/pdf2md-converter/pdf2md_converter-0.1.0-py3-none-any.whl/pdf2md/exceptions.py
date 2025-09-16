# src/pdf2md/exceptions.py

class Pdf2MdError(Exception):
    """
    Custom exception for errors specific to the pdf2md conversion process.
    """
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception