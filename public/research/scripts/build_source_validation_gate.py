#!/usr/bin/env python3
"""Build a source-validation gate for future puzzle source material.

This creates a single checklist/report from the current strongest baselines:
page-76 priority crops, zero/#0 hotspots, p79 pill geometry, and the repaired
p78-frame exact-edge benchmark. It does not inspect a new source and does not
generate keys.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_validation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_validation_gate.json"
OUT_MD = OUT / "source_validation_gate.md"
OUT_SHEET = OUT / "source_validation_gate_sheet.jpg"

PRIORITY_JSON = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"
ZERO_JSON = ROOT / "analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops.json"
PILL_JSON = ROOT / "analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry.json"
TRI_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
STABILITY_JSON = ROOT / "analysis_outputs/source_audit/repaired_exact_edge_stability_window/repaired_exact_edge_stability_window.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: str | Path) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def abs_path(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def make_thumb(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (246, 246, 246))
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, width: int, fill=(45, 45, 45), line_gap=5) -> int:
    x, y = xy
    words = text.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
            line = test
        else:
            draw.text((x, y), line, fill=fill, font=fnt)
            y += fnt.size + line_gap
            line = word
    if line:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += fnt.size + line_gap
    return y


def build_sheet(priority: dict, zero: dict, pill: dict, tri: dict, stability: dict) -> None:
    width, height = 1900, 1450
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title = font(32, True)
    h = font(22, True)
    body = font(18)
    small = font(15)

    y = 28
    draw.text((32, y), "Source Validation Gate: Max Keiser Puzzle", fill=(20, 20, 20), font=title)
    y += 48
    draw_wrapped(
        draw,
        (32, y),
        "Use this before any new extraction. A new source must either change source geometry in one of these benchmark regions or reveal new instruction/layer text.",
        body,
        1700,
        fill=(70, 70, 70),
    )

    # Top reference panels.
    panels = [
        ("Page 76 priority crops", abs_path(priority["sheet"])),
        ("Zero/#0 hotspots", abs_path(zero["sheet"])),
        ("P79 pill geometry", abs_path(pill["sheet"])),
        ("P78 tri-contact", abs_path(tri["overlay"])),
        ("Exact-edge stability", abs_path(stability["heatmap"])),
    ]
    x_positions = [32, 398, 764, 1130, 1496]
    y_panel = 145
    for (label, path), x in zip(panels, x_positions):
        draw.rectangle([x, y_panel, x + 340, y_panel + 300], outline=(190, 190, 190), width=2)
        draw.text((x + 12, y_panel + 10), label, fill=(20, 20, 20), font=h)
        thumb = make_thumb(path, (316, 220))
        image.paste(thumb, (x + 12, y_panel + 52))

    y = 485
    draw.text((32, y), "Acceptance Gates", fill=(20, 20, 20), font=title)
    y += 46

    gates = [
        ("A. Source Quality", "Native/original-layout export or physical scan/photo. Low-res thumbnails and OCR PDFs are witnesses only."),
        ("B. Page-76 Target Crops", "Check O5 `shitcoiner at heart`, G5 `Volcano Bonds`, and L25-L32 frame context first. If unchanged, do not rerun local text permutations."),
        ("C. Zero/#0 Hotspots", "Verify p77 `100,000` first, then `20,000`, `12,000`, `2008`, `2011`, `2017`, and both `10 years` references. Only visible source differences matter."),
        ("D. P79 Pills / Diff Pic", "Count and order the five p79 lower-left pill fragments. If count/order/placement differs, run registration before extraction."),
        ("E. Repaired P78 Frame", "Test whether `should sell | Volcano Bonds | shitcoiner at heart` with styles `R-K-Y` survives and whether M3/O5/G5 tri-contact fits dx about -38/-40."),
        ("F. Extraction Permission", "Only generate key candidates after a source/clue names the unit: word, letter, line, edge, font state, first/last, or equivalent."),
    ]
    for label, text in gates:
        draw.rectangle([32, y - 8, width - 32, y + 86], fill=(246, 248, 250), outline=(215, 220, 225))
        draw.text((52, y + 6), label, fill=(15, 70, 120), font=h)
        draw_wrapped(draw, (330, y + 8), text, body, 1450, fill=(45, 45, 45), line_gap=4)
        y += 104

    y += 8
    draw.text((32, y), "Current Baseline Facts", fill=(20, 20, 20), font=title)
    y += 48
    facts = [
        f"Priority targets: O5 `{priority['targetPriority']['primaryManualTarget']['text']}`; G5 `{priority['targetPriority']['pairedTarget']['text']}`.",
        f"Zero baseline: trusted high-res p77 reads `100,000`; source discrepancy remains unresolved until the exact browser/Canva/original view is supplied.",
        f"P79 pill baseline: trusted high-res fragments={len(pill['trustedHighresFragments'])}; OCR/Google witness also has {len(pill['googleNormalizedComponents'])} normalized fragments but is not geometry truth.",
        f"Stability window: exact-edge + tri-contact survives dx {stability['summaries']['targetExactAndTriContact']['dxRange']} and dy {stability['summaries']['targetExactAndTriContact']['dyRange']}.",
    ]
    for fact in facts:
        y = draw_wrapped(draw, (56, y), "- " + fact, small, 1760, fill=(60, 60, 60), line_gap=4)
        y += 6

    OUT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT_SHEET, quality=95)


def main() -> None:
    priority = load(PRIORITY_JSON)
    zero = load(ZERO_JSON)
    pill = load(PILL_JSON)
    tri = load(TRI_JSON)
    stability = load(STABILITY_JSON)

    gates = [
        {
            "id": "source_quality",
            "accept": "Native/original-layout export, source image, or physical scan/photo with enough resolution to inspect the benchmark crops.",
            "reject": "Connector thumbnail, OCR PDF coordinates, low-res screenshot, or derived analysis image only.",
        },
        {
            "id": "page76_priority_crops",
            "accept": "O5, G5, and L25-L32 crop regions are visible and can be compared against the baseline sheet.",
            "baseline": priority["sheet"],
            "activeTargets": priority["targetPriority"],
        },
        {
            "id": "zero_hash0_hotspots",
            "accept": "New source visibly confirms or changes one of the zero/#0 hotspots.",
            "baseline": rel(zero["sheet"]),
            "hotspotOrder": [row["token"] for row in zero["rows"]],
        },
        {
            "id": "p79_pill_geometry",
            "accept": "New source changes or confirms the five-fragment count/order/placement.",
            "baseline": rel(pill["sheet"]),
            "trustedFragmentCount": len(pill["trustedHighresFragments"]),
            "trustedFragmentCenters": [frag["center"] for frag in pill["trustedHighresFragments"]],
        },
        {
            "id": "p78_frame_exact_edge",
            "accept": "New source supports or changes the repaired exact-edge signature and M3/O5/G5 tri-contact.",
            "signature": stability["targetSignature"],
            "triContactFrame": tri["records"][1]["frame"],
            "stableDxRange": stability["summaries"]["targetExactAndTriContact"]["dxRange"],
            "stableDyRange": stability["summaries"]["targetExactAndTriContact"]["dyRange"],
        },
        {
            "id": "extraction_permission",
            "accept": "Only proceed to key checks if the new source/clue names the extraction unit/order.",
            "blockedWithout": ["word", "letter", "line", "edge", "font state", "first/last", "explicit ordering"],
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-validation gate for future physical/original-layout/source material; no key derivation",
        "inputs": {
            "priorityCropPack": rel(PRIORITY_JSON),
            "zeroVisualCrops": rel(ZERO_JSON),
            "pillGeometry": rel(PILL_JSON),
            "triContact": rel(TRI_JSON),
            "stabilityWindow": rel(STABILITY_JSON),
        },
        "sheet": rel(OUT_SHEET),
        "gates": gates,
        "decision": [
            "A new source is promoted only if it changes/validates source geometry in a benchmark region or reveals instruction/layer text.",
            "If benchmark regions are unchanged and no unit is named, treat the source as a witness only.",
            "Do not run key candidates until the extraction unit/order is named.",
        ],
        "nextMove": "When a new source arrives, run this gate first: source quality, page-76 priority crops, zero/#0 hotspots, p79 pill geometry, repaired p78 frame, then extraction permission.",
    }

    build_sheet(priority, zero, pill, tri, stability)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Validation Gate",
        "",
        "Scope: consolidate the current source-fidelity benchmarks into a gate for future physical/original-layout/source material. No key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Gates",
        "",
        "| gate | accept | reject / block |",
        "|---|---|---|",
    ]
    for gate in gates:
        block = gate.get("reject") or ", ".join(gate.get("blockedWithout", [])) or "-"
        lines.append(f"| `{gate['id']}` | {gate['accept']} | {block} |")

    lines.extend(
        [
            "",
            "## Baseline Priority",
            "",
            f"- O5 primary: `{priority['targetPriority']['primaryManualTarget']['text']}`.",
            f"- G5 pair: `{priority['targetPriority']['pairedTarget']['text']}`.",
            f"- Source band: `{priority['targetPriority']['sourceBandTarget']['text']}`.",
            f"- Zero/#0 baseline sheet: `{rel(zero['sheet'])}`.",
            f"- P79 pill baseline: `{len(pill['trustedHighresFragments'])}` lower-left fragments.",
            f"- Repaired exact-edge signature: `{ ' | '.join(stability['targetSignature']['labels']) }` / `{stability['targetSignature']['styles']}`.",
            "",
            "## Decision",
            "",
        ]
    )
    for item in result["decision"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("gates:", len(gates))


if __name__ == "__main__":
    main()
