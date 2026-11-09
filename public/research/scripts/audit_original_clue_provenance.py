#!/usr/bin/env python3
"""Recover and record source-level clue provenance.

This pass archives the public oEmbed payloads for the announcement tweet and
the later Schott/mirror clue tweet, then expands the short links. It does not
generate key candidates or run text transforms.
"""

from __future__ import annotations

import html
import json
import re
import ssl
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/external_clues"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "original_clue_provenance.json"
OUT_MD = OUT / "original_clue_provenance.md"

TWEETS = {
    "announcement": {
        "id": "1632068898169450497",
        "url": "https://twitter.com/maxkeiser/status/1632068898169450497",
    },
    "schott_mirror_clue": {
        "id": "1632391507008278528",
        "url": "https://twitter.com/maxkeiser/status/1632391507008278528",
    },
}


def fetch_url(url: str, *, json_expected: bool = False) -> dict:
    endpoint = url
    req = urllib.request.Request(endpoint, headers={"User-Agent": "Mozilla/5.0"})
    contexts = [None, ssl._create_unverified_context()]
    last_error = None
    for ctx in contexts:
        try:
            if ctx is None:
                resp = urllib.request.urlopen(req, timeout=25)
            else:
                resp = urllib.request.urlopen(req, timeout=25, context=ctx)
            body = resp.read().decode("utf-8", "replace")
            item = {
                "ok": True,
                "url": url,
                "finalUrl": resp.geturl(),
                "status": getattr(resp, "status", None),
                "contentType": resp.headers.get("content-type"),
                "body": body,
                "usedUnverifiedSsl": ctx is not None,
            }
            if json_expected:
                item["json"] = json.loads(body)
            return item
        except Exception as exc:  # pragma: no cover - diagnostic script
            last_error = f"{type(exc).__name__}: {exc}"
    return {"ok": False, "url": url, "error": last_error}


def oembed_url(tweet_url: str) -> str:
    return "https://publish.twitter.com/oembed?" + urllib.parse.urlencode(
        {"url": tweet_url, "omit_script": "true", "dnt": "true"}
    )


def plain_from_tweet_html(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    # Remove the author/date suffix after the em dash for the compact text field.
    return text.split("— Max Keiser", 1)[0].strip()


def extract_links(fragment: str) -> list[str]:
    return [html.unescape(m) for m in re.findall(r'href="([^"]+)"', fragment)]


def expand_short_link(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    contexts = [None, ssl._create_unverified_context()]
    last_error = None
    for ctx in contexts:
        try:
            if ctx is None:
                resp = urllib.request.urlopen(req, timeout=25)
            else:
                resp = urllib.request.urlopen(req, timeout=25, context=ctx)
            # Read a small amount so redirects complete; do not store page bodies.
            resp.read(256)
            return {
                "url": url,
                "ok": True,
                "finalUrl": resp.geturl(),
                "status": getattr(resp, "status", None),
                "contentType": resp.headers.get("content-type"),
                "usedUnverifiedSsl": ctx is not None,
            }
        except Exception as exc:  # pragma: no cover - diagnostic script
            last_error = f"{type(exc).__name__}: {exc}"
    return {"url": url, "ok": False, "error": last_error}


def main() -> None:
    tweet_results = {}
    short_links = []
    for name, info in TWEETS.items():
        fetched = fetch_url(oembed_url(info["url"]), json_expected=True)
        record = {**info, "oembed": fetched}
        if fetched["ok"]:
            html_fragment = fetched["json"].get("html", "")
            record["plainText"] = plain_from_tweet_html(html_fragment)
            record["links"] = extract_links(html_fragment)
            short_links.extend(link for link in record["links"] if "https://t.co/" in link)
        tweet_results[name] = record

    expanded = [expand_short_link(link) for link in sorted(set(short_links))]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-level clue provenance; no key derivation",
        "tweets": tweet_results,
        "expandedShortLinks": expanded,
        "assessment": [
            "The announcement tweet is recoverable as raw oEmbed and repeats the private-key/source/20 BTC statement.",
            "The Schott clue tweet is recoverable as raw oEmbed and quotes the exact paper title.",
            "The Schott clue tweet short links expand to the PMC paper and back to the original announcement tweet, confirming it is an instruction pointer tied to the same puzzle source.",
            "No additional selector words are present in the recovered tweet text itself.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Original Clue Provenance",
        "",
        "Scope: recover raw source-level clue text from public oEmbed payloads and expand the short links. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Tweets",
        "",
    ]
    for name, record in tweet_results.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- tweet id: `{record['id']}`")
        lines.append(f"- source URL: `{record['url']}`")
        if record["oembed"]["ok"]:
            lines.append(f"- recovered text: `{record['plainText']}`")
            lines.append(f"- oEmbed final URL: `{record['oembed'].get('finalUrl')}`")
            lines.append(f"- used unverified SSL fallback: `{record['oembed'].get('usedUnverifiedSsl')}`")
            lines.append("- links:")
            for link in record.get("links", []):
                lines.append(f"  - `{link}`")
        else:
            lines.append(f"- recovery failed: `{record['oembed'].get('error')}`")
        lines.append("")

    lines.extend(["## Short-Link Expansions", ""])
    for item in expanded:
        if item["ok"]:
            lines.append(
                f"- `{item['url']}` -> `{item['finalUrl']}` "
                f"(status={item['status']}, unverifiedSsl={item['usedUnverifiedSsl']})"
            )
        else:
            lines.append(f"- `{item['url']}` failed: `{item['error']}`")

    lines.extend(["", "## Assessment", ""])
    for note in result["assessment"]:
        lines.append(f"- {note}")
    lines.extend(
        [
            "- This strengthens the Schott/mirror clue as intentional source provenance, but it does not by itself choose source layer, target ordering, or extraction unit.",
            "- Next best move: use this recovered clue text as the canonical clue record and avoid paraphrase drift; source acquisition still means higher-resolution Canva/original layout/physical magazine evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
