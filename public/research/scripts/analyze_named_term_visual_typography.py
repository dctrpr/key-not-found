#!/usr/bin/env python3
"""Visual/font audit for the named page-76 term ledger.

This pass checks only the small word set produced by the line-offset/named-term
ledger. It combines:
- `Article with Fonts.docm` run state as the font witness;
- high-res page-76 OCR word/character boxes as geometry witness;
- trusted orange/grey highlight boxes as edge-contact witnesses.

No key candidates, hashes, seed phrases, or address checks are generated.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
NAMED_JSON = ROOT / "analysis_outputs/source_audit/named_term_unit_streams/named_term_unit_streams.json"
CANONICAL_JSON = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FONT_AUDIT_JSON = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.json"
REGISTERED_JSON = ROOT / "analysis_outputs/source_audit/registered_76_79_selector.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/named_term_visual_typography"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "named_term_visual_typography.json"
OUT_MD = OUT / "named_term_visual_typography.md"
OUT_OVERLAY = OUT / "named_term_visual_typography_overlay.jpg"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def box_intersection(a: list[float], b: list[float]) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    return (x2 - x1) * (y2 - y1)


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def state_for_run(run: dict) -> str:
    font = run.get("fontAscii") or ""
    if font == "Typeka Mix":
        base = "MIX"
    elif font == "Typeka":
        base = "TYPEKA_BOLD" if run.get("bold") else "TYPEKA"
    else:
        base = font.upper() or "UNKNOWN"
    hl = run.get("highlight")
    return f"{base}+{hl.upper()}" if hl else base


def load_docm_words() -> list[dict]:
    runs = json.loads(RUNS_JSON.read_text())
    audit = json.loads(FONT_AUDIT_JSON.read_text())
    p76_boundary = next(row for row in audit["pageBoundariesByParagraph"] if row["page"] == 76)
    out = []
    for run in runs:
        if not (p76_boundary["paragraphStart"] <= run["paragraphIndex"] <= p76_boundary["paragraphEnd"]):
            continue
        for match in re.finditer(r"[A-Za-z0-9']+", run.get("text", "")):
            token = norm(match.group(0))
            if not token:
                continue
            out.append(
                {
                    "token": token,
                    "text": match.group(0),
                    "runIndex": run["runIndex"],
                    "paragraphIndex": run["paragraphIndex"],
                    "fontAscii": run.get("fontAscii"),
                    "bold": bool(run.get("bold")),
                    "highlight": run.get("highlight"),
                    "state": state_for_run(run),
                    "runText": run.get("text", ""),
                }
            )
    counts: dict[str, int] = defaultdict(int)
    for item in out:
        counts[item["token"]] += 1
        item["occurrence"] = counts[item["token"]]
    for i, item in enumerate(out):
        item["wordOrdinal"] = i
        item["prevState"] = out[i - 1]["state"] if i else ""
        item["nextState"] = out[i + 1]["state"] if i + 1 < len(out) else ""
        item["stateEntry"] = item["state"] != item["prevState"]
        item["stateExit"] = item["state"] != item["nextState"]
    return out


def load_canonical_words() -> tuple[list[dict], dict[str, list[dict]]]:
    data = json.loads(CANONICAL_JSON.read_text())
    page = next(page for page in data["pages"].values() if page["articlePage"] == 76)
    out = []
    counts: dict[str, int] = defaultdict(int)
    by_line: dict[int, list[dict]] = defaultdict(list)
    for word in page["words"]:
        token = norm(word["letters"] or word["text"])
        if not token:
            continue
        counts[token] += 1
        item = {
            "token": token,
            "text": word["text"],
            "lineIndex": word["lineIndex"],
            "wordIndex": word["wordIndex"],
            "occurrence": counts[token],
        }
        out.append(item)
        by_line[word["lineIndex"]].append(item)
    return out, by_line


def load_highres_page() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def highres_rows(page: dict) -> list[dict]:
    rows: list[list[dict]] = []
    for word in sorted(page["words"], key=lambda w: (w["center"][1], w["center"][0])):
        if word["token"] == "overdose":
            continue
        placed = False
        for row in rows:
            if abs(row[0]["center"][1] - word["center"][1]) < 14:
                row.append(word)
                placed = True
                break
        if not placed:
            rows.append([word])
    out = []
    for row in rows:
        row.sort(key=lambda w: w["center"][0])
        out.append(
            {
                "y": sum(w["center"][1] for w in row) / len(row),
                "words": row,
                "tokens": [w["token"] for w in row if w["token"]],
                "box": [
                    min(w["box"][0] for w in row),
                    min(w["box"][1] for w in row),
                    max(w["box"][2] for w in row),
                    max(w["box"][3] for w in row),
                ],
            }
        )
    return out


def best_row_for_line(canonical_line: list[dict], rows: list[dict]) -> dict | None:
    line_tokens = [w["token"] for w in canonical_line]
    if not line_tokens:
        return None
    best = None
    best_score = -1
    for row in rows:
        row_tokens = row["tokens"]
        score = 0
        for tok in set(line_tokens):
            score += min(line_tokens.count(tok), row_tokens.count(tok))
        if score > best_score:
            best = row
            best_score = score
    return best if best_score > 0 else None


def load_trusted_highlights(page: dict) -> list[dict]:
    out = []
    orange_labels = {
        "p76_orange_1": "O1/orange/open-heart line",
        "p76_orange_2": "O2/orange/Bitcoin line",
        "p76_orange_3": "O3/orange/rancid-catnip",
        "p76_orange_4": "O4/orange/buying-the-dip",
        "p76_orange_5": "O5/orange/shitcoiner-heart",
    }
    for h in page["highlights"]:
        out.append({"id": h["id"], "kind": "orange", "label": orange_labels.get(h["id"], h["id"]), "box": h["box"]})

    # Use registered upper-page grey boxes for the three boxes that are known
    # to align with high-res word rows, and lower-page false-positive boxes for
    # the $1B / Volcano highlighted text boxes. The old registered grey_4/5
    # labels are intentionally not reused here because later audits found them
    # unreliable for lower-corridor coordinates.
    registered = json.loads(REGISTERED_JSON.read_text())
    for item in registered["targetGrey"][:3]:
        out.append({"id": item["id"], "kind": "grey", "label": item["label"], "box": item["box"]})

    lower = json.loads(LOWER_MARKS_JSON.read_text())
    for item in lower["analyses"][:2]:
        out.append({"id": f"lower_m{item['index']}", "kind": "grey", "label": item["note"], "box": item["box"]})
    return out


def highres_occurrence_lookup(page: dict) -> dict[tuple[str, int], dict]:
    counts: dict[str, int] = defaultdict(int)
    lookup = {}
    for word in page["words"]:
        token = norm(word.get("token") or word.get("text") or "")
        if not token:
            continue
        counts[token] += 1
        lookup[(token, counts[token])] = word
    return lookup


def approximate_word_from_row(term: str, row: dict | None, canonical_line: list[dict]) -> tuple[dict | None, str]:
    if row is None:
        return None, "no high-res row match"
    term_norm = norm(term)
    for word in row["words"]:
        tok = norm(word.get("token") or word.get("text") or "")
        if tok == term_norm or tok.startswith(term_norm) or term_norm.startswith(tok):
            return word, "row-token fuzzy match"

    best_word = None
    best_ratio = 0.0
    for word in row["words"]:
        tok = norm(word.get("token") or word.get("text") or "")
        if not tok:
            continue
        ratio = SequenceMatcher(None, tok, term_norm).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_word = word
    if best_word is not None and best_ratio >= 0.68:
        return best_word, f"row-token OCR fuzzy match {best_ratio:.2f}"

    # Approximate missing OCR words inside a row by canonical word order and
    # proportional word lengths. This is only used for bad OCR blobs such as
    # the final `shitcoiner at heart` line.
    line_tokens = [w["token"] for w in canonical_line]
    if term_norm not in line_tokens:
        return None, "term not present in canonical line"
    idx = line_tokens.index(term_norm)
    weights = [max(1, len(w["token"])) for w in canonical_line]
    total = sum(weights) + max(0, len(weights) - 1)
    before = sum(weights[:idx]) + idx
    width = weights[idx]
    row_box = row["box"]
    x1 = row_box[0] + (before / total) * (row_box[2] - row_box[0])
    x2 = row_box[0] + ((before + width) / total) * (row_box[2] - row_box[0])
    approx = {
        "id": f"approx_{term_norm}_{row['y']:.1f}",
        "index": None,
        "text": term,
        "token": term_norm,
        "box": [x1, row_box[1], x2, row_box[3]],
        "center": [(x1 + x2) / 2, row["y"]],
        "importance": 0,
        "reasons": ["approx-from-canonical-row"],
    }
    return approx, "approx canonical proportional"


def chars_for_box(page: dict, box: list[float]) -> list[dict]:
    out = []
    for ch in page["chars"]:
        if ch["c"].strip() and box_intersection(ch["box"], box) > 0:
            out.append(ch)
    return sorted(out, key=lambda c: c["x"])


def nearest_char_to_x(chars: list[dict], x: float) -> str:
    if not chars:
        return ""
    return min(chars, key=lambda c: abs(c["x"] - x))["c"]


def highlight_contacts(page: dict, word: dict | None, highlights: list[dict]) -> list[dict]:
    if word is None:
        return []
    wbox = word["box"]
    chars = chars_for_box(page, wbox)
    out = []
    for h in highlights:
        inter = box_intersection(wbox, h["box"])
        if inter <= 0:
            continue
        warea = area(wbox) or 1.0
        edge_letters = []
        for edge_name, x in (("left", h["box"][0]), ("right", h["box"][2])):
            if wbox[0] - 8 <= x <= wbox[2] + 8:
                letter = nearest_char_to_x(chars, x)
                if letter:
                    edge_letters.append({"edge": edge_name, "letter": letter, "distancePx": round(min(abs(x - wbox[0]), abs(x - wbox[2])), 2)})
        out.append(
            {
                "id": h["id"],
                "kind": h["kind"],
                "label": h["label"],
                "overlapFracOfWord": round(inter / warea, 3),
                "edgeLetters": edge_letters,
                "edgeDistancesPx": {
                    "left": round(wbox[0] - h["box"][0], 2),
                    "right": round(h["box"][2] - wbox[2], 2),
                    "top": round(wbox[1] - h["box"][1], 2),
                    "bottom": round(h["box"][3] - wbox[3], 2),
                },
            }
        )
    return out


def main() -> None:
    named = json.loads(NAMED_JSON.read_text())
    canonical_words, canonical_by_line = load_canonical_words()
    docm_words = load_docm_words()
    docm_lookup = {(w["token"], w["occurrence"]): w for w in docm_words}
    page = load_highres_page()
    hlookup = highres_occurrence_lookup(page)
    rows = highres_rows(page)
    highlights = load_trusted_highlights(page)

    records = []
    state_letters_entry = []
    state_letters_exit = []
    highlight_edge_letters = []

    for named_row in named["rows"]:
        line_index = named_row["targetLine"]
        canonical_line = canonical_by_line.get(line_index, [])
        hrow = best_row_for_line(canonical_line, rows)
        for term in named_row["namedTerms"]:
            term_norm = norm(term)
            canon_matches = [w for w in canonical_line if w["token"] == term_norm]
            if not canon_matches:
                continue
            canon = canon_matches[0]
            docm = docm_lookup.get((term_norm, canon["occurrence"]))
            highres, match_note = approximate_word_from_row(term_norm, hrow, canonical_line)
            if highres is None:
                highres = hlookup.get((term_norm, canon["occurrence"]))
                match_note = "token occurrence match" if highres else match_note
            contacts = highlight_contacts(page, highres, highlights)

            if docm and docm["stateEntry"]:
                state_letters_entry.append(term_norm[0])
            if docm and docm["stateExit"]:
                state_letters_exit.append(term_norm[-1])
            for contact in contacts:
                for edge in contact["edgeLetters"]:
                    highlight_edge_letters.append(edge["letter"].lower())

            records.append(
                {
                    "sourceId": named_row["sourceId"],
                    "targetLine": line_index,
                    "term": term_norm,
                    "canonical": canon,
                    "docm": docm,
                    "highres": {
                        "id": highres.get("id") if highres else None,
                        "text": highres.get("text") if highres else None,
                        "token": highres.get("token") if highres else None,
                        "box": [round(v, 2) for v in highres.get("box", [])] if highres else None,
                        "matchNote": match_note,
                    },
                    "highlightContacts": contacts,
                }
            )

    state_counts = defaultdict(int)
    contact_counts = defaultdict(int)
    for rec in records:
        docm = rec.get("docm")
        if docm:
            state_counts[docm["state"]] += 1
        for contact in rec["highlightContacts"]:
            contact_counts[contact["label"]] += 1

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Visual/font audit of named page-76 words only; no key derivation.",
        "records": records,
        "stateCounts": dict(sorted(state_counts.items())),
        "highlightContactCounts": dict(sorted(contact_counts.items())),
        "candidateStreams": {
            "fontStateEntryLetters": "".join(state_letters_entry),
            "fontStateExitLetters": "".join(state_letters_exit),
            "highlightEdgeLetters": "".join(highlight_edge_letters),
        },
        "assessment": [
            "Named terms do not produce a one-letter-per-word typography selector.",
            "The strongest font fact is local and expected: `George Clinton` is Typeka Mix, while the rest of the O2 carrier terms are ordinary Typeka.",
            "`shitcoiners`, `stun/genitals`, the top `bitcoin`, and final `heart` are Typeka-bold or highlighted because they sit inside visible emphasized phrases, not because only one letter is isolated.",
            "Highlight-edge contacts are sparse and mostly boundary contacts around whole highlighted phrases, not a repeated per-word letter selector.",
            "Close named-term Typeka/highlight-edge extraction as a standalone path; keep the overlay as a visual checklist if a later clue names font edges or highlight borders.",
        ],
        "nextMove": "Check whether the unmatched B3+3 landing (`Don't believe me?`) is a deliberate gap/instruction break, or whether another source layer points to it.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    image = Image.open(PAGE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
        small = ImageFont.truetype("Arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    for h in highlights:
        color = (255, 128, 0, 70) if h["kind"] == "orange" else (40, 40, 40, 70)
        outline = (255, 128, 0, 220) if h["kind"] == "orange" else (0, 0, 0, 220)
        draw.rectangle(h["box"], outline=outline, width=3, fill=color)

    state_color = {
        "MIX": (50, 110, 255, 230),
        "TYPEKA": (40, 180, 90, 230),
        "TYPEKA_BOLD": (180, 60, 220, 230),
        "TYPEKA_BOLD+YELLOW": (230, 140, 0, 240),
        "TYPEKA_BOLD+BLACK": (0, 0, 0, 240),
    }
    for rec in records:
        box = rec["highres"]["box"]
        if not box:
            continue
        state = rec["docm"]["state"] if rec.get("docm") else "UNKNOWN"
        color = state_color.get(state, (200, 50, 50, 230))
        draw.rectangle(box, outline=color, width=4)
        label = f"{rec['sourceId']}:{rec['term']}:{state}"
        draw.text((box[0], max(0, box[1] - 22)), label, fill=color, font=small)

    OUT_OVERLAY.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT_OVERLAY, quality=92)

    md = [
        "# Named Term Visual / Typography Audit",
        "",
        "Scope: inspect only the named page-76 words for Typeka state changes and highlight-edge contacts. No key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY}`",
        "",
        "## Summary",
        "",
        f"- Font-state counts: `{result['stateCounts']}`",
        f"- Highlight-contact counts: `{result['highlightContactCounts']}`",
        f"- `fontStateEntryLetters`: `{result['candidateStreams']['fontStateEntryLetters'] or '-'}`",
        f"- `fontStateExitLetters`: `{result['candidateStreams']['fontStateExitLetters'] or '-'}`",
        f"- `highlightEdgeLetters`: `{result['candidateStreams']['highlightEdgeLetters'] or '-'}`",
        "",
        "## Records",
        "",
        "| source | term | line | DOCM state | state boundary | high-res match | highlight contacts |",
        "|---|---|---:|---|---|---|---|",
    ]
    for rec in records:
        docm = rec["docm"] or {}
        boundary = []
        if docm.get("stateEntry"):
            boundary.append("entry")
        if docm.get("stateExit"):
            boundary.append("exit")
        contacts = []
        for contact in rec["highlightContacts"]:
            edges = "".join(f"{e['edge']}={e['letter']}" for e in contact["edgeLetters"])
            contacts.append(f"{contact['label']} {contact['overlapFracOfWord']} {edges}".strip())
        md.append(
            f"| `{rec['sourceId']}` | `{rec['term']}` | {rec['targetLine']} | `{docm.get('state', '-')}` | "
            f"`{','.join(boundary) or '-'}` | `{rec['highres']['text'] or '-'} / {rec['highres']['matchNote']}` | "
            f"`{'; '.join(contacts) or '-'}` |"
        )

    md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    md.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)
    print(OUT_OVERLAY)


if __name__ == "__main__":
    main()
