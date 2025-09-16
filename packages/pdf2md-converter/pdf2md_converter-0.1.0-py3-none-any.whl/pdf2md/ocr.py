import os
import gc
from typing import List, Union
from PIL import Image

import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

try:
    import easyocr

    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract

    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from .exceptions import Pdf2MdError


class OCR:
    """
    Handles OCR for different backends.
    """

    def __init__(self, backend: str, device: str = 'cpu'):
        self.backend = backend
        self.device = device
        self.processor = None
        self.model = None
        self.easyocr_reader = None

        if self.backend == 'trocr':
            self._load_trocr_model()
        elif self.backend == 'easyocr':
            self._load_easyocr_model()
        elif self.backend == 'pytesseract':
            if not PYTESSERACT_AVAILABLE:
                raise Pdf2MdError("Pytesseract backend selected but not installed. Please install 'pytesseract'.")

    def _load_trocr_model(self):
        # pdf2md --input documents/my_document.pdf --out output/ --backend trocr --layout lp_detectron (Not Fixed Yet)
        try:
            self.processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten", use_fast=True)
            self.model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            raise Pdf2MdError(f"Failed to load TrOCR model. Check network connection or model ID. Error: {e}")

    def _load_easyocr_model(self):
        if not EASYOCR_AVAILABLE:
            raise Pdf2MdError("EasyOCR backend selected but not installed. Please install 'easyocr' and 'Pillow'.")
        try:
            self.easyocr_reader = easyocr.Reader(['en'], gpu=(self.device == 'cuda'))
        except Exception as e:
            raise Pdf2MdError(f"Failed to load EasyOCR model. Error: {e}")

    def read_images_batch(self, images: List[Image.Image], batch_size: int = 16) -> List[str]:
        """
        Reads a batch of images using the configured backend.
        """
        if self.backend == 'trocr':
            return self._run_trocr_batch(images, batch_size)
        elif self.backend == 'easyocr':
            return self._run_easyocr_batch(images)
        elif self.backend == 'pytesseract':
            return self._run_pytesseract_batch(images)
        return []

    def _run_trocr_batch(self, images: List[Image.Image], batch_size: int) -> List[str]:
        texts = []
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i + batch_size]

            with torch.no_grad():
                pixel_values = self.processor(images=batch_images, return_tensors="pt").pixel_values
                pixel_values = pixel_values.to(self.device)

                generated_ids = self.model.generate(pixel_values)
                batch_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
                texts.extend(batch_texts)
        return texts

    def _run_easyocr_batch(self, images: List[Image.Image]) -> List[str]:
        texts = []
        for img in images:
            results = self.easyocr_reader.readtext(img, detail=0)
            texts.append(" ".join(results))
        return texts

    def _run_pytesseract_batch(self, images: List[Image.Image]) -> List[str]:
        texts = []
        for img in images:
            texts.append(pytesseract.image_to_string(img))
        return texts

    def close(self):
        """
        Explicitly cleans up resources, especially for GPU models.
        """
        if self.backend == 'trocr' and self.model:
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            gc.collect()
            if self.device == 'cuda':
                torch.cuda.empty_cache()  # IMPORTANT: Free GPU memory
        elif self.backend == 'easyocr' and self.easyocr_reader:
            del self.easyocr_reader
            self.easyocr_reader = None
            gc.collect()