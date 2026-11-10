#!/usr/bin/env python3
"""Independent offline saved-output verifier for the three column151 readings.

Only --definition and --self-test are source-free. --verify is permitted only
after the actual public registration commit contains this script, the primary
script, all declared source bytes, the shared helper, and the exact protocol.
No primary runner is imported. Seven record-format checks deliberately reuse
the pinned shared helper; this is byte agreement, not an independent engine.
Minikey22/26/30 shape enumeration and question-mark checks are implemented here.
No scalar/address derivation, network access, or semantic scoring is provided.
Python3.9+ and a Git checkout containing the registration object are required.
"""
from collections import Counter
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

TEST_ID = "column151-sand-three-readings"
BATCH_ID = "keiser-column151-sand-three-readings-20261110"
MODEL_ID = "issue24-declared-column151-physical-units-v1"
SOURCE_REL = "sources/issue24-column151/SOURCE.json"
PROTOCOL_REL = "analysis_outputs/continuation_20261110/column151_sand/PROTOCOL.json"
PRIMARY_REL = "scripts/column151_sand_probe.py"
SELF_REL = "scripts/verify_column151_sand.py"
COMMON_REL = "scripts/batch20_common.py"
SOURCE_SHA = "24242d3a31469a7bff5765a756fa51f6f8cfbd40f4a51737d852a172cd117c02"
COMMON_SHA = "48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d"
ENGLISH_SHA = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
CONTROLS_SHA = "d37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b"
SOURCE_PATHS = {
    SOURCE_REL, "magazine.pdf", "sources/printed-lines.json",
    "sources/issue24-column151/NATIVE_SOURCE_PROVENANCE.json",
    "sources/issue24-column151/INDEPENDENT_SOURCE_REVIEW.json",
    "sources/issue24-column151/native-contexts/p73-opener.png",
    "sources/issue24-column151/native-contexts/p75-article-title.png",
    "sources/issue24-column151/native-contexts/p78-display-quote.png",
    "sources/issue24-column151/native-contexts/p79-signature.png",
    "scripts/batch20_support/english.txt", "scripts/batch20_support/controls.json",
}
SCRIPT_PATHS = {PRIMARY_REL, SELF_REL, COMMON_REL}
READING_IDS = ["COLUMN151-FW-ALL", "COLUMN151-ODD-LINES", "COLUMN151-EVEN-CONTROL"]
SELECTED_COUNTS = [151, 76, 75]
COMMON7 = ["wif", "hex64", "bip39", "extended_private", "bip38", "address", "sec_public"]
LENGTHS = (22, 26, 30)
B58 = frozenset("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
FP_DOMAIN_TEXT = "KEY404/batch20/record-fingerprint/v1"
FINGERPRINT_RULE = {"algorithm": "SHA-256", "domainText": FP_DOMAIN_TEXT,
                    "separatorHex": "00", "rule": "SHA256(domain || 0x00 || ASCII(format) || 0x00 || canonical record bytes)"}
PAGE_COUNTS = {"73": 2, "75": 33, "76": 31, "77": 32, "78": 26, "79": 27}
ROLE_COUNTS = {"column-name": 1, "byline": 1, "article-title": 1,
               "body": 142, "display-quotation": 4, "signature": 2}
SOURCE_MODEL = {"id": MODEL_ID, "physicalUnits": 151, "byPrintedPage": PAGE_COUNTS,
                "originalTypesettingBytesRecovered": False}
CAP_INPUT = 2_000_000
CAP_PROTOCOL = 1_000_000
CAP_REGISTERED_BLOB = 20_000_000
CAP_ROW = 2_000
CAP_SOURCE = 100_000
CAP_READINGS = 200_000
CAP_FORMS = 400_000

# Filled from the declared protocol schema before freezing this verifier. This
# dictionary is a metadata contract, not imported primary transformation code.
EXPECTED_TEST = {'id': 'column151-sand-three-readings',
 'title': 'Three fixed Sand readings of the declared column151 source',
 'family': 'fixed-literal-source-reading',
 'branchId': 'text-lines',
 'inputPaths': ['sources/issue24-column151/SOURCE.json',
                'scripts/batch20_support/english.txt',
                'scripts/batch20_support/controls.json',
                'sources/issue24-column151/NATIVE_SOURCE_PROVENANCE.json',
                'sources/issue24-column151/INDEPENDENT_SOURCE_REVIEW.json',
                'sources/issue24-column151/native-contexts/p73-opener.png',
                'sources/issue24-column151/native-contexts/p75-article-title.png',
                'sources/issue24-column151/native-contexts/p78-display-quote.png',
                'sources/issue24-column151/native-contexts/p79-signature.png',
                'sources/printed-lines.json',
                'magazine.pdf'],
 'implementationPaths': ['scripts/column151_sand_probe.py',
                         'scripts/verify_column151_sand.py',
                         'scripts/batch20_common.py'],
 'protocolPath': 'analysis_outputs/continuation_20261110/column151_sand/PROTOCOL.json',
 'sourceModel': {'id': 'issue24-declared-column151-physical-units-v1',
                 'sha256': '24242d3a31469a7bff5765a756fa51f6f8cfbd40f4a51737d852a172cd117c02',
                 'physicalUnits': 151,
                 'byPrintedPage': {'73': 2, '75': 33, '76': 31, '77': 32, '78': 26, '79': 27},
                 'byRole': {'column-name': 1,
                            'byline': 1,
                            'article-title': 1,
                            'body': 142,
                            'display-quotation': 4,
                            'signature': 2},
                 'selection': 'All151 stored units, including2 opener units and149 prior display-inclusive '
                              'units; no role exclusion.',
                 'ordering': 'Exact ordinal/id/page/role layout in code; one global index, no page/block '
                             'reset.',
                 'encoding': 'Preserve every printedText UTF-8 string; no case, punctuation, Unicode or wrap '
                             'normalization.',
                 'originalTypesettingBytesRecovered': False},
 'readings': [{'id': 'COLUMN151-FW-ALL',
               'selectedRowCount': 151,
               'rule': 'First whitespace-delimited chunk of each row, retaining punctuation; join with one '
                       'U+0020.'},
              {'id': 'COLUMN151-ODD-LINES',
               'selectedRowCount': 76,
               'rule': 'Whole rows at global1-based odd positions1,3,...,151; join with LF.'},
              {'id': 'COLUMN151-EVEN-CONTROL',
               'selectedRowCount': 75,
               'rule': 'Whole rows at global1-based even positions2,4,...,150; join with LF; parity '
                       'control.'}],
 'forms': {'rule': 'Exactly each unique saved text and its whitespace-only compacted form, deduplicated '
                   'globally and sorted by Python string order.',
           'maximumReadings': 3,
           'maximumForms': 6,
           'otherTransforms': False},
 'literalValidation': {'commonFormats': ['wif',
                                         'hex64',
                                         'bip39',
                                         'extended_private',
                                         'bip38',
                                         'address',
                                         'sec_public'],
                       'commonImplementationUnchanged': True,
                       'commonSha256': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d',
                       'commonOldMinikeyCheckerCalled': False,
                       'minikey': {'lengths': [22, 26, 30],
                                   'shape': 'Every overlapping embedded S-prefixed Base58 window of '
                                            'exactly22/26/30characters; no outer token boundary requirement.',
                                   'validation': 'SHA256(ASCII(value + question mark))[0]==0;8bit weak check '
                                                 'only.',
                                   'scalarSHA256OfMinikey': False,
                                   'recordFingerprint': 'Existing batch20 domain-separated record '
                                                        'fingerprint; private only.'},
                       'zeroCheckBitFormatsAreOnlyShapeOrRangeLeads': True},
 'registrationGate': 'Full40hex Git commit; protocol and all source/code/support blobs equal actual '
                     'registered public/research bytes and current bytes; fixed public executing path.',
 'caps': {'targetJSONAndPrivateArtifactBytes': 2000000,
          'registeredBlobBytes': 20000000,
          'protocolBytes': 1000000,
          'rowCodepoints': 2000,
          'sourceCodepoints': 100000,
          'readingCodepoints': 200000,
          'totalFormCodepoints': 400000},
 'outputPolicy': {'rawArtifacts': ['READINGS.private.json',
                                   'READINGS.private.txt',
                                   'FORMS.private.json',
                                   'VALIDATION.private.json'],
                  'rawOutsideEntireSiteCheckout': True,
                  'directoryMode': '0700',
                  'fileMode': '0600',
                  'publicReceipt': 'Counts, declared scope and whole-artifact integrity only; no values, '
                                   'record fingerprints, addresses, SEC text or locators.',
                  'keyOutputsPublic': False,
                  'semanticConclusionComputed': False},
 'activityBoundary': {'newSelectors': 0,
                      'reversals': 0,
                      'initialsOrFinals': 0,
                      'arbitraryScalarWindows': 0,
                      'proseToKeyHashes': 0,
                      'minikeyScalarHashes': 0,
                      'addressDerivations': 0,
                      'seedDerivations': 0,
                      'childKeyDerivations': 0,
                      'networkQueries': 0,
                      'transactions': 0},
 'limitations': ['This is a declared151-unit transcription/ordering model, not original typesetting bytes or '
                 'authenticated extraction instructions.',
                 'Three readings and fixed literal-format gates do not exclude readable messages, other '
                 'readings, unknown record families or the whole column.',
                 'Weak minikey checksum, scalar-range-only hex and on-curve SEC matches are leads, not '
                 'solutions or prize/funding proof.',
                 'Registration check is a local Git-object byte check; prior remote publication is '
                 'separately established by the operator.']}
EXPECTED_ACTIVITY = {'newSelectors': 0,
 'reversals': 0,
 'initialsOrFinals': 0,
 'arbitraryScalarWindows': 0,
 'proseToKeyHashes': 0,
 'minikeyScalarHashes': 0,
 'addressDerivations': 0,
 'seedDerivations': 0,
 'childKeyDerivations': 0,
 'networkQueries': 0,
 'transactions': 0}


class GuardError(Exception):
    pass


def require(value, code):
    if not value:
        raise GuardError(code)


def sha(data):
    """Integrity checks only; minikey checks append '?', never a bare key hash."""
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)


def first_chunk(text):
    # Independent manual scan, rather than split(), regex projection or slicing
    # from the primary runner. A punctuation-only first chunk is retained.
    end = 0
    for character in text:
        if character.isspace():
            break
        end += 1
    require(end > 0, "empty-first-whitespace-chunk")
    return text[:end]


def expected_identity():
    result = [("p73-opener-name", 73, "column-name"),
              ("p73-opener-byline", 73, "byline"),
              ("p75_title_0", 75, "article-title")]
    for page, count in [(75, 32), (76, 31), (77, 32), (78, 22), (79, 25)]:
        result.extend(("p" + str(page) + "r" + str(i).zfill(2), page, "body")
                      for i in range(1, count + 1))
        if page == 78:
            result.extend(("p78_graphic_" + str(i), 78, "display-quotation") for i in range(4))
        elif page == 79:
            result.extend(("p79_signature_" + str(i), 79, "signature") for i in range(2))
    return result


def check_rows(rows, production=True):
    require(isinstance(rows, list) and 0 < len(rows) <= 151, "invalid-source-row-population")
    identities, total = [], 0
    for ordinal, row in enumerate(rows, 1):
        require(isinstance(row, dict), "invalid-source-row-record")
        require(all(key in row for key in ["id", "ordinal", "printedPage", "role", "printedText"]),
                "missing-source-row-field")
        require(type(row["ordinal"]) is int and row["ordinal"] == ordinal, "source-ordinal-mismatch")
        require(isinstance(row["id"], str) and row["id"], "invalid-source-row-id")
        require(type(row["printedPage"]) is int and isinstance(row["role"], str), "invalid-source-role-page")
        text = row["printedText"]
        require(isinstance(text, str) and 0 < len(text) <= CAP_ROW, "invalid-source-row-size")
        require(text == text.strip() and all(character == " " or
                (character.isprintable() and not character.isspace()) for character in text),
                "invalid-source-whitespace-or-control")
        identities.append((row["id"], row["printedPage"], row["role"]))
        total += len(text)
    require(len({identity[0] for identity in identities}) == len(rows), "duplicate-source-row-id")
    require(total <= CAP_SOURCE, "source-codepoint-cap")
    if production:
        require(identities == expected_identity(), "fixed-source-identity-order-mismatch")
        require(dict(Counter(str(r["printedPage"]) for r in rows)) == PAGE_COUNTS and
                dict(Counter(r["role"] for r in rows)) == ROLE_COUNTS, "source-population-mismatch")
    return total


def derive_readings(rows, production=True):
    check_rows(rows, production)
    words, odd, even = [], [], []
    all_ids, odd_ids, even_ids = [], [], []
    take_odd = True
    for row in rows:
        text, identifier = row["printedText"], row["id"]
        words.append(first_chunk(text))
        all_ids.append(identifier)
        if take_odd:
            odd.append(text)
            odd_ids.append(identifier)
        else:
            even.append(text)
            even_ids.append(identifier)
        take_odd = not take_odd
    pieces = [(" ".join(words), all_ids), ("\n".join(odd), odd_ids), ("\n".join(even), even_ids)]
    records = [{"id": identifier, "selectedRowCount": len(ids), "selectedRowIds": ids, "text": text}
               for identifier, (text, ids) in zip(READING_IDS, pieces)]
    require(sum(len(record["text"]) for record in records) <= CAP_READINGS, "reading-codepoint-cap")
    if production:
        require([record["selectedRowCount"] for record in records] == SELECTED_COUNTS,
                "fixed-reading-count-mismatch")
    return records


def derive_forms(readings):
    exact = {record["text"] for record in readings}
    # Independent literal whitespace walk, rather than regex substitution.
    compact = {"".join(c for c in text if not c.isspace()) for text in exact}
    forms = sorted(exact.union(compact))
    require(0 < len(forms) <= 6 and sum(map(len, forms)) <= CAP_FORMS, "form-population-or-codepoint-cap")
    return forms


def minikey_fingerprint(value):
    return hashlib.sha256((FP_DOMAIN_TEXT + "\x00minikey\x00" + value).encode("ascii")).hexdigest()


def mini_evaluate(forms):
    occurrence = {str(n): 0 for n in LENGTHS}
    distinct = {n: set() for n in LENGTHS}
    # This direct positional traversal deliberately does not use shared
    # shape_values()/validate_record('minikey') or the primary scanner.
    for text in forms:
        for start, character in enumerate(text):
            if character != "S":
                continue
            for length in LENGTHS:
                if start + length > len(text):
                    continue
                value = text[start:start + length]
                if all(char in B58 for char in value):
                    occurrence[str(length)] += 1
                    distinct[length].add(value)
    shapes, valid = [], []
    valid_counts = {str(n): 0 for n in LENGTHS}
    checks = 0
    for length in LENGTHS:
        for value in sorted(distinct[length]):
            shapes.append({"length": length, "value": value})
            checks += 1
            if hashlib.sha256((value + "?").encode("ascii")).digest()[0] == 0:
                valid_counts[str(length)] += 1
                valid.append({"format": "minikey", "length": length, "checkBits": 8,
                              "private": True, "fingerprint": minikey_fingerprint(value), "value": value})
    summary = {"lengths": list(LENGTHS), "shapeCounts": occurrence,
               "uniqueShapeCounts": {str(n): len(distinct[n]) for n in LENGTHS},
               "checksumCalls": checks, "validCounts": valid_counts,
               "privateReviewRequired": bool(valid), "fingerprintRule": FINGERPRINT_RULE}
    return summary, shapes, valid


def common_path():
    sibling = Path(__file__).resolve().parent / "batch20_common.py"
    if sibling.is_file():
        return sibling
    # Authoring/self-test convenience only. --verify requires the installed
    # public runtime path and all registered bytes before source extraction.
    fallback = Path(__file__).resolve().parents[3] / "site/public/research/scripts/batch20_common.py"
    require(fallback.is_file(), "pinned-shared-helper-not-found")
    return fallback


def load_common():
    file = common_path()
    require(file.stat().st_size <= CAP_INPUT and sha(file.read_bytes()) == COMMON_SHA, "shared-helper-pin-mismatch")
    support = file.parent / "batch20_support"
    for name, pin in [("english.txt", ENGLISH_SHA), ("controls.json", CONTROLS_SHA)]:
        require(sha((support / name).read_bytes()) == pin, "shared-support-pin-mismatch")
    spec = importlib.util.spec_from_file_location("column151_independent_shared7", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def full_validation(readings, forms, common):
    shared = common.scan_streams(readings, COMMON7)
    require(shared["uniqueFormCount"] == len(forms), "shared-seven-form-count-mismatch")
    mini, shapes, valid = mini_evaluate(forms)
    return {"schemaVersion": 1, "testId": TEST_ID, "common7": shared, "minikey": mini,
            "minikeyShapeValues": shapes, "minikeyValidRecords": valid}


def technical_counts(readings, forms, evaluation):
    shared, mini = evaluation["common7"], evaluation["minikey"]
    valid = dict(shared["validCounts"])
    valid["minikey"] = sum(mini["validCounts"].values())
    return {"readings": 3, "selectedRows": [r["selectedRowCount"] for r in readings],
            "submittedCodepoints": sum(len(r["text"]) for r in readings),
            "uniqueStreams": len({r["text"] for r in readings}), "uniqueForms": len(forms),
            "commonShapeCounts": shared["shapeCounts"], "commonUniqueShapeCounts": shared["uniqueShapeCounts"],
            "commonExecutionCount": shared["executionCount"],
            "minikeyShapeCountsByLength": mini["shapeCounts"],
            "minikeyUniqueShapesByLength": mini["uniqueShapeCounts"],
            "minikeyQuestionmarkChecksumCalls": mini["checksumCalls"],
            "minikeyValidCountsByLength": mini["validCounts"], "validCounts": valid,
            "totalValidRecords": sum(valid.values())}


def text_export(readings):
    return ("KEY404 / registered column151 Sand readings\n\n" + "\n\n".join(
        "[" + r["id"] + "]\nSelected rows: " + str(r["selectedRowCount"]) + "\n" + r["text"]
        for r in readings) + "\n").encode("utf-8")


def read_json(path, maximum=CAP_INPUT):
    path = Path(path)
    require(path.is_file() and path.stat().st_size <= maximum, "input-file-size-or-existence-guard")
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), "UTF8-without-BOM-required")
    def unique_keys(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "duplicate-json-key")
            value[key] = item
        return value
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys), raw
    except (UnicodeError, ValueError):
        raise GuardError("invalid-UTF8-or-JSON") from None


def site_root():
    return common_path().resolve().parents[3]


def private_path(value, existing=True):
    path = Path(value).resolve()
    require(not any(part.casefold() == "public" for part in path.parts) and
            not path.is_relative_to(site_root()), "private-path-outside-entire-public-checkout-required")
    if existing:
        require(path.is_file() and path.stat().st_mode & 0o077 == 0, "private-input-file-permissions-required")
    else:
        require(not path.exists() and path.parent.is_dir(), "fresh-private-output-required")
    return path


def validate_test(test):
    require(EXPECTED_TEST is not None and isinstance(test, dict), "frozen-protocol-contract-unavailable")
    require(canonical(test) == canonical(EXPECTED_TEST), "protocol-normative-test-mismatch")


def registered_pins(protocol_path, registration):
    require(re.fullmatch(r"[0-9a-f]{40}", registration or "") is not None, "invalid-registration-commit")
    research = Path(__file__).resolve().parent.parent
    require((research / SELF_REL).resolve() == Path(__file__).resolve(), "installed-public-verifier-required")
    require(Path(protocol_path).resolve() == (research / PROTOCOL_REL).resolve(), "fixed-protocol-path-required")
    protocol, raw = read_json(protocol_path, CAP_PROTOCOL)
    require(protocol.get("version") == 1 and protocol.get("batchId") == BATCH_ID, "protocol-identity-mismatch")
    validate_test(protocol.get("test"))
    sources, scripts = protocol.get("sourceHashes"), protocol.get("scriptHashes")
    require(isinstance(sources, dict) and set(sources) == SOURCE_PATHS and isinstance(scripts, dict) and
            set(scripts) == SCRIPT_PATHS, "registered-pin-population-mismatch")
    require(sources[SOURCE_REL] == SOURCE_SHA and scripts[COMMON_REL] == COMMON_SHA and
            sources["scripts/batch20_support/english.txt"] == ENGLISH_SHA and
            sources["scripts/batch20_support/controls.json"] == CONTROLS_SHA, "fixed-input-pin-mismatch")
    pins = dict(sources)
    pins.update(scripts)
    pins[PROTOCOL_REL] = sha(raw)
    for relative, expected in pins.items():
        require(re.fullmatch(r"[a-f0-9]{64}", expected or "") is not None, "invalid-SHA256-pin")
        file = (research / relative).resolve()
        require(file.is_relative_to(research) and file.is_file() and file.stat().st_size <= CAP_REGISTERED_BLOB,
                "registered-local-file-guard")
        require(sha(file.read_bytes()) == expected, "registered-local-byte-mismatch")
        saved = subprocess.run(["git", "show", registration + ":public/research/" + relative],
                               cwd=research, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        require(saved.returncode == 0 and len(saved.stdout) <= CAP_REGISTERED_BLOB and sha(saved.stdout) == expected,
                "actual-registration-byte-mismatch")
    return protocol, sha(raw), research


def verify(args):
    output = private_path(args.out, False)
    result_path = private_path(args.result)
    readings_path = private_path(args.readings)
    forms_path = private_path(args.forms)
    validation_path = private_path(args.validation)
    protocol, protocol_sha, research = registered_pins(args.protocol, args.registration_commit)
    source_path = research / SOURCE_REL
    if args.source:
        require(Path(args.source).resolve() == source_path.resolve(), "fixed-source-path-required")
    model, source_bytes = read_json(source_path)
    require(sha(source_bytes) == SOURCE_SHA and model.get("schemaVersion") == 1 and
            model.get("modelId") == MODEL_ID, "fixed-source-model-mismatch")
    readings = derive_readings(model.get("rows"))
    forms = derive_forms(readings)
    evaluation = full_validation(readings, forms, load_common())
    expected_readings = {"schemaVersion": 1, "testId": TEST_ID, "sourceSha256": SOURCE_SHA, "readings": readings}
    actual_readings, readings_bytes = read_json(readings_path)
    actual_forms, forms_bytes = read_json(forms_path)
    actual_validation, validation_bytes = read_json(validation_path)
    require(actual_readings == expected_readings, "complete-reading-or-selected-ID-mismatch")
    require(all(a["text"].encode("utf-8") == b["text"].encode("utf-8")
                for a, b in zip(actual_readings["readings"], readings)), "complete-UTF8-reading-mismatch")
    require(actual_forms == {"schemaVersion": 1, "testId": TEST_ID, "forms": forms}, "complete-form-UTF8-mismatch")
    require(canonical(actual_validation) == canonical(evaluation), "complete-literal-validation-mismatch")
    text_path = private_path(readings_path.with_name("READINGS.private.txt"))
    require(text_path.stat().st_size <= CAP_INPUT, "private-text-artifact-cap")
    text_bytes = text_path.read_bytes()
    require(text_bytes == text_export(readings), "complete-reading-TXT-mismatch")
    result, result_bytes = read_json(result_path)
    expected_top = {"version", "testId", "batchId", "status", "startedAtUTC", "completedAtUTC",
                    "registrationCommit", "protocolSha256", "sourceHashes", "scriptHashes", "sourceModel",
                    "scopeComplete", "readingsGenerated", "literalFormatGatesComplete", "semanticReviewComplete",
                    "privateReviewRequired", "counts", "privateArtifactIntegrity", "activity", "limitations"}
    require(set(result) == expected_top and result.get("version") == 1 and result.get("testId") == TEST_ID and
            result.get("batchId") == BATCH_ID, "result-identity-or-allowlist-mismatch")
    require(result.get("registrationCommit") == args.registration_commit and result.get("protocolSha256") == protocol_sha
            and result.get("sourceHashes") == protocol["sourceHashes"] and
            result.get("scriptHashes") == protocol["scriptHashes"], "result-provenance-mismatch")
    require(result.get("sourceModel") == SOURCE_MODEL, "result-source-model-mismatch")
    require(result.get("status") == "registered-literal-scope-complete" and result.get("scopeComplete") is True and
            result.get("readingsGenerated") is True and result.get("literalFormatGatesComplete") is True and
            result.get("semanticReviewComplete") is False, "result-completion-mismatch")
    private_review = evaluation["common7"]["privateReviewRequired"] or evaluation["minikey"]["privateReviewRequired"]
    require(result.get("privateReviewRequired") is private_review, "result-lead-flag-mismatch")
    require(canonical(result.get("counts")) == canonical(technical_counts(readings, forms, evaluation)), "result-aggregate-count-mismatch")
    artifact_pins = {"READINGS.private.json": sha(readings_bytes), "READINGS.private.txt": sha(text_bytes),
                     "FORMS.private.json": sha(forms_bytes), "VALIDATION.private.json": sha(validation_bytes)}
    require(result.get("privateArtifactIntegrity") == artifact_pins, "result-private-artifact-integrity-mismatch")
    require(result.get("limitations") == protocol["test"]["limitations"], "result-limitations-mismatch")
    check_activity(result.get("activity"), evaluation)
    try:
        begin = datetime.fromisoformat(result["startedAtUTC"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(result["completedAtUTC"].replace("Z", "+00:00"))
        require(begin.tzinfo is not None and end.tzinfo is not None and begin <= end, "result-time-order-mismatch")
    except (ValueError, TypeError, KeyError):
        raise GuardError("result-time-format-mismatch") from None
    receipt = {"version": 1, "testId": TEST_ID, "status": "PASS", "passed": True,
               "completedAtUTC": now(), "registrationCommit": args.registration_commit,
               "protocolSha256": protocol_sha, "sourceSha256": SOURCE_SHA,
               "primaryResultSha256": sha(result_bytes), "privateArtifactIntegrity": artifact_pins,
               "comparisons": {"fullReadingsUTF8": 3, "fullSelectedRowIDSetsAndOrder": 3,
                               "fullExactAndCompactedForms": len(forms), "fullPrivateValidation": True,
                               "allSafeAggregateCounts": True, "independentMinikeyLengths": list(LENGTHS)},
               "scope": "Independent reconstruction and minikey enumeration; seven validators deliberately share pinned code.",
               "semanticReviewPerformed": False, "scalarDerivations": 0, "addressDerivations": 0,
               "networkQueries": 0, "publicEdits": 0}
    output.mkdir(mode=0o700)
    write_private(output / "VERIFICATION.json", receipt)
    return receipt


def check_activity(activity, evaluation):
    require(canonical(activity) == canonical(EXPECTED_ACTIVITY), "result-activity-schema-or-action-mismatch")


def write_private(path, value):
    data = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    require(len(data) <= CAP_INPUT, "private-output-byte-cap")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)


def self_test():
    def fixture(texts):
        return [{"id": "synthetic-" + str(i), "ordinal": i, "printedPage": 73 if i < 3 else 75,
                 "role": "synthetic", "printedText": text} for i, text in enumerate(texts, 1)]
    rows = fixture(["First, alpha", "“Second” beta", "... gamma", "MiXeD-case delta", "Élan epsilon"])
    readings = derive_readings(rows, False)
    require([r["text"] for r in readings] == ["First, “Second” ... MiXeD-case Élan",
            "First, alpha\n... gamma\nÉlan epsilon", "“Second” beta\nMiXeD-case delta"],
            "synthetic-literal-reading-control")
    require([r["selectedRowIds"] for r in readings] == [["synthetic-1", "synthetic-2", "synthetic-3", "synthetic-4", "synthetic-5"],
            ["synthetic-1", "synthetic-3", "synthetic-5"], ["synthetic-2", "synthetic-4"]], "synthetic-selected-ID-control")
    for text, expected in [("... rest", "..."), ("Élan next", "Élan"), ("a  b", "a"),
                           ("A\tB", "A"), ("A\u00a0B", "A"), ("Solo", "Solo")]:
        require(first_chunk(text) == expected, "synthetic-first-whitespace-chunk-control")
    forms = derive_forms(readings)
    require("First,“Second”...MiXeD-caseÉlan" in forms, "synthetic-whitespace-only-compaction-control")
    require(sha("é".encode("utf-8")) != sha(b"e"), "synthetic-UTF8-integrity-control")
    full_rows = [{"id": identifier, "ordinal": i, "printedPage": page, "role": role,
                  "printedText": "Synthetic" + str(i) + " remainder"}
                 for i, (identifier, page, role) in enumerate(expected_identity(), 1)]
    full = derive_readings(full_rows)
    full_expected = [" ".join("Synthetic" + str(i) for i in range(1, 152)),
                     "\n".join("Synthetic" + str(i) + " remainder" for i in range(1, 152, 2)),
                     "\n".join("Synthetic" + str(i) + " remainder" for i in range(2, 152, 2))]
    require([r["text"] for r in full] == full_expected and
            [r["selectedRowCount"] for r in full] == SELECTED_COUNTS and
            full[1]["selectedRowIds"][1] == "p75_title_0", "synthetic-151-complete-text-global-order-control")
    rejected = 0
    for bad in ["", " leading", "trailing ", "A\tB", "A\nB", "A\u00a0B", "A\u200bB", "A\x00B"]:
        try:
            derive_readings(fixture([bad]), False)
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-invalid-source-row-accepted")
    for mode in ["id", "ordinal", "page", "role", "count"]:
        changed = json.loads(json.dumps(full_rows))
        if mode == "id": changed[1]["id"] = changed[0]["id"]
        elif mode == "ordinal": changed[1]["ordinal"] = True
        elif mode == "page": changed[2]["printedPage"] = 73
        elif mode == "role": changed[0]["role"] = "body"
        else: changed.pop()
        try:
            derive_readings(changed)
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-invalid-source-population-accepted")
    validate_test(EXPECTED_TEST)
    for key in ["id", "inputPaths", "implementationPaths", "sourceModel", "readings", "forms",
                "literalValidation", "registrationGate", "caps", "outputPolicy", "activityBoundary"]:
        bad = json.loads(json.dumps(EXPECTED_TEST))
        bad[key] = None
        try:
            validate_test(bad)
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-protocol-mutation-accepted")
    check_activity(EXPECTED_ACTIVITY, None)
    for bad in [{}, {**EXPECTED_ACTIVITY, "extra": 0}, {**EXPECTED_ACTIVITY, "networkQueries": 1},
                {**EXPECTED_ACTIVITY, "networkQueries": False}]:
        try:
            check_activity(bad, None)
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-activity-mutation-accepted")
    for bad_path in [site_root() / "dist/synthetic-private-output", Path("/tmp/public/synthetic-private-output")]:
        try:
            private_path(bad_path, False)
        except GuardError:
            rejected += 1
        else:
            raise GuardError("synthetic-public-output-path-accepted")
    common = load_common()
    require("minikey" not in COMMON7 and len(COMMON7) == 7, "synthetic-old-minikey-exclusion")
    controls = json.loads((common_path().parent / "batch20_support/controls.json").read_text())
    payload = b"\x80" + b"\x00" * 31 + b"\x01" + b"\x01"
    control_wif = common.b58encode(payload + common.sha256(common.sha256(payload))[:4])
    control_texts = [control_wif, "01" * 32, controls["bip39_valid"], controls["bip32_extended_private"],
                     controls["bip38_encrypted_private"], controls["legacy_address"],
                     controls["sec_compressed_generator"]]
    shared = common.scan_streams([{"id": "control", "text": "\n".join(control_texts)}], COMMON7)
    require(all(shared["validCounts"][kind] >= 1 for kind in COMMON7), "synthetic-seven-format-positive-controls")
    synthetic_minis = []
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    for length in LENGTHS:
        found = None
        for number in range(65536):
            n, suffix = number, ""
            for _ in range(8):
                n, digit = divmod(n, 58)
                suffix = alphabet[digit] + suffix
            candidate = "S" + "2" * (length - 9) + suffix
            if hashlib.sha256((candidate + "?").encode("ascii")).digest()[0] == 0:
                found = candidate
                break
        require(found is not None, "synthetic-minikey-positive-not-found-within-bound")
        synthetic_minis.append(found)
    mini, shapes, valid = mini_evaluate(["|".join(synthetic_minis)])
    require(all(mini["validCounts"][str(n)] >= 1 for n in LENGTHS), "synthetic-three-length-embedded-control")
    require(all(r["value"] in synthetic_minis or r["length"] < 30 for r in valid), "synthetic-mini-value-control")
    require(mini["checksumCalls"] == sum(mini["uniqueShapeCounts"].values()), "synthetic-minikey-unique-call-control")
    for good in synthetic_minis:
        bad = next(good[:-1] + char for char in alphabet
                   if hashlib.sha256((good[:-1] + char + "?").encode("ascii")).digest()[0] != 0)
        _, _, rejected_values = mini_evaluate([bad])
        require(not any(record["value"] == bad for record in rejected_values),
                "synthetic-invalid-question-mark-checksum-control")
    # A longer Base58 run must still allow every embedded22/26/30window; invalid
    # characters are barriers and never erased by the direct scanner.
    run = "S" * 33
    overlapping, _, _ = mini_evaluate([run])
    require(overlapping["shapeCounts"] == {"22": 12, "26": 8, "30": 4}, "synthetic-overlapping-mini-control")
    broken, _, _ = mini_evaluate([synthetic_minis[1][:13] + "0" + synthetic_minis[1][13:]])
    require(broken["shapeCounts"]["26"] == 0, "synthetic-invalid-character-barrier-control")
    separated = synthetic_minis[1][:13] + " " + synthetic_minis[1][13:]
    separated_result, _, _ = mini_evaluate([separated])
    joined_result, _, _ = mini_evaluate(["".join(c for c in separated if not c.isspace())])
    require(separated_result["shapeCounts"]["26"] == 0 and joined_result["validCounts"]["26"] == 1,
            "synthetic-exact-versus-compacted-form-control")
    dedup, _, _ = mini_evaluate([synthetic_minis[1], synthetic_minis[1]])
    require(dedup["shapeCounts"]["26"] == 2 and dedup["uniqueShapeCounts"]["26"] == 1,
            "synthetic-occurrence-versus-unique-control")
    # All target source, raw-text, private scalar and wallet inputs remain unopened.
    return {"version": 1, "status": "PASS", "sourceFreeCompleteReadings": 6,
            "rejectionControls": rejected, "sharedFormatPositiveControls": 7,
            "independentMinikeyLengths": list(LENGTHS), "targetSourceReads": 0,
            "targetReadingsGenerated": 0, "scalarDerivations": 0, "addressDerivations": 0,
            "networkQueries": 0, "primaryRunnerImports": 0}


def main():
    seen = set()
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            key = arg.split("=", 1)[0]
            require(key not in seen, "duplicate-command-argument")
            seen.add(key)
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--definition", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--verify", action="store_true")
    for name in ["protocol", "registration-commit", "result", "readings", "forms", "validation", "source", "out"]:
        parser.add_argument("--" + name)
    args = parser.parse_args()
    if args.definition:
        answer = {"testId": TEST_ID, "sourcePath": SOURCE_REL, "sourceSha256": SOURCE_SHA,
                  "sourcePaths": sorted(SOURCE_PATHS), "scriptPaths": sorted(SCRIPT_PATHS),
                  "protocolPath": PROTOCOL_REL, "sharedSevenFormatConsistency": COMMON7,
                  "independentMinikeyLengths": list(LENGTHS), "primaryImports": 0}
    elif args.self_test:
        answer = self_test()
    else:
        require(all(getattr(args, name) for name in ["protocol", "registration_commit", "result", "readings", "forms", "validation", "out"]),
                "verify-required-arguments-missing")
        answer = verify(args)
    print(json.dumps(answer, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except GuardError as error:
        print(json.dumps({"status": "FAIL-INCONCLUSIVE", "errorCode": str(error)}))
        raise SystemExit(2)
    except Exception:
        print(json.dumps({"status": "FAIL-INCONCLUSIVE", "errorCode": "unexpected-verification-failure"}))
        raise SystemExit(2)
