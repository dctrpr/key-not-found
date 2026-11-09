#!/usr/bin/env python3
import json
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'canonical_char_model.json'
COLOR_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'annotated_color_span_analysis.json'
GEOM_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'color_reflection_geometry.json'
OUT_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'overlapped_color_neighbors.json'
OUT_MD = ROOT / 'analysis_outputs' / '3d_article_map' / 'overlapped_color_neighbors.md'


def chunks(value, n):
    return ' '.join(value[i:i + n] for i in range(0, len(value), n))


def word_summary(word):
    if word['partialBold']:
        return f"{word['wordIndex']}:{word['text']}[{word['boldLetters']}]"
    if word['hasBold']:
        return f"{word['wordIndex']}:{word['text']}[*]"
    return f"{word['wordIndex']}:{word['text']}"


def collect_neighbor_stream(words, start, end, radius):
    lo = max(0, start - radius)
    hi = min(len(words) - 1, end + radius)
    region = words[lo:hi + 1]
    partial_words = [word for word in region if word['partialBold']]
    any_bold_words = [word for word in region if word['hasBold']]
    return {
        'radius': radius,
        'start': lo,
        'end': hi,
        'partialBold': ''.join(word['boldLetters'] for word in partial_words),
        'partialBoldReverse': ''.join(word['boldLetters'] for word in reversed(partial_words)),
        'anyBold': ''.join(word['boldLetters'] for word in any_bold_words),
        'partialWords': [word_summary(word) for word in partial_words],
        'anyBoldWords': [word_summary(word) for word in any_bold_words],
    }


def main():
    model = json.loads(MODEL_JSON.read_text())
    color = json.loads(COLOR_JSON.read_text())
    geometry = json.loads(GEOM_JSON.read_text())
    p2 = model['pages']['p2']
    words = p2['words']

    color_by_key = {
        (row['articlePage'], row['color'], row['phrase']): row
        for row in color['rows']
    }
    geom_hits = [
        row for row in geometry['rows']
        if row['articlePage'] == 76 and row['reflectionHits']
    ]

    rows = []
    for grow in geom_hits:
        crow = color_by_key.get((grow['articlePage'], grow['color'], grow['phrase']))
        if crow and crow.get('wordIndexes'):
            indexes = crow['wordIndexes']
            start = min(indexes)
            end = max(indexes)
            source = 'canonical-color-indexes'
        else:
            # Fall back to OCR geometry match only; these rows are useful but
            # cannot yet supply exact corrected-text word indexes.
            rows.append({
                'phrase': grow['phrase'],
                'color': grow['color'],
                'source': 'geometry-only-no-canonical-index',
                'bestReflection': grow['reflectionHits'][0]['id'],
                'windows': [],
            })
            continue
        windows = [collect_neighbor_stream(words, start, end, radius) for radius in (5, 10, 20, 40)]
        rows.append({
            'phrase': grow['phrase'],
            'color': grow['color'],
            'source': source,
            'wordIndexStart': start,
            'wordIndexEnd': end,
            'bestReflection': grow['reflectionHits'][0]['id'],
            'bestOverlapVsSpan': grow['reflectionHits'][0]['overlapVsSpan'],
            'windows': windows,
        })

    combined = OrderedDict()
    for radius in (5, 10, 20, 40):
        normal = ''.join(
            window['partialBold']
            for row in rows
            for window in row['windows']
            if window['radius'] == radius
        )
        reverse_each = ''.join(
            window['partialBoldReverse']
            for row in rows
            for window in row['windows']
            if window['radius'] == radius
        )
        combined[str(radius)] = {'normal': normal, 'reverseEachWindow': reverse_each}

    OUT_JSON.write_text(json.dumps({'rows': rows, 'combined': combined}, indent=2))

    lines = ['# Overlapped Color Neighbor Analysis', '']
    lines.append('Scope: for page-76 color spans touched by reflected boxes, collect only nearby partial-bold letters from the corrected transcript.')
    lines.append('')
    lines.append('## Span Windows')
    for row in rows:
        lines.append(f"- {row['color']} `{row['phrase']}` via {row['bestReflection']} source={row['source']}")
        for window in row['windows']:
            lines.append(
                f"  - radius {window['radius']}: partial=`{window['partialBold']}` "
                f"reverse=`{window['partialBoldReverse']}` words={window['partialWords']}"
            )
    lines.append('')
    lines.append('## Combined Streams By Radius')
    for radius, item in combined.items():
        lines.append(f"- radius {radius} normal len={len(item['normal'])}: `{chunks(item['normal'], 5)}`")
        lines.append(f"- radius {radius} reverse-each len={len(item['reverseEachWindow'])}: `{chunks(item['reverseEachWindow'], 5)}`")
    lines.append('')
    lines.append('## Assessment')
    lines.append('- Restricting to reflected-overlapped color spans greatly reduces the page-76 partial-bold stream, but the resulting windows still do not read as an instruction.')
    lines.append('- The most stable nearby partial fragments remain `eelibeippedelbe`, `lvd`, and small fragments around Mike/Novogratz/trust-guy when the radius is widened.')
    lines.append('- This keeps the branch alive as an ordering/registration clue, but not as a solved selector. The next best discriminator is source/layout: verify whether the exact same reflected overlaps survive on the high-res physical spread after affine registration.')
    OUT_MD.write_text('\n'.join(lines) + '\n')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')


if __name__ == '__main__':
    main()
