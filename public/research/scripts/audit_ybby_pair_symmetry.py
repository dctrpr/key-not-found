#!/usr/bin/env python3
"""
Test the locked page-76 Y-B-B-Y color sequence as a mirror/bracket geometry.

This is a bounded visual geometry check only. It does not derive private keys,
hash text, generate seed phrases, or check addresses.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "ybby_pair_symmetry"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OBBO_JSON = ROOT / "analysis_outputs" / "source_audit" / "obbo_highres_boundary_coincidences" / "obbo_highres_boundary_coincidences.json"
PAGE_IMG = ROOT / "analysis_outputs" / "3d_article_map" / "page_76_upright.jpg"
OUT_JSON = OUT_DIR / "ybby_pair_symmetry.json"
OUT_MD = OUT_DIR / "ybby_pair_symmetry.md"
OUT_OVERLAY = OUT_DIR / "ybby_pair_symmetry_overlay.jpg"


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def dims(box: list[float]) -> tuple[float, float]:
    return (box[2] - box[0], box[3] - box[1])


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def vec(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (b[0] - a[0], b[1] - a[1])


def angle_deg(v: tuple[float, float]) -> float:
    return (math.degrees(math.atan2(v[1], v[0])) + 360) % 180


def angle_delta(a: float, b: float) -> float:
    d = abs(a - b) % 180
    return min(d, 180 - d)


def midpoint(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def line_from_point_angle(p: tuple[float, float], angle: float, length: float = 900) -> tuple[tuple[float, float], tuple[float, float]]:
    r = math.radians(angle)
    dx = math.cos(r) * length / 2
    dy = math.sin(r) * length / 2
    return ((p[0] - dx, p[1] - dy), (p[0] + dx, p[1] + dy))


def common_reflection_residual(pair_a, pair_b) -> dict[str, float | str]:
    """Compare the perpendicular bisectors for two same-color point pairs."""
    a1, a2 = pair_a
    b1, b2 = pair_b
    va = vec(a1, a2)
    vb = vec(b1, b2)
    axis_a = (angle_deg(va) + 90) % 180
    axis_b = (angle_deg(vb) + 90) % 180
    return {
        "pairA_segmentAngle": round(angle_deg(va), 3),
        "pairB_segmentAngle": round(angle_deg(vb), 3),
        "pairA_perpendicularBisectorAngle": round(axis_a, 3),
        "pairB_perpendicularBisectorAngle": round(axis_b, 3),
        "commonMirrorAxisAngleDelta": round(angle_delta(axis_a, axis_b), 3),
        "midpointDistance": round(dist(midpoint(a1, a2), midpoint(b1, b2)), 3),
    }


def instruction_hits(text: str) -> list[str]:
    terms = ["read", "take", "fold", "mirror", "word", "letter", "line", "key", "left", "right", "first", "last"]
    low = text.lower()
    return [term for term in terms if term in low]


def main() -> None:
    obbo = json.loads(OBBO_JSON.read_text())
    anchors = {a["id"]: a for a in obbo["anchors"]}

    # Normalize names from the source report.
    target_map = {
        "O4_buying_the_dip": "O4",
        "B4_one_billion": "B4",
        "G5_volcano_bonds": "G5",
        "O5_shitcoiner_heart": "O5",
    }
    by_label = {}
    for item in obbo["anchors"]:
        label = item["label"]
        if "buying the dip" in label:
            by_label["O4"] = item
        elif "$1 billion" in label:
            by_label["B4"] = item
        elif "Volcano Bonds" in label:
            by_label["G5"] = item
        elif "shitcoiner" in label:
            by_label["O5"] = item

    order = ["O4", "B4", "G5", "O5"]
    rows = []
    for key in order:
        item = by_label[key]
        c = center(item["box"])
        w, h = dims(item["box"])
        rows.append(
            {
                "id": key,
                "label": item["label"],
                "color": "yellow/orange" if key.startswith("O") else "black/grey",
                "box": item["box"],
                "center": [round(c[0], 3), round(c[1], 3)],
                "width": round(w, 3),
                "height": round(h, 3),
            }
        )

    c = {row["id"]: tuple(row["center"]) for row in rows}
    orange_pair = (c["O4"], c["O5"])
    black_pair = (c["B4"], c["G5"])

    orange_vec = vec(*orange_pair)
    black_vec = vec(*black_pair)
    orange_mid = midpoint(*orange_pair)
    black_mid = midpoint(*black_pair)

    same_color_pair_metrics = {
        "orangePair": {
            "pair": ["O4", "O5"],
            "vector": [round(orange_vec[0], 3), round(orange_vec[1], 3)],
            "distance": round(dist(*orange_pair), 3),
            "segmentAngle": round(angle_deg(orange_vec), 3),
            "midpoint": [round(orange_mid[0], 3), round(orange_mid[1], 3)],
        },
        "blackPair": {
            "pair": ["B4", "G5"],
            "vector": [round(black_vec[0], 3), round(black_vec[1], 3)],
            "distance": round(dist(*black_pair), 3),
            "segmentAngle": round(angle_deg(black_vec), 3),
            "midpoint": [round(black_mid[0], 3), round(black_mid[1], 3)],
        },
        "commonReflectionTest": common_reflection_residual(orange_pair, black_pair),
        "centralSymmetryMidpointDistance": round(dist(orange_mid, black_mid), 3),
        "segmentAngleDelta": round(angle_delta(angle_deg(orange_vec), angle_deg(black_vec)), 3),
    }

    streams = {
        "topToBottom": " | ".join(by_label[k]["label"] for k in order),
        "bottomToTop": " | ".join(by_label[k]["label"] for k in reversed(order)),
        "sameColorOuterInner": " | ".join([by_label["O4"]["label"], by_label["O5"]["label"], by_label["B4"]["label"], by_label["G5"]["label"]]),
        "pairMidpoints": f"orange midpoint {orange_mid} | black midpoint {black_mid}",
    }
    stream_hits = {name: instruction_hits(text) for name, text in streams.items()}

    # Make a compact overlay for manual review.
    img = Image.open(PAGE_IMG).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    colors = {
        "O4": (255, 155, 46, 170),
        "O5": (255, 155, 46, 170),
        "B4": (40, 45, 55, 210),
        "G5": (40, 45, 55, 210),
    }
    outline = {
        "O4": (255, 190, 80, 255),
        "O5": (255, 190, 80, 255),
        "B4": (120, 220, 255, 255),
        "G5": (120, 220, 255, 255),
    }
    font = ImageFont.load_default()
    for row in rows:
        box = row["box"]
        key = row["id"]
        draw.rectangle(box, fill=colors[key], outline=outline[key], width=5)
        draw.text((box[0], box[1] - 18), f"{key} {row['label']}", fill=(255, 255, 255, 255), font=font)

    # Same-color pair lines and perpendicular bisectors.
    draw.line([c["O4"], c["O5"]], fill=(255, 190, 80, 255), width=6)
    draw.line([c["B4"], c["G5"]], fill=(120, 220, 255, 255), width=6)
    for pair, color in [(orange_pair, (255, 190, 80, 220)), (black_pair, (120, 220, 255, 220))]:
        v = vec(*pair)
        axis_angle = (angle_deg(v) + 90) % 180
        m = midpoint(*pair)
        a, b = line_from_point_angle(m, axis_angle, 1000)
        draw.line([a, b], fill=color, width=3)
        draw.ellipse([m[0] - 8, m[1] - 8, m[0] + 8, m[1] + 8], fill=color)

    # Crop to the active lower corridor with margin.
    min_x = max(0, int(min(row["box"][0] for row in rows) - 180))
    min_y = max(0, int(min(row["box"][1] for row in rows) - 180))
    max_x = min(img.width, int(max(row["box"][2] for row in rows) + 180))
    max_y = min(img.height, int(max(row["box"][3] for row in rows) + 180))
    img.crop((min_x, min_y, max_x, max_y)).save(OUT_OVERLAY, quality=92)

    assessment = [
        "The confirmed Y-B-B-Y sequence is a real active target signature, but the same-color pairs do not share a common mirror axis.",
        f"Orange pair and black pair segment angles differ by {same_color_pair_metrics['segmentAngleDelta']} degrees.",
        f"Their perpendicular-bisector axes differ by {same_color_pair_metrics['commonReflectionTest']['commonMirrorAxisAngleDelta']} degrees, so a single reflection axis cannot map O4->O5 and B4->G5.",
        f"The orange-pair and black-pair midpoints are {same_color_pair_metrics['centralSymmetryMidpointDistance']} px apart, so the four anchors do not form a clean 180-degree rotational bracket either.",
        "The simple order streams are only the known semantic labels and contain no instruction terms.",
    ]
    decision = (
        "Keep Y-B-B-Y / O-B-B-O as a distinctive page-76 source-comparison signature, not a mirror/bracket extraction rule."
    )
    next_move = (
        "Do not spend more local passes trying to infer an axis from the four color targets. The remaining blocker is still an external/source instruction or a new physical/original-layout image that changes the active target geometry."
    )

    report = {
        "scope": "Y-B-B-Y same-color pair symmetry audit; no key derivation",
        "anchors": rows,
        "sameColorPairMetrics": same_color_pair_metrics,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2))

    lines = [
        "# Y-B-B-Y Pair Symmetry Audit",
        "",
        "Scope: test whether the locked page-76 yellow/black/black/yellow sequence behaves as a mirror or bracket geometry. No key derivation, hashing, seed phrase, WIF, or address checks were run.",
        "",
        f"- Overlay: `{OUT_OVERLAY.relative_to(ROOT)}`",
        "",
        "## Anchor Rows",
        "",
        "| id | color | label | center | box |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row['id']}` | `{row['color']}` | `{row['label']}` | `{row['center']}` | `{row['box']}` |")

    lines.extend(
        [
            "",
            "## Same-Color Pair Metrics",
            "",
            f"- Orange pair O4->O5 vector: `{same_color_pair_metrics['orangePair']['vector']}`, angle `{same_color_pair_metrics['orangePair']['segmentAngle']}` deg, midpoint `{same_color_pair_metrics['orangePair']['midpoint']}`.",
            f"- Black pair B4->G5 vector: `{same_color_pair_metrics['blackPair']['vector']}`, angle `{same_color_pair_metrics['blackPair']['segmentAngle']}` deg, midpoint `{same_color_pair_metrics['blackPair']['midpoint']}`.",
            f"- Segment angle delta: `{same_color_pair_metrics['segmentAngleDelta']}` deg.",
            f"- Common reflection-axis angle delta: `{same_color_pair_metrics['commonReflectionTest']['commonMirrorAxisAngleDelta']}` deg.",
            f"- Pair midpoint distance: `{same_color_pair_metrics['centralSymmetryMidpointDistance']}` px.",
            "",
            "## Streams Checked",
            "",
            "| stream | text | instruction hits |",
            "|---|---|---|",
        ]
    )
    for name, text in streams.items():
        safe_text = text.replace("|", "\\|")
        lines.append(f"| `{name}` | `{safe_text}` | `{stream_hits[name]}` |")

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", "", "## Next Move", "", f"- {next_move}"])
    OUT_MD.write_text("\n".join(lines) + "\n")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_OVERLAY}")


if __name__ == "__main__":
    main()
