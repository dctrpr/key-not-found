#!/usr/bin/env python3
"""Audit the exact displayed captions of the March Bitcoin Beach interview."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis_outputs/continuation_20261111/bitcoin_beach_interview/SOURCE.json"
PATTERNS = {
    "magazine": r"\b(?:magazin\w*|overdose|censorship resistant|printed (?:page|issue|copy)|physical (?:copy|magazine))\b",
    "puzzle": r"\b(?:puzzl\w*|treasure\s*hunt|bount\w*|reward|prize|hidden|hid|hiding|encoded?|cryptogram|cipher|steganogra\w*|decod\w*)\b",
    "keyOrPrize": r"\b(?:private\s*keys?|secret\s*keys?|(?:twenty|20|ten|10)\s*(?:bit\s*coins?|btc)|(?:bit\s*coins?|btc)\s*(?:twenty|20|ten|10))\b",
    "direction": r"\b(?:mirrors?|mirroring|backwards?|revers\w*|first\s*words?|last\s*words?|every other line|alternat\w*\s*line|letters?|acrostic|read (?:the|it|this))\b",
    "causality": r"\b(?:chaos|financial crisis|2008|two thousand eight|bitcoins?\s+(?:is|are)\s+toxic|toxic\s+bitcoins?)\b",
    "creatorReference": r"\b(?:george sand|alfred de musset|schott|issue (?:24|twenty four)|20[ -]btc|bitcoin is toxic af)\b",
}


def digest(data):
    return sha256(data).hexdigest()


def seconds(time):
    if not re.fullmatch(r"(?:\d+:)?\d{1,2}:[0-5]\d", time):
        raise ValueError(f"Invalid displayed timestamp: {time}")
    total = 0
    for unit in time.split(":"):
        total = total * 60 + int(unit)
    return total


def analyze(raw, source):
    transcript = source["transcript"]
    if digest(raw) != transcript["sha256"] or len(raw) != transcript["bytes"]:
        raise ValueError("Displayed caption snapshot differs from the recorded witness")
    rows = json.loads(raw)
    if len(rows) != transcript["cueCount"] or any(set(row) != {"time", "text"} or not row["text"].strip() for row in rows):
        raise ValueError("Caption shape or count differs")
    times = [seconds(row["time"]) for row in rows]
    starts = [b - a for a, b in zip(times, times[1:])]
    if not all(gap > 0 for gap in starts) or rows[0]["time"] != transcript["firstCue"] or rows[-1]["time"] != transcript["lastCue"]:
        raise ValueError("Displayed cue ordering differs")

    matches = {}
    for name, expression in PATTERNS.items():
        records = []
        for index, row in enumerate(rows):
            text = row["text"]
            next_text = rows[index + 1]["text"] if index + 1 < len(rows) else ""
            for hit in re.finditer(expression, text + " " + next_text, re.IGNORECASE | re.ASCII):
                if hit.start() < len(text):
                    records.append({"ordinal": index + 1, "time": row["time"],
                                    "withinPairOffset": hit.start(), "crossesCueBoundary": hit.end() > len(text),
                                    "matchedTextSha256": digest(hit[0].encode("utf-8"))})
        matches[name] = records

    segments = []
    for start, stop in [(0, 2880), (2880, source["youtube"]["runtimeSeconds"] + 1)]:
        indices = [index for index, stamp in enumerate(times) if start <= stamp < stop]
        packet = "".join(f'{index+1:03d}\t{rows[index]["time"]}\t{rows[index]["text"]}\n' for index in indices).encode("utf-8")
        segments.append({"firstOrdinal": indices[0] + 1, "lastOrdinal": indices[-1] + 1,
                         "firstCue": rows[indices[0]]["time"], "lastCue": rows[indices[-1]]["time"],
                         "cueCount": len(indices), "packetSha256": digest(packet)})
    return {"snapshotSha256": digest(raw), "cuesScanned": len(rows), "maximumStartGapSeconds": max(starts),
            "runtimeAfterLastCueStartSeconds": source["youtube"]["runtimeSeconds"] - times[-1],
            "redactedCueCount": sum(bool(re.search(r"\[\s*_+\s*\]", row["text"])) for row in rows),
            "readerPackets": segments, "matchedOccurrencesByGroup": {name: len(group) for name, group in matches.items()},
            "matches": matches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    source_raw = SOURCE.read_bytes()
    result = {"sourceSha256": digest(source_raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              **analyze(args.transcript.read_bytes(), json.loads(source_raw))}
    with args.out.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2, allow_nan=False)
        output.write("\n")


if __name__ == "__main__":
    main()
