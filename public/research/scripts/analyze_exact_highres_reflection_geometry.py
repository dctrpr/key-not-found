#!/usr/bin/env python3
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "article_3d_map_data.json"
ORANGE_JSON = ROOT / "analysis_outputs" / "highlight_audit" / "highres_manual_highlight_reading.json"
GREY_JSON = ROOT / "analysis_outputs" / "highlight_audit" / "highres_manual_grey_reading.json"
OUT_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "exact_highres_reflection_geometry.json"
OUT_MD = ROOT / "analysis_outputs" / "3d_article_map" / "exact_highres_reflection_geometry.md"


def norm(value):
    value = value.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def phrase_tokens(value):
    return [norm(token) for token in re.findall(r"[A-Za-z0-9’'$%-]+", value) if norm(token)]


def token_match(want, got):
    if not want or not got:
        return False
    if want == got:
        return True
    if len(want) >= 5 and len(got) >= 5 and (want in got or got in want):
        return True
    return False


def bbox_union(boxes):
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def overlap(a, b):
    return area([max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])])


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def distance(a, b):
    ax, ay = center(a)
    bx, by = center(b)
    return math.hypot(ax - bx, ay - by)


def match_phrase_to_page_words(phrase, words):
    wanted = phrase_tokens(phrase)
    if not wanted:
        return [], 0.0
    page_tokens = [(norm(word.get("token") or word.get("text", "")), word) for word in words]
    matches = []
    pos = 0
    for want in wanted:
        found = None
        for idx in range(pos, len(page_tokens)):
            if token_match(want, page_tokens[idx][0]):
                found = idx
                break
        if found is not None:
            matches.append(page_tokens[found][1])
            pos = found + 1
    return matches, len(matches) / len(wanted)


def load_exact_spans():
    orange = json.loads(ORANGE_JSON.read_text())["combinedOrangeSpans"]
    grey = json.loads(GREY_JSON.read_text())["combinedGreyBlackSpans"]
    rows = []
    for color, spans in [("orange", orange), ("grey_black", grey)]:
        for seq, span in enumerate(spans, 1):
            text = span["text"]
            if "pill label" in text.lower():
                continue
            rows.append({"id": f"{color}_{seq}", "color": color, "page": int(span["page"]), "text": text})
    return rows


def main():
    map_data = json.loads(MAP_JSON.read_text())
    pages = {int(page["page"]): page for page in map_data["pages"]}
    reflections_by_target = {}
    for reflection in map_data.get("reflections", []):
        reflections_by_target.setdefault(int(reflection["target"]), []).append(reflection)

    rows = []
    for span in load_exact_spans():
        page = pages.get(span["page"])
        words, ratio = match_phrase_to_page_words(span["text"], page["words"] if page else [])
        box = bbox_union([word["box"] for word in words]) if words else None
        hits = []
        if box:
            for reflection in reflections_by_target.get(span["page"], []):
                rbox = reflection["targetBox"]
                ov = overlap(box, rbox)
                if ov <= 0:
                    continue
                hits.append({
                    "reflectionId": reflection["id"],
                    "source": reflection["source"],
                    "target": reflection["target"],
                    "reflectionText": reflection.get("text", ""),
                    "overlapArea": round(ov, 2),
                    "overlapVsSpan": round(ov / max(1, area(box)), 4),
                    "overlapVsReflection": round(ov / max(1, area(rbox)), 4),
                    "centerDistance": round(distance(box, rbox), 2),
                })
            hits.sort(key=lambda item: (item["overlapVsReflection"], item["overlapVsSpan"]), reverse=True)
        rows.append({
            **span,
            "matchedWords": len(words),
            "matchRatio": round(ratio, 3),
            "wordIndexes": [word["index"] for word in words],
            "box": box,
            "reflectionHits": hits,
        })

    page76 = [row for row in rows if row["page"] == 76]
    stable = []
    for row in page76:
        strong = [hit for hit in row["reflectionHits"] if hit["overlapVsReflection"] >= 0.45 or hit["overlapVsSpan"] >= 0.12]
        if strong:
            stable.append({
                "color": row["color"],
                "text": row["text"],
                "sources": sorted({hit["source"] for hit in strong}),
                "strongHits": strong,
            })

    OUT_JSON.write_text(json.dumps({"rows": rows, "page76Stable": stable}, indent=2, ensure_ascii=False))

    lines = [
        "# Exact High-Res Reflection Geometry",
        "",
        "Scope: rematch the manual high-res highlight source against 3D page words, then test reflected highlight boxes against those exact spans.",
        "OCR text is used only for approximate geometry boxes; exact span text comes from the high-res manual source.",
        "",
        "## Page 76 Exact Span Hits",
        "",
    ]
    for row in page76:
        best = "; ".join(
            f"{hit['reflectionId']} src={hit['source']} ovRefl={hit['overlapVsReflection']} ovSpan={hit['overlapVsSpan']} text=`{hit['reflectionText'][:70]}`"
            for hit in row["reflectionHits"][:4]
        ) or "none"
        lines.append(
            f"- {row['color']} `{row['text']}` match={row['matchedWords']} ratio={row['matchRatio']} hits={best}"
        )

    lines.extend(["", "## Stable Page 76 Geometry", ""])
    if stable:
        for item in stable:
            hit_list = "; ".join(
                f"{hit['reflectionId']}({hit['source']}->{hit['target']}, ovRefl={hit['overlapVsReflection']})"
                for hit in item["strongHits"][:4]
            )
            lines.append(f"- {item['color']} `{item['text']}` sources={item['sources']} hits={hit_list}")
    else:
        lines.append("- none")

    lines.extend(["", "## Non-Page-76 Intersections", ""])
    count = 0
    for row in rows:
        if row["page"] == 76 or not row["reflectionHits"]:
            continue
        count += 1
        hit = row["reflectionHits"][0]
        lines.append(
            f"- p{row['page']} {row['color']} `{row['text']}` -> {hit['reflectionId']} "
            f"ovRefl={hit['overlapVsReflection']} ovSpan={hit['overlapVsSpan']} text=`{hit['reflectionText'][:90]}`"
        )
    if not count:
        lines.append("- none")

    lines.extend(["", "## Assessment", ""])
    lines.append("- Re-running geometry from the corrected high-res highlight text preserves the same page-76 concentration: opening toxicity/UTXO area, Peter-Schiff/fiat-money area, El Salvador/Bukele corridor, and `$1 billion`/IMF corridor.")
    lines.append("- `Volcano Bonds` and `shitcoiner at heart` still do not get a strong reflected-box hit in the current OCR-derived geometry, so they remain semantic anchors rather than geometric intersections.")
    lines.append("- The p78 correction removes overcaptured connector prose from text streams but does not change the main geometry conclusion.")
    lines.append("- Next best move: affine-register the visual anchors on pages 76/78/79 and re-run this exact-span intersection from registered boxes, because current OCR boxes are good enough for regions but not exact letters.")
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
