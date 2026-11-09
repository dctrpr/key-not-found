#!/usr/bin/env python3
"""Audit DOCM package hidden/source-structure evidence.

This complements the font-layer audits. It does not execute macros. It checks
for Word-package features that could carry an instruction outside the visible
article text: comments, hidden runs, bookmarks, hyperlinks, field codes,
headers/footers, custom XML, relationships, properties, and printable VBA
strings.
"""

from __future__ import annotations

import hashlib
import json
import re
import string
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "docm_hidden_structure_audit.json"
OUT_MD = OUT / "docm_hidden_structure_audit.md"

DOCS = {
    "BOLD.docm": Path("private_inputs/Desktop/BOLD.docm"),
    "Article with Fonts.docm": Path("private_inputs/Desktop/Article with Fonts.docm"),
}

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

INSTRUCTION_RE = re.compile(
    r"\b(read|take|fold|mirror|reverse|left|right|word|letter|line|key|seed|private|"
    r"wallet|bip39|instruction|select|hidden|macro|highlight|font|typeka|overdose|"
    r"symptom|volcano|shitcoin|bitcoin|billion)\b",
    re.I,
)


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def printable_strings(data: bytes, min_len: int = 4) -> list[str]:
    chars = set(string.printable)
    rows: list[str] = []
    buf: list[str] = []
    for byte in data:
        ch = chr(byte)
        if ch in chars and ch not in "\x0b\x0c":
            buf.append(ch)
        else:
            if len(buf) >= min_len:
                rows.append("".join(buf).strip())
            buf = []
    if len(buf) >= min_len:
        rows.append("".join(buf).strip())
    return [row for row in rows if row]


def xml_root(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    if name not in zf.namelist():
        return None
    try:
        return ET.fromstring(zf.read(name))
    except ET.ParseError:
        return None


def text_of(element: ET.Element) -> str:
    return "".join(element.itertext())


def tag_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def visible_document_text(root: ET.Element | None) -> str:
    if root is None:
        return ""
    return "\n".join(para_text(p) for p in root.findall(".//w:p", NS))


def has_child(run_props: ET.Element | None, local: str) -> bool:
    if run_props is None:
        return False
    return run_props.find(f"w:{local}", NS) is not None


def hidden_runs(root: ET.Element | None) -> list[dict]:
    if root is None:
        return []
    rows = []
    for idx, run in enumerate(root.findall(".//w:r", NS), 1):
        rpr = run.find("w:rPr", NS)
        if has_child(rpr, "vanish") or has_child(rpr, "webHidden"):
            text = "".join(t.text or "" for t in run.findall(".//w:t", NS))
            rows.append({"runIndex": idx, "text": text, "vanish": has_child(rpr, "vanish"), "webHidden": has_child(rpr, "webHidden")})
    return rows


def bookmarks(root: ET.Element | None) -> list[dict]:
    if root is None:
        return []
    rows = []
    for node in root.findall(".//w:bookmarkStart", NS):
        rows.append(
            {
                "id": node.attrib.get(f"{{{NS['w']}}}id"),
                "name": node.attrib.get(f"{{{NS['w']}}}name"),
            }
        )
    return rows


def hyperlinks(root: ET.Element | None) -> list[dict]:
    if root is None:
        return []
    rows = []
    for node in root.findall(".//w:hyperlink", NS):
        rows.append(
            {
                "anchor": node.attrib.get(f"{{{NS['w']}}}anchor"),
                "relationshipId": node.attrib.get(f"{{{NS['r']}}}id"),
                "text": text_of(node),
            }
        )
    return rows


def field_codes(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    return [node.text or "" for node in root.findall(".//w:instrText", NS) if (node.text or "").strip()]


def core_props(zf: zipfile.ZipFile) -> dict:
    root = xml_root(zf, "docProps/core.xml")
    if root is None:
        return {}
    props = {}
    for node in list(root):
        name = tag_name(node.tag)
        props[name] = node.text or ""
    return props


def relationships(zf: zipfile.ZipFile, name: str) -> list[dict]:
    root = xml_root(zf, name)
    if root is None:
        return []
    rows = []
    for rel in root.findall(".//rel:Relationship", NS):
        rows.append({tag_name(k): v for k, v in rel.attrib.items()})
    return rows


def part_text_instruction_hits(zf: zipfile.ZipFile, parts: list[str], body_text: str) -> list[dict]:
    hits = []
    body_norm = re.sub(r"\s+", " ", body_text)
    for part in parts:
        if not (part.endswith(".xml") or part.endswith(".rels")):
            continue
        raw = zf.read(part)
        try:
            text = text_of(ET.fromstring(raw))
        except ET.ParseError:
            text = raw.decode("utf-8", errors="ignore")
        norm = re.sub(r"\s+", " ", text).strip()
        if not norm:
            continue
        # Avoid treating ordinary article body as a hidden instruction source.
        if part == "word/document.xml":
            continue
        matches = sorted(set(m.group(0).lower() for m in INSTRUCTION_RE.finditer(norm)))
        if matches:
            hits.append(
                {
                    "part": part,
                    "matches": matches,
                    "excerpt": norm[:360],
                    "appearsBodyDerived": bool(norm and norm in body_norm),
                }
            )
    return hits


def audit_doc(label: str, path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        parts = zf.namelist()
        doc_root = xml_root(zf, "word/document.xml")
        body_text = visible_document_text(doc_root)
        vba_strings = []
        if "word/vbaProject.bin" in parts:
            vba_strings = printable_strings(zf.read("word/vbaProject.bin"))
        vba_hits = [row for row in vba_strings if INSTRUCTION_RE.search(row)]
        special_parts = {
            "comments": [p for p in parts if "comments" in p.lower()],
            "headers": [p for p in parts if "/header" in p.lower()],
            "footers": [p for p in parts if "/footer" in p.lower()],
            "footnotes": [p for p in parts if "footnote" in p.lower()],
            "endnotes": [p for p in parts if "endnote" in p.lower()],
            "customXml": [p for p in parts if p.startswith("customXml/")],
            "embeddings": [p for p in parts if "embeddings/" in p],
            "media": [p for p in parts if "/media/" in p],
            "vba": [p for p in parts if "vba" in p.lower()],
        }
        return {
            "label": label,
            "path": str(path),
            "md5": md5(path),
            "parts": parts,
            "partCount": len(parts),
            "specialParts": special_parts,
            "coreProperties": core_props(zf),
            "packageRelationships": relationships(zf, "_rels/.rels"),
            "documentRelationships": relationships(zf, "word/_rels/document.xml.rels"),
            "paragraphCount": len(doc_root.findall(".//w:p", NS)) if doc_root is not None else 0,
            "visibleTextChars": len(body_text),
            "hiddenRuns": hidden_runs(doc_root),
            "bookmarks": bookmarks(doc_root),
            "hyperlinks": hyperlinks(doc_root),
            "fieldCodes": field_codes(doc_root),
            "annotationMarkers": {
                "commentRangeStart": len(doc_root.findall(".//w:commentRangeStart", NS)) if doc_root is not None else 0,
                "commentReference": len(doc_root.findall(".//w:commentReference", NS)) if doc_root is not None else 0,
                "ins": len(doc_root.findall(".//w:ins", NS)) if doc_root is not None else 0,
                "del": len(doc_root.findall(".//w:del", NS)) if doc_root is not None else 0,
            },
            "nonBodyInstructionHits": part_text_instruction_hits(zf, parts, body_text),
            "vbaInstructionStrings": vba_hits[:60],
            "vbaInstructionStringCount": len(vba_hits),
        }


def main() -> None:
    docs = []
    for label, path in DOCS.items():
        if path.exists():
            docs.append(audit_doc(label, path))
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "DOCM hidden/source-structure audit; no macro execution; no key derivation",
        "documents": docs,
        "assessment": [
            "Article with Fonts.docm has no comments, custom XML, hidden runs, bookmarks, hyperlinks, field codes, or VBA project in this package-level audit.",
            "BOLD.docm contains a VBA project and vbaData pointing to the already-known HighlightWordsFromTextFile workflow, but no hidden Word comments/runs/bookmarks that define a puzzle instruction.",
            "The only non-body instruction-like material remains BOLD.docm's macro strings and external BIP39/otrobip.txt path, which supports treating BOLD.docm as a generated working artifact rather than original puzzle source.",
            "No new source/layout instruction was recovered from DOCM hidden structure.",
        ],
        "nextMove": "Stop treating the DOCM containers as a source of hidden instructions unless the missing otrobip.txt or original layout files are recovered. Continue with external Canva/source clues or physical registration.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# DOCM Hidden Structure Audit",
        "",
        "Scope: inspect DOCM package structure for hidden/source instructions. Macros are not executed, and no key candidates are generated.",
        "",
    ]
    for doc in docs:
        lines.extend(
            [
                f"## {doc['label']}",
                "",
                f"- Path: `{doc['path']}`",
                f"- MD5: `{doc['md5']}`",
                f"- Parts: `{doc['partCount']}`",
                f"- Creator: `{doc['coreProperties'].get('creator', '')}`",
                f"- Created: `{doc['coreProperties'].get('created', '')}`",
                f"- Modified: `{doc['coreProperties'].get('modified', '')}`",
                f"- VBA parts: `{doc['specialParts']['vba']}`",
                f"- Comments/header/footer/custom XML parts: comments `{doc['specialParts']['comments']}`, headers `{doc['specialParts']['headers']}`, footers `{doc['specialParts']['footers']}`, customXml `{doc['specialParts']['customXml']}`",
                f"- Hidden runs: `{len(doc['hiddenRuns'])}`",
                f"- Bookmarks: `{len(doc['bookmarks'])}`",
                f"- Hyperlinks: `{len(doc['hyperlinks'])}`",
                f"- Field codes: `{len(doc['fieldCodes'])}`",
                f"- Annotation markers: `{doc['annotationMarkers']}`",
                f"- Non-body instruction-hit parts: `{len(doc['nonBodyInstructionHits'])}`",
                f"- VBA instruction strings: `{doc['vbaInstructionStringCount']}`",
                "",
            ]
        )
        if doc["hiddenRuns"]:
            lines.append("### Hidden Runs")
            for row in doc["hiddenRuns"][:20]:
                lines.append(f"- run `{row['runIndex']}`: `{row['text']}`")
            lines.append("")
        if doc["nonBodyInstructionHits"]:
            lines.append("### Non-Body Instruction-Like Parts")
            for row in doc["nonBodyInstructionHits"][:12]:
                lines.append(f"- `{row['part']}` matches `{', '.join(row['matches'])}` excerpt `{row['excerpt']}`")
            lines.append("")
        if doc["vbaInstructionStrings"]:
            lines.append("### VBA Printable Strings")
            for row in doc["vbaInstructionStrings"][:18]:
                lines.append(f"- `{row}`")
            lines.append("")
    lines.extend(
        [
            "## Assessment",
            "",
            "- `Article with Fonts.docm` does not expose a hidden instruction layer in package structure: no comments, hidden runs, bookmarks, hyperlinks, field codes, custom XML, or macros.",
            "- `BOLD.docm` contains the already-known macro/highlight workflow and `BIP39\\otrobip.txt` path, but no hidden Word annotation layer that tells us how to read the puzzle.",
            "- This strengthens the prior split: use `Article with Fonts.docm` as a formatting witness, treat `BOLD.docm` as a generated working artifact, and do not mine DOCM containers for more instructions unless `otrobip.txt` or original source files appear.",
            "",
            "## Next Best Move",
            "",
            "- Return to external source clues: higher-resolution Canva/original layout evidence, or physical-source registration that changes what lands on page 76.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
