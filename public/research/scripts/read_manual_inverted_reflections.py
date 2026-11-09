#!/usr/bin/env python3
from pathlib import Path

import fitz
from PIL import Image

from read_reflected_masks import PDF, PDF_PAGE_INDEX, PAGES, hflip_box, image_box_to_pdf_rect, words_in_rect, chars_in_rect


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs'


# Approximate image-coordinate boxes for black/white inverted highlight blocks.
# These are deliberately generous because the OCR layer is word-based.
INVERTED_BOXES = {
    75: [
        (940, 950, 1475, 1000),   # money printers, banking
        (250, 1005, 1370, 1060),  # terrorists... central bank arsonists
        (330, 1858, 900, 1912),   # Don't fall for shitcoinery
    ],
    76: [
        (360, 640, 1780, 690),    # Gotta be this way...
        (300, 690, 560, 745),     # nonsense
        (800, 1165, 1495, 1220),  # It's a stun gun...
        (330, 2185, 650, 2240),   # $1 billion
        (830, 2305, 1335, 2365),  # Volcano Bonds
    ],
    77: [
        (200, 575, 1470, 680),    # sorry Bhutan...
        (820, 1090, 1550, 1165),  # shitcoiners, useless Royals
        (800, 2480, 1510, 2545),  # It does this by monetizing
    ],
    78: [
        (1140, 805, 1675, 855),   # gargantuanly wasteful
        (565, 855, 910, 915),     # money printing
        (990, 855, 1465, 915),    # wars to keep it going
    ],
    79: [
        (1080, 325, 1450, 380),   # war and violence economy
    ],
}


def reflected_selection(source_page, target_page):
    source_img = Image.open(PAGES[source_page]).convert('RGB')
    target_img = Image.open(PAGES[target_page]).convert('RGB')
    doc = fitz.open(PDF)
    target_pdf_rect = doc[PDF_PAGE_INDEX[target_page]].rect
    results = []
    for idx, box in enumerate(INVERTED_BOXES.get(source_page, []), 1):
        reflected = hflip_box(box, source_img.width)
        rect = image_box_to_pdf_rect(reflected, target_img.size, target_pdf_rect)
        text = words_in_rect(doc, target_page, rect)
        chars = chars_in_rect(doc, target_page, rect)
        results.append((idx, box, reflected, text, chars))
    return results


def main():
    lines = []
    for source, target in [(79, 75), (75, 79), (78, 76), (76, 78), (77, 77)]:
        lines.append(f'\nSOURCE {source} inverted reflected onto TARGET {target}')
        joined = []
        for idx, box, reflected, text, chars in reflected_selection(source, target):
            lines.append(f'{idx:02d} src={box} reflected={reflected} -> {text}')
            lines.append(f'   chars -> {chars}')
            if text:
                joined.append(text)
        lines.append('JOINED: ' + ' / '.join(joined))
    report = '\n'.join(lines) + '\n'
    (OUT / 'manual_inverted_reflection_text_report.txt').write_text(report)
    print(report)


if __name__ == '__main__':
    main()
