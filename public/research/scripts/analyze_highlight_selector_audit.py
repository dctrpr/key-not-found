#!/usr/bin/env python3
"""Audit exact high-res highlighted spans for simple selector-like streams.

This is intentionally not a key-generation script. It checks whether the
manually verified highlight text, combined with the Markdown bold markup, gives
plain low-parameter instructions such as first letters, last letters, lengths,
or bold-highlight intersections.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
GREY = ROOT / "analysis_outputs/highlight_audit/highres_manual_grey_reading.json"
OUT_JSON = ROOT / "analysis_outputs/highlight_audit/highlight_selector_audit.json"
OUT_MD = ROOT / "analysis_outputs/highlight_audit/highlight_selector_audit.md"


COMMON_SELECTOR_WORDS = [
    "TAKE",
    "READ",
    "LEFT",
    "RIGHT",
    "MIRROR",
    "FOLD",
    "PAGE",
    "LINE",
    "WORD",
    "WORDS",
    "LETTER",
    "LETTERS",
    "FIRST",
    "LAST",
    "BOLD",
    "ORANGE",
    "BLACK",
    "GREY",
    "GRAY",
    "KEY",
    "USE",
    "LAYER",
    "ONE",
    "VOLCANO",
    "BONDS",
    "DIP",
    "BUY",
    "IMF",
    "EL",
    "SALVADOR",
    "BITCOIN",
    "TOXIC",
]


def norm_word(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def words(text: str) -> list[str]:
    # Split on whitespace first so contractions like `It’s`, `Don't`, and
    # then split hyphenated compounds to match the canonical word model.
    text = re.sub(r"[-‐‑‒–—]", " ", text)
    return [w for w in (norm_word(x) for x in text.split()) if w]


def letters(text: str) -> str:
    return re.sub(r"[^A-Za-z]+", "", text)


def load_spans() -> list[dict]:
    with ORANGE.open() as f:
        orange = json.load(f)
    with GREY.open() as f:
        grey = json.load(f)

    spans = []
    for span in orange["combinedOrangeSpans"]:
        text = span["text"]
        if text.startswith("["):
            continue
        spans.append({"color": "orange", "page": span["page"], "text": text})
    for span in grey["combinedGreyBlackSpans"]:
        spans.append({"color": "grey_black", "page": span["page"], "text": span["text"]})
    return spans


def page_by_article(canonical: dict) -> dict[int, dict]:
    return {page["articlePage"]: page for page in canonical["pages"].values()}


def find_span_words(page: dict, phrase: str) -> tuple[list[dict], str]:
    phrase_words = words(phrase)
    if not phrase_words:
        return [], "empty"
    page_words = page["words"]
    normalized = [norm_word(w["text"]) for w in page_words]

    for i in range(0, len(normalized) - len(phrase_words) + 1):
        if normalized[i : i + len(phrase_words)] == phrase_words:
            return page_words[i : i + len(phrase_words)], "contiguous"

    # Fallback for manual spans where the high-res reading combines two lines or
    # where the transcript has small punctuation/OCR differences.
    matched = []
    j = 0
    for w, nw in zip(page_words, normalized):
        if j < len(phrase_words) and nw == phrase_words[j]:
            matched.append(w)
            j += 1
    if j == len(phrase_words):
        return matched, "subsequence"
    return matched, "partial"


def word_initials(span_words: list[dict]) -> str:
    return "".join((w["letters"][:1] or "") for w in span_words)


def word_lasts(span_words: list[dict]) -> str:
    return "".join((w["letters"][-1:] or "") for w in span_words)


def word_lengths_mod26(span_words: list[dict]) -> str:
    out = []
    for w in span_words:
        n = len(w["letters"])
        if n:
            out.append(chr(ord("A") + ((n - 1) % 26)))
    return "".join(out)


def bold_letters(span_words: list[dict], *, partial_only: bool = False) -> str:
    out = []
    for w in span_words:
        if partial_only and not w.get("partialBold"):
            continue
        out.append(w.get("boldLetters", ""))
    return "".join(out)


def caesar(text: str, shift: int) -> str:
    out = []
    for ch in text.upper():
        if "A" <= ch <= "Z":
            out.append(chr(ord("A") + ((ord(ch) - ord("A") + shift) % 26)))
        else:
            out.append(ch)
    return "".join(out)


def atbash(text: str) -> str:
    out = []
    for ch in text.upper():
        if "A" <= ch <= "Z":
            out.append(chr(ord("Z") - (ord(ch) - ord("A"))))
        else:
            out.append(ch)
    return "".join(out)


def transform_hits(name: str, text: str) -> list[dict]:
    compact = letters(text).upper()
    if len(compact) < 3:
        return []
    variants = [(name, compact), (f"{name}:reverse", compact[::-1]), (f"{name}:atbash", atbash(compact))]
    variants.extend((f"{name}:caesar_{shift}", caesar(compact, shift)) for shift in range(1, 26))

    hits = []
    for vname, value in variants:
        found = [word for word in COMMON_SELECTOR_WORDS if word in value]
        # Ignore extremely short accidental hits unless they come with a longer word.
        if found and (any(len(w) >= 4 for w in found) or len(found) >= 3):
            hits.append({"variant": vname, "hits": found, "preview": value[:160]})
    return hits


def main() -> None:
    with CANONICAL.open() as f:
        canonical = json.load(f)
    pages = page_by_article(canonical)
    spans = load_spans()

    rows = []
    for i, span in enumerate(spans, 1):
        page = pages.get(span["page"])
        if not page:
            matched, mode = [], "missing_page"
        else:
            matched, mode = find_span_words(page, span["text"])
        row = {
            "index": i,
            "color": span["color"],
            "page": span["page"],
            "text": span["text"],
            "matchMode": mode,
            "matchedWords": len(matched),
            "wordCount": len(words(span["text"])),
            "phraseInitial": letters(span["text"])[:1],
            "wordInitials": word_initials(matched),
            "wordLasts": word_lasts(matched),
            "lengthsMod26": word_lengths_mod26(matched),
            "boldLetters": bold_letters(matched),
            "partialBoldLetters": bold_letters(matched, partial_only=True),
        }
        rows.append(row)

    stream_specs = {
        "all_phrase_initials": "".join(r["phraseInitial"] for r in rows),
        "all_word_initials": "".join(r["wordInitials"] for r in rows),
        "all_word_lasts": "".join(r["wordLasts"] for r in rows),
        "all_lengths_mod26": "".join(r["lengthsMod26"] for r in rows),
        "all_bold_letters": "".join(r["boldLetters"] for r in rows),
        "all_partial_bold_letters": "".join(r["partialBoldLetters"] for r in rows),
        "orange_phrase_initials": "".join(r["phraseInitial"] for r in rows if r["color"] == "orange"),
        "grey_phrase_initials": "".join(r["phraseInitial"] for r in rows if r["color"] == "grey_black"),
        "page76_phrase_initials": "".join(r["phraseInitial"] for r in rows if r["page"] == 76),
        "page76_bold_letters": "".join(r["boldLetters"] for r in rows if r["page"] == 76),
        "page76_partial_bold_letters": "".join(r["partialBoldLetters"] for r in rows if r["page"] == 76),
    }

    hits = []
    for name, stream in stream_specs.items():
        hits.extend(transform_hits(name, stream))

    by_page = {}
    for page in sorted(set(r["page"] for r in rows)):
        page_rows = [r for r in rows if r["page"] == page]
        by_page[str(page)] = {
            "phraseInitials": "".join(r["phraseInitial"] for r in page_rows),
            "wordInitials": "".join(r["wordInitials"] for r in page_rows),
            "wordLasts": "".join(r["wordLasts"] for r in page_rows),
            "boldLetters": "".join(r["boldLetters"] for r in page_rows),
            "partialBoldLetters": "".join(r["partialBoldLetters"] for r in page_rows),
        }

    result = {
        "source": {
            "canonical": str(CANONICAL),
            "orange": str(ORANGE),
            "grey": str(GREY),
        },
        "summary": {
            "spans": len(rows),
            "contiguousMatches": sum(1 for r in rows if r["matchMode"] == "contiguous"),
            "subsequenceMatches": sum(1 for r in rows if r["matchMode"] == "subsequence"),
            "partialMatches": sum(1 for r in rows if r["matchMode"] == "partial"),
            "selectorWordHits": len(hits),
        },
        "streams": stream_specs,
        "byPage": by_page,
        "selectorWordHits": hits,
        "rows": rows,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Highlight Selector Audit",
        "",
        "Scope: exact high-res highlighted spans plus Markdown bold markup. This checks simple human-readable selector streams only; it does not derive or test private keys.",
        "",
        "## Summary",
        "",
        f"- Spans checked: {result['summary']['spans']}",
        f"- Contiguous matches: {result['summary']['contiguousMatches']}",
        f"- Subsequence matches: {result['summary']['subsequenceMatches']}",
        f"- Partial matches: {result['summary']['partialMatches']}",
        f"- Selector-word transform hits: {result['summary']['selectorWordHits']}",
        "",
        "## Primary Streams",
        "",
    ]
    for key in [
        "all_phrase_initials",
        "orange_phrase_initials",
        "grey_phrase_initials",
        "page76_phrase_initials",
        "page76_bold_letters",
        "page76_partial_bold_letters",
        "all_lengths_mod26",
    ]:
        lines.append(f"- `{key}`: `{stream_specs[key]}`")

    lines.extend(["", "## Per Page", ""])
    for page, vals in by_page.items():
        lines.append(f"- p{page}: phraseInitials=`{vals['phraseInitials']}` bold=`{vals['boldLetters']}` partialBold=`{vals['partialBoldLetters']}`")

    lines.extend(["", "## Selector Word Hits", ""])
    if hits:
        for hit in hits[:30]:
            lines.append(f"- `{hit['variant']}` hits {', '.join(hit['hits'])}: `{hit['preview']}`")
    else:
        lines.append("- None. No first-letter/last-letter/length/bold-intersection stream produces a readable low-parameter instruction under raw, reverse, Atbash, or Caesar transforms.")

    lines.extend(["", "## Rows", ""])
    for r in rows:
        lines.append(
            f"- {r['color']} p{r['page']} `{r['text']}` -> mode={r['matchMode']} "
            f"initials=`{r['wordInitials']}` lasts=`{r['wordLasts']}` bold=`{r['boldLetters']}` partial=`{r['partialBoldLetters']}`"
        )

    lines.extend([
        "",
        "## Assessment",
        "",
        "- The highlight/bold intersection is structured but mostly reproduces already-visible emphasized words and known partial-bold fragments.",
        "- Page 76 remains semantically strong, but the exact highlighted spans do not provide a plain instruction through initials, endings, lengths, or bold-only extraction.",
        "- The next best move is source comparison or a manual selector hypothesis tied to the public mirror-writing clue, rather than more stream transforms.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
