#!/usr/bin/env python3
import hashlib
import itertools
import math
import re
from collections import OrderedDict
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from highres_reflection_extract import fit_mapping_for_page, map_box, orange_boxes
from read_reflected_masks import PDF as OCR_PDF, PDF_PAGE_INDEX, PAGES as OCR_IMAGES
from search_visual_private_keys import check_activity, key_addresses


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'anchor_ray_selector'
OUT.mkdir(parents=True, exist_ok=True)

TARGET_PAGE = 76

# Coordinates are in the upright high-resolution page coordinate system used by
# the source-audit scripts. Page-79 pill centers are mirrored onto page 76.
ANCHORS_HIGHRES = OrderedDict(
    [
        ('p79_pill_1_mirror', (2373.0, 2408.0)),
        ('p79_pill_2_mirror', (2122.5, 2454.5)),
        ('p79_pill_3_mirror', (1938.0, 2608.5)),
        ('p79_pill_4_mirror', (2107.0, 2780.5)),
        ('p79_pill_5_mirror', (2360.5, 2968.0)),
        ('p76_x_mark', (2358.5, 2751.5)),
        ('p76_dollar', (1973.5, 3092.0)),
        ('p76_black_bar_1', (1972.0, 859.5)),
        ('p76_black_bar_2', (1794.0, 1518.5)),
        # Manual barbed-wire knot centers estimated from the verified 76/79
        # overlay crop. They are selector anchors only, not key material.
        ('p76_wire_left_knot', (1985.0, 132.0)),
        ('p76_wire_right_knot', (2410.0, 327.0)),
    ]
)

FOCUS_TERMS = {
    'bitcoin',
    'bukele',
    'salvador',
    'volcano',
    'volcanoes',
    'bonds',
    'bond',
    'imf',
    'president',
    'buying',
    'dip',
    'twitter',
    'mine',
    'max',
}


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def highres_to_ocr_mapper():
    boxes, _ = orange_boxes(TARGET_PAGE)
    mapping, _, _ = fit_mapping_for_page(TARGET_PAGE, boxes)

    def map_point(point):
        x, y = point
        return center(map_box((x, y, x + 1, y + 1), mapping))

    return map_point


def page_words():
    doc = fitz.open(OCR_PDF)
    page = doc[PDF_PAGE_INDEX[TARGET_PAGE]]
    image = Image.open(OCR_IMAGES[TARGET_PAGE]).convert('RGB')
    words = []
    for index, word in enumerate(page.get_text('words')):
        text = word[4].strip()
        if not text:
            continue
        rect = fitz.Rect(word[:4])
        cx = ((rect.x0 + rect.x1) / 2) / page.rect.width * image.width
        cy = ((rect.y0 + rect.y1) / 2) / page.rect.height * image.height
        box = (
            rect.x0 / page.rect.width * image.width,
            rect.y0 / page.rect.height * image.height,
            rect.x1 / page.rect.width * image.width,
            rect.y1 / page.rect.height * image.height,
        )
        # Drop page number/running-header noise near margins.
        if cx < 35 or cx > image.width - 35:
            continue
        words.append({'index': index, 'text': text, 'center': (cx, cy), 'box': box})
    return words, image


def line_distance(point, a, b):
    px, py = point
    ax, ay = a
    bx, by = b
    vx = bx - ax
    vy = by - ay
    length2 = vx * vx + vy * vy
    if length2 == 0:
        return float('inf'), 0.0
    t = ((px - ax) * vx + (py - ay) * vy) / length2
    qx = ax + t * vx
    qy = ay + t * vy
    return math.hypot(px - qx, py - qy), t


def in_mode(t, mode):
    if mode == 'segment':
        return -0.05 <= t <= 1.05
    if mode == 'ray_ab':
        return t >= -0.05
    if mode == 'ray_ba':
        return t <= 1.05
    if mode == 'full_line':
        return True
    raise ValueError(mode)


def selector_pairs(anchor_names):
    pills = [name for name in anchor_names if name.startswith('p79_pill')]
    marks = ['p76_x_mark', 'p76_dollar', 'p76_black_bar_1', 'p76_black_bar_2', 'p76_wire_left_knot', 'p76_wire_right_knot']
    pairs = []
    pairs.extend(itertools.combinations(pills, 2))
    pairs.extend((pill, mark) for pill in pills for mark in marks)
    pairs.extend(
        [
            ('p76_x_mark', 'p76_wire_left_knot'),
            ('p76_x_mark', 'p76_wire_right_knot'),
            ('p76_dollar', 'p76_wire_left_knot'),
            ('p76_dollar', 'p76_wire_right_knot'),
            ('p76_black_bar_1', 'p76_dollar'),
            ('p76_black_bar_2', 'p76_dollar'),
            ('p76_black_bar_1', 'p76_x_mark'),
            ('p76_black_bar_2', 'p76_x_mark'),
            ('p76_wire_left_knot', 'p76_wire_right_knot'),
        ]
    )
    return pairs


def normalize_words(text):
    return re.sub(r'[^A-Za-z0-9]+', ' ', text).strip().split()


def score_selection(words):
    texts = [w['text'] for w in words]
    clean = [re.sub(r'[^A-Za-z0-9]', '', t).lower() for t in texts]
    focus_hits = sum(1 for token in clean if token in FOCUS_TERMS)
    alpha_ratio = sum(ch.isalpha() for t in texts for ch in t) / max(1, sum(len(t) for t in texts))
    count = len(texts)
    length_score = 12 - abs(10 - min(count, 20))
    return focus_hits * 18 + length_score + alpha_ratio * 8


def build_selections():
    map_point = highres_to_ocr_mapper()
    anchors_ocr = OrderedDict((name, map_point(point)) for name, point in ANCHORS_HIGHRES.items())
    words, image = page_words()
    selections = []

    for a_name, b_name in selector_pairs(list(anchors_ocr)):
        a = anchors_ocr[a_name]
        b = anchors_ocr[b_name]
        for mode in ['segment', 'ray_ab', 'ray_ba', 'full_line']:
            for threshold in [12, 20, 32, 48]:
                selected = []
                for word in words:
                    dist, t = line_distance(word['center'], a, b)
                    if dist <= threshold and in_mode(t, mode):
                        selected.append({**word, 'dist': dist, 't': t})
                if not (2 <= len(selected) <= 36):
                    continue
                by_projection = sorted(selected, key=lambda item: item['t'])
                by_reading = sorted(selected, key=lambda item: (round(item['center'][1] / 18), item['center'][0]))
                for order_name, ordered in [('projection', by_projection), ('reading', by_reading)]:
                    text = ' '.join(item['text'] for item in ordered)
                    words_clean = normalize_words(text)
                    if len(words_clean) < 2:
                        continue
                    selections.append(
                        {
                            'a': a_name,
                            'b': b_name,
                            'a_point': a,
                            'b_point': b,
                            'mode': mode,
                            'threshold': threshold,
                            'order': order_name,
                            'words': ordered,
                            'text': text,
                            'score': score_selection(ordered),
                        }
                    )

    deduped = OrderedDict()
    for selection in sorted(selections, key=lambda item: item['score'], reverse=True):
        key = re.sub(r'\s+', ' ', selection['text'].lower()).strip()
        deduped.setdefault(key, selection)
    return list(deduped.values()), anchors_ocr, image


def text_variants(label, text):
    words = normalize_words(text)
    letters = ''.join(re.findall(r'[A-Za-z]', text))
    alnum = ''.join(re.findall(r'[A-Za-z0-9]', text))
    variants = OrderedDict()
    variants[label] = text
    variants[f'{label}:lower'] = text.lower()
    variants[f'{label}:nospace'] = alnum
    variants[f'{label}:letters_lower'] = letters.lower()
    variants[f'{label}:reverse'] = text[::-1]
    variants[f'{label}:first_letters'] = ''.join(w[0] for w in words if w)
    variants[f'{label}:last_letters'] = ''.join(w[-1] for w in words if w)
    variants[f'{label}:firstlast'] = ''.join(w[0] + w[-1] for w in words if w)
    variants[f'{label}:word_lengths_digits'] = ''.join(str(len(w) % 10) for w in words)
    return variants


def candidate_secrets(selections, limit=120):
    candidates = OrderedDict()
    top = selections[:limit]
    for idx, selection in enumerate(top, 1):
        base_label = f"ray{idx:03d}:{selection['a']}->{selection['b']}:{selection['mode']}:{selection['threshold']}:{selection['order']}"
        for label, value in text_variants(base_label, selection['text']).items():
            compact = re.sub(r'[^A-Za-z0-9]', '', value)
            if len(compact) < 10:
                continue
            raw = value.encode('utf-8')
            for hash_name, secret in [
                ('sha256', hashlib.sha256(raw).digest()),
                ('sha256d', hashlib.sha256(hashlib.sha256(raw).digest()).digest()),
                ('sha3_256', hashlib.sha3_256(raw).digest()),
                ('blake2s', hashlib.blake2s(raw, digest_size=32).digest()),
            ]:
                candidates.setdefault(
                    secret.hex(),
                    {
                        'label': f'{label}:{hash_name}',
                        'secret': secret,
                        'source': value[:240],
                    },
                )
    return list(candidates.values())


def build_address_map(candidates):
    address_map = {}
    for candidate in candidates:
        for kind, address in key_addresses(candidate['secret'], candidate['label'], include_taproot=True):
            address_map[address] = {**candidate, 'kind': kind}
    return address_map


def draw_top_lines(image, selections, out_path):
    canvas = image.convert('RGB')
    draw = ImageDraw.Draw(canvas)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'black']
    for idx, selection in enumerate(selections[:16], 1):
        color = colors[(idx - 1) % len(colors)]
        ax, ay = selection['a_point']
        bx, by = selection['b_point']
        draw.line((ax, ay, bx, by), fill=color, width=3)
        draw.text((ax + 4, ay + 4), str(idx), fill=color)
        for word in selection['words']:
            x1, y1, x2, y2 = word['box']
            draw.rectangle((x1, y1, x2, y2), outline=color, width=2)
    canvas.save(out_path)


def write_report(selections, anchors_ocr, candidates, address_map, found):
    lines = ['# Anchor Ray Selector Experiment', '']
    lines.append('Hypothesis: page-79 pill marks and page-76 X/dollar/barbed-wire marks define rays or lines that select ordered page-76 text.')
    lines.append('')
    lines.append('## Anchors Mapped To OCR Page 76')
    for name, point in anchors_ocr.items():
        lines.append(f'- {name}: ({point[0]:.1f}, {point[1]:.1f})')
    lines.append('')
    lines.append('## Summary')
    lines.append(f'- unique readable selections: {len(selections)}')
    lines.append(f'- candidate private keys from top selections: {len(candidates)}')
    lines.append(f'- derived addresses checked: {len(address_map)}')
    lines.append(f'- active addresses found: {len(found)}')
    lines.append('')
    lines.append('## Top Selections')
    for idx, selection in enumerate(selections[:40], 1):
        lines.append(
            f"{idx:02d}. score={selection['score']:.1f} "
            f"{selection['a']} -> {selection['b']} "
            f"mode={selection['mode']} threshold={selection['threshold']} order={selection['order']}"
        )
        lines.append(f"    {selection['text']}")
    lines.append('')
    lines.append('## Chain Hits')
    if not found:
        lines.append('- none')
    for hit in found:
        lines.append(
            f"- {hit['address']} {hit['kind']} received={hit['total_received']} "
            f"balance={hit['final_balance']} label={hit['label']} source={hit['source']}"
        )
    (OUT / 'anchor_ray_selector_experiment.md').write_text('\n'.join(lines) + '\n')


def main():
    selections, anchors_ocr, image = build_selections()
    candidates = candidate_secrets(selections)
    address_map = build_address_map(candidates)
    print(f'unique readable selections: {len(selections)}')
    print(f'candidate private keys from top selections: {len(candidates)}')
    print(f'derived addresses to check: {len(address_map)}')
    draw_top_lines(image, selections, OUT / 'anchor_ray_selector_top_lines.png')
    found = check_activity(address_map, batch_size=40, sleep_s=0.25) if address_map else []
    print(f'active addresses found: {len(found)}')
    for hit in found:
        print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} {hit['label']}")
    write_report(selections, anchors_ocr, candidates, address_map, found)
    print(f"report: {OUT / 'anchor_ray_selector_experiment.md'}")
    print(f"image: {OUT / 'anchor_ray_selector_top_lines.png'}")


if __name__ == '__main__':
    main()
