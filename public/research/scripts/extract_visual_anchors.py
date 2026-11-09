#!/usr/bin/env python3
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from extract_visual_masks import masks_for_page
from highres_reflection_extract import SOURCE_PAGES, ensure_highres_sources, orange_boxes


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'source_audit'
OUT.mkdir(parents=True, exist_ok=True)


def connected_components(mask, min_area=250):
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    comps = []
    for y in range(h):
        xs = np.where(mask[y] & ~seen[y])[0]
        for x0 in xs:
            if seen[y, x0] or not mask[y, x0]:
                continue
            q = deque([(x0, y)])
            seen[y, x0] = True
            pts = []
            while q:
                x, yy = q.popleft()
                pts.append((x, yy))
                for nx in (x - 1, x, x + 1):
                    for ny in (yy - 1, yy, yy + 1):
                        if nx < 0 or ny < 0 or nx >= w or ny >= h:
                            continue
                        if mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((nx, ny))
            if len(pts) >= min_area:
                arr = np.array(pts)
                x1, y1 = arr.min(axis=0)
                x2, y2 = arr.max(axis=0)
                comps.append((len(pts), (int(x1), int(y1), int(x2) + 1, int(y2) + 1)))
    return sorted(comps, key=lambda item: (item[1][1], item[1][0]))


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def hflip_center(point, width):
    return (width - point[0], point[1])


def dark_anchor_boxes(img):
    rgb = np.asarray(img.convert('RGB'))
    brightness = rgb.mean(axis=2)
    dark = brightness < 118

    # Right-side graphics are the relevant Canva branch: barbed wire, pills,
    # dollar sign, and X-like marks. Avoid the main body text column.
    region = np.zeros_like(dark, dtype=bool)
    region[:, int(img.width * 0.68):] = True
    mask = dark & region

    boxes = []
    for area, box in connected_components(mask, min_area=220):
        x1, y1, x2, y2 = box
        w = x2 - x1
        h = y2 - y1
        if w < 20 or h < 20:
            continue
        if w > 520 and h > 180:
            continue
        boxes.append((area, box))
    return boxes


def small_orange_boxes(page):
    boxes, size = orange_boxes(page)
    out = []
    for box in boxes:
        w = box[2] - box[0]
        h = box[3] - box[1]
        if w <= 110 and h <= 110:
            out.append(box)
    return out, size


def annotate(page, dark_boxes, orange_small):
    img = Image.open(SOURCE_PAGES[page]).convert('RGB').rotate(180, expand=True)
    draw = ImageDraw.Draw(img)
    for idx, (_, box) in enumerate(dark_boxes, 1):
        draw.rectangle(box, outline='cyan', width=5)
        draw.text((box[0], max(0, box[1] - 24)), f'D{idx}', fill='cyan')
    for idx, box in enumerate(orange_small, 1):
        draw.rectangle(box, outline='red', width=5)
        draw.text((box[0], max(0, box[1] - 24)), f'O{idx}', fill='red')
    img.save(OUT / f'page_{page}_anchor_candidates.png')


def main():
    ensure_highres_sources()
    lines = ['# Visual Anchor Candidates', '']
    for page in [76, 79]:
        img = Image.open(SOURCE_PAGES[page]).convert('RGB').rotate(180, expand=True)
        dark = dark_anchor_boxes(img)
        orange_small, size = small_orange_boxes(page)
        annotate(page, dark, orange_small)
        lines.append(f'## Page {page}')
        lines.append(f'- image_size={size}')
        lines.append('- dark right-side candidates:')
        for idx, (area, box) in enumerate(dark, 1):
            c = center(box)
            fc = hflip_center(c, size[0])
            lines.append(f'  - D{idx}: area={area} box={box} center=({c[0]:.1f},{c[1]:.1f}) hflip_center=({fc[0]:.1f},{fc[1]:.1f})')
        lines.append('- small orange candidates:')
        for idx, box in enumerate(orange_small, 1):
            c = center(box)
            fc = hflip_center(c, size[0])
            lines.append(f'  - O{idx}: box={box} center=({c[0]:.1f},{c[1]:.1f}) hflip_center=({fc[0]:.1f},{fc[1]:.1f})')
        lines.append('')

    report = '\n'.join(lines)
    (OUT / 'visual_anchor_candidates.md').write_text(report + '\n')
    print(report)


if __name__ == '__main__':
    main()
