#!/usr/bin/env python3
from functools import lru_cache
from pathlib import Path
import ast

import fitz
from PIL import Image

from extract_visual_masks import PAGES, masks_for_page, connected_components, merge_close_boxes


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'keyser bitcoin .pdf'
OUT = ROOT / 'analysis_outputs'

PDF_PAGE_INDEX = {
    75: 2,
    76: 3,
    77: 4,
    78: 5,
    79: 6,
    80: 7,
}


@lru_cache(maxsize=None)
def orange_boxes(page_no):
    img = Image.open(PAGES[page_no]).convert('RGB')
    cached = cached_orange_boxes(page_no)
    if cached:
        boxes = cached
    else:
        mask = masks_for_page(img)['orange']
        comps = connected_components(mask, min_area=100)
        boxes = merge_close_boxes(comps, y_gap=16, x_gap=26)
    filtered = []
    for box in boxes:
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        if width < 20 or height < 8:
            continue
        if width > img.width * 0.95 or height > img.height * 0.35:
            continue
        # Drop page decorations accidentally caught as orange.
        if y1 < 150 or x1 > img.width - 120:
            continue
        filtered.append(box)
    return filtered, img.size


@lru_cache(maxsize=None)
def cached_orange_boxes(page_no):
    report = OUT / 'visual_mask_report.txt'
    if not report.exists():
        return []
    boxes = []
    active = False
    for line in report.read_text().splitlines():
        if line.startswith('page '):
            active = line.startswith(f'page {page_no} orange:')
            continue
        if not active:
            continue
        stripped = line.strip()
        if not stripped or '(' not in stripped:
            continue
        boxes.append(tuple(ast.literal_eval(stripped.split(' ', 1)[1])))
    return boxes


def hflip_box(box, width):
    x1, y1, x2, y2 = box
    return (width - x2, y1, width - x1, y2)


def image_box_to_pdf_rect(box, image_size, pdf_rect):
    w, h = image_size
    sx = pdf_rect.width / w
    sy = pdf_rect.height / h
    x1, y1, x2, y2 = box
    return fitz.Rect(x1 * sx, y1 * sy, x2 * sx, y2 * sy)


def words_in_rect(doc, page_no, rect, min_overlap=0.20):
    page = doc[PDF_PAGE_INDEX[page_no]]
    out = []
    for word in page.get_text('words'):
        wrect = fitz.Rect(word[:4])
        inter = wrect & rect
        if inter.is_empty:
            continue
        overlap = inter.get_area() / max(1.0, wrect.get_area())
        center_inside = rect.contains(wrect.tl + (wrect.br - wrect.tl) * 0.5)
        if center_inside or overlap >= min_overlap:
            text = word[4]
            # Skip vertical running headers and obvious OCR junk from margins.
            if len(text) <= 1 and not text.isalnum():
                continue
            out.append((wrect.y0, wrect.x0, text))
    return ' '.join(text for _, _, text in sorted(out))


def chars_in_rect(doc, page_no, rect):
    page = doc[PDF_PAGE_INDEX[page_no]]
    raw_chars = []
    for block in page.get_text('rawdict').get('blocks', []):
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                for ch in span.get('chars', []):
                    bbox = fitz.Rect(ch['bbox'])
                    if bbox.is_empty:
                        continue
                    center = bbox.tl + (bbox.br - bbox.tl) * 0.5
                    if rect.contains(center):
                        raw_chars.append((bbox.y0, bbox.x0, ch.get('c', '')))
    if raw_chars:
        lines = []
        current = []
        current_y = None
        for y, x, ch in sorted(raw_chars):
            if current_y is None or abs(y - current_y) <= 2.5:
                current.append((x, ch))
                current_y = y if current_y is None else current_y
            else:
                lines.append(''.join(c for _, c in sorted(current)).strip())
                current = [(x, ch)]
                current_y = y
        if current:
            lines.append(''.join(c for _, c in sorted(current)).strip())
        return ' '.join(line for line in lines if line)

    # Fallback for OCR layers without per-character boxes.
    chars = []
    for word in page.get_text('words'):
        wrect = fitz.Rect(word[:4])
        text = word[4]
        if not text:
            continue
        char_width = wrect.width / max(1, len(text))
        selected = []
        for idx, ch in enumerate(text):
            cx = wrect.x0 + (idx + 0.5) * char_width
            cy = (wrect.y0 + wrect.y1) / 2
            if rect.contains(fitz.Point(cx, cy)):
                selected.append(ch)
        if selected:
            chars.append((wrect.y0, wrect.x0, ''.join(selected)))
    return ' '.join(text for _, _, text in sorted(chars))


def reflected_selection(source_page, target_page):
    boxes, source_size = orange_boxes(source_page)
    target_img = Image.open(PAGES[target_page]).convert('RGB')
    doc = fitz.open(PDF)
    target_pdf_rect = doc[PDF_PAGE_INDEX[target_page]].rect
    results = []
    for idx, box in enumerate(boxes, 1):
        reflected = hflip_box(box, source_size[0])
        rect = image_box_to_pdf_rect(reflected, target_img.size, target_pdf_rect)
        text = words_in_rect(doc, target_page, rect)
        chars = chars_in_rect(doc, target_page, rect)
        results.append((idx, box, reflected, text, chars))
    return results


def main():
    lines = []
    for source, target in [(79, 75), (75, 79), (78, 76), (76, 78), (78, 75), (79, 76)]:
        lines.append(f'\nSOURCE {source} orange reflected onto TARGET {target}')
        joined = []
        for idx, box, reflected, text, chars in reflected_selection(source, target):
            lines.append(f'{idx:02d} src={box} reflected={reflected} -> {text}')
            lines.append(f'   chars -> {chars}')
            if text:
                joined.append(text)
        lines.append('JOINED: ' + ' / '.join(joined))
    report = '\n'.join(lines) + '\n'
    (OUT / 'reflected_mask_text_report.txt').write_text(report)
    print(report)


if __name__ == '__main__':
    main()
