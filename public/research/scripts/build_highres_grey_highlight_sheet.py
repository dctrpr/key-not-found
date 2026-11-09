#!/usr/bin/env python3
from pathlib import Path
import json
import math

from PIL import Image, ImageDraw

from build_3d_article_map_data import page_mapping, inverse_box
from highres_reflection_extract import upright_image
from read_manual_inverted_reflections import INVERTED_BOXES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'highlight_audit'
OUT.mkdir(parents=True, exist_ok=True)

MANUAL_LABELS = {
    (75, 1): 'money printers, banking',
    (75, 2): 'terrorists, stock traders, central bank arsonists',
    (75, 3): "Don't fall for shitcoinery",
    (76, 1): 'Gotta be this way... post-1971 fiat money',
    (76, 2): 'nonsense',
    (76, 3): "It's a stun gun to the genitals",
    (76, 4): '$1 billion',
    (76, 5): 'Volcano Bonds',
    (77, 1): 'Sorry Bhutan... shitcoin hell',
    (77, 2): 'shitcoiners, useless Royals',
    (77, 3): 'It does this by monetizing',
    (78, 1): 'gargantuanly wasteful',
    (78, 2): 'money printing',
    (78, 3): 'wars to keep it going',
    (79, 1): 'war and violence economy',
}


def pad_box(box, width, height, pad=70):
    return [
        max(0, int(math.floor(box[0] - pad))),
        max(0, int(math.floor(box[1] - pad))),
        min(width, int(math.ceil(box[2] + pad))),
        min(height, int(math.ceil(box[3] + pad))),
    ]


def crop(page_img, box, out_path, label):
    padded = pad_box(box, page_img.width, page_img.height)
    img = page_img.crop(tuple(padded)).convert('RGB')
    draw = ImageDraw.Draw(img)
    local = [box[0] - padded[0], box[1] - padded[1], box[2] - padded[0], box[3] - padded[1]]
    draw.rectangle(local, outline=(255, 0, 0), width=5)
    draw.rectangle((0, 0, min(img.width, 920), 40), fill='white')
    draw.text((8, 10), label, fill='black')
    img.save(out_path, quality=96)
    return out_path


def contact_sheet(rows, out_path, thumb_width=620):
    thumbs = []
    for row in rows:
        img = Image.open(row['crop']).convert('RGB')
        scale = thumb_width / img.width
        thumb = img.resize((thumb_width, max(1, int(img.height * scale))))
        label_h = 74
        tile = Image.new('RGB', (thumb_width, thumb.height + label_h), 'white')
        tile.paste(thumb, (0, label_h))
        draw = ImageDraw.Draw(tile)
        draw.text((8, 6), f"{row['id']} p{row['page']}\nexpected: {row['expected']}", fill='black')
        thumbs.append(tile)
    cols = 2
    cell_h = max(t.height for t in thumbs)
    sheet = Image.new('RGB', (thumb_width * cols, cell_h * math.ceil(len(thumbs) / cols)), (235, 235, 235))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % cols) * thumb_width, (i // cols) * cell_h))
    sheet.save(out_path, quality=94)
    return out_path


def main():
    rows = []
    for page_no, boxes in INVERTED_BOXES.items():
        mapping = page_mapping(page_no)
        page_img = upright_image(page_no).convert('RGB')
        for idx, ocr_box in enumerate(boxes, 1):
            highres_box = inverse_box(ocr_box, mapping)
            label = MANUAL_LABELS.get((page_no, idx), '')
            row_id = f'p{page_no}_grey_{idx}'
            crop_path = OUT / f'{row_id}_crop.jpg'
            crop(page_img, highres_box, crop_path, row_id)
            rows.append({
                'id': row_id,
                'page': page_no,
                'ocrBox': list(ocr_box),
                'highresBox': highres_box,
                'expected': label,
                'crop': str(crop_path),
            })
    sheet = contact_sheet(rows, OUT / 'manual_grey_highres_contact_sheet.jpg')
    (OUT / 'manual_grey_highres_crops.json').write_text(json.dumps({'contactSheet': str(sheet), 'rows': rows}, indent=2))
    lines = ['# Manual Grey/Black Highlight High-Res Crops', '', f'- contact sheet: `{sheet}`', '']
    for row in rows:
        lines.append(f"- {row['id']} p{row['page']} expected=`{row['expected']}` crop=`{row['crop']}`")
    (OUT / 'manual_grey_highres_crops.md').write_text('\n'.join(lines) + '\n')
    print(f'wrote {sheet}')
    print(f"wrote {OUT / 'manual_grey_highres_crops.md'}")


if __name__ == '__main__':
    main()
