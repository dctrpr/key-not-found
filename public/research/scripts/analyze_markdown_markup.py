#!/usr/bin/env python3
import hashlib
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'analysis_outputs' / '3d_article_map' / 'user_markdown_transcript.md'
OUT = ROOT / 'analysis_outputs' / '3d_article_map' / 'markdown_markup_analysis.md'
JSON_OUT = ROOT / 'analysis_outputs' / '3d_article_map' / 'markdown_markup_analysis.json'


def split_pages(text):
    markers = [
        ('p1', 'Page 1', 0),
        ('p2', 'Page 2', text.find('**Get some toxicity. Get some bitcoin. Open your heart to**')),
        ('p3', 'Page 3', text.find('Meanwhile, back in El Salvador')),
        ('p4', 'Page 4', text.find("**We've never had an economy and a money**")),
        ('p5', 'Page 5', text.find('To wrap this up, as we move from a war and violence economy')),
    ]
    starts = [(pid, label, idx) for pid, label, idx in markers if idx >= 0]
    starts.sort(key=lambda item: item[2])
    pages = OrderedDict()
    for i, (pid, label, start) in enumerate(starts):
        end = starts[i + 1][2] if i + 1 < len(starts) else len(text)
        pages[pid] = {'label': label, 'text': text[start:end].strip()}
    return pages


def parse_markup(text):
    spans = []
    plain = []
    bold = False
    strike = False
    i = 0
    active = None
    while i < len(text):
        if text.startswith('**', i):
            if bold and active:
                active['end_plain'] = len(plain)
                spans.append(active)
                active = None
            bold = not bold
            if bold:
                active = {'kind': 'bold', 'start_plain': len(plain), 'text': ''}
            i += 2
            continue
        if text.startswith('~~', i):
            if strike and active:
                active['end_plain'] = len(plain)
                spans.append(active)
                active = None
            strike = not strike
            if strike:
                active = {'kind': 'strike', 'start_plain': len(plain), 'text': ''}
            i += 2
            continue
        ch = text[i]
        plain.append(ch)
        if active:
            active['text'] += ch
        i += 1
    if active:
        active['end_plain'] = len(plain)
        active['unclosed'] = True
        spans.append(active)
    return ''.join(plain), spans


def word_bounds(plain):
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"[A-Za-z0-9%'’.-]+", plain)]


def classify_span(span, bounds):
    s, e = span['start_plain'], span['end_plain']
    containing = [item for item in bounds if item[0] <= s and e <= item[1]]
    if not containing:
        return 'phrase'
    w0, w1, word = containing[0]
    if s == w0 and e == w1:
        return 'whole_word'
    return 'partial_word'


def clean_letters(value):
    return ''.join(re.findall(r'[A-Za-z]', value))


def caesar(value, shift):
    out = []
    for ch in value:
        if 'a' <= ch <= 'z':
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        elif 'A' <= ch <= 'Z':
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        else:
            out.append(ch)
    return ''.join(out)


def atbash(value):
    out = []
    for ch in value:
        if 'a' <= ch <= 'z':
            out.append(chr(122 - (ord(ch) - 97)))
        elif 'A' <= ch <= 'Z':
            out.append(chr(90 - (ord(ch) - 65)))
        else:
            out.append(ch)
    return ''.join(out)


def chunks(value, n):
    return ' '.join(value[i:i + n] for i in range(0, len(value), n))


def analyze_page(page):
    plain, spans = parse_markup(page['text'])
    bounds = word_bounds(plain)
    enriched = []
    for span in spans:
        item = dict(span)
        item['class'] = classify_span(span, bounds)
        item['letters'] = clean_letters(span['text'])
        enriched.append(item)
    bold = [item for item in enriched if item['kind'] == 'bold']
    partial = [item for item in bold if item['class'] == 'partial_word']
    whole = [item for item in bold if item['class'] == 'whole_word']
    phrase = [item for item in bold if item['class'] == 'phrase']
    strike = [item for item in enriched if item['kind'] == 'strike']
    return {
        **page,
        'plain': plain,
        'spans': enriched,
        'bold_partial_stream': ''.join(item['letters'] for item in partial),
        'bold_all_stream': ''.join(item['letters'] for item in bold),
        'bold_whole_words': [item['text'] for item in whole],
        'bold_phrases': [item['text'] for item in phrase],
        'strike_spans': [item['text'] for item in strike],
        'counts': {
            'bold_spans': len(bold),
            'partial_bold_spans': len(partial),
            'whole_bold_spans': len(whole),
            'phrase_bold_spans': len(phrase),
            'strike_spans': len(strike),
        },
    }


def sequence_diagnostics(label, stream):
    letters = clean_letters(stream)
    lower = letters.lower()
    return {
        'label': label,
        'length': len(letters),
        'stream': letters,
        'chunks_5': chunks(letters, 5),
        'chunks_8': chunks(letters, 8),
        'reverse': letters[::-1],
        'atbash': atbash(letters),
        'caesar_candidates': {str(shift): caesar(lower, shift) for shift in range(26)},
        'sha256': hashlib.sha256(letters.encode()).hexdigest() if letters else '',
        'frequency': Counter(lower),
    }


def main():
    text = SRC.read_text()
    pages = split_pages(text)
    analyzed = OrderedDict((pid, analyze_page(page)) for pid, page in pages.items())
    partial_all = ''.join(page['bold_partial_stream'] for page in analyzed.values())
    all_bold = ''.join(page['bold_all_stream'] for page in analyzed.values())

    diagnostics = {
        'partial_all': sequence_diagnostics('partial_all', partial_all),
        'all_bold': sequence_diagnostics('all_bold', all_bold),
    }
    diagnostics['per_page_partial'] = {
        pid: sequence_diagnostics(pid, page['bold_partial_stream'])
        for pid, page in analyzed.items()
    }

    lines = ['# Markdown Markup Analysis', '']
    lines.append('Scope: parse the user-supplied Markdown transcript as a markup source. `**...**` is bold; `~~...~~` is black/grey highlight.')
    lines.append('')
    lines.append('## Counts')
    for pid, page in analyzed.items():
        c = page['counts']
        lines.append(
            f"- {page['label']}: bold={c['bold_spans']}, partial={c['partial_bold_spans']}, "
            f"whole={c['whole_bold_spans']}, phrase={c['phrase_bold_spans']}, strike={c['strike_spans']}, "
            f"partial_stream_len={len(page['bold_partial_stream'])}"
        )
    lines.append('')
    lines.append(f"- all partial-bold letters: {len(partial_all)}")
    lines.append(f"- all bold letters including full phrases: {len(all_bold)}")
    lines.append('')
    lines.append('## Partial-Bold Streams By Page')
    for pid, page in analyzed.items():
        stream = page['bold_partial_stream']
        lines.append(f"### {page['label']}")
        lines.append(f"- raw: `{stream}`")
        lines.append(f"- chunks 5: `{chunks(stream, 5)}`")
        lines.append(f"- reverse chunks 5: `{chunks(stream[::-1], 5)}`")
        lines.append(f"- atbash chunks 5: `{chunks(atbash(stream), 5)}`")
        lines.append('')
    lines.append('## Combined Partial-Bold Stream')
    lines.append(f"- raw: `{partial_all}`")
    lines.append(f"- chunks 5: `{chunks(partial_all, 5)}`")
    lines.append(f"- chunks 8: `{chunks(partial_all, 8)}`")
    lines.append(f"- reverse chunks 5: `{chunks(partial_all[::-1], 5)}`")
    lines.append(f"- atbash chunks 5: `{chunks(atbash(partial_all), 5)}`")
    lines.append('')
    lines.append('## First Caesar Candidates For Combined Partial Stream')
    for shift, value in list(diagnostics['partial_all']['caesar_candidates'].items()):
        if shift in {'0', '1', '2', '3', '13', '23', '24', '25'}:
            lines.append(f"- shift {shift}: `{chunks(value, 5)}`")
    lines.append('')
    lines.append('## Highlight/Strike Spans')
    for pid, page in analyzed.items():
        if not page['strike_spans']:
            continue
        lines.append(f"- {page['label']}: " + ' / '.join(f'`{span}`' for span in page['strike_spans']))
    lines.append('')
    lines.append('## Assessment')
    lines.append('- Partial bold fragments form a real, extractable sequence, but raw/reverse/atbash/simple Caesar do not immediately read as prose.')
    lines.append('- The sequence should be treated as structured key material or an index stream, not discarded.')
    lines.append('- Next best checks: map partial-bold stream positions back onto page geometry, compare with orange/black spans, and test whether per-page lengths or page-order chunks match BIP39/private-key index sizes only after a stronger selector is found.')
    OUT.write_text('\n'.join(lines) + '\n')

    serializable = {
        'source': str(SRC),
        'pages': analyzed,
        'diagnostics': diagnostics,
    }
    JSON_OUT.write_text(json.dumps(serializable, indent=2, default=lambda value: dict(value) if isinstance(value, Counter) else str(value)))
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
