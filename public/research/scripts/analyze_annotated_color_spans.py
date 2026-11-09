#!/usr/bin/env python3
import json
import re
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANNOTATED = ROOT / 'analysis_outputs' / '3d_article_map' / 'user_annotated_transcript.txt'
MODEL_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'canonical_char_model.json'
OUT_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'annotated_color_span_analysis.json'
OUT_MD = ROOT / 'analysis_outputs' / '3d_article_map' / 'annotated_color_span_analysis.md'

PAGE_SPLITS = [
    ('p1', 75, None),
    ('p2', 76, 'Second page'),
    ('p3', 77, 'page 3'),
    ('p4', 78, 'Page 4'),
    ('p5', 79, 'Page 5'),
]

DESCRIPTOR_PATTERNS = [
    r'\s+all\s+in\s+bold\s+and\s+highlighted\s+(orange|grey|gray)\s*$',
    r'\s+all\s+in\s+bold\s+and\s+(orange|grey|gray)\s+highlight\s*$',
    r'\s+all\s+in\s+bold\s+and\s+(orange|grey|gray)\s+highlighted\s*$',
    r'\s+all\s+in\s+bold\s+and\s+(orange|grey|gray)\s+highlight\s*$',
    r'\s+all\s+in\s+bold\s+and\s+(grey|gray)\s+highlight\s*$',
    r'\s+all\s+in\s+bold\s+and\s+highlighter\s+(orange|grey|gray)\s*$',
    r'\s+in\s+bold\s+and\s+highlighted\s+in\s+(orange|grey|gray)\s*$',
    r'\s+in\s+bold\s+and\s+highlighted\s+(orange|grey|gray)\s*$',
    r'\s+in\s+bold\s+highlighted\s+(orange|grey|gray)\s*$',
    r'\s+all\s+bold\s+(orange|grey|gray)\s+highlight\s*$',
    r'\s+all\s+in\s+bold\s+and\s+highlight\s+(orange|grey|gray)\s*$',
    r'\s+bold\s+and\s+highlighted\s+(orange|grey|gray)\s*$',
    r'\s+bold\s+and\s+highlighter\s+(orange|grey|gray)\s*$',
    r'\s+in\s+bold\s+and\s+highlighter\s+(orange|grey|gray)\s*$',
    r'\s+all\s+in\s+bold\s*$',
    r'\s+in\s+bold\s*$',
    r'\s+bold\s*$',
    r'\s+in\s+(orange|grey|gray)\s*$',
]


def normalize_color(color):
    if not color:
        return None
    return 'grey' if color == 'gray' else color


def split_annotated_pages(text):
    starts = []
    for pid, article_page, marker in PAGE_SPLITS:
        idx = 0 if marker is None else text.find(marker)
        if idx >= 0:
            starts.append((idx, pid, article_page))
    starts.sort()
    pages = OrderedDict()
    for i, (start, pid, article_page) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        pages[pid] = {'pid': pid, 'articlePage': article_page, 'text': text[start:end]}
    return pages


def clean_phrase(value):
    value = value.strip().strip('.,;: ')
    value = value.replace('“', '"').replace('”', '"').replace('’', "'")
    value = re.sub(r'\s+', ' ', value)
    return value


def parse_annotation(inside, prefix_text):
    raw = clean_phrase(inside)
    low = raw.lower()
    color = None
    if 'orange' in low:
        color = 'orange'
    elif 'grey' in low or 'gray' in low:
        color = 'grey'
    if not color:
        return None

    if low.startswith('last sentence'):
        sentences = re.split(r'(?<=[.!?])\s+', prefix_text.strip())
        sentence = sentences[-1] if sentences else ''
        return {'phrase': clean_phrase(sentence), 'color': color, 'annotation': raw}

    phrase = raw
    for pattern in DESCRIPTOR_PATTERNS:
        m = re.search(pattern, phrase, flags=re.I)
        if m:
            color = normalize_color(m.group(1).lower()) if m.groups() else color
            phrase = phrase[:m.start()]
            break
    phrase = clean_phrase(phrase)
    if not phrase or phrase.lower() in {'orange', 'grey', 'gray'}:
        return None
    return {'phrase': phrase, 'color': color, 'annotation': raw}


def extract_color_annotations(page_text):
    spans = []
    for match in re.finditer(r'\(([^()]{3,260})\)', page_text):
        parsed = parse_annotation(match.group(1), page_text[:match.start()])
        if not parsed:
            continue
        parsed['annotationStart'] = match.start()
        parsed['annotationEnd'] = match.end()
        spans.append(parsed)
    return spans


def norm_for_match(value):
    value = value.replace('“', '"').replace('”', '"').replace('’', "'")
    value = value.replace('—', '-').replace('–', '-')
    value = re.sub(r'\\([.()])', r'\1', value)
    value = re.sub(r'[^a-z0-9%$]+', ' ', value.lower())
    return re.sub(r'\s+', ' ', value).strip()


def model_words_by_page(model):
    return OrderedDict((pid, page['words']) for pid, page in model['pages'].items())


def find_phrase_words(words, phrase):
    phrase_tokens = norm_for_match(phrase).split()
    if not phrase_tokens:
        return []
    expanded = []
    for word in words:
        for token in norm_for_match(word['letters'] or word['text']).split():
            expanded.append((token, word))
    tokens = [token for token, _ in expanded]
    hits = []
    for i in range(0, len(tokens) - len(phrase_tokens) + 1):
        if tokens[i:i + len(phrase_tokens)] == phrase_tokens:
            seen = OrderedDict()
            for _, word in expanded[i:i + len(phrase_tokens)]:
                seen[word['wordIndex']] = word
            hits.append(list(seen.values()))
    return hits


def stream_for_words(words):
    return {
        'text': ' '.join(word['text'] for word in words),
        'partialBold': ''.join(word['boldLetters'] for word in words if word['partialBold']),
        'anyBold': ''.join(word['boldLetters'] for word in words if word['hasBold']),
        'firstLetters': ''.join((word['letters'] or word['text'])[:1] for word in words),
        'lastLetters': ''.join((word['letters'] or word['text'])[-1:] for word in words),
        'wordIndexes': [word['wordIndex'] for word in words],
    }


def main():
    model = json.loads(MODEL_JSON.read_text())
    annotated_pages = split_annotated_pages(ANNOTATED.read_text())
    words_by_page = model_words_by_page(model)

    rows = []
    for pid, page in annotated_pages.items():
        for span in extract_color_annotations(page['text']):
            hits = find_phrase_words(words_by_page.get(pid, []), span['phrase'])
            row = {
                'pid': pid,
                'articlePage': page['articlePage'],
                **span,
                'matchCount': len(hits),
            }
            if hits:
                row.update(stream_for_words(hits[0]))
            else:
                row.update({'text': '', 'partialBold': '', 'anyBold': '', 'firstLetters': '', 'lastLetters': '', 'wordIndexes': []})
            rows.append(row)

    by_color = OrderedDict()
    for color in ['orange', 'grey']:
        color_rows = [row for row in rows if row['color'] == color and row['matchCount']]
        by_color[color] = {
            'spanCount': len(color_rows),
            'fullTextFirstLetters': ''.join(row['firstLetters'] for row in color_rows),
            'fullTextLastLetters': ''.join(row['lastLetters'] for row in color_rows),
            'anyBold': ''.join(row['anyBold'] for row in color_rows),
            'partialBold': ''.join(row['partialBold'] for row in color_rows),
            'page76AnyBold': ''.join(row['anyBold'] for row in color_rows if row['articlePage'] == 76),
            'page76PartialBold': ''.join(row['partialBold'] for row in color_rows if row['articlePage'] == 76),
        }

    report = {'rows': rows, 'byColor': by_color}
    OUT_JSON.write_text(json.dumps(report, indent=2))

    lines = ['# Annotated Color Span Analysis', '']
    lines.append('Scope: parse the user-supplied natural-language annotations for orange and grey/black highlight spans, then match those phrases back to the canonical Markdown character model.')
    lines.append('')
    lines.append('## Summary')
    for color, item in by_color.items():
        lines.append(
            f"- {color}: matched-spans={item['spanCount']}, anyBoldLen={len(item['anyBold'])}, "
            f"partialBoldLen={len(item['partialBold'])}, page76AnyBoldLen={len(item['page76AnyBold'])}, "
            f"page76PartialBoldLen={len(item['page76PartialBold'])}"
        )
    unmatched = [row for row in rows if not row['matchCount']]
    lines.append(f"- unmatched color annotations: {len(unmatched)}")
    lines.append('')
    lines.append('## Matched Spans')
    for row in rows:
        status = 'matched' if row['matchCount'] else 'unmatched'
        lines.append(
            f"- {row['pid']} {row['color']} {status}: phrase=`{row['phrase']}` "
            f"partial=`{row['partialBold']}` anyBold=`{row['anyBold']}` indexes={row['wordIndexes']}"
        )
    lines.append('')
    lines.append('## Color Streams')
    for color, item in by_color.items():
        lines.append(f"### {color}")
        lines.append(f"- first letters: `{item['fullTextFirstLetters']}`")
        lines.append(f"- last letters: `{item['fullTextLastLetters']}`")
        lines.append(f"- any bold: `{item['anyBold']}`")
        lines.append(f"- partial bold: `{item['partialBold']}`")
        lines.append(f"- page76 any bold: `{item['page76AnyBold']}`")
        lines.append(f"- page76 partial bold: `{item['page76PartialBold']}`")
    lines.append('')
    lines.append('## Assessment')
    lines.append('- Color matching gives a stricter selector than bold alone, but the page-76 color intersections are still phrase-like rather than key-shaped.')
    lines.append('- Grey/black on page 76 isolates the struck Peter Schiff line plus grey-highlighted money/volcano phrases; orange isolates the public “heart/Bitcoin/buying dip/shitcoiner” phrases.')
    lines.append('- Next useful test is geometric: compare these color spans against reflected orange/black mask boxes to see which highlighted phrases are touched by the mirror, instead of hashing the color text directly.')
    OUT_MD.write_text('\n'.join(lines) + '\n')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')


if __name__ == '__main__':
    main()
