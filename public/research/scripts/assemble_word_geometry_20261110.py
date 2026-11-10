#!/usr/bin/env python3
"""Fixed source-only second-pass preparation and frozen word-model assembly.

No mirror masks, target text selection, candidate/key checks or network requests.
OCR observations remain local. An existing output is never overwritten.
"""
import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

from align_word_geometry_20261110 import norm, tables, upright_polygon

SECOND_PASS_ROWS = (
    'p75r17', 'p75r23', 'p76r05', 'p76r07', 'p76r14', 'p76r20',
    'p77r01', 'p77r06', 'p77r24', 'p77r25', 'p77r28', 'p78r07',
    'p78r16', 'p78r18', 'p79r01', 'p79r04', 'p79r06', 'p79r07',
)
VIEWS = ('gray-autocontrast-2x', 'black-ink-110-2x', 'white-ink-175-2x')
PLATE_SHA = '2704a672e1b07d9ec3fd262d7229dd81202cfd17503bdb2fd373fb1ab9550882'
ADJUDICATION_SHA = '0c06a877c46f98fe3b962dedf278d9993b95b35123cf88688b66b0c36cc7b1cc'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def save(path, data):
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def prepare_second_pass(first, output):
    from PIL import Image, ImageOps

    source = read(first / 'row-crops.json')
    by_id = {row['id']: row for row in source['rows']}
    require(all(row in by_id for row in SECOND_PASS_ROWS), 'Canonical second-pass row missing')
    output.mkdir(parents=True, exist_ok=False)
    (output / 'crops').mkdir()
    frames = {}
    rows, jobs = [], []
    for row_id in SECOND_PASS_ROWS:
        original = by_id[row_id]
        angle, page = original['rotationCCWDegrees'], original['page']
        frame_name = f'p{page}-ccw{angle:g}.png' if angle else f'p{page}-upright.png'
        if frame_name not in frames:
            frames[frame_name] = Image.open(first / 'frames' / frame_name).convert('RGB')
        x0, y0, x1, y1 = original['locator']
        crop_box = [max(0, x0 - 60), max(0, y0 - 18), min(2544, x1 + 60), min(3264, y1 + 18)]
        gray = frames[frame_name].crop(crop_box).convert('L')
        images = (
            ImageOps.autocontrast(gray, cutoff=1),
            gray.point(lambda value: 0 if value < 110 else 255),
            gray.point(lambda value: 0 if value > 175 else 255),
        )
        for view, image in zip(VIEWS, images):
            identifier = row_id + '-' + view
            relative = 'crops/' + identifier + '.png'
            image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS).save(output / relative)
            record = {key: copy.deepcopy(original[key]) for key in (
                'page', 'canonicalText', 'canonicalTokens', 'rotationCCWDegrees', 'coordinateSpace', 'locator'
            )}
            record.update(id=identifier, canonicalRowId=row_id, cropBox=crop_box,
                          cropPath=relative, sourceView=view, resampleScale=2, sourcePreflightOnly=True)
            rows.append(record)
            jobs.append(dict(id=identifier, path=relative, mode='ocr'))
    metadata = {key: copy.deepcopy(source[key]) for key in (
        'sourcePdf', 'sourcePdfSha256', 'canonicalRows', 'canonicalRowsSha256', 'sourceImages'
    )}
    metadata['rows'] = rows
    save(output / 'row-crops.json', metadata)
    save(output / 'jobs.json', dict(jobs=jobs))
    print(json.dumps(dict(preparedRows=len(rows), canonicalRows=len(SECOND_PASS_ROWS), targetKeyChecks=0)))


def score(row):
    alignment = row['alignment']
    return (alignment['verifiedLexicalTokenCount'], -alignment['editDistance'], alignment['verifiedTokenCount'])


def assemble(first, second, corpus, output):
    baseline = read(first / 'word-geometry-dedup.json')
    variants = read(second / 'word-geometry-dedup.json')
    adjudication_path = corpus / 'sources/word-geometry-adjudications-20261110.json'
    plate = corpus / 'sources/word-geometry-review-20261110.png'
    require(sha(plate.read_bytes()) == PLATE_SHA, 'Frozen source review plate differs')
    require(sha(adjudication_path.read_bytes()) == ADJUDICATION_SHA, 'Frozen source adjudications differ')
    adjudications = read(adjudication_path)['adjudications']
    require(len(adjudications) == 7, 'Expected seven frozen source adjudications')
    decisions = {item['wordId']: item for item in adjudications}
    pools = {row['id']: [('pass1', 'original-rgb', row)] for row in baseline['rows']}
    for row in variants['rows']:
        pools[row['canonicalRowId']].append(('pass2', row['sourceView'], row))
    result = {key: copy.deepcopy(value) for key, value in baseline.items() if key not in ('stats', 'rows')}
    rows, applied = [], set()
    for original in baseline['rows']:
        row_id = original['id']
        options = pools[row_id]
        # max() keeps the first equal-scoring choice: original, gray, black, white.
        selected_pass, view, chosen = max(options, key=lambda entry: score(entry[2]))
        row = copy.deepcopy(chosen)
        row['id'] = row_id
        row['selectedSourceView'] = view
        row['sourceCropPath'] = selected_pass + '/' + chosen['cropPath']
        row['sourceCropSha256'] = sha(((first if selected_pass == 'pass1' else second) / chosen['cropPath']).read_bytes())
        row['sourceVariantScores'] = [dict(
            **{'pass': name}, view=label,
            verifiedLexicalTokens=record['alignment']['verifiedLexicalTokenCount'],
            editDistance=record['alignment']['editDistance'], verifiedTokens=record['alignment']['verifiedTokenCount'],
        ) for name, label, record in options]
        for index, word in enumerate(row['words']):
            word['id'] = f'{row_id}w{index + 1:02d}'
            decision = decisions.get(word['id'])
            if decision is None:
                continue
            require(not word['verified'], 'Adjudicated token unexpectedly machine-resolved; new review required')
            observed = row['deduplicatedRawWords']
            canonical_norm = [norm(token) for token in row['canonicalTokens']]
            observed_norm = [norm(token['text']) for token in observed]
            forward, backward = tables(canonical_norm, observed_norm)
            cost = forward[len(canonical_norm)][len(observed_norm)]
            substitutions = [item for j, item in enumerate(observed)
                             if canonical_norm[index] != observed_norm[j]
                             and forward[index][j] + 1 + backward[index + 1][j + 1] == cost]
            require(len(substitutions) == 1 and not word['couldBeDeletedInOptimalAlignment'],
                    'Visual decision no longer has a unique source span; new review required')
            raw = substitutions[0]
            require(word['text'] == decision['canonicalText'] and raw['text'] == decision['observedText']
                    and raw['id'] == decision['rawOCRWordId'] and raw['box'] == decision['box'],
                    'Frozen visual decision does not match regenerated OCR span; new review required')
            box = copy.deepcopy(raw['box'])
            word.update(box=box, center=[(box[0] + box[2]) / 2, (box[1] + box[3]) / 2],
                        originalUprightPolygon=upright_polygon(box, row['rotationCCWDegrees']), verified=True,
                        verifiedBy='Codex visual source-pixel review: canonical word and unique observed substitution bbox agree; raw OCR retained',
                        visualSourceReviewed=True, humanVerified=False,
                        mappingStatus='visually-adjudicated-unique-token-substitution', rawOCRWordId=raw['id'],
                        rawOCRText=raw['text'], confidence=raw['confidence'], punctuationOrCaseDifference=True,
                        centerUncertaintyPx=3, reviewAdjudicationId=decision['id'], reviewPlateSha256=PLATE_SHA)
            applied.add(word['id'])
        lexical, punctuation = [], []
        for index, word in enumerate(row['words']):
            if any(character.isalnum() for character in word['text']):
                word['canonicalTokenIndex'] = index
                word['lexicalWordIndex'] = len(lexical)
                lexical.append(word)
            else:
                punctuation.append(word)
        row['words'] = lexical
        row['punctuationOnlyTokens'] = punctuation
        require(all(word['verified'] and word['box'] and all(math.isfinite(value) for value in word['box']) for word in lexical),
                'Unresolved lexical source geometry; new review required')
        require(all(a['center'][0] < b['center'][0] for a, b in zip(lexical, lexical[1:])), 'Word centers are not monotonic')
        row['status'], row['lexicallyComplete'] = 'complete', True
        row['statusMeaning'] = 'All canonical lexical words have source-backed geometry; standalone punctuation is preserved separately and is not a word unit.'
        rows.append(row)
    require(applied == set(decisions), 'Not all frozen source adjudications were applied')
    lexical_count = sum(len(row['words']) for row in rows)
    punctuation_count = sum(len(row['punctuationOnlyTokens']) for row in rows)
    require((len(rows), lexical_count, punctuation_count) == (142, 1243, 15), 'Frozen source coverage differs')
    result['verifiedMeaning'] = 'Unique machine normalized-token equality + observed Vision bbox, or one of seven explicit visual source-pixel adjudications. Does not assert human verification or glyph-tight font metrics.'
    result['stats'] = dict(rows=142, lexicallyCompleteRows=142, canonicalWhitespaceTokens=1258,
                           lexicalWords=1243, verifiedLexicalWords=1243, standalonePunctuationTokensPreserved=15,
                           visualAdjudications=7, machineOnlyLexicalWords=1236, targetSelections=0, keyChecks=0)
    result['rows'] = rows
    result['selectionRule'] = 'For18 originallylexicallyambiguous rows, compare originalRGB,grayautocontrast2x,blackinkL<1102x,whiteinkL>1752x; maximize exactnormalizedlexicalmatches, thenminimizeeditdistance, thenmaximizealltokenmatches. StabletieprefersoriginalRGB. No target masks, keystrings or decoding consulted.'
    result['lexicalWordDefinition'] = 'Canonical whitespace token containing at least one Unicode letter or digit. Exact canonical token text including attached punctuation is retained. Standalone punctuation tokens are preserved under punctuationOnlyTokens and canonicalTokens, outside the lexical word unit.'
    result['reviewEvidence'] = dict(path='sources/word-geometry-review-20261110.png', sha256=PLATE_SHA,
                                   adjudications='sources/word-geometry-adjudications-20261110.json',
                                   reviewRecordedAtUTC=adjudications[0]['recordedAtUTC'], reviewedSubstitutions=7)
    result.update(sourcePreflightOnly=True, targetSelectionsExecuted=False, keyChecksExecuted=False)
    save(output, result)
    print(json.dumps(dict(rows=142, lexicalWords=1243, visualAdjudications=7, targetKeyChecks=0,
                          sha256=sha(output.read_bytes()))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-second-pass', action='store_true')
    parser.add_argument('--first', type=Path, required=True)
    parser.add_argument('--second', type=Path)
    parser.add_argument('--corpus', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.prepare_second_pass:
        prepare_second_pass(args.first, args.out)
    else:
        require(args.second is not None, 'Assembly requires both OCR passes')
        assemble(args.first, args.second, args.corpus, args.out)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Source geometry assembly failed: ' + type(error).__name__ + '. Inspect local inputs; new source review may be required.', file=sys.stderr)
        sys.exit(1)
