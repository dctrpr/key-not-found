#!/usr/bin/env python3
"""Merge the two registered Issue 24 page-tile reviews."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


TEST_ID = "issue24-full-page-glyph-review"
PROTOCOL = "analysis_outputs/continuation_20261111/full_page_glyph_review/PROTOCOL.json"
SCRIPT = "scripts/merge_full_page_glyph_review.py"
PDF = "magazine.pdf"
PDF_SHA = "a30c61f8c49674afb7bccc6680d6477f6e919175386a2422de0a944db4e76c13"
MAX_JSON, MAX_FILE = 1_000_000, 32_000_000
CONTROL_EXPECTATIONS = {"c01": "ordinary", "c02": "reversed", "c03": "symmetric-only",
                        "c04": "rotated-ordinary"}
ORIENTATIONS = set(CONTROL_EXPECTATIONS.values()) | {"mixed", "nontext", "unclear"}
KINDS = ("reversed", "possible-reversal", "rotated-ordinary", "unclear")
POSITIONS = (("NW", [0, 0, 1320, 1680]), ("NE", [1224, 0, 2544, 1680]),
             ("SW", [0, 1584, 1320, 3264]), ("SE", [1224, 1584, 2544, 3264]))
TILES = {}
for page in range(73, 81):
    for position, bounds in POSITIONS:
        tile_id = f"p{page}-{position}"
        TILES[tile_id] = {"id": tile_id, "page": page, "box": bounds,
                          "uprightPath": f"u-{tile_id}.png", "reflectedPath": f"r-{tile_id}.png"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require_fields(value, fields, message):
    require(isinstance(value, dict) and set(value) == set(fields), message)


def strict_json(data):
    def unique_fields(pairs):
        fields = dict(pairs)
        require(len(fields) == len(pairs), "Repeated JSON field")
        return fields

    def invalid_number(_):
        raise ValueError("Nonfinite JSON number")

    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_fields, parse_constant=invalid_number)


def read_bytes(path, limit=MAX_JSON):
    require(path.is_file() and path.stat().st_size <= limit, "Input file missing or oversized")
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    require(len(data) <= limit, "Input size changed")
    return data


def timestamp(value):
    require(isinstance(value, str)
            and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", value),
            "Expected UTC timestamp")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def check_digest(digest):
    require(isinstance(digest, str) and re.fullmatch(r"[a-f0-9]{64}", digest), "Invalid SHA-256")


def checked_path(root, relative):
    require(isinstance(relative, str) and bool(relative), "Missing registered path")
    name = Path(relative)
    require(not name.is_absolute() and ".." not in name.parts and name.as_posix() == relative,
            "Expected a canonical relative path")
    path = (root / name).resolve(strict=True)
    require(path.is_relative_to(root) and path.relative_to(root).as_posix() == relative,
            "Registered path alias or escape")
    return path


def verify_receipt(receipt, commit, protocol_sha, pin_count):
    require_fields(receipt, ("registrationCommit", "protocolSha256", "remoteHeadMatched",
                   "verifiedAtUTC", "pinnedBlobsVerified", "targetPixelsOpenedAtVerification"),
                   "Unexpected registration receipt fields")
    require(receipt["registrationCommit"] == commit and receipt["protocolSha256"] == protocol_sha
            and receipt["remoteHeadMatched"] is True
            and receipt["targetPixelsOpenedAtVerification"] is False,
            "No verified pre-pixel registration")
    require(type(receipt["pinnedBlobsVerified"]) is int
            and receipt["pinnedBlobsVerified"] == pin_count + 1, "Registration pin count mismatch")
    return timestamp(receipt["verifiedAtUTC"])


def index_records(records, expected, key, fields):
    require(isinstance(records, list) and len(records) == len(expected), "Incomplete record population")
    indexed = {}
    for record in records:
        require_fields(record, fields, "Unexpected record fields")
        name = record[key]
        require(isinstance(name, str) and name in expected and name not in indexed,
                "Unknown or repeated record ID")
        indexed[name] = record
    return indexed


def fresh_private_output(path, checkout):
    entered = path if path.is_absolute() else Path.cwd() / path
    canonical = entered.resolve()
    require(canonical.parent.is_dir() and not entered.is_symlink() and not canonical.exists(),
            "Output must be fresh")
    for location in (entered, Path(os.path.abspath(entered)), canonical,
                     *(ancestor.resolve() for ancestor in entered.parents)):
        require(not location.is_relative_to(checkout)
                and "public" not in [part.lower() for part in location.parts], "Output must be private")
    return canonical


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def verify_registration(research, protocol, commit, receipt_path):
    require(re.fullmatch(r"[a-f0-9]{40}", commit), "Invalid Git commit")
    require(research.name == "research" and research.parent.name == "public", "Wrong research root")
    checkout = research.parent.parent
    require(protocol == checked_path(research, PROTOCOL), "Wrong protocol path")

    def git(*args):
        return subprocess.run(["git", "-C", str(checkout), *args], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, timeout=30, check=True).stdout

    require(Path(os.fsdecode(git("rev-parse", "--show-toplevel")).strip()).resolve() == checkout
            and git("cat-file", "-t", commit) == b"commit\n", "Invalid registered Git object")

    def registered_bytes(relative, limit):
        path = checked_path(research, relative)
        blob = f"{commit}:public/research/{relative}"
        require(int(git("cat-file", "-s", blob)) <= limit, "Registered blob exceeds cap")
        current = read_bytes(path, limit)
        require(current == git("cat-file", "blob", blob), "Current file differs from registered blob")
        return current

    protocol_bytes = registered_bytes(PROTOCOL, MAX_JSON)
    protocol_sha = sha(protocol_bytes)
    spec = strict_json(protocol_bytes)
    require(spec["testId"] == TEST_ID and spec["controlExpectations"] == CONTROL_EXPECTATIONS,
            "Wrong registered protocol")
    sources, scripts = spec["sourceHashes"], spec["scriptHashes"]
    require(isinstance(sources, dict) and isinstance(scripts, dict) and not set(sources) & set(scripts)
            and sources.get(PDF) == PDF_SHA and scripts.get(SCRIPT) == sha(read_bytes(Path(__file__))),
            "Registered source or executing code changed")
    pins = {**sources, **scripts}
    receipt_bytes = read_bytes(receipt_path)
    verified = verify_receipt(strict_json(receipt_bytes), commit, protocol_sha, len(pins))
    for relative, digest in pins.items():
        check_digest(digest)
        require(sha(registered_bytes(relative, MAX_FILE)) == digest, "Registered file hash changed")
    return protocol_sha, verified, sha(receipt_bytes)


def verify_packet(packet, commit, protocol_sha, verified, verify_asset):
    require_fields(packet, ("version", "testId", "registrationCommit", "protocolSha256",
                            "preparedAtUTC", "tiles", "controls", "assets"), "Unexpected packet fields")
    require(type(packet["version"]) is int and packet["version"] == 1 and packet["testId"] == TEST_ID
            and packet["registrationCommit"] == commit and packet["protocolSha256"] == protocol_sha,
            "Packet registration changed")
    prepared = timestamp(packet["preparedAtUTC"])
    require(verified < prepared, "Packet creation predates registration")
    tiles = index_records(packet["tiles"], TILES, "id", ("id", "page", "box", "uprightPath", "reflectedPath"))
    require(list(tiles) == list(TILES), "Unexpected tile order")
    paths = set()
    for name, tile in tiles.items():
        require(tile == TILES[name] and type(tile["page"]) is int
                and all(type(n) is int for n in tile["box"]), "Tile geometry changed")
        paths.update((tile["uprightPath"], tile["reflectedPath"]))
    controls = index_records(packet["controls"], CONTROL_EXPECTATIONS, "id", ("id", "path", "sha256"))
    for name, control in controls.items():
        require(control["path"] == f"control-{name}.png", "Wrong control asset path")
        paths.add(control["path"])
    assets = index_records(packet["assets"], paths, "path", ("path", "sha256"))
    for control in controls.values():
        require(assets[control["path"]]["sha256"] == control["sha256"], "Control asset pin differs")
    for path, asset in assets.items():
        check_digest(asset["sha256"])
        verify_asset(path, asset["sha256"])
    return prepared, len(assets)


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def safe_finding(finding, reader, tile, ordinal):
    require_fields(finding, ("kind", "box", "glyphs", "turnDegrees", "action", "unitOrOrder", "note"),
                   "Unexpected finding fields")
    require(finding["kind"] in KINDS and nonempty_text(finding["note"]), "Malformed finding")
    glyphs = finding["glyphs"]
    require(isinstance(glyphs, list) and all(nonempty_text(g) and len(g) <= 32 for g in glyphs),
            "Malformed glyph evidence")
    turn = finding["turnDegrees"]
    require(type(turn) is int and turn in (0, 90, 180, 270), "Invalid turn")
    action, unit = finding["action"], finding["unitOrOrder"]
    instruction = action is not None or unit is not None
    if instruction:
        require(finding["kind"] == "reversed" and len(glyphs) >= 2
                and all(nonempty_text(value) and len(value) <= 300 for value in (action, unit)),
                "Instruction needs a complete action, unit and reversed evidence")
    box = finding["box"]
    require(isinstance(box, list) and len(box) == 4 and all(type(n) is int for n in box),
            "Invalid finding box")
    left, top, right, bottom = tile["box"]
    x0, y0, x1, y1 = box
    require(0 <= x0 < x1 <= right - left and 0 <= y0 < y1 <= bottom - top,
            "Finding box exceeds tile")
    return {"readerId": reader, "tileId": tile["id"], "findingOrdinal": ordinal,
            "page": tile["page"], "kind": finding["kind"], "tileBox": box,
            "pageBox": [left + x0, top + y0, left + x1, top + y1],
            "turnDegrees": turn, "glyphCount": len(glyphs), "instructionReported": instruction}


def validate_review(review, reader, commit, packet_sha, prepared):
    require_fields(review, ("version", "reviewerId", "registrationCommit", "packetManifestSha256",
                            "startedAtUTC", "completedAtUTC", "peerMarksSeen", "priorTargetMarksSeen",
                            "controls", "tiles"), "Unexpected review fields")
    require(type(review["version"]) is int and review["version"] == 1 and review["reviewerId"] == reader
            and review["registrationCommit"] == commit and review["packetManifestSha256"] == packet_sha,
            "Reader or packet identity changed")
    require(review["peerMarksSeen"] is False and review["priorTargetMarksSeen"] is False,
            "Reviewer exposure conflicts with the protocol")
    require(prepared <= timestamp(review["startedAtUTC"]) <= timestamp(review["completedAtUTC"]),
            "Review timing conflicts with packet creation")
    controls = index_records(review["controls"], CONTROL_EXPECTATIONS, "id", ("id", "orientation", "note"))
    for control in controls.values():
        require(control["orientation"] in ORIENTATIONS and nonempty_text(control["note"]),
                "Malformed control decision")
    control_marks = {name: controls[name]["orientation"] for name in CONTROL_EXPECTATIONS}
    failed = [name for name, expected in CONTROL_EXPECTATIONS.items() if control_marks[name] != expected]
    tiles = index_records(review["tiles"], TILES, "id", ("id", "note", "findings"))
    findings = []
    for name, tile in TILES.items():
        mark = tiles[name]
        require(nonempty_text(mark["note"]) and isinstance(mark["findings"], list), "Malformed tile review")
        for ordinal, finding in enumerate(mark["findings"], 1):
            findings.append(safe_finding(finding, reader, tile, ordinal))
    return {"findings": findings, "controls": {"passed": not failed, "observed": control_marks,
                                                "failedControlIds": failed},
            "startedAtUTC": review["startedAtUTC"], "completedAtUTC": review["completedAtUTC"]}


def merge_reviews(a, b):
    findings = a["findings"] + b["findings"]
    kinds = Counter(mark["kind"] for mark in findings)
    instructions = sum(mark["instructionReported"] for mark in findings)
    unresolved = kinds["possible-reversal"] + kinds["unclear"]
    controls_pass = a["controls"]["passed"] and b["controls"]["passed"]
    outcome = "no-instruction-reported"
    if not controls_pass:
        outcome = "inconclusive-control-failure"
    elif unresolved or kinds["reversed"]:
        outcome = "needs-source-adjudication"
    return {"findings": findings, "outcome": outcome, "controlsPassed": controls_pass,
            "findingCounts": {kind: kinds[kind] for kind in KINDS},
            "unresolvedFindings": unresolved, "instructionReports": instructions,
            "readerSummary": {reader: {key: review[key] for key in ("controls", "startedAtUTC", "completedAtUTC")}
                              for reader, review in (("A", a), ("B", b))}}


def merge_registered(args):
    research = args.research.resolve(strict=True)
    out = fresh_private_output(args.out, research.parent.parent)
    commit = args.registration_commit
    protocol_sha, verified, receipt_sha = verify_registration(
        research, args.protocol.resolve(strict=True), commit, args.registration_receipt)
    started = utc()
    manifest = args.packet_manifest.resolve(strict=True)
    directory = args.packet_directory.resolve(strict=True) if args.packet_directory else manifest.parent
    manifest_bytes = read_bytes(manifest)
    packet_sha = sha(manifest_bytes)

    def verify_asset(path, digest):
        require(sha(read_bytes(checked_path(directory, path), MAX_FILE)) == digest, "Packet asset hash changed")

    prepared, assets = verify_packet(strict_json(manifest_bytes), commit, protocol_sha, verified, verify_asset)
    require(args.reader_a.resolve(strict=True) != args.reader_b.resolve(strict=True), "Expected separate reviews")
    reviews, reader_hashes = [], {}
    for reader, path in (("A", args.reader_a), ("B", args.reader_b)):
        data = read_bytes(path)
        reader_hashes[reader] = sha(data)
        reviews.append(validate_review(strict_json(data), reader, commit, packet_sha, prepared))
    merged = merge_reviews(*reviews)
    common = {"version": 1, "testId": TEST_ID, "registrationCommit": commit,
              "protocolSha256": protocol_sha, "registrationReceiptSha256": receipt_sha,
              "packetManifestSha256": packet_sha, "sourcePdfSha256": PDF_SHA,
              "readerHashes": reader_hashes, "readerExposureDeclarationsVerified": True}
    detail = json_bytes({**common, "tileIds": list(TILES), **merged})
    result = {**common, **{key: value for key, value in merged.items() if key != "findings"},
              "startedAtUTC": started, "completedAtUTC": utc(), "reviewCoverageComplete": True,
              "counts": {"readers": 2, "tilesPerReader": len(TILES), "tileReviews": 2 * len(TILES),
                         "packetAssetHashesVerified": assets, "readerFindings": len(merged["findings"])},
              "interpretation": "Independent reader marks on the 32 tiles, with source uncertainty retained.",
              "activity": {"pixelDecodes": 0, "newOCRCalls": 0, "glyphAdjudications": 0, "keyChecks": 0},
              "mergedArtifactSha256": sha(detail)}
    out.mkdir(mode=0o700)
    for filename, data in (("MERGED.json", detail), ("RESULT.json", json_bytes(result))):
        with os.fdopen(os.open(out / filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as handle:
            handle.write(data)


def self_test():
    from copy import deepcopy

    commit, digest, protocol_sha = "1" * 40, "2" * 64, "3" * 64
    receipt = {"registrationCommit": commit, "protocolSha256": protocol_sha, "remoteHeadMatched": True,
               "verifiedAtUTC": "2026-01-01T00:00:00Z", "pinnedBlobsVerified": 4,
               "targetPixelsOpenedAtVerification": False}
    verified = verify_receipt(receipt, commit, protocol_sha, 3)
    controls = [{"id": name, "path": f"control-{name}.png", "sha256": digest} for name in CONTROL_EXPECTATIONS]
    paths = [path for tile in TILES.values() for path in (tile["uprightPath"], tile["reflectedPath"])]
    paths.extend(control["path"] for control in controls)
    packet = {"version": 1, "testId": TEST_ID, "registrationCommit": commit, "protocolSha256": protocol_sha,
              "preparedAtUTC": "2026-01-01T00:00:01Z", "tiles": list(TILES.values()), "controls": controls,
              "assets": [{"path": path, "sha256": digest} for path in paths]}
    checked = []
    prepared, assets = verify_packet(packet, commit, protocol_sha, verified, lambda path, pin: checked.append(path))
    require(assets == len(set(checked)) == 68 and len(TILES) == 32, "Wrong synthetic scope")

    def review(reader):
        return {"version": 1, "reviewerId": reader, "registrationCommit": commit, "packetManifestSha256": digest,
                "startedAtUTC": "2026-01-01T00:00:02Z", "completedAtUTC": "2026-01-01T00:00:03Z",
                "peerMarksSeen": False, "priorTargetMarksSeen": False,
                "controls": [{"id": name, "orientation": label, "note": "fixture-only"}
                             for name, label in CONTROL_EXPECTATIONS.items()],
                "tiles": [{"id": name, "note": "fixture-only", "findings": []} for name in TILES]}

    a, b = review("A"), review("B")

    def validated(doc, reader):
        return validate_review(doc, reader, commit, digest, prepared)

    def merged(first, second):
        return merge_reviews(validated(first, "A"), validated(second, "B"))

    require(merged(a, b)["outcome"] == "no-instruction-reported", "Empty review outcome")
    finding = {"kind": "reversed", "box": [1, 2, 3, 4], "glyphs": ["F", "R"], "turnDegrees": 0,
               "action": "fixture-action", "unitOrOrder": "fixture-unit", "note": "fixture-only"}
    a["tiles"][3]["findings"] = [finding]
    b["tiles"][3]["findings"] = [finding]
    result = merged(a, b)
    require(result["outcome"] == "needs-source-adjudication" and result["instructionReports"] == 2
            and len(result["findings"]) == 2 and b"fixture-" not in json_bytes(result),
            "Overlapping reader marks lost or private fields copied")
    require(all(mark["pageBox"] == [1225, 1586, 1227, 1588] for mark in result["findings"]),
            "Tile-to-page translation changed")
    b["tiles"][3]["findings"] = [{**finding, "kind": "possible-reversal", "action": None, "unitOrOrder": None}]
    require(merged(a, b)["unresolvedFindings"] == 1, "Possible reversal was discarded")
    b["controls"][0]["orientation"] = "reversed"
    require(merged(a, b)["outcome"] == "inconclusive-control-failure", "Failed control allowed a result")
    rejected = 0

    def reject(operation):
        nonlocal rejected
        try:
            operation()
        except ValueError:
            rejected += 1
            return
        raise ValueError("Synthetic invalid input accepted")

    for change in ({"tiles": a["tiles"][:-1]}, {"peerMarksSeen": True}, {"priorTargetMarksSeen": True},
                   {"startedAtUTC": receipt["verifiedAtUTC"]}, {"packetManifestSha256": "4" * 64}):
        reject(lambda: validated({**a, **change}, "A"))
    for change in ({"box": [1, 2, 1321, 4]}, {"box": [True, 2, 3, 4]}, {"turnDegrees": 45},
                   {"kind": "possible-reversal"}, {"glyphs": ["F"]}, {"unitOrOrder": None}, {"note": " "}):
        invalid = deepcopy(a)
        invalid["tiles"][3]["findings"][0].update(change)
        reject(lambda: validated(invalid, "A"))
    reject(lambda: verify_packet({**packet, "assets": packet["assets"][:-1]}, commit, protocol_sha,
                                 verified, lambda *_: None))
    reject(lambda: verify_receipt({**receipt, "targetPixelsOpenedAtVerification": True}, commit, protocol_sha, 3))
    print(json.dumps({"passed": True, "syntheticTilesPerReader": 32, "syntheticAssets": assets,
                      "decisionCases": 4, "rejectedInputs": rejected, "targetReads": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--self-test", action="store_true")
    action.add_argument("--merge", action="store_true")
    for flag in ("research", "protocol", "registration-receipt", "packet-manifest", "packet-directory",
                 "reader-a", "reader-b", "out"):
        parser.add_argument(f"--{flag}", type=Path)
    parser.add_argument("--registration-commit")
    args = parser.parse_args()
    paths = (args.research, args.protocol, args.registration_receipt, args.packet_manifest,
             args.reader_a, args.reader_b, args.out, args.registration_commit)
    try:
        if args.self_test:
            require(not any(paths) and args.packet_directory is None, "Synthetic mode accepts no target paths")
            self_test()
        else:
            require(all(paths), "Merge requires explicit registered inputs and private output")
            merge_registered(args)
            print("PASS complete private page-tile merge")
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        print("Incomplete page-tile merge", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
