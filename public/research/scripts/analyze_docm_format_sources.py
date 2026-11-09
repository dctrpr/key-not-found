#!/usr/bin/env python3
"""Extract run-level bold/font data from user-provided DOCM article files.

The DOCM files are treated as OOXML ZIP archives only. Macros are not executed.
"""

from __future__ import annotations

import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/docm_format_sources"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DOCS = {
    "bold": Path("private_inputs/Desktop/BOLD.docm"),
    "article_with_fonts": Path("private_inputs/Desktop/Article with Fonts.docm"),
}

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def attr(el: ET.Element | None, name: str) -> str | None:
    if el is None:
        return None
    return el.attrib.get(W + name)


def bool_prop(rpr: ET.Element | None, prop: str) -> bool:
    if rpr is None:
        return False
    el = rpr.find(W + prop)
    if el is None:
        return False
    val = attr(el, "val")
    return val not in {"0", "false", "False", "off"}


def text_from_run(run: ET.Element) -> str:
    parts: list[str] = []
    for child in run:
        tag = child.tag
        if tag == W + "t":
            parts.append(child.text or "")
        elif tag == W + "tab":
            parts.append("\t")
        elif tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return "".join(parts)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z0-9]+)?", text)


def letters_only(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9$]", text))


def rpr_signature(rpr: ET.Element | None) -> dict:
    fonts = rpr.find(W + "rFonts") if rpr is not None else None
    color = rpr.find(W + "color") if rpr is not None else None
    sz = rpr.find(W + "sz") if rpr is not None else None
    highlight = rpr.find(W + "highlight") if rpr is not None else None
    shd = rpr.find(W + "shd") if rpr is not None else None
    style = rpr.find(W + "rStyle") if rpr is not None else None
    return {
        "bold": bool_prop(rpr, "b"),
        "italic": bool_prop(rpr, "i"),
        "underline": rpr.find(W + "u") is not None if rpr is not None else False,
        "strike": bool_prop(rpr, "strike") or bool_prop(rpr, "dstrike"),
        "fontAscii": attr(fonts, "ascii"),
        "fontHAnsi": attr(fonts, "hAnsi"),
        "fontCs": attr(fonts, "cs"),
        "fontEastAsia": attr(fonts, "eastAsia"),
        "sizeHalfPoints": attr(sz, "val"),
        "color": attr(color, "val"),
        "highlight": attr(highlight, "val"),
        "shadeFill": attr(shd, "fill"),
        "style": attr(style, "val"),
    }


def compact_sig(sig: dict) -> str:
    parts = []
    for key in [
        "bold",
        "italic",
        "underline",
        "strike",
        "fontAscii",
        "fontHAnsi",
        "fontCs",
        "fontEastAsia",
        "sizeHalfPoints",
        "color",
        "highlight",
        "shadeFill",
        "style",
    ]:
        val = sig.get(key)
        if val not in {None, False, ""}:
            parts.append(f"{key}={val}")
    return "; ".join(parts) or "plain"


def parse_doc(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
        names = set(zf.namelist())

    root = ET.fromstring(xml)
    paragraphs = []
    runs = []
    abs_pos = 0

    for p_idx, p in enumerate(root.iter(W + "p")):
        p_runs = []
        p_text_parts = []
        for r in p.findall(W + "r"):
            text = text_from_run(r)
            if text == "":
                continue
            rpr = r.find(W + "rPr")
            sig = rpr_signature(rpr)
            rec = {
                "runIndex": len(runs),
                "paragraphIndex": p_idx,
                "start": abs_pos,
                "end": abs_pos + len(text),
                "text": text,
                "clean": normalize_text(text),
                "letters": letters_only(text),
                **sig,
            }
            runs.append(rec)
            p_runs.append(rec["runIndex"])
            p_text_parts.append(text)
            abs_pos += len(text)
        para_text = "".join(p_text_parts)
        if p_runs or para_text.strip():
            paragraphs.append(
                {
                    "paragraphIndex": p_idx,
                    "runIndexes": p_runs,
                    "text": para_text,
                    "clean": normalize_text(para_text),
                }
            )
        abs_pos += 1  # paragraph separator in extracted full text

    full_text = "\n".join(p["text"] for p in paragraphs)
    bold_runs = [r for r in runs if r["bold"]]
    font_counter = Counter()
    size_counter = Counter()
    sig_counter = Counter()
    for r in runs:
        font = r["fontAscii"] or r["fontHAnsi"] or r["fontCs"] or r["fontEastAsia"] or "(none)"
        font_counter[font] += len(r["text"])
        size_counter[r["sizeHalfPoints"] or "(none)"] += len(r["text"])
        sig_counter[compact_sig(r)] += len(r["text"])

    # Build character streams for non-default signature groups. A group must be
    # reasonably small to be useful as a selector; huge body-font groups are
    # summarized but not treated as key material.
    by_font = defaultdict(list)
    by_sig = defaultdict(list)
    for r in runs:
        font = r["fontAscii"] or r["fontHAnsi"] or r["fontCs"] or r["fontEastAsia"] or "(none)"
        by_font[font].append(r["text"])
        by_sig[compact_sig(r)].append(r["text"])

    return {
        "path": str(path),
        "hasVbaProject": "word/vbaProject.bin" in names,
        "paragraphCount": len(paragraphs),
        "runCount": len(runs),
        "charCount": len(full_text),
        "wordCount": len(words(full_text)),
        "fullText": full_text,
        "paragraphs": paragraphs,
        "runs": runs,
        "summary": {
            "boldRunCount": len(bold_runs),
            "boldCharCount": sum(len(r["text"]) for r in bold_runs),
            "boldLetters": "".join(r["letters"] for r in bold_runs),
            "fontCharCounts": dict(font_counter.most_common()),
            "sizeHalfPointCharCounts": dict(size_counter.most_common()),
            "signatureCharCounts": dict(sig_counter.most_common()),
            "fontStreams": {k: normalize_text("".join(v)) for k, v in sorted(by_font.items())},
            "signatureStreams": {k: normalize_text("".join(v)) for k, v in sorted(by_sig.items())},
        },
    }


def small_streams(summary: dict, limit: int = 500) -> dict[str, str]:
    streams = {}
    for source_key in ["fontStreams", "signatureStreams"]:
        for key, value in summary[source_key].items():
            if 0 < len(value) <= limit:
                streams[f"{source_key}:{key}"] = value
    return streams


def main() -> None:
    docs = {name: parse_doc(path) for name, path in DOCS.items()}

    for name, doc in docs.items():
        (OUT_DIR / f"{name}_text.txt").write_text(doc["fullText"], encoding="utf-8")
        (OUT_DIR / f"{name}_runs.json").write_text(json.dumps(doc["runs"], indent=2, ensure_ascii=False) + "\n")

    result = {
        "sources": {name: doc["path"] for name, doc in docs.items()},
        "documents": {
            name: {
                key: doc[key]
                for key in ["path", "hasVbaProject", "paragraphCount", "runCount", "charCount", "wordCount", "summary"]
            }
            for name, doc in docs.items()
        },
        "smallStreams": {name: small_streams(doc["summary"]) for name, doc in docs.items()},
        "textEqualAfterWhitespaceNormalization": normalize_text(docs["bold"]["fullText"])
        == normalize_text(docs["article_with_fonts"]["fullText"]),
    }
    (OUT_DIR / "docm_format_audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# DOCM Formatting Source Audit",
        "",
        "Scope: extract run-level bold/font information from the user-provided Word macro documents without executing macros.",
        "",
        "## Sources",
        "",
    ]
    for name, doc in docs.items():
        lines.append(f"- `{name}`: `{doc['path']}`")
        lines.append(f"  - macros present: `{doc['hasVbaProject']}`")
        lines.append(f"  - paragraphs/runs/words/chars: `{doc['paragraphCount']}` / `{doc['runCount']}` / `{doc['wordCount']}` / `{doc['charCount']}`")
        lines.append(f"  - bold runs/chars: `{doc['summary']['boldRunCount']}` / `{doc['summary']['boldCharCount']}`")
    lines.extend(
        [
            "",
            f"- Text equal after whitespace normalization: `{result['textEqualAfterWhitespaceNormalization']}`",
            "",
            "## Bold Streams",
            "",
        ]
    )
    for name, doc in docs.items():
        stream = doc["summary"]["boldLetters"]
        preview = stream[:500] + ("..." if len(stream) > 500 else "")
        lines.append(f"- `{name}` bold letters length `{len(stream)}`: `{preview}`")

    lines.extend(["", "## Font Character Counts", ""])
    for name, doc in docs.items():
        lines.append(f"### {name}")
        for font, count in doc["summary"]["fontCharCounts"].items():
            lines.append(f"- `{font}`: {count}")

    lines.extend(["", "## Size Character Counts", ""])
    for name, doc in docs.items():
        lines.append(f"### {name}")
        for size, count in doc["summary"]["sizeHalfPointCharCounts"].items():
            lines.append(f"- `{size}`: {count}")

    lines.extend(["", "## Small Formatting Streams", ""])
    for name, streams in result["smallStreams"].items():
        lines.append(f"### {name}")
        if not streams:
            lines.append("- none")
        for key, value in streams.items():
            lines.append(f"- `{key}` len={len(value)}: `{value[:500]}`")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- These files are new formatting witnesses. They should be compared against the high-res article model before using them as selectors.",
            "- Macro presence is noted, but macro code was not executed.",
            "- If a font or bold stream is short and non-body-like, it is a candidate selector. Huge body-font streams should be treated as transcription support, not key material.",
        ]
    )
    (OUT_DIR / "docm_format_audit.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_DIR / 'docm_format_audit.md'}")
    print(f"wrote {OUT_DIR / 'docm_format_audit.json'}")
    for name in docs:
        print(f"wrote {OUT_DIR / (name + '_text.txt')}")
        print(f"wrote {OUT_DIR / (name + '_runs.json')}")


if __name__ == "__main__":
    main()
