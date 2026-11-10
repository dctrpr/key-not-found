#!/usr/bin/env python3
"""Offline bibliographic inventory of the retained 165-item RSS snapshot.

Python 3.9+, standard library only. The caller supplies the cached RSS file,
its expected SHA-256, the exact source URL (metadata only; never fetched), and
a NEW private output JSON path outside public directories/Git checkouts.
Only GUID, title, original pubDate text and UTC pubDate are retained per item.
Publication windows do not establish conversation/recording dates or complete
creator coverage. Raw XML, contact, author, description, link, enclosure and
HTTP metadata are never copied. Suspect title contacts block output with only
aggregate categories reported. No network or media implementation is included.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

NORMALIZATION = "rss-bibliography-xml-text-rfc2822-utc-seconds-v1"
EXPECTED_ITEMS = 165
MAX_BYTES = 2000000
WINDOWS = [
    ("december", "2022-12-12T00:00:00Z", "2023-01-10T00:00:00Z"),
    ("march", "2023-02-18T00:00:00Z", "2023-03-20T00:00:00Z"),
]
KNOWN = {
    "Buzzsprout-12448193": ("[OP64]", "2023-03-15T19:00:00Z"),
    "Buzzsprout-12498799": ("[OP65]", "2023-03-23T04:00:00Z"),
    "Buzzsprout-12546364": ("[OP66]", "2023-03-30T14:00:00Z"),
}
TITLE_GUARDS = {
    "email-like-title": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    "contact-scheme-title": re.compile(r"(?:mailto:|tel:|sms:)", re.I),
    "phone-contact-title": re.compile(r"(?:phone|whatsapp|telephone)\s*[:=]\s*[+()\d][\d ().-]{6,}", re.I),
    "personal-filesystem-title": re.compile(r"(?:\x2fUsers\x2f|\x2fhome\x2f|file://|[A-Z]:\\Users\\)", re.I),
    "credential-assignment-title": re.compile(r"(?:password|api[_-]?key|access[_-]?token)\s*[:=]", re.I),
    "tracked-url-title": re.compile(r"https?://\S*\?(?:\S*&)??(?:token|key|email|utm_[a-z]+)=", re.I),
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def parse_utc(raw_date):
    value = parsedate_to_datetime(raw_date)
    require(value.tzinfo is not None and value.utcoffset() is not None, "publication-date-needs-timezone")
    require(value.microsecond == 0, "unexpected-subsecond-publication-date")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def required_text(item, name):
    element = item.find(name)
    require(element is not None and len(element) == 0 and isinstance(element.text, str) and element.text,
            "missing-or-nonliteral-bibliographic-field")
    return element.text  # XML-decoded text, without stripping/case/Unicode edits.


def inventory(raw, expected_sha, source_url):
    require(digest(raw) == expected_sha, "source-body-hash-mismatch")
    require(len(raw) <= MAX_BYTES, "source-byte-cap")
    url = urlsplit(source_url)
    require(url.scheme == "https" and url.netloc and not url.username and not url.password and
            not url.query and not url.fragment, "source-url-needs-exact-clean-public-reference")
    require(b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper(), "DTD-or-entity-declaration-requires-review")
    root = ET.fromstring(raw)
    require(root.tag == "rss", "expected-rss-root")
    channel = root.find("channel")
    require(channel is not None, "missing-rss-channel")
    raw_items = channel.findall("item")
    require(len(raw_items) == EXPECTED_ITEMS, "fixed-snapshot-item-count-mismatch")
    items, privacy = [], Counter()
    for element in raw_items:
        guid = required_text(element, "guid")
        title = required_text(element, "title")
        publication = required_text(element, "pubDate")
        for category, pattern in TITLE_GUARDS.items():
            if pattern.search(title):
                privacy[category] += 1
        items.append({"guid": guid, "title": title, "pubDateRaw": publication,
                      "pubDateUTC": parse_utc(publication)})
    if privacy:
        # Never serialize or print the matched title, GUID, row number or value.
        return None, dict(privacy)
    require(len({x["guid"] for x in items}) == EXPECTED_ITEMS, "duplicate-guid-needs-review")
    for guid, (marker, timestamp) in KNOWN.items():
        match = [x for x in items if x["guid"] == guid]
        require(len(match) == 1 and marker in match[0]["title"] and match[0]["pubDateUTC"] == timestamp,
                "known-episode-roundtrip-mismatch")
    windows = []
    for name, start, end in WINDOWS:
        guids = [x["guid"] for x in items if start <= x["pubDateUTC"] < end]
        windows.append({"id": name, "startUTC": start, "endExclusiveUTC": end,
                        "feedPublicationItemCount": len(guids), "guids": guids})
    require([x["feedPublicationItemCount"] for x in windows] == [0, 1] and
            windows[1]["guids"] == ["Buzzsprout-12448193"], "fixed-window-count-mismatch")
    return {"version": 1, "normalizationVersion": NORMALIZATION,
            "source": {"url": source_url, "sha256": expected_sha, "bytes": len(raw)},
            "dateClass": "feed item publication, not conversation or recording date",
            "itemOrder": "Original direct RSS channel/item order; no sorting or deduplication.",
            "textPolicy": "XML-decoded bibliographic text exactly as stored; no trimming, case folding or Unicode normalization.",
            "utcPolicy": "RFC2822 pubDate must have a timezone; converted to UTC with whole seconds and Z suffix.",
            "windowPolicy": "UTC start inclusive; next-day end exclusive; no recording-date inference.",
            "itemCount": len(items), "items": items, "windows": windows,
            "limits": ["One archived feed snapshot; not complete creator or recording coverage.",
                       "Original-watch comparisons, feed linkage and source eligibility require separate evidence."]}, {}


def private_output(value):
    path = Path(value).resolve()
    require(not any(part.lower() == "public" for part in path.parts), "private-output-required")
    require(not any((parent / ".git").exists() for parent in path.parents), "output-outside-git-checkouts-required")
    require(not path.exists() and path.parent.is_dir(), "fresh-output-file-required")
    require(path.parent.stat().st_mode & 0o077 == 0, "private-parent-permissions-required")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rss", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    require(re.fullmatch(r"[a-f0-9]{64}", args.expected_sha256) is not None, "invalid-expected-source-hash")
    source = Path(args.rss)
    require(source.is_file() and source.stat().st_size <= MAX_BYTES, "source-file-byte-cap")
    output = private_output(args.out)
    result, privacy = inventory(source.read_bytes(), args.expected_sha256, args.source_url)
    if privacy:
        print(json.dumps({"status": "blocked-title-privacy-review", "categories": privacy}, sort_keys=True))
        return 2
    encoded = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    with os.fdopen(os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
        stream.write(encoded)
    print(json.dumps({"status": "PASS-private-output-only", "items": 165,
                      "windowPublicationCounts": [0, 1], "itemDatesSha256": digest(encoded),
                      "normalizationVersion": NORMALIZATION, "networkRequests": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Input/body values, paths and exception reprs are deliberately omitted.
        print(json.dumps({"status": "FAIL", "reason": "offline-inventory-could-not-complete"}))
        sys.exit(1)
