#!/usr/bin/env python3
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEOM_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "exact_highres_reflection_geometry.json"
MODEL_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "canonical_char_model.json"
OUT_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "page76_semantic_cluster_order.json"
OUT_MD = ROOT / "analysis_outputs" / "3d_article_map" / "page76_semantic_cluster_order.md"


def norm(value):
    value = value.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def tokens(value):
    return [norm(t) for t in re.findall(r"[A-Za-z0-9’'$%-]+", value) if norm(t)]


def token_match(a, b):
    if a == b:
        return True
    return len(a) >= 5 and len(b) >= 5 and (a in b or b in a)


def match_phrase_to_canonical(phrase, words):
    wanted = tokens(phrase)
    if not wanted:
        return [], 0.0
    normalized = [norm(word["text"]) for word in words]
    for start in range(0, max(0, len(words) - len(wanted) + 1)):
        window = normalized[start : start + len(wanted)]
        if all(token_match(want, got) for want, got in zip(wanted, window)):
            return words[start : start + len(wanted)], 1.0

    matches = []
    pos = 0
    for want in wanted:
        found = None
        for idx in range(pos, len(words)):
            if token_match(want, normalized[idx]):
                found = idx
                break
        if found is not None:
            matches.append(words[found])
            pos = found + 1
    return matches, len(matches) / len(wanted)


def initials(phrase):
    return "".join(t[0] for t in tokens(phrase))


def lasts(phrase):
    return "".join(t[-1] for t in tokens(phrase))


def phrase_label(phrase):
    words = tokens(phrase)
    return words[0][0] if words else ""


def source_code(sources):
    if sources == [78]:
        return "L"
    if sources == [79]:
        return "R"
    if sources == [78, 79]:
        return "B"
    return "".join(str(s) for s in sources)


def word_summary(word):
    if word["partialBold"]:
        return f"{word['wordIndex']}:{word['text']}[{word['boldLetters']}]"
    if word["hasBold"]:
        return f"{word['wordIndex']}:{word['text']}[*]"
    return f"{word['wordIndex']}:{word['text']}"


def neighbor_bold(words, start, end, radius):
    lo = max(0, start - radius)
    hi = min(len(words) - 1, end + radius)
    region = words[lo : hi + 1]
    partial = [word for word in region if word["partialBold"]]
    any_bold = [word for word in region if word["hasBold"]]
    return {
        "radius": radius,
        "start": lo,
        "end": hi,
        "partialBoldLetters": "".join(word["boldLetters"] for word in partial),
        "partialBoldWords": [word_summary(word) for word in partial],
        "anyBoldLetters": "".join(word["boldLetters"] for word in any_bold),
        "anyBoldWords": [word_summary(word) for word in any_bold],
    }


def main():
    geom = json.loads(GEOM_JSON.read_text())
    model = json.loads(MODEL_JSON.read_text())
    p2_words = model["pages"]["p2"]["words"]

    clusters = []
    for item in geom["page76Stable"]:
        # Keep only geometry-supported semantic items. Exclude the opening
        # broad slogan unless it is needed for reading-order context.
        phrase = item["text"]
        sources = sorted(item["sources"])
        row = next(
            row for row in geom["rows"]
            if row["page"] == 76 and row["color"] == item["color"] and row["text"] == phrase
        )
        cwords, ratio = match_phrase_to_canonical(phrase, p2_words)
        if cwords:
            start = min(word["wordIndex"] for word in cwords)
            end = max(word["wordIndex"] for word in cwords)
        else:
            start = end = None
        clusters.append({
            "color": item["color"],
            "text": phrase,
            "sources": sources,
            "sourceCode": source_code(sources),
            "matchRatio": round(ratio, 3),
            "canonicalStart": start,
            "canonicalEnd": end,
            "box": row.get("box"),
            "center": [
                round((row["box"][0] + row["box"][2]) / 2, 2),
                round((row["box"][1] + row["box"][3]) / 2, 2),
            ] if row.get("box") else None,
            "phraseInitial": phrase_label(phrase),
            "wordInitials": initials(phrase),
            "wordLasts": lasts(phrase),
            "neighbors": [neighbor_bold(p2_words, start, end, r) for r in (5, 10, 20, 40)] if cwords else [],
        })

    reading = sorted(clusters, key=lambda c: (c["canonicalStart"] if c["canonicalStart"] is not None else 9999))
    geometry = sorted(clusters, key=lambda c: (c["center"][1], c["center"][0]) if c["center"] else (9999, 9999))
    reflection_strength = sorted(
        clusters,
        key=lambda c: (len(c["sources"]), c["canonicalStart"] if c["canonicalStart"] is not None else 9999),
        reverse=True,
    )
    dual_source = [c for c in reading if c["sources"] == [78, 79]]

    def stream(rows, field):
        return "".join(row[field] for row in rows)

    streams = {
        "reading_phrase_initials": stream(reading, "phraseInitial"),
        "reading_source_codes": stream(reading, "sourceCode"),
        "geometry_phrase_initials": stream(geometry, "phraseInitial"),
        "geometry_source_codes": stream(geometry, "sourceCode"),
        "dual_source_phrase_initials": stream(dual_source, "phraseInitial"),
        "dual_source_word_initials": "".join(c["wordInitials"] for c in dual_source),
        "reading_radius20_partial_bold": "".join(
            c["neighbors"][2]["partialBoldLetters"] for c in reading if c["neighbors"]
        ),
        "dual_source_radius20_partial_bold": "".join(
            c["neighbors"][2]["partialBoldLetters"] for c in dual_source if c["neighbors"]
        ),
    }

    result = {
        "clusters": clusters,
        "orders": {
            "reading": [c["text"] for c in reading],
            "geometry": [c["text"] for c in geometry],
            "reflectionStrength": [c["text"] for c in reflection_strength],
            "dualSource": [c["text"] for c in dual_source],
        },
        "streams": streams,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    lines = [
        "# Page 76 Semantic Cluster Order",
        "",
        "Scope: inspect only exact high-res page-76 highlight spans that survive reflected-geometry checks.",
        "No hashing or broad key generation is performed here.",
        "",
        "## Geometry-Supported Clusters",
        "",
    ]
    for c in reading:
        lines.append(
            f"- {c['sourceCode']} {c['color']} idx={c['canonicalStart']}-{c['canonicalEnd']} "
            f"initial=`{c['phraseInitial']}` text=`{c['text']}` match={c['matchRatio']}"
        )
        for n in c["neighbors"]:
            if n["partialBoldLetters"]:
                lines.append(f"  - radius {n['radius']} partial=`{n['partialBoldLetters']}` words={n['partialBoldWords']}")

    lines.extend(["", "## Simple Streams", ""])
    for key, value in streams.items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Assessment", ""])
    lines.append(f"- Reading order gives source-code pattern `{streams['reading_source_codes']}`, which is structured but not directly instructional.")
    lines.append(f"- Dual-source geometry-supported phrases reduce to phrase initials `{streams['dual_source_phrase_initials']}`, not a readable instruction.")
    lines.append("- Nearby partial-bold letters remain dominated by known fragments such as `be`, `lvd`, and `ieNvz`; they point back to El Salvador / Mike Novogratz rather than forming a new message.")
    lines.append("- This supports the page-76 semantic corridor but does not supply the missing final selector.")
    lines.append("- Next best move: manually mark true overlay correspondences on the improved 76/79 registration image, or test page-76 semantic clusters as ordering labels for existing ray selections rather than as key material.")
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
