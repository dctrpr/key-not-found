#!/usr/bin/env python3
"""Corrected-topology page 77 -> page 76 light-table audit.

This pass tests the specific claim from the external next-experiments handoff:
the old topology may have swapped front/back leaves with facing spreads, making
page 77 the true physical back of page 76. It first compares old and proposed
leaf pairs with the existing paper-texture method, then runs a bounded
page-77 white-knockout -> page-76 light-table sweep against the locked
O4/B4/G5/O5 target boxes and nearby controls.

No key candidates, hashing, seed/WIF/address checks, BIP39 checks, address
generation, or brute force are performed.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_scan_only_held_to_light_adjudication as fixed_pass  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/corrected_topology_77_76_light_table"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "corrected_topology_77_76_light_table.json"
OUT_MD = OUT / "corrected_topology_77_76_light_table.md"
OUT_SHEET = OUT / "corrected_topology_77_76_light_table_sheet.jpg"

HANDOFF = Path("missing_rule_next_experiments.md")
TOPOLOGY = ROOT / "analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology.json"
PAPER_DUPEX_OLD = ROOT / "analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate/current_scan_paper_texture_duplex_gate.json"
ACTIVE_TARGETS = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
FRONTIER = ROOT / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json"

SOURCE_PAGE = 77
TARGET_PAGE = 76
OLD_ASSUMED_LEAVES = [(75, 76), (77, 78), (79, 80)]
PROPOSED_LEAVES = [(74, 75), (76, 77), (78, 79)]
PAIR_PAGES = list(range(73, 81))
TRANSFORMS = ["identity", "hmirror", "vmirror", "rot180"]
EXPECTED_BACK_TRANSFORM = "hmirror"

DX_VALUES = list(range(-80, 81, 20))
DY_VALUES = list(range(-80, 81, 20))
ROTATIONS = [-1.0, 0.0, 1.0]
MIN_WHITE_SOURCE_COVERAGE = 0.10
SAMPLE_WIDTH = 424
SAMPLE_HEIGHT = 544
MIN_VALID_PIXELS = 5000


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int = 16, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def transform_array(arr: np.ndarray, name: str) -> np.ndarray:
    if name == "identity":
        return arr
    if name == "hmirror":
        return np.fliplr(arr)
    if name == "vmirror":
        return np.flipud(arr)
    if name == "rot180":
        return np.flipud(np.fliplr(arr))
    raise ValueError(name)


def transform_image(
    img: Image.Image,
    angle: float,
    dx: int,
    dy: int,
    resample: Image.Resampling,
    fillcolor,
) -> Image.Image:
    rotated = img.rotate(
        angle,
        resample=resample,
        expand=False,
        center=(img.width / 2, img.height / 2),
        fillcolor=fillcolor,
    )
    return rotated.transform(
        img.size,
        Image.Transform.AFFINE,
        (1, 0, -dx, 0, 1, -dy),
        resample=resample,
        fillcolor=fillcolor,
    )


def load_readable_pages() -> dict[int, Image.Image]:
    pages: dict[int, Image.Image] = {}
    for page in PAIR_PAGES:
        img, _meta = fixed_pass.extract_embedded_page(fixed_pass.PDF, page)
        pages[page] = fixed_pass.normalize_to_readable(img)
    return pages


def paper_features(img: Image.Image) -> dict[str, np.ndarray]:
    small = img.convert("RGB").resize((SAMPLE_WIDTH, SAMPLE_HEIGHT), Image.Resampling.LANCZOS)
    gray = small.convert("L")
    blur = gray.filter(ImageFilter.GaussianBlur(radius=7))
    highpass = np.asarray(gray, dtype=np.float32) - np.asarray(blur, dtype=np.float32)
    rgb = np.asarray(small, dtype=np.float32)
    luma = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    background = (luma > 172.0) & (saturation < 46.0)
    interior = np.zeros_like(background, dtype=bool)
    interior[10:-10, 10:-10] = True
    background &= interior
    return {
        "image": np.asarray(small, dtype=np.uint8),
        "highpass": highpass,
        "background": background,
    }


def corrcoef(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> float | None:
    if int(mask.sum()) < MIN_VALID_PIXELS:
        return None
    av = a[mask].astype(np.float32)
    bv = b[mask].astype(np.float32)
    av -= float(av.mean())
    bv -= float(bv.mean())
    denom = float(np.sqrt(np.sum(av * av) * np.sum(bv * bv)))
    if denom <= 1e-9:
        return None
    return float(np.sum(av * bv) / denom)


def iou(a: np.ndarray, b: np.ndarray) -> float:
    union = a | b
    return float((a & b).sum() / union.sum()) if int(union.sum()) else 0.0


def inspect_paper_pair(page_a: int, page_b: int, pair_class: str, features: dict[int, dict[str, np.ndarray]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    a_hp = features[page_a]["highpass"]
    a_bg = features[page_a]["background"]
    b_hp = features[page_b]["highpass"]
    b_bg = features[page_b]["background"]
    for transform in TRANSFORMS:
        tb_hp = transform_array(b_hp, transform)
        tb_bg = transform_array(b_bg, transform)
        mask = a_bg & tb_bg
        corr = corrcoef(a_hp, tb_hp, mask)
        rows.append(
            {
                "pair": f"{page_a}/{page_b}",
                "pageA": page_a,
                "pageB": page_b,
                "class": pair_class,
                "transform": transform,
                "validPixelCount": int(mask.sum()),
                "backgroundIou": round(iou(a_bg, tb_bg), 6),
                "paperTextureCorrelation": None if corr is None else round(corr, 6),
                "isExpectedBackTransform": transform == EXPECTED_BACK_TRANSFORM,
            }
        )
    return rows


def rank_paper_rows(rows: list[dict[str, Any]]) -> None:
    by_pair: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_pair.setdefault(row["pair"], []).append(row)
    for pair_rows in by_pair.values():
        ranked = sorted(
            pair_rows,
            key=lambda row: -999.0 if row["paperTextureCorrelation"] is None else float(row["paperTextureCorrelation"]),
            reverse=True,
        )
        for rank, row in enumerate(ranked, start=1):
            row["rankWithinPair"] = rank
            row["pairBestTransform"] = ranked[0]["transform"]
            row["pairBestCorrelation"] = ranked[0]["paperTextureCorrelation"]


def paper_texture_step(pages: dict[int, Image.Image]) -> dict[str, Any]:
    features = {page: paper_features(img) for page, img in pages.items()}
    rows: list[dict[str, Any]] = []
    old_set = {tuple(pair) for pair in OLD_ASSUMED_LEAVES}
    corrected_set = {tuple(pair) for pair in PROPOSED_LEAVES}
    for pair in OLD_ASSUMED_LEAVES:
        rows.extend(inspect_paper_pair(pair[0], pair[1], "old_assumed_leaf", features))
    for pair in PROPOSED_LEAVES:
        rows.extend(inspect_paper_pair(pair[0], pair[1], "proposed_corrected_leaf", features))
    for a in PAIR_PAGES:
        for b in PAIR_PAGES:
            if a >= b:
                continue
            pair = (a, b)
            if pair in old_set or pair in corrected_set:
                continue
            rows.extend(inspect_paper_pair(a, b, "control_pair", features))
    rank_paper_rows(rows)
    control_corr = [
        float(row["paperTextureCorrelation"])
        for row in rows
        if row["class"] == "control_pair" and row["paperTextureCorrelation"] is not None
    ]
    control_p95 = float(np.quantile(control_corr, 0.95)) if control_corr else 0.0

    def summarize_class(class_name: str) -> dict[str, Any]:
        expected_rows = [row for row in rows if row["class"] == class_name and row["transform"] == EXPECTED_BACK_TRANSFORM]
        corr = [float(row["paperTextureCorrelation"]) for row in expected_rows if row["paperTextureCorrelation"] is not None]
        return {
            "pairCount": len(expected_rows),
            "expectedBackTransformBestCount": sum(1 for row in expected_rows if row.get("rankWithinPair") == 1),
            "expectedBackTransformAboveControlP95Count": sum(
                1
                for row in expected_rows
                if row["paperTextureCorrelation"] is not None and float(row["paperTextureCorrelation"]) > control_p95
            ),
            "expectedBackTransformMeanCorrelation": round(float(np.mean(corr)), 6) if corr else 0.0,
            "expectedBackTransformMaxCorrelation": round(max(corr), 6) if corr else 0.0,
            "bestTransforms": {row["pair"]: row["pairBestTransform"] for row in expected_rows},
        }

    old_summary = summarize_class("old_assumed_leaf")
    corrected_summary = summarize_class("proposed_corrected_leaf")
    topology_confirmed = (
        corrected_summary["expectedBackTransformBestCount"] == len(PROPOSED_LEAVES)
        and corrected_summary["expectedBackTransformAboveControlP95Count"] == len(PROPOSED_LEAVES)
        and corrected_summary["expectedBackTransformMeanCorrelation"] > old_summary["expectedBackTransformMeanCorrelation"]
    )
    return {
        "rows": rows,
        "summary": {
            "oldAssumed": old_summary,
            "proposedCorrected": corrected_summary,
            "controlP95": round(control_p95, 6),
            "controlMax": round(max(control_corr), 6) if control_corr else 0.0,
            "topologyConfirmedByPaperTexture": topology_confirmed,
            "paperTextureFingerprint": (
                f"oldBest={old_summary['expectedBackTransformBestCount']}/{len(OLD_ASSUMED_LEAVES)}|"
                f"oldAboveP95={old_summary['expectedBackTransformAboveControlP95Count']}/{len(OLD_ASSUMED_LEAVES)}|"
                f"corrBest={corrected_summary['expectedBackTransformBestCount']}/{len(PROPOSED_LEAVES)}|"
                f"corrAboveP95={corrected_summary['expectedBackTransformAboveControlP95Count']}/{len(PROPOSED_LEAVES)}|"
                f"oldMean={old_summary['expectedBackTransformMeanCorrelation']:.4f}|"
                f"corrMean={corrected_summary['expectedBackTransformMeanCorrelation']:.4f}|"
                f"controlP95={control_p95:.4f}|confirmed={int(topology_confirmed)}"
            ),
        },
    }


def white_knockout_mask(page77: Image.Image) -> np.ndarray:
    arr = np.asarray(page77.convert("RGB"), dtype=np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    saturation = arr.max(axis=2) - arr.min(axis=2)
    bright_neutral = (luma > 150.0) & (saturation < 80.0)
    # Remove isolated compression specks while preserving white text strokes.
    mask_img = Image.fromarray((bright_neutral.astype(np.uint8) * 255), mode="L")
    mask_img = mask_img.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    return np.asarray(mask_img) > 127


def transformed_mask(mask_img: Image.Image, angle: float, dx: int, dy: int) -> np.ndarray:
    mirrored = ImageOps.mirror(mask_img)
    moved = transform_image(
        mirrored,
        angle,
        dx,
        dy,
        Image.Resampling.NEAREST,
        0,
    )
    return np.asarray(moved) > 127


def score_box(source_mask: np.ndarray, target_mask: np.ndarray, box: list[float]) -> dict[str, float]:
    base = fixed_pass.mask_box_stats(source_mask, target_mask, box)
    return {
        "sourceCoverage": base["sourceCoverage"],
        "sourceOnlyCoverage": base["sourceOnlyCoverage"],
        "sourceTargetOverlapCoverage": base["sourceTargetOverlapCoverage"],
        "sourceTargetJaccard": base["sourceTargetJaccard"],
    }


def percentile(value: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return sum(1 for control in controls if control <= value) / len(controls)


def score_mode(
    source_mask: np.ndarray,
    target_mask: np.ndarray,
    rows: list[dict[str, Any]],
    control_map: dict[str, list[list[float]]],
    angle: float,
    dx: int,
    dy: int,
) -> dict[str, Any]:
    stats_rows = []
    for row in rows:
        stats = score_box(source_mask, target_mask, row["box"])
        controls = [score_box(source_mask, target_mask, box)["sourceCoverage"] for box in control_map[row["shortId"]]]
        controls_source_only = [
            score_box(source_mask, target_mask, box)["sourceOnlyCoverage"] for box in control_map[row["shortId"]]
        ]
        control_p95 = float(np.quantile(controls, 0.95)) if controls else 0.0
        control_p95_source_only = float(np.quantile(controls_source_only, 0.95)) if controls_source_only else 0.0
        stats_rows.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "box": row["box"],
                **stats,
                "controlCount": len(controls),
                "controlP95SourceCoverage": control_p95,
                "controlMaxSourceCoverage": max(controls) if controls else 0.0,
                "sourceCoverageControlPercentile": percentile(stats["sourceCoverage"], controls),
                "aboveControlP95SourceCoverage": stats["sourceCoverage"] > control_p95 if controls else False,
                "controlP95SourceOnlyCoverage": control_p95_source_only,
                "sourceOnlyControlPercentile": percentile(stats["sourceOnlyCoverage"], controls_source_only),
                "aboveControlP95SourceOnlyCoverage": stats["sourceOnlyCoverage"] > control_p95_source_only if controls_source_only else False,
                "atLeast10SourceCoverage": stats["sourceCoverage"] >= MIN_WHITE_SOURCE_COVERAGE,
            }
        )
    active_at_least_10 = sum(1 for row in stats_rows if row["atLeast10SourceCoverage"])
    active_above_p95 = sum(1 for row in stats_rows if row["aboveControlP95SourceCoverage"])
    active_above_source_only_p95 = sum(1 for row in stats_rows if row["aboveControlP95SourceOnlyCoverage"])
    return {
        "angleDegrees": angle,
        "dx": dx,
        "dy": dy,
        "transformLabel": f"hmirror p77 white, rot={angle:+.1f}, dx={dx:+d}, dy={dy:+d}",
        "statsRows": stats_rows,
        "activeAtLeast10SourceCoverageCount": active_at_least_10,
        "activeAboveControlP95SourceCoverageCount": active_above_p95,
        "activeAboveControlP95SourceOnlyCoverageCount": active_above_source_only_p95,
        "allFourAtLeast10SourceCoverage": active_at_least_10 == 4,
        "allFourAboveControlP95SourceCoverage": active_above_p95 == 4,
        "allFourSignalCandidate": active_at_least_10 == 4 and active_above_p95 == 4,
        "meanSourceCoverage": float(np.mean([row["sourceCoverage"] for row in stats_rows])),
        "minSourceCoverage": float(np.min([row["sourceCoverage"] for row in stats_rows])),
        "meanSourceCoverageControlPercentile": float(
            np.mean([row["sourceCoverageControlPercentile"] for row in stats_rows])
        ),
        "registrationDistance": abs(dx) + abs(dy) + abs(angle) * 40,
    }


def mode_rank(mode: dict[str, Any]) -> tuple[Any, ...]:
    return (
        mode["allFourSignalCandidate"],
        mode["activeAboveControlP95SourceCoverageCount"],
        mode["activeAtLeast10SourceCoverageCount"],
        mode["meanSourceCoverage"],
        mode["meanSourceCoverageControlPercentile"],
        -mode["registrationDistance"],
    )


def compact_mode(mode: dict[str, Any]) -> dict[str, Any]:
    return {
        "transformLabel": mode["transformLabel"],
        "angleDegrees": mode["angleDegrees"],
        "dx": mode["dx"],
        "dy": mode["dy"],
        "activeAtLeast10SourceCoverageCount": mode["activeAtLeast10SourceCoverageCount"],
        "activeAboveControlP95SourceCoverageCount": mode["activeAboveControlP95SourceCoverageCount"],
        "activeAboveControlP95SourceOnlyCoverageCount": mode["activeAboveControlP95SourceOnlyCoverageCount"],
        "allFourSignalCandidate": mode["allFourSignalCandidate"],
        "meanSourceCoverage": mode["meanSourceCoverage"],
        "minSourceCoverage": mode["minSourceCoverage"],
        "meanSourceCoverageControlPercentile": mode["meanSourceCoverageControlPercentile"],
    }


def blend_overlay(target: Image.Image, source_mask: np.ndarray, tint=(48, 168, 255)) -> Image.Image:
    mask_img = Image.fromarray((source_mask.astype(np.uint8) * 190), mode="L")
    overlay = Image.new("RGB", target.size, tint)
    return Image.composite(overlay, target, mask_img)


def crop_and_fit(img: Image.Image, crop: tuple[int, int, int, int], size=(620, 420)) -> Image.Image:
    return ImageOps.contain(img.crop(crop).convert("RGB"), size)


def titled_panel(title: str, subtitle: str, img: Image.Image, size=(660, 520)) -> Image.Image:
    canvas = Image.new("RGB", size, (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 12), title, fill=(20, 24, 31), font=font(21, True))
    draw.text((16, 40), subtitle, fill=(72, 84, 96), font=font(13))
    fit = ImageOps.contain(img, (size[0] - 28, size[1] - 70))
    canvas.paste(fit, ((size[0] - fit.width) // 2, 66))
    return canvas


def score_panel(best: dict[str, Any], natural: dict[str, Any], summary: dict[str, Any]) -> Image.Image:
    canvas = Image.new("RGB", (660, 520), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 12), "77 -> 76 decision", fill=(20, 24, 31), font=font(21, True))
    draw.text((16, 40), "Pass requires active boxes above controls plus source-backed R3.", fill=(72, 84, 96), font=font(13))
    y = 78
    for label, mode in [("best", best), ("natural", natural)]:
        draw.text((16, y), f"{label}: {mode['transformLabel']}", fill=(20, 24, 31), font=font(15, True))
        y += 22
        draw.text(
            (28, y),
            f">=10% {mode['activeAtLeast10SourceCoverageCount']}/4; above p95 {mode['activeAboveControlP95SourceCoverageCount']}/4; mean {mode['meanSourceCoverage']:.4f}",
            fill=(40, 48, 58),
            font=font(13),
        )
        y += 32
    y += 4
    draw.text((16, y), "Best active target scores", fill=(20, 24, 31), font=font(15, True))
    y += 26
    xs = [18, 92, 185, 280, 374, 492]
    headers = ["target", "src", "ctrl p95", "pct", "src-only", "pass"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 76, 84), font=font(12))
    y += 22
    for row in best["statsRows"]:
        vals = [
            row["target"],
            f"{row['sourceCoverage']:.4f}",
            f"{row['controlP95SourceCoverage']:.4f}",
            f"{row['sourceCoverageControlPercentile']:.2f}",
            f"{row['sourceOnlyCoverage']:.4f}",
            "yes" if row["aboveControlP95SourceCoverage"] else "no",
        ]
        for x, val in zip(xs, vals):
            draw.text((x, y), val, fill=(30, 35, 42), font=font(12))
        y += 22
    y += 10
    for line in [
        f"modes: {summary['modeCount']}; all-four signal modes: {summary['allFourSignalCandidateModeCount']}",
        f"source-backed R3: {summary['sourceBackedR3BridgeHitCount']}; selector unlocked: {summary['selectorUnlocked']}",
        f"paper step: {summary['paperTextureFingerprint']}",
        f"decision: {summary['decision']}",
    ]:
        draw.text((18, y), line[:95], fill=(30, 35, 42), font=font(12))
        y += 22
    return canvas


def paper_panel(paper: dict[str, Any]) -> Image.Image:
    canvas = Image.new("RGB", (660, 520), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 12), "Step 0: topology texture check", fill=(20, 24, 31), font=font(21, True))
    draw.text((16, 40), "Expected front/back view is horizontal mirror. This is evidence-only, not extraction.", fill=(72, 84, 96), font=font(13))
    summary = paper["summary"]
    y = 76
    rows = [
        ("old assumed leaves", summary["oldAssumed"]),
        ("proposed corrected leaves", summary["proposedCorrected"]),
    ]
    for label, item in rows:
        draw.text((18, y), label, fill=(20, 24, 31), font=font(15, True))
        y += 24
        draw.text(
            (32, y),
            f"hmirror best {item['expectedBackTransformBestCount']}/{item['pairCount']}; above control p95 {item['expectedBackTransformAboveControlP95Count']}/{item['pairCount']}; mean corr {item['expectedBackTransformMeanCorrelation']:.4f}",
            fill=(40, 48, 58),
            font=font(13),
        )
        y += 24
        draw.text((32, y), f"best transforms: {item['bestTransforms']}", fill=(40, 48, 58), font=font(12))
        y += 36
    draw.text((18, y), f"control p95 {summary['controlP95']:.4f}; control max {summary['controlMax']:.4f}", fill=(40, 48, 58), font=font(13))
    y += 34
    draw.text((18, y), "Proposed pair rows", fill=(20, 24, 31), font=font(15, True))
    y += 24
    proposed_rows = [
        row for row in paper["rows"]
        if row["class"] == "proposed_corrected_leaf" and row["transform"] == EXPECTED_BACK_TRANSFORM
    ]
    for row in proposed_rows:
        draw.text(
            (32, y),
            f"{row['pair']} hmirror rank {row['rankWithinPair']} corr {row['paperTextureCorrelation']} bgIoU {row['backgroundIou']}",
            fill=(30, 35, 42),
            font=font(13),
        )
        y += 24
    return canvas


def build_sheet(
    target: Image.Image,
    source: Image.Image,
    source_mask_base: np.ndarray,
    best_source_mask: np.ndarray,
    natural_source_mask: np.ndarray,
    rows: list[dict[str, Any]],
    crop: tuple[int, int, int, int],
    best: dict[str, Any],
    natural: dict[str, Any],
    paper: dict[str, Any],
    summary: dict[str, Any],
) -> None:
    target_crop = target.crop(crop).convert("RGB")
    source_mask_img = Image.fromarray((source_mask_base.astype(np.uint8) * 255), mode="L")
    source_white_vis = Image.new("RGB", source.size, (8, 12, 18))
    source_white_vis = Image.composite(Image.new("RGB", source.size, (255, 255, 255)), source_white_vis, source_mask_img)
    source_white_mirrored = ImageOps.mirror(source_white_vis)
    best_overlay = blend_overlay(target, best_source_mask)
    natural_overlay = blend_overlay(target, natural_source_mask, tint=(255, 174, 66))
    best_mask_vis = Image.fromarray((best_source_mask.astype(np.uint8) * 255), mode="L").convert("RGB")
    best_boxed = fixed_pass.draw_labeled_boxes(best_overlay.crop(crop), crop, rows, show_labels=True)
    target_boxed = fixed_pass.draw_labeled_boxes(target_crop, crop, rows, show_labels=True)
    panels = [
        titled_panel("page 76 target", "locked O4/B4/G5/O5 boxes", target_boxed),
        titled_panel("p77 white mask", "bright knockout mask, horizontally mirrored", crop_and_fit(source_white_mirrored, crop)),
        titled_panel("natural overlay", "hmirror p77 white mask, no shift", crop_and_fit(natural_overlay, crop)),
        titled_panel("best bounded overlay", best["transformLabel"], best_boxed),
        titled_panel("best source mask only", "same transformed mask used for scoring", crop_and_fit(best_mask_vis, crop)),
        score_panel(best, natural, summary),
        paper_panel(paper),
    ]
    cols = 2
    cell_w, cell_h = 660, 520
    header_h = 90
    rows_n = (len(panels) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, header_h + rows_n * cell_h), (236, 240, 244))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, header_h), fill=(16, 23, 32))
    draw.text((24, 18), "Corrected Topology 77 -> 76 Light-Table Audit", fill=(255, 255, 255), font=font(26, True))
    draw.text((24, 54), summary["fingerprint"], fill=(210, 220, 230), font=font(14))
    for idx, panel in enumerate(panels):
        x = (idx % cols) * cell_w
        y = header_h + (idx // cols) * cell_h
        sheet.paste(panel, (x, y))
    sheet.save(OUT_SHEET, quality=92)


def source_backed_r3_count() -> int:
    strict = load_json(fixed_pass.STRICT_TERM).get("summary", {})
    context = load_json(fixed_pass.TARGET_CONTEXT).get("summary", {})
    line_band = load_json(fixed_pass.LINE_BAND).get("summary", {})
    return max(
        int(strict.get("sourceBackedR3BridgeHitCount") or 0),
        int(context.get("sourceBackedR3BridgeHitCount") or 0),
        int(line_band.get("sourceBackedR3BridgeHitCount") or 0),
    )


def main() -> None:
    pages = load_readable_pages()
    paper = paper_texture_step(pages)

    target = pages[TARGET_PAGE]
    source = pages[SOURCE_PAGE]
    target_mask = fixed_pass.feature_mask(target)
    source_white = white_knockout_mask(source)
    source_mask_img = Image.fromarray((source_white.astype(np.uint8) * 255), mode="L")

    rows = fixed_pass.active_rows()
    active_boxes = [row["box"] for row in rows]
    control_map = {
        row["shortId"]: fixed_pass.control_boxes_for(row["box"], active_boxes, target.size)
        for row in rows
    }
    modes = []
    for angle in ROTATIONS:
        for dx in DX_VALUES:
            for dy in DY_VALUES:
                mask = transformed_mask(source_mask_img, angle, dx, dy)
                modes.append(score_mode(mask, target_mask, rows, control_map, angle, dx, dy))
    modes.sort(key=mode_rank, reverse=True)
    best = modes[0]
    natural = next(mode for mode in modes if mode["angleDegrees"] == 0.0 and mode["dx"] == 0 and mode["dy"] == 0)
    best_mask = transformed_mask(source_mask_img, best["angleDegrees"], best["dx"], best["dy"])
    natural_mask = transformed_mask(source_mask_img, 0.0, 0, 0)

    all_four_signal_modes = [mode for mode in modes if mode["allFourSignalCandidate"]]
    source_r3 = source_backed_r3_count()
    selector = bool(source_r3 > 0 and all_four_signal_modes)
    decision = (
        "pass_candidate_needs_r3_review"
        if all_four_signal_modes and source_r3 > 0
        else "fail_no_r3_or_target_specific_white_mask_signal"
    )
    if all_four_signal_modes and source_r3 == 0:
        decision = "partial_visual_signal_but_no_source_backed_r3"
    elif not all_four_signal_modes:
        decision = "fail_no_target_specific_white_mask_signal"

    summary = {
        "candidateClaim": "page 77 is corrected physical back of page 76",
        "sourcePage": SOURCE_PAGE,
        "targetPage": TARGET_PAGE,
        "modeCount": len(modes),
        "controlBoxesPerTarget": {key: len(value) for key, value in control_map.items()},
        "whiteMaskCoverageWholePage": float(source_white.mean()),
        "allFourSignalCandidateModeCount": len(all_four_signal_modes),
        "allFourAtLeast10SourceCoverageModeCount": sum(1 for mode in modes if mode["allFourAtLeast10SourceCoverage"]),
        "allFourAboveControlP95SourceCoverageModeCount": sum(
            1 for mode in modes if mode["allFourAboveControlP95SourceCoverage"]
        ),
        "bestMode": compact_mode(best),
        "naturalMode": compact_mode(natural),
        "sourceBackedR3BridgeHitCount": source_r3,
        "selectorUnlocked": selector,
        "paperTextureFingerprint": paper["summary"]["paperTextureFingerprint"],
        "topologyConfirmedByPaperTexture": paper["summary"]["topologyConfirmedByPaperTexture"],
        "decision": decision,
    }
    summary["fingerprint"] = (
        f"pair=77->76|whiteMask={summary['whiteMaskCoverageWholePage']:.4f}|"
        f"grid=dxdy+-80x20,rot=-1/0/+1|modes={summary['modeCount']}|"
        f"all4Signal={summary['allFourSignalCandidateModeCount']}|"
        f"bestGe10={best['activeAtLeast10SourceCoverageCount']}/4|"
        f"bestGtP95={best['activeAboveControlP95SourceCoverageCount']}/4|"
        f"paperConfirmed={int(summary['topologyConfirmedByPaperTexture'])}|"
        f"sourceR3={source_r3}|selectors={int(selector)}"
    )

    crop = fixed_pass.crop_bounds(rows, pad=210, page_size=target.size)
    build_sheet(target, source, source_white, best_mask, natural_mask, rows, crop, best, natural, paper, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "corrected-topology 77->76 light-table test; source/visual only, no key derivation",
        "inputs": {
            "handoffProposal": str(HANDOFF),
            "magazinePdf": rel(fixed_pass.PDF),
            "oldTopologyReport": rel(TOPOLOGY),
            "oldPaperTextureGate": rel(PAPER_DUPEX_OLD),
            "activeTargets": rel(ACTIVE_TARGETS),
            "missingRuleFrontier": rel(FRONTIER),
        },
        "paperTextureStep": {
            "oldAssumedLeaves": [list(pair) for pair in OLD_ASSUMED_LEAVES],
            "proposedCorrectedLeaves": [list(pair) for pair in PROPOSED_LEAVES],
            "summary": paper["summary"],
            "rows": paper["rows"],
        },
        "lightTableStep": {
            "sourcePage": SOURCE_PAGE,
            "targetPage": TARGET_PAGE,
            "sourceLayer": "page 77 regenerated bright neutral white-knockout mask, horizontally mirrored",
            "targetRows": rows,
            "bestMode": best,
            "naturalMode": natural,
            "topModes": [compact_mode(mode) for mode in modes[:12]],
        },
        "summary": summary,
        "decision": {
            "status": decision,
            "passed": bool(selector),
            "why": [
                "paper texture step did not confirm corrected topology" if not summary["topologyConfirmedByPaperTexture"] else "paper texture step supports corrected topology",
                f"all-four white-mask signal candidate modes: {len(all_four_signal_modes)}",
                f"source-backed R3 bridge hits: {source_r3}",
                "no selector/key checks may resume without source-backed unit/order evidence",
            ],
            "nextMove": (
                "If pursuing the topology claim further, use human/physical evidence or a physical copy bench test; "
                "the current scan-only 77->76 white-mask sweep does not unlock extraction."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Corrected Topology 77 -> 76 Light-Table Audit",
        "",
        "Scope: test the external proposal that page 77, not page 75, is the physical back-side partner of page 76. This is visual/source triage only; no key derivation, hashing, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Source/target: page `{SOURCE_PAGE}` -> page `{TARGET_PAGE}`",
        f"- Modes checked: `{summary['modeCount']}`",
        f"- Control boxes per target: `{summary['controlBoxesPerTarget']}`",
        f"- White-mask whole-page coverage: `{summary['whiteMaskCoverageWholePage']:.6f}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Step 0: Topology Texture Check",
        "",
        f"- Old assumed leaves: `{OLD_ASSUMED_LEAVES}`.",
        f"- Proposed corrected leaves: `{PROPOSED_LEAVES}`.",
        f"- Paper-texture fingerprint: `{paper['summary']['paperTextureFingerprint']}`.",
        f"- Topology confirmed by paper texture: `{summary['topologyConfirmedByPaperTexture']}`.",
        "",
        "| class | hmirror best | hmirror above control p95 | mean hmirror corr | best transforms |",
        "|---|---:|---:|---:|---|",
    ]
    for label, key in [("old assumed", "oldAssumed"), ("proposed corrected", "proposedCorrected")]:
        item = paper["summary"][key]
        lines.append(
            f"| {label} | `{item['expectedBackTransformBestCount']}/{item['pairCount']}` | "
            f"`{item['expectedBackTransformAboveControlP95Count']}/{item['pairCount']}` | "
            f"`{item['expectedBackTransformMeanCorrelation']:.6f}` | `{item['bestTransforms']}` |"
        )
    lines.extend(
        [
            "",
            "## Step 1: Page 77 White-Mask Landing",
            "",
            f"- Best mode: `{best['transformLabel']}`.",
            f"- Best active boxes with >=10% source coverage: `{best['activeAtLeast10SourceCoverageCount']}/4`.",
            f"- Best active boxes above same-size nearby-control p95: `{best['activeAboveControlP95SourceCoverageCount']}/4`.",
            f"- All-four signal candidate modes: `{summary['allFourSignalCandidateModeCount']}`.",
            f"- Source-backed R3 bridge hits: `{summary['sourceBackedR3BridgeHitCount']}`.",
            f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
            "",
            "| target | source coverage | control p95 | percentile | source-only | above p95 |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in best["statsRows"]:
        lines.append(
            f"| `{row['target']}` | `{row['sourceCoverage']:.6f}` | `{row['controlP95SourceCoverage']:.6f}` | "
            f"`{row['sourceCoverageControlPercentile']:.3f}` | `{row['sourceOnlyCoverage']:.6f}` | "
            f"`{row['aboveControlP95SourceCoverage']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Result: `{decision}`.",
            "- The proposal is worth testing because the old topology was assumption-driven, but this scan-only run does not yet make `77 -> 76` an extraction selector.",
            "- A physical copy bench test may still adjudicate the topology visually, but current pixels do not supply R3 unit/order evidence.",
            "- Do not resume selector/key checks from this branch without a source-backed unit/order instruction.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("decision:", decision)
    print("fingerprint:", summary["fingerprint"])


if __name__ == "__main__":
    main()
