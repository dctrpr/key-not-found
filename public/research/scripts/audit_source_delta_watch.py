#!/usr/bin/env python3
"""Watch local folders for new source-grade puzzle material.

The current frontier says local selector permutations are exhausted under the
trusted scan. This pass checks whether any new PDF/image/layout/document files
have appeared that could reopen source/physical/original-layout validation.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_delta_watch"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_delta_watch.json"
OUT_MD = OUT / "source_delta_watch.md"
INVENTORY = ROOT / "analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_inventory.json"

WATCH_ROOTS = [
    Path("private_inputs/Desktop"),
    Path("private_inputs/Downloads"),
    Path("private_inputs/Documents"),
]
SKIP_DIRS = {
    ".git",
    ".Trash",
    ".cache",
    ".codex",
    "Library",
    "node_modules",
    "analysis_outputs",
    "__pycache__",
    ".venv",
    "venv",
}
SOURCE_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".tif",
    ".tiff",
    ".heic",
    ".docx",
    ".docm",
    ".pptx",
    ".zip",
    ".indd",
    ".idml",
    ".ai",
    ".psd",
}
NAME_TERMS = {
    "bitcoin",
    "keiser",
    "max",
    "magazine",
    "issue",
    "overdose",
    "toxic",
    "canva",
    "schott",
    "bold",
    "article",
    "font",
    "fonts",
    "text",
    "salvador",
    "bukele",
    "volcano",
}
GEOMETRY_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}
LAYOUT_EXTENSIONS = {".indd", ".idml", ".ai", ".psd", ".zip"}


def load_inventory() -> tuple[set[str], dict[str, list[str]]]:
    if not INVENTORY.exists():
        return set(), {}
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    paths = set()
    hashes: dict[str, list[str]] = {}
    for key in ["candidates", "files", "rows", "records"]:
        value = data.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict) and item.get("path"):
                resolved = str(Path(item["path"]).resolve())
                paths.add(resolved)
                md5 = item.get("md5")
                if md5:
                    hashes.setdefault(str(md5), []).append(resolved)
    # The older inventory uses `items`.
    for item in data.get("items", []) if isinstance(data.get("items"), list) else []:
        if isinstance(item, dict) and item.get("path"):
            resolved = str(Path(item["path"]).resolve())
            paths.add(resolved)
            md5 = item.get("md5")
            if md5:
                hashes.setdefault(str(md5), []).append(resolved)
    return paths, hashes


def md5_file(path: Path, max_bytes: int = 250_000_000) -> str | None:
    try:
        stat = path.stat()
        if stat.st_size > max_bytes:
            return None
        digest = hashlib.md5()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def walk_candidates(now: datetime) -> list[dict]:
    cutoff_recent = now - timedelta(hours=36)
    rows = []
    seen: set[str] = set()
    project_root_resolved = ROOT.resolve()

    for root in WATCH_ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            path = Path(dirpath)
            parts = set(path.parts)
            if parts & SKIP_DIRS:
                dirnames[:] = []
                continue
            # Keep the Documents scan shallow except for the project root and
            # immediately adjacent user-supplied files.
            try:
                rel = path.relative_to(root)
                depth = len(rel.parts)
            except ValueError:
                depth = 0
            if root.name == "Documents" and project_root_resolved not in [path.resolve(), *path.resolve().parents] and depth > 3:
                dirnames[:] = []
                continue
            if root.name == "Documents" and project_root_resolved in [path.resolve(), *path.resolve().parents]:
                if "analysis_outputs" in path.parts:
                    dirnames[:] = []
                    continue

            for name in filenames:
                file_path = path / name
                ext = file_path.suffix.lower()
                if ext not in SOURCE_EXTENSIONS:
                    continue
                try:
                    stat = file_path.stat()
                    resolved = str(file_path.resolve())
                except OSError:
                    continue
                if resolved in seen:
                    continue
                seen.add(resolved)
                name_low = file_path.name.lower()
                full_low = str(file_path).lower()
                matched_terms = sorted(term for term in NAME_TERMS if term in full_low)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                is_recent = mtime >= cutoff_recent
                if not matched_terms and not is_recent:
                    continue

                score = 0
                score += 4 if ext in GEOMETRY_EXTENSIONS else 0
                score += 5 if ext in LAYOUT_EXTENSIONS else 0
                score += 2 * len(matched_terms)
                score += 4 if is_recent else 0
                score += 5 if any(term in name_low for term in ["magazine", "issue_24", "issue24", "toxic", "overdose"]) else 0
                score += 2 if any(term in name_low for term in ["scan", "photo", "canva", "source", "original"]) else 0

                rows.append(
                    {
                        "path": resolved,
                        "name": file_path.name,
                        "extension": ext,
                        "sizeBytes": stat.st_size,
                        "modified": mtime.isoformat(timespec="seconds"),
                        "recent36h": is_recent,
                        "matchedTerms": matched_terms,
                        "score": score,
                        "md5": md5_file(file_path),
                    }
                )
    return sorted(rows, key=lambda row: (-row["score"], row["path"]))


def classify(row: dict, known: set[str], known_hashes: dict[str, list[str]]) -> str:
    if row["path"] in known:
        return "known_inventory_item"
    if row.get("md5") and row["md5"] in known_hashes:
        return "duplicate_of_known_inventory"
    if row["extension"] in LAYOUT_EXTENSIONS:
        return "new_layout_or_source_candidate"
    if row["extension"] in GEOMETRY_EXTENSIONS and any(
        term in row["matchedTerms"] for term in ["magazine", "issue", "overdose", "toxic", "canva", "bitcoin"]
    ):
        return "new_geometry_candidate"
    if row["extension"] in {".docx", ".docm"} and any(
        term in row["matchedTerms"] for term in ["article", "font", "fonts", "bold", "keiser", "bitcoin", "toxic", "overdose"]
    ):
        return "new_text_or_formatting_candidate"
    return "low_priority_candidate"


def main() -> None:
    now = datetime.now()
    known, known_hashes = load_inventory()
    candidates = walk_candidates(now)
    for row in candidates:
        row["classification"] = classify(row, known, known_hashes)
        row["knownInLocalInventory"] = row["path"] in known
        row["duplicateOfKnownPaths"] = known_hashes.get(row.get("md5") or "", [])

    actionable = [
        row
        for row in candidates
        if row["classification"] in {"new_layout_or_source_candidate", "new_geometry_candidate", "new_text_or_formatting_candidate"}
    ]
    actionable_unknown = [row for row in actionable if not row["knownInLocalInventory"]]
    result = {
        "createdAt": now.isoformat(timespec="seconds"),
        "scope": "local source delta watch; no key derivation",
        "watchRoots": [str(path) for path in WATCH_ROOTS],
        "knownInventoryPathCount": len(known),
        "candidateCount": len(candidates),
        "actionableUnknownCount": len(actionable_unknown),
        "topCandidates": candidates[:30],
        "actionableUnknown": actionable_unknown[:30],
        "decision": "no_new_source_grade_candidate" if not actionable_unknown else "review_new_source_candidates",
        "assessment": [
            "This pass looks only for files that could change source geometry, visible layout, or formatting provenance.",
            "Known files remain useful in their existing roles: magazine.pdf as geometry truth, Article with Fonts.docm as formatting witness, and comparison PDFs as style-only controls.",
            "If `actionableUnknownCount` is zero, the current blocker remains unchanged: the missing extraction unit/order is not available in local source material.",
        ],
        "nextMove": "If a new physical scan/photo, original Canva export, layout source, or source-grade PDF appears, run the source gate and priority crop comparisons before any selector/key work.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Delta Watch",
        "",
        "Scope: check local folders for new source-grade puzzle material. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Watched roots: `{', '.join(result['watchRoots'])}`",
        f"- Candidate files scored: `{result['candidateCount']}`",
        f"- Actionable unknown source candidates: `{result['actionableUnknownCount']}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Actionable Unknown Candidates",
        "",
        "| class | score | modified | file | matched terms | duplicate of |",
        "|---|---:|---|---|---|",
    ]
    if actionable_unknown:
        for row in actionable_unknown[:30]:
            dup = ", ".join(row["duplicateOfKnownPaths"]) or "-"
            lines.append(
                f"| `{row['classification']}` | `{row['score']}` | `{row['modified']}` | `{row['path']}` | `{', '.join(row['matchedTerms'])}` | `{dup}` |"
            )
    else:
        lines.append("| - | - | - | none | - | - |")

    lines.extend(["", "## Top Scored Candidates", "", "| class | known | score | modified | file |", "|---|---|---:|---|---|"])
    for row in candidates[:15]:
        lines.append(
            f"| `{row['classification']}` | `{row['knownInLocalInventory']}` | `{row['score']}` | `{row['modified']}` | `{row['path']}` |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("actionableUnknownCount:", len(actionable_unknown))
    print("decision:", result["decision"])


if __name__ == "__main__":
    main()
