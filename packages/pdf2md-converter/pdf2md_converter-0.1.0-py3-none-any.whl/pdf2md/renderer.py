import fitz  # PyMuPDF
from PIL import Image
from typing import Iterator

from .exceptions import Pdf2MdError


class Renderer:
    """
    Context manager for rendering PDF pages to PIL images using PyMuPDF.
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None

    def __enter__(self) -> 'Renderer':
        try:
            self.doc = fitz.open(self.pdf_path)
            return self
        except fitz.FileNotFoundError:
            raise Pdf2MdError(f"PDF file not found at: {self.pdf_path}")
        except Exception as e:
            raise Pdf2MdError(f"Failed to open PDF file: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.doc:
            self.doc.close()

    def render_page(self, page_index: int, dpi: int = 300) -> Image.Image:
        """
        Renders a single PDF page as a high-resolution PIL Image.

        Args:
            page_index (int): The 0-based index of the page to render.
            dpi (int): The desired dots-per-inch for the rendered image.

        Returns:
            Image.Image: The rendered page as a Pillow image.
        """
        page = self.doc.load_page(page_index)
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Explicitly delete pixmap to free C++ memory
        del pix

        return pil_image