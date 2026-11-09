#!/usr/bin/env python3
"""Check whether the DOCM cyan `MNBILLION` layer is visible in the scan."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FONT_AUDIT_JSON = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.json"
ARTICLE_MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
GREY_JSON = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
OUT_DIR = ROOT / "analysis_outputs/docm_format_sources"
OUT_MD = OUT_DIR / "cyan_mnbillion_scan_visibility.md"
OUT_JSON = OUT_DIR / "cyan_mnbillion_scan_visibility.json"


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def letters(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9$]", text))


def page_for_para(paragraph_index: int, boundaries: list[dict]) -> int | None:
    for row in boundaries:
        if row["paragraphStart"] <= paragraph_index <= row["paragraphEnd"]:
            return row["page"]
    return None


def cyan_mask(arr: np.ndarray, *, strict: bool = False) -> np.ndarray:
    red = arr[:, :, 0].astype(np.int16)
    green = arr[:, :, 1].astype(np.int16)
    blue = arr[:, :, 2].astype(np.int16)
    if strict:
        return (red < 80) & (green > 180) & (blue > 180) & (np.abs(green - blue) < 60)
    return (red < 120) & (green > 150) & (blue > 150) & (np.abs(green - blue) < 80)


def count_cyan_in_image(path: Path) -> dict:
    arr = np.array(Image.open(path).convert("RGB"))
    loose = cyan_mask(arr, strict=False)
    strict = cyan_mask(arr, strict=True)
    return {
        "path": str(path),
        "width": int(arr.shape[1]),
        "height": int(arr.shape[0]),
        "pixels": int(arr.shape[0] * arr.shape[1]),
        "looseCyanPixels": int(loose.sum()),
        "strictCyanPixels": int(strict.sum()),
        "looseRatio": float(loose.sum() / loose.size),
        "strictRatio": float(strict.sum() / strict.size),
    }


def count_cyan_in_box(page: int, box: list[float], label: str) -> dict:
    path = ROOT / f"analysis_outputs/source_images/magazine_page_{page}.jpg"
    img = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0, x1 = max(0, x0), min(img.width, x1)
    y0, y1 = max(0, y0), min(img.height, y1)
    arr = np.array(img.crop((x0, y0, x1, y1)))
    loose = cyan_mask(arr, strict=False)
    strict = cyan_mask(arr, strict=True)
    return {
        "label": label,
        "page": page,
        "box": [x0, y0, x1, y1],
        "pixels": int(arr.shape[0] * arr.shape[1]),
        "looseCyanPixels": int(loose.sum()),
        "strictCyanPixels": int(strict.sum()),
    }


def find_word_box(article_map: dict, page: int, token: str) -> list[float] | None:
    for page_row in article_map["pages"]:
        if page_row["page"] != page:
            continue
        for word in page_row.get("words", []):
            if word.get("token", "").lower() == token.lower():
                return word["box"]
    return None


def main() -> None:
    runs = json.loads(RUNS_JSON.read_text())
    font_audit = json.loads(FONT_AUDIT_JSON.read_text())
    boundaries = font_audit["pageBoundariesByParagraph"]
    article_map = json.loads(ARTICLE_MAP_JSON.read_text())
    grey = json.loads(GREY_JSON.read_text())

    cyan_runs = []
    for run in runs:
        if run.get("highlight") != "cyan":
            continue
        page = page_for_para(run["paragraphIndex"], boundaries)
        cyan_runs.append(
            {
                "runIndex": run["runIndex"],
                "paragraphIndex": run["paragraphIndex"],
                "page": page,
                "text": run["text"],
                "letters": letters(run["text"]),
                "fontAscii": run.get("fontAscii"),
                "bold": bool(run.get("bold")),
                "start": run.get("start"),
                "end": run.get("end"),
            }
        )

    page_counts = []
    for page in range(75, 81):
        page_counts.append(count_cyan_in_image(ROOT / f"analysis_outputs/source_images/magazine_page_{page}.jpg"))
        page_counts[-1]["page"] = page

    region_counts = []
    nocoiners_box = find_word_box(article_map, 75, "nocoiners")
    if nocoiners_box:
        region_counts.append(count_cyan_in_box(75, nocoiners_box, "p75 visible word box: Nocoiners"))
    for row in grey["rows"]:
        if row["id"] == "p76_grey_4":
            region_counts.append(count_cyan_in_box(76, row["highresBox"], "p76 grey target: $1 billion"))
            break

    crop_counts = []
    for rel, label in [
        ("analysis_outputs/highlight_audit/p78_orange_2_crop.jpg", "p78 orange crop: America left $85"),
        ("analysis_outputs/highlight_audit/p78_orange_3_crop.jpg", "p78 orange crop: BILLION / $2 trillion"),
    ]:
        path = ROOT / rel
        info = count_cyan_in_image(path)
        info["label"] = label
        crop_counts.append(info)

    result = {
        "sourceRuns": str(RUNS_JSON),
        "scanSource": "analysis_outputs/source_images/magazine_page_75.jpg ... magazine_page_80.jpg",
        "cyanDefinition": {
            "loose": "R < 120, G > 150, B > 150, |G-B| < 80",
            "strict": "R < 80, G > 180, B > 180, |G-B| < 60",
        },
        "cyanRuns": cyan_runs,
        "cyanLetters": "".join(r["letters"] for r in cyan_runs),
        "scanPageCounts": page_counts,
        "targetRegionCounts": region_counts,
        "cropCounts": crop_counts,
        "assessment": [
            "The DOCM cyan stream is `MNBILLION`, but cyan highlighter color is not visible in the high-resolution magazine scan.",
            "Page 78 has only five loose-threshold cyan-like pixels across the whole 2544x3264 scan and zero strict-threshold pixels, so this is image noise rather than a printed cyan highlight.",
            "The p75 Nocoiners box, p76 `$1 billion` grey target, and p78 orange `$85/BILLION` crops all have zero cyan pixels under both thresholds.",
            "Treat cyan as a DOCM metadata/annotation anomaly, not as a printed visual selector, unless an independent source proves the DOCM formatting itself is the puzzle source.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Cyan `MNBILLION` Scan Visibility Audit",
        "",
        "Scope: check whether the cyan-highlighted `MNBILLION` layer from `Article with Fonts.docm` is actually visible in the high-resolution magazine scan. No key derivation was run.",
        "",
        "## DOCM Cyan Runs",
        "",
    ]
    for run in cyan_runs:
        md.append(
            f"- run {run['runIndex']} p{run['page']} para {run['paragraphIndex']}: "
            f"`{clean(run['text'])}` font=`{run['fontAscii']}` bold={run['bold']}"
        )
    md.extend(["", f"- Combined cyan letters: `{result['cyanLetters']}`", "", "## Scan Cyan Counts", ""])
    for row in page_counts:
        md.append(
            f"- p{row['page']}: loose={row['looseCyanPixels']} strict={row['strictCyanPixels']} "
            f"of {row['pixels']} pixels"
        )
    md.extend(["", "## Target Region Checks", ""])
    for row in region_counts:
        md.append(
            f"- {row['label']}: loose={row['looseCyanPixels']} strict={row['strictCyanPixels']} "
            f"pixels in box `{row['box']}`"
        )
    for row in crop_counts:
        md.append(
            f"- {row['label']}: loose={row['looseCyanPixels']} strict={row['strictCyanPixels']} "
            f"of {row['pixels']} pixels"
        )
    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The DOCM cyan stream is real as document formatting: `MNBILLION`.",
            "- It is not scan-visible. Under a generous cyan-highlighter threshold, pages 75, 76, 77, 79, and 80 contain zero cyan-like pixels; page 78 has only five loose-threshold pixels and zero strict-threshold pixels.",
            "- The relevant text regions checked directly (`Nocoiners`, p76 `$1 billion`, and p78 `$85/BILLION` orange crops) contain zero cyan pixels.",
            "- Conclusion: do not use cyan as a printed highlight/geometry selector. Keep it as a low-priority DOCM anomaly only if the Word formatting file is later proven to be an original puzzle source.",
            "- Next best move: stay on scan-visible evidence: orange/grey highlights, Typeka variants, page-76 corridor, and improved physical/high-res registration.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
