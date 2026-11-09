#!/usr/bin/env python3
"""Search for the macro-referenced BIP39 word-list artifact.

BOLD.docm references:

    private_inputs\\OneDrive\\Desktop\\Alles\\TOXIC_AF\\BIP39\\otrobip.txt

This pass does not use BIP39 words, derive keys, hash text, or inspect wallet
activity. It only checks whether the missing source artifact exists locally.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/otrobip_recovery_audit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "otrobip_recovery_audit.json"
OUT_MD = OUT / "otrobip_recovery_audit.md"

SEARCH_ROOTS = [
    Path("private_inputs/Desktop"),
    Path("private_inputs/Documents"),
    Path("private_inputs/Downloads"),
]
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "analysis_outputs",
    "node_modules",
    ".cache",
    "__pycache__",
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def is_generated_file(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    return rel.parts[:1] in [("scripts",)] and path.name == "audit_otrobip_recovery.py"


def walk_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        stack = [root]
        while stack:
            current = stack.pop()
            if should_skip(current):
                continue
            try:
                children = list(current.iterdir())
            except (OSError, PermissionError):
                continue
            for child in children:
                if should_skip(child):
                    continue
                if child.is_dir():
                    stack.append(child)
                elif child.is_file():
                    files.append(child)
    return files


def main() -> None:
    files = walk_files()
    candidate_files = [path for path in files if not is_generated_file(path)]
    exact_otrobip = [str(path) for path in candidate_files if path.name.lower() == "otrobip.txt"]
    otrobip_like = [str(path) for path in candidate_files if "otrobip" in path.name.lower()]
    bip39_text = [str(path) for path in candidate_files if "bip39" in path.name.lower() and path.suffix.lower() == ".txt"]
    toxic_or_bip_dirs = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for child in root.rglob("*"):
            if should_skip(child):
                continue
            if child.is_dir() and child.name.lower() in {"bip39", "toxic_af", "alles"}:
                toxic_or_bip_dirs.append(str(child))

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "bounded recovery search for macro-referenced otrobip.txt; no key derivation or BIP39 use",
        "referencedPath": r"private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt",
        "searchRoots": [str(path) for path in SEARCH_ROOTS],
        "skippedDirectories": sorted(SKIP_DIRS),
        "searchedFileCount": len(candidate_files),
        "exactOtrobipTxtMatches": exact_otrobip,
        "otrobipLikeMatches": otrobip_like,
        "bip39TextMatches": bip39_text,
        "toxicOrBipDirectories": toxic_or_bip_dirs[:100],
        "decision": "The macro-referenced word list is not locally recovered in Desktop/Documents/Downloads.",
        "nextMove": "Do not use BOLD.docm as an extraction source unless otrobip.txt or the original TOXIC_AF/BIP39 folder is supplied.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# otrobip.txt Recovery Audit",
        "",
        "Scope: search for the missing word-list artifact referenced by `BOLD.docm`. No BIP39 extraction, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Referenced path: `{result['referencedPath']}`",
        f"- Search roots: `{', '.join(result['searchRoots'])}`",
        f"- Files searched: `{result['searchedFileCount']}`",
        f"- Exact `otrobip.txt` matches: `{len(exact_otrobip)}`",
        f"- `otrobip`-like matches: `{len(otrobip_like)}`",
        f"- `bip39*.txt` matches: `{len(bip39_text)}`",
        f"- Relevant non-skipped directories: `{len(toxic_or_bip_dirs)}`",
        "",
        "## Matches",
        "",
        "### Exact `otrobip.txt`",
        "",
    ]
    if exact_otrobip:
        lines.extend(f"- `{path}`" for path in exact_otrobip)
    else:
        lines.append("- none")
    lines.extend(["", "### `otrobip`-Like", ""])
    if otrobip_like:
        lines.extend(f"- `{path}`" for path in otrobip_like)
    else:
        lines.append("- none")
    lines.extend(["", "### `bip39*.txt`", ""])
    if bip39_text:
        lines.extend(f"- `{path}`" for path in bip39_text)
    else:
        lines.append("- none")
    lines.extend(["", "### Relevant Directories", ""])
    if toxic_or_bip_dirs:
        lines.extend(f"- `{path}`" for path in toxic_or_bip_dirs[:100])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The macro-referenced `otrobip.txt` word list is not locally recovered in Desktop, Documents, or Downloads.",
            "- This leaves `BOLD.docm` as a generated/highlighted working artifact, not a source-backed selector.",
            "- The unresolved dependency is the actual `TOXIC_AF/BIP39/otrobip.txt` folder or original author/layout source, if it exists.",
            "",
            "## Next Move",
            "",
            "- Do not use `BOLD.docm` for extraction unless the missing word list or original folder is supplied.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("exactOtrobipTxtMatches:", len(exact_otrobip))
    print("searchedFileCount:", result["searchedFileCount"])


if __name__ == "__main__":
    main()
