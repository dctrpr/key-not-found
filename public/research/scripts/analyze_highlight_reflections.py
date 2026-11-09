#!/usr/bin/env python3
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from extract_visual_masks import PAGES, connected_components, masks_for_page


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs'
OUT.mkdir(exist_ok=True)


def dilate(mask, size=41):
    image = Image.fromarray((mask * 255).astype(np.uint8))
    image = image.filter(ImageFilter.MaxFilter(size))
    return np.asarray(image) > 0


def hflip(mask):
    return np.fliplr(mask)


def draw_mask_overlay(page_a, page_b, mask):
    img = Image.open(PAGES[page_a]).convert('RGBA')
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    arr = np.asarray(mask)
    red = np.zeros((img.height, img.width, 4), dtype=np.uint8)
    red[arr] = [255, 0, 0, 150]
    overlay = Image.fromarray(red, 'RGBA')
    out = Image.alpha_composite(img, overlay)
    out.save(OUT / f'intersection_orange_{page_a}_{page_b}_hflip.png')


def analyze_pair(page_a, page_b):
    img_a = Image.open(PAGES[page_a]).convert('RGB')
    img_b = Image.open(PAGES[page_b]).convert('RGB').resize(img_a.size)
    mask_a = masks_for_page(img_a)['orange']
    mask_b = hflip(masks_for_page(img_b)['orange'])

    # Exact mask overlap is too brittle on scans; dilate to find deliberate near-overlaps.
    overlap = dilate(mask_a, 55) & dilate(mask_b, 55)
    comps = connected_components(overlap, min_area=500)
    boxes = []
    for comp in comps:
        x1, y1, x2, y2 = comp['box']
        if (x2 - x1) < 25 or (y2 - y1) < 20:
            continue
        boxes.append(comp['box'])

    draw_mask_overlay(page_a, page_b, overlap)
    return boxes


def main():
    report = []
    for page_a, page_b in [(75, 79), (76, 78), (75, 78), (76, 79)]:
        boxes = analyze_pair(page_a, page_b)
        report.append(f'{page_a}/{page_b} orange-reflection overlap boxes: {len(boxes)}')
        for idx, box in enumerate(boxes, 1):
            report.append(f'  {idx:02d} {box}')
    (OUT / 'reflection_overlap_report.txt').write_text('\n'.join(report) + '\n')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
