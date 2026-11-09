#!/usr/bin/env python3
"""Audit the proposed "open your heart" capsule rule.

This bounded pass tests a proposed R3 rule: treat orange/dark highlights as a
closed O-K-K-O capsule and read the unhighlighted bridge between the two dark
spans. It checks uniqueness and downstream instruction value only. It does not
derive keys, hashes, seeds, WIFs, addresses, or run brute force.
"""

from __future__ import annotations

import json
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/open_heart_capsule_rule"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "open_heart_capsule_rule.json"
OUT_MD = OUT / "open_heart_capsule_rule.md"
OUT_SHEET = OUT / "open_heart_capsule_rule_sheet.jpg"

PROPOSAL = Path("r3_candidate_rules.md")
BODY_GRAMMAR = ROOT / "analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json"
OBBO_RECURRENCE = (
    ROOT
    / "analysis_outputs/comparison_articles/active_obbo_quartet_recurrence/"
    "active_obbo_quartet_recurrence.json"
)
SENTENCE_BRIDGE = (
    ROOT
    / "analysis_outputs/plain_text_transcript/sentence_line_highlight_bridge/"
    "sentence_line_highlight_bridge.json"
)
ACTIVE_UNITS = (
    ROOT
    / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/"
    "active_line_unit_reconciliation.json"
)
REOPEN_MATRIX = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
ORIENTATION_CONTROL = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_control_quartets/"
    "source_packet_orientation_control_quartets.json"
)
CANONICAL = ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt"
ACTIVE_OBBO_SHEET = (
    ROOT
    / "analysis_outputs/comparison_articles/active_obbo_quartet_recurrence/"
    "active_obbo_quartet_recurrence_sheet.jpg"
)
PAGE76_CROP_SHEET = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg"

EXTRACTION_ACTION_TERMS = {
    "read",
    "take",
    "extract",
    "decode",
    "select",
    "choose",
    "count",
    "use",
    "order",
    "open",
}
UNIT_TERMS = {
    "word",
    "words",
    "letter",
    "letters",
    "line",
    "lines",
    "edge",
    "edges",
    "font",
    "first",
    "last",
    "left",
    "right",
    "above",
    "below",
    "slot",
    "glyph",
    "order",
    "unit",
}
CONTENT_ACTION_TERMS = {"sell", "mine", "pay", "collateralized", "collateralize"}
TARGET_CONTEXT_TERMS = {
    "bitcoin",
    "bukele",
    "volcano",
    "bonds",
    "imf",
    "sell",
    "heart",
    "shitcoiner",
}
HARD_R3_PHRASES = {
    "private key",
    "take first",
    "take last",
    "read first",
    "read last",
    "extract",
    "decode",
    "encoded",
    "word order",
    "letter order",
    "read the",
    "take the",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("“", '"').replace("”", '"')).strip()


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def hit_terms(text: str, terms: set[str]) -> list[str]:
    tokens = token_set(text)
    return sorted(tokens & terms)


def hard_phrase_hits(text: str) -> list[str]:
    lower = norm(text).lower()
    return sorted(phrase for phrase in HARD_R3_PHRASES if phrase in lower)


def bridge_between(canonical: str, left: str, right: str) -> str:
    """Return canonical text between the first matching left/right phrases."""

    normalized = norm(canonical)
    lookup = normalized.lower()
    left_norm = norm(left)
    right_norm = norm(right)
    left_pos = lookup.find(left_norm.lower())
    if left_pos < 0:
        return ""
    start = left_pos + len(left_norm)
    right_pos = lookup.find(right_norm.lower(), start)
    if right_pos < 0:
        return ""
    return norm(normalized[start:right_pos].strip(" .,:;\"'()[]"))


def classify_bridge(text: str) -> dict[str, Any]:
    actions = hit_terms(text, EXTRACTION_ACTION_TERMS)
    units = hit_terms(text, UNIT_TERMS)
    content_actions = hit_terms(text, CONTENT_ACTION_TERMS)
    context = hit_terms(text, TARGET_CONTEXT_TERMS)
    hard = hard_phrase_hits(text)
    return {
        "wordCount": word_count(text),
        "extractionActionHits": actions,
        "unitHits": units,
        "contentActionHits": content_actions,
        "targetContextHits": context,
        "hardR3PhraseHits": hard,
        "sourceBackedR3": bool(hard or (actions and units)),
        "contentConvergenceOnly": bool(content_actions or context) and not bool(hard or (actions and units)),
    }


def visual_quartet_counts(body: dict[str, Any]) -> dict[str, Any]:
    total_windows = 0
    obbo_windows = 0
    independent_obbo = 0
    issue24_obbo = 0
    per_source: dict[str, dict[str, int]] = {}
    for page in body.get("pageRecords", []):
        source = page.get("source", "unknown")
        per_source.setdefault(source, {"pages": 0, "windows": 0, "obbo": 0})
        per_source[source]["pages"] += 1
        spans = []
        for box in page.get("orangeBoxes", []):
            spans.append({"kind": "O", "box": box})
        for box in page.get("darkBoxes", []):
            spans.append({"kind": "K", "box": box})
        spans.sort(key=lambda row: (row["box"][1], row["box"][0]))
        windows = max(0, len(spans) - 3)
        total_windows += windows
        per_source[source]["windows"] += windows
        for idx in range(windows):
            seq = "".join(row["kind"] for row in spans[idx : idx + 4])
            if seq == "OKKO":
                obbo_windows += 1
                per_source[source]["obbo"] += 1
                if source == "issue24_toxic_af":
                    issue24_obbo += 1
                else:
                    independent_obbo += 1
    return {
        "totalVisualQuartetWindows": total_windows,
        "totalObboWindows": obbo_windows,
        "issue24ObboWindows": issue24_obbo,
        "independentObboWindows": independent_obbo,
        "perSource": per_source,
    }


def known_obbo_bridge_rows(canonical: str, obbo: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in obbo.get("windows", []):
        page = row["page"] + 72 if row.get("source") == "issue24_toxic_af" else row.get("page")
        active_like = bool(row.get("activeLike"))
        if row.get("source") != "issue24_toxic_af":
            continue
        if page == 75 and row.get("windowIndex1") == 2:
            left = "money printers, banking"
            right = "terrorists, stock traders, central bank arsonists"
            bridge = bridge_between(canonical, left, right)
            note = "line-split black control; bridge is empty after canonical normalization"
        elif page == 76 and row.get("windowIndex1") == 2:
            left = "Gotta be this way. Forty years of dumb post-1971 fiat money"
            right = "nonsense"
            bridge = bridge_between(canonical, left, right)
            note = "upper page-76 black line split; bridge is empty after canonical normalization"
        elif page == 76 and row.get("windowIndex1") == 7:
            left = "$1 billion"
            right = "Volcano Bonds"
            bridge = bridge_between(canonical, left, right)
            note = "active lower corridor O4/B4/G5/O5 capsule bridge"
        else:
            left = ""
            right = ""
            bridge = ""
            note = "unclassified OBBO window"

        classified = classify_bridge(bridge)
        rows.append(
            {
                "source": row.get("source"),
                "articlePage": page,
                "windowIndex1": row.get("windowIndex1"),
                "sequence": row.get("sequence"),
                "activeLike": active_like,
                "leftBlack": left,
                "rightBlack": right,
                "bridgeText": bridge,
                "note": note,
                **classified,
            }
        )
    return rows


def known_adjacent_kk_controls(canonical: str) -> list[dict[str, Any]]:
    specs = [
        ("p75_split_black", 75, "money printers, banking", "terrorists, stock traders, central bank arsonists"),
        ("p76_upper_split_black", 76, "Gotta be this way. Forty years of dumb post-1971 fiat money", "nonsense"),
        ("p76_active_bridge", 76, "$1 billion", "Volcano Bonds"),
        ("p78_kk_1", 78, "gargantuanly wasteful", "money printing"),
        ("p78_kk_2", 78, "money printing", "wars to keep it going"),
    ]
    rows = []
    for label, page, left, right in specs:
        bridge = bridge_between(canonical, left, right)
        rows.append(
            {
                "label": label,
                "articlePage": page,
                "leftBlack": left,
                "rightBlack": right,
                "bridgeText": bridge,
                "isActive": label == "p76_active_bridge",
                **classify_bridge(bridge),
            }
        )
    return rows


def source_cue_rows() -> list[dict[str, Any]]:
    canonical = read_text(CANONICAL)
    canonical_norm = norm(canonical).lower()
    cues = [
        {
            "cue": "Open your heart to Bitcoin",
            "source": rel(CANONICAL),
            "present": "open your heart to bitcoin" in canonical_norm,
            "role": "authorizes opening/heart metaphor, but not an explicit word/letter/line unit",
        },
        {
            "cue": "shitcoiner at heart",
            "source": rel(CANONICAL),
            "present": "shitcoiner at heart" in canonical_norm,
            "role": "closes the page-76 heart bracket at the active O5 span",
        },
        {
            "cue": "MAX heart KEISER marker-layer claim",
            "source": rel(PROPOSAL),
            "present": "MAX ♡ KEISER" in read_text(PROPOSAL),
            "role": "external proposal claims marker-layer heart=center; not independently adjudicated in this pass",
        },
    ]
    return cues


def wrap_lines(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1700, 1220
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 17)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    summary = result["summary"]
    draw.rectangle((0, 0, width, 96), fill=(25, 31, 40))
    draw.text((24, 17), "Open-Heart Capsule Rule Audit", fill="white", font=title)
    draw.text((24, 58), summary["fingerprint"], fill=(230, 230, 230), font=tiny)

    y = 124
    draw.text((24, y), "OBBO / capsule windows", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["page", "idx", "active", "left black", "bridge", "words", "R3", "content hits", "note"]
    xs = [24, 88, 142, 228, 520, 1060, 1125, 1195, 1380]
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(result["obboBridgeRows"]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 66), fill=fill)
        values = [
            str(row["articlePage"]),
            str(row["windowIndex1"]),
            "yes" if row["activeLike"] else "no",
            row["leftBlack"][:34],
            row["bridgeText"][:72] or "-",
            str(row["wordCount"]),
            "yes" if row["sourceBackedR3"] else "no",
            ",".join(row["contentActionHits"] + row["targetContextHits"]) or "-",
            row["note"][:36],
        ]
        for x, v in zip(xs, values):
            draw.text((x, y), v, fill=(30, 30, 30), font=tiny)
        y += 72

    y += 18
    draw.text((24, y), "Adjacent K-K bridge controls", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["label", "page", "bridge", "words", "R3", "content/action", "unit"]
    xs = [24, 245, 310, 910, 975, 1045, 1275]
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(result["adjacentKkRows"]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 48), fill=fill)
        values = [
            row["label"],
            str(row["articlePage"]),
            row["bridgeText"][:82] or "-",
            str(row["wordCount"]),
            "yes" if row["sourceBackedR3"] else "no",
            ",".join(row["contentActionHits"] + row["extractionActionHits"]) or "-",
            ",".join(row["unitHits"]) or "-",
        ]
        for x, v in zip(xs, values):
            draw.text((x, y), v, fill=(30, 30, 30), font=tiny)
        y += 54

    y += 20
    draw.text((24, y), "Source cues and decision", fill=(45, 45, 45), font=small)
    y += 30
    for cue in result["sourceCueRows"]:
        line = f"{'PASS' if cue['present'] else 'MISS'}: {cue['cue']} - {cue['role']}"
        draw.text((36, y), line[:150], fill=(35, 35, 35), font=tiny)
        y += 24
    y += 8
    for line in wrap_lines(result["decision"]["reason"], 132):
        draw.text((36, y), line, fill=(35, 35, 35), font=tiny)
        y += 22

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    body = load_json(BODY_GRAMMAR)
    obbo = load_json(OBBO_RECURRENCE)
    sentence = load_json(SENTENCE_BRIDGE)
    active = load_json(ACTIVE_UNITS)
    reopen = load_json(REOPEN_MATRIX)
    orientation = load_json(ORIENTATION_CONTROL)
    canonical = read_text(CANONICAL)

    counts = visual_quartet_counts(body)
    obbo_rows = known_obbo_bridge_rows(canonical, obbo)
    kk_rows = known_adjacent_kk_controls(canonical)
    source_cues = source_cue_rows()

    active_obbo = [row for row in obbo_rows if row["activeLike"]]
    control_obbo = [row for row in obbo_rows if not row["activeLike"]]
    active_bridge = active_obbo[0] if active_obbo else {}
    max_nonactive_obbo_bridge_words = max([row["wordCount"] for row in control_obbo] or [0])
    max_adjacent_kk_bridge_words = max([row["wordCount"] for row in kk_rows if not row["isActive"]] or [0])
    active_unique_substantive = bool(
        active_bridge
        and active_bridge.get("wordCount", 0) >= 5
        and active_bridge.get("wordCount", 0) > max_nonactive_obbo_bridge_words
        and active_bridge.get("wordCount", 0) > max_adjacent_kk_bridge_words
    )
    source_backed_r3 = bool(active_bridge.get("sourceBackedR3"))
    content_only = bool(active_bridge.get("contentConvergenceOnly"))
    satisfied_triggers = reopen.get("summary", {}).get("satisfiedNow", 0)
    trigger_count = reopen.get("triggerCount") or reopen.get("summary", {}).get("triggerCount", 9)

    sentence45 = next((row for row in sentence.get("bridges", []) if row.get("sentenceRow") == 45), {})
    active_records = active.get("records", [])

    if active_unique_substantive and source_backed_r3:
        status = "pass_r3_selector"
    elif active_unique_substantive and content_only:
        status = "partial_unique_selector_no_downstream_r3"
    elif active_unique_substantive:
        status = "partial_unique_selector_no_instruction_terms"
    else:
        status = "fail_not_unique_selector"

    selector_unlocked = status == "pass_r3_selector"
    fingerprint = (
        f"visualQuartets={counts['totalVisualQuartetWindows']}|"
        f"obbo={counts['totalObboWindows']}|issue24Obbo={counts['issue24ObboWindows']}|"
        f"indObbo={counts['independentObboWindows']}|activeBridgeWords={active_bridge.get('wordCount', 0)}|"
        f"maxNonactiveObboBridgeWords={max_nonactive_obbo_bridge_words}|"
        f"maxAdjacentKkBridgeWords={max_adjacent_kk_bridge_words}|uniqueBridge={int(active_unique_substantive)}|"
        f"sourceR3={int(source_backed_r3)}|triggers={satisfied_triggers}/{trigger_count}|"
        f"selector={int(selector_unlocked)}"
    )

    if status == "partial_unique_selector_no_downstream_r3":
        reason = (
            "The proposed capsule operation is a useful partial selector: among the checked OBBO windows, "
            "the lower page-76 active window is the only one with a substantive black-to-black bridge, and "
            "that bridge contains the pre-registered `should sell` convergence. It still does not supply a "
            "source-backed extraction unit/order such as word, letter, line, edge, first/last, or a hard "
            "read/take/extract instruction, so it cannot unlock key material by itself."
        )
    elif status == "pass_r3_selector":
        reason = (
            "The capsule rule uniquely selects the active bridge and the bridge contains source-backed "
            "unit/order wording. This would reopen a narrow downstream extraction pass."
        )
    elif status == "partial_unique_selector_no_instruction_terms":
        reason = (
            "The capsule rule appears unique as a bridge selector, but its selected bridge contains no "
            "downstream instruction terms. Record as a locator only."
        )
    else:
        reason = "The capsule rule does not uniquely select the active bridge against controls."

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "test the proposed open-your-heart O-K-K-O capsule rule using current visual span controls; "
            "no key derivation, hashing, WIF, seed, address, BIP39, or brute force"
        ),
        "inputs": {
            "proposal": str(PROPOSAL),
            "canonical": rel(CANONICAL),
            "body_highlighter_grammar": rel(BODY_GRAMMAR),
            "active_obbo_recurrence": rel(OBBO_RECURRENCE),
            "sentence_line_highlight_bridge": rel(SENTENCE_BRIDGE),
            "active_line_unit_reconciliation": rel(ACTIVE_UNITS),
            "source_packet_reopen_trigger_matrix": rel(REOPEN_MATRIX),
            "source_packet_orientation_control_quartets": rel(ORIENTATION_CONTROL),
            "active_obbo_sheet": rel(ACTIVE_OBBO_SHEET),
            "page76_priority_crop_sheet": rel(PAGE76_CROP_SHEET),
        },
        "rule": {
            "name": "open your heart capsule rule",
            "operation": "for each O-K-K-O visual quartet, read the unhighlighted canonical text between the two K spans",
            "passCondition": "active bridge is uniquely substantive and supplies source-backed extraction unit/order wording",
            "partialCondition": "active bridge is uniquely substantive but supplies only article-context convergence",
        },
        "visualQuartetCounts": counts,
        "existingBroaderYkQuartetControls": {
            "source": rel(ORIENTATION_CONTROL),
            "summary": orientation.get("summary", {}),
            "interpretation": (
                "This existing broader control set supports contiguous YKKY uniqueness "
                "within available full-page Y/K groups, while also showing YKKY is not "
                "unique as an unordered pattern. It is not the proposal's unlocated "
                "`715-quartet` falsifier."
            ),
        },
        "obboBridgeRows": obbo_rows,
        "adjacentKkRows": kk_rows,
        "sourceCueRows": source_cues,
        "activeSentence45": {
            "sentenceText": sentence45.get("sentenceText"),
            "pageLineSpan": sentence45.get("pageLineSpan"),
            "corridorSpan": sentence45.get("corridorSpan"),
            "highlights": sentence45.get("highlights"),
        },
        "activeRecords": active_records,
        "summary": {
            "status": status,
            "selectorUnlocked": selector_unlocked,
            "activeUniqueSubstantiveBridge": active_unique_substantive,
            "sourceBackedR3": source_backed_r3,
            "activeBridgeText": active_bridge.get("bridgeText", ""),
            "activeBridgeWordCount": active_bridge.get("wordCount", 0),
            "maxNonactiveObboBridgeWordCount": max_nonactive_obbo_bridge_words,
            "maxAdjacentKkBridgeWordCount": max_adjacent_kk_bridge_words,
            "activeBridgeContentActionHits": active_bridge.get("contentActionHits", []),
            "activeBridgeTargetContextHits": active_bridge.get("targetContextHits", []),
            "activeBridgeExtractionActionHits": active_bridge.get("extractionActionHits", []),
            "activeBridgeUnitHits": active_bridge.get("unitHits", []),
            "satisfiedReopenTriggers": satisfied_triggers,
            "triggerCount": trigger_count,
            "fingerprint": fingerprint,
        },
        "decision": {
            "openHeartCapsuleRule": status,
            "selectorUnlocked": selector_unlocked,
            "reason": reason,
            "nextMove": (
                "If pursuing this branch, test whether the selected bridge's `should sell` phrase is named by an external/source clue "
                "as a unit/order operation. Without that, keep the capsule rule as a target selector only."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Open-Heart Capsule Rule Audit",
        "",
        "Scope: test the proposed O-K-K-O `open your heart` capsule rule as a source-backed R3 candidate. "
        "No key derivation, hashing, WIF, seed/address checks, BIP39, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Proposal: `{PROPOSAL}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Visual Control Counts",
        "",
        f"- Total visual quartet windows checked from body-highlighter grammar: `{counts['totalVisualQuartetWindows']}`.",
        f"- O-K-K-O / OBBO windows: `{counts['totalObboWindows']}`.",
        f"- Issue 24 OBBO windows: `{counts['issue24ObboWindows']}`.",
        f"- Independent-control OBBO windows: `{counts['independentObboWindows']}`.",
        f"- Existing broader Y/K controls: `{orientation.get('summary', {}).get('fullPageYkCombinationCount', 0)}` full-page combinations, "
        f"`{orientation.get('summary', {}).get('fullPageYkYkkyCombinationCount', 0)}` YKKY combinations, "
        f"`{orientation.get('summary', {}).get('fullPageYkSlidingYkkyCount', 0)}` contiguous sliding YKKY window.",
        f"- Caveat: the proposal's referenced `715-quartet` control set was not located as a named artifact; this pass uses the existing visual/body-highlighter and Y/K quartet controls.",
        "",
        "## OBBO Bridge Rows",
        "",
        "| page | index | active-like | bridge words | source R3 | content hits | bridge text |",
        "|---:|---:|---|---:|---|---|---|",
    ]
    for row in obbo_rows:
        md.append(
            f"| `{row['articlePage']}` | `{row['windowIndex1']}` | `{'yes' if row['activeLike'] else 'no'}` | "
            f"`{row['wordCount']}` | `{'yes' if row['sourceBackedR3'] else 'no'}` | "
            f"`{', '.join(row['contentActionHits'] + row['targetContextHits']) or '-'}` | "
            f"`{row['bridgeText'] or '-'}` |"
        )

    md.extend(
        [
            "",
            "## Adjacent K-K Controls",
            "",
            "| label | page | bridge words | source R3 | content/action hits | unit hits | bridge text |",
            "|---|---:|---:|---|---|---|---|",
        ]
    )
    for row in kk_rows:
        md.append(
            f"| `{row['label']}` | `{row['articlePage']}` | `{row['wordCount']}` | "
            f"`{'yes' if row['sourceBackedR3'] else 'no'}` | "
            f"`{', '.join(row['contentActionHits'] + row['extractionActionHits']) or '-'}` | "
            f"`{', '.join(row['unitHits']) or '-'}` | `{row['bridgeText'] or '-'}` |"
        )

    md.extend(
        [
            "",
            "## Decision",
            "",
            f"- Result: `{status}`.",
            f"- Active bridge uniquely substantive: `{active_unique_substantive}`.",
            f"- Source-backed R3 / selector unlocked: `{source_backed_r3}` / `{selector_unlocked}`.",
            f"- Max non-active OBBO bridge words / adjacent K-K control bridge words: `{max_nonactive_obbo_bridge_words}` / `{max_adjacent_kk_bridge_words}`.",
            f"- Reason: {reason}",
            "",
            "## Next Move",
            "",
            result["decision"]["nextMove"],
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "fingerprint": fingerprint, "report": rel(OUT_MD)}, indent=2))


if __name__ == "__main__":
    main()
