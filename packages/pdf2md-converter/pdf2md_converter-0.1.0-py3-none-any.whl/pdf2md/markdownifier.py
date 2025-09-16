import re
from typing import List, Dict, Any


def to_markdown(blocks: List[Dict[str, Any]]) -> str:
    """
    Converts a list of text/image blocks into a single Markdown string.

    Args:
        blocks (List[Dict]): A list of dictionaries with 'text' and 'type'.
                             Image blocks have a 'path'.

    Returns:
        str: The Markdown formatted string.
    """
    markdown_lines = []

    # Sort blocks by vertical position to ensure correct reading order
    blocks.sort(key=lambda b: b['bbox'][1])

    for block in blocks:
        if block['type'] == 'text':
            text = block.get('text', '').strip()
            if not text:
                continue

            lines = text.split('\n')

            # Apply basic heuristics
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Heuristic 1: All-caps short line might be a header
                if len(line) < 50 and line.isupper() and ' ' in line:
                    markdown_lines.append(f"## {line}\n")
                # Heuristic 2: Lines starting with a bullet or number
                elif re.match(r'^\s*[-*]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                    markdown_lines.append(f"{line}\n")
                # Default: regular paragraph
                else:
                    markdown_lines.append(f"{line}\n")

            markdown_lines.append("\n")  # Add a paragraph break

        elif block['type'] == 'image':
            image_path = block.get('path')
            if image_path:
                markdown_lines.append(f"![Image from PDF]({image_path})\n\n")

    return "".join(markdown_lines)