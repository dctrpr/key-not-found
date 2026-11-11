#!/usr/bin/env python3
"""Verify locked source review receipts and apply the declared heading comparison."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp(value):
    require(value.endswith("Z"), "Timestamp must be UTC")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def intersection(a, b):
    if not a or not b:
        return False
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def native_box(box, view):
    x0, y0, x1, y1 = box
    require(all(type(v) is int for v in box), "Box needs integer pixel bounds")
    require(0 <= x0 < x1 <= 2040 and 0 <= y0 < y1 <= 1683, "Box outside crop")
    return [2040 - x1, y0, 2040 - x0, y1] if view == "reflected" else box


def receipt(path, label, stage, packet_hash):
    value = read(path)
    require(value["reader"] == label and value["stage"] == stage, "Wrong reviewer or stage")
    require(value["packetManifestSha256"] == packet_hash, "Wrong review packet")
    require(value["bothViewsInspected"] is True and value["peerMarksSeen"] is False
            and value["priorComparisonSeen"] is False
            and value["page75ReferenceSeen"] is (stage == 2), "Unexpected review exposure")
    require(timestamp(value["startedAtUTC"]) <= timestamp(value["completedAtUTC"]), "Review timing")
    require(value["view"] in {"upright", "reflected", "uncertain"}, "Unknown view")
    words = value["words"]
    require(all(re.fullmatch(r"[A-Z]+", word) for word in words), "Invalid reading tokens")
    box = value["featureBoxXYXY"]
    value["nativeFeatureBox"] = native_box(box, value["view"]) if box else None
    require(not words or (box and value["view"] != "uncertain"), "Reading needs a feature and orientation")
    seen = set()
    for glyph in value["glyphs"]:
        word, char = glyph["wordIndex"], glyph["charIndex"]
        require(0 <= word < len(words) and 0 <= char < len(words[word]), "Glyph index outside reading")
        require(words[word][char] == glyph["glyph"] and (word, char) not in seen, "Glyph identity or index")
        seen.add((word, char))
        glyph["nativeBox"] = native_box(glyph["boxXYXY"], value["view"])
        require(intersection(value["nativeFeatureBox"], glyph["nativeBox"]), "Glyph outside feature")
    for crop in value["diagnosticCrops"]:
        require(crop["view"] in {"upright", "reflected"}, "Unknown diagnostic view")
        native_box(crop["boxXYXY"], crop["view"])
    return value


def positions(words, phrase):
    return [i for i in range(len(words) - len(phrase) + 1) if words[i:i + len(phrase)] == phrase]


def shared_phrases(a, b, minimum):
    for length in range(min(len(a), len(b)), minimum - 1, -1):
        for i in range(len(a) - length + 1):
            phrase = a[i:i + length]
            for j in positions(b, phrase):
                yield i, j, phrase


def match_anchors(a, b, offset_a, offset_b, length):
    peer_boxes = {
        (mark["wordIndex"] - offset_b, mark["charIndex"], mark["glyph"]): mark["nativeBox"]
        for mark in b["glyphs"]
    }
    matches = {}
    for mark in a["glyphs"]:
        key = (mark["wordIndex"] - offset_a, mark["charIndex"], mark["glyph"])
        if 0 <= key[0] < length and intersection(mark["nativeBox"], peer_boxes.get(key)):
            matches[key] = [mark["nativeBox"], peer_boxes[key]]
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--packet-manifest", required=True, type=Path)
    parser.add_argument("--receipts", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    protocol = read(args.protocol)
    packet = read(args.packet_manifest)
    packet_hash = digest(args.packet_manifest)
    require(packet["testId"] == protocol["testId"] and packet["protocolSha256"] == digest(args.protocol),
            "Packet and protocol disagree")
    lock_path = args.receipts / "STAGE1_LOCK.json"
    lock = read(lock_path)
    require(lock["packetManifestSha256"] == packet_hash, "Lock belongs to another packet")
    ordered = {}
    receipt_hashes = {}
    for label in ("A", "B"):
        stage1 = args.receipts / f"READER_{label}_STAGE1.json"
        stage2 = args.receipts / f"READER_{label}_STAGE2.json"
        first = receipt(stage1, label, 1, packet_hash)
        second = receipt(stage2, label, 2, packet_hash)
        first_hash = digest(stage1)
        require(first_hash == lock["receiptHashes"][label] == second["stage1ReceiptSha256"],
                "Stage 1 receipt changed")
        require(timestamp(packet["preparedAtUTC"]) <= timestamp(first["startedAtUTC"])
                <= timestamp(first["completedAtUTC"]) <= timestamp(lock["lockedAtUTC"])
                <= timestamp(second["startedAtUTC"]), "Stage order violation")
        ordered[label] = [first, second]
        receipt_hashes[label] = {"stage1": first_hash, "stage2": digest(stage2)}
    a, ar = ordered["A"]
    b, br = ordered["B"]
    min_words = protocol["rule"]["minimumConsecutiveWords"]
    min_glyphs = protocol["rule"]["minimumSharedAsymmetricGlyphs"]
    controls = all(r["view"] == "upright" and len(r["words"]) >= min_words
                   and r["nativeFeatureBox"] for r in (ar, br))
    located = intersection(a["nativeFeatureBox"], b["nativeFeatureBox"])
    common_words = next((phrase for _, _, phrase in shared_phrases(a["words"], b["words"], 1)), [])
    candidate = []
    outcome = "inconclusive"
    if controls and located and a["view"] == b["view"] == "reflected":
        for start_a, start_b, phrase in shared_phrases(a["words"], b["words"], min_words):
            source_marks = match_anchors(a, b, start_a, start_b, len(phrase))
            if len(source_marks) < min_glyphs:
                continue
            for reference_a in positions(ar["words"], phrase):
                for reference_b in positions(br["words"], phrase):
                    reference_marks = match_anchors(ar, br, reference_a, reference_b, len(phrase))
                    shared = sorted(source_marks.keys() & reference_marks.keys())
                    if len(shared) >= min_glyphs:
                        candidate = [{"readingIndex": list(key), "page74": source_marks[key],
                                      "page75": reference_marks[key]} for key in shared]
                        outcome, common_words = "corroborated", phrase
                        break
                if candidate:
                    break
            if candidate:
                break
    if (outcome == "inconclusive" and controls and located and a["view"] == b["view"]
            and a["words"] == b["words"] and len(common_words) >= min_words
            and len(match_anchors(a, b, 0, 0, len(common_words))) >= min_glyphs
            and (a["view"] == "upright"
                 or (not positions(ar["words"], common_words) and not positions(br["words"], common_words)))):
        outcome = "contradicted-at-observed-feature"
    result = {
        "version": 1, "testId": protocol["testId"], "outcome": outcome,
        "completedAtUTC": max(ar["completedAtUTC"], br["completedAtUTC"], key=timestamp),
        "registrationCommit": packet["registrationCommit"], "protocolSha256": digest(args.protocol),
        "packetManifestSha256": packet_hash, "stage1LockSha256": digest(lock_path),
        "readerReceiptHashes": receipt_hashes, "page75OrientationControlsPassed": bool(controls),
        "commonPage74Feature": located, "agreedPage74Words": common_words,
        "sharedAsymmetricGlyphs": candidate,
        "counts": {"readers": 2, "stageReceipts": 4, "agreedPage74Words": len(common_words),
                   "corroboratedGlyphAnchors": len(candidate)},
        "activity": {"newOCRCalls": 0, "fittedTransforms": 0, "keyChecks": 0},
    }
    with args.out.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print(json.dumps({"testId": result["testId"], "outcome": outcome, **result["counts"]}))


if __name__ == "__main__":
    main()
