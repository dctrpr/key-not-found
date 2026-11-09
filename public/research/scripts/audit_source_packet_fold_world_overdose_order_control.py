#!/usr/bin/env python3
"""Audit fold-world ordering against active OVERDOSE slot streams.

This pass asks whether the 3D fold-view world coordinates add an independent
front/back, depth, or fold-order instruction to the already-known active
O4/B4/G5/O5 OVERDOSE slot geometry. It is a small geometry/control pass only:
no OCR extraction, key derivation, hashing, seed/WIF/address checks, or broad
candidate generation.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_fold_world_overdose_order_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_fold_world_overdose_order_control.json"
OUT_MD = OUT / "source_packet_fold_world_overdose_order_control.md"
OUT_SHEET = OUT / "source_packet_fold_world_overdose_order_control_sheet.jpg"

FOLD_ORDERING = ROOT / "analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering.json"
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
CENTER_ROTATION = ROOT / (
    "analysis_outputs/source_audit/source_packet_center_rotation_word_control/"
    "source_packet_center_rotation_word_control.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_WITNESSES = [
    ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    ROOT / "analysis_outputs/plain_text_transcript/plain_article_correction_report.md",
]

DEPTH_CUE_TERMS = [
    "behind",
    "depth",
    "z-order",
    "z order",
    "fold order",
    "front to back",
    "back to front",
    "front/back",
]
INSTRUCTION_TERMS = [
    "take",
    "read",
    "order",
    "first",
    "last",
    "line",
    "letter",
    "word",
    "slot",
    "fold",
    "mirror",
    "depth",
    "front",
    "back",
]
KNOWN_CENTER_STREAMS = {"OVED", "VEDO"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def dist(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def rotations(text: str) -> list[str]:
    return [text[i:] + text[:i] for i in range(len(text))]


def rev_rotations(text: str) -> list[str]:
    rev = text[::-1]
    return rotations(rev)


def source_cue_rows() -> list[dict]:
    rows = []
    for path in SOURCE_WITNESSES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        hits = [term for term in DEPTH_CUE_TERMS if term in text]
        if hits:
            rows.append({"path": rel(path), "hits": hits})
    return rows


def build_rows() -> tuple[list[dict], dict]:
    fold = load_json(FOLD_ORDERING)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    active_rows = {row["id"]: row for row in active_index.get("activeRows", [])}
    anchors = {}
    for anchor in fold.get("activeAnchors", []):
        row = active_rows.get(anchor["id"], {}).copy()
        row.update(
            {
                "world": anchor["world"],
                "foldCenter": anchor["center"],
                "foldLabel": anchor["label"],
            }
        )
        anchors[anchor["id"]] = row

    page76_fold_center = fold.get("foldPositionsFromViewer", {}).get("76", [0, 0, 0])[:3]
    p78_fold_center = fold.get("foldPositionsFromViewer", {}).get("78", [0, 0, 0])[:3]

    order_specs = [
        ("page_line_top_to_bottom", lambda r: (r["pageLine"], r["centerX"])),
        ("page_x_left_to_right", lambda r: (r["centerX"], r["pageLine"])),
        ("fold_world_x_left_to_right", lambda r: (r["world"][0], r["world"][1])),
        ("fold_world_y_low_to_high", lambda r: (r["world"][1], r["world"][0])),
        ("fold_world_y_high_to_low", lambda r: (-r["world"][1], r["world"][0])),
        ("fold_depth_z_front_to_back_low_to_high", lambda r: (r["world"][2], r["world"][0])),
        ("fold_depth_z_back_to_front_high_to_low", lambda r: (-r["world"][2], r["world"][0])),
        (
            "distance_from_page76_fold_center_near_to_far",
            lambda r: (dist(r["world"], page76_fold_center), r["pageLine"]),
        ),
        (
            "distance_from_p78_pair_center_near_to_far",
            lambda r: (dist(r["world"], p78_fold_center), r["pageLine"]),
        ),
    ]

    rows = []
    for name, key in order_specs:
        ordered = sorted(anchors.values(), key=key)
        stream = "".join(row["centerSlotLetter"] for row in ordered)
        state_stream = "".join(row["visualState"] for row in ordered)
        color_stream = "".join("O" if row["color"] == "orange" else "B" for row in ordered)
        short_ids = " ".join(row["shortId"] for row in ordered)
        variants = sorted(set(rotations(stream) + rev_rotations(stream)))
        instruction_hits = sorted(
            {
                term.upper()
                for variant in variants
                for term in INSTRUCTION_TERMS
                if term.upper() in variant
            }
        )
        layout_hits = sorted({word for word in ["OVER", "DOSE"] if word in variants})
        thematic_hits = sorted({word for word in ["DOVE", "ROSE", "SORE", "EROS"] if word in variants})
        rows.append(
            {
                "orderName": name,
                "shortIds": short_ids,
                "centerSlotStream": stream,
                "stateStream": state_stream,
                "colorStream": color_stream,
                "rotationsAndReversals": variants,
                "isKnownPageOrXStream": stream in KNOWN_CENTER_STREAMS,
                "instructionHits": instruction_hits,
                "layoutHits": layout_hits,
                "thematicHits": thematic_hits,
            }
        )
    return rows, {
        "foldOrdering": fold,
        "activeIndexSlot": active_index,
        "page76FoldCenter": page76_fold_center,
        "p78FoldCenter": p78_fold_center,
    }


def draw_sheet(summary: dict, rows: list[dict]) -> None:
    width, height = 1840, 1040
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 104), fill=(25, 31, 42))
    draw.text((24, 18), "Fold-World OVERDOSE Order Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"orders {summary['orderCount']} | unique streams {summary['uniqueStreamCount']} | "
            f"new fold streams {summary['newFoldOnlyStreamsCsv']} | source depth cues {summary['sourceDepthCueHitCount']} | "
            f"R3/triggers {summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 132
    draw.text((24, y), "Active O4/B4/G5/O5 order streams in page and fold-world coordinates", fill=(45, 45, 45), font=small)
    y += 34
    xs = [24, 430, 620, 750, 880, 1010, 1170, 1360, 1530]
    headers = ["order", "targets", "slots", "state", "color", "known", "layout", "theme", "instruction"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 46), fill=fill)
        draw.text((xs[0], y), row["orderName"][:52], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["shortIds"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["centerSlotStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["stateStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["colorStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), str(row["isKnownPageOrXStream"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y), ",".join(row["layoutHits"]) or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[7], y), ",".join(row["thematicHits"]) or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[8], y), ",".join(row["instructionHits"]) or "-", fill=(30, 30, 30), font=tiny)
        y += 52

    y += 20
    draw.text((24, y), summary["foldWorldOverdoseOrderFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    rows, _context = build_rows()
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    center_rotation = load_json(CENTER_ROTATION)
    source_cues = source_cue_rows()
    unique_streams = sorted({row["centerSlotStream"] for row in rows})
    known_stream_rows = [row for row in rows if row["isKnownPageOrXStream"]]
    new_streams = sorted(set(unique_streams) - KNOWN_CENTER_STREAMS)
    instruction_rows = [row for row in rows if row["instructionHits"]]
    layout_rows = [row for row in rows if row["layoutHits"]]
    thematic_rows = [row for row in rows if row["thematicHits"]]
    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0
    summary = {
        "orderCount": len(rows),
        "uniqueStreamCount": len(unique_streams),
        "uniqueStreamsCsv": ",".join(unique_streams),
        "knownPageOrXStreamOrderCount": len(known_stream_rows),
        "newFoldOnlyStreamsCsv": ",".join(new_streams),
        "instructionHitOrderCount": len(instruction_rows),
        "layoutHitOrderCount": len(layout_rows),
        "thematicHitOrderCount": len(thematic_rows),
        "sourceDepthCueHitCount": len(source_cues),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "priorCenterRotationThematicHitRowCount": center_rotation.get("summary", {}).get(
            "thematicHitRowCount"
        ),
        "selectorUnlocked": bool(instruction_rows and source_r3 > 0 and triggers > 0),
    }
    summary["foldWorldOverdoseOrderFingerprint"] = (
        f"orders={summary['orderCount']}|unique={summary['uniqueStreamCount']}|"
        f"streams={summary['uniqueStreamsCsv']}|knownOrders={summary['knownPageOrXStreamOrderCount']}|"
        f"new={summary['newFoldOnlyStreamsCsv']}|instructionRows={summary['instructionHitOrderCount']}|"
        f"layoutRows={summary['layoutHitOrderCount']}|themeRows={summary['thematicHitOrderCount']}|"
        f"sourceDepthCues={summary['sourceDepthCueHitCount']}|sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketFoldWorldOverdoseOrderControl": "fold_world_order_does_not_unlock_overdose_selector",
        "selectorUnlocked": summary["selectorUnlocked"],
        "reason": (
            "Fold-world x/depth/distance order only permutes the same four active OVERDOSE center "
            "slot letters. The fold-only new streams are not instruction/layout terms, and source "
            "witnesses do not name a front/back/depth order rule."
        ),
        "nextMove": (
            "Keep fold-world order as source-validation/orientation context only. Reopen extraction "
            "only with new source-backed wording that names fold depth, front/back, or OVERDOSE slot order."
        ),
    }
    draw_sheet(summary, rows)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "fold-world active quartet OVERDOSE order control; no extraction or candidate generation",
        "inputs": {
            "foldOrdering": rel(FOLD_ORDERING),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "centerRotationControl": rel(CENTER_ROTATION),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourceWitnesses": [rel(path) for path in SOURCE_WITNESSES if path.exists()],
        },
        "orderRows": rows,
        "sourceDepthCueRows": source_cues,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Fold-World OVERDOSE Order Control",
                "",
                f"- Fold/page order modes checked: `{summary['orderCount']}`.",
                f"- Unique active center-slot streams: `{summary['uniqueStreamsCsv']}`.",
                f"- Known page/x stream order rows: `{summary['knownPageOrXStreamOrderCount']}`.",
                f"- Fold-only new streams: `{summary['newFoldOnlyStreamsCsv']}`.",
                f"- Instruction-hit order rows: `{summary['instructionHitOrderCount']}`.",
                f"- Layout-hit / thematic-hit order rows: `{summary['layoutHitOrderCount']}` / `{summary['thematicHitOrderCount']}`.",
                f"- Source depth/front/back cue hits: `{summary['sourceDepthCueHitCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['foldWorldOverdoseOrderFingerprint']}`.",
                "",
                "Order rows:",
                "",
            ]
            + [
                (
                    f"- `{row['orderName']}`: targets `{row['shortIds']}`, slots `{row['centerSlotStream']}`, "
                    f"state `{row['stateStream']}`, color `{row['colorStream']}`, "
                    f"layout `{','.join(row['layoutHits']) or '-'}`, theme `{','.join(row['thematicHits']) or '-'}`, "
                    f"instruction `{','.join(row['instructionHits']) or '-'}`."
                )
                for row in rows
            ]
            + [
                "",
                "Decision: fold-world active target order does not reopen OVERDOSE-slot extraction.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
