import argparse
from pathlib import Path

from .core import Pdf2Md
from .exceptions import Pdf2MdError

def main():
    parser = argparse.ArgumentParser(
        description="Convert a PDF to Markdown using advanced OCR and layout detection."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input PDF file."
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Path to the output directory to save Markdown files."
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=['trocr', 'easyocr', 'pytesseract'],
        default='trocr',
        help="The OCR backend to use (default: trocr)."
    )
    parser.add_argument(
        "--layout",
        type=str,
        choices=['lp_detectron', 'heuristic'],
        default='heuristic',
        help="The layout detection method (default: heuristic)."
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=['cpu', 'cuda'],
        default='cpu',
        help="The device to use for processing (default: cpu). Use 'cuda' for GPU."
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for rendering the PDF pages (default: 300)."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size for OCR processing (default: 16)."
    )
    parser.add_argument(
        "--pages",
        type=str,
        help="Comma-separated list of 1-based page numbers to convert (e.g., '1,3,5')."
    )

    args = parser.parse_args()

    # Process pages argument
    pages = None
    if args.pages:
        try:
            pages = [int(p) for p in args.pages.split(',')]
        except ValueError:
            print("Error: --pages must be a comma-separated list of integers.")
            return

    try:
        converter = Pdf2Md(
            backend=args.backend,
            layout=args.layout,
            device=args.device,
            dpi=args.dpi,
            batch_size=args.batch_size
        )
        converter.convert(args.input, args.out, pages)
        print(f"Conversion complete. Markdown files saved to {Path(args.out).resolve()}")
    except Pdf2MdError as e:
        print(f"Conversion failed: {e}")

if __name__ == "__main__":
    main()