#!/usr/bin/env python3
"""Independent saved-output checker for the three fixed Funky/Sand readings.

Only --self-test is used before registration.  --verify independently builds
the three literal texts and compares saved outputs; it performs no semantic,
format, checksum, key, address or network test.  No primary runner is imported.

Requires Python 3.9+ and a Git checkout containing the registration commit
object. A standalone ZIP is insufficient for --verify. Input receipts and fresh
output must be private and outside the entire public Git checkout (including
dist) and every directory named public. Use an absolute output path.
"""
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

TEST_ID = "funky-sand-direct"
BATCH_ID = "keiser-funky-sand-direct-20261110"
MODEL_ID = "funky-upheaval-physical-lines-v1"
SOURCE_REL = "sources/funky-upheaval/physical-lines.json"
SOURCE_SHA = "12ef2d85578b89a164a109c7f5045e9fd28b88fd7ce5c58e30632e242a60eb11"
SOURCE_PATHS = {
    SOURCE_REL, "sources/funky-upheaval/SOURCE_REGISTER.json",
    "sources/funky-upheaval/pages/108.jpg", "sources/funky-upheaval/pages/109.jpg",
    "sources/funky-upheaval/pages/110.jpg", "sources/funky-upheaval/pages/111.jpg",
    "analysis_outputs/continuation_20261109/george_sand_research.md",
}
SCRIPT_PATHS = {"scripts/funky_sand_direct.py", "scripts/verify_funky_sand_direct.py"}
READING_IDS = ["SAND-FW-ALL", "SAND-ODD-LINES", "SAND-EVEN-CONTROL"]
ROLES = {"title", "deck", "lead", "body", "display-emphasis", "attributed-quotation",
         "facts-display", "name-list", "section-introduction", "work-list", "closing-display"}
PAGE_COUNTS = {108: 11, 109: 41, 110: 29, 111: 34}
CONTENT_PAGE_COUNTS = {"108": 7, "109": 41, "110": 29, "111": 34}
ROLE_COUNTS = {"title": 4, "deck": 7, "lead": 12, "body": 53, "display-emphasis": 10,
               "attributed-quotation": 10, "facts-display": 5, "name-list": 3,
               "section-introduction": 3, "work-list": 5, "closing-display": 3}
MAX_SOURCE_CODEPOINTS = 50000
MAX_OUTPUT_CODEPOINTS = 100000


class GuardError(Exception):
    pass


def need(condition, message):
    if not condition:
        raise GuardError(message)


def digest(data):
    """File/output integrity only; never a prose-to-key operation."""
    return hashlib.sha256(data).hexdigest()


def matching_bytes(data, expected):
    need(digest(data) == expected, "file-integrity-pin-mismatch")


def normative_parameters(encoding):
    """Independently stated protocol parameters, not imported from the runner."""
    return {
        "id": TEST_ID, "family": "fixed-literal-source-reading", "branchId": "text-lines",
        "inputPaths": [SOURCE_REL, "sources/funky-upheaval/SOURCE_REGISTER.json"] +
                      ["sources/funky-upheaval/pages/" + str(p) + ".jpg" for p in PAGE_COUNTS] +
                      ["analysis_outputs/continuation_20261109/george_sand_research.md"],
        "implementationPaths": ["scripts/funky_sand_direct.py", "scripts/verify_funky_sand_direct.py"],
        "protocolPath": "analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.json",
        "sourceModel": {"id": MODEL_ID, "physicalRows": 115, "titleRowsExcluded": 4,
                        "contentRows": 111, "contentRowsByPrintedPage": CONTENT_PAGE_COUNTS,
                        "rolePopulation": ROLE_COUNTS, "encoding": encoding,
                        "ordering": "Stored source order; remove only title rows, then one global content-row index.",
                        "issueAndDateAuthenticated": False},
        "readings": [
            {"id": READING_IDS[0], "selectedRowCount": 111,
             "rule": "First nonempty U+0020-delimited chunk of each retained row, preserving every glyph; join with one U+0020. Stop if a first chunk contains no ASCII letter/digit."},
            {"id": READING_IDS[1], "selectedRowCount": 56,
             "rule": "Whole retained rows numbered 1,3,...,111 globally after title exclusion; join with LF."},
            {"id": READING_IDS[2], "selectedRowCount": 55,
             "rule": "Whole retained rows numbered 2,4,...,110 globally after title exclusion; join with LF; predeclared parity control."}],
        "boundaries": {"pageOrBlockResets": False, "roleSelectionsBeyondTitleExclusion": False,
                       "caseOrUnicodeNormalization": False, "punctuationRemoval": False,
                       "wrapJoining": False, "reversals": False, "initialsOrFinals": False,
                       "selectedSubstrings": False, "keyFormatOrChecksumChecks": False,
                       "wordlistFiltering": False, "proseToKeyHashing": False,
                       "seedOrAddressDerivation": False, "networkQueries": 0},
        "caps": {"maximumInputOrRegisteredBlobBytes": 2000000, "maximumProtocolBytes": 1000000,
                 "maximumRowCodepoints": 2000, "maximumSourceCodepoints": 100000,
                 "maximumOutputCodepoints": 200000, "maximumReadings": 3},
        "outputPolicy": {"privateArtifacts": ["READINGS.private.json", "READINGS.private.txt"],
                         "rawOutputOutsidePublicCheckoutRequired": True},
    }


def validate_normative_parameters(test, encoding):
    need(isinstance(test, dict), "invalid-protocol-test")
    canonical = lambda value: json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)
    for key, expected in normative_parameters(encoding).items():
        if key == "outputPolicy":
            need(isinstance(test.get(key), dict), "protocol-output-policy-mismatch")
            for field, value in expected.items():
                need(canonical(test[key].get(field)) == canonical(value), "protocol-output-policy-mismatch")
        else:
            need(canonical(test.get(key)) == canonical(expected), "protocol-normative-parameter-mismatch")


def first_chunk(text):
    # A manual U+0020 walk deliberately avoids Unicode-aware split/tokenizers.
    end = 0
    letter_or_digit = False
    while end < len(text) and text[end] != " ":
        char = text[end]
        if "A" <= char <= "Z" or "a" <= char <= "z" or "0" <= char <= "9":
            letter_or_digit = True
        end += 1
    need(letter_or_digit, "initial-chunk-has-no-ASCII-letter-or-digit")
    return text[:end]


def validate_rows(rows, production=True):
    need(isinstance(rows, list) and 0 < len(rows) <= 115, "invalid-row-population")
    ids, pages, previous_page, codepoints = set(), Counter(), 0, 0
    title_count = 0
    for index, row in enumerate(rows, 1):
        need(isinstance(row, dict), "invalid-row-record")
        need(set(row) == {"id", "ordinal", "printedPage", "role", "block", "lineInBlock", "printedText"},
             "unexpected-row-fields")
        need(isinstance(row["id"], str) and row["id"] and row["id"] not in ids,
             "invalid-or-duplicate-row-id")
        ids.add(row["id"])
        need(type(row["ordinal"]) is int and row["ordinal"] == index, "row-ordinal-mismatch")
        page = row["printedPage"]
        need(type(page) is int and page in PAGE_COUNTS and page >= previous_page, "row-page-order-mismatch")
        previous_page = page
        pages[page] += 1
        need(row["role"] in ROLES, "unexpected-row-role")
        title_count += row["role"] == "title"
        need(isinstance(row["block"], str) and row["block"] and
             type(row["lineInBlock"]) is int and row["lineInBlock"] > 0, "invalid-block-metadata")
        text = row["printedText"]
        need(isinstance(text, str) and 0 < len(text) <= 1000, "invalid-row-text-size")
        need(not text.startswith(" ") and not text.endswith(" ") and "  " not in text and
             all(char == " " or (char.isprintable() and not char.isspace()) for char in text),
             "invalid-row-spacing-or-line-break")
        codepoints += len(text)
    need(codepoints <= MAX_SOURCE_CODEPOINTS, "source-character-cap-exceeded")
    if production:
        need(len(rows) == 115 and title_count == 4 and dict(pages) == PAGE_COUNTS,
             "fixed-source-population-mismatch")
        need(all(row["role"] == "title" for row in rows[:4]) and
             all(row["role"] != "title" for row in rows[4:]), "fixed-title-population-mismatch")
    return rows


def build_readings(rows, production=True):
    validate_rows(rows, production)
    chunks, odd, even = [], [], []
    retained = 0
    for row in rows:
        if row["role"] == "title":
            continue
        retained += 1
        text = row["printedText"]
        chunks.append(first_chunk(text))
        if retained % 2:
            odd.append(text)
        else:
            even.append(text)
    if production:
        need([retained, len(odd), len(even)] == [111, 56, 55], "fixed-reading-population-mismatch")
    texts = [" ".join(chunks), "\n".join(odd), "\n".join(even)]
    need(sum(map(len, texts)) <= MAX_OUTPUT_CODEPOINTS, "output-character-cap-exceeded")
    return [{"id": name, "selectedRowCount": count, "text": text}
            for name, count, text in zip(READING_IDS, [retained, len(odd), len(even)], texts)]


def descriptors(readings):
    return [{"id": item["id"], "selectedRowCount": item["selectedRowCount"],
             "codepoints": len(item["text"]), "utf8Bytes": len(item["text"].encode("utf-8")),
             "sha256": digest(item["text"].encode("utf-8"))} for item in readings]


def text_export(readings):
    sections = []
    for item in readings:
        sections.append("[" + item["id"] + "]\nSelected rows: " + str(item["selectedRowCount"]) +
                        "\n" + item["text"])
    return ("KEY404 / three fixed literal readings\nSource SHA-256: " + SOURCE_SHA + "\n" +
            "\n\n".join(sections) + "\n").encode("utf-8")


def self_test():
    def row(index, text, role="body", page=108):
        return {"id": "synthetic-" + str(index), "ordinal": index, "printedPage": page,
                "role": role, "block": "synthetic", "lineInBlock": index, "printedText": text}
    fixture = [row(1, "Title", "title"), row(2, "Read, first", "deck"),
               row(3, "THE second"), row(4, "Other", "title"),
               row(5, "“Exact” third", "attributed-quotation"), row(6, "don't fourth", "name-list", 109),
               row(7, "MiXeD-fifth fifth", "facts-display", 109),
               row(8, "(Six) sixth", "display-emphasis", 110), row(9, "Élan seventh", "closing-display", 111)]
    actual = build_readings(fixture, False)
    expected_texts = ["Read, THE “Exact” don't MiXeD-fifth (Six) Élan",
                      "Read, first\n“Exact” third\nMiXeD-fifth fifth\nÉlan seventh",
                      "THE second\ndon't fourth\n(Six) sixth"]
    need([x["text"] for x in actual] == expected_texts, "synthetic-complete-text-control-failed")
    need([x["selectedRowCount"] for x in actual] == [7, 4, 3], "synthetic-count-control-failed")
    need(first_chunk("Alpha\u00a0Beta rest") == "Alpha\u00a0Beta", "non-ASCII-space-control-failed")
    need(first_chunk("Solo") == "Solo", "single-chunk-control-failed")
    need(first_chunk("'A-b' rest") == "'A-b'", "literal-punctuation-control-failed")
    integrity = descriptors([{"id": "synthetic", "selectedRowCount": 1, "text": "é A"}])[0]
    need(integrity["codepoints"] == 3 and integrity["utf8Bytes"] == 4,
         "UTF8-integrity-length-control-failed")
    matching_bytes(b"synthetic-file", digest(b"synthetic-file"))
    rejected = 0
    try:
        matching_bytes(b"synthetic-file", digest(b"changed-synthetic-file"))
    except GuardError:
        rejected += 1
    else:
        raise GuardError("synthetic-pin-mismatch-was-accepted")
    for malformed in ["", " leading", "trailing ", "two  gaps", "a\tb", "a\rb", "a\nb",
                      "a\u00a0b", "a\u200bb", "a\u2028b", "... rest", "— rest"]:
        try:
            build_readings([row(1, malformed)], False)
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-malformed-row-was-accepted")
    for mutation in ["ordinal", "duplicate-id", "role", "page-order", "population", "row-size"]:
        test = json.loads(json.dumps(fixture))
        if mutation == "ordinal": test[0]["ordinal"] = 2
        elif mutation == "duplicate-id": test[1]["id"] = test[0]["id"]
        elif mutation == "role": test[1]["role"] = "unknown"
        elif mutation == "page-order": test[-1]["printedPage"] = 108
        elif mutation == "row-size": test[1]["printedText"] = "a" * 1001
        try:
            build_readings(test, mutation == "population")
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-mutation-was-accepted")
    # Full-sized synthetic population exercises production counts without target data.
    full, number = [], 0
    for page, count in PAGE_COUNTS.items():
        for local in range(count):
            index = len(full) + 1
            if index <= 4:
                full.append(row(index, "Synthetic title", "title", page))
            else:
                number += 1
                full.append(row(index, "Marker" + str(number) + " remainder", "body", page))
    whole = build_readings(full)
    need([x["selectedRowCount"] for x in whole] == [111, 56, 55], "synthetic-full-population-failed")
    need(whole[0]["text"] == " ".join("Marker" + str(i) for i in range(1, 112)),
         "synthetic-full-first-chunks-failed")
    test = normative_parameters({"normalization": "none"})
    validate_normative_parameters(test, {"normalization": "none"})
    for key in ["id", "readings", "boundaries", "sourceModel", "outputPolicy"]:
        bad = json.loads(json.dumps(test))
        bad[key] = None
        try:
            validate_normative_parameters(bad, {"normalization": "none"})
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-protocol-mutation-was-accepted")
    for bad_path in [Path(__file__).resolve().parents[3] / "dist/synthetic-raw-output",
                     Path("/tmp/public/synthetic-raw-output")]:
        try:
            private_path(bad_path, False)
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-public-path-was-accepted")
    return {"status": "PASS", "syntheticReadingsCompared": 6, "rejectionControls": rejected,
            "targetSourceReads": 0, "targetReadingsGenerated": 0, "cryptoChecks": 0, "networkQueries": 0}


def private_path(path, existing=True):
    path = Path(path).resolve()
    need(not any(part.lower() == "public" for part in path.parts), "private-path-required")
    need(not path.is_relative_to(Path(__file__).resolve().parents[3]), "private-path-outside-public-checkout-required")
    if existing:
        need(path.is_file() and path.stat().st_mode & 0o077 == 0, "private-input-permissions-required")
    else:
        need(not path.exists() and path.parent.is_dir(), "fresh-private-output-required")
    return path


def read_json(path, maximum):
    need(path.is_file() and path.stat().st_size <= maximum, "input-size-or-existence-guard")
    data = path.read_bytes()
    need(not data.startswith(b"\xef\xbb\xbf"), "UTF8-without-BOM-required")
    return json.loads(data.decode("utf-8")), data


def registered_pins(research, protocol_path, registration):
    need(re.fullmatch(r"[a-f0-9]{40}", registration) is not None, "invalid-registration-commit")
    need(protocol_path.resolve().is_relative_to(research), "protocol-outside-research-root")
    protocol, protocol_bytes = read_json(protocol_path, 100000)
    need(protocol.get("version") == 1 and protocol.get("batchId") == BATCH_ID and
         isinstance(protocol.get("test"), dict), "protocol-identity-mismatch")
    source_pins, script_pins = protocol.get("sourceHashes"), protocol.get("scriptHashes")
    need(isinstance(source_pins, dict) and set(source_pins) == SOURCE_PATHS and
         isinstance(script_pins, dict) and set(script_pins) == SCRIPT_PATHS, "pin-population-mismatch")
    need(source_pins[SOURCE_REL] == SOURCE_SHA, "fixed-source-hash-mismatch")
    need((research / "scripts/verify_funky_sand_direct.py").resolve() == Path(__file__).resolve(),
         "verifier-runtime-location-mismatch")
    all_pins = {**source_pins, **script_pins,
                str(protocol_path.resolve().relative_to(research)): digest(protocol_bytes)}
    for relative, expected in all_pins.items():
        need(re.fullmatch(r"[a-f0-9]{64}", expected) is not None, "invalid-pin")
        file = (research / relative).resolve()
        need(file.is_relative_to(research) and file.is_file() and file.stat().st_size <= 16000000,
             "pinned-file-guard")
        matching_bytes(file.read_bytes(), expected)
        saved = subprocess.run(["git", "show", registration + ":public/research/" + relative],
                               cwd=research, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=20, check=False)
        need(saved.returncode == 0 and digest(saved.stdout) == expected, "registration-bytes-mismatch")
    return protocol, digest(protocol_bytes)


def verify(args):
    research = Path(__file__).resolve().parent.parent
    source_path = research / SOURCE_REL
    if args.source:
        need(Path(args.source).resolve() == source_path.resolve(), "source-path-mismatch")
    out = private_path(args.out, False)
    protocol, protocol_sha = registered_pins(research, Path(args.protocol), args.registration_commit)
    model, _ = read_json(source_path, 100000)
    need(model.get("version") == 1 and model.get("modelId") == MODEL_ID and
         model.get("issueNumber") is None and model.get("publicationDate") is None,
         "source-model-mismatch")
    need(model.get("encoding", {}).get("normalization") == "none" and
         model["encoding"].get("originalTypesettingUnicodeRecovered") is False and
         model["encoding"].get("glyphPerfectOriginalByteStringClaimed") is False, "encoding-policy-mismatch")
    validate_normative_parameters(protocol["test"], model["encoding"])
    readings = build_readings(model.get("rows"))
    saved, readings_bytes = read_json(private_path(args.readings), 200000)
    expected = {"schemaVersion": 1, "testId": TEST_ID, "sourceSha256": SOURCE_SHA, "readings": readings}
    need(saved == expected, "complete-saved-readings-mismatch")
    # Equality above compares all fields; compare encoded text explicitly as well.
    need(all(a["text"].encode("utf-8") == b["text"].encode("utf-8")
             for a, b in zip(saved["readings"], readings)), "saved-UTF8-text-mismatch")
    text_path = private_path(Path(args.readings).with_name("READINGS.private.txt"))
    need(text_path.stat().st_size <= 200000, "private-text-artifact-cap-exceeded")
    text_bytes = text_path.read_bytes()
    need(text_bytes == text_export(readings), "complete-private-text-export-mismatch")
    result, result_bytes = read_json(private_path(args.result), 200000)
    need(set(result) == {"version", "testId", "batchId", "status", "startedAtUTC", "completedAtUTC",
         "registrationCommit", "protocolSha256", "sourceHashes", "scriptHashes", "sourceModel",
         "scopeComplete", "readingsGenerated", "semanticReviewComplete", "counts", "readingDescriptors",
         "privateArtifactIntegrity", "activity", "limitations"}, "result-public-allowlist-mismatch")
    need(result.get("version") == 1 and result.get("testId") == TEST_ID and
         result.get("batchId") == BATCH_ID, "result-identity-mismatch")
    need(result.get("registrationCommit") == args.registration_commit and
         result.get("protocolSha256") == protocol_sha and
         result.get("sourceHashes") == protocol["sourceHashes"] and
         result.get("scriptHashes") == protocol["scriptHashes"], "result-provenance-mismatch")
    need(result.get("sourceModel") == {"id": MODEL_ID, "physicalRows": 115, "titleRowsExcluded": 4,
         "contentRows": 111, "contentRowsByPrintedPage": CONTENT_PAGE_COUNTS,
         "issueNumber": None, "publicationDate": None, "eligibility": "unverified-conditional",
         "originalTypesettingBytesRecovered": False}, "result-source-model-mismatch")
    need(result.get("scopeComplete") is True and result.get("readingsGenerated") is True and
         result.get("semanticReviewComplete") is False and "completeNegative" not in result,
         "result-completion-scope-mismatch")
    need(result.get("counts") == {"readings": 3, "selectedRows": [111, 56, 55],
         "submittedCodepoints": sum(len(x["text"]) for x in readings)}, "result-counts-mismatch")
    need(result.get("readingDescriptors") == descriptors(readings), "output-integrity-descriptors-mismatch")
    need(result.get("privateArtifactIntegrity") == {"readingsJsonSha256": digest(readings_bytes),
         "readingsTextSha256": digest(text_bytes)}, "private-artifact-integrity-mismatch")
    need(result.get("status") == "readings-generated-awaiting-review" and
         result.get("limitations") == protocol["test"].get("limitations"), "technical-result-status-mismatch")
    need(set(result.get("activity", {})) == {"variantsBeyondRegisteredReadings", "keyFormatChecks",
         "checksumChecks", "wordlistFilters", "proseToKeyHashes", "seedDerivations", "addressDerivations",
         "semanticScoring", "networkQueries", "transactions"} and
         all(type(value) is int and value == 0 for value in result["activity"].values()),
         "unexpected-run-activity")
    parse = lambda value: datetime.fromisoformat(value.replace("Z", "+00:00"))
    need(parse(result["startedAtUTC"]) <= parse(result["completedAtUTC"]), "result-time-order-mismatch")
    receipt = {"version": 1, "testId": TEST_ID, "status": "PASS", "passed": True,
               "completedAtUTC": datetime.now(timezone.utc).isoformat(),
               "registrationCommit": args.registration_commit, "protocolSha256": protocol_sha,
               "verifierSha256": digest(Path(__file__).read_bytes()), "sourceSha256": SOURCE_SHA,
               "primaryResultSha256": digest(result_bytes), "sourcePinsMatched": len(SOURCE_PATHS),
               "scriptPinsMatched": len(SCRIPT_PATHS), "completePrivateReadingRecordsMatch": True,
               "fullUTF8TextsMatch": True, "outputIntegrityDescriptorsMatch": True,
               "privateTextExportMatches": True, "privateArtifactIntegrityMatches": True,
               "readingCount": 3, "selectedRows": [111, 56, 55], "semanticReviewComplete": False,
               "scope": "Deterministic saved-output agreement only; no semantic or puzzle conclusion.",
               "targetCryptoChecks": 0, "addressDerivations": 0, "networkQueries": 0}
    out.mkdir(mode=0o700)
    fd = os.open(out / "INDEPENDENT_CHECK.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=True, indent=2)
        stream.write("\n")
    return {"status": "PASS", "readingCount": 3, "fullSavedReadingsMatch": True,
            "semanticReviewComplete": False, "cryptoChecks": 0, "networkQueries": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--verify", action="store_true")
    for option in ["source", "protocol", "registration-commit", "result", "readings", "out"]:
        parser.add_argument("--" + option)
    args = parser.parse_args()
    if args.self_test:
        need(all(getattr(args, name) is None for name in
                 ["source", "protocol", "registration_commit", "result", "readings", "out"]),
             "self-test-does-not-accept-input-paths")
        safe = self_test()
    else:
        need(all(getattr(args, name) for name in
                 ["protocol", "registration_commit", "result", "readings", "out"]), "explicit-verify-arguments-required")
        safe = verify(args)
    print(json.dumps(safe, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except GuardError as error:
        print(json.dumps({"status": "FAIL", "reason": str(error)}))
        sys.exit(1)
    except Exception:
        print(json.dumps({"status": "FAIL", "reason": "verification-could-not-complete"}))
        sys.exit(1)
