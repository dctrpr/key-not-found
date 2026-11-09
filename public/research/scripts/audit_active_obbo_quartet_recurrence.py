#!/usr/bin/env python3
"""Check whether the active page-76 O-B-B-O quartet recurs in controls.

This is a bounded OVERDOSE layout-control pass. It scans the line-shaped
orange/dark highlight boxes already detected in Issue 24 and independent Max
comparison articles, looking for consecutive top-to-bottom O-B-B-O quartets and
for quartets whose vertical placement matches the active page-76 lower corridor.
It does not run OCR extraction, key derivation, hashing, seed/WIF checks, or
address checks.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/comparison_articles/active_obbo_quartet_recurrence"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_obbo_quartet_recurrence.json"
OUT_MD = OUT / "active_obbo_quartet_recurrence.md"
SHEET = OUT / "active_obbo_quartet_recurrence_sheet.jpg"

REPORTS = {
    "body_highlighter_grammar": ROOT / "analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json",
    "active_crop_completion": ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json",
    "active_order_orientation_trap": ROOT / "analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.json",
    "comparison_layout_r3_gate": ROOT / "analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis/overdose_layout_r3_gate_synthesis.json",
}

ISSUE24_SOURCE = "issue24_toxic_af"
INDEPENDENT_CONTROL_SOURCES = {"issue26", "issue27", "bitcoin3"}
ACTIVE_L1_THRESHOLD = 0.08


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def center_y(box: list[int | float]) -> float:
    return (float(box[1]) + float(box[3])) / 2.0


def center_x(box: list[int | float]) -> float:
    return (float(box[0]) + float(box[2])) / 2.0


def page_events(record: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for box in record.get("orangeBoxes", []):
        events.append({"color": "O", "box": box, "centerY": center_y(box), "centerX": center_x(box)})
    for box in record.get("darkBoxes", []):
        events.append({"color": "B", "box": box, "centerY": center_y(box), "centerX": center_x(box)})
    return sorted(events, key=lambda item: (item["centerY"], item["centerX"]))


def active_ratios(crop_completion: dict[str, Any]) -> list[float]:
    targets = sorted(
        crop_completion.get("targets", []),
        key=lambda row: (center_y(row.get("box", [0, 0, 0, 0])), center_x(row.get("box", [0, 0, 0, 0]))),
    )
    source_image = ROOT / crop_completion.get("sourceImage", "analysis_outputs/3d_article_map/page_76_upright.jpg")
    height = Image.open(source_image).height if source_image.exists() else 3264
    return [center_y(row["box"]) / height for row in targets]


def scan_windows(body: dict[str, Any], active: list[float]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    page_summaries: list[dict[str, Any]] = []
    windows: list[dict[str, Any]] = []
    for record in body.get("pageRecords", []):
        events = page_events(record)
        seq = "".join(event["color"] for event in events)
        page_summaries.append(
            {
                "source": record.get("source"),
                "page": record.get("page"),
                "sequence": seq,
                "eventCount": len(events),
                "orangeCount": sum(1 for event in events if event["color"] == "O"),
                "darkCount": sum(1 for event in events if event["color"] == "B"),
                "grammarScore": record.get("grammarScore"),
            }
        )
        height = record.get("size", [0, 1])[1] or 1
        for idx in range(0, max(0, len(events) - 3)):
            segment = events[idx : idx + 4]
            if "".join(event["color"] for event in segment) != "OBBO":
                continue
            ratios = [event["centerY"] / height for event in segment]
            delta = sum(abs(a - b) for a, b in zip(active, ratios))
            windows.append(
                {
                    "source": record.get("source"),
                    "page": record.get("page"),
                    "windowIndex1": idx + 1,
                    "sequence": "OBBO",
                    "yRatios": [round(value, 6) for value in ratios],
                    "activeL1Delta": round(delta, 6),
                    "boxes": [event["box"] for event in segment],
                    "image": rel(record.get("path")),
                    "isIssue24": record.get("source") == ISSUE24_SOURCE,
                    "isIndependentControl": record.get("source") in INDEPENDENT_CONTROL_SOURCES,
                    "activeLike": delta <= ACTIVE_L1_THRESHOLD,
                }
            )
    return page_summaries, sorted(windows, key=lambda item: item["activeL1Delta"])


def draw_window_panel(sheet: Image.Image, window: dict[str, Any], box: tuple[int, int, int, int]) -> None:
    draw = ImageDraw.Draw(sheet)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(18, 22, 28), outline=(48, 58, 70))
    title = f"{window['source']} p{window['page']} idx {window['windowIndex1']} delta {window['activeL1Delta']}"
    draw.text((x0 + 12, y0 + 10), title, fill=(238, 243, 248), font=font(16))

    image_path = ROOT / window["image"]
    if not image_path.exists():
        draw.text((x0 + 12, y0 + 40), "image missing", fill=(255, 130, 130), font=font(14))
        return
    image = Image.open(image_path).convert("RGB")
    overlay = image.copy()
    odraw = ImageDraw.Draw(overlay)
    colors = ["#ff9b2e", "#8f98a5", "#8f98a5", "#ff9b2e"]
    labels = ["O", "B", "B", "O"]
    for b, color, label in zip(window["boxes"], colors, labels):
        for offset in range(5):
            odraw.rectangle((b[0] - offset, b[1] - offset, b[2] + offset, b[3] + offset), outline=color)
        odraw.text((b[0], max(0, b[1] - 32)), label, fill=color, font=font(32))

    max_w = x1 - x0 - 24
    max_h = y1 - y0 - 58
    scale = min(max_w / overlay.width, max_h / overlay.height)
    resized = overlay.resize((max(1, int(overlay.width * scale)), max(1, int(overlay.height * scale))), Image.Resampling.LANCZOS)
    sheet.paste(resized, (x0 + 12, y0 + 46))


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1760, 1380
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "Active O-B-B-O Quartet Recurrence", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 46),
        "Scans line-shaped orange/dark highlight boxes across Issue 24 and independent OVERDOSE controls.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("active y ratios", " ".join(f"{v:.3f}" for v in result["summary"]["activeYRatios"])),
        ("total OBBO windows", result["summary"]["totalObboWindows"]),
        ("independent OBBO", result["summary"]["independentControlObboWindows"]),
        ("active-like controls", result["summary"]["independentControlActiveLikeWindows"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 405, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value)[:42], fill=(232, 239, 246), font=mono)
        x += 425

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 102), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "The lower page-76 active OBBO geometry is distinctive in local controls, but still only location/style evidence.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 74),
        "No comparison page supplies word/letter/line/font order; R3 remains blocked.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 135
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("source", 12), ("pages", 230), ("OBBO windows", 400), ("active-like", 610), ("note", 820)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["sourceSummaries"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 44), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 12), row["source"], fill=(238, 243, 248), font=small)
        draw.text((margin + 230, y + 12), str(row["pages"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 400, y + 12), str(row["obboWindows"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 610, y + 12), str(row["activeLikeWindows"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 820, y + 12), row["note"], fill=(176, 186, 198), font=small)
        y += 48

    y += 24
    panels = result["windows"][:3]
    panel_w = (sheet_w - margin * 2 - 32) // 3
    panel_h = 520
    for idx, window in enumerate(panels):
        x0 = margin + idx * (panel_w + 16)
        draw_window_panel(sheet, window, (x0, y, x0 + panel_w, y + panel_h))

    sheet.save(SHEET, quality=94)


def main() -> None:
    body = load_json(REPORTS["body_highlighter_grammar"])
    crop_completion = load_json(REPORTS["active_crop_completion"])
    order_trap = load_json(REPORTS["active_order_orientation_trap"])
    comparison_gate = load_json(REPORTS["comparison_layout_r3_gate"])

    active = active_ratios(crop_completion)
    page_summaries, windows = scan_windows(body, active)

    by_source: dict[str, dict[str, Any]] = defaultdict(lambda: {"pages": 0, "obboWindows": 0, "activeLikeWindows": 0})
    for page in page_summaries:
        by_source[page["source"]]["pages"] += 1
    for window in windows:
        by_source[window["source"]]["obboWindows"] += 1
        if window["activeLike"]:
            by_source[window["source"]]["activeLikeWindows"] += 1

    source_summaries = []
    for source in sorted(by_source):
        note = "Issue 24 target article" if source == ISSUE24_SOURCE else "independent control"
        source_summaries.append({"source": source, **by_source[source], "note": note})

    independent_windows = [w for w in windows if w["isIndependentControl"]]
    active_like_independent = [w for w in independent_windows if w["activeLike"]]
    active_like_issue24 = [w for w in windows if w["isIssue24"] and w["activeLike"]]

    summary = {
        "activeYRatios": [round(v, 6) for v in active],
        "activePattern": "OBBO",
        "activeOrderGuardrail": order_trap.get("summary", {}).get("uprightPageLines"),
        "activeCorridorGuardrail": order_trap.get("summary", {}).get("uprightCorridorIndexes"),
        "activeLikeThresholdL1": ACTIVE_L1_THRESHOLD,
        "pageRecords": len(page_summaries),
        "independentControlSources": sorted(INDEPENDENT_CONTROL_SOURCES),
        "totalObboWindows": len(windows),
        "issue24ObboWindows": sum(1 for w in windows if w["isIssue24"]),
        "independentControlObboWindows": len(independent_windows),
        "issue24ActiveLikeWindows": len(active_like_issue24),
        "independentControlActiveLikeWindows": len(active_like_independent),
        "nearestIndependentControlDelta": min((w["activeL1Delta"] for w in independent_windows), default=None),
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active OBBO quartet recurrence across body-highlighter control records; no extraction, no OCR, no key derivation, no hashing, no address checks",
        "inputs": {name: rel(path) for name, path in REPORTS.items()},
        "summary": summary,
        "sourceSummaries": source_summaries,
        "windows": windows,
        "decision": "active_obbo_quartet_distinctive_but_no_r3_selector",
        "sheet": rel(SHEET),
        "nextMove": "Keep the lower page-76 O4/B4/G5/O5 OBBO quartet as distinctive target-location/source-validation evidence only; do not treat it as extraction permission without R3 unit/order wording.",
        "comparisonGateDecision": comparison_gate.get("decision"),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active O-B-B-O Quartet Recurrence",
        "",
        "Scope: scan existing line-shaped orange/dark highlighter detections across Issue 24 and independent Max/OVERDOSE comparison articles for the active page-76 `OBBO` quartet. No extraction, key derivation, hashing, OCR extraction, WIF/Base58 scanning, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Active y ratios: `{' '.join(str(v) for v in summary['activeYRatios'])}`.",
        f"- Active readable line order guardrail: `{summary['activeOrderGuardrail']}`.",
        f"- Active readable corridor guardrail: `{summary['activeCorridorGuardrail']}`.",
        f"- Total consecutive `OBBO` windows: `{summary['totalObboWindows']}`.",
        f"- Issue 24 `OBBO` windows: `{summary['issue24ObboWindows']}`.",
        f"- Independent-control `OBBO` windows: `{summary['independentControlObboWindows']}`.",
        f"- Issue 24 active-like windows: `{summary['issue24ActiveLikeWindows']}`.",
        f"- Independent-control active-like windows: `{summary['independentControlActiveLikeWindows']}`.",
        "",
        "## Source Summary",
        "",
        "| source | pages | OBBO windows | active-like windows | note |",
        "|---|---:|---:|---:|---|",
    ]
    for row in source_summaries:
        lines.append(
            f"| `{row['source']}` | `{row['pages']}` | `{row['obboWindows']}` | `{row['activeLikeWindows']}` | {row['note']} |"
        )
    lines.extend(["", "## OBBO Windows", "", "| rank | source/page | index | y ratios | active L1 delta | active-like |", "|---:|---|---:|---|---:|---|"])
    for rank, window in enumerate(windows, start=1):
        lines.append(
            f"| `{rank}` | `{window['source']} p{window['page']}` | `{window['windowIndex1']}` | `{window['yRatios']}` | `{window['activeL1Delta']}` | `{window['activeLike']}` |"
        )
    if not windows:
        lines.append("| - | none | - | - | - | - |")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The exact lower page-76 `OBBO` placement appears as an active-like window only in Issue 24 page 4, matching O4/B4/G5/O5.",
            "- The independent comparison articles in the body-highlighter grammar set produce `0` consecutive `OBBO` windows, so the active quartet is not a generic OVERDOSE body-highlighter pattern in the local controls.",
            "- This strengthens the page-76 lower corridor as target-location/source-validation evidence, but it still does not name a word/letter/line/font unit or an extraction order.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
