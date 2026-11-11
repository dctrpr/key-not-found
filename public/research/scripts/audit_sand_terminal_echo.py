#!/usr/bin/env python3
"""Check the archived terminal echo and one fixed print-boundary analogy."""
import argparse
from collections import defaultdict
import gzip
from hashlib import sha256
from itertools import groupby
import json
from pathlib import Path
import unicodedata

from audit_sand_quote_markup import metadata, read


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "analysis_outputs/continuation_20261111/sand_terminal_echo"


def digest(data):
    return sha256(data).hexdigest()


def pinned(spec):
    raw = (ROOT / spec["path"]).read_bytes()
    if digest(raw) != spec["sha256"]:
        raise ValueError(f"Pinned artifact differs: {spec['path']}")
    return raw


def canonical(text):
    return " ".join(unicodedata.normalize("NFC", text).split()).casefold().rstrip(" .…")


def archive_role(path, source):
    raw, quotes = read(path)
    if digest(raw) != source["sha256"] or metadata(quotes) != json.loads(pinned(source["priorReceipt"]))["archive"]:
        raise ValueError("Archived bytes or quotation metadata differ")
    first, question, reply = quotes
    prefix = first[0][0]
    closing, mark = question[-1]
    suffix = closing[len(prefix):]
    lead_in = bool(closing.startswith(prefix) and suffix and set(suffix) <= set(" .…") and not mark)
    question_first_words = [index for index, (text, marked) in enumerate(question, 1) if marked == text.split()[0]]
    reply_first_words = [index for index, (text, marked) in enumerate(reply, 1) if marked == text.split()[0]]
    if len(question) != 9 or question_first_words != list(range(1, 9)) or reply_first_words != [1, 2] or not lead_in:
        raise ValueError("Archived positive control did not recover the declared role")
    return {"capture": source["capture"], "sha256": digest(raw), "questionLines": len(question),
            "questionFirstWordMarks": question_first_words, "replyFirstWordMarks": reply_first_words,
            "terminalEchoOfOpeningLine": lead_in, "terminalSuffixCodepoints": [f"U+{ord(ch):04X}" for ch in suffix],
            "terminalMarked": bool(mark), "openingLineSha256": digest(prefix.encode())}


def issue24_echoes(spec, body_spec):
    rows = json.loads(pinned(spec))["rows"]
    if len(rows) != spec["units"] or [row["ordinal"] for row in rows] != list(range(1, len(rows) + 1)):
        raise ValueError("Issue 24 print model order differs")
    earlier = defaultdict(list)
    echoes = []
    for row in rows:
        text = canonical(row["printedText"])
        if not text:
            raise ValueError("An empty printed unit cannot be compared")
        if earlier[text]:
            echoes.append({"laterId": row["id"], "laterRole": row["role"], "earlierIds": earlier[text].copy()})
        earlier[text].append(row["id"])
    by_id = {row["id"]: row for row in rows}
    printed_quote = " ".join(row["printedText"] for row in rows if row["role"] == "display-quotation")
    body_source = " ".join(by_id[row_id]["printedText"] for row_id in spec["pullQuoteBodyRowIds"])
    repeated_sentence = canonical(body_source.rsplit(". ", 1)[-1]) == canonical(printed_quote)
    body = json.loads(pinned(body_spec))["rows"]
    if len(body) != body_spec["rows"]:
        raise ValueError("Issue 24 body count differs")
    paragraphs = []
    for _, group in groupby(body, lambda row: (row["page"], row["section"], row["paragraph"])):
        group = list(group)
        if len(group) != 9:
            continue
        colors = [index for index, row in enumerate(group, 1) if row["highlighted_printed_row"]]
        annotation = [index for index, row in enumerate(group, 1) if row["annotation_bold_any"]]
        paragraphs.append({"rowIds": [row["id"] for row in group], "colorMarkedRows": colors,
                           "historicalAnnotationRows": annotation,
                           "colorPatternMatchesFirstEight": colors == list(range(1, 9))})
    return {"units": len(rows), "uniqueCanonicalLines": len(earlier), "exactLineEchoes": echoes,
            "bodyParagraphsOfNineRows": paragraphs,
            "pullQuoteRepeatsBodySentenceWithDifferentWrap": repeated_sentence,
            "pullQuoteBodyRowIds": spec["pullQuoteBodyRowIds"]}


def issue26_readings(spec, assets):
    for asset in assets:
        pinned(asset)
    article = json.loads(pinned(spec))
    ordered = sorted(article["rows"], key=lambda row: row["articleReadingIndex"])
    intro = [row for row in ordered if row["flowBlock"] == spec["flowBlock"]]
    ids = [row["id"] for row in intro]
    if ids != spec["rowIds"] or [row["id"] for row in ordered[:9]] != ids or ordered[9]["id"] != spec["nextRowId"]:
        raise ValueError("Issue 26 opener or following boundary differs")
    if any(row["firstWordStatus"] != "verified-source-pixels" or row["role"] != "body-prose" for row in intro):
        raise ValueError("A fixed first word is unverified or outside the prose opener")
    if [row["paragraph"] for row in intro] != [1] * 6 + [2] * 3:
        raise ValueError("Issue 26 opener paragraph grouping differs")
    words = [row["firstWordSource"] for row in intro]
    if any(not word or word != word.strip() or len(word.split()) != 1 for word in words):
        raise ValueError("Expected one source token per physical row")
    return {"openerRowIds": ids, "paragraphSizes": [6, 3], "followingRowId": ordered[9]["id"],
            "prefixEight": " ".join(words[:8]), "wholeNine": " ".join(words),
            "ninthRowRole": intro[-1]["role"],
            "ninthRowRoleBasis": "Independent page-102 visual review: prose continuation, not a separately marked echo. Full exact text is not used."}


def prior_issue26_coverage(spec, readings):
    count = prefix = baseline = 0
    prefix_ids = readings["openerRowIds"][:8]
    for line in gzip.decompress(pinned(spec)).splitlines():
        row = json.loads(line)
        count += 1
        ids = row["selectedRowIds"]
        if ids in (prefix_ids, prefix_ids[::-1]):
            prefix += 1
        if (ids == readings["openerRowIds"] and row["unit"] == "p102-intro"
                and row["surface"] == "firstWordSource" and row["rowOrder"] == "forward"
                and row["phase"] == "all" and row["projection"] == "words-spaced"
                and row["characterOrder"] == "exact"):
            if row["text"] != readings["wholeNine"]:
                raise ValueError("Earlier whole-opener reading differs")
            baseline += 1
    if count != spec["records"] or baseline == 0:
        raise ValueError("Earlier Issue 26 ledger is incomplete")
    return {"priorRecords": count, "exactPrefixEightLabels": prefix, "exactWholeNineBaselineLabels": baseline}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--earlier", type=Path, required=True)
    parser.add_argument("--same-day", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = (DIRECTORY / "PROTOCOL.json").read_bytes()
    spec = json.loads(raw)
    archives = [archive_role(path, source) for path, source in zip([args.earlier, args.same_day], spec["archives"])]
    if archives[0]["openingLineSha256"] != archives[1]["openingLineSha256"]:
        raise ValueError("The archival opening-line identities differ")
    issue26 = issue26_readings(spec["issue26"], spec["issue26Assets"])
    issue26["priorCoverage"] = prior_issue26_coverage(spec["issue26SavedReadings"], issue26)
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              "archives": archives, "issue24": issue24_echoes(spec["issue24"], spec["issue24Body"]),
              "issue26": issue26}
    with args.out.open("x", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=False, indent=2, allow_nan=False)
        output.write("\n")


if __name__ == "__main__":
    main()
