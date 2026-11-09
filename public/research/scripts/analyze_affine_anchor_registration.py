#!/usr/bin/env python3
import itertools
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "article_3d_map_data.json"
OUT_JSON = ROOT / "analysis_outputs" / "source_audit" / "affine_anchor_registration.json"
OUT_MD = ROOT / "analysis_outputs" / "source_audit" / "affine_anchor_registration.md"


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def centroid(points):
    return (
        sum(p[0] for p in points) / len(points),
        sum(p[1] for p in points) / len(points),
    )


def fit_similarity(src_points, dst_points):
    # Orthogonal Procrustes in 2D: y = s R x + t, no shear.
    sx, sy = centroid(src_points)
    dx, dy = centroid(dst_points)
    src = [(x - sx, y - sy) for x, y in src_points]
    dst = [(x - dx, y - dy) for x, y in dst_points]

    a = sum(x * u + y * v for (x, y), (u, v) in zip(src, dst))
    b = sum(x * v - y * u for (x, y), (u, v) in zip(src, dst))
    denom = sum(x * x + y * y for x, y in src)
    if denom == 0:
        return None
    scale = math.hypot(a, b) / denom
    theta = math.atan2(b, a)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    def transform(point):
        x, y = point
        xr = scale * (cos_t * (x - sx) - sin_t * (y - sy)) + dx
        yr = scale * (sin_t * (x - sx) + cos_t * (y - sy)) + dy
        return (xr, yr)

    mapped = [transform(p) for p in src_points]
    errors = [dist(a, b) for a, b in zip(mapped, dst_points)]
    return {
        "scale": scale,
        "thetaDeg": math.degrees(theta),
        "translation": [dx - scale * (cos_t * sx - sin_t * sy), dy - scale * (sin_t * sx + cos_t * sy)],
        "rms": math.sqrt(sum(e * e for e in errors) / len(errors)),
        "maxError": max(errors),
        "errors": errors,
        "transform": transform,
    }


def nearest(point, targets):
    ranked = sorted(((dist(point, item["point"]), item) for item in targets), key=lambda item: item[0])
    return ranked[0]


def main():
    data = json.loads(MAP_JSON.read_text())
    anchors = data["anchors"]
    pills = [a for a in anchors if a["id"].startswith("p79_pill_") and a["id"].endswith("_mirror")]
    targets = [a for a in anchors if a["id"].startswith("p76_")]
    pills.sort(key=lambda a: a["id"])
    targets.sort(key=lambda a: a["id"])

    trials = []
    for size in (3, 4, 5):
        for source_subset in itertools.combinations(pills, size):
            for target_subset in itertools.combinations(targets, size):
                for perm in itertools.permutations(target_subset):
                    fit = fit_similarity([p["point"] for p in source_subset], [p["point"] for p in perm])
                    if not fit:
                        continue
                    mapped_all = []
                    for pill in pills:
                        mapped = fit["transform"](pill["point"])
                        d, tgt = nearest(mapped, targets)
                        mapped_all.append({
                            "source": pill["id"],
                            "mapped": [round(mapped[0], 2), round(mapped[1], 2)],
                            "nearestTarget": tgt["id"],
                            "nearestDistance": round(d, 2),
                        })
                    trials.append({
                        "size": size,
                        "sourceIds": [p["id"] for p in source_subset],
                        "targetIds": [p["id"] for p in perm],
                        "scale": round(fit["scale"], 5),
                        "thetaDeg": round(fit["thetaDeg"], 3),
                        "translation": [round(v, 2) for v in fit["translation"]],
                        "rms": round(fit["rms"], 2),
                        "maxError": round(fit["maxError"], 2),
                        "errors": [round(e, 2) for e in fit["errors"]],
                        "mappedAll": mapped_all,
                        "meanNearestAll": round(sum(item["nearestDistance"] for item in mapped_all) / len(mapped_all), 2),
                        "maxNearestAll": round(max(item["nearestDistance"] for item in mapped_all), 2),
                    })
    trials.sort(key=lambda item: (item["size"] < 4, item["meanNearestAll"], item["rms"], item["maxNearestAll"]))

    best_by_size = {}
    for trial in sorted(trials, key=lambda item: (item["meanNearestAll"], item["rms"])):
        best_by_size.setdefault(str(trial["size"]), trial)

    OUT_JSON.write_text(json.dumps({"bestBySize": best_by_size, "topTrials": trials[:50]}, indent=2))

    lines = [
        "# Affine Anchor Registration Check",
        "",
        "Scope: test whether the mirrored page-79 pill centers can be registered onto the page-76 X/dollar/black-bar/wire anchor set using a simple similarity transform.",
        "This is a pattern-registration test only; it does not generate key candidates.",
        "",
        "## Best Fits By Pair Count",
        "",
    ]
    for size in ("3", "4", "5"):
        trial = best_by_size.get(size)
        if not trial:
            continue
        lines.append(
            f"- {size} pairs: meanNearestAll={trial['meanNearestAll']} maxNearestAll={trial['maxNearestAll']} "
            f"fitRms={trial['rms']} scale={trial['scale']} theta={trial['thetaDeg']}deg"
        )
        lines.append(f"  - source={trial['sourceIds']}")
        lines.append(f"  - target={trial['targetIds']}")
        lines.append(f"  - mappedAll={[(m['source'], m['nearestTarget'], m['nearestDistance']) for m in trial['mappedAll']]}")

    lines.extend(["", "## Assessment", ""])
    best4 = best_by_size.get("4")
    best5 = best_by_size.get("5")
    if best4 and best4["meanNearestAll"] < 90 and best4["maxNearestAll"] < 180:
        lines.append("- A plausible 4-point similarity registration exists. This is worth turning into a visual overlay and re-running exact-span intersections.")
    else:
        lines.append("- No strong 4- or 5-point similarity registration appears from the current manual anchor set. The best low-residual fits are likely overfit 3-point coincidences.")
    if best5:
        lines.append(f"- The best 5-point fit still leaves mean/max nearest distances of {best5['meanNearestAll']} / {best5['maxNearestAll']} px, too loose for letter-level extraction.")
    lines.append("- Current conclusion: these anchors remain orientation/region evidence. Precise affine registration needs either more corresponding visual marks or a manual overlay chosen from the actual page images, not just the current anchor list.")
    lines.append("- Next best move: create a visual registration workbench/contact sheet for 76/79 and manually mark true corresponding points before re-running exact highlight geometry.")
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
