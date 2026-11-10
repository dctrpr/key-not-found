#!/usr/bin/env python3
"""Validate and merge the two registered G07 source-glyph reviews."""
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


TEST_ID = "g07-mirror-glyph-orientation"
FOLDER = "analysis_outputs/continuation_20261110/g07_glyph_review"
PROTOCOL = f"{FOLDER}/PROTOCOL.json"
INVENTORY = f"{FOLDER}/BASELINE_BOXES.json"
INVENTORY_SHA = "2d7a6b97564ec8e85c3ac086a4dba87e9631666d3329d0a709c514d88b627fa0"
SCRIPT = "scripts/merge_g07_glyph_review.py"
PAGE_COUNTS = dict(zip(range(73, 81), (10, 7, 20, 22, 17, 10, 13, 15)))
CONTROL_EXPECTATIONS = {"c01": "symmetric-only", "c02": "reversed", "c03": "ordinary"}
ORIENTATIONS = ("ordinary", "reversed", "mixed", "symmetric-only", "nontext", "unclear")
INSTRUCTIONS = ("none", "candidate", "unclear")
REVERSED = ("reversed", "mixed")
WIDTH, HEIGHT = 2544, 3264
PADDING, SHEET_ROWS = 8, 4
MAX_JSON, MAX_FILE = 1_000_000, 32_000_000


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


def verify_registration(research, protocol, commit, receipt_path):
    require(isinstance(commit, str) and re.fullmatch(r"[a-f0-9]{40}", commit), "Invalid Git commit")
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
    require(spec["testId"] == TEST_ID and type(spec["paddingPx"]) is int
            and spec["paddingPx"] == PADDING and type(spec["sheetRows"]) is int
            and spec["sheetRows"] == SHEET_ROWS and spec["controlExpectations"] == CONTROL_EXPECTATIONS,
            "Wrong registered protocol parameters")
    sources, scripts = spec["sourceHashes"], spec["scriptHashes"]
    require(isinstance(sources, dict) and isinstance(scripts, dict) and not set(sources) & set(scripts)
            and sources.get(INVENTORY) == INVENTORY_SHA
            and scripts.get(SCRIPT) == sha(read_bytes(Path(__file__))),
            "Registered inventory or executing code identity changed")
    pins = {**sources, **scripts}
    receipt_bytes = read_bytes(receipt_path)
    verified_at = verify_receipt(strict_json(receipt_bytes), commit, protocol_sha, len(pins))
    inventory = None
    for relative, digest in pins.items():
        check_digest(digest)
        content = registered_bytes(relative, MAX_FILE)
        require(sha(content) == digest, "Registered file hash changed")
        if relative == INVENTORY:
            inventory = strict_json(content)
    return protocol_sha, verified_at, sha(receipt_bytes), inventory


def expected_packet(inventory):
    require(inventory["testId"] == "G07" and inventory["counts"] ==
            {"normal": 207, "horizontalMirror": 114, "total": 321}
            and len(inventory["records"]) == 321, "Wrong G07 baseline population")
    mirrored = [record for record in inventory["records"] if record["orientation"] == "horizontal-mirror"]
    require(len(mirrored) == 114, "Incomplete mirror inventory")
    targets, sheets = {}, {}
    at = 0
    for page, count in PAGE_COUNTS.items():
        for index in range(count):
            record = mirrored[at]
            at += 1
            job = f"p{page}-baseline-m1"
            stream = f"G07:{job}:observation{index}"
            require(type(record["printedPage"]) is int and record["printedPage"] == page
                    and record["jobId"] == job and record["publicStreamId"] == stream
                    and record["imageDimensionsPx"] == [WIDTH, HEIGHT], "Wrong mirror source identity")
            bounds = record["uprightPixelEnclosure"]
            require(isinstance(bounds, list) and len(bounds) == 4 and all(type(n) is int for n in bounds),
                    "Malformed inventory pixel bounds")
            left, top, right, bottom = bounds
            require(0 <= left < right <= WIDTH and 0 <= top < bottom <= HEIGHT,
                    "Invalid inventory pixel bounds")
            name = f"p{page}-{index + 1:02d}"
            sheet = f"sheet-p{page}-{index // SHEET_ROWS + 1:02d}.png"
            sheets.setdefault(sheet, []).append(name)
            targets[name] = {"id": name, "printedPage": page, "publicStreamId": stream,
                             "sheet": sheet, "uprightPath": f"u-{name}.png",
                             "reflectedPath": f"r-{name}.png",
                             "pixelBounds": [max(0, left - PADDING), max(0, top - PADDING),
                                             min(WIDTH, right + PADDING), min(HEIGHT, bottom + PADDING)]}
    return targets, sheets


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


def verify_packet(doc, commit, protocol_sha, verified_at, targets, sheets, verify_asset):
    require_fields(doc, ("version", "testId", "registrationCommit", "protocolSha256", "preparedAtUTC",
                         "targets", "controls", "assets", "sheets"), "Unexpected packet fields")
    require(type(doc["version"]) is int and doc["version"] == 1 and doc["testId"] == TEST_ID
            and doc["registrationCommit"] == commit and doc["protocolSha256"] == protocol_sha,
            "Packet registration changed")
    prepared_at = timestamp(doc["preparedAtUTC"])
    require(verified_at < prepared_at, "Packet creation predates registration")
    submitted = index_records(doc["targets"], targets, "id", next(iter(targets.values())).keys())
    for name, record in submitted.items():
        require(type(record["printedPage"]) is int and isinstance(record["pixelBounds"], list)
                and all(type(n) is int for n in record["pixelBounds"]) and record == targets[name],
                "Target crop differs from the registered source bounds")
    submitted_sheets = index_records(doc["sheets"], sheets, "path", ("path", "targetIds"))
    require(all(record["targetIds"] == sheets[path] for path, record in submitted_sheets.items()),
            "Wrong sheet target order")
    controls = index_records(doc["controls"], CONTROL_EXPECTATIONS, "id", ("id", "path", "sha256"))
    asset_paths = set(sheets)
    for target in targets.values():
        asset_paths.update((target["uprightPath"], target["reflectedPath"]))
    for name, control in controls.items():
        require(control["path"] == f"control-{name}.png", "Wrong control asset path")
        asset_paths.add(control["path"])
    assets = index_records(doc["assets"], asset_paths, "path", ("path", "sha256"))
    for control in controls.values():
        require(control["sha256"] == assets[control["path"]]["sha256"], "Control asset pin differs")
    for path, asset in assets.items():
        check_digest(asset["sha256"])
        verify_asset(path, asset["sha256"])
    return prepared_at, len(assets)


def short_text(value, maximum=300):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= maximum


def validate_review(doc, reviewer, commit, manifest_sha, prepared_at, targets):
    require_fields(doc, ("version", "reviewerId", "registrationCommit", "packetManifestSha256",
                         "startedAtUTC", "completedAtUTC", "peerMarksSeen", "priorTargetMarksSeen",
                         "controls", "rows"), "Unexpected review fields")
    require(type(doc["version"]) is int and doc["version"] == 1 and doc["reviewerId"] == reviewer
            and doc["registrationCommit"] == commit and doc["packetManifestSha256"] == manifest_sha,
            "Reader or source identity mismatch")
    require(doc["peerMarksSeen"] is False and doc["priorTargetMarksSeen"] is False,
            "Reviewer exposure conflicts with the protocol")
    require(prepared_at <= timestamp(doc["startedAtUTC"]) <= timestamp(doc["completedAtUTC"]),
            "Review timing conflicts with packet creation")
    controls = index_records(doc["controls"], CONTROL_EXPECTATIONS, "id", ("id", "orientation", "note"))
    for control in controls.values():
        require(control["orientation"] in ORIENTATIONS and short_text(control["note"]),
                "Malformed control decision")
    rows = index_records(doc["rows"], targets, "id", ("id", "orientation", "instruction", "reversedEvidence",
                                                   "action", "unitOrOrder", "note"))
    for row in rows.values():
        require(row["orientation"] in ORIENTATIONS and row["instruction"] in INSTRUCTIONS
                and short_text(row["note"]) and isinstance(row["reversedEvidence"], list),
                "Malformed target decision")
        require(all(row[key] is None or isinstance(row[key], str) for key in ("action", "unitOrOrder")),
                "Malformed instruction fields")
        for evidence in row["reversedEvidence"]:
            require_fields(evidence, ("glyph", "region"), "Unexpected glyph evidence fields")
            require(short_text(evidence["glyph"], 32) and short_text(evidence["region"]),
                    "Malformed glyph evidence")
        if row["orientation"] in REVERSED:
            require(len(row["reversedEvidence"]) >= 1, "Reverse mark requires source evidence")
        if row["instruction"] == "candidate":
            require(row["orientation"] in REVERSED and len(row["reversedEvidence"]) >= 2
                    and all(value and value.strip() for value in (row["action"], row["unitOrOrder"])),
                    "Candidate requires reversed source evidence and a complete instruction")
        else:
            require(row["action"] is None and row["unitOrOrder"] is None,
                    "Noncandidate instruction fields must be null")
    return {"rows": rows, "controls": controls, "startedAtUTC": doc["startedAtUTC"],
            "completedAtUTC": doc["completedAtUTC"]}


def merge_reviews(a, b, targets):
    regions = []
    ids = {key: [] for key in ("agreedIds", "unresolvedIds", "candidateIds", "disagreementIds", "reverseFlagIds")}
    for name in targets:
        marks = {reader: {k: review["rows"][name][k] for k in ("orientation", "instruction")}
                 for reader, review in (("A", a), ("B", b))}
        first, second = marks.values()
        candidate = any(mark["instruction"] == "candidate" for mark in marks.values())
        disagreement = first != second
        agreed = not disagreement and first["orientation"] != "unclear" and first["instruction"] == "none"
        reverse_flag = any(mark["orientation"] in REVERSED for mark in marks.values())
        ids["agreedIds" if agreed else "unresolvedIds"].append(name)
        for flag, field in ((candidate, "candidateIds"), (disagreement, "disagreementIds"),
                            (reverse_flag, "reverseFlagIds")):
            if flag:
                ids[field].append(name)
        regions.append({"id": name, "printedPage": targets[name]["printedPage"],
                        "agreed": agreed, "candidate": candidate, "disagreement": disagreement,
                        "reverseFlag": reverse_flag, "readerMarks": marks})

    controls, orientation_counts, reader_times = {}, {}, {}
    for reader, review in (("A", a), ("B", b)):
        marks = {name: review["controls"][name]["orientation"] for name in CONTROL_EXPECTATIONS}
        mismatches = [name for name, expected in CONTROL_EXPECTATIONS.items() if marks[name] != expected]
        controls[reader] = {"passed": not mismatches, "observed": marks, "failedControlIds": mismatches}
        observed = Counter(row["orientation"] for row in review["rows"].values())
        orientation_counts[reader] = {orientation: observed[orientation] for orientation in ORIENTATIONS}
        reader_times[reader] = {key: review[key] for key in ("startedAtUTC", "completedAtUTC")}
    controls_passed = all(value["passed"] for value in controls.values())
    negative = controls_passed and len(ids["agreedIds"]) == 114 and not ids["candidateIds"]
    if not controls_passed:
        outcome = "inconclusive-control-failure"
    elif ids["candidateIds"]:
        outcome = "candidate-open-for-pixel-adjudication"
    elif negative:
        outcome = "complete-scoped-negative"
    else:
        outcome = "inconclusive-unresolved-regions"
    return {"regions": regions, **ids, "controls": controls, "controlsPassed": controls_passed,
            "orientationCounts": orientation_counts, "readerTimes": reader_times,
            "completeScopedNegative": negative, "outcome": outcome}


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


def merge_registered(args):
    research = args.research.resolve(strict=True)
    out = fresh_private_output(args.out, research.parent.parent)
    commit = args.registration_commit
    protocol_sha, verified_at, receipt_sha, inventory = verify_registration(
        research, args.protocol.resolve(strict=True), commit, args.registration_receipt)
    started = utc()
    targets, sheets = expected_packet(inventory)
    manifest = args.packet_manifest.resolve(strict=True)
    directory = args.packet_directory.resolve(strict=True) if args.packet_directory else manifest.parent
    manifest_bytes = read_bytes(manifest)
    manifest_sha = sha(manifest_bytes)

    def verify_asset(path, digest):
        require(sha(read_bytes(checked_path(directory, path), MAX_FILE)) == digest,
                "Packet asset hash changed")

    prepared, assets = verify_packet(strict_json(manifest_bytes), commit, protocol_sha,
                                     verified_at, targets, sheets, verify_asset)
    require(args.reader_a.resolve(strict=True) != args.reader_b.resolve(strict=True), "Expected separate reviews")
    reviews, reader_hashes = [], {}
    for reader, path in (("A", args.reader_a), ("B", args.reader_b)):
        data = read_bytes(path)
        reader_hashes[reader] = sha(data)
        reviews.append(validate_review(strict_json(data), reader, commit, manifest_sha, prepared, targets))
    merged = merge_reviews(*reviews, targets)
    common = {"version": 1, "testId": TEST_ID, "registrationCommit": commit,
              "protocolSha256": protocol_sha, "registrationReceiptSha256": receipt_sha,
              "baselineBoxesSha256": INVENTORY_SHA, "packetManifestSha256": manifest_sha,
              "readerHashes": reader_hashes, "readerExposureDeclarationsVerified": True}
    detail = json_bytes({**common, **merged})
    result = {**common, **{key: value for key, value in merged.items() if key != "regions"},
              "startedAtUTC": started, "completedAtUTC": utc(), "scopeComplete": True,
              "counts": {"readers": 2, "regionsPerReader": len(targets), "sheets": len(sheets),
                         "packetAssetHashesVerified": assets, "agreedRegions": len(merged["agreedIds"]),
                         "unresolvedRegions": len(merged["unresolvedIds"]),
                         "disagreementRegions": len(merged["disagreementIds"]),
                         "candidateRegions": len(merged["candidateIds"]),
                         "reverseFlagRegions": len(merged["reverseFlagIds"])},
              "interpretation": "Reviewer agreement on the saved mirrored baseline regions only.",
              "activity": {"pixelDecodes": 0, "newOCRCalls": 0, "glyphAdjudications": 0, "keyChecks": 0},
              "mergedArtifactSha256": sha(detail)}
    out.mkdir(mode=0o700)
    for filename, data in (("MERGED.json", detail), ("RESULT.json", json_bytes(result))):
        with os.fdopen(os.open(out / filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as handle:
            handle.write(data)


def self_test():
    from copy import deepcopy

    source = {"testId": "G07", "counts": {"normal": 207, "horizontalMirror": 114, "total": 321},
              "records": [{"orientation": "normal"}] * 207}
    for page, count in PAGE_COUNTS.items():
        job = f"p{page}-baseline-m1"
        for index in range(count):
            source["records"].append({"orientation": "horizontal-mirror", "printedPage": page,
                                      "jobId": job, "publicStreamId": f"G07:{job}:observation{index}",
                                      "imageDimensionsPx": [WIDTH, HEIGHT],
                                      "uprightPixelEnclosure": [4, 5, WIDTH - 4, HEIGHT - 5]})
    targets, sheets = expected_packet(source)
    require(len(targets) == 114 and len(sheets) == 32, "Synthetic region population")
    require(targets["p73-01"]["pixelBounds"] == [0, 0, WIDTH, HEIGHT], "Synthetic clipping")
    commit, digest, protocol_sha = "1" * 40, "2" * 64, "3" * 64
    receipt = {"registrationCommit": commit, "protocolSha256": protocol_sha,
               "verifiedAtUTC": "2026-01-01T00:00:00Z", "pinnedBlobsVerified": 8,
               "remoteHeadMatched": True, "targetPixelsOpenedAtVerification": False}
    verified = verify_receipt(receipt, commit, protocol_sha, 7)
    controls = [{"id": name, "path": f"control-{name}.png", "sha256": digest} for name in CONTROL_EXPECTATIONS]
    paths = [path for target in targets.values() for path in (target["uprightPath"], target["reflectedPath"])]
    paths += list(sheets) + [control["path"] for control in controls]
    packet = {"version": 1, "testId": TEST_ID, "registrationCommit": commit, "protocolSha256": protocol_sha,
              "preparedAtUTC": "2026-01-01T00:00:01Z", "targets": list(targets.values()), "controls": controls,
              "assets": [{"path": path, "sha256": digest} for path in paths],
              "sheets": [{"path": path, "targetIds": ids} for path, ids in sheets.items()]}
    checked_assets = []
    prepared, count = verify_packet(packet, commit, protocol_sha, verified, targets, sheets,
                                    lambda path, pin: checked_assets.append((path, pin)))
    require(count == len(checked_assets) == len(set(checked_assets)) == 263, "Synthetic asset population")

    def review(reader):
        return {"version": 1, "reviewerId": reader, "registrationCommit": commit,
                "packetManifestSha256": digest, "startedAtUTC": "2026-01-01T00:00:02Z",
                "completedAtUTC": "2026-01-01T00:00:03Z", "peerMarksSeen": False,
                "priorTargetMarksSeen": False,
                "controls": [{"id": name, "orientation": orientation, "note": "fixture-only"}
                             for name, orientation in CONTROL_EXPECTATIONS.items()],
                "rows": [{"id": name, "orientation": "ordinary", "instruction": "none",
                          "reversedEvidence": [], "action": None, "unitOrOrder": None, "note": "fixture-only"}
                         for name in targets]}

    a, b = review("A"), review("B")

    def validated(doc, reader):
        return validate_review(doc, reader, commit, digest, prepared, targets)

    def merged(first, second):
        return merge_reviews(validated(first, "A"), validated(second, "B"), targets)

    result = merged(a, b)
    require(result["completeScopedNegative"] and len(result["agreedIds"]) == 114,
            "Full agreement did not close the synthetic scope")
    candidate = deepcopy(a)
    candidate["rows"][0].update(orientation="mixed", instruction="candidate", action="fixture-action",
                               unitOrOrder="fixture-unit", reversedEvidence=[{"glyph": "F", "region": "left"},
                                                                           {"glyph": "R", "region": "right"}])
    peer_candidate = {**candidate, "reviewerId": "B"}
    result = merged(candidate, peer_candidate)
    require(result["candidateIds"] == result["unresolvedIds"] == result["reverseFlagIds"] == ["p73-01"]
            and not result["completeScopedNegative"] and not result["disagreementIds"],
            "Agreed candidate incorrectly resolved")
    require(b"fixture-" not in json_bytes(result), "Private reader prose leaked")
    result = merged(candidate, b)
    require(result["disagreementIds"] == ["p73-01"] and result["candidateIds"] == ["p73-01"],
            "Unilateral candidate omitted")
    uncertain_a, uncertain_b = deepcopy(a), deepcopy(b)
    uncertain_a["rows"][0]["instruction"] = uncertain_b["rows"][0]["instruction"] = "unclear"
    result = merged(uncertain_a, uncertain_b)
    require(result["unresolvedIds"] == ["p73-01"] and not result["disagreementIds"],
            "Shared uncertainty incorrectly resolved")
    bad_control = deepcopy(b)
    bad_control["controls"][0]["orientation"] = "ordinary"
    result = merged(a, bad_control)
    require(result["outcome"] == "inconclusive-control-failure" and not result["completeScopedNegative"],
            "Failed control allowed a negative")
    failures = 0

    def reject(operation):
        nonlocal failures
        try:
            operation()
        except ValueError:
            failures += 1
            return
        raise ValueError("Synthetic invalid input accepted")

    for update in ({"rows": a["rows"][:-1]}, {"rows": [a["rows"][0], *a["rows"][:-1]]},
                   {"peerMarksSeen": True}, {"priorTargetMarksSeen": True}, {"reviewerId": "B"},
                   {"packetManifestSha256": "4" * 64}, {"startedAtUTC": receipt["verifiedAtUTC"]},
                   {"controls": a["controls"][:-1]}, {"version": True}):
        reject(lambda: validated({**a, **update}, "A"))
    for update in ({"orientation": "ordinary"}, {"reversedEvidence": [{"glyph": "R", "region": "left"}]},
                   {"action": " "}, {"unitOrOrder": None}):
        broken = deepcopy(candidate)
        broken["rows"][0].update(update)
        reject(lambda: validated(broken, "A"))
    for update in ({"orientation": "reversed"}, {"action": "fixture-action"}, {"note": " "}):
        broken = deepcopy(a)
        broken["rows"][0].update(update)
        reject(lambda: validated(broken, "A"))
    for update in ({"targetPixelsOpenedAtVerification": True}, {"remoteHeadMatched": False},
                   {"pinnedBlobsVerified": 7}):
        reject(lambda: verify_receipt({**receipt, **update}, commit, protocol_sha, 7))
    for update in ({"assets": packet["assets"][:-1]}, {"preparedAtUTC": receipt["verifiedAtUTC"]}):
        reject(lambda: verify_packet({**packet, **update}, commit, protocol_sha, verified,
                                     targets, sheets, lambda *_: None))
    wrong_bounds = deepcopy(packet)
    wrong_bounds["targets"][0]["pixelBounds"][0] = 1
    reject(lambda: verify_packet(wrong_bounds, commit, protocol_sha, verified, targets, sheets, lambda *_: None))
    reject(lambda: strict_json(b'{"id":1,"id":2}'))
    print(json.dumps({"passed": True, "syntheticRegionsPerReader": 114, "syntheticAssets": count,
                      "decisionCases": 5, "rejectedInputs": failures, "targetReads": 0}))


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
            print("PASS complete private G07 review merge")
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        print("Incomplete G07 review merge", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
