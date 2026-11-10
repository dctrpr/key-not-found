#!/usr/bin/env python3
"""Private-first independent Issue27 stride12 saved-output checker.

Import and --self-test never open target source/tokens/readings/results. Only
explicit --verify performs target replay after root's public registration.
No primary runner or shared batch20 scanner import. Four-format validation is
delegated only to the separately reviewed, byte-pinned independent calculator.
No network, Git, key/address derivation, token locators or raw text in output.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
EVALUATOR_SHA256 = '97cace8ee5f9b2707cc1344c08e46e068db327edc504a8625fb825481261422b'
POLICY_SHA256 = '5c6d4a7b406f99515b1bb16c7f7874df6444c64c3be2e6a32c0798ac08e0d1e5'
BODY_RELATIVE = 'analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json'
BODY_SHA256 = '783cc6676edf9b135d1eeff04d8bf8636088c1334f9e983f0d9f07dc579bff27'
SELF_RELATIVE = 'scripts/verify_issue27_stride12.py'
EVALUATOR_RELATIVE = 'scripts/verify_issue27_saved.py'
POLICY_RELATIVE = 'analysis_outputs/continuation_20261110/issue27_stride12/POLICY_PROPOSAL.json'
SCRIPT_PATHS = ('scripts/issue27_stride12.py', 'scripts/batch20_common.py', SELF_RELATIVE, EVALUATOR_RELATIVE)
EXPECTED_SOURCE_HASHES = {
    BODY_RELATIVE: BODY_SHA256,
    POLICY_RELATIVE: POLICY_SHA256,
    'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json':
        'f5f441345ebe411ee769cdcb624c0717a2b4f790b7eadc50d10dc12d37da07bb',
    'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_01.jpg':
        'd4cca9f4326ba21a959551e8537596846bccdea42efe37f463506cd2d423fb8c',
    'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_02.jpg':
        'e18e02e521444c9ea760c6e1d80a39bbee08d65a7839e970629ab81b4fd83610',
    'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_03.jpg':
        'b7f120860b1a76aa6ba97c836bb56388477ee8878665d75414098f9b8a38a1b5',
    'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_04.jpg':
        '60da7f7ed64764e8c9bb347bce163eb2f8dc4c4ad20abbd00182bced3ad3343a',
    'scripts/batch20_support/english.txt':
        '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',
    'scripts/batch20_support/controls.json':
        'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b',
}
ASCII_SPACE = frozenset(' \t\r\n\f\v')
WRAPPERS = frozenset('!"\'(),.:;?[]{}‘’“”')
PROJECTIONS = ('words', 'initials', 'finals')
DIRECTIONS = ('forward', 'reverse')
UNCERTAIN_ROWS = {'p4:col1_top:2': 'l', 'p4:col1_top:3': 'e', 'p4:col1_top:4': 's'}
MAX_TOKENS = 5000
MAX_READINGS = 72
MAX_FORMS = 144
MAX_CHARACTERS = 250000


def require(condition):
    if not condition:
        raise ValueError('Independent validation failed')


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value)
        value[key] = item
    return value


def exact_equal(left, right):
    # Canonical byte comparison preserves every string/codepoint and JSON type;
    # object key insertion order alone is not a semantic schema difference.
    return json.dumps(left, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('ascii') == \
        json.dumps(right, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('ascii')


def read_bytes(file, limit):
    require(file.is_file() and file.stat().st_size <= limit)
    with file.open('rb') as handle:
        value = handle.read(limit + 1)
    require(len(value) <= limit)
    return value


def private_path(argument, existing=False):
    file = Path(argument).expanduser().resolve()
    require(not any(part.lower() == 'public' for part in file.parts))
    if existing:
        require(file.is_file() and file.stat().st_mode & 0o077 == 0)
    return file


def evaluator_path():
    local = Path(__file__).resolve().parent / 'verify_issue27_saved.py'
    if local.is_file():
        return local
    return Path(__file__).resolve().parents[3] / 'site/public/research/scripts/verify_issue27_saved.py'


def load_evaluator():
    file = evaluator_path()
    require(hashlib.sha256(read_bytes(file, 100000)).hexdigest() == EVALUATOR_SHA256)
    spec = importlib.util.spec_from_file_location('_pinned_independent_issue27_evaluator', file)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.FORMATS == ('wif', 'minikey', 'hex64', 'bip39'))
    return module


def contains_ascii_alnum(text):
    return any('A' <= char <= 'Z' or 'a' <= char <= 'z' or '0' <= char <= '9' for char in text)


def literal_chunks(text):
    # Independent manual boundary walk: Unicode whitespace outside these six
    # characters remains inside a chunk, exactly as the registered model says.
    position = 0
    while position < len(text):
        while position < len(text) and text[position] in ASCII_SPACE:
            position += 1
        start = position
        while position < len(text) and text[position] not in ASCII_SPACE:
            position += 1
        chunk = text[start:position]
        if not contains_ascii_alnum(chunk):
            continue
        left, right = 0, len(chunk)
        while left < right and chunk[left] in WRAPPERS:
            left += 1
        while right > left and chunk[right - 1] in WRAPPERS:
            right -= 1
        core = chunk[left:right]
        require(bool(core))
        yield core


def tokens_from_rows(rows):
    tokens = []
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get('rowId'), str) and isinstance(row.get('modelText'), str))
        uncertain = row.get('uncertainForProjections')
        indices = row.get('uncertainTokenIndices')
        require(isinstance(uncertain, list) and uncertain in ([], ['words', 'initials']))
        require(isinstance(indices, list) and all(type(index) is int and index >= 0 for index in indices))
        require(len(set(indices)) == len(indices))
        require(bool(uncertain) == bool(indices))
        within = 0
        for text in literal_chunks(row['modelText']):
            tokens.append({'tokenIndex0': len(tokens), 'rowId': row['rowId'], 'withinRowIndex0': within,
                           'text': text, 'uncertainForProjections': list(uncertain) if within in indices else []})
            within += 1
            require(len(tokens) <= MAX_TOKENS)
        require(all(index < within for index in indices))
    require(sum(len(token['text']) for token in tokens) <= MAX_CHARACTERS)
    return tokens


def readings_from_tokens(tokens):
    records = []
    for direction in DIRECTIONS:
        ordered = tokens if direction == 'forward' else list(reversed(tokens))
        for phase in range(1, 13):
            selected = []
            index = phase - 1
            while index < len(ordered):
                selected.append(ordered[index])
                index += 12
            for projection in PROJECTIONS:
                affected = sum(projection in token['uncertainForProjections'] for token in selected)
                if projection == 'words':
                    text = ' '.join(token['text'] for token in selected)
                elif projection == 'initials':
                    text = ''.join(token['text'][0] for token in selected)
                else:
                    text = ''.join(token['text'][-1] for token in selected)
                records.append({'id': f'{direction}:phase{phase:02d}:{projection}', 'direction': direction,
                                'phase': phase, 'projection': projection, 'selectedTokenCount': len(selected),
                                'sourceCompleteForProjection': affected == 0,
                                'uncertainSelectedTokens': affected, 'text': text})
    require(len(records) == MAX_READINGS and sum(len(record['text']) for record in records) <= MAX_CHARACTERS)
    unique = {record['text'] for record in records}
    forms = unique | {''.join(char for char in text if not char.isspace()) for text in unique}
    require(len(forms) <= MAX_FORMS and sum(map(len, forms)) <= MAX_CHARACTERS)
    return records


def strict_known(records):
    # Whole-reading subset only. Unknown tokens are never deleted/bridged.
    return [record for record in records if record['sourceCompleteForProjection']]


def source_rows(source):
    require(isinstance(source, dict) and source.get('schemaVersion') == 1)
    rows = source.get('rows')
    require(isinstance(rows, list) and len(rows) == 312)
    require(len({row['rowId'] for row in rows}) == 312)
    require(Counter(row['printedPage'] for row in rows) == {79: 109, 80: 116, 81: 87})
    require(all(row.get('kind') == 'body' for row in rows))
    for row in rows:
        expected = row['rowId'] in UNCERTAIN_ROWS
        require(exact_equal(row.get('uncertainForProjections'), ['words', 'initials'] if expected else []))
        require(exact_equal(row.get('uncertainTokenIndices'), [0] if expected else []))
    require({row['rowId'] for row in rows if row['uncertainForProjections']} == set(UNCERTAIN_ROWS))
    return rows


def self_test():
    evaluator = load_evaluator()
    shared_independent_controls = evaluator.self_test()
    require(shared_independent_controls['status'] == 'PASS' and len(WRAPPERS) == 18)
    def row(identity, text, indices=None):
        return {'rowId': identity, 'modelText': text, 'uncertainForProjections': ['words', 'initials'] if indices else [],
                'uncertainTokenIndices': indices or []}
    literal = tokens_from_rows([row('literal1', '“c****.” U.S. exponen-'), row('literal2', 'tial. and/'),
                               row('literal3', 'or $400 can’t'), row('literal4', 'day — ‘til 12-step')])
    expected = ['c****', 'U.S', 'exponen-', 'tial', 'and/', 'or', '$400', 'can’t', 'day', 'til', '12-step']
    require([token['text'] for token in literal] == expected)
    require(''.join(token['text'][0] for token in literal) == 'cUetao$cdt1')
    require(''.join(token['text'][-1] for token in literal) == '*S-l/r0tylp')
    require(all(list(literal_chunks(text)) == ['til'] for text in ("'til", '‘til', '’til', '“til”')))
    require(list(literal_chunks('Alpha\u00a0Beta\t[Z] !!! $ / ***')) == ['Alpha\u00a0Beta', 'Z'])
    toy = ['a' + str(index).zfill(2) for index in range(24)]
    tokens = tokens_from_rows([row('toy', ' '.join(toy), [5])])
    generated = readings_from_tokens(tokens)
    def find(direction, phase, projection):
        return next(record for record in generated if (record['direction'], record['phase'], record['projection']) == (direction, phase, projection))
    require(find('forward', 6, 'words')['text'] == 'a05 a17')
    require(find('reverse', 6, 'words')['text'] == 'a18 a06')
    require(find('forward', 6, 'finals')['text'] == '57' and find('reverse', 6, 'finals')['text'] == '86')
    require(not find('forward', 6, 'words')['sourceCompleteForProjection'])
    require(not find('forward', 6, 'initials')['sourceCompleteForProjection'])
    require(find('forward', 6, 'finals')['sourceCompleteForProjection'])
    require(all(find('forward', 7, projection)['sourceCompleteForProjection'] for projection in PROJECTIONS))
    split = tokens_from_rows([row('page1', ' '.join(toy[:7])), row('page2', ' '.join(toy[7:17])), row('page3', ' '.join(toy[17:]))])
    no_reset = readings_from_tokens(split)
    require([record['text'] for record in generated] == [record['text'] for record in no_reset])
    punctuation = tokens_from_rows([row('punctuation', '— A — B', [0])])
    require([token['withinRowIndex0'] for token in punctuation] == [0, 1])
    require(punctuation[0]['uncertainForProjections'] == ['words', 'initials'] and punctuation[1]['uncertainForProjections'] == [])
    empty = readings_from_tokens([])
    require(len(empty) == 72 and len({record['text'] for record in empty}) == 1 and len(strict_known(empty)) == 72)
    sample = 'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'
    positive_readings = readings_from_tokens(tokens_from_rows([row('public-positive', sample, [0])]))
    _, indexes = evaluator.wordlist()
    all_evaluation = evaluator.evaluate(positive_readings, indexes)
    strict_evaluation = evaluator.evaluate(strict_known(positive_readings), indexes)
    require(all_evaluation['validCounts']['minikey'] == 1 and not strict_evaluation['privateReviewRequired'])
    require(not exact_equal({'ordinal': 1}, {'ordinal': True}))
    require(not exact_equal(positive_readings, positive_readings[::-1]))
    return {'status': 'PASS', 'controls': ['literal-18-wrapper-policy', 'ASCII-whitespace-only',
            'no-join-no-dedup-case-preservation', 'full-reversal-before-phase', 'phase1-to12',
            'no-row-page-resets', 'projection-specific-source-uncertainty', 'whole-reading-strict-subset',
            '72-empty-and-duplicate-records', 'actual-positive-independent-validation', 'exact-JSON-types-and-order'],
            'independentEvaluatorControls': shared_independent_controls,
            'syntheticReadings': 72, 'targetInputsRead': False, 'targetTokenizations': 0,
            'targetStrideSelections': 0, 'targetChecksumChecks': 0, 'networkQueries': 0}


def save_private(file, value):
    with os.fdopen(os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=True)
        handle.write('\n')


def verify(args):
    out = private_path(args.out)
    require(not out.exists() and out.parent.is_dir())
    out.mkdir(mode=0o700)
    receipt = {'schemaVersion': 1, 'status': 'FAIL', 'passed': False, 'networkQueries': 0,
               'completePhysicalHypothesisNegative': False}
    try:
        controls = self_test()
        evaluator = load_evaluator()
        result = json.loads(read_bytes(private_path(args.result, True), 4000000), object_pairs_hook=unique_object)
        require(result.get('testId') == 'issue27-body-stride12')
        require(result.get('batchId') == 'keiser-issue27-body-stride12-20261110')
        require(exact_equal(result.get('sourceHashes'), EXPECTED_SOURCE_HASHES))
        require(result.get('policySha256') == POLICY_SHA256)
        require(re.fullmatch(r'[a-f0-9]{40}', result.get('registrationCommit', '')))
        require(re.fullmatch(r'[a-f0-9]{64}', result.get('protocolSha256', '')))
        require(result.get('scriptHashes', {}).get(EVALUATOR_RELATIVE) == EVALUATOR_SHA256)
        own_hash = hashlib.sha256(read_bytes(Path(__file__).resolve(), 100000)).hexdigest()
        require(result.get('scriptHashes', {}).get(SELF_RELATIVE) == own_hash)
        require(set(result['scriptHashes']) == set(SCRIPT_PATHS))
        research_root = evaluator_path().resolve().parent.parent
        for relative, expected in result['scriptHashes'].items():
            require(isinstance(expected, str) and re.fullmatch(r'[a-f0-9]{64}', expected))
            file = (research_root / relative).resolve(strict=True)
            require(file.is_relative_to(research_root))
            require(hashlib.sha256(read_bytes(file, 200000)).hexdigest() == expected)
        policy_file = (research_root / POLICY_RELATIVE).resolve(strict=True)
        require(policy_file.is_relative_to(research_root))
        require(hashlib.sha256(read_bytes(policy_file, 20000)).hexdigest() == POLICY_SHA256)
        require(exact_equal(result.get('sourceExpectations'), {'bodyRows': 312, 'bodyTokenCount': 2018, 'uncertainTokens': 3}))
        require(result.get('networkQueries') == 0 and result.get('transactions') == 0)
        source_bytes = read_bytes(Path(args.source).expanduser().resolve(strict=True), 1000000)
        require(len(source_bytes) == 218304 and hashlib.sha256(source_bytes).hexdigest() == BODY_SHA256)
        source = json.loads(source_bytes, object_pairs_hook=unique_object)
        rows = source_rows(source)
        expected_tokens = tokens_from_rows(rows)
        require(len(expected_tokens) == 2018)
        require(sum(bool(token['uncertainForProjections']) for token in expected_tokens) == 3)
        row_pages = {row['rowId']: row['printedPage'] for row in rows}
        require(Counter(row_pages[token['rowId']] for token in expected_tokens) == {79: 669, 80: 707, 81: 642})
        for token in expected_tokens:
            if token['uncertainForProjections']:
                require(token['withinRowIndex0'] == 0 and token['text'][-1] == UNCERTAIN_ROWS[token['rowId']])
        saved_tokens = json.loads(read_bytes(private_path(args.tokens, True), 4000000), object_pairs_hook=unique_object)
        require(exact_equal(saved_tokens, {'schemaVersion': 1, 'tokens': expected_tokens}))
        expected_readings = readings_from_tokens(expected_tokens)
        raw_readings = read_bytes(private_path(args.readings, True), 2000000).decode('utf-8')
        lines = raw_readings.split('\n')
        if lines and lines[-1] == '':
            lines.pop()
        require(len(lines) == 72 and all(lines))
        saved_readings = [json.loads(line, object_pairs_hook=unique_object) for line in lines]
        require(exact_equal(saved_readings, expected_readings))
        known = strict_known(expected_readings)
        _, indexes = evaluator.wordlist()
        evaluation_all = evaluator.evaluate(expected_readings, indexes)
        evaluation_known = evaluator.evaluate(known, indexes)
        require(exact_equal(result.get('evaluationAll'), evaluation_all))
        require(exact_equal(result.get('evaluationStrictKnown'), evaluation_known))
        procedure_counts = {'bodyRows': 312, 'bodyTokens': 2018, 'uncertainTokens': 3,
                            'nominalReadings': 72, 'strictKnownReadings': len(known),
                            'sourceAffectedReadings': 72 - len(known),
                            'readingsByProjection': {projection: sum(record['projection'] == projection for record in expected_readings) for projection in PROJECTIONS},
                            'strictKnownReadingsByProjection': {projection: sum(record['projection'] == projection for record in known) for projection in PROJECTIONS},
                            'submittedCodePoints': sum(len(record['text']) for record in expected_readings),
                            'perStreamHashes': False}
        require(exact_equal(result.get('procedureCounts'), procedure_counts))
        expected_flags = {'scopeComplete': True, 'computationalModelComplete': True, 'physicalSourceComplete': False,
                          'completeNegative': False, 'privateReviewRequired': evaluation_all['privateReviewRequired'],
                          'completeModelNegative': not evaluation_all['privateReviewRequired'],
                          'strictKnownSubsetComplete': True,
                          'strictKnownSubsetNegative': not evaluation_known['privateReviewRequired'],
                          'completePhysicalHypothesisNegative': False}
        require(all(exact_equal(result.get(key), value) for key, value in expected_flags.items()))
        receipt.update(status='PASS', passed=True, testId=result['testId'],
                       registrationCommit=result['registrationCommit'], protocolSha256=result['protocolSha256'],
                       verifierSha256=own_hash, evaluatorSha256=EVALUATOR_SHA256,
                       bodySha256=BODY_SHA256, policySha256=POLICY_SHA256,
                       tokenRecordsExactlyEqual=True, readingRecordsExactlyEqual=True,
                       bodyRows=312, tokenCount=2018, nominalReadings=72, strictKnownReadings=len(known),
                       sourceAffectedReadings=72-len(known),
                       sourceAffectedByProjection={projection: sum(not record['sourceCompleteForProjection'] for record in expected_readings if record['projection'] == projection) for projection in PROJECTIONS},
                       evaluationAll=evaluation_all, evaluationStrictKnown=evaluation_known,
                       procedureCounts=procedure_counts,
                       controls=controls, **expected_flags,
                       scope='Independent exact saved token/reading replay and four-format validation; complete fixed model and strict-known reading subset only. No complete physical hypothesis exclusion.')
    except Exception as error:
        receipt.update(errorClass=type(error).__name__, error='Independent replay failed; no agreement or negative claim.')
    receipt['completedAtUTC'] = datetime.now(timezone.utc).isoformat()
    save_private(out / 'INDEPENDENT_CHECK.json', receipt)
    print(json.dumps({'status': receipt['status'], 'passed': receipt['passed'],
                      'completePhysicalHypothesisNegative': False, 'networkQueries': 0}))
    return 0 if receipt['passed'] else 1


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('Invalid arguments')


def main(argv=None):
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--self-test', action='store_true')
    action.add_argument('--verify', action='store_true')
    for name in ('result', 'tokens', 'readings', 'source', 'out'):
        parser.add_argument('--' + name)
    arguments = list(sys.argv[1:] if argv is None else argv)
    for option in ('--self-test', '--verify', '--result', '--tokens', '--readings', '--source', '--out'):
        require(sum(value == option or value.startswith(option + '=') for value in arguments) <= 1)
    args = parser.parse_args(arguments)
    paths = (args.result, args.tokens, args.readings, args.source, args.out)
    if args.self_test:
        require(not any(paths))
        print(json.dumps(self_test(), indent=2))
        return 0
    require(all(paths))
    return verify(args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        print(json.dumps({'status': 'FAIL', 'passed': False,
                          'completePhysicalHypothesisNegative': False, 'networkQueries': 0}), file=sys.stderr)
        sys.exit(1)
