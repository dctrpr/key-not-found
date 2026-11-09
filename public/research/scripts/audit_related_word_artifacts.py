#!/usr/bin/env python3
"""Audit two likely puzzle-related Word artifacts.

This is a source-artifact check, not extraction. It inspects only two files
whose names suggest possible relation to the BOLD.docm/macro workflow:

    private_inputs/Desktop/Text_by_sentences.docx
    private_inputs/Documents/macro data.docx

It does not generate keys, hashes, BIP39 phrases, WIFs, or addresses.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/related_word_artifacts"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "related_word_artifacts.json"
OUT_MD = OUT / "related_word_artifacts.md"

DOCS = {
    "Text_by_sentences.docx": Path("private_inputs/Desktop/Text_by_sentences.docx"),
    "macro data.docx": Path("private_inputs/Documents/macro data.docx"),
}

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
}

TERMS = [
    "bitcoin",
    "toxic",
    "keiser",
    "max",
    "bip39",
    "otrobip",
    "seed",
    "mnemonic",
    "wallet",
    "private",
    "key",
    "typeka",
    "macro",
    "highlight",
    "word",
    "sentence",
    "volcano",
    "bond",
    "shitcoin",
    "satoshi",
    "mirror",
    "read",
    "take",
    "line",
    "letter",
]


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def xml_root(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    if name not in zf.namelist():
        return None
    try:
        return ET.fromstring(zf.read(name))
    except ET.ParseError:
        return None


def tag_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def core_props(zf: zipfile.ZipFile) -> dict[str, str]:
    root = xml_root(zf, "docProps/core.xml")
    if root is None:
        return {}
    return {tag_name(node.tag): node.text or "" for node in list(root)}


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def visible_text(root: ET.Element | None) -> str:
    if root is None:
        return ""
    return "\n".join(para_text(p) for p in root.findall(".//w:p", NS))


def has_child(run_props: ET.Element | None, local: str) -> bool:
    if run_props is None:
        return False
    return run_props.find(f"w:{local}", NS) is not None


def hidden_runs(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    rows = []
    for run in root.findall(".//w:r", NS):
        rpr = run.find("w:rPr", NS)
        if has_child(rpr, "vanish") or has_child(rpr, "webHidden"):
            text = "".join(t.text or "" for t in run.findall(".//w:t", NS))
            if text:
                rows.append(text)
    return rows


def part_names(parts: list[str], token: str) -> list[str]:
    return [part for part in parts if token.lower() in part.lower()]


def term_hits(text: str) -> dict[str, int]:
    low = text.lower()
    return {term: len(re.findall(rf"\b{re.escape(term)}\b", low)) for term in TERMS if re.search(rf"\b{re.escape(term)}\b", low)}


def excerpts(text: str, terms: list[str], limit: int = 10) -> list[dict[str, str]]:
    rows = []
    low = text.lower()
    for term in terms:
        for match in re.finditer(rf"\b{re.escape(term)}\b", low):
            start = max(0, match.start() - 90)
            end = min(len(text), match.end() + 110)
            rows.append({"term": term, "excerpt": re.sub(r"\s+", " ", text[start:end]).strip()})
            if len(rows) >= limit:
                return rows
    return rows


def audit(path: Path, label: str) -> dict:
    if not path.exists():
        return {"label": label, "path": str(path), "exists": False}
    with zipfile.ZipFile(path) as zf:
        parts = zf.namelist()
        doc_root = xml_root(zf, "word/document.xml")
        text = visible_text(doc_root)
        hits = term_hits(text)
        return {
            "label": label,
            "path": str(path),
            "exists": True,
            "md5": md5(path),
            "sizeBytes": path.stat().st_size,
            "partCount": len(parts),
            "coreProperties": core_props(zf),
            "paragraphCount": len(doc_root.findall(".//w:p", NS)) if doc_root is not None else 0,
            "visibleTextChars": len(text),
            "visibleTextWords": len(re.findall(r"[A-Za-z0-9']+", text)),
            "specialParts": {
                "comments": part_names(parts, "comments"),
                "vba": part_names(parts, "vba"),
                "customXml": [part for part in parts if part.startswith("customXml/")],
                "media": [part for part in parts if "/media/" in part],
                "embeddings": [part for part in parts if "/embeddings/" in part],
            },
            "hiddenRuns": hidden_runs(doc_root),
            "termHits": hits,
            "hitExcerpts": excerpts(text, list(hits.keys())),
            "firstTextSample": re.sub(r"\s+", " ", text[:500]).strip(),
        }


def main() -> None:
    docs = [audit(path, label) for label, path in DOCS.items()]
    puzzle_related = [
        doc["label"]
        for doc in docs
        if doc.get("exists") and any(term in doc.get("termHits", {}) for term in ["bitcoin", "toxic", "bip39", "otrobip", "typeka", "volcano", "shitcoin"])
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "bounded audit of two likely Word artifacts; no key derivation, hashing, BIP39 use, WIF, seed, or address checks",
        "documents": docs,
        "puzzleRelatedByKeyword": puzzle_related,
        "decision": "Use any artifact only if it contains puzzle/source keywords or hidden instruction structure; otherwise keep it out of the selector set.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Related Word Artifacts Audit",
        "",
        "Scope: inspect two likely Word artifacts by filename only: `Text_by_sentences.docx` and `macro data.docx`. No key derivation, hashing, BIP39 use, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Puzzle-related by keyword: `{puzzle_related}`",
        "",
    ]
    for doc in docs:
        lines.extend([f"## {doc['label']}", ""])
        if not doc.get("exists"):
            lines.extend([f"- Path: `{doc['path']}`", "- Exists: `False`", ""])
            continue
        props = doc["coreProperties"]
        lines.extend(
            [
                f"- Path: `{doc['path']}`",
                f"- MD5: `{doc['md5']}`",
                f"- Size: `{doc['sizeBytes']}` bytes",
                f"- Creator: `{props.get('creator', '')}`",
                f"- Created: `{props.get('created', '')}`",
                f"- Modified: `{props.get('modified', '')}`",
                f"- Paragraphs / words / chars: `{doc['paragraphCount']}` / `{doc['visibleTextWords']}` / `{doc['visibleTextChars']}`",
                f"- Special parts: `{doc['specialParts']}`",
                f"- Hidden runs: `{len(doc['hiddenRuns'])}`",
                f"- Term hits: `{doc['termHits']}`",
                "",
            ]
        )
        if doc["hitExcerpts"]:
            lines.append("### Hit Excerpts")
            for row in doc["hitExcerpts"]:
                lines.append(f"- `{row['term']}`: `{row['excerpt']}`")
            lines.append("")
        else:
            lines.extend(["### Text Sample", "", f"`{doc['firstTextSample']}`", ""])
    lines.extend(
        [
            "## Assessment",
            "",
            "- Only files with puzzle keywords or hidden instruction structure should affect the solve path.",
            "- If neither file contains `bitcoin` / `toxic` / `bip39` / `otrobip` / `typeka` / page-76 corridor terms, they are not source artifacts for this puzzle.",
            "- This pass does not reopen BIP39 or key-generation branches.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("puzzleRelatedByKeyword:", puzzle_related)


if __name__ == "__main__":
    main()
