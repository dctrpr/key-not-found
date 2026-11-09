#!/usr/bin/env python3
"""Audit macro provenance in BOLD.docm without executing macros."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "docm_format_sources"
BOLD_DOCM = Path("private_inputs/Desktop/BOLD.docm")
ARTICLE_DOCM = Path("private_inputs/Desktop/Article with Fonts.docm")


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return zf.namelist()


def read_zip_member(path: Path, name: str) -> bytes:
    with zipfile.ZipFile(path) as zf:
        return zf.read(name)


def xml_props(path: Path) -> dict[str, str]:
    names = zip_names(path)
    if "docProps/core.xml" not in names:
        return {}
    data = read_zip_member(path, "docProps/core.xml")
    root = ET.fromstring(data)
    out: dict[str, str] = {}
    for child in root:
        tag = child.tag.split("}", 1)[-1]
        out[tag] = child.text or ""
    return out


def printable_strings(data: bytes) -> list[str]:
    ascii_hits = [
        m.group(0).decode("latin1", "ignore")
        for m in re.finditer(rb"[ -~]{4,}", data)
    ]
    # VBA projects often include UTF-16LE strings. Decode defensively and pull
    # printable runs so we can inspect provenance without running the macro.
    decoded = data.decode("utf-16le", "ignore")
    wide_hits = re.findall(r"[ -~]{4,}", decoded)
    seen: set[str] = set()
    out: list[str] = []
    for hit in ascii_hits + wide_hits:
        cleaned = hit.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            out.append(cleaned)
    return out


def macro_summary(path: Path) -> dict:
    names = zip_names(path)
    has_vba = "word/vbaProject.bin" in names
    has_vba_data = "word/vbaData.xml" in names
    strings: list[str] = []
    vba_data_text = ""
    if has_vba:
        strings = printable_strings(read_zip_member(path, "word/vbaProject.bin"))
    if has_vba_data:
        vba_data_text = read_zip_member(path, "word/vbaData.xml").decode(
            "utf-8", "replace"
        )

    interesting_terms = [
        "Highlight",
        "words",
        ".txt",
        "BIP39",
        "otrobip",
        "TOXIC_AF",
        "current document",
        "Highlighting complete",
        "Error reading file",
    ]
    interesting_strings = [
        s
        for s in strings
        if any(term.lower() in s.lower() for term in interesting_terms)
    ]

    local_otrobip_matches = []
    for base in [Path("private_inputs/Desktop"), ROOT]:
        for candidate in base.rglob("*"):
            if candidate.is_file() and candidate.name.lower() == "otrobip.txt":
                local_otrobip_matches.append(str(candidate))

    return {
        "path": str(path),
        "md5": md5(path),
        "size": path.stat().st_size,
        "coreProperties": xml_props(path),
        "hasVbaProject": has_vba,
        "hasVbaData": has_vba_data,
        "vbaDataContainsHighlightWordsMacro": "HighlightWordsFromTextFile"
        in vba_data_text,
        "interestingStrings": interesting_strings,
        "otrobipSearchRoots": ["private_inputs/Desktop", str(ROOT)],
        "localOtrobipMatches": local_otrobip_matches,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    bold = macro_summary(BOLD_DOCM)
    article_names = zip_names(ARTICLE_DOCM)
    article = {
        "path": str(ARTICLE_DOCM),
        "md5": md5(ARTICLE_DOCM),
        "size": ARTICLE_DOCM.stat().st_size,
        "coreProperties": xml_props(ARTICLE_DOCM),
        "hasVbaProject": "word/vbaProject.bin" in article_names,
        "hasVbaData": "word/vbaData.xml" in article_names,
    }

    report = {
        "bold": bold,
        "articleWithFonts": article,
        "assessment": [
            "BOLD.docm contains a VBA project and should be treated as an investigator/generated markup artifact, not an original formatting source.",
            "The macro strings indicate a word-highlighting routine that reads a text file at private_inputs\\OneDrive\\Desktop\\Alles\\TOXIC_AF\\BIP39\\otrobip.txt.",
            "The referenced local otrobip.txt file was not found under Desktop or the puzzle workspace.",
            "Article with Fonts.docm has no embedded VBA project and remains the better Word-level formatting witness.",
        ],
    }

    json_path = OUT_DIR / "bold_docm_macro_audit.json"
    md_path = OUT_DIR / "bold_docm_macro_audit.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# BOLD.docm Macro Provenance Audit",
        "",
        "Scope: inspect macro-enabled Word-package metadata and embedded VBA strings without executing macros.",
        "",
        "## Sources",
        "",
        f"- `BOLD.docm`: `{BOLD_DOCM}`",
        f"  - MD5: `{bold['md5']}`",
        f"  - embedded VBA project: `{bold['hasVbaProject']}`",
        f"  - embedded VBA data: `{bold['hasVbaData']}`",
        f"  - created by: `{bold['coreProperties'].get('creator', '')}`",
        f"  - created: `{bold['coreProperties'].get('created', '')}`",
        f"  - modified: `{bold['coreProperties'].get('modified', '')}`",
        f"- `Article with Fonts.docm`: `{ARTICLE_DOCM}`",
        f"  - MD5: `{article['md5']}`",
        f"  - embedded VBA project: `{article['hasVbaProject']}`",
        f"  - embedded VBA data: `{article['hasVbaData']}`",
        f"  - created by: `{article['coreProperties'].get('creator', '')}`",
        "",
        "## Macro Evidence",
        "",
        f"- `word/vbaData.xml` references `HighlightWordsFromTextFile`: `{bold['vbaDataContainsHighlightWordsMacro']}`",
        "- Relevant printable strings from `word/vbaProject.bin`:",
    ]
    for s in bold["interestingStrings"]:
        lines.append(f"  - `{s}`")
    if not bold["interestingStrings"]:
        lines.append("  - none")

    lines.extend(
        [
            "",
            "## Referenced Word List Search",
            "",
            "- Macro-referenced path: `private_inputs\\OneDrive\\Desktop\\Alles\\TOXIC_AF\\BIP39\\otrobip.txt`",
            f"- Search roots checked: `{', '.join(bold['otrobipSearchRoots'])}`",
            f"- Local `otrobip.txt` matches found: `{len(bold['localOtrobipMatches'])}`",
        ]
    )
    for match in bold["localOtrobipMatches"]:
        lines.append(f"  - `{match}`")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- `BOLD.docm` is probably not an original article-format source. It appears to be a generated/highlighted working document made by a macro that reads a separate text file of words.",
            "- The folder name `BIP39` and file name `otrobip.txt` suggest this document may highlight BIP39-like words, but the actual word list file was not recovered locally.",
            "- Do not use `BOLD.docm` as proof that the puzzle's original bolding is BIP39-based.",
            "- Use `Article with Fonts.docm` as the stronger Word-level formatting witness because it has no embedded VBA project and preserves font/highlight layers directly.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n")
    print(md_path)
    print(json_path)


if __name__ == "__main__":
    main()
