from PIL import Image
from typing import List, Dict, Any

try:
    import layoutparser as lp

    LAYOUTPARSER_AVAILABLE = True
except ImportError:
    LAYOUTPARSER_AVAILABLE = False

from .exceptions import Pdf2MdError


class LayoutDetector:
    """
    Detects layout blocks (text, image, table) on a PIL image.
    """

    def __init__(self, layout: str = 'heuristic'):
        self.layout_type = layout
        self.model = None
        if self.layout_type == 'lp_detectron' and LAYOUTPARSER_AVAILABLE:
            try:
                self.model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_R_50_FPN_3x/config',
                                                      extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                                                      label_map={0: "text", 1: "title", 2: "list", 3: "table",
                                                                 4: "figure"})
            except Exception as e:
                print(f"Warning: Failed to load layoutparser model. Falling back to heuristic. Error: {e}")
                self.layout_type = 'heuristic'
                self.model = None

    def detect(self, pil_image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detects layout blocks.

        Args:
            pil_image (Image.Image): The input image.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a block with
                                  'bbox' (x1,y1,x2,y2) and 'type' ('text'|'image'|'table').
        """
        if self.layout_type == 'lp_detectron' and self.model:
            layout_blocks = self.model.detect(pil_image)
            blocks = []
            for block in layout_blocks:
                # Convert layoutparser blocks to our internal format
                bbox = (int(block.block.x_1), int(block.block.y_1), int(block.block.x_2), int(block.block.y_2))
                block_type = 'text'  # Default to text
                if block.type in ['figure', 'table']:
                    block_type = 'image' if block.type == 'figure' else 'table'
                blocks.append({'bbox': bbox, 'type': block_type})
            return blocks
        else:
            # Heuristic fallback: Treat the entire page as a single text block.
            width, height = pil_image.size
            return [{'bbox': (0, 0, width, height), 'type': 'text'}]