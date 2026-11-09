#!/usr/bin/env python3
import json
import re
from collections import defaultdict
from pathlib import Path

import fitz
from PIL import Image

from highres_reflection_extract import (
    SOURCE_PAGES,
    ensure_highres_sources,
    fit_mapping_for_page,
    orange_boxes,
    reflected_selection as highres_reflected_selection,
    upright_image,
)
from read_reflected_masks import PDF as OCR_PDF, PDF_PAGE_INDEX, PAGES as OCR_IMAGES
from run_anchor_ray_selector import ANCHORS_HIGHRES, build_selections


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / '3d_article_map'
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [75, 76, 77, 78, 79, 80]
FOCUS_TERMS = {
    'bitcoin',
    'salvador',
    'bukele',
    'volcano',
    'volcanoes',
    'bonds',
    'bond',
    'imf',
    'mirror',
    'overdose',
    'president',
    'toxic',
    'love',
    'fear',
    'energy',
    'genesis',
    'satoshi',
    'utxo',
}


def clean_token(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def inverse_point(point, mapping):
    ax, bx, ay, by = mapping
    x, y = point
    if abs(ax) < 1e-9 or abs(ay) < 1e-9:
        return x, y
    return ((x - bx) / ax, (y - by) / ay)


def inverse_box(box, mapping):
    x1, y1 = inverse_point((box[0], box[1]), mapping)
    x2, y2 = inverse_point((box[2], box[3]), mapping)
    return [round(min(x1, x2), 2), round(min(y1, y2), 2), round(max(x1, x2), 2), round(max(y1, y2), 2)]


def pdf_box_to_ocr(box, pdf_rect, image_size):
    return [
        box[0] / pdf_rect.width * image_size[0],
        box[1] / pdf_rect.height * image_size[1],
        box[2] / pdf_rect.width * image_size[0],
        box[3] / pdf_rect.height * image_size[1],
    ]


def write_upright_images():
    paths = {}
    for page_no in PAGES:
        img = upright_image(page_no).convert('RGB')
        out_path = OUT / f'page_{page_no}_upright.jpg'
        img.save(out_path, quality=92)
        paths[page_no] = out_path
    return paths


def page_mapping(page_no):
    boxes, _ = orange_boxes(page_no)
    mapping, _, _ = fit_mapping_for_page(page_no, boxes)
    return mapping


def extract_page(doc, page_no, image_path, ray_word_scores):
    pdf_page = doc[PDF_PAGE_INDEX[page_no]]
    ocr_size = Image.open(OCR_IMAGES[page_no]).size
    highres_size = Image.open(image_path).size
    mapping = page_mapping(page_no)
    words = []
    chars = []
    word_lookup = {}

    for word_idx, word in enumerate(pdf_page.get_text('words')):
        text = word[4].strip()
        if not text:
            continue
        ocr_box = pdf_box_to_ocr(word[:4], pdf_page.rect, ocr_size)
        highres_box = inverse_box(ocr_box, mapping)
        token = clean_token(text)
        importance = 0
        reasons = []
        if token in FOCUS_TERMS:
            importance += 3
            reasons.append('focus-term')
        if ray_word_scores.get((page_no, word_idx)):
            importance += ray_word_scores[(page_no, word_idx)]
            reasons.append('anchor-ray')
        if page_no == 76 and token in {'president', 'nayib', 'bukele', 'salvador', 'volcanoes', 'volcano', 'imf'}:
            importance += 3
            reasons.append('thread-media-page76')
        record = {
            'id': f'p{page_no}w{word_idx}',
            'index': word_idx,
            'text': text,
            'token': token,
            'box': highres_box,
            'center': [round((highres_box[0] + highres_box[2]) / 2, 2), round((highres_box[1] + highres_box[3]) / 2, 2)],
            'importance': importance,
            'reasons': reasons,
        }
        words.append(record)
        word_lookup[word_idx] = record

    # Character extraction keeps every OCR character available for the 3D map.
    char_idx = 0
    for block in pdf_page.get_text('rawdict').get('blocks', []):
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                for ch in span.get('chars', []):
                    value = ch.get('c', '')
                    if not value:
                        continue
                    bbox = ch.get('bbox')
                    if not bbox:
                        continue
                    ocr_box = pdf_box_to_ocr(bbox, pdf_page.rect, ocr_size)
                    highres_box = inverse_box(ocr_box, mapping)
                    cx = (highres_box[0] + highres_box[2]) / 2
                    cy = (highres_box[1] + highres_box[3]) / 2
                    chars.append(
                        {
                            'id': f'p{page_no}c{char_idx}',
                            'i': char_idx,
                            'c': value,
                            'box': highres_box,
                            'x': round(cx, 2),
                            'y': round(cy, 2),
                        }
                    )
                    char_idx += 1

    highlights = []
    for idx, box in enumerate(orange_boxes(page_no)[0], 1):
        highlights.append({'id': f'p{page_no}_orange_{idx}', 'kind': 'orange', 'box': list(map(float, box))})

    return {
        'page': page_no,
        'image': f'page_{page_no}_upright.jpg',
        'width': highres_size[0],
        'height': highres_size[1],
        'chars': chars,
        'words': words,
        'highlights': highlights,
    }


def build_ray_word_scores():
    selections, _, _ = build_selections()
    scores = defaultdict(int)
    top = []
    for selection_idx, selection in enumerate(selections[:40], 1):
        score = max(1, int(round(selection['score'] / 18)))
        word_ids = []
        for word in selection['words']:
            scores[(76, word['index'])] += score
            word_ids.append(word['index'])
        top.append(
            {
                'rank': selection_idx,
                'score': round(selection['score'], 2),
                'a': selection['a'],
                'b': selection['b'],
                'mode': selection['mode'],
                'threshold': selection['threshold'],
                'order': selection['order'],
                'text': selection['text'],
                'wordIndexes': word_ids,
            }
        )
    return scores, top


def build_reflections():
    reflections = []
    for source, target in [(79, 75), (78, 76), (76, 78), (79, 76)]:
        target_mapping = page_mapping(target)
        target_width = Image.open(OCR_IMAGES[target]).size[0]
        for idx, src_box, reflected_ocr_box, text, chars in highres_reflected_selection(source, target):
            target_highres_box = inverse_box(reflected_ocr_box, target_mapping)
            reflections.append(
                {
                    'id': f'{source}_{target}_{idx}',
                    'source': source,
                    'target': target,
                    'sourceBox': list(map(float, src_box)),
                    'targetBox': target_highres_box,
                    'text': text,
                    'chars': chars,
                    'targetOcrWidth': target_width,
                }
            )
    return reflections


def build_anchors():
    anchors = []
    for name, point in ANCHORS_HIGHRES.items():
        page = 76
        source = 'page76-or-page79-mirrored'
        if name.startswith('p79_'):
            page = 76
            source = 'page79-mirrored-onto-page76'
        anchors.append({'id': name, 'page': page, 'source': source, 'point': [round(point[0], 2), round(point[1], 2)]})

    anchors.extend(
        [
            {'id': 'p79_pill_1_original', 'page': 79, 'source': 'page79-original', 'point': [171.0, 2408.0]},
            {'id': 'p79_pill_2_original', 'page': 79, 'source': 'page79-original', 'point': [421.5, 2454.5]},
            {'id': 'p79_pill_3_original', 'page': 79, 'source': 'page79-original', 'point': [606.0, 2608.5]},
            {'id': 'p79_pill_4_original', 'page': 79, 'source': 'page79-original', 'point': [437.0, 2780.5]},
            {'id': 'p79_pill_5_original', 'page': 79, 'source': 'page79-original', 'point': [183.5, 2968.0]},
        ]
    )
    return anchors


def main():
    ensure_highres_sources()
    image_paths = write_upright_images()
    doc = fitz.open(OCR_PDF)
    ray_scores, ray_selections = build_ray_word_scores()
    pages = [extract_page(doc, page_no, image_paths[page_no], ray_scores) for page_no in PAGES]
    data = {
        'meta': {
            'title': 'Max Keiser Puzzle 3D Article Map',
            'purpose': 'High-resolution page planes with every OCR character mapped into 3D, plus highlight, mirror, anchor, and ray-selector layers.',
            'sourcePdf': str(OCR_PDF),
            'highresSource': str(ROOT / 'magazine.pdf'),
        },
        'pages': pages,
        'anchors': build_anchors(),
        'reflections': build_reflections(),
        'raySelections': ray_selections,
        'focusTerms': sorted(FOCUS_TERMS),
    }
    out_path = OUT / 'article_3d_map_data.json'
    out_path.write_text(json.dumps(data, separators=(',', ':')))

    summary_lines = [
        '# 3D Article Map Data',
        '',
        f'- pages: {len(pages)}',
        f'- total OCR characters: {sum(len(page["chars"]) for page in pages)}',
        f'- total OCR words: {sum(len(page["words"]) for page in pages)}',
        f'- anchors: {len(data["anchors"])}',
        f'- reflected highlight boxes: {len(data["reflections"])}',
        f'- top anchor-ray selections: {len(data["raySelections"])}',
        f'- data file: `{out_path}`',
        '',
        '## Page Counts',
    ]
    for page in pages:
        important = sum(1 for word in page['words'] if word['importance'] > 0)
        summary_lines.append(f'- page {page["page"]}: {len(page["chars"])} chars, {len(page["words"])} words, {important} important words')
    (OUT / 'article_3d_map_data_summary.md').write_text('\n'.join(summary_lines) + '\n')
    print('\n'.join(summary_lines))


if __name__ == '__main__':
    main()
