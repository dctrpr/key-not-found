#!/usr/bin/env python3
"""Check saved G02 shape flags by scanning the complete paired-mask product."""

import argparse
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import prod
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

GRAMMAR = {"wif": ("5KL", (51, 52)), "minikey": ("S", (22, 26, 30))}
BASE58_CLASS = r"[1-9A-HJ-NP-Za-km-z]"
PATTERNS = {
    name: {
        str(length): re.compile(f"[{markers}]" + BASE58_CLASS + "{" + str(length - 1) + "}")
        for length in lengths
    }
    for name, (markers, lengths) in GRAMMAR.items()
}
MAX_PRODUCTS = 50_000
MAX_CHARACTERS = 30_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bind_lexical_tokens(pinned, grouped):
    rows = {row["id"]: row for row in json.loads(pinned["sources/printed-lines.json"])["rows"]}
    maps = {row["id"]: row for row in json.loads(pinned["sources/word-geometry-20261110.json"])["rows"]}
    require(len(rows) == len(maps) == 142 and set(rows) == set(maps), "Source row population differs")
    tokens = {}
    for records in grouped.values():
        for record in records:
            row_id = record["rowId"]
            row, mapping = rows[row_id], maps[row_id]
            require(row["page"] == mapping["page"] == record["target"]
                    and mapping["lexicallyComplete"] is True, "Incomplete lexical row")
            canonical = [token for token in row["text"].split() if any(c.isalnum() for c in token)]
            lexical = [word for word in mapping["words"] if any(c.isalnum() for c in word["text"])]
            require([word["text"] for word in lexical] == canonical, "Canonical lexical tokens differ")
            index = record["wordOrdinalInRow"] - 1
            require(0 <= index < len(lexical), "Invalid lexical ordinal")
            word = lexical[index]
            require(word["id"] == record["wordId"] and word["verified"] is True
                    and word["id"] not in tokens, "Frozen lexical identity differs")
            tokens[word["id"]] = canonical[index]
    require(len(tokens) == 962, "Frozen lexical position count differs")
    return tokens


def project(token_ids, tokens, order, mode):
    require(order in ("forward", "reverse"), "Unexpected order")
    ordered = token_ids if order == "forward" else reversed(token_ids)
    words = [tokens[identifier] for identifier in ordered]
    if mode == "words-joined":
        return "".join(words)
    require(mode == "initials", "Unexpected projection")
    return "".join(next(character for character in word if character.isalnum()) for word in words)


def mask_options(descriptor, leaves, leaf_order):
    selector = descriptor["selector"]
    require(selector in ("source-only", "target-only"), "Unexpected selector")
    scope = descriptor["scope"]
    if scope == "global":
        return [
            sorted({tuple(first) + tuple(second) for first, second in leaves[leaf][selector]})
            for leaf in leaf_order
        ]
    for leaf in leaf_order:
        lower, higher = leaf
        for index, (source, target) in enumerate(((lower, higher), (higher, lower))):
            if scope == f"{source}-to-{target}":
                return [sorted({tuple(pair[index]) for pair in leaves[leaf][selector]})]
    raise ValueError("Unexpected scope")


def scan_product(options, tokens, descriptor, used_products, used_characters):
    require(all(options), "Empty mask population")
    products = prod(len(group) for group in options)
    require(used_products + products <= MAX_PRODUCTS, "Flat product cap reached")
    flags = {name: dict.fromkeys(patterns, False) for name, patterns in PATTERNS.items()}
    characters = 0
    for parts in product(*options):
        text = project(tuple(identifier for part in parts for identifier in part), tokens,
                       descriptor["order"], descriptor["mode"])
        characters += len(text)
        require(used_characters + characters <= MAX_CHARACTERS, "Flat character cap reached")
        for name, patterns in PATTERNS.items():
            for length, pattern in patterns.items():
                found = pattern.search(text) is not None
                flags[name][length] |= found
    return flags, products, characters


def self_test():
    require(PATTERNS["minikey"]["22"].search("!" + "S" + "a" * 21 + "!") is not None,
            "Embedded minikey grammar control failed")
    require(PATTERNS["minikey"]["22"].search("S" + "a" * 20 + "0") is None,
            "Non-Base58 boundary control failed")
    require(PATTERNS["wif"]["52"].search("5" + "a" * 51) is not None,
            "WIF grammar control failed")
    require(project(("a", "b"), {"a": "(Écho)", "b": "Beta."}, "reverse", "initials") == "BÉ",
            "Reverse Unicode projection control failed")
    flags, count, _ = scan_product(
        [[("left",)], [(), ("right",)]], {"left": "S" + "a" * 10, "right": "a" * 11},
        {"order": "forward", "mode": "words-joined"}, 0, 0,
    )
    require(count == 2 and flags["minikey"]["22"] and not flags["minikey"]["26"],
            "Full-product seam control failed")


def verify(args):
    research = args.research.resolve()
    module_path = research / "scripts/verify_g02_shared_query.py"
    spec = spec_from_file_location("registered_g02_mask_verifier", module_path)
    verifier = module_from_spec(spec)
    spec.loader.exec_module(verifier)
    started = verifier.utc()
    output = verifier._private_path(args.out, research)
    protocol, pinned, protocol_sha = verifier._verified_bytes(
        research, args.protocol.resolve(), args.registration_commit
    )
    primary_raw = args.primary_result.read_bytes()
    primary = json.loads(primary_raw)
    primary_sha = verifier.digest(primary_raw)
    mask_receipt_raw = args.mask_receipt.read_bytes()
    mask_receipt = json.loads(mask_receipt_raw)
    require(primary["testId"] == verifier.TEST_ID and primary["sharedQueryComplete"] is True
            and primary["registrationCommit"] == args.registration_commit
            and primary["protocolSha256"] == protocol_sha, "Primary result is unbound")
    require(mask_receipt["verificationPassed"] is True
            and mask_receipt["completePairedMaskAgreement"] is True
            and mask_receipt["primaryResultSha256"] == primary_sha
            and mask_receipt["protocolSha256"] == protocol_sha
            and mask_receipt["registrationCommit"] == args.registration_commit, "Mask receipt is unbound")

    grouped = verifier._bound_inventory(pinned)
    tokens = bind_lexical_tokens(pinned, grouped)
    masks = verifier._mask_pages(json.loads(pinned[verifier.MAP]), json.loads(pinned[verifier.DUPLEX]))
    leaves = {}
    for leaf in verifier.LEAVES:
        leaves[leaf], _ = verifier.paired_leaf(
            grouped[leaf], masks, leaf, radius=protocol["guardPx"], width=protocol["widthPx"],
            maximum_cells=protocol["maximumIndependentLeafCells"],
            maximum_masks=protocol["maximumIndependentPairedMasks"],
        )
    paired_sha = verifier.paired_digest({f"{a}-{b}": values for (a, b), values in leaves.items()})
    require(paired_sha == primary["pairedMaskSha256"] == mask_receipt["pairedMaskSha256"],
            "Paired masks differ from verified inventory")
    prior_raw = pinned[verifier.SHAPE_RESULT]
    require(verifier.digest(prior_raw) == primary["priorShapeResultSha256"], "Predecessor result is unbound")
    prior = json.loads(prior_raw)
    require(len(prior["descriptors"]) == prior["counts"]["completedDescriptors"] == 160
            and all(row["complete"] and row["reason"] is None for row in prior["descriptors"]),
            "Predecessor descriptor population is incomplete")
    descriptors = [
        row for row in prior["descriptors"]
        if any(value for name in GRAMMAR for value in row["presence"][name].values())
    ]
    checks = primary["languageChecks"]
    ids = [row["id"] for row in descriptors]
    require(len(descriptors) == len(set(ids)) == len(checks) == 8
            and ids == [row["id"] for row in checks], "Registered positive descriptor scope differs")
    totals = Counter()
    products = characters = flags_compared = positive = 0
    for descriptor, saved in zip(descriptors, checks):
        require(saved["priorPresence"] == {name: descriptor["presence"][name] for name in GRAMMAR},
                "Saved predecessor grammar flags differ")
        options = mask_options(descriptor, leaves, verifier.LEAVES)
        require([len(group) for group in options] == saved["distinctMasksByFragment"][::(
            -1 if descriptor["scope"] == "global" and descriptor["order"] == "reverse" else 1
        )], "Projected mask counts differ")
        flags, evaluated, length = scan_product(options, tokens, descriptor, products, characters)
        require(flags == saved["sharedQueryPresence"], "Flat syntax flags differ from primary")
        products += evaluated
        characters += length
        flags_compared += sum(len(group) for group in flags.values())
        positive += any(value for group in flags.values() for value in group.values())
        for name, group in flags.items():
            totals.update(name + size for size, found in group.items() if found)
    require(dict(totals) == primary["shapePresentDescriptorCounts"]
            and positive == primary["counts"]["syntaxPositiveLanguages"], "Aggregate shape counts differ")
    result = {
        "version": 1, "testId": verifier.TEST_ID, "verification": "post-result-flat-shape-comparison",
        "verificationPassed": True, "startedAtUTC": started, "completedAtUTC": verifier.utc(),
        "registrationCommit": args.registration_commit, "protocolSha256": protocol_sha,
        "primaryResultSha256": primary_sha, "pairedMaskSha256": paired_sha,
        "independentMaskReceiptSha256": verifier.digest(mask_receipt_raw),
        "verifierSha256": verifier.digest(Path(__file__).read_bytes()),
        "maskVerifierSha256": verifier.digest(pinned[verifier.SCRIPT_PATH]),
        "counts": {"descriptorsCompared": len(descriptors), "flagsCompared": flags_compared,
                   "completeProductsScanned": products, "projectedCharactersScanned": characters,
                   "positiveDescriptors": positive},
        "shapePresentDescriptorCounts": dict(totals),
        "limits": {"maximumProducts": MAX_PRODUCTS, "maximumCharacters": MAX_CHARACTERS,
                   "conditionalQueryModelOnly": True, "physicalDisplacementMeasured": False},
        "activity": {"rawStreamsSaved": 0, "rawStreamsPrinted": 0, "keyChecksumValidations": 0,
                     "derivations": 0, "historyQueries": 0, "walletActions": 0, "networkQueries": 0},
    }
    with os.fdopen(os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as handle:
        os.fchmod(handle.fileno(), 0o600)
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(result["counts"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--research", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--registration-commit")
    parser.add_argument("--primary-result", type=Path)
    parser.add_argument("--mask-receipt", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    self_test()
    if args.self_test:
        print(json.dumps({"syntheticControlsPassed": True, "targetEvaluations": 0}))
        return
    if not all((args.research, args.protocol, args.registration_commit,
                args.primary_result, args.mask_receipt, args.out)):
        parser.error("Supply all verification arguments")
    verify(args)


if __name__ == "__main__":
    main()
