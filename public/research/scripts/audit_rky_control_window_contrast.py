#!/usr/bin/env python3
"""Contrast the only adjacent R-K-Y style window with the repaired p78-frame R-K-Y.

The previous rarity pass showed one adjacent R-K-Y style window on page 75 and
the repaired geometry-selected R-K-Y trio on page 76. This audit checks whether
the page-75 adjacent window is an instruction/control clue or just ordinary
article content.

No key material, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RKY_JSON = ROOT / "analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity.json"
CONVERGENCE_JSON = ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json"

OUT = ROOT / "analysis_outputs/docm_format_sources/rky_control_window_contrast"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "rky_control_window_contrast.json"
OUT_MD = OUT / "rky_control_window_contrast.md"
OUT_SHEET = OUT / "rky_control_window_contrast_sheet.jpg"


PROCEDURAL_TERMS = [
    "read",
    "mirror",
    "fold",
    "reverse",
    "backward",
    "left",
    "right",
    "above",
    "below",
    "inside",
    "outside",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "take",
    "use",
    "count",
    "number",
    "page",
    "column",
    "row",
    "dose",
    "pill",
    "light",
]

CONTENT_COMMAND_TERMS = ["don't", "keep", "sell", "fall"]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+(?:'[A-Za-z]+)?", text)


def initials(text: str) -> str:
    return "".join(w[0] for w in words(text) if w)


def lasts(text: str) -> str:
    return "".join(w[-1] for w in words(text) if w)


def term_hits(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", lowered)]


def target_hits(text: str, convergence: dict) -> list[str]:
    lowered = text.lower()
    hits = []
    if "shitcoiner at heart" in lowered:
        hits.append("O5")
    if "volcano bonds" in lowered or ("volcano" in lowered and "bonds" in lowered):
        hits.append("G5")
    if any(token in lowered for token in ["el salvador", "imf", "bukele", "novogratz", "trust"]):
        hits.append("CORRIDOR")
    if "$1 billion" in lowered or "1 billion" in lowered:
        hits.append("G4")
    if "get some toxicity" in lowered or "open your heart" in lowered:
        hits.append("O1")
    if "rancid catnip" in lowered:
        hits.append("O3")
    if "buying the dip" in lowered:
        hits.append("O4")
    if "gotta be this way" in lowered or "post-1971" in lowered:
        hits.append("G1")
    if "stun gun" in lowered:
        hits.append("G3")
    return hits


def summarize_window(name: str, page: int, texts: list[str], source: str, convergence: dict) -> dict:
    joined = clean(" | ".join(texts))
    compact = clean(" ".join(texts))
    return {
        "name": name,
        "page": page,
        "source": source,
        "texts": texts,
        "joined": joined,
        "wordCount": len(words(compact)),
        "initials": initials(compact),
        "lasts": lasts(compact),
        "reversedWords": " ".join(reversed(words(compact))),
        "proceduralHits": term_hits(compact, PROCEDURAL_TERMS),
        "contentCommandHits": term_hits(compact, CONTENT_COMMAND_TERMS),
        "page76TargetHits": target_hits(compact, convergence),
    }


def draw_sheet(records: list[dict]) -> None:
    width = 1700
    height = 580
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 28)
        font = ImageFont.truetype("Arial.ttf", 19)
        small = ImageFont.truetype("Arial.ttf", 17)
    except OSError:
        title_font = ImageFont.load_default()
        font = title_font
        small = title_font

    y = 28
    draw.text((28, y), "Adjacent R-K-Y control vs repaired page-76 R-K-Y signature", fill=(20, 20, 20), font=title_font)
    y += 52
    for record in records:
        fill = (238, 241, 245) if record["name"].startswith("adjacent") else (248, 238, 224)
        draw.rectangle([24, y - 10, width - 24, y + 195], fill=fill)
        draw.text((42, y), f"{record['name']} | page {record['page']} | {record['source']}", fill=(20, 20, 20), font=font)
        y += 34
        draw.text((58, y), record["joined"][:180], fill=(35, 35, 35), font=small)
        y += 34
        draw.text((58, y), f"initials={record['initials']}  lasts={record['lasts']}  words={record['wordCount']}", fill=(70, 70, 70), font=small)
        y += 30
        draw.text((58, y), f"procedural={record['proceduralHits']}  content commands={record['contentCommandHits']}", fill=(80, 60, 40), font=small)
        y += 30
        draw.text((58, y), f"page76 target hits={record['page76TargetHits']}", fill=(40, 80, 40), font=small)
        y += 74
    image.save(OUT_SHEET, quality=95)


def main() -> None:
    rky = json.loads(RKY_JSON.read_text())
    convergence = json.loads(CONVERGENCE_JSON.read_text())

    adjacent = next(
        window
        for page_record in rky["pageRecords"]
        for window in page_record["adjacentRkyWindows"]
    )
    adjacent_record = summarize_window(
        "adjacent_RKY_control",
        75,
        adjacent["texts"],
        "only adjacent R-K-Y style window in DOCM pages 75-79",
        convergence,
    )

    repaired_texts = [part.strip() for part in rky["repairedSignature"]["exactEdgeLabels"].split("|")]
    repaired_record = summarize_window(
        "repaired_RKY_geometry_signature",
        76,
        repaired_texts,
        "p78-frame exact-edge geometry at dx=-38",
        convergence,
    )

    records = [adjacent_record, repaired_record]
    draw_sheet(records)

    assessment = [
        "The page-75 adjacent R-K-Y window has content commands (`Don't`, `Keep`) but no extraction terms such as read, mirror, fold, word, letter, key, line, or take.",
        "The repaired page-76 R-K-Y trio has the relevant target terms (`Volcano Bonds`, `shitcoiner at heart`) but still no procedural extraction terms.",
        "This contrast makes the page-75 adjacent R-K-Y useful as a control/decoy check, not as an instruction source.",
        "The lower-corridor R-K-Y remains valuable only because geometry selects the exact target trio; it still needs an external/source rule for the extraction unit.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "contrast adjacent R-K-Y style control with repaired lower-corridor R-K-Y geometry; no key derivation",
        "sourceReports": {
            "rkyRarity": str(RKY_JSON.relative_to(ROOT)),
            "page76TargetConvergence": str(CONVERGENCE_JSON.relative_to(ROOT)),
        },
        "records": records,
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": assessment,
        "nextMove": "Do not follow the page-75 adjacent R-K-Y window unless a new clue points back to `Don't fall` / `Keep your dignity`. Keep priority on lower-corridor source registration and a rule naming the unit to extract.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# R-K-Y Control Window Contrast",
        "",
        "Scope: compare the only adjacent `R-K-Y` style window with the repaired lower-corridor `R-K-Y` geometry signature. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Records",
        "",
        "| record | page | source | text | initials | lasts | procedural hits | target hits |",
        "|---|---:|---|---|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            "| `{name}` | {page} | {source} | {text} | `{initials}` | `{lasts}` | `{proc}` | `{targets}` |".format(
                name=record["name"],
                page=record["page"],
                source=record["source"],
                text=record["joined"].replace("|", "/"),
                initials=record["initials"],
                lasts=record["lasts"],
                proc=", ".join(record["proceduralHits"]) or "none",
                targets=", ".join(record["page76TargetHits"]) or "none",
            )
        )

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    for record in records:
        print(record["name"], "procedural", record["proceduralHits"], "targets", record["page76TargetHits"])


if __name__ == "__main__":
    main()
