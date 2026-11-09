#!/usr/bin/env python3
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs'
OUT.mkdir(exist_ok=True)

PAGES = {
    75: ROOT / 'keyser bitcoin -3_1.jpg',
    76: ROOT / 'keyser bitcoin -4_1.jpg',
    77: ROOT / 'keyser bitcoin -5_1.jpg',
    78: ROOT / 'keyser bitcoin -6_1.jpg',
    79: ROOT / 'keyser bitcoin -7_1.jpg',
    80: ROOT / 'keyser bitcoin -8_1.jpg',
}


def connected_components(mask, min_area=80):
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
            points = []
            while q:
                x, yy = q.popleft()
                points.append((x, yy))
                for nx in (x - 1, x, x + 1):
                    for ny in (yy - 1, yy, yy + 1):
                        if nx < 0 or ny < 0 or nx >= w or ny >= h:
                            continue
                        if not seen[ny, nx] and mask[ny, nx]:
                            seen[ny, nx] = True
                            q.append((nx, ny))
            if len(points) >= min_area:
                arr = np.array(points)
                x1, y1 = arr.min(axis=0)
                x2, y2 = arr.max(axis=0)
                comps.append(
                    {
                        'area': len(points),
                        'box': (int(x1), int(y1), int(x2) + 1, int(y2) + 1),
                        'center': ((int(x1) + int(x2)) / 2, (int(y1) + int(y2)) / 2),
                    }
                )
    return sorted(comps, key=lambda c: (c['box'][1], c['box'][0]))


def merge_close_boxes(comps, y_gap=12, x_gap=20):
    boxes = [c['box'] for c in comps]
    changed = True
    while changed:
        changed = False
        merged = []
        used = [False] * len(boxes)
        for i, a in enumerate(boxes):
            if used[i]:
                continue
            ax1, ay1, ax2, ay2 = a
            current = a
            used[i] = True
            for j, b in enumerate(boxes):
                if used[j]:
                    continue
                bx1, by1, bx2, by2 = b
                vertical_close = not (ay2 + y_gap < by1 or by2 + y_gap < ay1)
                horizontal_close = not (ax2 + x_gap < bx1 or bx2 + x_gap < ax1)
                if vertical_close and horizontal_close:
                    current = (min(current[0], bx1), min(current[1], by1), max(current[2], bx2), max(current[3], by2))
                    used[j] = True
                    changed = True
            merged.append(current)
        boxes = merged
    return sorted(boxes, key=lambda b: (b[1], b[0]))


def masks_for_page(img):
    rgb = np.asarray(img.convert('RGB'))
    r = rgb[:, :, 0].astype(int)
    g = rgb[:, :, 1].astype(int)
    b = rgb[:, :, 2].astype(int)
    brightness = (r + g + b) / 3

    # Orange highlight ink/paper. Threshold is intentionally broad to include scan variation.
    orange = (r > 170) & (g > 65) & (g < 185) & (b < 105) & ((r - b) > 85) & ((r - g) > 25)

    # Black highlight blocks on white pages: very dark, wide horizontal rectangles.
    black = brightness < 130

    # White inverted highlight blocks on black page 77.
    white = brightness > 185

    return {'orange': orange, 'black': black, 'white': white}


def dilate(mask, size):
    image = Image.fromarray((mask * 255).astype(np.uint8))
    image = image.filter(ImageFilter.MaxFilter(size))
    return np.asarray(image) > 0


def draw_boxes(img, boxes, color):
    out = img.convert('RGB')
    draw = ImageDraw.Draw(out)
    for idx, box in enumerate(boxes, start=1):
        draw.rectangle(box, outline=color, width=4)
        draw.text((box[0], max(0, box[1] - 18)), str(idx), fill=color)
    return out


def main():
    report = []
    for page, path in PAGES.items():
        img = Image.open(path)
        masks = masks_for_page(img)
        for name, mask in masks.items():
            if name == 'black' and page == 77:
                continue
            if name == 'white' and page != 77:
                continue

            comp_mask = mask
            if name in {'black', 'white'}:
                # Inverted highlight blocks are rectangular fields with text holes.
                # Dilation merges the text/background into line-sized blocks.
                comp_mask = dilate(mask, 19)

            comps = connected_components(comp_mask, min_area=100)
            boxes = merge_close_boxes(comps, y_gap=16, x_gap=26)
            # Keep plausible text/highlight boxes, not page edges or giant image noise.
            filtered = []
            for box in boxes:
                x1, y1, x2, y2 = box
                width = x2 - x1
                height = y2 - y1
                if width < 20 or height < 8:
                    continue
                if width > img.width * 0.95 or height > img.height * 0.35:
                    continue
                if name == 'black':
                    fill = mask[y1:y2, x1:x2].mean()
                    if not (width > 120 and height > 20 and fill > 0.15):
                        continue
                if name == 'white':
                    fill = mask[y1:y2, x1:x2].mean()
                    if not (width > 120 and height > 20 and fill > 0.18):
                        continue
                filtered.append(box)

            mask_img = Image.fromarray((mask * 255).astype(np.uint8))
            mask_img.save(OUT / f'page_{page}_{name}_mask.png')
            boxed = draw_boxes(img, filtered, {'orange': 'red', 'black': 'cyan', 'white': 'blue'}[name])
            boxed.save(OUT / f'page_{page}_{name}_boxes.png')
            report.append(f'page {page} {name}: {len(filtered)} boxes')
            for idx, box in enumerate(filtered, start=1):
                report.append(f'  {idx:02d} {box}')

    (OUT / 'visual_mask_report.txt').write_text('\n'.join(report) + '\n')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
