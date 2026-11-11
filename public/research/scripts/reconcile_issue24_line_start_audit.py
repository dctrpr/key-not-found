#!/usr/bin/env python3
"""Reconcile locked Issue 24 line-start observations without producing a reading."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import sys

TEST_ID = "issue24-line-start-audit"
PAGES = (75, 76, 77, 78, 79)
WIDTH, HEIGHT = 2040, 2805
CANONICAL = "sources/printed-lines.json"
CANONICAL_SHA = "c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe"
PAGE_COUNTS = dict(zip(PAGES, (32, 31, 32, 22, 25)))
SCRIPT = "scripts/reconcile_issue24_line_start_audit.py"
SHA = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}")
MAX_JSON = 2_000_000
MAX_ROWS_PER_PAGE = 96


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(raw):
    def unique(pairs):
        result = dict(pairs)
        require(len(result) == len(pairs), "Duplicate JSON key")
        return result

    def invalid_number(_):
        raise ValueError("Nonfinite JSON value")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid_number)


def read_json(path, expected=None):
    require(path.is_file() and path.stat().st_size <= MAX_JSON, "Missing or oversized metadata")
    raw = path.read_bytes()
    require(len(raw) <= MAX_JSON, "Metadata exceeded size cap")
    pin = digest(raw)
    require(expected is None or pin == expected, "Pinned metadata differs")
    return strict_json(raw), pin


def time_value(value):
    require(isinstance(value, str)
            and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", value),
            "Invalid UTC timestamp")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def norm(chunk):
    return "".join(c for c in chunk.casefold() if c.isalnum()) if chunk is not None else ""


def valid_box(box):
    return (isinstance(box, list) and len(box) == 4 and all(type(n) is int for n in box)
            and 0 <= box[0] < box[2] <= WIDTH and 0 <= box[1] < box[3] <= HEIGHT)


def box_overlap(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def valid_chunk(value):
    return (isinstance(value, str) and 0 < len(value) <= 160
            and not any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value))


def cue(row):
    return tuple(norm(chunk) for chunk in row["cue"]) if row["cue"] is not None else None


def exact_edges(a, b):
    return all(a[key] is not None and a[key] == b[key] for key in ("firstChunk", "lastChunk"))


def low_pair(a, b):
    if not box_overlap(a["boxXYXY"], b["boxXYXY"]):
        return False
    a_cue, b_cue = cue(a), cue(b)
    if a_cue is not None and a_cue == b_cue:
        return True
    return a_cue is None and b_cue is None and exact_edges(a, b)


def high_view(row):
    chunks = row["text"].split()
    require(bool(chunks), "Canonical row lacks whitespace chunks")
    # Retain each boundary exactly; normalize only the interior matching cues.
    lexical = [norm(t) for t in chunks if norm(t)]
    internal = lexical[1:-1]
    cues = {(a, b) for a, b in zip(internal, internal[1:]) if a and b}
    return {"id": row["id"], "firstChunk": chunks[0], "lastChunk": chunks[-1],
            "firstLexicalAlias": row["first_word"], "lastLexicalAlias": row["last_word"],
            "cuePairs": cues, "short": len(lexical) <= 3}


def high_pair(low, high):
    shared = cue(low[0])
    return shared is not None and shared in high["cuePairs"]


def matching(n, m, edges):
    """Find every optimal edge and the pairs used by every optimum."""
    prefix = [[0] * (m + 1) for _ in range(n + 1)]
    suffix = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            take = prefix[i][j] + 1 if (i, j) in edges else 0
            prefix[i + 1][j + 1] = max(prefix[i][j + 1], prefix[i + 1][j], take)
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            take = suffix[i + 1][j + 1] + 1 if (i, j) in edges else 0
            suffix[i][j] = max(suffix[i + 1][j], suffix[i][j + 1], take)
    maximum = prefix[n][m]
    ranks = [[] for _ in range(maximum)]
    for i, j in sorted(edges):
        before = prefix[i][j]
        if before + 1 + suffix[i + 1][j + 1] == maximum:
            # The edge can occur only at rank before + 1. A unique edge at a
            # rank is compulsory because each maximum matching uses that rank.
            ranks[before].append((i, j))
    require(all(ranks), "Optimal matching has an empty rank")
    return maximum, [r[0] for r in ranks if len(r) == 1], [p for r in ranks for p in r]


def match_rows(left, right, accepts):
    edges = {(i, j) for i, a in enumerate(left) for j, b in enumerate(right) if accepts(a, b)}
    return matching(len(left), len(right), edges)


def record_unmatched(page, stage, left_ids, right_ids, forced, possible):
    records = []
    for side, mine, other in ((0, left_ids, right_ids), (1, right_ids, left_ids)):
        matched = {p[side] for p in forced}
        for index, row_id in enumerate(mine):
            if index in matched:
                continue
            partners = [other[p[1 - side]] for p in possible if p[side] == index]
            records.append({"page": page, "stage": stage, "side": "left" if side == 0 else "right",
                            "rowId": row_id, "possibleOptimalPartners": partners,
                            "reason": "non-forced-optimal-pair" if partners else "no-optimal-pair"})
    return records


def compare_page(page, a_rows, b_rows, canonical_rows):
    high = [high_view(row) for row in canonical_rows]
    low_size, low_forced, low_possible = match_rows(a_rows, b_rows, low_pair)
    paired = [(a_rows[i], b_rows[j]) for i, j in low_forced]
    high_size, high_forced, high_possible = match_rows(paired, high, high_pair)
    low_ids = [{"A": a["id"], "B": b["id"]} for a, b in paired]
    ambiguities = record_unmatched(page, "A-vs-B", [r["id"] for r in a_rows],
                                   [r["id"] for r in b_rows], low_forced, low_possible)
    ambiguities.extend(record_unmatched(page, "low-vs-canonical", low_ids, [r["id"] for r in high],
                                        high_forced, high_possible))
    short = [{"page": page, "lowRows": low_ids[i], "possibleCanonicalRows": ids}
             for i, (a, b) in enumerate(paired) if cue(a) is None
             if (ids := [h["id"] for h in high if h["short"]
                         and exact_edges(a, h) and exact_edges(b, h)])]
    cases, evidence = [], []
    for i, j in high_forced:
        a, b = paired[i]
        h = high[j]
        identifiers = {"page": page, "lowRows": low_ids[i], "canonicalRow": h["id"]}
        geometry = {who: {"boxXYXY": row["boxXYXY"], "baseline": row["baseline"]}
                    for who, row in (("A", a), ("B", b))}
        evidence.append({**identifiers, "lowGeometry": geometry,
                         "paragraphStartAgreement": a["paragraphStart"] == b["paragraphStart"]})
        if a["paragraphStart"] != b["paragraphStart"]:
            ambiguities.append({**identifiers, "stage": "matched-row", "reason": "paragraph-disagreement"})
        for edge in ("first", "last"):
            key = edge + "Chunk"
            if a[key] is None or a[key] != b[key] or a["uncertainties"] or b["uncertainties"]:
                ambiguities.append({**identifiers, "stage": "matched-row", "edge": edge,
                                    "reason": "edge-disagreement-or-uncertainty"})
                continue
            if a[key] == h[key]:
                continue
            old_alias = h[edge + "LexicalAlias"]
            low_lexical, old_lexical = norm(a[key]), norm(old_alias)
            if not low_lexical or not old_lexical:
                classification = "lexical-edge-unresolved"
            elif low_lexical != old_lexical:
                classification = "lexical-chunk-difference"
            else:
                classification = "case-or-punctuation-only"
            cases.append({**identifiers, "edge": edge, "classification": classification,
                          "canonicalLiteralChunk": h[key], "canonicalLexicalAlias": old_alias,
                          "agreedLowLiteralChunk": a[key], "lowGeometry": geometry})
    return {
        "page": page,
        "counts": {"lowA": len(a_rows), "lowB": len(b_rows), "canonical": len(high),
                   "lowOptimalPairs": low_size, "lowForcedPairs": len(low_forced),
                   "highOptimalPairs": high_size, "highForcedPairs": len(high_forced),
                   "tentativeEdges": len(cases), "ambiguities": len(ambiguities)},
        "lowForcedPairs": low_ids, "matchedRows": evidence,
        "tentativeCases": cases, "ambiguities": ambiguities, "shortRowCandidates": short,
    }


CROPS = {"top": [0, 0, WIDTH, 1483], "bottom": [0, 1322, WIDTH, HEIGHT]}
ASSETS = {f"assets/p{page}-{side}.png": (page, box)
          for page in PAGES for side, box in CROPS.items()}
SOURCE = {"path": "keyser bitcoin .pdf",
          "sha256": "dcd13efd0e46c49927dc8ec2e38a96fffc20d92fde7434151250fd6b9c62e6f4",
          "pdfPages": {str(page): page - 73 for page in PAGES},
          "nativeDimensions": [WIDTH, HEIGHT], "rotation": 0}


def is_digest(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def validate_protocol(protocol, script_sha):
    require(protocol["testId"] == TEST_ID and protocol["version"] == 1
            and protocol["source"] == SOURCE
            and protocol["canonical"] == {"path": CANONICAL, "sha256": CANONICAL_SHA}
            and protocol["cropXYXY"] == list(CROPS.values()), "Unexpected protocol")
    pins = protocol["registrationPins"]
    require(isinstance(pins, list) and all(set(pin) == {"path", "sha256"}
            and is_digest(pin["sha256"]) for pin in pins), "Malformed registration pins")
    indexed = {pin["path"]: pin["sha256"] for pin in pins}
    require(len(indexed) == len(pins)
            and indexed.get(f"public/research/{SCRIPT}") == script_sha
            and indexed.get(f"public/research/{CANONICAL}") == CANONICAL_SHA,
            "Registered code or canonical pin differs")


def validate_packet(packet, protocol, protocol_sha):
    require(packet["testId"] == TEST_ID and packet["version"] == 1
            and packet["source"] == SOURCE and packet["protocolSha256"] == protocol_sha
            and packet["cropXYXY"] == list(CROPS.values())
            and isinstance(packet["registrationCommit"], str) and COMMIT.fullmatch(packet["registrationCommit"])
            and is_digest(packet["registrationReceiptSha256"]), "Wrong registered packet")
    pages = packet["pages"]
    expected_jpegs = protocol["embeddedJpegSha256ByPage"]
    require(set(pages) == set(expected_jpegs) == {str(p) for p in PAGES}, "Packet pages differ")
    for page, record in pages.items():
        require(is_digest(record["embeddedJpegSha256"])
                and record["embeddedJpegSha256"] == expected_jpegs[page]
                and is_digest(record["uprightRGBSha256"]), "Packet page identity differs")
    assets = packet["assets"]
    require(isinstance(assets, list) and len(assets) == len(ASSETS), "Wrong asset population")
    seen = set()
    for record in assets:
        name = record["path"]
        require(isinstance(name, str) and name in ASSETS and name not in seen, "Wrong packet asset ID")
        page, box = ASSETS[name]
        require(type(record["page"]) is int and record["page"] == page
                and valid_box(record["cropXYXY"]) and record["cropXYXY"] == box
                and record["width"] == WIDTH and record["height"] == box[3] - box[1]
                and is_digest(record["rgbSha256"]) and is_digest(record["sha256"]),
                "Packet asset geometry or identity differs")
        seen.add(name)
    return time_value(packet["preparedAtUTC"])


def validate_context(record, fields):
    require(isinstance(record, dict) and set(record) == set(fields)
            and type(record["page"]) is int and record["page"] in PAGES
            and valid_box(record["boxXYXY"]), "Invalid context record")


def validate_reader(doc, label, packet_sha, prepared, locked):
    require(isinstance(doc, dict) and set(doc) == {
        "reader", "packetManifestSha256", "startedAtUTC", "completedAtUTC",
        "priorCanonicalRowsSeen", "peerMarksSeen", "inspectedAssets", "rows",
        "exclusions", "diagnosticCrops", "notes",
    }, "Invalid reader fields")
    require(doc["reader"] == label and doc["packetManifestSha256"] == packet_sha
            and doc["priorCanonicalRowsSeen"] is False and doc["peerMarksSeen"] is False,
            "Reader identity or exposure differs")
    require(prepared <= time_value(doc["startedAtUTC"]) <= time_value(doc["completedAtUTC"]) <= locked,
            "Reader chronology differs")
    inspected = doc["inspectedAssets"]
    require(isinstance(inspected, list) and len(inspected) == len(ASSETS)
            and set(inspected) == set(ASSETS), "Reader did not cover the exact asset population")
    require(isinstance(doc["notes"], str)
            and all(isinstance(doc[k], list) for k in ("rows", "exclusions", "diagnosticCrops")),
            "Malformed reader inventory")
    ids = set()
    order = None
    counts = Counter()
    for row in doc["rows"]:
        validate_context(row, ("id", "page", "boxXYXY", "baseline", "firstChunk", "lastChunk",
                               "cue", "paragraphStart", "uncertainties"))
        identifier = row["id"]
        require(isinstance(identifier, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", identifier)
                and identifier not in ids, "Invalid or repeated row ID")
        ids.add(identifier)
        box = row["boxXYXY"]
        line = row["baseline"]
        require(isinstance(line, list) and len(line) == 2 and all(
            isinstance(p, list) and len(p) == 2 and all(type(n) is int for n in p)
            and box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]
            and p[0] < WIDTH and p[1] < HEIGHT for p in line)
            and line[0][0] < line[1][0], "Invalid baseline")
        position = (row["page"], line[0][1] + line[1][1])
        require(order is None or position >= order, "Reader rows are out of page order")
        order = position
        counts[row["page"]] += 1
        require(counts[row["page"]] <= MAX_ROWS_PER_PAGE, "Reader row cap exceeded")
        require(all(row[key] is None or valid_chunk(row[key]) for key in ("firstChunk", "lastChunk")),
                "Invalid edge chunk")
        require(row["cue"] is None or (isinstance(row["cue"], list) and len(row["cue"]) == 2
                and all(valid_chunk(value) and norm(value) for value in row["cue"])),
                "Invalid interior cue")
        require(row["paragraphStart"] is None or type(row["paragraphStart"]) is bool,
                "Invalid paragraph marker")
        require(isinstance(row["uncertainties"], list)
                and all(isinstance(note, str) and note for note in row["uncertainties"]),
                "Invalid uncertainty notes")
    for record in doc["exclusions"]:
        validate_context(record, ("page", "boxXYXY", "role", "notes"))
        require(isinstance(record["role"], str) and bool(record["role"])
                and isinstance(record["notes"], str), "Invalid exclusion")
    for record in doc["diagnosticCrops"]:
        validate_context(record, ("page", "boxXYXY"))


def compare_all(a, b, canonical):
    high = canonical["rows"]
    require(isinstance(high, list) and len(high) == sum(PAGE_COUNTS.values())
            and all(row["section"] == "body" for row in high), "Canonical body scope differs")
    expected_ids = [(page, f"p{page}r{n:02d}") for page in PAGES
                    for n in range(1, PAGE_COUNTS[page] + 1)]
    require([(row["page"], row["id"]) for row in high] == expected_ids, "Canonical order differs")
    pages = [compare_page(page, *([row for row in rows if row["page"] == page]
                                 for rows in (a["rows"], b["rows"], high))) for page in PAGES]
    return pages


def reconcile(args):
    started = utc()
    entered = args.out.absolute()
    out = entered.resolve()
    checkout = Path(__file__).resolve().parents[3]
    require(out.parent.is_dir() and not entered.is_symlink() and not out.exists()
            and all(not path.is_relative_to(checkout)
                    and "public" not in {part.lower() for part in path.parts}
                    for path in (entered, out)), "Use a fresh private result path outside the checkout")
    protocol, protocol_sha = read_json(args.protocol)
    validate_protocol(protocol, digest(Path(__file__).read_bytes()))
    packet, packet_sha = read_json(args.packet_manifest)
    prepared = validate_packet(packet, protocol, protocol_sha)
    lock, lock_sha = read_json(args.receipt_lock)
    require(lock["packetManifestSha256"] == packet_sha and set(lock["receiptHashes"]) == {"A", "B"}
            and all(is_digest(h) for h in lock["receiptHashes"].values()), "Reader lock differs")
    locked = time_value(lock["lockedAtUTC"])
    require(prepared <= locked <= time_value(started), "Reader lock chronology differs")
    readers, hashes = {}, {}
    for label, path in (("A", args.receipt_a), ("B", args.receipt_b)):
        reader, pin = read_json(path, lock["receiptHashes"][label])
        validate_reader(reader, label, packet_sha, prepared, locked)
        readers[label], hashes[label] = reader, pin
    canonical, canonical_sha = read_json(args.canonical, CANONICAL_SHA)
    pages = compare_all(readers["A"], readers["B"], canonical)
    totals = Counter()
    for page in pages:
        totals.update(page["counts"])
    totals.update({"readers": 2, "assetsPerReader": len(ASSETS), "pages": len(PAGES),
                   "confirmedSourceDeltas": 0,
                   "shortRowCandidates": sum(len(page["shortRowCandidates"]) for page in pages)})
    result = {
        "version": 1, "testId": TEST_ID,
        "status": "metadata-reconciliation-complete-adjudication-pending",
        "complete": True, "adjudicationPending": True, "confirmedSourceDeltas": [],
        "startedAtUTC": started, "completedAtUTC": utc(),
        "registrationCommit": packet["registrationCommit"], "protocolSha256": protocol_sha,
        "registrationReceiptSha256": packet["registrationReceiptSha256"],
        "packetManifestSha256": packet_sha, "receiptLockSha256": lock_sha,
        "readerReceiptHashes": hashes, "canonicalSha256": canonical_sha,
        "counts": dict(totals),
        "tentativeCases": [item for page in pages for item in page["tentativeCases"]],
        "ambiguities": [item for page in pages for item in page["ambiguities"]],
        "pages": [{key: value for key, value in page.items() if key not in {"tentativeCases", "ambiguities"}}
                  for page in pages],
        "activity": {"sourcePixelsOpened": 0, "newReadingStreams": 0, "keyChecks": 0},
    }
    with os.fdopen(os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}))


def self_test():
    universe = list(itertools.product(range(3), repeat=2))
    monotone_chains = [()]
    for n in (1, 2, 3):
        for chain in itertools.combinations(universe, n):
            if all(i < k and j < l for (i, j), (k, l) in zip(chain, chain[1:])):
                monotone_chains.append(chain)
    for mask in range(1 << len(universe)):
        edges = {pair for bit, pair in enumerate(universe) if mask & (1 << bit)}
        feasible = [set(chain) for chain in monotone_chains if set(chain) <= edges]
        largest = max(map(len, feasible))
        optimal = [chain for chain in feasible if len(chain) == largest]
        length, forced, possible = matching(3, 3, edges)
        require(length == largest and set(forced) == set.intersection(*optimal)
                and set(possible) == set.union(*optimal), "Synthetic exhaustive matching differs")

    def row(identifier, y, start, end, interior, uncertainties=()):
        return {"id": identifier, "page": 75, "boxXYXY": [10, y, 400, y + 20],
                "baseline": [[10, y + 15], [399, y + 16]], "firstChunk": start, "lastChunk": end,
                "cue": interior, "paragraphStart": False, "uncertainties": list(uncertainties)}

    def high(identifier, text, first, last):
        return {"id": identifier, "text": text, "first_word": first, "last_word": last}

    a = [row("a1", 10, "new", "word!", ["Look", "in"]),
         row("a2", 40, "Brief", "line.", None),
         row("a3", 70, "same", "end", ["make", "cue"])]
    b = [row("b1", 11, "new", "word!", ["look", "in."]),
         row("b2", 41, "Brief", "line.", None),
         row("b3", 71, "same", None, ["make", "cue"], ["Unreadable last chunk."])]
    canonical = [high("h1", "old Look — in word.", "old", "word"),
                 high("h2", "Brief line.", "Brief", "line"),
                 high("h3", "same make cue end", "same", "end")]
    found = compare_page(75, a, b, canonical)
    require(found["counts"]["lowForcedPairs"] == 3 and found["counts"]["highForcedPairs"] == 2,
            "Short row became a canonical anchor")
    require(found["shortRowCandidates"] == [{"page": 75, "lowRows": {"A":"a2","B":"b2"},
                                             "possibleCanonicalRows":["h2"]}],
            "Synthetic short row is missing from manual queue")
    require([(r["edge"], r["classification"]) for r in found["tentativeCases"]] ==
            [("first","lexical-chunk-difference"), ("last","case-or-punctuation-only")],
            "Synthetic edge differences not preserved")
    require(all(r["canonicalRow"] != "h3" for r in found["tentativeCases"]),
            "Uncertain edge produced a tentative change")
    require(not low_pair(a[0], {**b[0], "boxXYXY":[401, 11, 500, 32]}),
            "Disjoint boxes produced a match")

    prepared = time_value("2026-01-01T00:00:00Z")
    locked = time_value("2026-01-01T00:01:00Z")
    reader = {"reader":"A","packetManifestSha256":"0"*64,"startedAtUTC":"2026-01-01T00:00:01Z",
              "completedAtUTC":"2026-01-01T00:00:59Z","priorCanonicalRowsSeen":False,
              "peerMarksSeen":False,"inspectedAssets":list(ASSETS),"rows":a,"exclusions":[],
              "diagnosticCrops":[],"notes":""}
    validate_reader(reader,"A","0"*64,prepared,locked)
    rejected = [
        {"rows":[{**a[0],"boxXYXY":[10, 10, WIDTH + 1, 30]}]},
        {"rows":[{**a[0],"baseline":[[12, 20],[2, 20]]}]},
        {"rows":[{**a[0],"firstChunk":"two chunks"}]},
        {"rows":a[::-1]}, {"inspectedAssets":list(ASSETS)[:-1]}, {"peerMarksSeen":True},
    ]
    for update in rejected:
        try:
            validate_reader({**reader, **update},"A","0"*64,prepared,locked)
        except ValueError:
            continue
        raise ValueError("Malformed synthetic receipt accepted")
    print(json.dumps({"status":"passed","exhaustiveMatchingGraphs":512,
                      "malformedReceiptControls":len(rejected),"targetInputsOpened":0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    for name in ("protocol","packet-manifest","receipt-a","receipt-b","receipt-lock","canonical","out"):
        parser.add_argument(f"--{name}", type=Path)
    args = parser.parse_args()
    inputs = (args.protocol,args.packet_manifest,args.receipt_a,args.receipt_b,args.receipt_lock,
              args.canonical,args.out)
    try:
        if args.self_test:
            require(not any(inputs), "Synthetic controls take no input paths")
            self_test()
        else:
            require(all(inputs), "Supply all comparison metadata paths")
            reconcile(args)
    except (OSError,ValueError,TypeError,KeyError,IndexError,AttributeError):
        print("Incomplete line-start reconciliation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
