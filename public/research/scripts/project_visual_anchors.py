#!/usr/bin/env python3
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from highres_reflection_extract import (
    SOURCE_PAGES,
    ensure_highres_sources,
    fit_mapping_for_page,
    map_box,
    orange_boxes,
)
from read_reflected_masks import PDF as OCR_PDF, PDF_PAGE_INDEX, PAGES as OCR_IMAGES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'source_audit'
OUT.mkdir(parents=True, exist_ok=True)


# Manual visual anchors from the Canva branch. These are the obvious non-text
# page-art marks visible in the high-res 76/79 mirrored overlay.
ANCHORS = [
    {'id': 'p79_pill_1', 'page': 79, 'box': (146, 2370, 196, 2446), 'kind': 'pill'},
    {'id': 'p79_pill_2', 'page': 79, 'box': (387, 2429, 456, 2480), 'kind': 'pill'},
    {'id': 'p79_pill_3', 'page': 79, 'box': (577, 2576, 635, 2641), 'kind': 'pill'},
    {'id': 'p79_pill_4', 'page': 79, 'box': (408, 2746, 466, 2815), 'kind': 'pill'},
    {'id': 'p79_pill_5', 'page': 79, 'box': (161, 2935, 206, 3001), 'kind': 'pill'},
    {'id': 'p76_small_x', 'page': 76, 'box': (2173, 2619, 2544, 2884), 'kind': 'x_mark'},
    {'id': 'p76_dollar', 'page': 76, 'box': (1827, 3003, 2120, 3181), 'kind': 'dollar'},
    {'id': 'p76_black_bar_1', 'page': 76, 'box': (1729, 835, 2215, 884), 'kind': 'black_bar'},
    {'id': 'p76_black_bar_2', 'page': 76, 'box': (1729, 1495, 1859, 1542), 'kind': 'black_bar'},
]


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def reflect_point(point, width):
    return (width - point[0], point[1])


def mapping_for_page(page):
    boxes, _ = orange_boxes(page)
    mapping, _, _ = fit_mapping_for_page(page, boxes)
    return mapping


def map_point_to_ocr(point, mapping):
    x, y = point
    mapped = map_box((x, y, x + 1, y + 1), mapping)
    return center(mapped)


def point_to_pdf(point, image_size, pdf_rect):
    x, y = point
    return fitz.Point(
        x / image_size[0] * pdf_rect.width,
        y / image_size[1] * pdf_rect.height,
    )


def word_center(word):
    x0, y0, x1, y1 = word[:4]
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def nearest_words(doc, page_no, ocr_point, limit=6):
    page = doc[PDF_PAGE_INDEX[page_no]]
    pdf_point = point_to_pdf(ocr_point, Image.open(OCR_IMAGES[page_no]).size, page.rect)
    scored = []
    for word in page.get_text('words'):
        cx, cy = word_center(word)
        dist = ((cx - pdf_point.x) ** 2 + (cy - pdf_point.y) ** 2) ** 0.5
        line_dist = abs(cy - pdf_point.y)
        scored.append((dist, line_dist, word[4], word[:4]))
    return sorted(scored)[:limit]


def words_on_same_line(doc, page_no, ocr_point, tolerance_px=18):
    page = doc[PDF_PAGE_INDEX[page_no]]
    image_size = Image.open(OCR_IMAGES[page_no]).size
    pdf_point = point_to_pdf(ocr_point, image_size, page.rect)
    pdf_tol = tolerance_px / image_size[1] * page.rect.height
    words = []
    for word in page.get_text('words'):
        cx, cy = word_center(word)
        if abs(cy - pdf_point.y) <= pdf_tol:
            words.append((word[0], word[4]))
    return ' '.join(text for _, text in sorted(words))


def annotate_projection(target_page, projected):
    img = Image.open(SOURCE_PAGES[target_page]).convert('RGB').rotate(180, expand=True)
    draw = ImageDraw.Draw(img)
    for item in projected:
        x, y = item['target_highres_point']
        r = 18
        draw.ellipse((x - r, y - r, x + r, y + r), outline='red', width=5)
        draw.text((x + 22, y - 18), item['id'], fill='red')
    img.save(OUT / f'page_{target_page}_anchor_projection.png')


def main():
    ensure_highres_sources()
    doc = fitz.open(OCR_PDF)
    lines = ['# Visual Anchor Projections', '']
    projected_by_target = {76: [], 79: []}

    for anchor in ANCHORS:
        source_page = anchor['page']
        target_page = 76 if source_page == 79 else 79
        source_img = Image.open(SOURCE_PAGES[source_page])
        c = center(anchor['box'])
        reflected = reflect_point(c, source_img.width)
        target_mapping = mapping_for_page(target_page)
        ocr_point = map_point_to_ocr(reflected, target_mapping)
        nearest = nearest_words(doc, target_page, ocr_point)
        same_line = words_on_same_line(doc, target_page, ocr_point)

        projected = {
            **anchor,
            'target_page': target_page,
            'source_point': c,
            'target_highres_point': reflected,
            'target_ocr_point': ocr_point,
            'nearest': nearest,
            'same_line': same_line,
        }
        projected_by_target[target_page].append(projected)

        lines.append(f'## {anchor["id"]} ({anchor["kind"]})')
        lines.append(f'- source page {source_page} center=({c[0]:.1f},{c[1]:.1f})')
        lines.append(f'- mirrored to page {target_page} highres=({reflected[0]:.1f},{reflected[1]:.1f}), ocr=({ocr_point[0]:.1f},{ocr_point[1]:.1f})')
        lines.append('- nearest words: ' + ' / '.join(f'{w}({dist:.1f})' for dist, _, w, _ in nearest))
        lines.append('- same-line text: ' + same_line)
        lines.append('')

    for page, items in projected_by_target.items():
        annotate_projection(page, items)

    (OUT / 'visual_anchor_projections.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
