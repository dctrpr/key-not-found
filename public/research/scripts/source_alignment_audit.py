#!/usr/bin/env python3
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageEnhance

from extract_visual_masks import PAGES as OCR_IMAGES
from highres_reflection_extract import (
    SOURCE_PAGES,
    ensure_highres_sources,
    map_highres_boxes_to_ocr,
    orange_boxes as highres_orange_boxes,
    reflected_selection,
)
from read_reflected_masks import PDF as OCR_PDF


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'source_audit'
OUT.mkdir(parents=True, exist_ok=True)


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def hflip_box(box, width):
    x1, y1, x2, y2 = box
    return (width - x2, y1, width - x1, y2)


def resize_to(img, size):
    return img.convert('RGB').resize(size)


def draw_labeled_boxes(img, boxes, color, prefix):
    out = img.convert('RGB')
    draw = ImageDraw.Draw(out)
    for idx, box in boxes:
        draw.rectangle(box, outline=color, width=4)
        draw.text((box[0], max(0, box[1] - 18)), f'{prefix}{idx}', fill=color)
    return out


def overlay_pair(left_page, right_page):
    left = Image.open(SOURCE_PAGES[left_page]).convert('RGB').rotate(180, expand=True)
    right = Image.open(SOURCE_PAGES[right_page]).convert('RGB').rotate(180, expand=True)
    right_flip = right.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    right_flip = resize_to(right_flip, left.size)

    blend = Image.blend(left, right_flip, 0.45)
    diff = ImageChops.difference(left, right_flip)
    diff = ImageEnhance.Contrast(diff).enhance(2.0)

    blend.save(OUT / f'highres_overlay_{left_page}_{right_page}_hflip.png')
    diff.save(OUT / f'highres_diff_{left_page}_{right_page}_hflip.png')


def canva_anchor_candidate_lines():
    lines = []
    page = 79
    boxes, size = highres_orange_boxes(page)
    small = []
    for idx, box in enumerate(boxes, 1):
        w = box[2] - box[0]
        h = box[3] - box[1]
        if w <= 90 and h <= 90:
            small.append((idx, box))

    lines.append('## Canva Anchor Candidates')
    lines.append('Small orange components on page 79 are likely the pill marks mentioned in the Canva note.')
    for idx, box in small:
        c = center(box)
        reflected = hflip_box(box, size[0])
        rc = center(reflected)
        lines.append(
            f'- page 79 orange box {idx:02d}: box={box} center=({c[0]:.1f},{c[1]:.1f}) '
            f'hflip_center=({rc[0]:.1f},{rc[1]:.1f})'
        )
    lines.append('')
    return lines


def ocr_text_probe_lines():
    doc = fitz.open(OCR_PDF)
    probes = ['10years', '20,000', '100,000', '12,000', 'shitcoin', 'SHITCOINS']
    lines = ['## OCR Probe']
    lines.append('The Canva note says browser/OCR viewing missed a “#0”. These exact OCR-PDF text probes show what the local OCR layer does preserve:')
    full = '\n'.join(page.get_text('text') for page in doc)
    for probe in probes:
        lines.append(f'- {probe}: {"present" if probe in full else "missing"}')
    lines.append('')
    return lines


def orange_alignment_lines():
    lines = ['## Orange Highlight Registration']
    for page in [75, 76, 77, 78, 79, 80]:
        highres_boxes, highres_size = highres_orange_boxes(page)
        mapped_boxes, ocr_size = map_highres_boxes_to_ocr(page, highres_boxes)
        lines.append(
            f'- page {page}: highres_size={highres_size}, ocr_size={ocr_size}, '
            f'highres_orange_boxes={len(highres_boxes)}, mapped_boxes={len(mapped_boxes)}'
        )
        for idx, (hi, mapped) in enumerate(zip(highres_boxes, mapped_boxes), 1):
            hc = center(hi)
            mc = center(mapped)
            lines.append(
                f'  {idx:02d} highres={hi} center=({hc[0]:.1f},{hc[1]:.1f}) '
                f'ocr_mapped={mapped} center=({mc[0]:.1f},{mc[1]:.1f})'
            )
    lines.append('')
    return lines


def reflected_text_summary_lines():
    lines = ['## Targeted Reflection Text']
    for source, target in [(79, 75), (78, 76), (76, 78), (79, 76)]:
        joined = []
        for _, _, _, text, _ in reflected_selection(source, target):
            if text:
                joined.append(text)
        lines.append(f'- {source} -> {target}: ' + ' / '.join(joined))
    lines.append('')
    return lines


def main():
    ensure_highres_sources()

    for pair in [(75, 79), (76, 78), (76, 79), (75, 78)]:
        overlay_pair(*pair)

    lines = ['# Source Alignment Audit', '']
    lines.append('Purpose: validate the Canva concern that mixed PDF/image sources, rotation, and browser OCR can change what lines up.')
    lines.append('')
    lines.append('## Source Files')
    for page in [75, 76, 77, 78, 79, 80]:
        hi = Image.open(SOURCE_PAGES[page])
        lo = Image.open(OCR_IMAGES[page])
        lines.append(f'- page {page}: magazine_pdf_image={hi.size}, ocr_pdf_image={lo.size}')
    lines.append('')
    lines += ocr_text_probe_lines()
    lines += orange_alignment_lines()
    lines += canva_anchor_candidate_lines()
    lines += reflected_text_summary_lines()
    lines.append('## Output Images')
    for pair in [(75, 79), (76, 78), (76, 79), (75, 78)]:
        lines.append(f'- highres_overlay_{pair[0]}_{pair[1]}_hflip.png')
        lines.append(f'- highres_diff_{pair[0]}_{pair[1]}_hflip.png')
    lines.append('')

    report = '\n'.join(lines)
    (OUT / 'source_alignment_audit.md').write_text(report + '\n')
    print(report)


if __name__ == '__main__':
    main()
