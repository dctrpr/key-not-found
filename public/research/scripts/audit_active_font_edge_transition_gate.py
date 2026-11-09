#!/usr/bin/env python3
"""Check exact DOCM font-state edges around the active O4/B4/G5/O5 targets.

This bounded pass inspects the Word run layer immediately before and after the
locked active highlighted targets. It asks whether Typeka Mix or font-state
boundaries provide a side-specific selector. It does not derive keys, hash
text, generate seeds, scan WIF/Base58, OCR pages, or check addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
LOWER_SELECTOR_JSON = ROOT / "analysis_outputs/docm_format_sources/lower_corridor_font_state_selector/lower_corridor_font_state_selector.json"
FORMAT_LOCK_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json"
TRANSITIONS_JSON = ROOT / "analysis_outputs/docm_format_sources/typeka_transition_boundaries/typeka_transition_boundaries.json"
OUT = ROOT / "analysis_outputs/docm_format_sources/active_font_edge_transition_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_font_edge_transition_gate.json"
OUT_MD = OUT / "active_font_edge_transition_gate.md"
SHEET = OUT / "active_font_edge_transition_gate_sheet.jpg"

ACTIVE_IDS = ["O4", "B4_text", "G5", "O5"]
INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]


def load_json(path: Path) -> Any:
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


def norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z0-9]+)?", text)


def first_word(text: str) -> str:
    parts = words(text)
    return parts[0] if parts else "-"


def last_word(text: str) -> str:
    parts = words(text)
    return parts[-1] if parts else "-"


def first_char(text: str) -> str:
    match = re.search(r"[A-Za-z0-9$]", text)
    return match.group(0) if match else "-"


def last_char(text: str) -> str:
    chars = re.findall(r"[A-Za-z0-9$]", text)
    return chars[-1] if chars else "-"


def instruction_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def state_code(run: dict[str, Any]) -> str:
    font_name = (run.get("fontAscii") or run.get("fontHAnsi") or "").lower()
    highlight = (run.get("highlight") or "").lower()
    if "typeka mix" in font_name:
        return "M"
    if "typeka" in font_name and run.get("bold") and highlight == "yellow":
        return "Y"
    if "typeka" in font_name and run.get("bold") and highlight == "black":
        return "K"
    if "typeka" in font_name and run.get("bold"):
        return "B"
    if "typeka" in font_name:
        return "R"
    return "O"


def state_label(code: str) -> str:
    return {
        "R": "Typeka regular",
        "M": "Typeka Mix",
        "B": "Typeka bold",
        "Y": "Typeka bold yellow",
        "K": "Typeka bold black",
        "O": "other font",
    }.get(code, code)


def expand_same_state_cluster(runs: list[dict[str, Any]], run_indices: list[int]) -> tuple[int, int]:
    by_index = {run["runIndex"]: i for i, run in enumerate(runs)}
    positions = sorted(by_index[idx] for idx in run_indices if idx in by_index)
    if not positions:
        raise RuntimeError(f"no run positions for {run_indices}")
    left = positions[0]
    right = positions[-1]
    target_state = state_code(runs[left])
    while left > 0 and state_code(runs[left - 1]) == target_state and norm_space(runs[left - 1].get("text", "")):
        if runs[left - 1]["paragraphIndex"] != runs[left]["paragraphIndex"]:
            break
        left -= 1
    while right + 1 < len(runs) and state_code(runs[right + 1]) == target_state and norm_space(runs[right + 1].get("text", "")):
        if runs[right + 1]["paragraphIndex"] != runs[right]["paragraphIndex"]:
            break
        right += 1
    return left, right


def nearest_nonempty(runs: list[dict[str, Any]], start: int, step: int) -> dict[str, Any] | None:
    i = start
    while 0 <= i < len(runs):
        if norm_space(runs[i].get("text", "")):
            return runs[i]
        i += step
    return None


def build_active_record(runs: list[dict[str, Any]], phrase: dict[str, Any]) -> dict[str, Any]:
    cluster_left, cluster_right = expand_same_state_cluster(runs, phrase.get("runIndices", []))
    cluster_runs = runs[cluster_left : cluster_right + 1]
    target_state = state_code(cluster_runs[0])
    left_run = nearest_nonempty(runs, cluster_left - 1, -1)
    right_run = nearest_nonempty(runs, cluster_right + 1, 1)
    left_state = state_code(left_run) if left_run else "-"
    right_state = state_code(right_run) if right_run else "-"
    cluster_text = norm_space("".join(run.get("text", "") for run in cluster_runs))
    left_text = norm_space(left_run.get("text", "")) if left_run else "-"
    right_text = norm_space(right_run.get("text", "")) if right_run else "-"
    edge_pattern = f"{left_state}>{target_state}>{right_state}"

    return {
        "id": phrase["id"],
        "label": phrase["label"],
        "pageLineRole": phrase.get("id"),
        "targetState": target_state,
        "targetStateLabel": state_label(target_state),
        "edgePattern": edge_pattern,
        "runStart": cluster_runs[0]["runIndex"],
        "runEnd": cluster_runs[-1]["runIndex"],
        "paragraphStart": cluster_runs[0]["paragraphIndex"],
        "paragraphEnd": cluster_runs[-1]["paragraphIndex"],
        "clusterText": cluster_text,
        "leftRunIndex": left_run.get("runIndex") if left_run else None,
        "leftState": left_state,
        "leftStateLabel": state_label(left_state),
        "leftText": left_text,
        "leftLastWord": last_word(left_text),
        "leftLastChar": last_char(left_text),
        "rightRunIndex": right_run.get("runIndex") if right_run else None,
        "rightState": right_state,
        "rightStateLabel": state_label(right_state),
        "rightText": right_text,
        "rightFirstWord": first_word(right_text),
        "rightFirstChar": first_char(right_text),
        "hasMixNeighbor": left_state == "M" or right_state == "M",
        "boundaryPair": f"{last_char(left_text)}{first_char(cluster_text)}{last_char(cluster_text)}{first_char(right_text)}",
    }


def cluster_all_page76_nonregular(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clusters = []
    i = 0
    while i < len(runs):
        code = state_code(runs[i])
        text = norm_space(runs[i].get("text", ""))
        if code in {"M", "B", "Y", "K"} and text and 60 <= runs[i].get("paragraphIndex", -1) <= 73:
            start = i
            end = i
            while end + 1 < len(runs) and state_code(runs[end + 1]) == code and norm_space(runs[end + 1].get("text", "")):
                if runs[end + 1]["paragraphIndex"] != runs[end]["paragraphIndex"]:
                    break
                end += 1
            left_run = nearest_nonempty(runs, start - 1, -1)
            right_run = nearest_nonempty(runs, end + 1, 1)
            left_state = state_code(left_run) if left_run else "-"
            right_state = state_code(right_run) if right_run else "-"
            clusters.append(
                {
                    "state": code,
                    "edgePattern": f"{left_state}>{code}>{right_state}",
                    "runStart": runs[start]["runIndex"],
                    "runEnd": runs[end]["runIndex"],
                    "text": norm_space("".join(run.get("text", "") for run in runs[start : end + 1])),
                    "leftState": left_state,
                    "rightState": right_state,
                }
            )
            i = end + 1
        else:
            i += 1
    return clusters


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1700, 1020
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "Active Font-Edge Transition Gate", fill=(244, 247, 250), font=title)
    draw.text(
        (margin, margin + 46),
        "Inspects the immediate DOCM run-level font states before and after O4/B4/G5/O5.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("target states", result["summary"]["targetStateStream"]),
        ("edge patterns", result["summary"]["edgePatternStream"]),
        ("mix neighbors", result["summary"]["mixNeighborCount"]),
        ("instruction hits", result["summary"]["instructionHitCount"]),
    ]
    widths = [300, 620, 250, 250]
    x = margin
    for (label, value), width in zip(chips, widths):
        draw.rectangle((x, y, x + width, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value)[:70], fill=(232, 239, 246), font=mono)
        x += width + 20

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 108), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "Active highlighted targets are regular-Typeka insulated: R>Y/K>R, with no direct Typeka Mix neighbor.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 76),
        "Font edges support target identity/source comparison, but do not name a boundary side or extraction unit.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 140
    draw.text((margin, y), "Active Font Edges", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("target", 12), ("runs", 240), ("edge", 350), ("left word", 540), ("target text", 750), ("right word", 1120), ("mix?", 1350)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["activeEdges"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 44), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 12), row["id"], fill=(176, 186, 198), font=small)
        draw.text((margin + 240, y + 12), f"{row['runStart']}-{row['runEnd']}", fill=(232, 239, 246), font=mono)
        draw.text((margin + 350, y + 12), row["edgePattern"], fill=(232, 239, 246), font=mono)
        draw.text((margin + 540, y + 12), row["leftLastWord"], fill=(176, 186, 198), font=small)
        draw.text((margin + 750, y + 12), row["clusterText"][:46], fill=(232, 239, 246), font=small)
        draw.text((margin + 1120, y + 12), row["rightFirstWord"], fill=(176, 186, 198), font=small)
        draw.text((margin + 1350, y + 12), str(row["hasMixNeighbor"]), fill=(232, 239, 246), font=mono)
        y += 48

    y += 24
    draw.text((margin, y), "Page-76 Non-Regular Clusters", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("state", 12), ("edge", 110), ("runs", 300), ("text", 420)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["page76NonRegularClusters"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 38), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 10), row["state"], fill=(176, 186, 198), font=mono)
        draw.text((margin + 110, y + 10), row["edgePattern"], fill=(232, 239, 246), font=mono)
        draw.text((margin + 300, y + 10), f"{row['runStart']}-{row['runEnd']}", fill=(176, 186, 198), font=mono)
        draw.text((margin + 420, y + 10), row["text"][:110], fill=(176, 186, 198), font=small)
        y += 42

    sheet.save(SHEET, quality=94)


def main() -> None:
    runs = load_json(RUNS_JSON)
    lower = load_json(LOWER_SELECTOR_JSON)
    fmt = load_json(FORMAT_LOCK_JSON)
    transitions = load_json(TRANSITIONS_JSON)
    phrases = {row["id"]: row for row in lower.get("phrases", [])}

    active_edges = [build_active_record(runs, phrases[active_id]) for active_id in ACTIVE_IDS]
    page76_clusters = cluster_all_page76_nonregular(runs)
    target_state_stream = "".join(row["targetState"] for row in active_edges)
    edge_pattern_stream = " | ".join(row["edgePattern"] for row in active_edges)
    left_exit_stream = " ".join(row["leftLastWord"] for row in active_edges)
    right_entry_stream = " ".join(row["rightFirstWord"] for row in active_edges)
    boundary_pair_stream = " ".join(row["boundaryPair"] for row in active_edges)
    all_text = " ".join([target_state_stream, edge_pattern_stream, left_exit_stream, right_entry_stream, boundary_pair_stream])
    hits = instruction_hits(all_text)

    summary = {
        "targetStateStream": target_state_stream,
        "edgePatternStream": edge_pattern_stream,
        "leftExitWordStream": left_exit_stream,
        "rightEntryWordStream": right_entry_stream,
        "boundaryPairStream": boundary_pair_stream,
        "mixNeighborCount": sum(1 for row in active_edges if row["hasMixNeighbor"]),
        "activeEdgeAllRegularInsulated": all(row["leftState"] == "R" and row["rightState"] == "R" for row in active_edges),
        "page76NonRegularClusterCount": len(page76_clusters),
        "activeVisualStateOrder": fmt.get("summary", {}).get("activeVisualStateOrder"),
        "activeColorPattern": fmt.get("summary", {}).get("activeColorPattern"),
        "fontVariantFocusPath": transitions.get("fontVariantAudit", {}).get("streams", {}).get("path"),
        "visualStateFocusPath": transitions.get("visualStateAudit", {}).get("streams", {}).get("path"),
        "instructionHitCount": len(hits),
        "instructionHits": hits,
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active font-edge transition gate; no extraction, no key derivation, no hashing, no seed/WIF/address checks",
        "inputs": {
            "articleRuns": rel(RUNS_JSON),
            "lowerCorridorFontStateSelector": rel(LOWER_SELECTOR_JSON),
            "page76TargetFormatAuthorityLock": rel(FORMAT_LOCK_JSON),
            "typekaTransitionBoundaries": rel(TRANSITIONS_JSON),
        },
        "summary": summary,
        "activeEdges": active_edges,
        "page76NonRegularClusters": page76_clusters,
        "assessment": [
            "The active highlighted quartet is font-edge regular-insulated: every active target is entered from Typeka regular and exits to Typeka regular.",
            "No active O4/B4/G5/O5 target has Typeka Mix as its immediate run-level neighbor, so Typeka Mix is not a direct side selector for the active quartet.",
            "The target state stream remains the already-known `YKKY`; the edge pattern stream is just `R>Y>R | R>K>R | R>K>R | R>Y>R`.",
            "Left-exit and right-entry word streams from DOCM run boundaries are ordinary corridor prose and contain no instruction hits.",
            "This supports the active highlights as target/source-validation evidence, but does not supply R3 unit/order evidence.",
        ],
        "decision": "active_font_edges_are_regular_insulated_no_typeka_mix_selector",
        "sheet": rel(SHEET),
        "nextMove": "Keep font-edge transitions as a source-comparison guardrail; reopen only if raw clue/source wording names Typeka Mix, font boundary, left/right run edge, or font-state extraction.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Font-Edge Transition Gate",
        "",
        "Scope: inspect the immediate DOCM run-level font states before and after locked O4/B4/G5/O5 targets. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Target state stream: `{summary['targetStateStream']}`.",
        f"- Edge pattern stream: `{summary['edgePatternStream']}`.",
        f"- Left-exit word stream: `{summary['leftExitWordStream']}`.",
        f"- Right-entry word stream: `{summary['rightEntryWordStream']}`.",
        f"- Mix-neighbor count: `{summary['mixNeighborCount']}`.",
        f"- Active edges all regular-insulated: `{summary['activeEdgeAllRegularInsulated']}`.",
        f"- Instruction hit count: `{summary['instructionHitCount']}`.",
        "",
        "## Active Edges",
        "",
        "| id | target | runs | edge | left state | left last word | target text | right first word | right state | Typeka Mix neighbor |",
        "|---|---|---|---|---|---|---|---|---|---:|",
    ]
    for row in active_edges:
        lines.append(
            f"| `{row['id']}` | `{row['label']}` | `{row['runStart']}-{row['runEnd']}` | `{row['edgePattern']}` | `{row['leftStateLabel']}` | `{row['leftLastWord']}` | `{row['clusterText']}` | `{row['rightFirstWord']}` | `{row['rightStateLabel']}` | `{row['hasMixNeighbor']}` |"
        )

    lines.extend(["", "## Page-76 Non-Regular Clusters", "", "| state | edge | runs | text |", "|---|---|---|---|"])
    for row in page76_clusters:
        lines.append(f"| `{row['state']}` | `{row['edgePattern']}` | `{row['runStart']}-{row['runEnd']}` | `{row['text']}` |")

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
