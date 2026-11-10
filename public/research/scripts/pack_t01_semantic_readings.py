#!/usr/bin/env python3
"""Lossless inventory/packet copy of one frozen, previously generated artifact."""
import argparse
import datetime
import hashlib
import json
import os
import tempfile
from pathlib import Path

SOURCE_SHA = "2900473b467c74c18ee29f841f0fbb150376ffa42ab8e9862d9d0957fce8b395"
CAP = 10000
PROJECTIONS = ("full_text", "first_words", "last_words", "first_initials",
               "first_finals", "last_initials", "last_finals")


def expected_ids():
    return [f"{unit}/{direction}/{reset}/{parity}/{projection}"
            for unit in ("body", "p75", "p76", "p77", "p78", "p79")
            for direction in ("forward", "reverse")
            for reset in (("global", "page") if unit == "body" else ("page",))
            for parity in (0, 1) for projection in PROJECTIONS]


def group_records(records):
    groups, indices = [], {}
    for ordinal, record in enumerate(records, 1):
        raw = record["text"].encode("utf-8")
        if raw not in indices:
            indices[raw] = len(groups)
            n = len(groups) + 1
            groups.append({"groupOrdinal": n, "id": f"T01-G{n:03d}",
                           "sourceAliases": [], "text": record["text"]})
        group = groups[indices[raw]]
        group["sourceAliases"].append({"sourceRecordOrdinal": ordinal,
                                       "id": record["id"]})
    return groups


def packet_groups(groups, cap):
    packets, current, length = [], [], 0
    for group in groups:
        n = len(group["text"])
        if current and length + n > cap:
            packets.append(current)
            current, length = [], 0
        current.append(group)
        length += n
        if n > cap:
            packets.append(current)
            current, length = [], 0
    if current:
        packets.append(current)
    return packets


def private_output_path(output, site):
    # Check the entered and lexically normalized paths as well as the resolved
    # destination: a Site/public symlink must not turn an unsafe entry into an
    # accepted private path merely by pointing outside the checkout.
    literal = output if output.is_absolute() else Path.cwd() / output
    normalized = Path(os.path.abspath(literal))
    canonical = literal.resolve()
    site = site.resolve()
    # Ancestors catch an alias that enters Site/public and then exits through a
    # later symlink; comparing the final destination alone cannot detect that.
    candidates = [literal, normalized, canonical]
    candidates.extend(parent.resolve() for parent in literal.parents)
    for candidate in candidates:
        assert not candidate.is_relative_to(site), "Output must be outside Site"
        assert "public" not in [part.lower() for part in candidate.parts], "Public output path rejected"
    return canonical


def output_guard_controls():
    with tempfile.TemporaryDirectory(prefix="key404-packet-path-control-") as name:
        root = Path(name)
        site, outside, public = root / "site", root / "outside", root / "public"
        for directory in (site, outside, public):
            directory.mkdir()
        (site / "escape").symlink_to(outside, target_is_directory=True)
        (root / "site-alias").symlink_to(site, target_is_directory=True)
        (public / "escape").symlink_to(outside, target_is_directory=True)
        (root / "public-alias").symlink_to(public, target_is_directory=True)
        rejected = [site / "new", public / "new", site / "escape" / "new",
                    root / "site-alias" / "new", public / "escape" / "new",
                    root / "public-alias" / "new", public / ".." / "outside" / "new",
                    outside / ".." / "site" / "escape" / "new",
                    root / "site-alias" / "escape" / "new",
                    root / "public-alias" / "escape" / "new"]
        for candidate in rejected:
            try:
                private_output_path(candidate, site)
            except AssertionError:
                continue
            raise AssertionError("Unsafe synthetic output accepted")
        assert private_output_path(outside / "new", site) == (outside / "new").resolve()
    return {"passed": True, "unsafePathsRejected": 10,
            "safeFreshPrivatePathAccepted": True,
            "cases": ["raw-Site", "raw-public", "Site-symlink-to-outside",
                      "alias-resolving-to-Site", "public-symlink-to-outside",
                      "alias-resolving-to-public", "raw-public-dotdot",
                      "normalized-Site-symlink-to-outside", "Site-alias-then-escape",
                      "public-alias-then-escape"]}


def controls():
    rows = [{"id": str(i), "text": s} for i, s in enumerate(
        ["é", "e\u0301", "é", "A", "a", " a ", "", "\n", "x" * 11], 1)]
    groups = group_records(rows)
    assert len(groups) == 8
    assert [a["sourceRecordOrdinal"] for a in groups[0]["sourceAliases"]] == [1, 3]
    packets = packet_groups(groups, 10)
    assert len(packets[-1]) == 1 and len(packets[-1][0]["text"]) == 11
    assert [g for p in packets for g in p] == groups
    for group in groups:
        for alias in group["sourceAliases"]:
            assert rows[alias["sourceRecordOrdinal"] - 1]["text"].encode("utf-8") == group["text"].encode("utf-8")
    assert json.loads(json.dumps(groups, ensure_ascii=False)) == groups
    return {"passed": True, "controls": ["byte-equality-only-dedup",
        "Unicode-composed-distinct-from-decomposed", "case-and-whitespace-retained",
        "empty-and-newline-retained", "all-aliases-ordered", "whole-oversize-text",
        "packet-order", "UTF8-JSON-roundtrip"]}


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    path.chmod(0o600)


def package(source, output):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    check = controls()
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    obj = json.loads(raw)
    assert list(obj) == ["testId", "streams"] and obj["testId"] == "T01"
    records = obj["streams"]
    assert len(records) == 196 and [r["id"] for r in records] == expected_ids()
    assert all(list(r) == ["id", "text"] and isinstance(r["text"], str) for r in records)
    groups = group_records(records)
    assert len(groups) == 152
    packets = packet_groups(groups, CAP)
    # A private output must be fresh and outside the source's whole Site checkout.
    source = source.resolve()
    assert "public" in source.parts
    site = Path(*source.parts[:source.parts.index("public")])
    output = private_output_path(output, site)
    output.mkdir(mode=0o700)
    output.chmod(0o700)
    inventory, mapping, covered = [], [], []
    for ordinal, packet in enumerate(packets, 1):
        filename = f"PACKET_{ordinal:03d}.json"
        save(output / filename, {"version": 1, "testId": "T01",
             "sourceArtifactSha256": SOURCE_SHA, "packetOrdinal": ordinal,
             "groups": packet})
        cp = sum(len(g["text"]) for g in packet)
        assert cp <= CAP or len(packet) == 1
        inventory.append({"file": filename, "packetOrdinal": ordinal,
             "groupOrdinals": [g["groupOrdinal"] for g in packet],
             "groups": len(packet), "sourceAliases": sum(len(g["sourceAliases"]) for g in packet),
             "textCodepoints": cp, "textUTF8Bytes": sum(len(g["text"].encode("utf-8")) for g in packet),
             "oversizeWholeText": cp > CAP})
        loaded = json.loads((output / filename).read_bytes())
        assert loaded["groups"] == packet
        for group in loaded["groups"]:
            for alias in group["sourceAliases"]:
                index = alias["sourceRecordOrdinal"] - 1
                assert alias["id"] == records[index]["id"]
                assert group["text"].encode("utf-8") == records[index]["text"].encode("utf-8")
                covered.append(index + 1)
                mapping.append({**alias, "groupOrdinal": group["groupOrdinal"],
                    "groupId": group["id"], "packetOrdinal": ordinal,
                    "textCodepoints": len(group["text"]),
                    "textUTF8Bytes": len(group["text"].encode("utf-8"))})
    assert sorted(covered) == list(range(1, 197)) and len(set(covered)) == 196
    mapping.sort(key=lambda x: x["sourceRecordOrdinal"])
    assert [m["id"] for m in mapping] == expected_ids()
    save(output / "MAPPING.json", {"version": 1, "testId": "T01", "sourceArtifactSha256": SOURCE_SHA,
         "records": mapping})
    result = {"version": 1, "testId": "T01", "startedAtUTC": started,
        "completedAtUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "sourceArtifact": "analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json",
        "sourceArtifactSha256": SOURCE_SHA, "sourceBytes": len(raw),
        "sourceRecords": len(records), "uniqueUTF8ByteStrings": len(groups),
        "sourceRecordCodepoints": sum(len(r["text"]) for r in records),
        "sourceRecordUTF8Bytes": sum(len(r["text"].encode("utf-8")) for r in records),
        "uniqueTextCodepoints": sum(len(g["text"]) for g in groups),
        "uniqueTextUTF8Bytes": sum(len(g["text"].encode("utf-8")) for g in groups),
        "packetCount": len(packets), "packetTextCodepointCap": CAP,
        "maximumPacketTextCodepoints": max(p["textCodepoints"] for p in inventory),
        "maximumIndividualTextCodepoints": max(len(g["text"]) for g in groups),
        "oversizeWholeTextPackets": sum(p["oversizeWholeText"] for p in inventory),
        "orderedIDsMatchOwningGenerator": True, "aliasesCoveredExactlyOnce": True,
        "everyAliasUTF8EqualsGroupText": True, "packetsRoundtripVerified": True,
        "ordering": "Groups in first source occurrence order; aliases retain original record ordinals; packet group order unchanged.",
        "deduplication": "Exact UTF8 byte equality only; no per-text cryptographic hash, normalization or whitespace transform.",
        "controls": check, "packets": inventory,
        "activity": {"targetArtifactOpenedForInventory": True, "newCandidatePopulation": False,
             "semanticReview": False, "targetTransforms": 0, "shapeScans": 0,
             "checksums": 0, "derivations": 0, "networkRequests": 0}}
    save(output / "INVENTORY.json", result)
    return {k: result[k] for k in ("sourceRecords", "uniqueUTF8ByteStrings", "packetCount",
        "maximumPacketTextCodepoints", "maximumIndividualTextCodepoints", "oversizeWholeTextPackets",
        "uniqueTextCodepoints", "uniqueTextUTF8Bytes", "sourceRecordCodepoints", "sourceRecordUTF8Bytes")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        assert args.source is None and args.out is None
        print(json.dumps({**controls(), "outputPathGuards": output_guard_controls()}))
    else:
        assert args.source is not None and args.out is not None
        print(json.dumps(package(args.source, args.out)))
