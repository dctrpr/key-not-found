#!/usr/bin/env python3
"""Control rotated active OVERDOSE center-letter words.

This bounded pass checks the tempting short words that appear if the active
O4/B4/G5/O5 OVERDOSE center-slot streams are rotated or reversed. It records
whether any source layer names the required start/rotation rule. It does not
derive key material.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_center_rotation_word_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_center_rotation_word_control.json"
OUT_MD = OUT / "source_packet_center_rotation_word_control.md"
OUT_SHEET = OUT / "source_packet_center_rotation_word_control_sheet.jpg"

INPUTS = {
    "source_packet_active_index_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json",
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "source_packet_active_format_stream_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_format_stream_control/"
    "source_packet_active_format_stream_control.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
    "canonical_plain_article_body": ROOT
    / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    "user_markdown_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "user_annotated_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "plain_article_correction_report": ROOT
    / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json",
}

THEMATIC_WORDS = {"DOVE", "ROSE", "SORE", "EROS"}
LAYOUT_WORDS = {"OVER", "DOSE", "REVO", "ESOD"}
STRICT_START_CUES = [
    "start at",
    "start from",
    "begin at",
    "begin from",
    "read from",
    "rotate",
    "rotation",
    "clockwise",
    "counterclockwise",
    "one step",
    "start point",
    "starting point",
    "first target",
    "last target",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def rotations(stream: str) -> list[dict]:
    rows = []
    for reversed_flag, value in [(False, stream), (True, stream[::-1])]:
        direction = "reverse" if reversed_flag else "forward"
        for shift in range(len(value)):
            rotated = value[shift:] + value[:shift]
            rows.append(
                {
                    "direction": direction,
                    "shift": shift,
                    "stream": rotated,
                    "thematicHits": sorted(word for word in THEMATIC_WORDS if word == rotated),
                    "layoutHits": sorted(word for word in LAYOUT_WORDS if word == rotated),
                }
            )
    return rows


def collect_center_streams(mirrored: dict) -> list[dict]:
    rows = []
    for variant in mirrored.get("variants", []):
        for stream in variant.get("streams", []):
            name = stream.get("name", "")
            if "active_center" not in name:
                continue
            rows.append(
                {
                    "variant": variant.get("name"),
                    "slotLetters": variant.get("slotLetters"),
                    "streamName": name,
                    "stream": stream.get("stream", ""),
                    "targetOrder": stream.get("targetOrder", []),
                    "mirrorGeometry": variant.get("mirrorGeometry"),
                    "reverseLabels": variant.get("reverseLabels"),
                }
            )
    return rows


def cue_hits(texts: dict[str, str]) -> list[dict]:
    rows = []
    for source, text in texts.items():
        lower = text.lower()
        for cue in STRICT_START_CUES:
            if cue in lower:
                rows.append({"source": source, "cue": cue})
    return rows


def draw_sheet(summary: dict, hit_rows: list[dict], cue_rows: list[dict]) -> None:
    width, height = 1740, 940
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

    draw.rectangle((0, 0, width, 96), fill=(26, 31, 42))
    draw.text((24, 18), "Center Rotation Word Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"streams {summary['centerStreamRowCount']} | rotations "
            f"{summary['rotationRowCount']} | thematic hits "
            f"{summary['thematicHitRowCount']} | source cues "
            f"{summary['sourceStartCueHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Rotated/reversed short-word hits", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 330, 580, 720, 820, 960, 1110]
    headers = ["variant", "base", "dir", "shift", "stream", "hits", "meaning"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(hit_rows[:12]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        draw.text((xs[0], y), row["variant"][:36], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["baseStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["direction"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), str(row["shift"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["stream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), ",".join(row["thematicHits"] + row["layoutHits"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y), row["controlMeaning"][:82], fill=(70, 70, 70), font=tiny)
        y += 48

    y += 22
    draw.text((24, y), "Source start-point cue search", fill=(45, 45, 45), font=small)
    y += 30
    if cue_rows:
        for row in cue_rows[:10]:
            draw.text((24, y), f"{row['source']}: {row['cue']}", fill=(70, 70, 70), font=tiny)
            y += 22
    else:
        draw.text((24, y), "No strict start/rotation cue phrase found in checked source witnesses.", fill=(70, 70, 70), font=tiny)
        y += 30

    y += 16
    draw.text((24, y), summary["centerRotationFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    data = {name: load_json(path) for name, path in INPUTS.items() if path.suffix == ".json"}
    texts = {
        name: load_text(path)
        for name, path in INPUTS.items()
        if path.suffix != ".json"
    }
    correction_text = json.dumps(data.get("plain_article_correction_report", {}), ensure_ascii=False)
    texts["plain_article_correction_report"] = correction_text

    index_control = data["source_packet_active_index_slot_control"]
    format_control = data["source_packet_active_format_stream_control"]
    mirrored = data["c9_mirrored_header_glyph_gate"]
    reopen = data["source_packet_reopen_trigger_matrix"]

    center_rows = collect_center_streams(mirrored)
    rotation_rows = []
    for row in center_rows:
        for rotated in rotations(row["stream"]):
            hit = bool(rotated["thematicHits"] or rotated["layoutHits"])
            rotation_rows.append(
                {
                    **row,
                    "baseStream": row["stream"],
                    **rotated,
                    "hasHit": hit,
                    "controlMeaning": "short word appears only after choosing a start/direction/label mode",
                }
            )
    hit_rows = [row for row in rotation_rows if row["hasHit"]]
    thematic_hit_rows = [row for row in hit_rows if row["thematicHits"]]
    layout_hit_rows = [row for row in hit_rows if row["layoutHits"]]
    cue_rows = cue_hits(texts)
    unique_thematic = sorted({word for row in thematic_hit_rows for word in row["thematicHits"]})
    unique_layout = sorted({word for row in layout_hit_rows for word in row["layoutHits"]})

    source_r3 = format_control.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0)
    selector_unlocked = bool(cue_rows) and source_r3 > 0 and triggers > 0

    summary = {
        "centerStreamRowCount": len(center_rows),
        "uniqueCenterStreamCount": len({row["stream"] for row in center_rows}),
        "rotationRowCount": len(rotation_rows),
        "hitRowCount": len(hit_rows),
        "thematicHitRowCount": len(thematic_hit_rows),
        "layoutHitRowCount": len(layout_hit_rows),
        "uniqueThematicHits": unique_thematic,
        "uniqueLayoutHits": unique_layout,
        "doveHitCount": sum(1 for row in thematic_hit_rows if "DOVE" in row["thematicHits"]),
        "sourceStartCueHitCount": len(cue_rows),
        "slotOrderRotationIndex": index_control.get("summary", {}).get("slotOrderRotationIndex"),
        "lineToSlotAffineFitCount": index_control.get("summary", {}).get("lineToSlotAffineFitCount"),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "p75ControlMatchesActiveBlackCount": mirrored.get("summary", {}).get("p75ControlMatchesActiveBlackCount"),
        "mirrorVariantCount": mirrored.get("summary", {}).get("variantCount"),
        "selectorUnlocked": selector_unlocked,
    }
    summary["centerRotationFingerprint"] = (
        f"streams={summary['centerStreamRowCount']}|unique={summary['uniqueCenterStreamCount']}|"
        f"rotRows={summary['rotationRowCount']}|themeHits={summary['thematicHitRowCount']}|"
        f"layoutHits={summary['layoutHitRowCount']}|DOVE={summary['doveHitCount']}|"
        f"cueHits={summary['sourceStartCueHitCount']}|slotRot={summary['slotOrderRotationIndex']}|"
        f"lineSlotFits={summary['lineToSlotAffineFitCount']}|p75match={summary['p75ControlMatchesActiveBlackCount']}/{summary['mirrorVariantCount']}|"
        f"sourceR3={source_r3}|triggers={triggers}/{trigger_count}|selectors={int(selector_unlocked)}"
    )

    decision = {
        "sourcePacketCenterRotationWordControl": "center_rotation_words_controlled_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "Rotating/reversing four-letter OVERDOSE center streams can create tempting "
            "short words such as DOVE, ROSE, SORE, and EROS, but no checked source "
            "witness supplies the required start-point, rotation, or direction rule."
        ),
        "nextMove": (
            "Treat DOVE/ROSE/SORE/EROS center-rotation hits as arbitrary short-word "
            "artifacts. Reopen only if a distinct source supplies a start/rotation "
            "instruction that also survives p75 and mirror/reverse controls."
        ),
    }

    payload = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active OVERDOSE center rotation word control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "centerRows": center_rows,
        "rotationRows": rotation_rows,
        "hitRows": hit_rows,
        "sourceCueRows": cue_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Center Rotation Word Control",
                "",
                f"- Center stream rows checked: `{summary['centerStreamRowCount']}`.",
                f"- Rotation/reversal rows checked: `{summary['rotationRowCount']}`.",
                f"- Thematic short-word hit rows: `{summary['thematicHitRowCount']}` (`{', '.join(unique_thematic) or '-'}`).",
                f"- Layout-word hit rows: `{summary['layoutHitRowCount']}` (`{', '.join(unique_layout) or '-'}`).",
                f"- DOVE hit rows: `{summary['doveHitCount']}`.",
                f"- Source start/rotation cue hits: `{summary['sourceStartCueHitCount']}`.",
                f"- p75 active-black mirror matches: `{summary['p75ControlMatchesActiveBlackCount']}/{summary['mirrorVariantCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['centerRotationFingerprint']}`.",
                "",
                "Decision: keep rotated center words as arbitrary short-word artifacts.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    draw_sheet(summary, hit_rows, cue_rows)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(summary["centerRotationFingerprint"])


if __name__ == "__main__":
    main()
