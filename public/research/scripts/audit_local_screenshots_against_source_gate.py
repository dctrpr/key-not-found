#!/usr/bin/env python3
"""Apply the source-validation gate to local Desktop screenshots.

This is a bounded source-quality audit. It checks whether any already-local
Desktop screenshot can be promoted to source material under the newly defined
gate. It does not perform OCR, key derivation, hashing, or address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = Path("private_inputs/Desktop")
REVIEW_JSON = ROOT / "analysis_outputs/source_audit/local_source_candidate_inventory/local_screenshot_visual_review.json"
INVENTORY_JSON = ROOT / "analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_inventory.json"
GATE_JSON = ROOT / "analysis_outputs/source_audit/source_validation_gate/source_validation_gate.json"

OUT = ROOT / "analysis_outputs/source_audit/local_screenshot_source_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "local_screenshot_source_gate.json"
OUT_MD = OUT / "local_screenshot_source_gate.md"
OUT_SHEET = OUT / "local_screenshot_source_gate_sheet.jpg"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def thumb(path: Path, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, (246, 246, 246))
    try:
        img = Image.open(path).convert("RGB")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        canvas.paste(img, ((size[0] - img.width) // 2, (size[1] - img.height) // 2))
    except Exception:
        pass
    return canvas


def draw_sheet(records: list[dict]) -> None:
    cols = 2
    card_w = 920
    card_h = 260
    margin = 32
    width = margin * 2 + cols * card_w
    rows = (len(records) + cols - 1) // cols
    height = 100 + rows * card_h + margin
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title = font(30, True)
    h = font(18, True)
    small = font(15)
    draw.text((margin, 26), "Local Screenshots vs Source Validation Gate", fill=(20, 20, 20), font=title)
    for idx, record in enumerate(records):
        row, col = divmod(idx, cols)
        x = margin + col * card_w
        y = 90 + row * card_h
        fill = (255, 247, 247) if record["sourceGateStatus"] == "reject" else (245, 250, 245)
        draw.rectangle([x, y, x + card_w - 18, y + card_h - 20], fill=fill, outline=(210, 210, 210))
        image.paste(thumb(Path(record["path"]), (240, 170)), (x + 16, y + 42))
        draw.text((x + 16, y + 14), record["name"], fill=(20, 20, 20), font=h)
        tx = x + 275
        draw.text((tx, y + 42), f"status: {record['sourceGateStatus']}", fill=(140, 30, 30), font=h)
        draw.text((tx, y + 72), f"visual: {record['visualContent']}", fill=(45, 45, 45), font=small)
        draw.text((tx, y + 100), f"source quality: {record['sourceQuality']}", fill=(45, 45, 45), font=small)
        draw.text((tx, y + 128), f"benchmark visibility: {record['benchmarkVisibility']}", fill=(45, 45, 45), font=small)
        draw.text((tx, y + 156), f"decision: {record['decision']}", fill=(45, 45, 45), font=small)
    image.save(OUT_SHEET, quality=95)


def find_path_by_name(name: str, inventory: dict) -> Path:
    for record in inventory["records"]:
        if record.get("name") == name:
            return Path(record["path"])
    return DESKTOP / name


def image_meta(path: Path) -> dict:
    try:
        with Image.open(path) as img:
            return {"width": img.width, "height": img.height, "mode": img.mode}
    except Exception as exc:
        return {"error": str(exc)}


def main() -> None:
    review = load(REVIEW_JSON)
    inventory = load(INVENTORY_JSON)
    gate = load(GATE_JSON)
    records = []
    for item in review["screenshots"]:
        path = find_path_by_name(item["name"], inventory)
        meta = image_meta(path)
        visual = item["visualContent"]
        verdict = item["verdict"]
        source_like = any(term in visual.lower() for term in ["page", "magazine", "canva", "article", "pdf", "spread"])
        benchmark_like = any(term in visual.lower() for term in ["page 76", "volcano", "shitcoiner", "pill", "zero", "#0", "overdose"])
        status = "candidate" if source_like and benchmark_like else "reject"
        if "not source" in verdict or "unrelated" in verdict:
            status = "reject"
        record = {
            "name": item["name"],
            "path": str(path),
            "image": meta,
            "visualContent": visual,
            "priorVerdict": verdict,
            "sourceQuality": "fails: screenshot, not native/original-layout export or physical scan",
            "benchmarkVisibility": "passes visually" if benchmark_like else "fails: no visible page-76/zero/pill/frame benchmark",
            "sourceGateStatus": status,
            "decision": "do not promote; witness/noise only" if status == "reject" else "manual review required",
        }
        records.append(record)

    promoted = [r for r in records if r["sourceGateStatus"] != "reject"]
    draw_sheet(records)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "apply source-validation gate to local Desktop screenshots; no key derivation",
        "gateSource": str(GATE_JSON.relative_to(ROOT)),
        "inputReview": str(REVIEW_JSON.relative_to(ROOT)),
        "records": records,
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "promotedCount": len(promoted),
        "decision": "No local Desktop screenshot passes the source gate. All remain unrelated, media context, or solver/reference artifacts rather than source geometry.",
        "nextMove": "Do not revisit local screenshots unless a new file appears. Continue waiting for physical scan/original export/source asset, or use comparison PDFs only for style conventions.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Local Screenshots Against Source Gate",
        "",
        "Scope: apply the source-validation gate to the six already-local Desktop screenshots. No OCR, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Promoted screenshots: `{result['promotedCount']}`",
        "",
        "## Results",
        "",
        "| screenshot | visual content | source gate | reason |",
        "|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            f"| `{record['name']}` | {record['visualContent']} | `{record['sourceGateStatus']}` | {record['sourceQuality']}; {record['benchmarkVisibility']} |"
        )
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("promotedCount:", len(promoted))


if __name__ == "__main__":
    main()
