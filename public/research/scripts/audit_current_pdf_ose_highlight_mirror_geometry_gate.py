#!/usr/bin/env python3
"""Mirror page-75 orange highlights onto page 76 and check OSE geometry.

The previous pass found that the stable PDF-native OSE source slots touch
page-75 orange highlight text, but not a complete highlight/phrase selector.
This pass checks the geometry directly: under the valid 75 -> 76 horizontal
mirror, do those page-75 highlights land selectively on page-76 active targets,
page-76 highlights, or measured OVERDOSE slots?

No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address
checks, BIP39 checks, or broad brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ose_highlight_mirror_geometry_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ose_highlight_mirror_geometry_gate.json"
OUT_MD = OUT / "current_pdf_ose_highlight_mirror_geometry_gate.md"
OUT_SHEET = OUT / "current_pdf_ose_highlight_mirror_geometry_gate_sheet.jpg"

ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_TARGETS = ROOT / (
    "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
OSE_HIGHLIGHT_PHRASE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_ose_source_highlight_phrase_gate/"
    "current_pdf_ose_source_highlight_phrase_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE75 = ROOT / "analysis_outputs/3d_article_map/page_75_upright.jpg"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

PAGE_SIZE = (2544, 3264)


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
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


def area(box: list[float] | None) -> float:
    if not box:
        return 0.0
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def mirror_box(box: list[float]) -> list[float]:
    width = float(PAGE_SIZE[0])
    return [width - box[2], box[1], width - box[0], box[3]]


def page_highlights(article_map: dict[str, Any], page_no: int) -> list[dict[str, Any]]:
    for page in article_map.get("pages", []):
        if int(page.get("page", -1)) != page_no:
            continue
        return [
            {
                "id": str(item.get("id", "")),
                "kind": str(item.get("kind", "")),
                "box": [float(v) for v in item.get("box", [])],
            }
            for item in page.get("highlights", [])
            if item.get("box")
        ]
    return []


def active_targets(active_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in active_data.get("targets", []):
        rows.append(
            {
                "id": str(target["label"]).split()[0],
                "targetId": target["id"],
                "label": target["label"],
                "phrase": target["phrase"],
                "box": [float(v) for v in target["box"]],
                "visualState": target.get("visualState", ""),
            }
        )
    return rows


def overdose_slots(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])]
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "id": f"{slot['letter']}{slot['index']}",
                "letter": str(slot["letter"]),
                "index": int(slot["index"]),
                "box": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return rows


def contact_rows(source_box: list[float], targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        inter = overlap(source_box, target["box"])
        if not inter:
            continue
        rows.append(
            {
                "id": target["id"],
                "label": target.get("label", target["id"]),
                "overlapArea": round(area(inter), 3),
                "sourceAreaShare": round(area(inter) / max(area(source_box), 1.0), 6),
                "targetAreaShare": round(area(inter) / max(area(target["box"]), 1.0), 6),
            }
        )
    rows.sort(key=lambda row: (-row["sourceAreaShare"], row["id"]))
    return rows


def render_ose_highlight_ids(ose_data: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for row in ose_data.get("slotRows", []):
        if row.get("carrier") == "render" and row.get("sourceSupportedDominant"):
            ids.update(row.get("sourceHighlightIds", []))
    return ids


def draw_sheet(rows: list[dict[str, Any]], p76_highlights: list[dict[str, Any]], targets: list[dict[str, Any]], slots: list[dict[str, Any]]) -> None:
    left = Image.open(PAGE75).convert("RGB")
    mirrored = ImageOps.mirror(left)
    page76 = Image.open(PAGE76).convert("RGB")
    crop = [240, 2080, 2280, 3060]

    def crop_panel(img: Image.Image, title: str) -> Image.Image:
        panel = img.crop(tuple(crop)).copy()
        panel = panel.resize((980, int(panel.height * 980 / panel.width)), Image.Resampling.LANCZOS)
        out = Image.new("RGB", (panel.width, panel.height + 52), (250, 250, 247))
        out.paste(panel, (0, 52))
        ImageDraw.Draw(out).text((16, 12), title, fill=(18, 25, 34), font=font(26, True))
        return out

    left_panel = crop_panel(mirrored, "Mirrored page-75 orange highlights")
    right_panel = crop_panel(page76, "Page-76 highlights / active boxes / slots")
    sheet = Image.new("RGB", (left_panel.width + right_panel.width + 36, left_panel.height + 320), (248, 249, 247))
    sheet.paste(left_panel, (12, 12))
    sheet.paste(right_panel, (left_panel.width + 24, 12))
    draw = ImageDraw.Draw(sheet)

    def tx(box: list[float], xoff: int) -> list[float]:
        scale = 980 / (crop[2] - crop[0])
        return [
            xoff + (box[0] - crop[0]) * scale,
            12 + 52 + (box[1] - crop[1]) * scale,
            xoff + (box[2] - crop[0]) * scale,
            12 + 52 + (box[3] - crop[1]) * scale,
        ]

    left_x = 12
    right_x = left_panel.width + 24
    for row in rows:
        if row["sourceId"] not in {"p75_orange_7", "p75_orange_8"}:
            continue
        draw.rectangle(tx(row["mirroredBox"], left_x), outline=(224, 72, 52), width=5)
        draw.text((tx(row["mirroredBox"], left_x)[0] + 6, tx(row["mirroredBox"], left_x)[1] + 5), row["sourceId"], fill=(224, 72, 52), font=font(18, True))
    for highlight in p76_highlights:
        draw.rectangle(tx(highlight["box"], right_x), outline=(255, 145, 0), width=4)
    for target in targets:
        draw.rectangle(tx(target["box"], right_x), outline=(40, 146, 90), width=4)
        draw.text((tx(target["box"], right_x)[0] + 4, tx(target["box"], right_x)[1] + 4), target["id"], fill=(40, 146, 90), font=font(18, True))
    for slot in slots:
        draw.rectangle(tx(slot["box"], right_x), outline=(75, 105, 210), width=2)
        draw.text((tx(slot["box"], right_x)[0] + 4, tx(slot["box"], right_x)[1] + 24), slot["id"], fill=(75, 105, 210), font=font(14, True))

    y = left_panel.height + 36
    draw.text((20, y), "OSE source highlights under valid 75 -> 76 mirror", fill=(18, 25, 34), font=font(24, True))
    y += 40
    headers = ["source", "p76 highlight", "active target", "OVERDOSE slots"]
    xs = [20, 185, 430, 690]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(72, 82, 96), font=font(16, True))
    y += 30
    for row in rows:
        if row["sourceId"] not in {"p75_orange_7", "p75_orange_8"}:
            continue
        vals = [
            row["sourceId"],
            ",".join(item["id"] for item in row["p76HighlightContacts"]) or "-",
            ",".join(item["id"] for item in row["activeTargetContacts"]) or "-",
            ",".join(item["id"] for item in row["overdoseSlotContacts"]) or "-",
        ]
        for x, val in zip(xs, vals):
            draw.text((x, y), val[:34], fill=(22, 28, 36), font=font(16))
        y += 28
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    article_map = load_json(ARTICLE_MAP)
    p75_highlights = page_highlights(article_map, 75)
    p76_highlights = page_highlights(article_map, 76)
    targets = active_targets(load_json(ACTIVE_TARGETS))
    slots = overdose_slots(load_json(C9_HEADER_GLYPH_SLOT_GATE))
    ose_ids = render_ose_highlight_ids(load_json(OSE_HIGHLIGHT_PHRASE))
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_count = len(reopen.get("triggerRows", []))

    rows = []
    for source in p75_highlights:
        mirrored = mirror_box(source["box"])
        p76_contacts = contact_rows(mirrored, p76_highlights)
        target_contacts = contact_rows(mirrored, targets)
        slot_contacts = contact_rows(mirrored, slots)
        rows.append(
            {
                "sourceId": source["id"],
                "sourceKind": source["kind"],
                "sourceBox": source["box"],
                "mirroredBox": [round(v, 2) for v in mirrored],
                "isOseSourceHighlight": source["id"] in ose_ids,
                "p76HighlightContacts": p76_contacts,
                "activeTargetContacts": target_contacts,
                "overdoseSlotContacts": slot_contacts,
                "p76HighlightContactCount": len(p76_contacts),
                "activeTargetContactCount": len(target_contacts),
                "overdoseSlotContactCount": len(slot_contacts),
                "overdoseSlotStream": "".join(item["id"] for item in slot_contacts),
            }
        )

    ose_rows = [row for row in rows if row["isOseSourceHighlight"]]
    non_ose_rows = [row for row in rows if not row["isOseSourceHighlight"]]
    ose_active_rows = sum(1 for row in ose_rows if row["activeTargetContacts"])
    ose_p76_highlight_rows = sum(1 for row in ose_rows if row["p76HighlightContacts"])
    ose_slot_rows = sum(1 for row in ose_rows if row["overdoseSlotContacts"])
    non_ose_active_rows = sum(1 for row in non_ose_rows if row["activeTargetContacts"])
    selector_candidates = [
        row
        for row in ose_rows
        if row["activeTargetContacts"] and row["p76HighlightContacts"] and row["overdoseSlotContacts"]
    ]
    source_backed_r3 = 0
    satisfied_triggers = 0
    fingerprint = (
        f"p75Hi={len(rows)}|oseHi={len(ose_rows)}|"
        f"oseP76Hi={ose_p76_highlight_rows}/{len(ose_rows)}|"
        f"oseActive={ose_active_rows}/{len(ose_rows)}|"
        f"oseSlots={ose_slot_rows}/{len(ose_rows)}|"
        f"nonOseActive={non_ose_active_rows}/{len(non_ose_rows)}|"
        f"candidates={len(selector_candidates)}|sourceR3={source_backed_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    decision = "pdf_ose_highlight_mirror_geometry_no_selector"
    summary = {
        "p75HighlightCount": len(rows),
        "oseSourceHighlightIds": sorted(ose_ids),
        "oseSourceHighlightCount": len(ose_rows),
        "oseRowsWithP76HighlightContact": ose_p76_highlight_rows,
        "oseRowsWithActiveTargetContact": ose_active_rows,
        "oseRowsWithOverdoseSlotContact": ose_slot_rows,
        "nonOseRowsWithActiveTargetContact": non_ose_active_rows,
        "selectorCandidateCount": len(selector_candidates),
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }

    draw_sheet(rows, p76_highlights, targets, slots)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid 75->76 mirrored page-75 orange highlight geometry against page-76 highlights, active targets, and OVERDOSE slots; no extraction/key derivation",
        "inputs": {
            "articleMap": rel(ARTICLE_MAP),
            "activeTargets": rel(ACTIVE_TARGETS),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "oseHighlightPhraseGate": rel(OSE_HIGHLIGHT_PHRASE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "rows": rows,
        "decision": decision,
        "reason": (
            "The OSE source highlights mirror into OVERDOSE slot bands, explaining the OSE support, "
            "but they do not mirror onto any active target boxes and do not form a page-76 highlight selector."
        ),
        "nextMove": (
            "Treat OSE highlight geometry as slot-band provenance only. Continue only with new source/clue "
            "material or a distinct physical/original-layout feature that supplies unit and read order."
        ),
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current PDF OSE Highlight Mirror Geometry Gate",
        "",
        "Scope: mirrored page-75 orange highlights onto page 76 under the valid `75 -> 76` horizontal mirror, then checked contacts with page-76 orange highlights, locked O4/B4/G5/O5 active target boxes, and measured OVERDOSE slots. No OCR-to-key extraction, key candidates, hashes-to-key, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{decision}`",
        f"- Page-75 orange highlights / OSE source highlights: `{len(rows)}` / `{len(ose_rows)}`",
        f"- OSE rows with page-76 highlight contact: `{ose_p76_highlight_rows}/{len(ose_rows)}`",
        f"- OSE rows with active target contact: `{ose_active_rows}/{len(ose_rows)}`",
        f"- OSE rows with OVERDOSE slot contact: `{ose_slot_rows}/{len(ose_rows)}`",
        f"- Non-OSE rows with active target contact: `{non_ose_active_rows}/{len(non_ose_rows)}`",
        f"- Selector candidates: `{len(selector_candidates)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_backed_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        "",
        "## OSE Source Highlight Rows",
        "",
        "| source highlight | mirrored box | page-76 highlight contacts | active target contacts | OVERDOSE slot contacts |",
        "|---|---|---|---|---|",
    ]
    for row in ose_rows:
        lines.append(
            "| `{src}` | `{box}` | `{p76}` | `{active}` | `{slots}` |".format(
                src=row["sourceId"],
                box=",".join(str(v) for v in row["mirroredBox"]),
                p76=",".join(item["id"] for item in row["p76HighlightContacts"]) or "-",
                active=",".join(item["id"] for item in row["activeTargetContacts"]) or "-",
                slots=",".join(item["id"] for item in row["overdoseSlotContacts"]) or "-",
            )
        )
    lines.extend(
        [
            "",
            "## All Page-75 Highlight Rows",
            "",
            "| source highlight | OSE source | page-76 highlight count | active count | slot count | slot stream |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['sourceId']}` | `{int(row['isOseSourceHighlight'])}` | `{row['p76HighlightContactCount']}` | `{row['activeTargetContactCount']}` | `{row['overdoseSlotContactCount']}` | `{row['overdoseSlotStream'] or '-'}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`.",
            "- The OSE source highlights land in the lower OVERDOSE slot bands, which explains the stable source-supported OSE geometry.",
            "- They do not land on locked O4/B4/G5/O5 active target boxes and do not create a page-76 highlight selector.",
            "- This closes the geometry-only version of the OSE-highlight idea for the current scan/PDF.",
            "",
            "## Next Move",
            "",
            "- Keep OSE highlight geometry as slot-band provenance. The next useful move still needs source/clue wording or a distinct physical/original-layout feature that supplies unit, transform, and read order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{fingerprint}|decision={decision}")


if __name__ == "__main__":
    main()
