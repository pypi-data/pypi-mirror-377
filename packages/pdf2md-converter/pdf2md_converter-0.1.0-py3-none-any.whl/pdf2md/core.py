import os
import gc
from typing import List
from pathlib import Path
from datetime import datetime

import torch

from .renderer import Renderer
from .layout import LayoutDetector
from .ocr import OCR
from .markdownifier import to_markdown
from .exceptions import Pdf2MdError


class Pdf2Md:
    """
    Core orchestrator for the PDF to Markdown conversion process.
    """

    def __init__(self,
                 backend: str = 'trocr',
                 layout: str = 'lp_detectron',
                 device: str = 'cpu',
                 dpi: int = 300,
                 batch_size: int = 16):
        """
        Initializes the conversion pipeline.

        Args:
            backend (str): The OCR backend to use ('trocr', 'easyocr', 'pytesseract').
            layout (str): The layout detector to use ('lp_detectron', 'heuristic').
            device (str): The device to use for models ('cpu', 'cuda').
            dpi (int): The DPI for PDF rendering.
            batch_size (int): The batch size for OCR.
        """
        self.device = 'cuda' if device == 'cuda' and torch.cuda.is_available() else 'cpu'
        self.ocr = OCR(backend=backend, device=self.device)
        self.layout_detector = LayoutDetector(layout=layout)
        self.dpi = dpi
        self.batch_size = batch_size

    def convert(self, pdf_path: str, output_dir: str, pages: List[int] = None):
        """
        Converts a PDF file to a set of Markdown files, one per page.

        Args:
            pdf_path (str): The path to the input PDF file.
            output_dir (str): The directory to save the output files.
            pages (List[int]): A list of 1-based page numbers to convert.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        images_dir = output_path / "images"
        images_dir.mkdir(exist_ok=True)

        try:
            with Renderer(pdf_path) as renderer:
                total_pages = renderer.doc.page_count
                pages_to_convert = pages if pages else range(1, total_pages + 1)

                for page_num in pages_to_convert:
                    if not 1 <= page_num <= total_pages:
                        print(f"Warning: Page {page_num} is out of range. Skipping.")
                        continue

                    print(f"Converting page {page_num}...")
                    pil_image = renderer.render_page(page_num - 1, self.dpi)
                    blocks = self.layout_detector.detect(pil_image)

                    # Extract images and text blocks separately
                    image_blocks = [b for b in blocks if b['type'] == 'image']
                    text_blocks = [b for b in blocks if b['type'] == 'text']

                    # Process text blocks with OCR
                    if text_blocks:
                        crops = [pil_image.crop(b['bbox']) for b in text_blocks]
                        ocr_results = self.ocr.read_images_batch(crops, self.batch_size)
                        for i, result in enumerate(ocr_results):
                            text_blocks[i]['text'] = result

                    # Create a consolidated list of results for markdownifier
                    results = text_blocks + image_blocks

                    # Save images and update image block paths
                    for i, block in enumerate(image_blocks):
                        image_name = f"page_{page_num:03}_img_{i:02}.png"
                        image_path = images_dir / image_name
                        pil_image.crop(block['bbox']).save(image_path)
                        block['path'] = str(image_path)  # Relative path for Markdown
                        block['text'] = ""  # Clear text for image blocks

                    markdown_content = to_markdown(results)

                    output_file_path = output_path / f"page_{page_num:03}.md"
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)

                    # Explicitly release resources for the current page
                    del pil_image
                    gc.collect()

            # Final cleanup after all pages are processed
            self.ocr.close()
            if self.device == 'cuda' and torch.cuda.is_available():
                torch.cuda.empty_cache()  # IMPORTANT: Free GPU memory

        except Exception as e:
            raise Pdf2MdError(f"An error occurred during conversion: {e}") from e