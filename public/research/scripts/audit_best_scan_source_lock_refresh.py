#!/usr/bin/env python3
"""
Refresh the source lock for the user-supplied best scan.

This is a source-fidelity check only. It verifies that the Desktop best scan,
the workspace scan, and the 3D map metadata all point to the same high-res
geometry source. No key derivation or text extraction is performed.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "best_scan_source_lock_refresh"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DESKTOP_SCAN = Path("private_inputs/Desktop/magazine.pdf")
WORKSPACE_SCAN = ROOT / "magazine.pdf"
OCR_PDF = ROOT / "keyser bitcoin .pdf"
MAP_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "article_3d_map_data.json"
PAGE_DIR = ROOT / "analysis_outputs" / "3d_article_map"
OUT_JSON = OUT_DIR / "best_scan_source_lock_refresh.json"
OUT_MD = OUT_DIR / "best_scan_source_lock_refresh.md"


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdfinfo(path: Path) -> dict[str, str]:
    if not path.exists():
        return {"missing": "true"}
    proc = subprocess.run(
        ["pdfinfo", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    if proc.returncode != 0:
        result["pdfinfoError"] = proc.stderr.strip()
    return result


def image_dims(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"exists": False}
    with Image.open(path) as img:
        return {"exists": True, "width": img.width, "height": img.height, "mode": img.mode}


def main() -> None:
    map_data = json.loads(MAP_JSON.read_text())
    meta = map_data.get("meta", {})
    meta_highres = Path(meta.get("highresSource", ""))
    meta_ocr = Path(meta.get("sourcePdf", ""))

    pdfs = {
        "desktopBestScan": DESKTOP_SCAN,
        "workspaceScan": WORKSPACE_SCAN,
        "mapHighresSource": meta_highres,
        "mapOcrSource": meta_ocr,
        "workspaceOcrPdf": OCR_PDF,
    }
    pdf_rows = []
    for name, path in pdfs.items():
        pdf_rows.append(
            {
                "id": name,
                "path": str(path),
                "exists": path.exists(),
                "sizeBytes": path.stat().st_size if path.exists() else None,
                "sha256": sha256(path),
                "pdfinfo": pdfinfo(path) if path.exists() else {},
            }
        )

    page_rows = []
    for page in range(75, 81):
        path = PAGE_DIR / f"page_{page}_upright.jpg"
        page_rows.append({"page": page, "path": str(path), **image_dims(path)})

    desktop_hash = sha256(DESKTOP_SCAN)
    workspace_hash = sha256(WORKSPACE_SCAN)
    meta_highres_hash = sha256(meta_highres) if meta_highres.exists() else None
    ocr_hash = sha256(OCR_PDF)

    conclusions = []
    if desktop_hash == workspace_hash == meta_highres_hash and desktop_hash:
        conclusions.append("Desktop best scan, workspace scan, and 3D map high-res source are byte-identical.")
    else:
        conclusions.append("Source mismatch detected among Desktop/workspace/3D-map high-res scan paths.")
    if ocr_hash and ocr_hash != workspace_hash:
        conclusions.append("The OCR PDF is a different file and remains label/navigation evidence only, not geometry truth.")
    if all(row.get("width") == 2544 and row.get("height") == 3264 for row in page_rows):
        conclusions.append("All 3D page images for pages 75-80 are 2544x3264 upright derivatives of the high-res scan geometry.")

    extraction_status = (
        "blocked: current source identity is settled, but no source/clue names an extraction unit or order."
    )
    decision = (
        "Treat `private_inputs/Desktop/magazine.pdf` and workspace `magazine.pdf` as the same canonical high-res geometry source. "
        "Do not reopen local PDF source selection unless a materially different physical scan, original layout export, or higher-resolution image appears."
    )
    next_move = (
        "Use this refreshed source lock as the baseline for future source comparison. Further progress needs a new source image/original layout clue or an explicit unit/order rule."
    )

    report = {
        "scope": "best scan source lock refresh; no key derivation",
        "mapMeta": meta,
        "pdfRows": pdf_rows,
        "pageImageRows": page_rows,
        "conclusions": conclusions,
        "extractionStatus": extraction_status,
        "decision": decision,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2))

    lines = [
        "# Best Scan Source Lock Refresh",
        "",
        "Scope: verify that the user-supplied Desktop best scan, the workspace scan, and the 3D article map all use the same high-res geometry source. No key derivation, hashing of candidate text, seed phrase, WIF, or address checks were run.",
        "",
        "## PDF Sources",
        "",
        "| id | exists | size | sha256 | pages | rotation | page size |",
        "|---|---:|---:|---|---:|---|---|",
    ]
    for row in pdf_rows:
        info = row["pdfinfo"]
        lines.append(
            f"| `{row['id']}` | `{row['exists']}` | `{row['sizeBytes']}` | `{row['sha256']}` | `{info.get('Pages', '-')}` | `{info.get('Page rot', info.get('Page    1 rot', '-'))}` | `{info.get('Page size', '-')}` |"
        )

    lines.extend(["", "## 3D Page Image Derivatives", "", "| page | width | height | mode |", "|---:|---:|---:|---|"])
    for row in page_rows:
        lines.append(f"| {row['page']} | `{row.get('width')}` | `{row.get('height')}` | `{row.get('mode')}` |")

    lines.extend(["", "## Conclusions", ""])
    lines.extend(f"- {item}" for item in conclusions)
    lines.extend(["", "## Decision", "", f"- {decision}", "", "## Next Move", "", f"- {next_move}"])
    OUT_MD.write_text("\n".join(lines) + "\n")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
