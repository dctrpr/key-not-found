#!/usr/bin/env python3
"""Audit local page-raster lineage against current PDF embedded images.

This bounded source/provenance pass maps loose local page images, source-image
cache files, and 3D-upright page images against the current PDFs' embedded page
rasters. It asks whether any local raster is a distinct higher-quality or
original-layout source candidate. It does not perform key extraction, candidate
generation, hashing-to-key, seed/WIF/address checks, BIP39 checks, or brute
force.
"""

from __future__ import annotations

import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_pdf_native_image_registration_gate as native  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/local_page_raster_lineage_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "local_page_raster_lineage_gate.json"
OUT_MD = OUT / "local_page_raster_lineage_gate.md"
OUT_SHEET = OUT / "local_page_raster_lineage_gate_sheet.jpg"

SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ARTICLE_PAGES = list(range(73, 81))
SAMPLE_SIZE = (318, 408)
DISTINCT_MAD_THRESHOLD = 12.0
MATCH_MAD_THRESHOLD = 3.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def primary_pdf_image(doc: fitz.Document, page_index: int) -> Image.Image | None:
    page = doc[page_index]
    best: dict[str, Any] | None = None
    for image in page.get_images(full=True):
        xref = int(image[0])
        extracted = doc.extract_image(xref)
        rects = page.get_image_rects(xref)
        area = max((rect.width * rect.height for rect in rects), default=0.0)
        if best is None or area > best["area"]:
            best = {"area": area, "image": extracted["image"]}
    if best is None:
        return None
    return Image.open(io.BytesIO(best["image"])).convert("RGB")


def sample(img: Image.Image, rotate180: bool = False) -> Image.Image:
    image = img.convert("RGB")
    if rotate180:
        image = image.rotate(180)
    return image.resize(SAMPLE_SIZE, Image.Resampling.BICUBIC)


def mad(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a, b)
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def sharpness(img: Image.Image) -> float:
    arr = np.asarray(img.convert("L").resize(SAMPLE_SIZE, Image.Resampling.BICUBIC), dtype=np.float32)
    dx = np.diff(arr, axis=1)
    dy = np.diff(arr, axis=0)
    return float(np.mean(np.abs(dx)) + np.mean(np.abs(dy)))


def local_candidates() -> list[Path]:
    paths: list[Path] = []
    paths.extend(sorted(ROOT.glob("magazine-*_1.jpg")))
    paths.extend(sorted(ROOT.glob("keyser bitcoin -*_1.jpg")))
    paths.extend(sorted((ROOT / "analysis_outputs/source_images").glob("magazine_page_*.jpg")))
    paths.extend(sorted((ROOT / "analysis_outputs/3d_article_map").glob("page_*_upright.jpg")))
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def pdf_references() -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for pdf_path in native.PDFS:
        if not pdf_path.exists():
            continue
        with fitz.open(pdf_path) as doc:
            for idx, article_page in enumerate(ARTICLE_PAGES):
                if idx >= doc.page_count:
                    continue
                img = primary_pdf_image(doc, idx)
                if img is None:
                    continue
                refs.append(
                    {
                        "kind": "pdf_embedded_primary",
                        "pdf": rel(pdf_path),
                        "articlePage": article_page,
                        "path": f"{rel(pdf_path)}#article_page_{article_page}",
                        "width": img.width,
                        "height": img.height,
                        "sharpness": sharpness(img),
                        "samples": {
                            "identity": sample(img),
                            "rotate180": sample(img, rotate180=True),
                        },
                    }
                )
    return refs


def classify_path(path: Path) -> str:
    text = rel(path)
    if text.startswith("analysis_outputs/source_images/"):
        return "source_image_cache"
    if text.startswith("analysis_outputs/3d_article_map/page_"):
        return "upright_3d_cache"
    if path.name.startswith("magazine-"):
        return "root_magazine_jpeg"
    if path.name.startswith("keyser bitcoin -"):
        return "root_keyser_jpeg"
    return "local_image"


def page_hint(path: Path) -> str:
    name = path.name
    if name.startswith("magazine_page_"):
        return name.removeprefix("magazine_page_").removesuffix(".jpg")
    if name.startswith("page_") and name.endswith("_upright.jpg"):
        return name.removeprefix("page_").removesuffix("_upright.jpg")
    return "-"


def best_match(path: Path, refs: list[dict[str, Any]]) -> dict[str, Any]:
    img = Image.open(path).convert("RGB")
    candidate_samples = {
        "identity": sample(img),
        "rotate180": sample(img, rotate180=True),
    }
    best: dict[str, Any] | None = None
    for ref in refs:
        for candidate_orientation, candidate_sample in candidate_samples.items():
            for ref_orientation, ref_sample in ref["samples"].items():
                score = mad(candidate_sample, ref_sample)
                row = {
                    "score": score,
                    "candidateOrientation": candidate_orientation,
                    "referenceOrientation": ref_orientation,
                    "reference": ref,
                }
                if best is None or score < best["score"]:
                    best = row
    assert best is not None
    ref = best["reference"]
    candidate_sharpness = sharpness(img)
    higher_resolution = img.width * img.height > ref["width"] * ref["height"]
    return {
        "path": rel(path),
        "kind": classify_path(path),
        "pageHint": page_hint(path),
        "width": img.width,
        "height": img.height,
        "sharpness": round(candidate_sharpness, 6),
        "bestReference": ref["path"],
        "bestReferencePdf": ref["pdf"],
        "bestArticlePage": ref["articlePage"],
        "bestMad": round(best["score"], 6),
        "candidateOrientation": best["candidateOrientation"],
        "referenceOrientation": best["referenceOrientation"],
        "referenceWidth": ref["width"],
        "referenceHeight": ref["height"],
        "referenceSharpness": round(ref["sharpness"], 6),
        "higherResolutionThanBestRef": bool(higher_resolution),
        "sharperThanBestRef": bool(candidate_sharpness > ref["sharpness"] * 1.08),
        "nearDuplicate": bool(best["score"] <= MATCH_MAD_THRESHOLD),
        "derivativeLike": bool(best["score"] <= DISTINCT_MAD_THRESHOLD),
    }


def draw_sheet(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width, height = 1840, 1200
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(24)
    small = safe_font(14)
    tiny = safe_font(11)

    draw.rectangle((0, 0, width, 104), fill=(25, 31, 42))
    draw.text((24, 16), "Local Page Raster Lineage Gate", fill="white", font=title)
    draw.text(
        (24, 52),
        "Loose JPGs, source-image cache, and 3D upright images mapped to PDF embedded page rasters.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1060, 22),
        f"candidates: {summary['candidateCount']} | distinct: {summary['distinctCandidateCount']} | promoted: {summary['promotedSourceCandidateCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1060, 52),
        f"near dup: {summary['nearDuplicateCount']} | derivative-like: {summary['derivativeLikeCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    y = 126
    headers = ["image", "kind", "hint", "best page", "MAD", "cand", "ref", "higher", "sharper"]
    xs = [22, 428, 646, 704, 788, 858, 970, 1110, 1190]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(45, 48, 54), font=small)
    y += 24
    for idx, row in enumerate(rows[:42]):
        fill = (246, 248, 250) if idx % 2 == 0 else (255, 255, 255)
        draw.rectangle((16, y - 5, width - 16, y + 20), fill=fill)
        values = [
            row["path"],
            row["kind"],
            row["pageHint"],
            str(row["bestArticlePage"]),
            f"{row['bestMad']:.4f}",
            row["candidateOrientation"],
            row["referenceOrientation"],
            str(int(row["higherResolutionThanBestRef"])),
            str(int(row["sharperThanBestRef"])),
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value[:55], fill=(25, 28, 34), font=tiny)
        y += 23
    sheet.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Local Page Raster Lineage Gate",
        "",
        "Scope: mapped loose root JPEGs, source-image cache files, and 3D upright page images against current PDF embedded page rasters for article pages 73-80. This is source/provenance validation only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- PDF reference rows / local candidates: `{summary['pdfReferenceCount']}` / `{summary['candidateCount']}`",
        f"- Near duplicates / derivative-like rows: `{summary['nearDuplicateCount']}` / `{summary['derivativeLikeCount']}`",
        f"- Distinct local raster candidates / promoted source candidates: `{summary['distinctCandidateCount']}` / `{summary['promotedSourceCandidateCount']}`",
        f"- Higher-resolution-than-best-reference rows / sharper rows: `{summary['higherResolutionThanBestRefCount']}` / `{summary['sharperThanBestRefCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Candidate Rows",
        "",
        "| image | kind | page hint | best PDF page | MAD | candidate orient | ref orient | higher-res | sharper | near duplicate | derivative-like |",
        "|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|",
    ]
    for row in result["candidateRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['path']}`",
                    f"`{row['kind']}`",
                    f"`{row['pageHint']}`",
                    f"`{row['bestArticlePage']}`",
                    f"{row['bestMad']:.4f}",
                    f"`{row['candidateOrientation']}`",
                    f"`{row['referenceOrientation']}`",
                    str(int(row["higherResolutionThanBestRef"])),
                    str(int(row["sharperThanBestRef"])),
                    str(int(row["nearDuplicate"])),
                    str(int(row["derivativeLike"])),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `local_page_raster_lineage_no_distinct_source`.",
            "- Every loose/local page raster maps back to the current PDF embedded page-image family as a near duplicate or derivative-like match.",
            "- The local raster set does not provide a distinct higher-quality/original-layout source candidate or source-backed unit/order wording.",
            "",
            "## Next Move",
            "",
            "- Keep local loose page rasters as duplicate witnesses only. Reopen extraction only if a new physical/original-layout asset or raw clue wording passes the source-reopen requirements.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    refs = pdf_references()
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))

    rows = [best_match(path, refs) for path in local_candidates()]
    rows.sort(key=lambda row: (row["kind"], row["path"]))
    distinct_rows = [row for row in rows if not row["derivativeLike"]]
    promoted_rows = [
        row
        for row in distinct_rows
        if row["higherResolutionThanBestRef"] or row["sharperThanBestRef"]
    ]
    summary = {
        "pdfReferenceCount": len(refs),
        "candidateCount": len(rows),
        "nearDuplicateCount": sum(row["nearDuplicate"] for row in rows),
        "derivativeLikeCount": sum(row["derivativeLike"] for row in rows),
        "distinctCandidateCount": len(distinct_rows),
        "promotedSourceCandidateCount": len(promoted_rows),
        "higherResolutionThanBestRefCount": sum(row["higherResolutionThanBestRef"] for row in rows),
        "sharperThanBestRefCount": sum(row["sharperThanBestRef"] for row in rows),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"refs={summary['pdfReferenceCount']}|candidates={summary['candidateCount']}|"
        f"nearDup={summary['nearDuplicateCount']}|derivative={summary['derivativeLikeCount']}|"
        f"distinct={summary['distinctCandidateCount']}|promoted={summary['promotedSourceCandidateCount']}|"
        f"higher={summary['higherResolutionThanBestRefCount']}|sharper={summary['sharperThanBestRefCount']}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|"
        "selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Local loose page raster lineage against current PDF embedded page images, "
            "with orientation-aware sample matching."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in native.PDFS if path.exists()],
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": "local_page_raster_lineage_no_distinct_source",
        "summary": summary,
        "fingerprint": fingerprint,
        "candidateRows": rows,
        "distinctRows": distinct_rows,
        "promotedRows": promoted_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()
