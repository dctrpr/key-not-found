#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLUSTERS_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "page76_semantic_cluster_order.json"
SELECTOR_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "selector_intersection_analysis.json"
OUT_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "cluster_labeled_rays.json"
OUT_MD = ROOT / "analysis_outputs" / "3d_article_map" / "cluster_labeled_rays.md"


def label_for_cluster(cluster):
    text = cluster["text"]
    if text.startswith("Get some"):
        return "OPEN_HEART"
    if text.startswith("Gotta"):
        return "FIAT_NONSENSE"
    if text.startswith("by the"):
        return "FIAT_CATNIP"
    if "stun gun" in text:
        return "STUN_GUN"
    if "buying the dip" in text:
        return "BUY_DIP"
    if "$1 billion" in text:
        return "ONE_BILLION"
    return text[:20].upper()


def distance_to_range(indexes, start, end):
    if not indexes:
        return 999999
    if any(start <= idx <= end for idx in indexes):
        return 0
    return min(min(abs(idx - start), abs(idx - end)) for idx in indexes)


def overlap_count(indexes, start, end):
    return sum(1 for idx in indexes if start <= idx <= end)


def main():
    clusters_data = json.loads(CLUSTERS_JSON.read_text())
    selector_data = json.loads(SELECTOR_JSON.read_text())
    clusters = sorted(clusters_data["clusters"], key=lambda item: item["canonicalStart"])
    rays = selector_data["rayIntersections"]

    rows = []
    for cluster in clusters:
        start = cluster["canonicalStart"]
        end = cluster["canonicalEnd"]
        label = label_for_cluster(cluster)
        candidates = []
        for ray in rays:
            indexes = ray.get("wordIndexes") or []
            overlap = overlap_count(indexes, start, end)
            distance = distance_to_range(indexes, start, end)
            near = [idx for idx in indexes if start - 12 <= idx <= end + 12]
            if overlap or distance <= 12:
                candidates.append({
                    "rank": ray["rank"],
                    "selector": ray["selector"],
                    "text": ray["text"],
                    "matchRatio": ray["matchRatio"],
                    "overlap": overlap,
                    "distance": distance,
                    "nearWordIndexes": near,
                    "partialBold": ray.get("partialBold", ""),
                    "anyBold": ray.get("anyBold", ""),
                    "firstLetters": ray.get("firstLetters", ""),
                    "lastLetters": ray.get("lastLetters", ""),
                    "lengths": ray.get("lengths", ""),
                })
        candidates.sort(key=lambda item: (item["overlap"] > 0, -item["distance"], item["matchRatio"]), reverse=True)
        rows.append({
            "label": label,
            "sourceCode": cluster["sourceCode"],
            "phraseInitial": cluster["phraseInitial"],
            "text": cluster["text"],
            "range": [start, end],
            "candidateRays": candidates,
        })

    # Compress to one best ray per cluster so we can inspect whether the
    # semantic labels impose a readable order on the ray material.
    best_rows = [row for row in rows if row["candidateRays"]]
    reading_best = []
    for row in best_rows:
        best = row["candidateRays"][0]
        reading_best.append({
            "cluster": row["label"],
            "sourceCode": row["sourceCode"],
            "phraseInitial": row["phraseInitial"],
            **best,
        })

    streams = {
        "cluster_labels": "|".join(item["cluster"] for item in reading_best),
        "source_codes": "".join(item["sourceCode"] for item in reading_best),
        "phrase_initials": "".join(item["phraseInitial"] for item in reading_best),
        "ray_first_letters": "".join(item["firstLetters"] for item in reading_best),
        "ray_last_letters": "".join(item["lastLetters"] for item in reading_best),
        "ray_any_bold": "".join(item["anyBold"] for item in reading_best),
        "ray_partial_bold": "".join(item["partialBold"] for item in reading_best),
        "ray_lengths": ".".join(item["lengths"] for item in reading_best),
    }

    OUT_JSON.write_text(json.dumps({"rows": rows, "readingBest": reading_best, "streams": streams}, indent=2, ensure_ascii=False))

    lines = [
        "# Cluster-Labeled Anchor Rays",
        "",
        "Scope: use the geometry-supported page-76 semantic clusters as labels for existing anchor-ray selections.",
        "This tests ordering/labeling only; it does not hash or derive keys.",
        "",
        "## Best Ray Per Cluster",
        "",
    ]
    for row in rows:
        if not row["candidateRays"]:
            lines.append(f"- {row['label']} `{row['text']}` range={row['range']}: no ray within 12 words")
            continue
        best = row["candidateRays"][0]
        lines.append(
            f"- {row['label']} src={row['sourceCode']} initial={row['phraseInitial']} range={row['range']} "
            f"bestRank={best['rank']} distance={best['distance']} overlap={best['overlap']} selector=`{best['selector']}`"
        )
        lines.append(f"  - text=`{best['text']}`")
        if best["anyBold"] or best["partialBold"]:
            lines.append(f"  - bold any=`{best['anyBold']}` partial=`{best['partialBold']}`")

    lines.extend(["", "## Streams From Best Rays In Cluster Reading Order", ""])
    for key, value in streams.items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Assessment", ""])
    lines.append("- Every cluster has at least one nearby ray, but the same broad ray supports multiple early clusters, so this does not create an independent ordering rule.")
    lines.append("- The later rays touch the IMF/El/Monetary corridor, while earlier rays mostly repeat generic UTXO/fiat/bitcoin material.")
    lines.append("- Combined best-ray bold material is `bitcoinUTXObitcoinUTXOthetheIEl`, with no partial-bold stream. This is semantic reinforcement, not final key material.")
    lines.append("- The cluster labels do not impose a readable message over the ray selections.")
    lines.append("- Next best move: manually mark real corresponding points on the improved overlay; automated global alignment and cluster-labeled rays have both failed to produce a final selector.")
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
