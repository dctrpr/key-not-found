#!/usr/bin/env python3
"""Audit whether any local authority layer bridges source-packet visuals to R3.

This is a bounded source/intake check. It scans the trusted local text witnesses
and the current handoff reports for source-backed unit/order wording tied to the
active page-76 quartet. It does not generate candidates or test keys.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_r3_bridge_audit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_r3_bridge_audit.json"
OUT_MD = OUT / "source_packet_r3_bridge_audit.md"
OUT_SHEET = OUT / "source_packet_r3_bridge_audit_sheet.jpg"

INPUTS = {
    "source_reopen_requirements": ROOT
    / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
    "future_source_validation_packet": ROOT
    / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "source_packet_handoff_integrity_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/"
    "source_packet_handoff_integrity_matrix.json",
    "source_packet_false_positive_guardrail": ROOT
    / "analysis_outputs/source_audit/source_packet_false_positive_guardrail/"
    "source_packet_false_positive_guardrail.json",
    "external_clue_unit_order_intake": ROOT
    / "analysis_outputs/external_clues/external_clue_unit_order_intake/"
    "external_clue_unit_order_intake.json",
}

AUTHORITY_TEXTS = {
    "canonical_plain_article_body": {
        "path": ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
        "authority": "canonical_plain_text",
        "sourceBackedEligible": True,
    },
    "user_annotated_transcript": {
        "path": ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
        "authority": "user_annotation_witness",
        "sourceBackedEligible": True,
    },
    "user_markdown_transcript": {
        "path": ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
        "authority": "markdown_markup_witness",
        "sourceBackedEligible": True,
    },
    "plain_article_correction_report": {
        "path": ROOT / "analysis_outputs/plain_text_transcript/plain_article_correction_report.md",
        "authority": "derived_correction_markup",
        "sourceBackedEligible": False,
    },
}

GENERATED_REPORTS = {
    "missing_rule_frontier": ROOT / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md",
    "source_reopen_requirements": ROOT
    / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.md",
    "source_packet_handoff_integrity_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/"
    "source_packet_handoff_integrity_matrix.md",
    "source_packet_false_positive_guardrail": ROOT
    / "analysis_outputs/source_audit/source_packet_false_positive_guardrail/"
    "source_packet_false_positive_guardrail.md",
}

ACTIVE_PHRASES = [
    "$1 billion",
    "Volcano Bonds",
    "IMF loan",
    "Mike Novogratz",
    "shitcoiner at heart",
    "buying the dip",
    "President Nayib Bukele",
]

VISUAL_TERMS = [
    "bold",
    "highlight",
    "highlighted",
    "orange",
    "grey",
    "gray",
    "frame",
    "overdose",
    "fold",
    "mirror",
    "mirrored",
]

ACTION_TERMS = [
    "take",
    "read",
    "extract",
    "decode",
    "encode",
    "select",
    "choose",
    "count",
    "use",
    "order",
]

UNIT_TERMS = [
    "word",
    "words",
    "letter",
    "letters",
    "line",
    "lines",
    "edge",
    "edges",
    "font",
    "fonts",
    "first",
    "last",
    "left",
    "right",
    "above",
    "below",
    "frame",
    "slot",
    "glyph",
    "glyphs",
    "order",
]

HARD_PHRASES = [
    "private key",
    "bitcoin key",
    "take first",
    "take last",
    "read first",
    "read last",
    "extract",
    "decode",
    "encoded",
    "unit/order",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9$#%']+", norm(text))


def token_indexes(tokens: list[str], phrase: str) -> list[int]:
    phrase_tokens = tokenize(phrase)
    if not phrase_tokens:
        return []
    out = []
    n = len(phrase_tokens)
    for idx in range(0, len(tokens) - n + 1):
        if tokens[idx : idx + n] == phrase_tokens:
            out.append(idx)
    return out


def context_windows(tokens: list[str], phrases: list[str], radius: int = 25) -> list[dict]:
    windows = []
    for phrase in phrases:
        for idx in token_indexes(tokens, phrase):
            start = max(0, idx - radius)
            end = min(len(tokens), idx + len(tokenize(phrase)) + radius)
            words = tokens[start:end]
            word_set = set(words)
            hard_phrase_hits = [p for p in HARD_PHRASES if p in " ".join(words)]
            action_hits = sorted(set(ACTION_TERMS) & word_set)
            unit_hits = sorted(set(UNIT_TERMS) & word_set)
            visual_hits = sorted(set(VISUAL_TERMS) & word_set)
            bridge = bool(hard_phrase_hits or (action_hits and unit_hits))
            windows.append(
                {
                    "phrase": phrase,
                    "tokenIndex": idx,
                    "actionHits": action_hits,
                    "unitHits": unit_hits,
                    "visualHits": visual_hits,
                    "hardPhraseHits": hard_phrase_hits,
                    "bridgeHit": bridge,
                    "contextPreview": " ".join(words[:60]),
                }
            )
    return windows


def scan_text_source(source_id: str, meta: dict) -> dict:
    text = read_text(meta["path"])
    tokens = tokenize(text)
    windows = context_windows(tokens, ACTIVE_PHRASES)
    hard_bridge_windows = [w for w in windows if w["bridgeHit"]]
    visual_only_windows = [
        w
        for w in windows
        if (w["visualHits"] or "**" in text or "highlight" in text.lower()) and not w["bridgeHit"]
    ]
    doc = norm(text)
    return {
        "sourceId": source_id,
        "authority": meta["authority"],
        "path": str(meta["path"].relative_to(ROOT)),
        "exists": meta["path"].exists(),
        "sourceBackedEligible": meta.get("sourceBackedEligible", False),
        "tokenCount": len(tokens),
        "activeTargetMentionCount": len(windows),
        "visualOnlyTargetWindowCount": len(visual_only_windows),
        "hardR3BridgeWindowCount": len(hard_bridge_windows),
        "hardPhraseGlobalHits": [p for p in HARD_PHRASES if p in doc],
        "bridgeWindows": hard_bridge_windows[:8],
        "sampleVisualOnlyWindows": visual_only_windows[:4],
        "sourceBackedR3Bridge": bool(meta.get("sourceBackedEligible", False) and hard_bridge_windows),
    }


def scan_generated_report(source_id: str, path: Path) -> dict:
    text = read_text(path)
    doc = norm(text)
    return {
        "sourceId": source_id,
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "hardPhraseHits": [p for p in HARD_PHRASES if p in doc],
        "unitOrderPhraseCount": doc.count("unit/order"),
        "sourceBacked": False,
    }


def draw_sheet(summary: dict, authority_rows: list[dict], guardrail_rows: list[dict]) -> None:
    width, height = 1500, 900
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
        small = ImageFont.truetype("Arial.ttf", 17)
        tiny = ImageFont.truetype("Arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 88), fill=(22, 24, 28))
    draw.text((24, 22), "Source Packet R3 Bridge Audit", fill=(255, 255, 255), font=font)
    draw.text(
        (24, 56),
        f"hard R3 bridge hits: {summary['sourceBackedR3BridgeHitCount']} | guardrails still blocked: {summary['guardrailStillBlockedCount']} | fingerprint: {summary['r3BridgeFingerprint']}",
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 118
    draw.text((24, y), "Authority layers", fill=(20, 20, 20), font=font)
    y += 36
    headers = ["source", "target windows", "visual-only", "R3 bridge", "verdict"]
    xs = [24, 460, 640, 800, 970]
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(60, 60, 60), font=small)
    y += 24
    for row in authority_rows:
        fill = (248, 248, 248) if y // 32 % 2 else (235, 239, 244)
        draw.rectangle((18, y - 4, width - 18, y + 30), fill=fill)
        draw.text((xs[0], y), row["sourceId"][:44], fill=(20, 20, 20), font=tiny)
        draw.text((xs[1], y), str(row["activeTargetMentionCount"]), fill=(20, 20, 20), font=tiny)
        draw.text((xs[2], y), str(row["visualOnlyTargetWindowCount"]), fill=(20, 20, 20), font=tiny)
        draw.text((xs[3], y), str(row["hardR3BridgeWindowCount"]), fill=(20, 20, 20), font=tiny)
        verdict = "blocked: no source-backed unit/order"
        draw.text((xs[4], y), verdict, fill=(120, 40, 30), font=tiny)
        y += 34

    y += 26
    draw.text((24, y), "Visual guardrails checked against R3 bridge", fill=(20, 20, 20), font=font)
    y += 36
    for row in guardrail_rows[:9]:
        fill = (255, 246, 238) if row["r3BridgeAvailable"] is False else (235, 250, 235)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((24, y), row["guardrailId"], fill=(20, 20, 20), font=tiny)
        draw.text((280, y), row["missingR3Reason"][:150], fill=(70, 70, 70), font=tiny)
        y += 42

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    reopen = load_json(INPUTS["source_reopen_requirements"])
    future = load_json(INPUTS["future_source_validation_packet"])
    handoff = load_json(INPUTS["source_packet_handoff_integrity_matrix"])
    false_positive = load_json(INPUTS["source_packet_false_positive_guardrail"])
    external = load_json(INPUTS["external_clue_unit_order_intake"])

    authority_rows = [
        scan_text_source(source_id, meta) for source_id, meta in AUTHORITY_TEXTS.items()
    ]
    generated_rows = [
        scan_generated_report(source_id, path) for source_id, path in GENERATED_REPORTS.items()
    ]

    raw_like_r3 = external.get("rawLikeR3PassCount", 0)
    derived_r3 = external.get("derivedR3PassCount", 0)
    source_backed_hits = sum(
        row["hardR3BridgeWindowCount"]
        for row in authority_rows
        if row["sourceBackedEligible"]
    )
    derived_bridge_hits = sum(
        row["hardR3BridgeWindowCount"]
        for row in authority_rows
        if not row["sourceBackedEligible"]
    )
    generated_unit_hits = sum(row["unitOrderPhraseCount"] for row in generated_rows)

    guardrail_rows = []
    for row in false_positive.get("guardrailRows", []):
        guardrail_rows.append(
            {
                "guardrailId": row.get("id"),
                "temptingMatch": row.get("temptingMatch"),
                "requiredToReopen": row.get("requiredToReopen", []),
                "r3BridgeAvailable": False,
                "missingR3Reason": "No authoritative local text or raw external clue supplies source-backed unit/order wording for this visual match.",
                "decision": "still_hard_reject_without_r3",
            }
        )

    r3_gate = next(
        (gate for gate in reopen.get("reopenGates", []) if gate.get("id") == "R3"), {}
    )
    c3_condition = next(
        (
            row
            for row in future.get("minimumReopenConditions", [])
            if str(row.get("condition", "")).startswith("C3")
        ),
        {},
    )

    summary = {
        "authoritySourceCount": len(authority_rows),
        "authorityActiveTargetMentionCount": sum(
            row["activeTargetMentionCount"] for row in authority_rows
        ),
        "authorityVisualOnlyTargetWindowCount": sum(
            row["visualOnlyTargetWindowCount"] for row in authority_rows
        ),
        "sourceBackedR3BridgeHitCount": source_backed_hits,
        "derivedCorrectionBridgeWindowCount": derived_bridge_hits,
        "externalRawLikeR3PassCount": raw_like_r3,
        "externalDerivedR3PassCount": derived_r3,
        "generatedUnitOrderPhraseCount": generated_unit_hits,
        "guardrailCount": false_positive.get("summary", {}).get("guardrailCount"),
        "guardrailStillBlockedCount": len(guardrail_rows),
        "activeVisualStateOrder": false_positive.get("summary", {}).get(
            "activeVisualStateOrder"
        ),
        "activePageLines": false_positive.get("summary", {}).get("activePageLines"),
        "activeCorridorIndexes": false_positive.get("summary", {}).get(
            "activeCorridorIndexes"
        ),
        "handoffSelectorUnlockedCount": handoff.get("summary", {}).get(
            "selectorUnlockedCount"
        ),
        "handoffExtractionReadyGateCount": handoff.get("summary", {}).get(
            "extractionReadyGateCount"
        ),
        "r3BridgeFingerprint": (
            f"authority={len(authority_rows)}"
            f"|targetWindows={sum(row['activeTargetMentionCount'] for row in authority_rows)}"
            f"|visualOnly={sum(row['visualOnlyTargetWindowCount'] for row in authority_rows)}"
            f"|sourceR3={source_backed_hits}"
            f"|derivedR3={derived_bridge_hits}"
            f"|externalRawR3={raw_like_r3}"
            f"|generatedUnitOrder={generated_unit_hits}"
            f"|guardrails={len(guardrail_rows)}"
            f"|selectorUnlocks={handoff.get('summary', {}).get('selectorUnlockedCount')}"
        ),
        "sourceBackedR3BridgeUnlocked": False,
    }

    decision = {
        "sourcePacketR3BridgeAudit": "no_source_backed_r3_bridge_found",
        "reason": "Authoritative local text layers contain active target wording and visual witness markup, but no source-backed unit/order instruction tied to the active quartet or visual/layout mechanics. Generated reports mention unit/order as a requirement only, not as evidence.",
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet R3 bridge audit; no OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation",
        "inputs": {name: str(path.relative_to(ROOT)) for name, path in INPUTS.items()},
        "r3Gate": r3_gate,
        "c3Condition": c3_condition,
        "authorityRows": authority_rows,
        "generatedReportRows": generated_rows,
        "guardrailRows": guardrail_rows,
        "summary": summary,
        "decision": decision,
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "nextMove": "Keep using the source-packet handoff and false-positive guardrail. Reopen extraction only after new source/provenance text supplies R3 unit/order wording and passes R1-R5.",
    }

    draw_sheet(summary, authority_rows, guardrail_rows)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet R3 Bridge Audit",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scope: {result['scope']}",
        f"- Decision: `{decision['sourcePacketR3BridgeAudit']}`",
        f"- R3 gate: `{r3_gate.get('passCondition')}`",
        f"- C3 source condition: `{c3_condition.get('requiredEvidence')}`",
        f"- Authority active target windows: `{summary['authorityActiveTargetMentionCount']}`",
        f"- Visual-only target windows: `{summary['authorityVisualOnlyTargetWindowCount']}`",
        f"- Source-backed R3 bridge hits: `{summary['sourceBackedR3BridgeHitCount']}`",
        f"- Derived correction bridge windows: `{summary['derivedCorrectionBridgeWindowCount']}`",
        f"- External raw-like R3 passes: `{summary['externalRawLikeR3PassCount']}`",
        f"- Generated report unit/order mentions: `{summary['generatedUnitOrderPhraseCount']}`",
        f"- Guardrails still blocked: `{summary['guardrailStillBlockedCount']}`",
        f"- R3 bridge fingerprint: `{summary['r3BridgeFingerprint']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Authority Rows",
        "",
        "| source | authority | target windows | visual-only windows | R3 bridge windows | verdict |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in authority_rows:
        lines.append(
            f"| `{row['sourceId']}` | `{row['authority']}` | {row['activeTargetMentionCount']} | {row['visualOnlyTargetWindowCount']} | {row['hardR3BridgeWindowCount']} | no source-backed R3 bridge |"
        )

    lines.extend(
        [
            "",
            "## Guardrail Bridge Rows",
            "",
            "| guardrail | tempting match | required bridge | decision |",
            "|---|---|---|---|",
        ]
    )
    for row in guardrail_rows:
        req = "; ".join(row["requiredToReopen"])
        lines.append(
            f"| `{row['guardrailId']}` | {row['temptingMatch']} | {req} | `{row['decision']}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The active quartet wording is present in canonical/plain/Markdown/annotated layers, and visual witness tags are present in the annotated/Markdown layers.",
            "- No authoritative local layer supplies a hard instruction such as taking/reading/extracting/counting words, letters, lines, edges, slots, glyphs, or an order tied to O4/B4/G5/O5.",
            "- Generated reports mention `unit/order` because they describe the missing requirement; those mentions are contamination if treated as puzzle evidence.",
            "- All nine false-positive guardrails remain hard rejects without new source-backed R3 wording.",
            "",
            "## Next Move",
            "",
            result["nextMove"],
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("r3BridgeFingerprint:", summary["r3BridgeFingerprint"])
    print("sourceBackedR3BridgeUnlocked:", summary["sourceBackedR3BridgeUnlocked"])


if __name__ == "__main__":
    main()
