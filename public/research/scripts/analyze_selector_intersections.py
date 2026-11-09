#!/usr/bin/env python3
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'canonical_char_model.json'
MAP_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'article_3d_map_data.json'
OUT_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'selector_intersection_analysis.json'
OUT_MD = ROOT / 'analysis_outputs' / '3d_article_map' / 'selector_intersection_analysis.md'

TARGET_TERMS = {
    'el', 'salvador', 'president', 'nayib', 'bukele', 'imf', 'loan', 'volcanoes',
    'volcano', 'bonds', 'bond', 'buying', 'dip', 'mike', 'novogratz', 'shitcoiner',
    'heart', 'twitter', 'mine', 'bitcoin',
}
PAGE76_PHRASE_TERMS = [
    ['el', 'salvador'],
    ['president', 'nayib', 'bukele'],
    ['buying', 'the', 'dip'],
    ['imf', 'loan'],
    ['volcano', 'bonds'],
    ['shitcoiner', 'at', 'heart'],
]


def clean_token(value):
    return re.sub(r'[^a-z0-9]+', '', value.lower())


def chunks(value, n):
    return ' '.join(value[i:i + n] for i in range(0, len(value), n))


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


def load_pages():
    model = json.loads(MODEL_JSON.read_text())
    pages = OrderedDict((pid, page) for pid, page in model['pages'].items())
    return model, pages


def page_by_article(pages, article_page):
    for page in pages.values():
        if page['articlePage'] == article_page:
            return page
    return None


def word_tokens(words):
    return [clean_token(word['letters'] or word['text']) for word in words]


def find_phrase(words, phrase_terms):
    tokens = word_tokens(words)
    phrase = [clean_token(term) for term in phrase_terms]
    hits = []
    for i in range(0, len(tokens) - len(phrase) + 1):
        if tokens[i:i + len(phrase)] == phrase:
            hits.append(words[i:i + len(phrase)])
    return hits


def stream_for_words(words):
    return {
        'text': ' '.join(word['text'] for word in words),
        'partialBold': ''.join(word['boldLetters'] for word in words if word['partialBold']),
        'anyBold': ''.join(word['boldLetters'] for word in words if word['hasBold']),
        'firstLetters': ''.join((word['letters'] or word['text'])[:1] for word in words),
        'lastLetters': ''.join((word['letters'] or word['text'])[-1:] for word in words),
        'lengths': ''.join(str(len(word['letters'] or word['text']) % 10) for word in words),
        'wordIndexes': [word['wordIndex'] for word in words],
    }


def greedy_match_selection(page_words, selection_text):
    wanted = [clean_token(token) for token in re.findall(r"[A-Za-z0-9%$’']+", selection_text)]
    wanted = [token for token in wanted if token]
    tokens = word_tokens(page_words)
    matches = []
    pos = 0
    for want in wanted:
        found = None
        for i in range(pos, len(tokens)):
            token = tokens[i]
            if token == want:
                found = i
                break
            if len(want) >= 5 and len(token) >= 5 and (want in token or token in want):
                found = i
                break
        if found is not None:
            matches.append(page_words[found])
            pos = found + 1
    return matches, wanted


def sequence_variants(label, stream):
    variants = OrderedDict()
    if not stream:
        return variants
    variants[f'{label}:raw'] = stream
    variants[f'{label}:reverse'] = stream[::-1]
    variants[f'{label}:atbash'] = atbash(stream)
    for shift in (1, 3, 5, 13, 21, 23, 25):
        variants[f'{label}:caesar{shift}'] = caesar(stream.lower(), shift)
    return variants


def score_text(value):
    lower = value.lower()
    vowels = sum(ch in 'aeiou' for ch in lower)
    letters = sum(ch.isalpha() for ch in lower)
    common = sum(lower.count(word) for word in ['the', 'and', 'you', 'key', 'use', 'left', 'right', 'mirror', 'page', 'take', 'read'])
    base58ish = bool(re.fullmatch(r'[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{20,60}', value))
    hexish = bool(re.fullmatch(r'[0-9a-fA-F]{32,66}', value))
    return {
        'letters': letters,
        'vowelRatio': round(vowels / letters, 3) if letters else 0,
        'commonWordScore': common,
        'base58ish': base58ish,
        'hexish': hexish,
    }


def bimanual_pairs(pages):
    page_streams = {pid: page['streams']['partialBoldLetters'] for pid, page in pages.items()}
    pairs = [('p1', 'p5'), ('p2', 'p4')]
    rows = []
    for left, right in pairs:
        a = page_streams.get(left, '')
        b = page_streams.get(right, '')
        for mode, bb in [('normal', b), ('right_reversed', b[::-1])]:
            interleave = ''.join(x + y for x, y in zip(a, bb))
            leftover = a[len(bb):] if len(a) > len(bb) else bb[len(a):]
            rows.append({
                'label': f'{left}+{right}:{mode}:interleave',
                'stream': interleave + leftover,
                'aLength': len(a),
                'bLength': len(b),
            })
    center = page_streams.get('p3', '')
    rows.append({'label': 'p3:center_page', 'stream': center, 'aLength': len(center), 'bLength': 0})
    return rows


def number_index_tests(streams):
    numbers = [20, 24, 75, 76, 77, 78, 79, 80, 2008, 51, 95, 42, 100000, 2017, 12000, 85, 2, 10]
    rows = []
    for label, stream in streams.items():
        if not stream:
            continue
        for mode in ['mod1', 'mod0']:
            chars = []
            positions = []
            for n in numbers:
                if mode == 'mod1':
                    idx = (n - 1) % len(stream)
                else:
                    idx = n % len(stream)
                chars.append(stream[idx])
                positions.append(idx)
            rows.append({
                'label': f'{label}:{mode}:canonical_numbers',
                'stream': ''.join(chars),
                'positions': positions,
                'numbers': numbers,
                'score': score_text(''.join(chars)),
            })
    return rows


def main():
    model, pages = load_pages()
    map_data = json.loads(MAP_JSON.read_text())
    page76 = page_by_article(pages, 76)
    if page76 is None:
        raise SystemExit('no page 76 model')

    target_words = [word for word in page76['words'] if clean_token(word['letters'] or word['text']) in TARGET_TERMS]
    target_stream = stream_for_words(target_words)

    phrase_hits = []
    for terms in PAGE76_PHRASE_TERMS:
        for words in find_phrase(page76['words'], terms):
            phrase_hits.append({'terms': terms, **stream_for_words(words)})

    ray_rows = []
    for selection in map_data.get('raySelections', [])[:40]:
        matches, wanted = greedy_match_selection(page76['words'], selection['text'])
        row = {
            'rank': selection.get('rank'),
            'selector': f"{selection.get('a')}->{selection.get('b')}:{selection.get('mode')}:{selection.get('threshold')}:{selection.get('order')}",
            'sourceText': selection['text'],
            'wantedTokens': wanted,
            'matchCount': len(matches),
            'matchRatio': round(len(matches) / max(1, len(wanted)), 3),
            **stream_for_words(matches),
        }
        ray_rows.append(row)

    reflected_rows = []
    for reflection in map_data.get('reflections', []):
        target_page = page_by_article(pages, reflection.get('target'))
        if not target_page:
            continue
        matches, wanted = greedy_match_selection(target_page['words'], reflection.get('text', ''))
        reflected_rows.append({
            'id': reflection.get('id'),
            'source': reflection.get('source'),
            'target': reflection.get('target'),
            'sourceText': reflection.get('text', ''),
            'wantedTokens': wanted,
            'matchCount': len(matches),
            'matchRatio': round(len(matches) / max(1, len(wanted)), 3),
            **stream_for_words(matches),
        })

    partial_by_page = {pid: page['streams']['partialBoldLetters'] for pid, page in pages.items()}
    bimanual_rows = bimanual_pairs(pages)
    number_rows = number_index_tests({
        'all_partial': model['streams']['partialBoldLetters'],
        'page76_partial': page76['streams']['partialBoldLetters'],
        'page76_target_any_bold': target_stream['anyBold'],
    })

    interesting_variants = []
    for label, stream in [
        ('page76_target_partial', target_stream['partialBold']),
        ('page76_target_any_bold', target_stream['anyBold']),
        ('phrase_hits_any_bold', ''.join(row['anyBold'] for row in phrase_hits)),
        ('rays_any_bold_top10', ''.join(row['anyBold'] for row in ray_rows[:10])),
        ('rays_partial_top10', ''.join(row['partialBold'] for row in ray_rows[:10])),
        ('reflections_partial', ''.join(row['partialBold'] for row in reflected_rows)),
    ]:
        for variant_label, value in sequence_variants(label, stream).items():
            interesting_variants.append({'label': variant_label, 'stream': value, 'score': score_text(value)})

    report = {
        'targetWords': target_stream,
        'phraseHits': phrase_hits,
        'rayIntersections': ray_rows,
        'reflectedIntersections': reflected_rows,
        'partialByPage': partial_by_page,
        'bimanualRows': bimanual_rows,
        'numberIndexRows': number_rows,
        'variantDiagnostics': interesting_variants,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2))

    lines = ['# Selector Intersection Analysis', '']
    lines.append('Scope: use the corrected character model as the text layer, then intersect it with page-76 target terms, ray selections, reflected selections, page-pair mirror order, and canonical puzzle numbers.')
    lines.append('')
    lines.append('## Page 76 Target-Term Intersection')
    lines.append(f"- matched target words: {len(target_words)}")
    lines.append(f"- text: `{target_stream['text']}`")
    lines.append(f"- partial-bold letters only: `{target_stream['partialBold']}`")
    lines.append(f"- any-bold letters: `{target_stream['anyBold']}`")
    lines.append(f"- first letters: `{target_stream['firstLetters']}`")
    lines.append(f"- word lengths mod 10: `{target_stream['lengths']}`")
    lines.append('')
    lines.append('## Page 76 Named Phrase Hits')
    for row in phrase_hits:
        lines.append(
            f"- {' '.join(row['terms'])}: text=`{row['text']}` partial=`{row['partialBold']}` anyBold=`{row['anyBold']}` "
            f"indexes={row['wordIndexes']}"
        )
    lines.append('')
    lines.append('## Top Ray Intersections Onto Corrected Page 76')
    for row in ray_rows[:15]:
        lines.append(
            f"- rank {row['rank']} match={row['matchCount']}/{len(row['wantedTokens'])} selector={row['selector']} "
            f"partial=`{row['partialBold']}` anyBold=`{row['anyBold']}` text=`{row['text']}`"
        )
    lines.append('')
    lines.append('## Reflected Selection Markup Intersections')
    for row in reflected_rows[:20]:
        if row['partialBold'] or row['anyBold']:
            lines.append(
                f"- {row['id']} {row['source']}->{row['target']} match={row['matchCount']}/{len(row['wantedTokens'])} "
                f"partial=`{row['partialBold']}` anyBold=`{row['anyBold']}` text=`{row['text'][:140]}`"
            )
    lines.append('')
    lines.append('## Bimanual Mirror-Pair Streams')
    for row in bimanual_rows:
        stream = row['stream']
        lines.append(f"- {row['label']}: len={len(stream)} chunks5=`{chunks(stream, 5)}`")
    lines.append('')
    lines.append('## Canonical Number Index Tests')
    for row in number_rows:
        lines.append(f"- {row['label']}: `{row['stream']}` positions={row['positions']} score={row['score']}")
    lines.append('')
    lines.append('## Variant Diagnostics')
    for row in interesting_variants:
        score = row['score']
        if score['commonWordScore'] or score['base58ish'] or score['hexish'] or 0.28 <= score['vowelRatio'] <= 0.48:
            lines.append(f"- {row['label']}: `{chunks(row['stream'], 5)}` score={score}")
    if not any(row['score']['base58ish'] or row['score']['hexish'] for row in interesting_variants):
        lines.append('- No intersection stream produced an obvious WIF/Base58/private-key-shaped or hex-shaped string.')
    lines.append('')
    lines.append('## Assessment')
    lines.append('- The page-76 target-term intersection is coherent but still not readable as an instruction or direct key.')
    lines.append('- The strongest ray intersection remains the Bukele/El Salvador/IMF/volcano region; after exact transcript matching it mostly selects all-bold phrase words rather than hidden partial-bold letters.')
    lines.append('- Bimanual page-pair interleaves did not produce readable text under normal/reverse pairing.')
    lines.append('- Next higher-value step: add color flags from the original annotated transcript or visual masks, then test bold ∩ orange/reflected-orange and bold ∩ grey/black as stricter selectors.')
    OUT_MD.write_text('\n'.join(lines) + '\n')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')


if __name__ == '__main__':
    main()
