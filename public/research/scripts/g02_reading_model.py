#!/usr/bin/env python3
"""Replay the frozen G02 word choices and enumerate the small opposite-color language."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

AUDIT = "analysis_outputs/continuation_20261110/g02_joint_color_audit/"
LINES = "sources/printed-lines.json"
GEOMETRY = "sources/word-geometry-20261110.json"
MEMBERSHIP = AUDIT + "MEMBERSHIP.json"
RESULT = AUDIT + "RESULT.json"
INDEPENDENT = AUDIT + "INDEPENDENT_VERIFICATION.json"
REGISTRATION = AUDIT + "REGISTRATION.json"
MODEL_INPUTS = (LINES, GEOMETRY, MEMBERSHIP, RESULT, INDEPENDENT, REGISTRATION)
PAIRS = ((76, 77), (77, 76), (78, 79), (79, 78))
SELECTORS = ("same-color", "opposite-color", "source-only", "target-only")
ORDERS = ("forward", "reverse")
MODES = ("words-spaced", "words-joined", "initials", "finals")
PAIR_COUNTS = (263, 274, 226, 199)
STATES = ("must", "optional", "out", "unresolved")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_inputs(research, protocol_path):
    """Return the protocol and its byte-checked inputs."""
    protocol = json.loads(protocol_path.read_bytes())
    verified = {}
    for section in ("sourceHashes", "scriptHashes"):
        for rel, digest in protocol[section].items():
            relative = Path(rel)
            require(not relative.is_absolute() and ".." not in relative.parts, "Invalid pin path")
            path = (research / relative).resolve()
            require(path.is_relative_to(research), "Pin points outside research root")
            content = path.read_bytes()
            require(sha256(content).hexdigest() == digest, f"Changed pin: {rel}")
            verified[rel] = content
    own_path = Path(__file__).resolve().relative_to(research).as_posix()
    require(own_path in protocol["scriptHashes"], "Current model script is unpinned")
    require(all(name in protocol["sourceHashes"] for name in MODEL_INPUTS), "Missing model input pin")
    return protocol, verified


def load_model(verified):
    """Bind membership IDs to original ordered tokens and reproduce all scope counts."""
    lines, geometry, inventory, result, replay, registration = (
        json.loads(verified[name]) for name in MODEL_INPUTS
    )
    membership_hash = sha256(verified[MEMBERSHIP]).hexdigest()
    require(result["sourceModelComplete"] is True, "Source model is incomplete")
    require(result["inventory"]["sha256"] == membership_hash, "Result-to-inventory mismatch")
    require(replay["verificationPassed"] is True and replay["allOrderedMetadataFieldsMatch"] is True,
            "Prior source reconstruction is incomplete")
    require(replay["primaryInventorySha256"] == membership_hash, "Prior inventory digest mismatch")
    require(replay["primaryResultSha256"] == sha256(verified[RESULT]).hexdigest(),
            "Prior result digest mismatch")
    require(registration["registrationCommit"] == result["registrationCommit"] ==
            replay["registrationCommit"], "Prior registration mismatch")
    require(replay["registrationReceiptSha256"] == sha256(verified[REGISTRATION]).hexdigest(),
            "Prior registration digest mismatch")
    require(replay["pairs"] == result["pairs"] and replay["globalSelectors"] ==
            result["globalSelectors"], "Prior scope count mismatch")
    require(inventory["definition"]["pairs"] == [list(pair) for pair in PAIRS]
            and inventory["definition"]["selectors"] == list(SELECTORS), "Source scopes changed")

    rows = lines["rows"]
    by_row = {row["id"]: row for row in geometry["rows"]}
    require(len(rows) == len(by_row) == len(geometry["rows"]) == 142, "Row population changed")
    require(len({row["id"] for row in rows}) == 142, "Duplicate canonical row")
    records = inventory["wordRecords"]
    require(len(records) == sum(PAIR_COUNTS), "Membership population changed")
    require(len({record["wordId"] for record in records}) == len(records), "Duplicate word ID")

    model = {}
    offset = 0
    for index, (source, target) in enumerate(PAIRS):
        pair_rows = [row for row in rows if row["page"] == target]
        entries = []
        for row in pair_rows:
            mapped = by_row[row["id"]]
            require(mapped["status"] == "complete" and mapped["lexicallyComplete"] is True
                    and mapped["page"] == target, "Incomplete row")
            lexical = [word for word in mapped["words"] if any(char.isalnum() for char in word["text"])]
            tokens = [token for token in row["text"].split() if any(char.isalnum() for char in token)]
            require([word["text"] for word in lexical] == tokens, "Token alignment differs")
            for ordinal, word in enumerate(lexical, 1):
                record = records[offset]
                offset += 1
                require(word["verified"] is True, "Unverified token")
                identity = (record["source"], record["target"], record["rowId"],
                            record["wordId"], record["wordOrdinalInRow"])
                require(identity == (source, target, row["id"], word["id"], ordinal),
                        "Ordered membership identity differs")
                states = record["selectorMembership"]
                require(set(states) == set(SELECTORS) and
                        all(value in STATES[:3] for value in states.values()), "Unresolved membership")
                entries.append((word["id"], word["text"], states))
        require(len(entries) == PAIR_COUNTS[index], "Pair word count differs")
        scope = f"{source}-to-{target}"
        compare_counts(entries, result["pairs"][index]["selectors"])
        model[scope] = entries
    require(offset == len(records), "Unexpected extra membership records")
    model["global"] = [entry for entries in model.values() for entry in entries]
    compare_counts(model["global"], result["globalSelectors"])
    return model


def compare_counts(entries, expected):
    for selector in SELECTORS:
        counts = Counter(states[selector] for _, _, states in entries)
        actual = {state: counts[state] for state in STATES}
        actual["independentAssignmentUpperBound"] = str(2 ** counts["optional"])
        require(actual == expected[selector], f"Selector counts differ: {selector}")


def project(words, mode):
    if mode == "words-spaced":
        return " ".join(words)
    if mode == "words-joined":
        return "".join(words)
    if mode == "initials":
        return "".join(next(char for char in word if char.isalnum()) for word in words)
    require(mode == "finals", "Unknown projection")
    return "".join(next(char for char in reversed(word) if char.isalnum()) for word in words)


def opposite_readings(entries):
    options = [(identifier, word) for identifier, word, states in entries
               if states["opposite-color"] == "optional"]
    require(len(options) == 3 and all(states["opposite-color"] != "must"
            for _, _, states in entries), "Opposite-color population changed")
    records = []
    for bits in product("01", repeat=3):
        assignment = "".join(bits)
        forward = [item for item, bit in zip(options, bits) if bit == "1"]
        for order in ORDERS:
            selected = forward if order == "forward" else forward[::-1]
            ids = [identifier for identifier, _ in selected]
            words = [word for _, word in selected]
            for mode in MODES:
                records.append(dict(id=f"{assignment}/{order}/{mode}", assignment=assignment,
                                    order=order, mode=mode, selectedWordIds=ids,
                                    text=project(words, mode)))
    return records


def layers(entries, selector):
    return [[None, word] if states[selector] == "optional" else [word]
            for _, word, states in entries if states[selector] != "out"]


def private_dir(path, research):
    require(path.is_absolute(), "Supply an absolute output path")
    root = research.parent.parent
    resolved = path.resolve()
    require(not resolved.is_relative_to(root) and "public" not in
            {part.lower() for part in resolved.parts}, "Output must be outside public paths")
    resolved.mkdir(mode=0o700, parents=False, exist_ok=False)
    return resolved


def write_private(path, content):
    path.touch(mode=0o600, exist_ok=False)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def self_test():
    items = [("a", "(Écho!)", {"opposite-color": "optional"}),
             ("b", "Beta-2.", {"opposite-color": "optional"}),
             ("c", "C", {"opposite-color": "optional"})]
    records = opposite_readings(items)
    require(len(records) == 64 and len({r["id"] for r in records}) == 64, "Wrong label population")
    lookup = {record["id"]: record for record in records}
    require(lookup["000/reverse/finals"]["text"] == "", "Empty path changed")
    require(lookup["110/reverse/words-spaced"]["text"] == "Beta-2. (Écho!)", "Spacing or order changed")
    require(lookup["110/reverse/words-joined"]["text"] == "Beta-2.(Écho!)", "Compaction changed")
    require(lookup["110/reverse/initials"]["text"] == "BÉ", "Initials changed")
    require(lookup["110/reverse/finals"]["text"] == "2o", "Finals changed")
    require(lookup["110/reverse/finals"]["selectedWordIds"] == ["b", "a"], "Word identity changed")
    require(layers(items, "opposite-color") == [[None, word] for _, word, _ in items], "Optional edge changed")
    print(json.dumps({"syntheticControlsPassed": True, "targetReadingsGenerated": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--research", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--registration-commit")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    require(all((args.research, args.protocol, args.registration_commit, args.out)), "Missing run arguments")
    require(re.fullmatch(r"[0-9a-f]{40}", args.registration_commit), "Expected full registration commit")
    research = args.research.resolve()
    protocol, verified = verify_inputs(research, args.protocol)
    require(protocol["testId"] == "g02-opposite-color-reading-review", "Wrong opposite-color protocol")
    model = load_model(verified)
    records = opposite_readings(model["global"])
    output = private_dir(args.out, research)
    write_private(output / "READINGS.private.json", {"records": records})
    print(json.dumps({"labeledReadings": len(records), "distinctReadings": len({r["text"] for r in records})}))


if __name__ == "__main__":
    main()
