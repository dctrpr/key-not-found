#!/usr/bin/env python3
import hashlib
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

try:
    from bip_utils import Bip39MnemonicValidator, WifDecoder
except Exception:
    Bip39MnemonicValidator = None
    WifDecoder = None


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "highlight_audit"
ORANGE_JSON = OUT_DIR / "highres_manual_highlight_reading.json"
GREY_JSON = OUT_DIR / "highres_manual_grey_reading.json"
BIP39_JSON = ROOT / "node_modules" / "bip39" / "src" / "wordlists" / "english.json"
REPORT_MD = OUT_DIR / "highres_exact_highlight_streams.md"
REPORT_JSON = OUT_DIR / "highres_exact_highlight_streams.json"

BASE58 = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")


def words(text):
    return re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text)


def letters(text):
    return re.findall(r"[A-Za-z]", text)


def norm_word(word):
    return re.sub(r"[^a-z]", "", word.lower())


def page_key(item):
    return (int(item["page"]), item["text"])


def load_spans():
    orange = json.loads(ORANGE_JSON.read_text())["combinedOrangeSpans"]
    grey = json.loads(GREY_JSON.read_text())["combinedGreyBlackSpans"]
    return {
        "orange": sorted(orange, key=page_key),
        "grey_black": sorted(grey, key=page_key),
    }


def span_initials(spans):
    return "".join(w[0] for span in spans for w in words(span["text"]) if w)


def span_last_letters(spans):
    return "".join(w[-1] for span in spans for w in words(span["text"]) if w)


def phrase_initials(spans):
    return "".join(words(span["text"])[0][0] for span in spans if words(span["text"]))


def phrase_last_letters(spans):
    return "".join(words(span["text"])[-1][-1] for span in spans if words(span["text"]))


def page_streams(spans):
    grouped = defaultdict(list)
    for span in spans:
        grouped[int(span["page"])].append(span)
    out = OrderedDict()
    for page in sorted(grouped):
        page_spans = grouped[page]
        out[f"p{page}:text"] = " ".join(span["text"] for span in page_spans)
        out[f"p{page}:word_initials"] = span_initials(page_spans)
        out[f"p{page}:word_lasts"] = span_last_letters(page_spans)
        out[f"p{page}:phrase_initials"] = phrase_initials(page_spans)
        out[f"p{page}:phrase_lasts"] = phrase_last_letters(page_spans)
        out[f"p{page}:word_lengths"] = ".".join(str(len(w)) for span in page_spans for w in words(span["text"]))
    return out


def interleave(a, b):
    out = []
    for idx in range(max(len(a), len(b))):
        if idx < len(a):
            out.append(a[idx])
        if idx < len(b):
            out.append(b[idx])
    return out


def build_streams(spans_by_color):
    streams = OrderedDict()
    for color, spans in spans_by_color.items():
        streams[f"{color}:all_text"] = " ".join(span["text"] for span in spans)
        streams[f"{color}:all_text_reverse_span_order"] = " ".join(span["text"] for span in reversed(spans))
        streams[f"{color}:word_initials"] = span_initials(spans)
        streams[f"{color}:word_lasts"] = span_last_letters(spans)
        streams[f"{color}:phrase_initials"] = phrase_initials(spans)
        streams[f"{color}:phrase_lasts"] = phrase_last_letters(spans)
        streams[f"{color}:word_lengths"] = ".".join(str(len(w)) for span in spans for w in words(span["text"]))
        for label, stream in page_streams(spans).items():
            streams[f"{color}:{label}"] = stream

    orange = spans_by_color["orange"]
    grey = spans_by_color["grey_black"]
    streams["combined:orange_then_grey:text"] = streams["orange:all_text"] + " " + streams["grey_black:all_text"]
    streams["combined:grey_then_orange:text"] = streams["grey_black:all_text"] + " " + streams["orange:all_text"]
    streams["combined:interleaved_spans:text"] = " ".join(span["text"] for span in interleave(orange, grey))
    streams["combined:interleaved_span_phrase_initials"] = phrase_initials(interleave(orange, grey))

    for page in sorted({int(span["page"]) for span in orange + grey}):
        op = [span for span in orange if int(span["page"]) == page]
        gp = [span for span in grey if int(span["page"]) == page]
        if op or gp:
            streams[f"combined:p{page}:orange_then_grey_initials"] = span_initials(op) + span_initials(gp)
            streams[f"combined:p{page}:interleaved_phrase_initials"] = phrase_initials(interleave(op, gp))
    return streams


def key_shape_checks(streams):
    checks = []
    for label, text in streams.items():
        variants = {
            "raw": text,
            "reverse_chars": text[::-1],
            "letters_only": "".join(letters(text)),
            "letters_only_reversed": "".join(reversed(letters(text))),
            "alnum_only": "".join(re.findall(r"[A-Za-z0-9]", text)),
        }
        for variant, value in variants.items():
            compact58 = "".join(ch for ch in value if ch in BASE58)
            for length in (51, 52):
                for start in range(0, max(0, len(compact58) - length + 1)):
                    chunk = compact58[start : start + length]
                    if not chunk or chunk[0] not in "5KL":
                        continue
                    valid = False
                    if WifDecoder is not None:
                        try:
                            WifDecoder.Decode(chunk)
                            valid = True
                        except Exception:
                            valid = False
                    checks.append({"label": label, "variant": variant, "type": "wif_window", "start": start, "value": chunk, "valid": valid, "credible": valid})

            for length in (22, 26, 30):
                for start in range(0, max(0, len(compact58) - length + 1)):
                    chunk = compact58[start : start + length]
                    if chunk.startswith("S") and hashlib.sha256((chunk + "?").encode()).digest()[0] == 0:
                        checks.append({"label": label, "variant": variant, "type": "minikey", "start": start, "value": chunk, "valid": True, "credible": True})

            compact_hex = "".join(re.findall(r"[0-9a-fA-F]", value))
            stripped = value.strip()
            if re.fullmatch(r"[0-9a-fA-F]{64}", stripped):
                checks.append({"label": label, "variant": variant, "type": "hex64_exact_stream", "start": 0, "value": stripped, "valid": True, "credible": True})
            elif len(compact_hex) >= 64:
                checks.append({"label": label, "variant": variant, "type": "hex64_accidental_prose_window", "count": len(compact_hex) - 63, "valid": True, "credible": False})
    return checks


def bip39_checks(spans_by_color, streams):
    wordlist = set(json.loads(BIP39_JSON.read_text())) if BIP39_JSON.exists() else set()
    span_hits = []
    for color, spans in spans_by_color.items():
        for span in spans:
            hit_words = [w for w in words(span["text"]) if norm_word(w) in wordlist]
            if hit_words:
                span_hits.append({"color": color, "page": span["page"], "text": span["text"], "bip39Words": hit_words})

    filtered_mnemonic_hits = []
    contiguous_mnemonic_hits = []
    if Bip39MnemonicValidator is not None:
        validator = Bip39MnemonicValidator()
        for label, text in streams.items():
            normalized = [norm_word(w) for w in words(text)]
            valid_words = [w for w in normalized if w in wordlist]
            for size in (12, 24):
                for start in range(0, max(0, len(valid_words) - size + 1)):
                    phrase = " ".join(valid_words[start : start + size])
                    if validator.IsValid(phrase):
                        filtered_mnemonic_hits.append({"label": label, "start": start, "size": size, "phrase": phrase})
                for start in range(0, max(0, len(normalized) - size + 1)):
                    window = normalized[start : start + size]
                    if all(word in wordlist for word in window):
                        phrase = " ".join(window)
                        if validator.IsValid(phrase):
                            contiguous_mnemonic_hits.append({"label": label, "start": start, "size": size, "phrase": phrase})
    return span_hits, filtered_mnemonic_hits, contiguous_mnemonic_hits


def main():
    spans_by_color = load_spans()
    streams = build_streams(spans_by_color)
    key_checks = key_shape_checks(streams)
    credible_key_shapes = [item for item in key_checks if item.get("credible")]
    accidental_key_shapes = [item for item in key_checks if item.get("valid") and not item.get("credible")]
    bip39_span_hits, filtered_bip39_mnemonic_hits, contiguous_bip39_mnemonic_hits = bip39_checks(spans_by_color, streams)

    result = {
        "source": {
            "orange": str(ORANGE_JSON),
            "greyBlack": str(GREY_JSON),
        },
        "spanCounts": {color: len(spans) for color, spans in spans_by_color.items()},
        "streams": streams,
        "keyShapeChecks": key_checks,
        "credibleKeyShapes": credible_key_shapes,
        "accidentalKeyShapes": accidental_key_shapes,
        "bip39SpanHits": bip39_span_hits,
        "filteredBip39MnemonicHits": filtered_bip39_mnemonic_hits,
        "contiguousBip39MnemonicHits": contiguous_bip39_mnemonic_hits,
    }
    REPORT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    lines = [
        "# High-Res Exact Highlight Streams",
        "",
        "Inputs are the manual high-res orange and grey/black highlight readings, not OCR.",
        "",
        "## Summary",
        "",
        f"- Orange spans: {len(spans_by_color['orange'])}",
        f"- Grey/black spans: {len(spans_by_color['grey_black'])}",
        f"- Streams generated: {len(streams)}",
        f"- Credible direct WIF/minikey/exact-hex candidates: {len(credible_key_shapes)}",
        f"- Accidental hex-like prose windows ignored: {len(accidental_key_shapes)}",
        f"- Contiguous checksum-valid BIP39 12/24-word mnemonics: {len(contiguous_bip39_mnemonic_hits)}",
        f"- Filtered BIP39-word checksum hits, treated as accidental: {len(filtered_bip39_mnemonic_hits)}",
        "",
        "## High-Signal Streams",
        "",
    ]
    for key in [
        "orange:phrase_initials",
        "orange:word_initials",
        "orange:word_lasts",
        "grey_black:phrase_initials",
        "grey_black:word_initials",
        "grey_black:word_lasts",
        "combined:interleaved_span_phrase_initials",
    ]:
        lines.append(f"- `{key}`: `{streams.get(key, '')}`")

    lines.extend(["", "## Per-Page Phrase Initials", ""])
    for color in ("orange", "grey_black"):
        for page in (75, 76, 77, 78, 79, 80):
            key = f"{color}:p{page}:phrase_initials"
            if key in streams:
                lines.append(f"- `{key}`: `{streams[key]}`")

    lines.extend(["", "## Direct Key Shapes", ""])
    if credible_key_shapes:
        lines.append("- Local checksum/key-shape candidates found. These need chain validation before being treated as meaningful:")
        for item in credible_key_shapes:
            lines.append(f"- {item['type']} from `{item['label']}` / `{item['variant']}`: `{item['value']}`")
    else:
        lines.append("- No local WIF, minikey, or exact 64-hex candidates found.")
    lines.append("- Hex-looking windows made from ordinary prose letters `a-f` are counted separately as accidental and ignored.")

    lines.extend(["", "## BIP39 Word Presence", ""])
    lines.append(f"- Highlight spans containing at least one BIP39 word: {len(bip39_span_hits)}")
    lines.append("- This is expected with normal English prose and is not enough by itself.")
    for hit in bip39_span_hits[:12]:
        lines.append(f"- {hit['color']} p{hit['page']}: `{', '.join(hit['bip39Words'])}`")
    if len(bip39_span_hits) > 12:
        lines.append(f"- Additional BIP39-bearing spans omitted from this summary: {len(bip39_span_hits) - 12}")

    lines.extend(["", "## Conclusion", ""])
    lines.append("- Exact high-res highlighted text does not directly contain a contiguous checksum-valid BIP39 mnemonic, WIF, or exact 64-hex private key.")
    lines.append("- Minikey checksum windows can occur by chance inside long prose-derived streams; they require address activity or a strong selector rule before being considered real.")
    lines.append("- The useful signal is still selector/order: phrase initials, page grouping, color grouping, and page-76/El-Salvador intersections should be used as labels for geometry, not as direct keys.")
    lines.append("- OCR-derived highlight text should stay excluded from text-stream candidate generation.")
    REPORT_MD.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(f"credible_key_shapes={len(credible_key_shapes)} contiguous_bip39_mnemonics={len(contiguous_bip39_mnemonic_hits)} filtered_bip39_hits={len(filtered_bip39_mnemonic_hits)}")


if __name__ == "__main__":
    main()
