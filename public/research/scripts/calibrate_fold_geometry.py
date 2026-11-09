#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import re
from collections import OrderedDict
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

from extract_visual_masks import PAGES, masks_for_page
from read_reflected_masks import PDF, PDF_PAGE_INDEX, orange_boxes
from search_visual_private_keys import (
    build_address_map,
    check_activity,
    clean_words,
    digest_candidates,
    direct_text_candidates,
    key_addresses,
    text_variants,
    valid_secret,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs'
PAIR_DIRECTIONS = [(79, 75), (75, 79), (78, 76), (76, 78)]


def restricted_orange_mask(page_no, fill_boxes=True):
    img = Image.open(PAGES[page_no]).convert('RGB')
    base = masks_for_page(img)['orange']
    restricted = np.zeros_like(base, dtype=bool)
    boxes, _ = orange_boxes(page_no)
    for x1, y1, x2, y2 in boxes:
        if fill_boxes:
            restricted[y1:y2, x1:x2] = True
        else:
            restricted[y1:y2, x1:x2] |= base[y1:y2, x1:x2]
    return restricted


def reflected_mask(page_no, dx=0, dy=0, fill_boxes=True):
    mask = np.fliplr(restricted_orange_mask(page_no, fill_boxes=fill_boxes))
    h, w = mask.shape
    shifted = np.zeros_like(mask, dtype=bool)
    src_x1 = max(0, -dx)
    src_x2 = min(w, w - dx)
    dst_x1 = max(0, dx)
    dst_x2 = min(w, w + dx)
    src_y1 = max(0, -dy)
    src_y2 = min(h, h - dy)
    dst_y1 = max(0, dy)
    dst_y2 = min(h, h + dy)
    if src_x1 < src_x2 and src_y1 < src_y2:
        shifted[dst_y1:dst_y2, dst_x1:dst_x2] = mask[src_y1:src_y2, src_x1:src_x2]
    return shifted


def page_chars(doc, page_no):
    page = doc[PDF_PAGE_INDEX[page_no]]
    img = Image.open(PAGES[page_no]).convert('RGB')
    sx = img.width / page.rect.width
    sy = img.height / page.rect.height
    chars = []
    for block in page.get_text('rawdict').get('blocks', []):
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                for ch in span.get('chars', []):
                    c = ch.get('c', '')
                    bbox = fitz.Rect(ch['bbox'])
                    if not c or bbox.is_empty:
                        continue
                    x1 = max(0, min(img.width, int(bbox.x0 * sx)))
                    y1 = max(0, min(img.height, int(bbox.y0 * sy)))
                    x2 = max(0, min(img.width, int(np.ceil(bbox.x1 * sx))))
                    y2 = max(0, min(img.height, int(np.ceil(bbox.y1 * sy))))
                    if x1 >= x2 or y1 >= y2:
                        continue
                    chars.append({'c': c, 'bbox': (x1, y1, x2, y2), 'x': (x1 + x2) / 2, 'y': (y1 + y2) / 2})
    return sorted(chars, key=lambda item: (item['y'], item['x']))


def select_chars(chars, mask, min_coverage=0.08, center_only=False):
    selected = []
    h, w = mask.shape
    for ch in chars:
        cx = max(0, min(w - 1, int(ch['x'])))
        cy = max(0, min(h - 1, int(ch['y'])))
        if center_only:
            if mask[cy, cx]:
                selected.append(ch)
            continue
        x1, y1, x2, y2 = ch['bbox']
        x1 = max(0, min(w, x1))
        x2 = max(0, min(w, x2))
        y1 = max(0, min(h, y1))
        y2 = max(0, min(h, y2))
        if x1 >= x2 or y1 >= y2:
            continue
        region = mask[y1:y2, x1:x2]
        coverage = float(region.mean()) if region.size else 0.0
        if coverage >= min_coverage or mask[cy, cx]:
            selected.append(ch)
    return selected


def select_chars_shifted_centers(chars, reflected_base_mask, dx, dy):
    h, w = reflected_base_mask.shape
    selected = []
    for ch in chars:
        sx = int(ch['x']) - dx
        sy = int(ch['y']) - dy
        if 0 <= sx < w and 0 <= sy < h and reflected_base_mask[sy, sx]:
            selected.append(ch)
    return selected


def chars_to_lines(chars, y_gap=14):
    lines = []
    current = []
    current_y = None
    for ch in sorted(chars, key=lambda item: (item['y'], item['x'])):
        if current_y is None or abs(ch['y'] - current_y) <= y_gap:
            current.append(ch)
            current_y = ch['y'] if current_y is None else (current_y * 0.85 + ch['y'] * 0.15)
        else:
            lines.append(''.join(item['c'] for item in sorted(current, key=lambda item: item['x'])).strip())
            current = [ch]
            current_y = ch['y']
    if current:
        lines.append(''.join(item['c'] for item in sorted(current, key=lambda item: item['x'])).strip())
    return [line for line in lines if line]


def score_selection(lines):
    text = ' '.join(lines)
    alnum = sum(ch.isalnum() for ch in text)
    words = clean_words(text)
    long_words = sum(len(word) >= 3 for word in words)
    fragments = sum(len(word) <= 1 for word in words)
    return alnum + long_words * 5 - fragments * 3


def calibrate_pair(source_page, target_page, search_radius=36, step=4, fill_boxes=True):
    doc = fitz.open(PDF)
    chars = page_chars(doc, target_page)
    base_mask = np.fliplr(restricted_orange_mask(source_page, fill_boxes=fill_boxes))
    results = []
    for dx in range(-search_radius, search_radius + 1, step):
        for dy in range(-search_radius, search_radius + 1, step):
            selected = select_chars_shifted_centers(chars, base_mask, dx, dy)
            lines = chars_to_lines(selected)
            text = ' '.join(lines)
            if not text.strip():
                continue
            results.append(
                {
                    'source': source_page,
                    'target': target_page,
                    'dx': dx,
                    'dy': dy,
                    'score': score_selection(lines),
                    'chars': sum(len(line) for line in lines),
                    'words': len(clean_words(text)),
                    'text': text,
                }
            )
    return sorted(results, key=lambda item: (-item['score'], abs(item['dx']) + abs(item['dy']), -item['chars']))


def page77_sequences():
    doc = fitz.open(PDF)
    chars = page_chars(doc, 77)
    raw = ''.join(ch['c'] for ch in chars)
    letters = ''.join(ch for ch in raw if ch.isalpha())
    alnum = ''.join(ch for ch in raw if ch.isalnum())
    words = clean_words(raw)
    return {'raw': raw, 'letters': letters, 'alnum': alnum, 'words': words}


def number_streams(text):
    words = clean_words(text)
    letters = ''.join(ch for ch in text if ch.isalpha())
    streams = OrderedDict()
    streams['word_lengths'] = [len(word) for word in words]
    streams['first_alpha'] = [ord(word[0].lower()) - 96 for word in words if word and word[0].isalpha()]
    streams['last_alpha'] = [ord(word[-1].lower()) - 96 for word in words if word and word[-1].isalpha()]
    streams['letter_alpha'] = [ord(ch.lower()) - 96 for ch in letters]
    streams['numbers'] = [int(n) for n in re.findall(r'\d+', text)]
    if streams['first_alpha'] and streams['last_alpha']:
        streams['first_last_alpha'] = list(itertools.chain.from_iterable(zip(streams['first_alpha'], streams['last_alpha'])))
    return {key: values for key, values in streams.items() if values}


def index_page77(label, text):
    seqs = page77_sequences()
    outputs = OrderedDict()
    for stream_name, nums in number_streams(text).items():
        if len(nums) < 4:
            continue
        for seq_name in ('letters', 'alnum', 'raw'):
            seq = seqs[seq_name]
            if not seq:
                continue
            one_based = ''.join(seq[(num - 1) % len(seq)] for num in nums)
            zero_based = ''.join(seq[num % len(seq)] for num in nums)
            outputs[f'{label}:{stream_name}:page77_{seq_name}:1based'] = one_based
            outputs[f'{label}:{stream_name}:page77_{seq_name}:0based'] = zero_based
        words = seqs['words']
        if words:
            outputs[f'{label}:{stream_name}:page77_words:1based'] = ' '.join(words[(num - 1) % len(words)] for num in nums)
            outputs[f'{label}:{stream_name}:page77_words:0based'] = ' '.join(words[num % len(words)] for num in nums)
    return outputs


def candidate_secrets(calibrations, top_n=3):
    candidates = OrderedDict()

    def add(label, secret, source):
        if valid_secret(secret):
            candidates.setdefault(secret.hex(), {'label': label, 'secret': secret, 'source': source})

    selected = []
    for (source, target), results in calibrations.items():
        for item in results[:top_n]:
            selected.append((f'{source}_onto_{target}_dx{item["dx"]}_dy{item["dy"]}', item['text']))

    combined = ' '.join(text for _, text in selected)
    selected.append(('all_calibrated_top', combined))
    selected.append(('all_calibrated_top_reverse', combined[::-1]))

    for label, text in selected:
        derived = index_page77(label, text)
        derived[label] = text
        for out_label, value in derived.items():
            for tlabel, variant in text_variants(out_label, value).items():
                for clabel, secret, source in digest_candidates(tlabel, variant):
                    add(clabel, secret, source)
                for clabel, secret, source in direct_text_candidates(tlabel, variant):
                    add(clabel, secret, source)
    return candidates


def write_report(calibrations, candidates):
    lines = ['# Fold Calibration Report', '']
    for pair, results in calibrations.items():
        lines.append(f'## {pair[0]} reflected onto {pair[1]}')
        for item in results[:10]:
            lines.append(f'dx={item["dx"]:+d} dy={item["dy"]:+d} score={item["score"]} chars={item["chars"]} words={item["words"]}')
            lines.append(item['text'])
            lines.append('')
    lines.append('## Candidate Summary')
    lines.append(f'private-key candidates: {len(candidates)}')
    for item in itertools.islice(candidates.values(), 30):
        lines.append(f'{item["secret"].hex()} {item["label"]} source={item["source"][:120]}')
    (OUT / 'fold_calibration_report.md').write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description='Calibrate reflected highlight masks and test page-77 indexing candidates.')
    parser.add_argument('--radius', type=int, default=36)
    parser.add_argument('--step', type=int, default=4)
    parser.add_argument('--top-n', type=int, default=3)
    parser.add_argument('--raw-orange', action='store_true', help='use only orange pixels instead of filled highlight boxes')
    parser.add_argument('--check-chain', action='store_true')
    parser.add_argument('--kind-filter', default='all')
    parser.add_argument('--batch-size', type=int, default=35)
    parser.add_argument('--sleep', type=float, default=1.5)
    args = parser.parse_args()

    calibrations = OrderedDict()
    for source, target in PAIR_DIRECTIONS:
        calibrations[(source, target)] = calibrate_pair(
            source,
            target,
            search_radius=args.radius,
            step=args.step,
            fill_boxes=not args.raw_orange,
        )

    candidates = candidate_secrets(calibrations, top_n=args.top_n)
    write_report(calibrations, candidates)

    print(f'wrote {OUT / "fold_calibration_report.md"}')
    for pair, results in calibrations.items():
        best = results[0] if results else None
        if best:
            print(f'{pair[0]}->{pair[1]} best dx={best["dx"]:+d} dy={best["dy"]:+d} score={best["score"]} chars={best["chars"]} words={best["words"]}')
            print(best['text'][:240])
    print(f'private-key candidates: {len(candidates)}')

    if args.check_chain:
        address_map = build_address_map(candidates, kind_filter=args.kind_filter)
        print(f'checking {len(address_map)} addresses...')
        found = check_activity(address_map, batch_size=args.batch_size, sleep_s=args.sleep)
        print(f'addresses with activity: {len(found)}')
        for hit in found:
            print()
            print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']}")
            print(f"{hit['label']} secret={hit['secret'].hex()}")
            print(hit['source'][:500])


if __name__ == '__main__':
    main()
