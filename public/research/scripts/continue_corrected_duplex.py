#!/usr/bin/env python3
"""Fixed mirror-mask diagnostic; no prose hashing or wallet actions."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs/continuation_20261109'
MODEL = ROOT / 'analysis_outputs/3d_article_map/article_3d_map_data.json'
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
LEAVES = {frozenset((76, 77)), frozenset((78, 79))}


def wif_valid(s):
    if len(s) not in (51, 52) or any(c not in B58 for c in s):
        return False
    n = 0
    for c in s:
        n = n * 58 + B58.index(c)
    b = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    b = b'\0' * (len(s) - len(s.lstrip('1'))) + b
    if len(b) not in (37, 38) or b[0] != 128:
        return False
    if len(b) == 38 and b[-5] != 1:
        return False
    k = int.from_bytes(b[1:33], 'big')
    return (0 < k < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
            and hashlib.sha256(hashlib.sha256(b[:-4]).digest()).digest()[:4] == b[-4:])


def lines(items):
    """Group OCR centers by line with fixed 25px tolerance, then left to right."""
    result = []
    for item in sorted(items, key=lambda v: (v['y'], v['x'])):
        if result and abs(item['y'] - result[-1]['y']) <= 25:
            result[-1]['items'].append(item)
        else:
            result.append({'y': item['y'], 'items': [item]})
    return [sorted(v['items'], key=lambda v: v['x']) for v in result]


def main():
    model = json.loads(MODEL.read_text())
    pages = {v['page']: v for v in model['pages'] if 75 <= v['page'] <= 79}
    rows, checked, hits = [], 0, []
    for sn, source in pages.items():
        # Printed orange text masks only; exclude the five pill-art components.
        masks = [m for m in source['highlights'] if not (sn == 79 and int(m['id'].rsplit('_', 1)[1]) >= 6)]
        for tn, target in pages.items():
            if sn == tn:
                continue
            boxes = []
            for m in masks:
                a, b, c, d = m['box']
                boxes.append([(source['width'] - c) / source['width'] * target['width'],
                              b / source['height'] * target['height'],
                              (source['width'] - a) / source['width'] * target['width'],
                              d / source['height'] * target['height']])

            def inside(x, y, box):
                return box[0] <= x <= box[2] and box[1] <= y <= box[3]

            chars = [{'x': c['x'], 'y': c['y'], 'text': c['c'], 'id': c['id']}
                     for c in target['chars'] if not c['c'].isspace()]
            words = [{'x': w['center'][0], 'y': w['center'][1], 'text': w['text'], 'id': w['id']}
                     for w in target['words']]
            streams = {}
            for unit, units, join in [('characters', chars, ''), ('words', words, ' ')]:
                chosen = [v for v in units if any(inside(v['x'], v['y'], b) for b in boxes)]
                streams[unit] = '\n'.join(join.join(v['text'] for v in line) for line in lines(chosen))
            per_mask = []
            for m, b in zip(masks, boxes):
                chosen = [v for v in words if inside(v['x'], v['y'], b)]
                per_mask.append({'mask': m['id'], 'targetBox': b,
                                 'text': '\n'.join(' '.join(v['text'] for v in line) for line in lines(chosen))})
            for kind, text in streams.items():
                for direction, value in [('forward', text), ('reverse', text[::-1])]:
                    compact = re.sub(r'\s', '', value)
                    checked += 1
                    if wif_valid(compact) or (len(compact) == 64 and re.fullmatch('[0-9a-fA-F]{64}', compact)):
                        hits.append({'source': sn, 'target': tn, 'unit': kind, 'direction': direction,
                                     'candidate': compact})
            rows.append({'source': sn, 'target': tn,
                         'correctedPhysicalLeaf': frozenset((sn, tn)) in LEAVES,
                         'streams': streams, 'masks': per_mask})
    result = {'sourceModel': str(MODEL.relative_to(ROOT)),
              'sourceModelSha256': hashlib.sha256(MODEL.read_bytes()).hexdigest(),
              'method': 'Horizontal reflection, page-size normalization only, no shift/rotation fitting; center-in-mask selection; fixed 25px OCR line grouping.',
              'limits': ['OCR characters are imperfect; this diagnostic does not establish exact key text.',
                         'Bounding boxes approximate highlight ink, including merged multiline masks.',
                         'Corrected leaves are 76/77 and 78/79; p74 is absent from the model.',
                         'No transform is selected using desired article context.',
                         'Direct shape/checksum tests do not exhaust encodings. No hashing or online balance checks.'],
              'pairCount': len(rows), 'directStreamsChecked': checked, 'directEncodingHits': hits, 'pairs': rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'corrected_duplex_orange.json').write_text(json.dumps(result, indent=2) + '\n')
    md = ['# Corrected duplex orange-mask experiment', '', result['method'], '',
          f'{len(rows)} ordered page pairs; {checked} complete direct text streams checked; {len(hits)} exact WIF/64-hex hits.', '',
          '## Corrected physical leaf results', '']
    for row in rows:
        if row['correctedPhysicalLeaf']:
            md += [f"### {row['source']} → {row['target']}", '', '```text', row['streams']['words'], '```', '']
    md += ['## Limits', ''] + ['- ' + v for v in result['limits']]
    md += ['', 'No solution is claimed. Full selections and controls are in corrected_duplex_orange.json.', '']
    (OUT / 'corrected_duplex_orange.md').write_text('\n'.join(md))
    print(json.dumps({k: result[k] for k in ['pairCount', 'directStreamsChecked', 'directEncodingHits']}))


if __name__ == '__main__':
    main()
