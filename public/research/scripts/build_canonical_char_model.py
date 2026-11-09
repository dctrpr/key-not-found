#!/usr/bin/env python3
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'analysis_outputs' / '3d_article_map' / 'user_markdown_transcript.md'
OUT_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'canonical_char_model.json'
OUT_MD = ROOT / 'analysis_outputs' / '3d_article_map' / 'canonical_char_model.md'

PAGE_MARKERS = [
    ('p1', 75, 'Article page 75', None),
    ('p2', 76, 'Article page 76', '**Get some toxicity. Get some bitcoin. Open your heart to**'),
    ('p3', 77, 'Article page 77', 'Meanwhile, back in El Salvador'),
    ('p4', 78, 'Article page 78', "**We've never had an economy and a money**"),
    ('p5', 79, 'Article pages 79-80 text block', 'To wrap this up, as we move from a war and violence economy'),
]

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)?|[%$][A-Za-z0-9]+|[A-Za-z0-9]+[%]")


def split_pages(text):
    starts = []
    for pid, article_page, label, marker in PAGE_MARKERS:
        idx = 0 if marker is None else text.find(marker)
        if idx >= 0:
            starts.append((idx, pid, article_page, label))
    starts.sort()
    pages = OrderedDict()
    for n, (start, pid, article_page, label) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(text)
        pages[pid] = {
            'pid': pid,
            'articlePage': article_page,
            'label': label,
            'markdown': text[start:end].strip(),
        }
    return pages


def parse_markup(markdown):
    chars = []
    lines = [{'lineIndex': 0, 'start': 0, 'text': ''}]
    bold = False
    strike = False
    italic = False
    i = 0
    plain_i = 0
    line_i = 0
    col_i = 0

    while i < len(markdown):
        if markdown.startswith('**', i):
            bold = not bold
            i += 2
            continue
        if markdown.startswith('~~', i):
            strike = not strike
            i += 2
            continue
        if markdown[i] == '*' and not markdown.startswith('**', i):
            italic = not italic
            i += 1
            continue
        if markdown[i] == '\\' and i + 1 < len(markdown):
            i += 1
        ch = markdown[i]
        item = {
            'plainIndex': plain_i,
            'lineIndex': line_i,
            'colIndex': col_i,
            'c': ch,
            'bold': bold,
            'strike': strike,
            'italic': italic,
        }
        chars.append(item)
        lines[-1]['text'] += ch
        plain_i += 1
        if ch == '\n':
            lines[-1]['end'] = plain_i
            line_i += 1
            col_i = 0
            lines.append({'lineIndex': line_i, 'start': plain_i, 'text': ''})
        else:
            col_i += 1
        i += 1

    if lines:
        lines[-1]['end'] = plain_i
    plain = ''.join(ch['c'] for ch in chars)
    return plain, chars, lines


def word_records(plain, chars):
    words = []
    for wi, match in enumerate(WORD_RE.finditer(plain)):
        start, end = match.span()
        wchars = chars[start:end]
        text = match.group(0)
        letters = ''.join(ch['c'] for ch in wchars if ch['c'].isalpha())
        bold_letters = ''.join(ch['c'] for ch in wchars if ch['bold'] and ch['c'].isalpha())
        strike_letters = ''.join(ch['c'] for ch in wchars if ch['strike'] and ch['c'].isalpha())
        alpha_chars = [ch for ch in wchars if ch['c'].isalpha()]
        alpha_count = len(alpha_chars)
        bold_alpha_count = sum(1 for ch in alpha_chars if ch['bold'])
        strike_alpha_count = sum(1 for ch in alpha_chars if ch['strike'])
        words.append({
            'wordIndex': wi,
            'start': start,
            'end': end,
            'lineIndex': wchars[0]['lineIndex'] if wchars else None,
            'text': text,
            'letters': letters,
            'lower': letters.lower(),
            'boldLetters': bold_letters,
            'strikeLetters': strike_letters,
            'hasBold': bold_alpha_count > 0,
            'allBold': alpha_count > 0 and bold_alpha_count == alpha_count,
            'partialBold': 0 < bold_alpha_count < alpha_count,
            'hasStrike': strike_alpha_count > 0,
            'allStrike': alpha_count > 0 and strike_alpha_count == alpha_count,
        })
    return words


def page_model(page):
    plain, chars, lines = parse_markup(page['markdown'])
    words = word_records(plain, chars)
    partial_stream = ''.join(word['boldLetters'] for word in words if word['partialBold'])
    all_bold_stream = ''.join(word['boldLetters'] for word in words if word['hasBold'])
    strike_stream = ''.join(word['strikeLetters'] for word in words if word['hasStrike'])
    return {
        **page,
        'plain': plain,
        'chars': chars,
        'lines': lines,
        'words': words,
        'streams': {
            'partialBoldLetters': partial_stream,
            'allBoldLetters': all_bold_stream,
            'strikeLetters': strike_stream,
            'firstLetters': ''.join(word['letters'][:1] for word in words if word['letters']),
            'lastLetters': ''.join(word['letters'][-1:] for word in words if word['letters']),
        },
        'counts': {
            'plainChars': len(plain),
            'words': len(words),
            'boldWordsAny': sum(1 for word in words if word['hasBold']),
            'boldWordsAll': sum(1 for word in words if word['allBold']),
            'boldWordsPartial': sum(1 for word in words if word['partialBold']),
            'strikeWordsAny': sum(1 for word in words if word['hasStrike']),
            'partialBoldLetters': len(partial_stream),
            'allBoldLetters': len(all_bold_stream),
            'strikeLetters': len(strike_stream),
        },
    }


def summarize_word(word):
    flags = []
    if word['partialBold']:
        flags.append(f"partial=`{word['boldLetters']}`")
    elif word['allBold']:
        flags.append('all-bold')
    if word['hasStrike']:
        flags.append('strike')
    return f"{word['wordIndex']:03d}:{word['text']} ({', '.join(flags)})"


def build_report(model):
    lines = ['# Canonical Character Model', '']
    lines.append('Source: user-supplied Markdown transcript. This is the corrected text layer used for selector experiments.')
    lines.append('')
    lines.append('## Page Mapping')
    lines.append('- Logical pages p1-p5 are mapped to article pages 75-79/80 by transcript boundaries. Page 5 likely spans the end of the article across pages 79-80, so geometry checks should treat that mapping as approximate.')
    lines.append('')
    lines.append('## Counts')
    for page in model['pages'].values():
        c = page['counts']
        lines.append(
            f"- {page['pid']} / {page['label']}: words={c['words']}, "
            f"partial-bold-words={c['boldWordsPartial']}, all-bold-words={c['boldWordsAll']}, "
            f"partial-bold-letters={c['partialBoldLetters']}, all-bold-letters={c['allBoldLetters']}, "
            f"strike-letters={c['strikeLetters']}"
        )
    lines.append('')
    lines.append('## Partial-Bold Streams')
    for page in model['pages'].values():
        stream = page['streams']['partialBoldLetters']
        lines.append(f"- {page['pid']}: len={len(stream)} `{stream}`")
    lines.append('')
    lines.append('## Page 76 Marked Words')
    page76 = next((page for page in model['pages'].values() if page['articlePage'] == 76), None)
    if page76:
        marked = [word for word in page76['words'] if word['hasBold'] or word['hasStrike']]
        for chunk_start in range(0, len(marked), 12):
            lines.append('- ' + ' / '.join(summarize_word(word) for word in marked[chunk_start:chunk_start + 12]))
    lines.append('')
    lines.append('## Global Letter Frequency')
    partial_all = model['streams']['partialBoldLetters']
    freq = Counter(partial_all.lower())
    lines.append('- partial-bold: ' + ', '.join(f'{k}:{v}' for k, v in sorted(freq.items())))
    lines.append('')
    lines.append('## Interpretation')
    lines.append('- The corrected markup is now usable at character, word, and page level.')
    lines.append('- Direct bold-stream key derivation was already ruled out; the next tests should use intersections with mirror/reflection/ray selectors and page-76 target phrases.')
    return '\n'.join(lines) + '\n'


def main():
    pages = OrderedDict((pid, page_model(page)) for pid, page in split_pages(SRC.read_text()).items())
    model = {
        'source': str(SRC),
        'pages': pages,
        'streams': {
            'partialBoldLetters': ''.join(page['streams']['partialBoldLetters'] for page in pages.values()),
            'allBoldLetters': ''.join(page['streams']['allBoldLetters'] for page in pages.values()),
            'strikeLetters': ''.join(page['streams']['strikeLetters'] for page in pages.values()),
        },
    }
    OUT_JSON.write_text(json.dumps(model, indent=2))
    OUT_MD.write_text(build_report(model))
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')


if __name__ == '__main__':
    main()
