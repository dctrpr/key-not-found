#!/usr/bin/env python3
"""Refine manually selected ordinary same-face page 75 landmarks."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

# Feature label, approximate center in higher-resolution upright pixels,
# and fixed crop width/height. Chosen visually from native page 75.
POINTS = [
    ('overdose-header', 312, 146, 184, 52),
    ('reaction', 1608, 560, 145, 55),
    ('crash', 1735, 849, 126, 55),
    ('markets-are', 1916, 925, 163, 55),
    ('sum-of', 1997, 1004, 149, 65),
    ('banking', 1805, 1226, 143, 61),
    ('wall-street', 1942, 1297, 153, 60),
    ('black-hole', 1963, 1370, 158, 62),
    ('bitcoin-margin', 120, 1444, 58, 103),
    ('magazine-margin', 118, 1588, 58, 104),
    ('in-fact', 504, 1555, 122, 60),
    ('caused-by', 1917, 1562, 152, 60),
    ('bitcoin-was', 1190, 555, 150, 44),
    ('global-financial', 680, 631, 150, 44),
    ('coming', 1240, 851, 150, 50),
    ('markets-left', 442, 923, 148, 48),
    ('discount-stuff', 1252, 928, 160, 48),
    ('neuroses', 685, 1070, 170, 58),
    ('global-unconscious', 861, 1219, 160, 58),
    ('jamie-dimon', 613, 1363, 162, 55),
    ('it-had', 991, 1439, 151, 52),
    ('the-chaos', 861, 1557, 157, 57),
]
SCALE_X = (0.77, 0.78, 0.79, 0.80, 0.81, 0.82)
SCALE_Y = (0.76, 0.78, 0.80, 0.82)


def midpoint(box):
    x0, y0, x1, y1 = box
    return [(x0 + x1) / 2, (y0 + y1) / 2]


def overlap(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def bandpass(analysis, crop):
    raster = np.asarray(crop, dtype='float64')
    return analysis.box_blur(raster, 1) - analysis.box_blur(raster, 6)


def refine(analysis, high, low, landmark):
    label, x, y, width, height = landmark
    x0, y0 = x - width // 2, y - height // 2
    high_box = [x0, y0, x0 + width, y0 + height]
    template = high.crop(high_box)
    # Approximate visible-grid mapping sets the search location only.
    nominal_x, nominal_y = int(0.793 * x - 35), int(0.795 * y)
    left, top = nominal_x - 45 - width // 2, nominal_y - 40 - height // 2
    right, bottom = nominal_x + 45 + width // 2, nominal_y + 40 + height // 2
    search = bandpass(analysis, low.crop((left, top, right, bottom)))
    best = None
    for scale_x in SCALE_X:
        for scale_y in SCALE_Y:
            tw, th = round(width * scale_x), round(height * scale_y)
            scaled = template.resize((tw, th), Image.Resampling.BICUBIC)
            scores = analysis.score_map(search, bandpass(analysis, scaled))
            iy, ix = map(int, np.unravel_index(scores.argmax(), scores.shape))
            score = float(scores[iy, ix])
            if best is None or score > best['sameFaceNcc']:
                low_box = [left + ix, top + iy, left + ix + tw, top + iy + th]
                best = {'feature': label, 'high': midpoint(high_box), 'low': midpoint(low_box),
                        'highBox': high_box, 'lowBox': low_box, 'sameFaceNcc': score,
                        'templateScale': [scale_x, scale_y], 'searchBox': [left, top, right, bottom]}
    return best


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.site.resolve() / 'public/research/scripts'))
    import measure_issue24_heading_pixels as analysis

    sources = json.loads(analysis.PROTOCOL.read_text())['sources']
    upright = []
    hashes = []
    for source in sources:
        pages, image_hashes = analysis.load_pages(source, [75])
        upright.append(Image.fromarray(pages[75].astype('uint8')))
        hashes.append(image_hashes[75])
    records = [refine(analysis, *upright, landmark) for landmark in POINTS]
    for record in records:
        for source, field in zip(sources, ['highBox', 'lowBox']):
            if any(overlap(record[field], f['box']) for f in source['features']):
                raise ValueError('Landmark intersects an earlier page 75 template: ' + record['feature'])
    result = {'printedPage': 75, 'coordinateConvention': 'midpoint of half-open native upright crop',
              'p75EmbeddedJpegSha256': hashes, 'landmarks': records,
              'transferFitted': False, 'otherPagesRead': []}
    with args.out.open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps({'landmarks': len(records), 'disjoint': True, 'pagesRead': [75]}))


if __name__ == '__main__':
    main()
