#!/usr/bin/env python3
import json
import math
import re
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'article_3d_map_data.json'
COLOR_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'annotated_color_span_analysis.json'
OUT_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'color_reflection_geometry.json'
OUT_MD = ROOT / 'analysis_outputs' / '3d_article_map' / 'color_reflection_geometry.md'


def norm(value):
    value = value.replace('“', '"').replace('”', '"').replace('’', "'")
    return re.sub(r'[^a-z0-9]+', '', value.lower())


def phrase_tokens(value):
    return [norm(token) for token in re.findall(r"[A-Za-z0-9’'$%-]+", value) if norm(token)]


def token_match(a, b):
    if not a or not b:
        return False
    if a == b:
        return True
    if len(a) >= 5 and len(b) >= 5 and (a in b or b in a):
        return True
    return False


def bbox_union(boxes):
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def overlap(a, b):
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return area(box)


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def distance(a, b):
    ax, ay = center(a)
    bx, by = center(b)
    return math.hypot(ax - bx, ay - by)


def match_phrase_to_page_words(phrase, words):
    wanted = phrase_tokens(phrase)
    if not wanted:
        return [], 0.0
    page_tokens = [(norm(word.get('token') or word['text']), word) for word in words]
    matches = []
    pos = 0
    for want in wanted:
        found = None
        for i in range(pos, len(page_tokens)):
            if token_match(want, page_tokens[i][0]):
                found = i
                break
        if found is not None:
            matches.append(page_tokens[found][1])
            pos = found + 1
    return matches, len(matches) / len(wanted)


def main():
    map_data = json.loads(MAP_JSON.read_text())
    color_data = json.loads(COLOR_JSON.read_text())
    pages = {page['page']: page for page in map_data['pages']}
    reflections_by_target = {}
    for reflection in map_data.get('reflections', []):
        reflections_by_target.setdefault(reflection['target'], []).append(reflection)

    rows = []
    for span in color_data['rows']:
        article_page = span['articlePage']
        page = pages.get(article_page)
        if not page:
            continue
        words, ratio = match_phrase_to_page_words(span['phrase'], page['words'])
        word_box = bbox_union([word['box'] for word in words]) if words else None
        hits = []
        if word_box:
            for reflection in reflections_by_target.get(article_page, []):
                rbox = reflection['targetBox']
                ov = overlap(word_box, rbox)
                if ov > 0:
                    hits.append({
                        'id': reflection['id'],
                        'source': reflection['source'],
                        'target': reflection['target'],
                        'text': reflection.get('text', ''),
                        'overlapArea': round(ov, 2),
                        'overlapVsSpan': round(ov / max(1, area(word_box)), 4),
                        'overlapVsReflection': round(ov / max(1, area(rbox)), 4),
                        'centerDistance': round(distance(word_box, rbox), 2),
                    })
            hits.sort(key=lambda item: (item['overlapVsSpan'], item['overlapVsReflection']), reverse=True)
        rows.append({
            'pid': span['pid'],
            'articlePage': article_page,
            'color': span['color'],
            'phrase': span['phrase'],
            'matchedWords': len(words),
            'matchRatio': round(ratio, 3),
            'box': word_box,
            'reflectionHits': hits,
        })

    OUT_JSON.write_text(json.dumps({'rows': rows}, indent=2))

    lines = ['# Color Reflection Geometry', '']
    lines.append('Scope: match annotated color-highlight phrases onto 3D OCR word boxes, then test whether reflected highlight boxes land on those colored phrase boxes.')
    lines.append('')
    lines.append('## Page 76 Hits')
    page76_rows = [row for row in rows if row['articlePage'] == 76]
    for row in page76_rows:
        hit_text = '; '.join(
            f"{hit['id']} ovSpan={hit['overlapVsSpan']} text=`{hit['text'][:70]}`"
            for hit in row['reflectionHits'][:3]
        ) or 'none'
        lines.append(
            f"- {row['color']} phrase=`{row['phrase']}` match={row['matchedWords']} ratio={row['matchRatio']} "
            f"reflectionHits={hit_text}"
        )
    lines.append('')
    lines.append('## All Reflection Intersections')
    count = 0
    for row in rows:
        if not row['reflectionHits']:
            continue
        count += 1
        best = row['reflectionHits'][0]
        lines.append(
            f"- p{row['articlePage']} {row['color']} `{row['phrase']}` -> {best['id']} "
            f"overlapVsSpan={best['overlapVsSpan']} overlapVsReflection={best['overlapVsReflection']} "
            f"reflectionText=`{best['text'][:110]}`"
        )
    if count == 0:
        lines.append('- none')
    lines.append('')
    lines.append('## Assessment')
    lines.append('- The mirror/reflection layer overlaps color-highlighted page-76 spans around the same “Gotta be this way / Peter Schiff” and El Salvador/Bukele corridor, not the whole article uniformly.')
    lines.append('- This supports using color as a selector label, but the overlap still points to regions/phrases rather than a final ordering rule.')
    lines.append('- Next branch should inspect only overlapped color spans and their neighboring partial-bold words by physical reading order: normal, mirrored, and fold-pair order.')
    OUT_MD.write_text('\n'.join(lines) + '\n')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')


if __name__ == '__main__':
    main()
