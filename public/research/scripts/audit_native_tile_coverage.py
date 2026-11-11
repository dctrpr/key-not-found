#!/usr/bin/env python3
"""Exact, metadata-only coverage of 32 fixed Issue 24 native tiles."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

SOURCE = 'analysis_outputs/continuation_20261110/g07_glyph_review'
PINS = {
    'BASELINE_BOXES.json': '2d7a6b97564ec8e85c3ac086a4dba87e9631666d3329d0a709c514d88b627fa0',
    'COVERAGE.json': 'f3cb34d9bb35da3cad7c81f46a708d9b178f61f009099d5b27920ff0afa17276',
    'PACKET_MANIFEST.json': '8d0e0d6f9e8cff832f619197f5aa4fdd318ca179bfa82f37978537344ff9b33f',
}
PAGES = range(73, 81)
SIZE = [2544, 3264]
FRAME = [0, 0, *SIZE]
TILE_LAYOUT = {
    'NW': [0, 0, 1320, 1680],
    'NE': [1224, 0, 2544, 1680],
    'SW': [0, 1584, 1320, 3264],
    'SE': [1224, 1584, 2544, 3264],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def intersect(a, b):
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return box if box[0] < box[2] and box[1] < box[3] else None


def union_area(rectangles):
    """Partition at both axes' exact rectangle boundaries."""
    xcuts = sorted({x for a, _, b, _ in rectangles for x in (a, b)})
    ycuts = sorted({y for _, a, _, b in rectangles for y in (a, b)})
    return sum((r-l)*(b-t)
               for l, r in zip(xcuts, xcuts[1:])
               for t, b in zip(ycuts, ycuts[1:])
               if any(x <= l < z and y <= t < w for x, y, z, w in rectangles))


def valid_box(box):
    return (isinstance(box, list) and len(box) == 4
            and all(type(n) is int for n in box)
            and intersect(box, FRAME) == box)


def padded(box):
    return [max(0, box[0]-8), max(0, box[1]-8),
            min(SIZE[0], box[2]+8), min(SIZE[1], box[3]+8)]


def load_inputs(root):
    docs = []
    for name, pin in PINS.items():
        raw = (root / SOURCE / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin, 'Pinned metadata bytes changed')
        docs.append(json.loads(raw))
    return docs


def audit(baseline, prior, manifest):
    require(prior['baselineBoxesSha256'] == PINS['BASELINE_BOXES.json']
            and prior['packetManifestSha256'] == PINS['PACKET_MANIFEST.json'],
            'Prior coverage links changed')
    rows = baseline['records']
    require(len(rows) == 321 and len({row['publicStreamId'] for row in rows}) == 321,
            'Unexpected baseline population')
    require(all(row['printedPage'] in PAGES and row['imageDimensionsPx'] == SIZE
                and valid_box(row['uprightPixelEnclosure']) for row in rows),
            'Malformed baseline enclosure')
    mirror = [row for row in rows if row['orientation'] == 'horizontal-mirror']
    ordinary = [row for row in rows if row['orientation'] == 'normal']
    require(len(mirror) == len(manifest['targets']) == prior['targetBoxCount'] == 114
            and len(ordinary) == prior['normalBoxCount'] == 207, 'Unexpected detector cohort')
    old_windows = {page: [] for page in PAGES}
    for row, target in zip(mirror, manifest['targets']):
        region = padded(row['uprightPixelEnclosure'])
        page = row['printedPage']
        require(page == target['printedPage'] and row['publicStreamId'] == target['publicStreamId']
                and region == target['pixelBounds'], 'Archived crop does not match baseline')
        old_windows[page].append(region)

    require(all(valid_box(box) for box in TILE_LAYOUT.values())
            and union_area(list(TILE_LAYOUT.values())) == area(FRAME),
            'Fixed tile union has a source gap')
    tiles = [{'id': f'p{page}-{label}', 'printedPage': page, 'pixelBounds': box}
             for page in PAGES for label, box in TILE_LAYOUT.items()]
    archived = []
    priority = []
    coverage = Counter()
    per_page = {page: Counter() for page in PAGES}
    seam_axes = Counter()
    for row in ordinary:
        page, box = row['printedPage'], row['uprightPixelEnclosure']
        identifier = row['publicStreamId']
        old_clips = [clip for w in old_windows[page] if (clip := intersect(box, w))]
        old_area = union_area(old_clips)
        total = area(box)
        state = 'disjoint' if old_area == 0 else 'full' if old_area == total else 'partial'
        archived.append({'printedPage':page, 'publicStreamId':identifier,
                         'pixels':total, 'coveredPixels':old_area, 'status':state})
        intersections = []
        for label, tile in TILE_LAYOUT.items():
            clip = intersect(box, tile)
            if clip:
                intersections.append({
                    'tileId':f'p{page}-{label}', 'intersectionXYXY':clip,
                    'intersectionInTileXYXY':[n - tile[i%2] for i, n in enumerate(clip)],
                    'containsEntireBox':clip == box})
        retained = union_area([item['intersectionXYXY'] for item in intersections])
        require(retained == total, 'Ordinary box has a tile-coverage gap')
        full = any(item['containsEntireBox'] for item in intersections)
        axes = ([axis for axis, low, high, i in [('x', 1224, 1320, 0), ('y', 1584, 1680, 1)]
                 if box[i] < low and box[i+2] > high])
        require(full == (not axes), 'Containment and overlap condition disagree')
        coverage[state, full] += 1
        if state == 'full':
            continue
        per_page[page][state] += 1
        per_page[page]['fullyContained' if full else 'splitAcrossTiles'] += 1
        seam_axes.update(axes)
        priority.append({'printedPage':page, 'publicStreamId':identifier,
                         'ordinaryBoxXYXY':box, 'oldWindowCoverage':state,
                         'ordinaryBoxPixels':total, 'oldCoveredPixels':old_area,
                         'allTileCoveredPixels':retained, 'fullyContainedInOneTile':full,
                         'seamAxesBeyondOverlap':axes, 'tileIntersections':intersections})
    require(archived == prior['normalBoxCoverage'], 'Archived coverage did not reproduce')
    require(Counter(item['status'] for item in archived) == {'full':95, 'partial':29, 'disjoint':83},
            'Archived cohort counts changed')
    require(len(priority) == 112, 'Unexpected priority population')
    return {
        'version':1, 'testId':'g07-native-tile-coverage-metadata',
        'sourcePins':{f'{SOURCE}/{name}':pin for name, pin in PINS.items()},
        'coordinates':{'pageSizePx':SIZE, 'coordinateSystem':'half-open XYXY, upright native pixels',
                       'overlapPx':{'x':96, 'y':96}},
        'coverage':{'pages':8, 'tiles':len(tiles), 'pixelsPerPage':area(FRAME),
                    'distinctSourcePixelsCovered':8*area(FRAME), 'missingPixels':0,
                    'archivedCoverageRowsReproduced':len(archived),
                    'ordinaryBoxStates':{s:{'containedInOneTile':coverage[s,True],
                                            'splitAcrossTiles':coverage[s,False]}
                                         for s in ('disjoint','partial','full')},
                    'priorityBoxes':len(priority),
                    'priorityContainedInOneTile':sum(r['fullyContainedInOneTile'] for r in priority),
                    'prioritySplitAcrossTiles':sum(not r['fullyContainedInOneTile'] for r in priority),
                    'prioritySplitAxisCounts':dict(seam_axes)},
        'perPage':{str(p):{k:per_page[p][k]
                          for k in ('disjoint','partial','fullyContained','splitAcrossTiles')}
                   for p in PAGES},
        'tiles':tiles, 'priorityBoxes':priority,
        'activity':{'sourcePixelsOpened':0,'glyphAssessments':0,'targetReadings':0},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--research', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve(strict=True)
    out = args.out.resolve()
    require(not out.is_relative_to(root.parent.parent), 'Metadata output must remain outside the site checkout')
    result = audit(*load_inputs(root))
    with out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(result['coverage'], indent=2))


if __name__ == '__main__':
    main()
