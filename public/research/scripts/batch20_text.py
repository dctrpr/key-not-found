#!/usr/bin/env python3
"""T01–T10: fixed text and serialized-record tests; no default target work."""
from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from batch20_common import scan_streams, self_test as common_self_test, DEFAULT_FORMATS

ROOT = Path(__file__).resolve().parents[1]
PRINTED = "sources/printed-lines.json"
FROZEN = "analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json"
FROZEN_SHA = "1651a33dab46babf36f56439ddb409058cfa36712d96ead7d4200962b80817b9"
WORDLIST = "scripts/batch20_support/english.txt"
CONTROLS = "scripts/batch20_support/controls.json"
SCRIPTS = ("scripts/batch20_common.py", "scripts/batch20_text.py")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def definition(number, title, family, priority, parameters, controls, limitations):
    test_id = f"T{number:02d}"
    return {"id": test_id, "methodId": "batch20-" + test_id.lower(), "title": title,
            "family": family, "branchId": "sources" if number >= 7 else "text-lines",
            "priority": priority, "parameters": parameters,
            "inputPaths": [FROZEN if number >= 7 else PRINTED, WORDLIST, CONTROLS],
            "controls": controls,
            "negativeCriterion": "No valid declared literal record excludes only this exact extraction, source population and record-format scope; it does not exclude another cipher, format or selector.",
            "limitations": limitations}


BASE = {"formats": list(DEFAULT_FORMATS), "forms": ["exact", "whitespace-only-compacted"],
        "raw32AsciiScalars": False, "hashWrappers": False,
        "bip39Tokenization": "lowercase unfiltered lexical tokens; ordinary punctuation boundaries; invalid-group ␞ is a hard region boundary",
        "hexMatching": "64hex scalar and SEC records require non-hex boundaries"}
UNITS = ["whole-body", "each-page"]
TEST_DEFINITIONS = [
    definition(1, "Alternating direction on the actual printed lines", "faithful-boustrophedon", "high",
               {**BASE, "units": UNITS, "rowOrder": ["forward", "reverse"],
                "reversedRowParity": [0, 1], "bodyParityReset": ["global", "page"],
                "projections": ["full_text", "first_words", "last_words", "first_initials", "first_finals", "last_initials", "last_finals"]},
               ["synthetic alternating-row inversion", "both parities and page-reset distinction"],
               ["The older boustrophedon test used merged transcript lines; this is a corrected-source test.", "Direction and parity variants are one procedure, not independent theories."]),
    definition(2, "Fixed interior columns of printed words and characters", "interior-column-null-cipher", "medium",
               {**BASE, "units": UNITS, "rowOrder": ["forward", "reverse"],
                "sides": ["left", "right"], "wordColumns": "k=2..min(20,shortest-row-token-count)",
                "characterColumns": "k=2..min(80,shortest-exact-row-codepoint-count)",
                "wordProjections": ["words", "initials", "finals"], "shortRowPolicy": "common rectangle only; never pad or omit rows"},
               ["synthetic column2 fixture", "left-right and row-order reversal"],
               ["Interior columns extend the first-word clue but are not creator instructions.", "Character columns are logical indices, not measured scan x coordinates."]),
    definition(3, "Mirror-axis centers of printed lines", "line-mesostics", "exploratory",
               {**BASE, "units": UNITS, "rowOrder": ["forward", "reverse"],
                "centers": ["floor((n-1)/2)", "floor(n/2)"],
                "surfaces": ["exact-codepoints", "ASCII-letters", "lexical-words"],
                "wordProjections": ["words", "initials", "finals"], "offsetFitting": False},
               ["synthetic odd/even center positions", "exact whitespace remains a source character"],
               ["The center selector is an exploratory mirror hypothesis.", "Logical centers are not physical page-fold intersections."]),
    definition(4, "Paragraph-boundary readings", "paragraph-edge-null-cipher", "medium",
               {**BASE, "units": UNITS, "groupBy": ["page", "paragraph"],
                "mergeAcrossPage": False, "phases": ["all", "odd", "even"],
                "groupOrder": ["forward", "reverse"], "projections": ["first_words", "last_words", "first_initials", "first_finals", "last_initials", "last_finals", "boundary_initial_pairs"]},
               ["synthetic reflow-invariance", "no merge across a page boundary"],
               ["Paragraph IDs were visually reconstructed, not supplied by an authoritative manuscript.", "The previous paragraph reset selected alternating lines rather than one word per paragraph."]),
    definition(5, "Sentence-boundary readings from the faithful body", "sentence-edge-null-cipher", "medium",
               {**BASE, "units": ["whole-body"], "splitter": "published canonical splitter: protect U.K.; punctuation then whitespace and capital/digit", "phases": ["all", "odd", "even"], "groupOrder": ["forward", "reverse"], "projections": ["first_words", "last_words", "first_initials", "first_finals", "last_initials", "last_finals", "boundary_initial_pairs"]},
               ["U.K. and quoted-ending segmentation fixture", "line-reflow invariance"],
               ["Sentence segmentation is a declared inference; alternate segmentation is outside this test.", "Older sentence audits only checked local instruction terms and did not validate full-body literal records."]),
    definition(6, "Visible capitalization as a data carrier", "capitalization-carrier", "exploratory",
               {**BASE, "units": UNITS, "literalCarriers": ["uppercase-ASCII-letters", "uppercase-whole-tokens-at-least2letters"], "bitCarrier": "case of first alphabetic character in the first lexical word of each printed row", "nonAlphabeticFirstWord": "barrier at original bit position; never drop", "bitPolarity": ["upper=1", "upper=0"], "bitOrder": ["forward", "reverse"], "groupPhase": 0, "decoders": ["modern26-letter-Bacon5", "ASCII8"], "incompleteGroup": "record count; no padding", "invalidGroup": "non-whitespace barrier"},
               ["synthetic ASCII and Bacon case carriers", "invalid groups and unpadded trailing bits"],
               ["Grammar, ordinary capitalization and the all-caps paragraph are strong null explanations.", "This uses visible case, not unreliable DOCM bold labels.", "A positive requires source-crop verification of the precise case choices."]),
    definition(7, "Serialized extended private-key records", "extended-private-record-coverage", "high",
               {"formats": ["extended_private"], "sourcePopulation": "frozen-clean42forms", "recordLength": 111, "mainnetVersions": ["0488ade4", "049d7878", "04b2430c", "0295b005", "02aa7a99"], "validate": ["canonicalBase58", "Base58Check", "78byte-payload", "private-marker00", "scalar-range", "root-parent-child-zero-consistency"], "deriveChildKeys": False},
               ["official BIP32 vector", "all5SLIP132 version round-trips", "illegal root-parent/marker/scalar/checksum"],
               ["No extended-private format is specified by the creator.", "A valid record is a private-review lead, not proof of the prize; no child path is guessed."]),
    definition(8, "BIP38 encrypted private-key records", "encrypted-private-record-coverage", "high",
               {"formats": ["bip38"], "sourcePopulation": "frozen-clean42forms", "recordLength": 58, "prefix": "6P", "payloadPrefixes": ["0142", "0143"], "flags0142": ["c0", "e0"], "flags0143": ["00", "04", "20", "24"], "payloadBytes": 39, "passphraseGuesses": False, "decrypt": False},
               ["official BIP38 vector", "all registered structural flag combinations", "reserved flags and checksum negatives"],
               ["A structural encrypted record would require a separate passphrase/source lead.", "No password guessing, decryption or spendable-secret claim is part of this test."]),
    definition(9, "Literal candidate funding addresses", "public-address-discovery", "high",
               {"formats": ["address"], "sourcePopulation": "frozen-clean42forms", "legacyVersions": ["00", "05"], "legacyLengths": [26, 35], "witness": {"0": [20, 32], "1": [32]}, "hrp": "bc", "uniformUppercaseAllowed": True, "mixedCaseAllowed": False, "maxBech32Length": 90, "addressQueries": False},
               ["Base58Check address", "official Bech32/Bech32m vectors", "mixed case/padding/cross-checksum-version negatives"],
               ["A valid or active address is not authenticated as Max Keiser's.", "This is record discovery only; no network activity checks or private-key derivation occur."]),
    definition(10, "Literal SEC public keys and curve membership", "public-point-discovery", "high",
               {"formats": ["sec_public"], "sourcePopulation": "frozen-clean42forms", "compressedPrefixes": ["02", "03"], "compressedHexLength": 66, "uncompressedPrefix": "04", "uncompressedHexLength": 130, "curve": "secp256k1", "onCurveRequired": True, "repairHex": False, "deriveAddresses": False},
               ["published generator in compressed/uncompressed form", "x>=p and off-curve negatives"],
               ["Curve membership has no embedded checksum and does not prove intentional encoding or ownership.", "No private-key inversion, address derivation, network request or transaction occurs."]),
]
DEFINITIONS = {d["id"]: d for d in TEST_DEFINITIONS}


def tokens(text: str) -> list[str]:
    # Same boundary rule as the frozen printed-line probe.
    values = [re.sub(r"^[^A-Za-z0-9$]+|[^A-Za-z0-9]+$", "", w) for w in re.split(r"\s+", text)]
    return [w for w in values if re.search(r"[A-Za-z0-9]", w)]


def units(rows: list[dict]) -> list[tuple[str, list[dict]]]:
    pages = list(dict.fromkeys(r["page"] for r in rows))
    return [("body", rows)] + [(f"p{page}", [r for r in rows if r["page"] == page]) for page in pages]


def projections(texts: list[str], include_full=False) -> dict[str, str]:
    split = [tokens(text) for text in texts]
    if any(not words for words in split):
        raise ValueError("Empty lexical row in declared unit")
    first, last = [w[0] for w in split], [w[-1] for w in split]
    result = {"first_words": " ".join(first), "last_words": " ".join(last),
              "first_initials": "".join(w[0] for w in first), "first_finals": "".join(w[-1] for w in first),
              "last_initials": "".join(w[0] for w in last), "last_finals": "".join(w[-1] for w in last)}
    if include_full:
        return {"full_text": "\n".join(texts), **result}
    result["boundary_initial_pairs"] = "".join(a[0] + b[0] for a, b in zip(first, last))
    return result


def add_stream(out: list, stream_id: str, text: str, **metadata):
    out.append({"id": stream_id, "text": text, **metadata})


def boustrophedon(rows, direction, reset, parity):
    ordered = rows if direction == "forward" else list(reversed(rows))
    counters, texts = {}, []
    for row in ordered:
        key = "all" if reset == "global" else row["page"]
        index = counters.get(key, 0)
        counters[key] = index + 1
        texts.append(row["text"][::-1] if index % 2 == parity else row["text"])
    return texts


def sentence_units(text: str) -> list[str]:
    # Unchanged published canonical splitter; no target-driven corrections.
    protected = {"U.K.": "UKDOT"}
    for old, new in protected.items():
        text = text.replace(old, new)
    marked = re.sub(r"([.!?][\"”')\]]?)\s+(?=[\"(]?[A-Z0-9])", r"\1<SPLIT>", text)
    result = []
    for part in marked.split("<SPLIT>"):
        part = part.strip()
        if part:
            for old, new in protected.items():
                part = part.replace(new, old)
            result.append(part)
    return result


def grouped_edges(out, prefix, groups):
    for phase in ("all", "odd", "even"):
        selected = groups if phase == "all" else groups[0 if phase == "odd" else 1::2]
        if not selected:
            continue
        for order in ("forward", "reverse"):
            values = selected if order == "forward" else list(reversed(selected))
            for name, text in projections(values).items():
                add_stream(out, f"{prefix}/{phase}/{order}/{name}", text)


def decode_case_bits(bits: list[int | None], width: int) -> tuple[str, dict]:
    result, invalid = [], 0
    for offset in range(0, len(bits) - width + 1, width):
        group = bits[offset:offset + width]
        if None in group:
            result.append("␞")
            invalid += 1
            continue
        value = int("".join(map(str, group)), 2)
        if width == 5 and value < 26:
            result.append(chr(65 + value))
        elif width == 8 and value < 128:
            result.append(chr(value))
        else:
            result.append("␞")
            invalid += 1
    return "".join(result), {"invalidGroups": invalid, "unconsumedTrailingBits": len(bits) % width}


def frozen_clean_forms(data: dict) -> list[dict]:
    selected = {}
    for candidate in data["candidates"]:
        eligible = [v for v in candidate["variants"] if v["frame"] == "body" and v["subset"] == "all" and v["parityBase"] == "all_printed_rows" and v["reset"] in ("global", "page") and ((v["projection"] == "complete_lines" and v["phase"] in ("odd", "even")) or (v["projection"] in ("first_words", "first_word_initials") and v["phase"] == "all"))]
        if eligible:
            if hashlib.sha256(candidate["text"].encode()).hexdigest() != candidate["sha256"]:
                raise ValueError("Frozen stream hash mismatch")
            selected[candidate["text"]] = candidate["sha256"]
    if len(selected) != 22:
        raise ValueError("Frozen population is not22streams")
    forms = {}
    for text, source in selected.items():
        for mode, value in (("exact", text), ("compact", re.sub(r"\s", "", text))):
            forms.setdefault(value, []).append({"sourceSha256": source, "form": mode})
    if len(forms) != 42:
        raise ValueError("Frozen population is not42forms")
    positions = {size: sum(max(0, len(text) - size + 1) for text in forms) for size in (22, 30)}
    if positions != {22: 113830, 30: 113494}:
        raise ValueError("Frozen form-position counts changed")
    return [{"id": "frozen-" + hashlib.sha256(text.encode()).hexdigest(), "text": text, "sources": sources}
            for text, sources in sorted(forms.items())]


def generate_streams(test_id: str, data: dict) -> list[dict]:
    if test_id not in DEFINITIONS:
        raise ValueError("Unknown text test")
    if int(test_id[1:]) >= 7:
        return frozen_clean_forms(data)
    rows = [r for r in data["rows"] if r["section"] == "body"]
    out = []
    if test_id == "T01":
        for unit, selected in units(rows):
            for direction in ("forward", "reverse"):
                for reset in (("global", "page") if unit == "body" else ("page",)):
                    for parity in (0, 1):
                        texts = boustrophedon(selected, direction, reset, parity)
                        for projection, text in projections(texts, True).items():
                            add_stream(out, f"{unit}/{direction}/{reset}/{parity}/{projection}", text)
    elif test_id == "T02":
        for unit, selected in units(rows):
            word_rows = [tokens(r["text"]) for r in selected]
            for surface, matrix, cap in (("word", word_rows, 20), ("character", [list(r["text"]) for r in selected], 80)):
                common = min(cap, min(map(len, matrix)))
                for column in range(2, common + 1):
                    for side in ("left", "right"):
                        values = [row[column - 1 if side == "left" else -column] for row in matrix]
                        for order in ("forward", "reverse"):
                            ordered = values if order == "forward" else list(reversed(values))
                            outputs = {"characters": "".join(ordered)} if surface == "character" else {"words": " ".join(ordered), "initials": "".join(w[0] for w in ordered), "finals": "".join(w[-1] for w in ordered)}
                            for projection, text in outputs.items():
                                add_stream(out, f"{unit}/{surface}/{column}/{side}/{order}/{projection}", text)
    elif test_id == "T03":
        for unit, selected in units(rows):
            matrices = {"exact-codepoints": [list(r["text"]) for r in selected], "ASCII-letters": [re.findall(r"[A-Za-z]", r["text"]) for r in selected], "lexical-words": [tokens(r["text"]) for r in selected]}
            for surface, matrix in matrices.items():
                if any(not row for row in matrix):
                    raise ValueError("Empty center carrier")
                for center in ("left-middle", "right-middle"):
                    values = [row[(len(row) - 1) // 2 if center == "left-middle" else len(row) // 2] for row in matrix]
                    for order in ("forward", "reverse"):
                        ordered = values if order == "forward" else list(reversed(values))
                        outputs = {"characters": "".join(ordered)} if surface != "lexical-words" else {"words": " ".join(ordered), "initials": "".join(w[0] for w in ordered), "finals": "".join(w[-1] for w in ordered)}
                        for projection, text in outputs.items():
                            add_stream(out, f"{unit}/{surface}/{center}/{order}/{projection}", text)
    elif test_id == "T04":
        for unit, selected in units(rows):
            grouped = OrderedDict()
            for row in selected:
                grouped.setdefault((row["page"], row["paragraph"]), []).append(row["text"])
            grouped_edges(out, unit, [" ".join(parts) for parts in grouped.values()])
    elif test_id == "T05":
        grouped_edges(out, "body", sentence_units(" ".join(r["text"] for r in rows)))
    elif test_id == "T06":
        for unit, selected in units(rows):
            text = "\n".join(r["text"] for r in selected)
            add_stream(out, f"{unit}/uppercase-letters", "".join(re.findall(r"[A-Z]", text)))
            upper_tokens = [w for w in tokens(text) if len(re.findall(r"[A-Za-z]", w)) >= 2 and w.upper() == w]
            add_stream(out, f"{unit}/uppercase-whole-tokens", " ".join(upper_tokens))
            bits = []
            for row in selected:
                first = tokens(row["text"])[0]
                alpha = re.search(r"[A-Za-z]", first)
                bits.append(None if alpha is None else int(alpha.group().isupper()))
            for polarity in ("upper=1", "upper=0"):
                polarity_bits = bits if polarity == "upper=1" else [None if b is None else 1 - b for b in bits]
                for order in ("forward", "reverse"):
                    ordered = polarity_bits if order == "forward" else list(reversed(polarity_bits))
                    for width in (5, 8):
                        decoded, meta = decode_case_bits(ordered, width)
                        add_stream(out, f"{unit}/{polarity}/{order}/width{width}", decoded, **meta, carrierGaps=sum(b is None for b in bits))
    return out


def self_test() -> dict:
    common = common_self_test()
    fixture = [{"page": 75, "paragraph": 0, "section": "body", "text": "Aa TARGET Cc"},
               {"page": 75, "paragraph": 0, "section": "body", "text": "Dd SECOND Ff"},
               {"page": 76, "paragraph": 0, "section": "body", "text": "Gg THIRD Ii"}]
    assert boustrophedon(fixture, "forward", "global", 1) == [fixture[0]["text"], fixture[1]["text"][::-1], fixture[2]["text"]]
    assert boustrophedon(fixture, "forward", "page", 0)[2] == fixture[2]["text"][::-1]
    assert boustrophedon(fixture, "reverse", "page", 0)[0] == fixture[2]["text"][::-1]
    columns = generate_streams("T02", {"rows": fixture})
    assert any(s["id"] == "body/word/2/left/forward/words" and s["text"] == "TARGET SECOND THIRD" for s in columns)
    centers = generate_streams("T03", {"rows": fixture})
    assert any(s["id"] == "body/lexical-words/left-middle/forward/words" and s["text"] == "TARGET SECOND THIRD" for s in centers)
    reflow = [dict(fixture[0], text="Aa TARGET"), dict(fixture[1], text="Cc Dd SECOND Ff"), fixture[2]]
    para_a = {s["id"]: s["text"] for s in generate_streams("T04", {"rows": fixture})}
    para_b = {s["id"]: s["text"] for s in generate_streams("T04", {"rows": reflow})}
    assert para_a == para_b
    assert sentence_units('U.K. rules. "Next?" Yes.') == ['U.K. rules.', '"Next?"', 'Yes.']
    assert decode_case_bits([0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 5)[0] == "AB"
    assert decode_case_bits([0, 1, 0, 0, 0, 0, 0, 1], 8)[0] == "A"
    assert decode_case_bits([1] * 5 + [0], 5) == ("␞", {"invalidGroups": 1, "unconsumedTrailingBits": 1})
    assert decode_case_bits([None] + [0] * 7, 8)[0] == "␞"
    for test_id in ("T01", "T02", "T03", "T04", "T05", "T06"):
        generated = generate_streams(test_id, {"rows": fixture})
        assert generated and len({s["id"] for s in generated}) == len(generated)
    return {"passed": True, "common": common, "textControls": ["boustrophedon-parity-order-page-reset", "fixed-interior-column", "odd-even-middle", "paragraph-reflow", "U.K.-quoted-sentence-splitter", "Bacon-ASCII-case-decoding", "barriers-and-unpadded-tail", "unique-stream-ids"], "targetInputRead": False, "targetChecks": 0, "networkQueries": 0}


def validate_protocol(protocol, test_id):
    if protocol.get("batchId") != "keiser-20261110-batch20" or protocol.get("version") != 1:
        raise ValueError("Unexpected batch protocol")
    entries = [t for t in protocol.get("tests", []) if t.get("id") == test_id]
    if len(entries) != 1 or entries[0].get("parameters") != DEFINITIONS[test_id]["parameters"]:
        raise ValueError("Registered test parameters do not match implementation")
    checked = {}
    pins = protocol.get("sourceHashes", {})
    for relative in DEFINITIONS[test_id]["inputPaths"]:
        if relative not in pins:
            raise ValueError("Missing required source pin: " + relative)
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != pins[relative]:
            raise ValueError("Source hash mismatch: " + relative)
        checked[relative] = actual
    if test_id in ("T07", "T08", "T09", "T10") and checked[FROZEN] != FROZEN_SHA:
        raise ValueError("Frozen original-reading hash changed")
    script_checked = {}
    for relative in SCRIPTS:
        if relative not in protocol.get("scriptHashes", {}):
            raise ValueError("Missing implementation pin: " + relative)
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != protocol["scriptHashes"][relative]:
            raise ValueError("Implementation hash mismatch: " + relative)
        script_checked[relative] = actual
    return checked, script_checked


def run_test(test_id, protocol_path, registration_commit, output_dir):
    started = utc_now()
    if not re.fullmatch(r"[a-f0-9]{40}", registration_commit):
        raise ValueError("Registration commit must be forty lowercase hexadecimal characters")
    destination = Path(output_dir).resolve()
    if destination.exists():
        raise ValueError("Refusing to overwrite an existing result directory")
    protocol_bytes = Path(protocol_path).read_bytes()
    protocol = json.loads(protocol_bytes)
    source_hashes, script_hashes = validate_protocol(protocol, test_id)
    controls = self_test()
    source = FROZEN if int(test_id[1:]) >= 7 else PRINTED
    data = json.loads((ROOT / source).read_text())
    if source == PRINTED:
        counts = {str(p): sum(r["section"] == "body" and r["page"] == p for r in data["rows"]) for p in range(75, 80)}
        if counts != {"75": 32, "76": 31, "77": 32, "78": 22, "79": 25}:
            raise ValueError("Faithful printed-row counts changed")
    streams = generate_streams(test_id, data)
    evaluation = scan_streams(streams, DEFINITIONS[test_id]["parameters"]["formats"])
    completed = utc_now()
    result = {"schemaVersion": 1, "batchId": protocol["batchId"], "testId": test_id,
              "methodId": DEFINITIONS[test_id]["methodId"], "title": DEFINITIONS[test_id]["title"],
              "family": DEFINITIONS[test_id]["family"], "startedAtUTC": started, "completedAtUTC": completed,
              "registrationCommit": registration_commit, "protocolSha256": hashlib.sha256(protocol_bytes).hexdigest(),
              "sourceHashes": source_hashes, "scriptHashes": script_hashes,
              "parameters": DEFINITIONS[test_id]["parameters"], "controls": controls,
              "evaluation": evaluation, "outcome": "record-lead-private-review-required" if evaluation["privateReviewRequired"] else "no-valid-declared-literal-record",
              "negativeCriterion": DEFINITIONS[test_id]["negativeCriterion"],
              "limitations": DEFINITIONS[test_id]["limitations"],
              "privateReviewRequired": evaluation["privateReviewRequired"], "networkQueries": 0,
              "rawStreamFile": "streams.private.json; never publish without separate review"}
    destination.mkdir(parents=True, mode=0o700)
    (destination / "streams.private.json").write_text(json.dumps({"testId": test_id, "streams": streams}, indent=2) + "\n")
    (destination / "streams.private.json").chmod(0o600)
    (destination / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    (destination / "RESULT.json").chmod(0o600)
    print(json.dumps({"testId": test_id, "completedAtUTC": completed, "streamCount": evaluation["streamCount"], "uniqueStreamCount": evaluation["uniqueStreamCount"], "shapeCounts": evaluation["shapeCounts"], "validCounts": evaluation["validCounts"], "outcome": result["outcome"], "privateReviewRequired": evaluation["privateReviewRequired"], "networkQueries": 0}, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--self-test", action="store_true")
    action.add_argument("--list", action="store_true")
    action.add_argument("--run", choices=sorted(DEFINITIONS))
    parser.add_argument("--protocol")
    parser.add_argument("--registration-commit")
    parser.add_argument("--out")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))
    elif args.list:
        print(json.dumps(TEST_DEFINITIONS, indent=2))
    elif args.run:
        if not args.protocol or not args.registration_commit or not args.out:
            parser.error("--run requires --protocol, --registration-commit and explicit --out NEW_DIR")
        run_test(args.run, args.protocol, args.registration_commit, args.out)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, AssertionError, KeyError, OSError) as error:
        message = str(error).replace(str(ROOT), "<research>")
        message = re.sub(r"(?:/" + "Users/|/" + r"home/)[^\s\"'<>]+", "<personal-path>", message)
        print(json.dumps({"error": message[:600], "result": "inconclusive", "networkQueries": 0}))
        raise SystemExit(1)
