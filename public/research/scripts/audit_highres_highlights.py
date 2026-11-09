#!/usr/bin/env python3
import json
import math
import re
from collections import OrderedDict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'analysis_outputs' / '3d_article_map' / 'article_3d_map_data.json'
COLOR = ROOT / 'analysis_outputs' / '3d_article_map' / 'annotated_color_span_analysis.json'
OUT = ROOT / 'analysis_outputs' / 'highlight_audit'
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / 'highres_highlight_audit.md'
JSON_OUT = OUT / 'highres_highlight_audit.json'


def norm(value):
    return re.sub(r'[^a-z0-9]+', '', value.lower())


def word_area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def overlap(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    return max(0, x2 - x1) * max(0, y2 - y1)


def center_in(box, region):
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    return region[0] <= cx <= region[2] and region[1] <= cy <= region[3]


def words_in_box(words, box, min_overlap=0.08):
    selected = []
    for word in words:
        wbox = word['box']
        ov = overlap(wbox, box)
        ratio = ov / max(1, word_area(wbox))
        if center_in(wbox, box) or ratio >= min_overlap:
            selected.append(word)
    return sorted(selected, key=lambda item: (round(item['center'][1] / 22), item['center'][0]))


def union_box(boxes):
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def pad_box(box, width, height, pad=55):
    return [
        max(0, int(math.floor(box[0] - pad))),
        max(0, int(math.floor(box[1] - pad))),
        min(width, int(math.ceil(box[2] + pad))),
        min(height, int(math.ceil(box[3] + pad))),
    ]


def crop_and_mark(page_img, box, out_path, label):
    padded = pad_box(box, page_img.width, page_img.height, pad=70)
    crop = page_img.crop(tuple(padded)).convert('RGB')
    draw = ImageDraw.Draw(crop)
    local = [box[0] - padded[0], box[1] - padded[1], box[2] - padded[0], box[3] - padded[1]]
    draw.rectangle(local, outline=(255, 0, 0), width=5)
    draw.rectangle((0, 0, min(crop.width, 900), 36), fill=(255, 255, 255))
    draw.text((10, 8), label, fill=(0, 0, 0))
    crop.save(out_path, quality=96)
    return out_path


def make_contact_sheet(items, out_path, thumb_width=520):
    thumbs = []
    for item in items:
        img = Image.open(item['crop']).convert('RGB')
        scale = thumb_width / img.width
        thumb = img.resize((thumb_width, max(1, int(img.height * scale))))
        label_h = 82
        canvas = Image.new('RGB', (thumb_width, thumb.height + label_h), 'white')
        canvas.paste(thumb, (0, label_h))
        draw = ImageDraw.Draw(canvas)
        text = f"{item['id']} p{item['page']} {item.get('kind', '')}\n{item.get('expected', '')[:80]}\nOCR: {item.get('ocrText', '')[:80]}"
        draw.text((8, 6), text, fill=(0, 0, 0))
        thumbs.append(canvas)
    if not thumbs:
        return None
    cols = 2
    rows = math.ceil(len(thumbs) / cols)
    cell_w = thumb_width
    cell_h = max(t.height for t in thumbs)
    sheet = Image.new('RGB', (cell_w * cols, cell_h * rows), (235, 235, 235))
    for idx, thumb in enumerate(thumbs):
        x = (idx % cols) * cell_w
        y = (idx // cols) * cell_h
        sheet.paste(thumb, (x, y))
    sheet.save(out_path, quality=94)
    return out_path


def page_images(data):
    base = ROOT / 'analysis_outputs' / '3d_article_map'
    return {
        page['page']: Image.open(base / page['image']).convert('RGB')
        for page in data['pages']
    }


def text_for_words(words):
    return ' '.join(word['text'] for word in words)


def audit_visual_orange(data, images):
    pages = {page['page']: page for page in data['pages']}
    rows = []
    for page_no, page in pages.items():
        page_img = images[page_no]
        for highlight in page.get('highlights', []):
            box = highlight['box']
            words = words_in_box(page['words'], box)
            row = {
                'id': highlight['id'],
                'page': page_no,
                'kind': 'visual-orange',
                'box': box,
                'ocrText': text_for_words(words),
                'wordIndexes': [word['index'] for word in words],
            }
            crop_path = OUT / f"{row['id']}_crop.jpg"
            row['crop'] = str(crop_and_mark(page_img, box, crop_path, row['id']))
            rows.append(row)
    return rows


def audit_annotated_spans(data, color_data, images):
    pages = {page['page']: page for page in data['pages']}
    rows = []
    for idx, span in enumerate(color_data['rows'], 1):
        if not span.get('wordIndexes'):
            rows.append({
                'id': f"annotated_{idx:02d}",
                'page': span['articlePage'],
                'kind': f"annotated-{span['color']}",
                'expected': span['phrase'],
                'ocrText': '',
                'wordIndexes': [],
                'status': 'unmatched-in-canonical-model',
            })
            continue
        page = pages.get(span['articlePage'])
        if not page:
            continue
        by_index = {word['index']: word for word in page['words']}
        words = [by_index[index] for index in span['wordIndexes'] if index in by_index]
        if not words:
            continue
        box = union_box([word['box'] for word in words])
        page_img = images[span['articlePage']]
        expected_norm = norm(span['phrase'])
        ocr_text = text_for_words(words)
        ocr_norm = norm(ocr_text)
        row = {
            'id': f"annotated_{idx:02d}_{span['color']}",
            'page': span['articlePage'],
            'kind': f"annotated-{span['color']}",
            'box': box,
            'expected': span['phrase'],
            'ocrText': ocr_text,
            'wordIndexes': span['wordIndexes'],
            'status': 'ok' if expected_norm == ocr_norm or expected_norm in ocr_norm or ocr_norm in expected_norm else 'text-mismatch-check-crop',
        }
        crop_path = OUT / f"{row['id']}_crop.jpg"
        row['crop'] = str(crop_and_mark(page_img, box, crop_path, row['id']))
        rows.append(row)
    return rows


def likely_matches(visual_rows, annotated_rows):
    matches = []
    annotated_valid = [row for row in annotated_rows if row.get('box')]
    for visual in visual_rows:
        vtokens = norm(visual.get('ocrText', ''))
        candidates = []
        for annotated in annotated_valid:
            if visual['page'] != annotated['page']:
                continue
            abox = annotated['box']
            vbox = visual['box']
            ov = overlap(vbox, abox)
            spatial = ov / max(1, min(word_area(vbox), word_area(abox)))
            text_hit = bool(vtokens and (vtokens in norm(annotated.get('expected', '')) or norm(annotated.get('expected', '')) in vtokens))
            if spatial > 0.05 or text_hit:
                candidates.append({
                    'annotatedId': annotated['id'],
                    'kind': annotated['kind'],
                    'expected': annotated.get('expected', ''),
                    'spatialOverlap': round(spatial, 3),
                    'textHit': text_hit,
                })
        matches.append({'visualId': visual['id'], 'page': visual['page'], 'ocrText': visual['ocrText'], 'candidates': candidates})
    return matches


def main():
    data = json.loads(DATA.read_text())
    color_data = json.loads(COLOR.read_text())
    images = page_images(data)
    visual_rows = audit_visual_orange(data, images)
    annotated_rows = audit_annotated_spans(data, color_data, images)
    matches = likely_matches(visual_rows, annotated_rows)

    orange_sheet = make_contact_sheet(visual_rows, OUT / 'visual_orange_contact_sheet.jpg')
    annotated_sheet = make_contact_sheet([row for row in annotated_rows if row.get('crop')], OUT / 'annotated_color_contact_sheet.jpg')

    result = {
        'visualOrangeRows': visual_rows,
        'annotatedColorRows': annotated_rows,
        'visualToAnnotatedMatches': matches,
        'visualOrangeContactSheet': str(orange_sheet) if orange_sheet else None,
        'annotatedColorContactSheet': str(annotated_sheet) if annotated_sheet else None,
    }
    JSON_OUT.write_text(json.dumps(result, indent=2))

    lines = ['# High-Resolution Highlight Audit', '']
    lines.append('Scope: treat the high-resolution magazine page images as the visual source of truth for highlight locations. Text is extracted from the mapped OCR word layer, so every crop needs manual visual confirmation where OCR is noisy.')
    lines.append('')
    lines.append('## Contact Sheets')
    lines.append(f"- visual orange crops: `{orange_sheet}`")
    lines.append(f"- annotated orange/grey phrase crops: `{annotated_sheet}`")
    lines.append('')
    lines.append('## Visual Orange Boxes From High-Res Source')
    for row in visual_rows:
        lines.append(f"- {row['id']} p{row['page']} words={row['wordIndexes']} OCR=`{row['ocrText']}` crop=`{row['crop']}`")
    lines.append('')
    lines.append('## Annotated Color Phrase Crops')
    for row in annotated_rows:
        status = row.get('status', 'ok')
        lines.append(
            f"- {row['id']} p{row['page']} {row['kind']} status={status} "
            f"expected=`{row.get('expected', '')}` OCR=`{row.get('ocrText', '')}` crop=`{row.get('crop', '')}`"
        )
    lines.append('')
    lines.append('## Visual Orange To Annotated Matches')
    for match in matches:
        cands = '; '.join(f"{cand['annotatedId']} {cand['kind']} overlap={cand['spatialOverlap']} textHit={cand['textHit']} expected=`{cand['expected']}`" for cand in match['candidates'])
        if not cands:
            cands = 'no annotated match'
        lines.append(f"- {match['visualId']} p{match['page']} OCR=`{match['ocrText']}` -> {cands}")
    lines.append('')
    lines.append('## Needs Manual Attention')
    for row in annotated_rows:
        if row.get('status') != 'ok':
            lines.append(f"- {row['id']} p{row['page']} {row['kind']}: {row.get('status')} expected=`{row.get('expected', '')}` OCR=`{row.get('ocrText', '')}`")
    for match in matches:
        if not match['candidates']:
            lines.append(f"- {match['visualId']} p{match['page']}: high-res orange box has no matched annotation; OCR=`{match['ocrText']}`")
    lines.append('')
    lines.append('## Assessment')
    lines.append('- The high-res orange boxes are now individually cropped and indexed. Use the crop sheets for exact visual confirmation before treating any highlighted phrase as canonical.')
    lines.append('- OCR text remains imperfect in several highlighted regions, especially page 79 and page 80. The manually supplied transcript should override OCR only after visually checking the crop.')
    lines.append('- Grey/black highlights are represented through annotated phrase crops, because automatic black-box detection is not reliable enough to be a source of truth without manual confirmation.')
    REPORT.write_text('\n'.join(lines) + '\n')
    print(f'wrote {JSON_OUT}')
    print(f'wrote {REPORT}')
    print(f'wrote {orange_sheet}')
    print(f'wrote {annotated_sheet}')


if __name__ == '__main__':
    main()
