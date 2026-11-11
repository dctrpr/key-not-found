#!/usr/bin/env python3
"""Compare explicit HTML line breaks and bold spans in the three linked examples."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Quotes(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.bold = 0
        self.quotes = []

    def handle_starttag(self, tag, attrs):
        if tag == "blockquote":
            if not self.depth:
                self.quotes.append([[]])
                self.bold = 0
            self.depth += 1
        elif self.depth and tag in ("strong", "b"):
            self.bold += 1
        elif self.depth and tag == "br":
            self.quotes[-1].append([])

    def handle_endtag(self, tag):
        if tag == "blockquote" and self.depth:
            self.depth -= 1
        elif self.depth and tag in ("strong", "b"):
            self.bold = max(0, self.bold - 1)

    def handle_data(self, text):
        if self.depth:
            self.quotes[-1][-1].append((text, bool(self.bold)))

    def lines(self):
        quotes = []
        for quote in self.quotes:
            rows = []
            for segments in quote:
                whole = " ".join("".join(text for text, _ in segments).split())
                marked = " ".join("".join(text for text, bold in segments if bold).split())
                if whole:
                    rows.append((whole, marked))
            quotes.append(rows)
        return quotes


def read(path):
    raw = path.read_bytes()
    parser = Quotes()
    parser.feed(raw.decode("utf8"))
    return raw, parser.lines()


def metadata(quotes):
    return [
        {"visibleLines": len(quote),
         "markedLineNumbers": [i for i, (_, marked) in enumerate(quote, 1) if marked],
         "visibleMarkupSha256": sha(json.dumps(quote, ensure_ascii=False, separators=(",", ":")).encode())}
        for quote in quotes
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archived", type=Path)
    parser.add_argument("current", type=Path)
    args = parser.parse_args()
    old_raw, old = read(args.archived)
    new_raw, new = read(args.current)
    if len(old) != 3 or len(new) != 3:
        parser.error("Expected exactly three quotation blocks per document")
    print(json.dumps({
        "captureRawSha256": sha(old_raw), "currentRawSha256": sha(new_raw),
        "archive": metadata(old), "current": metadata(new),
        "openingLetterFinalRowSplit": (
            old[0][:-1] == new[0][:-2] and old[0][-1][0] == " ".join(row[0] for row in new[0][-2:])
            and not old[0][-1][1] and not new[0][-2][1] and bool(new[0][-1][1])),
        "secondAndThirdQuoteBlocksIdentical": old[1:] == new[1:],
    }, indent=2))


if __name__ == "__main__":
    main()
