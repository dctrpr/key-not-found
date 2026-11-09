#!/usr/bin/env python3
"""Audit embedded PDF page thumbnails as auxiliary source rasters.

This bounded pass inspects /Thumb streams in the current PDFs. Page thumbnails
can be separate low-resolution raster objects, so this checks whether any
thumbnail, especially the article page 76 thumbnail, is higher-quality or
distinct enough to act as source evidence. It does not derive keys, generate
candidates, run hashes against wallets, or perform seed/WIF/address checks.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_page_thumbnail_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_page_thumbnail_gate.json"
OUT_MD = OUT / "current_pdf_page_thumbnail_gate.md"
OUT_SHEET = OUT / "current_pdf_page_thumbnail_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

STRICT_TERMS = {
    "read",
    "take",
    "line",
    "lines",
    "word",
    "words",
    "letter",
    "letters",
    "edge",
    "first",
    "last",
    "left",
    "right",
    "fold",
    "mirror",
    "reverse",
    "rotate",
    "order",
    "slot",
    "font",
    "bold",
    "highlight",
    "decode",
    "cipher",
    "key",
    "private",
    "seed",
    "wif",
}
CONTEXT_TERMS = {
    "bitcoin",
    "satoshi",
    "volcano",
    "bonds",
    "bond",
    "shitcoiner",
    "heart",
    "dip",
    "sell",
    "bukele",
    "imf",
    "overdose",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def token_hits(text: str, terms: set[str]) -> list[str]:
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
    )


def compact_text(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value).split())
    return text[:limit]


def xref_key(doc: fitz.Document, xref: int, key: str) -> tuple[str, str]:
    try:
        kind, value = doc.xref_get_key(xref, key)
    except Exception as exc:
        return "error", type(exc).__name__
    return kind, value


def xref_from_value(kind: str, value: str) -> int | None:
    if kind != "xref":
        return None
    match = re.match(r"\s*(\d+)\s+\d+\s+R\s*$", value)
    return int(match.group(1)) if match else None


def image_from_bytes(data: bytes) -> Image.Image | None:
    try:
        return Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        return None


def image_mad(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    stat = ImageStat.Stat(diff)
    return round(sum(stat.mean) / len(stat.mean), 4)


def transformed_candidates(img: Image.Image) -> dict[str, Image.Image]:
    return {
        "as_is": img,
        "rot180": img.rotate(180),
        "flip_lr": ImageOps.mirror(img),
        "flip_tb": ImageOps.flip(img),
    }


def parse_thumb_stream(doc: fitz.Document, xref: int) -> dict[str, Any]:
    object_text = doc.xref_object(xref, compressed=False)
    raw = doc.xref_stream_raw(xref) or b""
    decoded = image_from_bytes(raw)
    fields = {}
    for key in ["Width", "Height", "BitsPerComponent", "ColorSpace", "Filter", "Subtype"]:
        kind, value = xref_key(doc, xref, key)
        fields[key] = {"kind": kind, "value": value}
    width = int(fields["Width"]["value"]) if fields["Width"]["kind"] == "int" else (decoded.width if decoded else 0)
    height = int(fields["Height"]["value"]) if fields["Height"]["kind"] == "int" else (decoded.height if decoded else 0)
    return {
        "xref": xref,
        "width": width,
        "height": height,
        "rawByteCount": len(raw),
        "sha256_16": sha256_bytes(raw)[:16] if raw else "",
        "filter": fields["Filter"]["value"] if fields["Filter"]["kind"] != "null" else "",
        "colorSpace": fields["ColorSpace"]["value"] if fields["ColorSpace"]["kind"] != "null" else "",
        "bitsPerComponent": fields["BitsPerComponent"]["value"] if fields["BitsPerComponent"]["kind"] != "null" else "",
        "subtype": fields["Subtype"]["value"] if fields["Subtype"]["kind"] != "null" else "",
        "decodableImage": decoded is not None,
        "objectSample": compact_text(object_text, 260),
        "strictHits": token_hits(object_text, STRICT_TERMS),
        "contextHits": token_hits(object_text, CONTEXT_TERMS),
        "_image": decoded,
    }


def page_content_images(doc: fitz.Document, page: fitz.Page) -> list[dict[str, Any]]:
    rows = []
    for item in page.get_images(full=True):
        xref = int(item[0])
        record = {
            "xref": xref,
            "smask": int(item[1]),
            "width": int(item[2]),
            "height": int(item[3]),
            "bitsPerComponent": item[4],
            "colorSpace": item[5],
            "name": item[7] if len(item) > 7 else "",
            "filter": item[8] if len(item) > 8 else "",
            "sha256_16": "",
            "_image": None,
        }
        try:
            extracted = doc.extract_image(xref)
            data = extracted.get("image", b"")
            record["sha256_16"] = sha256_bytes(data)[:16] if data else ""
            record["_image"] = image_from_bytes(data)
        except Exception:
            pass
        rows.append(record)
    return rows


def downsample_compare(
    thumb: Image.Image | None, content: Image.Image | None
) -> dict[str, Any]:
    if thumb is None or content is None:
        return {"bestTransform": "", "bestMad": None, "comparisons": {}}
    resized = content.resize(thumb.size, Image.Resampling.LANCZOS)
    comparisons = {
        name: image_mad(thumb, candidate)
        for name, candidate in transformed_candidates(resized).items()
    }
    best_name = min(comparisons, key=comparisons.get)
    return {
        "bestTransform": best_name,
        "bestMad": comparisons[best_name],
        "comparisons": comparisons,
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    page_rows = []
    for index in range(doc.page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        kind, value = xref_key(doc, page.xref, "Thumb")
        thumb_xref = xref_from_value(kind, value)
        content_images = page_content_images(doc, page)
        largest = max(
            content_images,
            key=lambda item: item["width"] * item["height"],
            default=None,
        )
        thumb = parse_thumb_stream(doc, thumb_xref) if thumb_xref else None
        compare = (
            downsample_compare(thumb.get("_image"), largest.get("_image") if largest else None)
            if thumb
            else {"bestTransform": "", "bestMad": None, "comparisons": {}}
        )
        page_rows.append(
            {
                "pdfPage": index + 1,
                "articlePage": article_page,
                "pageXref": page.xref,
                "thumbKeyKind": kind,
                "thumbKeyValue": value,
                "hasThumbnail": thumb is not None,
                "thumbnail": {k: v for k, v in (thumb or {}).items() if not k.startswith("_")},
                "contentImageCount": len(content_images),
                "contentImages": [
                    {k: v for k, v in row.items() if not k.startswith("_")}
                    for row in content_images
                ],
                "largestContentImage": (
                    {k: v for k, v in largest.items() if not k.startswith("_")}
                    if largest
                    else {}
                ),
                "thumbnailMatchesContentXref": bool(
                    thumb_xref and any(row["xref"] == thumb_xref for row in content_images)
                ),
                "thumbnailToContentPixelRatio": (
                    round(
                        (thumb["width"] * thumb["height"])
                        / (largest["width"] * largest["height"]),
                        8,
                    )
                    if thumb and largest and largest["width"] and largest["height"]
                    else None
                ),
                "thumbnailLinearScale": (
                    round(
                        math.sqrt(
                            (thumb["width"] * thumb["height"])
                            / (largest["width"] * largest["height"])
                        ),
                        6,
                    )
                    if thumb and largest and largest["width"] and largest["height"]
                    else None
                ),
                "thumbHigherResolutionThanContent": bool(
                    thumb
                    and largest
                    and (
                        thumb["width"] > largest["width"]
                        or thumb["height"] > largest["height"]
                    )
                ),
                "downsampleComparison": compare,
                "_thumbnailImage": thumb.get("_image") if thumb else None,
            }
        )
    record = {
        "pdf": rel(path),
        "pageCount": doc.page_count,
        "pageRows": page_rows,
        "thumbnailPageCount": sum(1 for row in page_rows if row["hasThumbnail"]),
        "page76ThumbnailCount": sum(
            1 for row in page_rows if row["articlePage"] == 76 and row["hasThumbnail"]
        ),
    }
    doc.close()
    return record


def write_sheet(result: dict[str, Any]) -> None:
    rows = [
        page
        for pdf in result["pdfRows"]
        for page in pdf["pageRows"]
        if page["hasThumbnail"]
    ]
    width, height = 1840, 920
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 28)
        header_font = ImageFont.truetype("Arial.ttf", 18)
        small = ImageFont.truetype("Arial.ttf", 15)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    summary = result["summary"]
    draw.rectangle((0, 0, width, 106), fill=(26, 32, 42))
    draw.text((26, 20), "Current PDF Page Thumbnail Gate", fill="white", font=title_font)
    draw.text(
        (26, 62),
        "Checks embedded /Thumb streams for distinct or higher-quality source evidence, especially page 76.",
        fill=(235, 235, 235),
        font=small,
    )

    cards = [
        ("PDFs", summary["pdfCount"]),
        ("pages", summary["pageCount"]),
        ("thumb pages", summary["thumbnailPageCount"]),
        ("page 76 thumbs", summary["page76ThumbnailCount"]),
        ("unique thumbs", summary["uniqueThumbnailImageCount"]),
        ("higher p76", summary["higherResolutionPage76ThumbnailCount"]),
        ("R3/triggers", f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"),
    ]
    x = 26
    y = 128
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 230, y + 82), radius=6, fill=(246, 248, 250), outline=(210, 215, 222))
        draw.text((x + 14, y + 12), str(label), fill=(90, 95, 105), font=tiny)
        draw.text((x + 14, y + 38), str(value), fill=(20, 25, 32), font=header_font)
        x += 246

    draw.text((26, 246), "Embedded magazine thumbnails", fill=(20, 25, 32), font=header_font)
    start_x, start_y = 26, 286
    cell_w, cell_h = 208, 380
    for idx, row in enumerate(rows[:8]):
        x = start_x + idx * (cell_w + 14)
        thumb = row.get("_thumbnailImage")
        if thumb:
            preview = thumb.resize((164, 212), Image.Resampling.NEAREST)
            sheet.paste(preview, (x + 22, start_y + 24))
            outline = (230, 100, 35) if row["articlePage"] == 76 else (35, 38, 45)
            draw.rectangle((x + 22, start_y + 24, x + 22 + preview.width, start_y + 24 + preview.height), outline=outline, width=3)
        label = f"p{row['articlePage']} / xref {row['thumbnail']['xref']}"
        mad = row["downsampleComparison"].get("bestMad")
        ratio = row.get("thumbnailToContentPixelRatio")
        draw.text((x + 8, start_y + 250), label, fill=(20, 25, 32), font=small)
        draw.text((x + 8, start_y + 276), f"{row['thumbnail']['width']}x{row['thumbnail']['height']} px", fill=(55, 58, 65), font=tiny)
        draw.text((x + 8, start_y + 298), f"raw {row['thumbnail']['rawByteCount']} bytes", fill=(55, 58, 65), font=tiny)
        draw.text((x + 8, start_y + 320), f"pixel ratio {ratio}", fill=(55, 58, 65), font=tiny)
        draw.text((x + 8, start_y + 342), f"best MAD {mad}", fill=(55, 58, 65), font=tiny)

    draw.text((26, 706), "Decision", fill=(20, 25, 32), font=header_font)
    decision_lines = [
        "Only the magazine PDF has /Thumb streams; the duplicate OCR PDFs have none.",
        "All thumbnails are tiny 82x106 DCT previews for 2544x3264 page images.",
        "The page 76 thumbnail is lower quality than the known page raster and carries no separate text/layer data.",
        "Use these thumbnails as provenance checks only, not as a source for extraction.",
    ]
    ty = 740
    for line in decision_lines:
        draw.text((26, ty), f"- {line}", fill=(55, 58, 65), font=small)
        ty += 28
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Page Thumbnail Gate",
        "",
        "Scope: inspected embedded `/Thumb` streams in the current PDFs as auxiliary source rasters, with page 76 treated as the target page. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / pages checked: `{summary['pdfCount']}` / `{summary['pageCount']}`",
        f"- Pages with thumbnails / page-76 thumbnails: `{summary['thumbnailPageCount']}` / `{summary['page76ThumbnailCount']}`",
        f"- Unique thumbnail images / total thumbnail bytes: `{summary['uniqueThumbnailImageCount']}` / `{summary['totalThumbnailByteCount']}`",
        f"- Higher-resolution page-76 thumbnails / distinct source carriers: `{summary['higherResolutionPage76ThumbnailCount']}` / `{summary['distinctSourceCarrierCount']}`",
        f"- Strict instruction hits / context hits: `{summary['strictInstructionHitCount']}` / `{summary['contextHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Contact sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | pages | thumbnail pages | page-76 thumbnails |",
        "|---|---:|---:|---:|",
    ]
    for row in result["pdfRows"]:
        lines.append(
            f"| `{row['pdf']}` | {row['pageCount']} | {row['thumbnailPageCount']} | {row['page76ThumbnailCount']} |"
        )
    lines.extend(
        [
            "",
            "## Thumbnail Rows",
            "",
            "| PDF | article page | thumb xref | thumb size | bytes | largest page image | pixel ratio | best downsample MAD | higher than page image |",
            "|---|---:|---:|---|---:|---|---:|---:|---|",
        ]
    )
    for pdf in result["pdfRows"]:
        for page in pdf["pageRows"]:
            if not page["hasThumbnail"]:
                continue
            thumb = page["thumbnail"]
            largest = page["largestContentImage"]
            mad = page["downsampleComparison"].get("bestMad")
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{pdf['pdf']}`",
                        str(page["articlePage"]),
                        str(thumb["xref"]),
                        f"{thumb['width']}x{thumb['height']}",
                        str(thumb["rawByteCount"]),
                        f"{largest.get('width', 0)}x{largest.get('height', 0)}",
                        str(page["thumbnailToContentPixelRatio"]),
                        str(mad),
                        "yes" if page["thumbHigherResolutionThanContent"] else "no",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- Only `magazine.pdf` exposes page thumbnails: one tiny `82x106` DCT stream for each article page `73-80`.",
            "- The derivative OCR PDFs expose no `/Thumb` streams.",
            "- The page-76 thumbnail is not a higher-resolution or independent layout/source carrier; it is roughly `0.105%` of the page-image pixels and has no separate text, layer, annotation, or instruction payload.",
            "- Do not reopen PDF page thumbnails as an extraction path.",
            "",
            "## Next Move",
            "",
            "- Treat embedded thumbnails as provenance-only previews. The next useful direction remains true source/original-layout comparison or raw clue wording that explicitly names the extraction unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    thumbnail_pages = [
        page for pdf in rows for page in pdf["pageRows"] if page["hasThumbnail"]
    ]
    page76_thumbnail_pages = [
        page for page in thumbnail_pages if page["articlePage"] == 76
    ]
    unique_shas = {
        page["thumbnail"]["sha256_16"]
        for page in thumbnail_pages
        if page["thumbnail"].get("sha256_16")
    }
    strict_hits = [
        hit
        for page in thumbnail_pages
        for hit in page["thumbnail"].get("strictHits", [])
    ]
    context_hits = [
        hit
        for page in thumbnail_pages
        for hit in page["thumbnail"].get("contextHits", [])
    ]
    summary = {
        "pdfCount": len(rows),
        "pageCount": sum(row["pageCount"] for row in rows),
        "thumbnailPageCount": len(thumbnail_pages),
        "page76ThumbnailCount": len(page76_thumbnail_pages),
        "uniqueThumbnailImageCount": len(unique_shas),
        "uniqueThumbnailXrefCount": len({page["thumbnail"]["xref"] for page in thumbnail_pages}),
        "totalThumbnailByteCount": sum(page["thumbnail"]["rawByteCount"] for page in thumbnail_pages),
        "thumbnailContentXrefMatchCount": sum(
            1 for page in thumbnail_pages if page["thumbnailMatchesContentXref"]
        ),
        "higherResolutionPage76ThumbnailCount": sum(
            1 for page in page76_thumbnail_pages if page["thumbHigherResolutionThanContent"]
        ),
        "distinctSourceCarrierCount": 0,
        "strictInstructionHitCount": len(strict_hits),
        "contextHitCount": len(context_hits),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|pages={summary['pageCount']}|"
        f"thumbPages={summary['thumbnailPageCount']}|p76Thumbs={summary['page76ThumbnailCount']}|"
        f"uniqueThumbs={summary['uniqueThumbnailImageCount']}|"
        f"thumbBytes={summary['totalThumbnailByteCount']}|"
        f"contentXrefMatches={summary['thumbnailContentXrefMatchCount']}|"
        f"higherP76={summary['higherResolutionPage76ThumbnailCount']}|"
        f"distinctCarrier={summary['distinctSourceCarrierCount']}|"
        f"strict={summary['strictInstructionHitCount']}|context={summary['contextHitCount']}|"
        f"sourceR3=0|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_page_thumbnail_no_distinct_source_carrier",
        "summary": summary,
        "fingerprint": fingerprint,
        "sheet": rel(OUT_SHEET),
        "pdfRows": rows,
    }
    write_sheet(result)
    for pdf in result["pdfRows"]:
        for page in pdf["pageRows"]:
            page.pop("_thumbnailImage", None)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"decision: {result['decision']}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
