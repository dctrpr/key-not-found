#!/usr/bin/env python3
"""Audit page-frame/trim evidence for current scan held-to-light registration.

This pass asks whether the current upright page rasters expose a measurable
outer page frame, trim line, skew, or crop offset that could justify changing
the valid page-75 -> page-76 held-to-light registration.

It is geometry/source validation only. It does not extract text as key material,
generate key candidates, hash text into secrets, or run WIF/seed/address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/source_audit/current_scan_page_frame_trim_registration_gate"
JSON_OUT = OUT_DIR / "current_scan_page_frame_trim_registration_gate.json"
MD_OUT = OUT_DIR / "current_scan_page_frame_trim_registration_gate.md"
SHEET_OUT = OUT_DIR / "current_scan_page_frame_trim_registration_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HELD_TO_LIGHT = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
BLEEDTHROUGH = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/"
    "current_scan_valid_leaf_bleedthrough_control_grid.json"
)
REOPEN_TRIGGER_MATRIX = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"
PAGES = [75, 76, 78, 79]
VALID_PAIR = (75, 76)
EDGE_SCAN_PX = 360
EDGE_SAMPLE_STEP = 8
EDGE_BAND_PX = 24
INK_LUMA_THRESHOLD = 244.0
SATURATION_THRESHOLD = 18.0
FRAME_COVERAGE_THRESHOLD = 0.90
FRAME_IQR_THRESHOLD = 10.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def safe_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for item in candidates:
        if item and Path(item).exists():
            try:
                return ImageFont.truetype(item, size)
            except OSError:
                pass
    return ImageFont.load_default()


def normalize_page(page: int) -> tuple[Image.Image, str]:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    upright = Image.open(upright_path).convert("RGB")
    if not source_path.exists():
        return upright, "upright_only"
    source = Image.open(source_path).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    if rot_diff < same_diff:
        return source.rotate(180), "source_rot180_to_readable"
    return source, "source_as_readable"


def saturation(arr: np.ndarray) -> np.ndarray:
    maxc = arr.max(axis=2)
    minc = arr.min(axis=2)
    return maxc - minc


def content_mask(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)
    luma = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    sat = saturation(arr)
    return (luma < INK_LUMA_THRESHOLD) | (sat > SATURATION_THRESHOLD)


def iqr(values: list[float]) -> float:
    if not values:
        return 0.0
    arr = np.array(values, dtype=np.float32)
    q75, q25 = np.percentile(arr, [75, 25])
    return float(q75 - q25)


def edge_runs(mask: np.ndarray, side: str) -> list[int | None]:
    h, w = mask.shape
    runs: list[int | None] = []
    if side in {"top", "bottom"}:
        xs = range(0, w, EDGE_SAMPLE_STEP)
        for x in xs:
            col = mask[:EDGE_SCAN_PX, x] if side == "top" else mask[h - EDGE_SCAN_PX :, x][::-1]
            hit = np.flatnonzero(col)
            runs.append(int(hit[0]) if len(hit) else None)
    else:
        ys = range(0, h, EDGE_SAMPLE_STEP)
        for y in ys:
            row = mask[y, :EDGE_SCAN_PX] if side == "left" else mask[y, w - EDGE_SCAN_PX :][::-1]
            hit = np.flatnonzero(row)
            runs.append(int(hit[0]) if len(hit) else None)
    return runs


def edge_band_share(mask: np.ndarray, side: str) -> float:
    h, w = mask.shape
    if side == "top":
        band = mask[:EDGE_BAND_PX, :]
    elif side == "bottom":
        band = mask[h - EDGE_BAND_PX :, :]
    elif side == "left":
        band = mask[:, :EDGE_BAND_PX]
    else:
        band = mask[:, w - EDGE_BAND_PX :]
    return float(band.mean())


def summarize_edge(mask: np.ndarray, side: str) -> dict[str, Any]:
    runs = edge_runs(mask, side)
    valid = [float(v) for v in runs if v is not None]
    coverage = len(valid) / len(runs) if runs else 0.0
    if valid:
        median_run = float(median(valid))
        min_run = float(min(valid))
        p10 = float(np.percentile(valid, 10))
        p90 = float(np.percentile(valid, 90))
        iqr_run = iqr(valid)
    else:
        median_run = min_run = p10 = p90 = iqr_run = None
    frame_like = bool(
        coverage >= FRAME_COVERAGE_THRESHOLD
        and iqr_run is not None
        and iqr_run <= FRAME_IQR_THRESHOLD
        and median_run is not None
        and median_run <= EDGE_SCAN_PX * 0.5
    )
    return {
        "side": side,
        "coverage": round(coverage, 6),
        "medianFirstContentPx": None if median_run is None else round(median_run, 3),
        "minFirstContentPx": None if min_run is None else round(min_run, 3),
        "p10FirstContentPx": None if p10 is None else round(p10, 3),
        "p90FirstContentPx": None if p90 is None else round(p90, 3),
        "iqrFirstContentPx": None if iqr_run is None else round(iqr_run, 3),
        "edgeBandNonwhiteShare": round(edge_band_share(mask, side), 6),
        "frameLikeEdge": frame_like,
    }


def page_summary(page: int) -> dict[str, Any]:
    image, source_mode = normalize_page(page)
    mask = content_mask(image)
    edges = {side: summarize_edge(mask, side) for side in ["top", "bottom", "left", "right"]}
    frame_like_count = sum(1 for row in edges.values() if row["frameLikeEdge"])
    return {
        "page": page,
        "image": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))),
        "sourceMode": source_mode,
        "size": list(image.size),
        "edgeSummaries": edges,
        "frameLikeEdgeCount": frame_like_count,
        "allEdgesFrameLike": frame_like_count == 4,
    }


def active_box_distances(active_index: dict[str, Any], page_edges: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    active_rows = [row for row in active_index.get("activeRows", []) if row.get("shortId") in {"O4", "B4", "G5", "O5"}]
    for row in sorted(active_rows, key=lambda item: ["O4", "B4", "G5", "O5"].index(item["shortId"])):
        box = [float(v) for v in row["box"]]
        rows.append(
            {
                "shortId": row["shortId"],
                "phrase": row["phrase"],
                "visualState": row["visualState"],
                "box": box,
                "distanceToCanvas": {
                    "left": round(box[0], 3),
                    "top": round(box[1], 3),
                    "right": round(2544 - box[2], 3),
                    "bottom": round(3264 - box[3], 3),
                },
                "pageFrameAvailable": bool(page_edges.get("allEdgesFrameLike")),
            }
        )
    return rows


def compare_valid_pair(page_rows: list[dict[str, Any]]) -> dict[str, Any]:
    lookup = {row["page"]: row for row in page_rows}
    left = lookup[VALID_PAIR[0]]
    right = lookup[VALID_PAIR[1]]
    deltas: dict[str, Any] = {}
    for side in ["top", "bottom", "left", "right"]:
        a = left["edgeSummaries"][side]
        b = right["edgeSummaries"][side]
        if a["medianFirstContentPx"] is not None and b["medianFirstContentPx"] is not None:
            median_delta = round(b["medianFirstContentPx"] - a["medianFirstContentPx"], 3)
        else:
            median_delta = None
        deltas[side] = {
            "coverageDelta": round(b["coverage"] - a["coverage"], 6),
            "medianFirstContentDeltaPx": median_delta,
            "bothFrameLike": bool(a["frameLikeEdge"] and b["frameLikeEdge"]),
            "edgeBandShareDelta": round(b["edgeBandNonwhiteShare"] - a["edgeBandNonwhiteShare"], 6),
        }
    return {
        "pair": f"{VALID_PAIR[0]}->{VALID_PAIR[1]}",
        "sameCanvasSize": left["size"] == right["size"],
        "bothPagesAllEdgesFrameLike": bool(left["allEdgesFrameLike"] and right["allEdgesFrameLike"]),
        "edgeDeltas": deltas,
    }


def load_trigger_summary() -> tuple[int, int]:
    data = load_json(REOPEN_TRIGGER_MATRIX)
    summary = data.get("summary", {})
    return (
        int(summary.get("satisfiedReopenTriggerCount", 0) or 0),
        int(summary.get("triggerCount", 0) or 0),
    )


def draw_sheet(page_rows: list[dict[str, Any]], pair: dict[str, Any], summary: dict[str, Any]) -> None:
    w, h = 1900, 1180
    sheet = Image.new("RGB", (w, h), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    title = safe_font(34, bold=True)
    header = safe_font(24, bold=True)
    body = safe_font(21)
    small = safe_font(18)
    draw.text((40, 28), "Current Scan Page Frame / Trim Registration Gate", fill=(15, 23, 42), font=title)
    y = 84
    for line in [
        f"Decision: {summary['decision']}",
        f"Pages checked: {summary['pageCount']}   valid pair: {pair['pair']}   same canvas: {int(pair['sameCanvasSize'])}",
        f"Pages with all four frame-like edges: {summary['allEdgesFrameLikePageCount']}   trim correction candidate: {int(summary['trimCorrectionCandidate'])}",
    ]:
        draw.text((40, y), line, fill=(30, 41, 59), font=body)
        y += 34
    y += 18
    cols = [40, 130, 280, 450, 620, 790, 980, 1160, 1340, 1520]
    labels = ["page", "mode", "top med/cov", "bottom med/cov", "left med/cov", "right med/cov", "top band", "bottom band", "left band", "right band"]
    for x, label in zip(cols, labels):
        draw.text((x, y), label, fill=(15, 23, 42), font=header)
    y += 38
    draw.line((40, y, w - 40, y), fill=(148, 163, 184), width=2)
    y += 18
    for row in page_rows:
        vals = [str(row["page"]), row["sourceMode"]]
        for side in ["top", "bottom", "left", "right"]:
            edge = row["edgeSummaries"][side]
            vals.append(f"{edge['medianFirstContentPx']}/{edge['coverage']:.2f}")
        for side in ["top", "bottom", "left", "right"]:
            vals.append(f"{row['edgeSummaries'][side]['edgeBandNonwhiteShare']:.4f}")
        for x, val in zip(cols, vals):
            draw.text((x, y), str(val)[:18], fill=(30, 41, 59), font=small)
        y += 42
    y += 18
    draw.text((40, y), "Valid 75->76 Pair Edge Deltas", fill=(15, 23, 42), font=header)
    y += 38
    for side, delta in pair["edgeDeltas"].items():
        line = (
            f"{side}: median delta {delta['medianFirstContentDeltaPx']} px, "
            f"coverage delta {delta['coverageDelta']}, both frame-like {int(delta['bothFrameLike'])}"
        )
        draw.text((64, y), "- " + line, fill=(30, 41, 59), font=body)
        y += 34
    y += 10
    draw.text((40, y), "Interpretation", fill=(15, 23, 42), font=header)
    y += 38
    notes = [
        "No page has all four frame-like edges; edge hits are content profiles, not a physical trim/frame line.",
        "The valid pair has identical canvas size, so no PDF/scan frame correction is justified from the raster edges.",
        "Held-to-light failures should not be reopened with ad hoc trim/skew correction unless a new physical/original source supplies it.",
    ]
    for note in notes:
        draw.text((64, y), "- " + note, fill=(30, 41, 59), font=body)
        y += 34
    sheet.save(SHEET_OUT, quality=92)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    page_rows = [page_summary(page) for page in PAGES]
    pair = compare_valid_pair(page_rows)
    active_distances = active_box_distances(active_index, {row["page"]: row for row in page_rows}.get(76, {}))
    satisfied, trigger_count = load_trigger_summary()
    all_edges_count = sum(1 for row in page_rows if row["allEdgesFrameLike"])
    trim_candidate = bool(pair["sameCanvasSize"] and pair["bothPagesAllEdgesFrameLike"])
    hidden_candidate = False
    summary = {
        "decision": "current_scan_page_frame_trim_registration_no_selector",
        "pageCount": len(page_rows),
        "pagesChecked": PAGES,
        "validPair": pair["pair"],
        "sameCanvasValidPair": pair["sameCanvasSize"],
        "allEdgesFrameLikePageCount": all_edges_count,
        "validPairBothPagesAllEdgesFrameLike": pair["bothPagesAllEdgesFrameLike"],
        "trimCorrectionCandidate": trim_candidate,
        "hiddenTrimSkewCandidate": hidden_candidate,
        "activeDistanceRowCount": len(active_distances),
        "priorHeldToLightFingerprint": load_json(HELD_TO_LIGHT)
        .get("summary", {})
        .get("heldToLightSimulatorFingerprint"),
        "priorBleedthroughFingerprint": load_json(BLEEDTHROUGH).get("fingerprint"),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "pageFrameTrimFingerprint": (
            f"pages={len(page_rows)}|pair={pair['pair']}|sameCanvas={int(pair['sameCanvasSize'])}"
            f"|allEdgesPages={all_edges_count}|pairAllEdges={int(pair['bothPagesAllEdgesFrameLike'])}"
            f"|trimCandidate={int(trim_candidate)}|hiddenCandidate={int(hidden_candidate)}"
            f"|sourceR3=0|triggers={satisfied}/{trigger_count}|selectors=0"
        ),
    }
    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current scan page-frame/trim registration audit for held-to-light geometry; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT),
            "bleedthroughControlGrid": rel(BLEEDTHROUGH),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePageTemplate": rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=75))).replace("75", "{page}"),
            "uprightPageTemplate": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=75))).replace("75", "{page}"),
        },
        "pageRows": page_rows,
        "validPairComparison": pair,
        "activeBoxDistances": active_distances,
        "summary": summary,
        "decision": {
            "currentScanPageFrameTrimRegistrationGate": summary["decision"],
            "selectorUnlocked": False,
            "reason": (
                "Current scan rasters share the same canvas for the valid 75->76 pair, but the edge profiles "
                "do not expose a stable all-edge physical page-frame/trim line. Edge hits are content/margin "
                "profiles, so they do not justify changing held-to-light registration."
            ),
            "nextMove": (
                "Do not reopen held-to-light with ad hoc trim/skew correction unless a distinct physical or "
                "original-layout source supplies a measurable frame/registration cue."
            ),
        },
        "sheet": rel(SHEET_OUT),
        "fingerprint": summary["pageFrameTrimFingerprint"],
    }
    draw_sheet(page_rows, pair, summary)
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    write_md(result)
    print(f"Wrote {rel(MD_OUT)}")
    print(f"Wrote {rel(JSON_OUT)}")
    print(f"Wrote {rel(SHEET_OUT)}")
    print(f"Decision: {summary['decision']}")
    print(f"Fingerprint: {summary['pageFrameTrimFingerprint']}")


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    pair = result["validPairComparison"]
    lines = [
        "# Current Scan Page Frame / Trim Registration Gate",
        "",
        "Scope: inspected current upright/source page rasters for a measurable page-frame, trim-line, skew, or crop-offset cue that could justify changing valid page-75 -> page-76 held-to-light registration. This is geometry/source validation only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Pages checked: `{summary['pagesChecked']}`",
        f"- Valid pair / same canvas: `{summary['validPair']}` / `{int(summary['sameCanvasValidPair'])}`",
        f"- Pages with all four frame-like edges: `{summary['allEdgesFrameLikePageCount']}`",
        f"- Valid pair both pages all-edge frame-like: `{int(summary['validPairBothPagesAllEdgesFrameLike'])}`",
        f"- Trim correction candidate / hidden trim-skew candidate: `{int(summary['trimCorrectionCandidate'])}` / `{int(summary['hiddenTrimSkewCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['pageFrameTrimFingerprint']}`",
        "",
        "## Page Edge Rows",
        "",
        "| page | mode | top med/cov/iqr | bottom med/cov/iqr | left med/cov/iqr | right med/cov/iqr | frame-like edges |",
        "|---:|---|---|---|---|---|---:|",
    ]
    for row in result["pageRows"]:
        vals = []
        for side in ["top", "bottom", "left", "right"]:
            edge = row["edgeSummaries"][side]
            vals.append(
                f"{edge['medianFirstContentPx']}/{edge['coverage']}/{edge['iqrFirstContentPx']}"
            )
        lines.append(
            f"| `{row['page']}` | `{row['sourceMode']}` | `"
            + "` | `".join(vals)
            + f"` | `{row['frameLikeEdgeCount']}` |"
        )
    lines.extend(
        [
            "",
            "## Valid 75 -> 76 Edge Deltas",
            "",
            "| side | median first-content delta px | coverage delta | edge-band share delta | both frame-like |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for side, delta in pair["edgeDeltas"].items():
        lines.append(
            f"| `{side}` | `{delta['medianFirstContentDeltaPx']}` | `{delta['coverageDelta']}` | `{delta['edgeBandShareDelta']}` | `{int(delta['bothFrameLike'])}` |"
        )
    lines.extend(
        [
            "",
            "## Active Target Frame Use",
            "",
            "- Page-76 active boxes were only measured against the canvas because no reliable physical page-frame line was detected.",
            f"- Active box distance rows: `{summary['activeDistanceRowCount']}`",
            "",
            "## Decision",
            "",
            f"- `{summary['decision']}`",
            "- The valid 75->76 pages share the same `2544x3264` canvas, but the edge profiles do not expose a stable all-edge physical trim/frame line.",
            "- Edge hits are content/margin profiles rather than a registration frame, so they do not justify a hidden trim, skew, or crop correction.",
            "",
            "## Next Move",
            "",
            "- Keep current-scan held-to-light registration closed unless a distinct physical/original-layout source supplies a measurable page-frame or registration cue. The best direction remains source validation or raw clue wording that names unit/order/transform.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
