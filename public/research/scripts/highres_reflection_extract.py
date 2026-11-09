#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO

import fitz
import numpy as np
from PIL import Image

from extract_visual_masks import masks_for_page, connected_components, merge_close_boxes, draw_boxes
from read_reflected_masks import PDF, PDF_PAGE_INDEX, PAGES as OCR_PAGES, image_box_to_pdf_rect, words_in_rect, chars_in_rect, orange_boxes as ocr_orange_boxes


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'highres'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE_OUT = ROOT / 'analysis_outputs' / 'source_images'
SOURCE_OUT.mkdir(parents=True, exist_ok=True)

SOURCE_PAGES = {
    75: SOURCE_OUT / 'magazine_page_75.jpg',
    76: SOURCE_OUT / 'magazine_page_76.jpg',
    77: SOURCE_OUT / 'magazine_page_77.jpg',
    78: SOURCE_OUT / 'magazine_page_78.jpg',
    79: SOURCE_OUT / 'magazine_page_79.jpg',
    80: SOURCE_OUT / 'magazine_page_80.jpg',
}

MAGAZINE_PDF = ROOT / 'magazine.pdf'


def ensure_highres_sources():
    missing = [path for path in SOURCE_PAGES.values() if not path.exists()]
    if not missing:
        return

    doc = fitz.open(MAGAZINE_PDF)
    for article_page, out_path in SOURCE_PAGES.items():
        # Article page 75 is PDF page 3 / embedded image index 2.
        pdf_page_index = article_page - 73
        images = doc[pdf_page_index].get_images(full=True)
        if not images:
            raise RuntimeError(f'no image found on magazine.pdf page {pdf_page_index + 1}')
        image_info = doc.extract_image(images[0][0])
        img = Image.open(BytesIO(image_info['image'])).convert('RGB')
        img.save(out_path, quality=95)

# The high-resolution source scan and the public OCR PDF use different crops.
# Most pages match one-to-one, but the lower-quality OCR extraction sometimes
# splits or merges highlights. These pairings are only for fitting the
# high-res-to-OCR coordinate transform; reflected text is still selected from
# the OCR layer.
#
# Values are OCR-box indexes from analysis_outputs/visual_mask_report.txt.
# A tuple of indexes means use the envelope of those OCR boxes. A tuple of
# (index, y0_frac, y1_frac) means use a vertical slice of that OCR box.
MANUAL_OCR_MATCHES = {
    75: [0, 1, 2, 3, 4, 5, 6, 7],
    76: [0, 1, 2, 3, 4],
    # Page artifact filtering leaves only the two real page-77 highlights.
    77: [0, 1],
    # High-res box 2 spans two OCR components.
    78: [0, 1, (2, 3), 4],
    # Page artifact filtering removes the raw right-margin artifact on page 79.
    # OCR box 3 merged two high-res lines, so split it vertically for a stable fit.
    79: [0, 1, 2, (3, 0.00, 0.48), (3, 0.48, 1.00), 4, 5, 6, 7, 8],
    # Page 80 is not part of the primary reflected-pair hypothesis, but these
    # mappings avoid fitting against right-margin artifacts.
    80: [0, 1],
}


def upright_image(page_no):
    ensure_highres_sources()
    img = Image.open(SOURCE_PAGES[page_no]).convert('RGB')
    # magazine.pdf embeds these scans with page rotation 180.
    return img.rotate(180, expand=True)


def orange_boxes(page_no):
    img = upright_image(page_no)
    mask = masks_for_page(img)['orange']
    comps = connected_components(mask, min_area=150)
    boxes = merge_close_boxes(comps, y_gap=20, x_gap=34)
    filtered = []
    for box in boxes:
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        if width < 25 or height < 10:
            continue
        if width > img.width * 0.95 or height > img.height * 0.35:
            continue
        if y1 < 175 or x1 > img.width - 150:
            continue
        filtered.append(box)
    return filtered, img.size


def hflip_box(box, width, dx=0, dy=0):
    x1, y1, x2, y2 = box
    return (width - x2 + dx, y1 + dy, width - x1 + dx, y2 + dy)


def reflected_selection(source_page, target_page, dx=0, dy=0):
    boxes, source_size = orange_boxes(source_page)
    mapped_boxes, mapped_size = map_highres_boxes_to_ocr(source_page, boxes)
    target_img = Image.open(OCR_PAGES[target_page]).convert('RGB')
    doc = fitz.open(PDF)
    target_pdf_rect = doc[PDF_PAGE_INDEX[target_page]].rect
    results = []
    for idx, (box, mapped_box) in enumerate(zip(boxes, mapped_boxes), 1):
        reflected = hflip_box(mapped_box, mapped_size[0], dx=dx, dy=dy)
        rect = image_box_to_pdf_rect(reflected, target_img.size, target_pdf_rect)
        text = words_in_rect(doc, target_page, rect)
        chars = chars_in_rect(doc, target_page, rect)
        results.append((idx, box, reflected, text, chars))
    return results


def fit_axis_mapping(source_boxes, target_boxes):
    points_src = []
    points_dst = []
    for sbox, tbox in zip(source_boxes, target_boxes):
        sx1, sy1, sx2, sy2 = sbox
        tx1, ty1, tx2, ty2 = tbox
        points_src.extend([(sx1, sy1), (sx2, sy2), ((sx1 + sx2) / 2, (sy1 + sy2) / 2)])
        points_dst.extend([(tx1, ty1), (tx2, ty2), ((tx1 + tx2) / 2, (ty1 + ty2) / 2)])
    src = np.array(points_src, dtype=float)
    dst = np.array(points_dst, dtype=float)
    ax, bx = np.polyfit(src[:, 0], dst[:, 0], 1)
    ay, by = np.polyfit(src[:, 1], dst[:, 1], 1)
    return ax, bx, ay, by


def envelope(boxes):
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def vertical_slice(box, y0_frac, y1_frac):
    x1, y1, x2, y2 = box
    height = y2 - y1
    return (
        x1,
        int(round(y1 + height * y0_frac)),
        x2,
        int(round(y1 + height * y1_frac)),
    )


def target_box_from_spec(ocr_boxes, spec):
    if isinstance(spec, int):
        return ocr_boxes[spec]
    if len(spec) == 2:
        return envelope([ocr_boxes[idx] for idx in spec])
    if len(spec) == 3:
        idx, y0_frac, y1_frac = spec
        return vertical_slice(ocr_boxes[idx], y0_frac, y1_frac)
    raise ValueError(f'unsupported OCR match spec: {spec!r}')


def map_box(box, mapping):
    ax, bx, ay, by = mapping
    x1, y1, x2, y2 = box
    mx1 = ax * x1 + bx
    mx2 = ax * x2 + bx
    my1 = ay * y1 + by
    my2 = ay * y2 + by
    return (int(round(min(mx1, mx2))), int(round(min(my1, my2))), int(round(max(mx1, mx2))), int(round(max(my1, my2))))


def map_highres_boxes_to_ocr(page_no, highres_boxes):
    ocr_boxes, ocr_size = ocr_orange_boxes(page_no)
    specs = MANUAL_OCR_MATCHES.get(page_no)
    if specs and len(specs) <= len(highres_boxes):
        target_boxes = [target_box_from_spec(ocr_boxes, spec) for spec in specs]
        fit_source_boxes = highres_boxes[:len(target_boxes)]
    else:
        # Fallback only; explicit mappings above handle all puzzle pages.
        n = min(len(highres_boxes), len(ocr_boxes))
        fit_source_boxes = highres_boxes[:n]
        target_boxes = ocr_boxes[:n]
    mapping = fit_axis_mapping(fit_source_boxes, target_boxes)
    mapped = list(target_boxes)
    if len(highres_boxes) > len(mapped):
        mapped.extend(map_box(box, mapping) for box in highres_boxes[len(mapped):])
    return mapped, ocr_size


def fit_residuals(source_boxes, target_boxes, mapping):
    residuals = []
    for idx, (source, target) in enumerate(zip(source_boxes, target_boxes), 1):
        mapped = map_box(source, mapping)
        cx_m = (mapped[0] + mapped[2]) / 2
        cy_m = (mapped[1] + mapped[3]) / 2
        cx_t = (target[0] + target[2]) / 2
        cy_t = (target[1] + target[3]) / 2
        residuals.append((idx, round(cx_m - cx_t, 1), round(cy_m - cy_t, 1), mapped, target))
    return residuals


def fit_mapping_for_page(page_no, highres_boxes):
    ocr_boxes, _ = ocr_orange_boxes(page_no)
    specs = MANUAL_OCR_MATCHES.get(page_no, [])
    if specs and len(specs) <= len(highres_boxes):
        target_boxes = [target_box_from_spec(ocr_boxes, spec) for spec in specs]
        fit_source_boxes = highres_boxes[:len(target_boxes)]
    else:
        n = min(len(highres_boxes), len(ocr_boxes))
        fit_source_boxes = highres_boxes[:n]
        target_boxes = ocr_boxes[:n]
    mapping = fit_axis_mapping(fit_source_boxes, target_boxes)
    return mapping, fit_source_boxes, target_boxes


def write_box_images():
    report = []
    for page in SOURCE_PAGES:
        img = upright_image(page)
        boxes, _ = orange_boxes(page)
        mapping, fit_source_boxes, target_boxes = fit_mapping_for_page(page, boxes)
        mapped, _ = map_highres_boxes_to_ocr(page, boxes)
        boxed = draw_boxes(img, boxes, 'red')
        boxed.save(OUT / f'page_{page}_orange_boxes.png')
        report.append(f'page {page} orange: {len(boxes)} boxes')
        report.append(
            '  mapping '
            f'x={mapping[0]:.6f}*x+{mapping[1]:.2f} '
            f'y={mapping[2]:.6f}*y+{mapping[3]:.2f}'
        )
        for idx, dx, dy, mapped_fit, target in fit_residuals(fit_source_boxes, target_boxes, mapping):
            report.append(f'  fit {idx:02d} residual center dx={dx:+.1f} dy={dy:+.1f} mapped={mapped_fit} target={target}')
        for idx, box in enumerate(boxes, 1):
            report.append(f'  {idx:02d} highres={box} mapped_ocr={mapped[idx - 1]}')
    (OUT / 'highres_visual_mask_report.txt').write_text('\n'.join(report) + '\n')


def main():
    write_box_images()
    lines = []
    for source, target in [(79, 75), (75, 79), (78, 76), (76, 78), (78, 75), (79, 76)]:
        lines.append(f'\nSOURCE {source} highres orange reflected onto TARGET {target}')
        joined = []
        for idx, box, reflected, text, chars in reflected_selection(source, target):
            lines.append(f'{idx:02d} src={box} reflected={reflected} -> {text}')
            lines.append(f'   chars -> {chars}')
            if text:
                joined.append(text)
        lines.append('JOINED: ' + ' / '.join(joined))
    report = '\n'.join(lines) + '\n'
    (OUT / 'highres_reflected_mask_text_report.txt').write_text(report)
    print(report)


if __name__ == '__main__':
    main()
