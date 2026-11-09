#!/usr/bin/env python3
"""Check whether the current scan already contains physical bleed-through.

The earlier light-table passes synthesize a held-to-light overlay. This bounded
gate asks a different source-quality question: do the current page images
themselves show target-page darkening that correlates with the mirrored back
page in low-ink/background regions?

No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address
checks, BIP39 checks, or brute force are run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_physical_bleedthrough_correlation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_physical_bleedthrough_correlation_gate.json"
OUT_MD = OUT / "current_scan_physical_bleedthrough_correlation_gate.md"
OUT_SHEET = OUT / "current_scan_physical_bleedthrough_correlation_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PAGES = [75, 76, 77, 78, 79, 80]
VALID_LEAF_PAIRS = [(75, 76), (77, 78), (79, 80)]
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
SOURCE_SIGNAL_LUMA_MAX = 185.0
TARGET_BACKGROUND_LUMA_MIN = 190.0
MIN_SOURCE_SIGNAL_PIXELS = 200


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def normalize_page(page: int) -> Image.Image:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    if source_path.exists() and upright_path.exists():
        source = Image.open(source_path).convert("RGB")
        upright = Image.open(upright_path).convert("RGB")
        sample_size = (318, 408)
        source_sample = source.resize(sample_size)
        upright_sample = upright.resize(sample_size)
        same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
        rot_diff = sum(
            ImageStat.Stat(
                ImageChops.difference(source_sample.rotate(180), upright_sample)
            ).mean
        )
        return source.rotate(180) if rot_diff < same_diff else source
    return Image.open(upright_path).convert("RGB")


def luma_from_image(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def active_boxes(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") in TARGET_ORDER:
            rows.append(
                {
                    "id": row.get("id"),
                    "shortId": row["shortId"],
                    "phrase": row.get("phrase", ""),
                    "pageLine": int(row["pageLine"]),
                    "box": [float(v) for v in row["box"]],
                }
            )
    rows.sort(key=lambda item: TARGET_ORDER.index(item["shortId"]))
    return rows


def envelope_box(rows: list[dict[str, Any]], pad: float, width: int, height: int) -> list[float]:
    return [
        max(0.0, min(row["box"][0] for row in rows) - pad),
        max(0.0, min(row["box"][1] for row in rows) - pad),
        min(float(width), max(row["box"][2] for row in rows) + pad),
        min(float(height), max(row["box"][3] for row in rows) + pad),
    ]


def box_mask(shape: tuple[int, int], box: list[float]) -> np.ndarray:
    h, w = shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    mask = np.zeros((h, w), dtype=bool)
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = True
    return mask


def corrcoef_safe(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or b.size < 2:
        return 0.0
    a_std = float(a.std())
    b_std = float(b.std())
    if a_std == 0.0 or b_std == 0.0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def metric_for_region(
    source_luma: np.ndarray,
    target_luma: np.ndarray,
    region: np.ndarray | None = None,
) -> dict[str, Any]:
    source_signal = source_luma <= SOURCE_SIGNAL_LUMA_MAX
    target_background = target_luma >= TARGET_BACKGROUND_LUMA_MIN
    usable = target_background if region is None else np.logical_and(target_background, region)
    signal = np.logical_and(source_signal, usable)
    nonsignal = np.logical_and(~source_signal, usable)
    darkness = 255.0 - target_luma

    signal_count = int(signal.sum())
    nonsignal_count = int(nonsignal.sum())
    usable_count = int(usable.sum())
    if signal_count < MIN_SOURCE_SIGNAL_PIXELS or nonsignal_count < MIN_SOURCE_SIGNAL_PIXELS:
        return {
            "usablePixelCount": usable_count,
            "sourceSignalPixelCount": signal_count,
            "nonSourceSignalPixelCount": nonsignal_count,
            "sourceSignalFraction": round(signal_count / max(1, usable_count), 8),
            "meanDarknessAtSourceSignal": None,
            "meanDarknessAtNonSourceSignal": None,
            "darknessDelta": None,
            "binarySourceDarknessCorrelation": None,
        }

    source_darkness = darkness[signal]
    non_source_darkness = darkness[nonsignal]
    source_binary = source_signal[usable].astype(np.float32)
    usable_darkness = darkness[usable].astype(np.float32)
    delta = float(source_darkness.mean() - non_source_darkness.mean())
    return {
        "usablePixelCount": usable_count,
        "sourceSignalPixelCount": signal_count,
        "nonSourceSignalPixelCount": nonsignal_count,
        "sourceSignalFraction": round(signal_count / max(1, usable_count), 8),
        "meanDarknessAtSourceSignal": round(float(source_darkness.mean()), 6),
        "meanDarknessAtNonSourceSignal": round(float(non_source_darkness.mean()), 6),
        "darknessDelta": round(delta, 6),
        "binarySourceDarknessCorrelation": round(
            corrcoef_safe(source_binary, usable_darkness), 8
        ),
    }


def percentile(values: list[float], pct: float) -> float:
    clean = [value for value in values if value is not None]
    if not clean:
        return 0.0
    return float(np.percentile(clean, pct))


def row_delta(row: dict[str, Any]) -> float | None:
    value = row.get("darknessDelta")
    return None if value is None else float(value)


def build_pair_rows(page_luma: dict[int, np.ndarray]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_page in PAGES:
        mirrored_source = np.fliplr(page_luma[source_page])
        for target_page in PAGES:
            if source_page == target_page:
                continue
            metrics = metric_for_region(mirrored_source, page_luma[target_page])
            rows.append(
                {
                    "sourcePage": source_page,
                    "targetPage": target_page,
                    "pair": f"{source_page}->{target_page}",
                    "validLeafPair": (source_page, target_page) in VALID_LEAF_PAIRS,
                    **metrics,
                }
            )
    return rows


def annotate_pair_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        controls = [
            row_delta(other)
            for other in rows
            if other["targetPage"] == row["targetPage"] and not other["validLeafPair"]
        ]
        p95 = percentile([value for value in controls if value is not None], 95)
        delta = row_delta(row)
        row["targetInvalidControlP95Delta"] = round(p95, 6)
        row["aboveTargetInvalidP95"] = bool(delta is not None and delta > p95)


def build_region_rows(
    page_luma: dict[int, np.ndarray],
    active: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source75 = np.fliplr(page_luma[75])
    target76 = page_luma[76]
    h, w = target76.shape
    active_rows: list[dict[str, Any]] = []
    for active_row in active:
        mask = box_mask((h, w), active_row["box"])
        valid_metrics = metric_for_region(source75, target76, mask)
        control_deltas: list[float] = []
        control_rows = []
        for source_page in [page for page in PAGES if page != 75 and page != 76]:
            control_metrics = metric_for_region(np.fliplr(page_luma[source_page]), target76, mask)
            control_rows.append({"sourcePage": source_page, **control_metrics})
            delta = control_metrics.get("darknessDelta")
            if delta is not None:
                control_deltas.append(float(delta))
        p95 = percentile(control_deltas, 95)
        delta = valid_metrics.get("darknessDelta")
        active_rows.append(
            {
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "box": active_row["box"],
                **valid_metrics,
                "invalidSourceControlP95Delta": round(p95, 6),
                "aboveInvalidSourceP95": bool(delta is not None and float(delta) > p95),
                "controlRows": control_rows,
            }
        )

    envelope = envelope_box(active, 48.0, w, h)
    envelope_mask = box_mask((h, w), envelope)
    region_rows: list[dict[str, Any]] = []
    for source_page, target_page, label, mask in [
        (75, 76, "page76_active_envelope_padded48", envelope_mask),
        (75, 76, "page76_full_page", None),
    ]:
        metrics = metric_for_region(np.fliplr(page_luma[source_page]), page_luma[target_page], mask)
        region_rows.append(
            {
                "region": label,
                "sourcePage": source_page,
                "targetPage": target_page,
                "box": envelope if mask is not None else None,
                **metrics,
            }
        )
    return active_rows, region_rows


def make_sheet(images: dict[int, Image.Image], active: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    target = images[76].resize((636, 816))
    source = ImageOps.mirror(images[75]).resize(target.size)
    source_luma = luma_from_image(source)
    overlay = target.convert("RGBA")
    red = Image.new("RGBA", target.size, (255, 0, 0, 0))
    red_arr = np.asarray(red).copy()
    red_arr[source_luma <= SOURCE_SIGNAL_LUMA_MAX, 3] = 90
    overlay = Image.alpha_composite(overlay, Image.fromarray(red_arr, "RGBA"))
    draw = ImageDraw.Draw(overlay)
    scale_x = target.size[0] / images[76].size[0]
    scale_y = target.size[1] / images[76].size[1]
    colors = {"O4": "#f97316", "B4": "#111111", "G5": "#2563eb", "O5": "#f97316"}
    for row in active:
        x0, y0, x1, y1 = row["box"]
        box = [x0 * scale_x, y0 * scale_y, x1 * scale_x, y1 * scale_y]
        draw.rectangle(box, outline=colors.get(row["shortId"], "red"), width=3)
        draw.text((box[0], max(0, box[1] - 18)), row["shortId"], fill=colors.get(row["shortId"], "red"), font=font(14))

    table_w = 760
    sheet = Image.new("RGB", (overlay.width + table_w, overlay.height), "white")
    sheet.paste(overlay.convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(sheet)
    x = overlay.width + 20
    y = 20
    draw.text((x, y), "Physical bleed-through correlation", fill="black", font=font(22))
    y += 34
    lines = [
        f"Valid leaf pairs above target-control p95: {summary['validPairsAboveTargetInvalidP95Count']}/{summary['validLeafPairCount']}",
        f"Page 75->76 delta / p95: {summary['page76ValidDarknessDelta']} / {summary['page76InvalidControlP95Delta']}",
        f"Page 76 active boxes above invalid p95: {summary['page76ActiveBoxesAboveInvalidP95Count']}/4",
        f"All-four active above invalid p95: {int(summary['page76AllFourActiveBoxesAboveInvalidP95'])}",
        f"Hidden bleed-through candidate: {int(summary['hiddenPhysicalBleedthroughCandidate'])}",
        f"Source-backed R3 / triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
    ]
    for line in lines:
        draw.text((x, y), line, fill="black", font=font(16))
        y += 26
    y += 12
    draw.text((x, y), "Active target rows", fill="black", font=font(18))
    y += 28
    for row in summary["activeRowDigest"]:
        line = (
            f"{row['target']}: delta={row['darknessDelta']} "
            f"p95={row['invalidSourceControlP95Delta']} "
            f"sigPix={row['sourceSignalPixelCount']} "
            f"above={int(row['aboveInvalidSourceP95'])}"
        )
        draw.text((x, y), line, fill="black", font=font(14))
        y += 22
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_summary = reopen.get("summary", {})

    images = {page: normalize_page(page) for page in PAGES}
    page_luma = {page: luma_from_image(image) for page, image in images.items()}
    active = active_boxes(active_index)
    pair_rows = build_pair_rows(page_luma)
    annotate_pair_rows(pair_rows)
    active_rows, region_rows = build_region_rows(page_luma, active)

    valid_rows = [row for row in pair_rows if row["validLeafPair"]]
    control_rows = [row for row in pair_rows if not row["validLeafPair"]]
    page76_valid = next(row for row in pair_rows if row["sourcePage"] == 75 and row["targetPage"] == 76)
    page76_invalid_p95 = page76_valid["targetInvalidControlP95Delta"]
    active_above = sum(1 for row in active_rows if row["aboveInvalidSourceP95"])
    active_enough_signal = sum(
        1 for row in active_rows if row["sourceSignalPixelCount"] >= MIN_SOURCE_SIGNAL_PIXELS
    )
    hidden_candidate = (
        page76_valid["aboveTargetInvalidP95"]
        and active_above == len(active_rows)
        and active_enough_signal == len(active_rows)
    )
    valid_above_count = sum(1 for row in valid_rows if row["aboveTargetInvalidP95"])
    max_valid_delta = max((row_delta(row) or 0.0 for row in valid_rows), default=0.0)
    max_control_delta = max((row_delta(row) or 0.0 for row in control_rows), default=0.0)
    median_valid_delta = median([row_delta(row) or 0.0 for row in valid_rows])
    median_control_delta = median([row_delta(row) or 0.0 for row in control_rows])
    active_digest = [
        {
            "target": row["target"],
            "darknessDelta": row["darknessDelta"],
            "invalidSourceControlP95Delta": row["invalidSourceControlP95Delta"],
            "sourceSignalPixelCount": row["sourceSignalPixelCount"],
            "aboveInvalidSourceP95": row["aboveInvalidSourceP95"],
        }
        for row in active_rows
    ]
    fingerprint = (
        f"pairs={len(pair_rows)}|valid={len(valid_rows)}|controls={len(control_rows)}"
        f"|validAboveP95={valid_above_count}|page76Delta={page76_valid['darknessDelta']}"
        f"|page76P95={page76_invalid_p95}|activeAbove={active_above}/4"
        f"|activeEnoughSignal={active_enough_signal}/4|validMedian={median_valid_delta:.4f}"
        f"|controlMedian={median_control_delta:.4f}|validMax={max_valid_delta:.4f}"
        f"|controlMax={max_control_delta:.4f}|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger_summary.get('sourceBackedR3BridgeHitCount', 0)}"
        f"|triggers={trigger_summary.get('satisfiedTriggerCount', 0)}/{trigger_summary.get('triggerCount', 0)}"
        "|selectors=0"
    )
    summary = {
        "validLeafPairCount": len(valid_rows),
        "invalidControlPairCount": len(control_rows),
        "validPairsAboveTargetInvalidP95Count": valid_above_count,
        "page76ValidDarknessDelta": page76_valid["darknessDelta"],
        "page76InvalidControlP95Delta": page76_invalid_p95,
        "page76ValidAboveInvalidP95": page76_valid["aboveTargetInvalidP95"],
        "page76ActiveBoxesAboveInvalidP95Count": active_above,
        "page76ActiveBoxesWithEnoughSourceSignalCount": active_enough_signal,
        "page76AllFourActiveBoxesAboveInvalidP95": active_above == len(active_rows),
        "medianValidDarknessDelta": round(float(median_valid_delta), 6),
        "medianInvalidControlDarknessDelta": round(float(median_control_delta), 6),
        "maxValidDarknessDelta": round(float(max_valid_delta), 6),
        "maxInvalidControlDarknessDelta": round(float(max_control_delta), 6),
        "hiddenPhysicalBleedthroughCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": trigger_summary.get("sourceBackedR3BridgeHitCount", 0),
        "satisfiedReopenTriggerCount": trigger_summary.get("satisfiedTriggerCount", 0),
        "triggerCount": trigger_summary.get("triggerCount", 0),
        "selectorUnlocked": False,
        "physicalBleedthroughCorrelationFingerprint": fingerprint,
        "activeRowDigest": active_digest,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current-scan physical bleed-through correlation gate; fixed valid leaf pairs "
            "against invalid controls; no extraction, key candidates, hashes, WIF/seed/address "
            "checks, BIP39 checks, or brute force"
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePageTemplate": rel(SOURCE_PAGE_TEMPLATE),
            "uprightPageTemplate": rel(UPRIGHT_PAGE_TEMPLATE),
        },
        "parameters": {
            "pages": PAGES,
            "validLeafPairs": VALID_LEAF_PAIRS,
            "sourceSignalLumaMax": SOURCE_SIGNAL_LUMA_MAX,
            "targetBackgroundLumaMin": TARGET_BACKGROUND_LUMA_MIN,
            "minSourceSignalPixels": MIN_SOURCE_SIGNAL_PIXELS,
        },
        "pairRows": pair_rows,
        "activeRows": active_rows,
        "regionRows": region_rows,
        "summary": summary,
        "decision": {
            "currentScanPhysicalBleedthroughCorrelationGate": "current_scan_physical_bleedthrough_correlation_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "The current scan does not show a page-76 physical bleed-through "
                "correlation that separates valid leaf pairs from invalid source-page controls "
                "or supplies all-four active-box support."
            ),
            "nextMove": (
                "Treat the current images as scanned/rendered page witnesses, not a physical "
                "translucency source. Reopen only with a true physical scan/photo or source clue "
                "naming unit/order/transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    make_sheet(images, active, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current Scan Physical Bleed-Through Correlation Gate",
        "",
        "Scope: tested whether the current scan/PDF-derived page images already contain real physical backside bleed-through. Mirrored source-page darkness was compared with target-page darkness in low-ink/background regions for fixed valid leaf pairs and invalid source-page controls. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Valid leaf pairs / invalid control pairs: `{len(valid_rows)}` / `{len(control_rows)}`",
        f"- Valid pairs above same-target invalid-control p95: `{valid_above_count}` / `{len(valid_rows)}`",
        f"- Page 75->76 darkness delta / invalid-control p95: `{page76_valid['darknessDelta']}` / `{page76_invalid_p95}`",
        f"- Page 76 active boxes above invalid-source p95: `{active_above}` / `{len(active_rows)}`",
        f"- Page 76 active boxes with enough source-signal pixels: `{active_enough_signal}` / `{len(active_rows)}`",
        f"- All-four active above invalid-source p95: `{int(active_above == len(active_rows))}`",
        f"- Median valid/control darkness delta: `{median_valid_delta:.6f}` / `{median_control_delta:.6f}`",
        f"- Max valid/control darkness delta: `{max_valid_delta:.6f}` / `{max_control_delta:.6f}`",
        f"- Hidden physical bleed-through candidate: `{int(hidden_candidate)}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Valid Pair Rows",
        "",
        "| pair | delta | invalid p95 | above p95 | source signal pixels | corr |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in valid_rows:
        lines.append(
            f"| `{row['pair']}` | `{row['darknessDelta']}` | `{row['targetInvalidControlP95Delta']}` | `{int(row['aboveTargetInvalidP95'])}` | `{row['sourceSignalPixelCount']}` | `{row['binarySourceDarknessCorrelation']}` |"
        )
    lines.extend(
        [
            "",
            "## Page 76 Active Rows",
            "",
            "| target | phrase | delta | invalid-source p95 | above p95 | source signal pixels | source signal fraction |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in active_rows:
        lines.append(
            f"| `{row['target']}` | `{row['phrase']}` | `{row['darknessDelta']}` | `{row['invalidSourceControlP95Delta']}` | `{int(row['aboveInvalidSourceP95'])}` | `{row['sourceSignalPixelCount']}` | `{row['sourceSignalFraction']}` |"
        )
    lines.extend(
        [
            "",
            "## Region Rows",
            "",
            "| region | delta | signal pixels | corr |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in region_rows:
        lines.append(
            f"| `{row['region']}` | `{row['darknessDelta']}` | `{row['sourceSignalPixelCount']}` | `{row['binarySourceDarknessCorrelation']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_physical_bleedthrough_correlation_no_selector`",
            "- The current page images do not behave like a physically translucent scan that makes page 75 visibly bleed into page 76 in a selective way.",
            "- Valid leaf-pair darkness deltas do not beat invalid source-page controls, and the page-76 active quartet does not have all-four active-box support.",
            "- This keeps current scan/PDF images in the witness/provenance bucket, not the extraction-source bucket.",
            "",
            "## Next Move",
            "",
            "- Continue only with true physical/original-layout source validation or raw clue wording that names the missing registration unit, reading order, or transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
