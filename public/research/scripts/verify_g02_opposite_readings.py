#!/usr/bin/env python3
"""Enumerate the registered global opposite-color assignments without format tests."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import re
import subprocess
import sys

AUDIT = 'analysis_outputs/continuation_20261110/g02_joint_color_audit/'
RESULT = AUDIT + 'RESULT.json'
MEMBERSHIP = AUDIT + 'MEMBERSHIP.json'
INDEPENDENT = AUDIT + 'INDEPENDENT_VERIFICATION.json'
AUDIT_REGISTRATION = AUDIT + 'REGISTRATION.json'
LINES = 'sources/printed-lines.json'
GEOMETRY = 'sources/word-geometry-20261110.json'
SCRIPT = 'scripts/verify_g02_opposite_readings.py'
PRIMARY = 'scripts/g02_reading_model.py'
PROTOCOL = 'analysis_outputs/continuation_20261110/g02_opposite_reading/PROTOCOL.json'
AUDIT_COMMIT = 'ec3bb322cb1b8baa35ee128143dd8864cb6ab451'
PINS = {
    RESULT: '392903951d353d971258a578ac3b967a813e4b95a19e1991cb76d5e84ef7abe4',
    MEMBERSHIP: '2c10b715873e50cb0911765d8e096cbc38094a43d8cb0aff6c9a7ea8caacca91',
    INDEPENDENT: '59f3522d9525547dd83de6a48055922ec618e3ca6430e82eac980ca3f603e325',
    AUDIT_REGISTRATION: 'f703e4d79b8c675d532e5ae740bbcba4a448c26dbd3096f3c07859e453496024',
    LINES: 'c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe',
    GEOMETRY: 'e3348d0d60d3097b05d0afdb0a1fccf66409274408af9ae7a9369c37fe596e9f',
}
PAIRS = ((76, 77), (77, 76), (78, 79), (79, 78))
MODES = ('words-spaced', 'words-joined', 'initials', 'finals')
OPTIONAL_IDS = ('p77r14w07', 'p76r14w01', 'p76r14w02')
EXPECTED = {'must': 0, 'optional': 3, 'out': 959, 'unresolved': 0,
            'independentAssignmentUpperBound': '8'}
MAX_FILE = 24_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def lexical_positions(rows, geometry_rows):
    geometry = {row['id']: row for row in geometry_rows}
    require(len(geometry) == len(geometry_rows) == len(rows), 'Geometry row count changed')
    require(len({row['id'] for row in rows}) == len(rows), 'Duplicate canonical row')
    by_page = {}
    all_ids = set()
    for row in rows:
        observed = geometry[row['id']]
        require(observed['page'] == row['page'] and observed['status'] == 'complete'
                and observed['lexicallyComplete'] is True, 'Incomplete source geometry')
        words = [word for word in observed['words'] if any(c.isalnum() for c in word['text'])]
        tokens = [token for token in row['text'].split() if any(c.isalnum() for c in token)]
        require([word['text'] for word in words] == tokens, 'Lexical source mismatch')
        page_positions = by_page.setdefault(row['page'], [])
        for ordinal, word in enumerate(words, 1):
            word_id = word['id']
            require(word['verified'] is True and word_id not in all_ids, 'Invalid source word ID')
            all_ids.add(word_id)
            page_positions.append((row['id'], word_id, ordinal, word['text']))
    return by_page


def join_membership(by_page, records, pairs):
    expected = [(source, target, row_id, word_id, ordinal, text)
                for source, target in pairs
                for row_id, word_id, ordinal, text in by_page[target]]
    require(len(expected) == len(records), 'Membership position count changed')
    selected = []
    counts = Counter()
    for position, record in zip(expected, records):
        witness = tuple(record[key] for key in ('source', 'target', 'rowId', 'wordId', 'wordOrdinalInRow'))
        require(position[:5] == witness, 'Membership order or source identity changed')
        state = record['selectorMembership']['opposite-color']
        require(state in ('out', 'optional'), 'Unexpected fixed or unresolved opposite-color position')
        counts[state] += 1
        if state == 'optional':
            selected.append((position[3], position[5]))
    return selected, counts


def enumerate_records(optionals):
    require(len(optionals) == 3 and len({word_id for word_id, _ in optionals}) == 3,
            'Expected three distinct optional positions')
    records = []
    for bits in product('01', repeat=3):
        assignment = ''.join(bits)
        forward = [position for position, bit in zip(optionals, bits) if bit == '1']
        for order, positions in (('forward', forward), ('reverse', forward[::-1])):
            ids = [word_id for word_id, _ in positions]
            words = [word for _, word in positions]
            edges = [[c for c in word if c.isalnum()] for word in words]
            texts = (' '.join(words), ''.join(words),
                     ''.join(letters[0] for letters in edges),
                     ''.join(letters[-1] for letters in edges))
            for mode, text in zip(MODES, texts):
                records.append({'id': f'{assignment}/{order}/{mode}', 'assignment': assignment,
                                'order': order, 'mode': mode, 'selectedWordIds': ids, 'text': text})
    return {'records': records}


def self_test():
    def row(name, page, text):
        return {'id': name, 'page': page, 'text': text}

    def geometry(name, page, entries):
        return {'id': name, 'page': page, 'status': 'complete', 'lexicallyComplete': True,
                'words': [{'id': word_id, 'text': text, 'verified': True} for word_id, text in entries]}

    def membership(source, target, row_id, word_id, index, state):
        return {'source': source, 'target': target, 'rowId': row_id, 'wordId': word_id,
                'wordOrdinalInRow': index, 'selectorMembership': {'opposite-color': state}}

    rows = [row('r76', 76, '“Äb-2!” + Ḃ.'), row('r77', 77, '(中ø?) omit')]
    geometries = [geometry('r77', 77, [('X', '(中ø?)'), ('ignored', 'omit')]),
                  geometry('r76', 76, [('A', '“Äb-2!”'), ('symbol', '+'), ('B', 'Ḃ.')])]
    records = [membership(76, 77, 'r77', 'X', 1, 'optional'),
               membership(76, 77, 'r77', 'ignored', 2, 'out'),
               membership(77, 76, 'r76', 'A', 1, 'optional'),
               membership(77, 76, 'r76', 'B', 2, 'optional')]
    by_page = lexical_positions(rows, geometries)
    optionals, counts = join_membership(by_page, records, PAIRS[:2])
    require(counts == {'optional': 3, 'out': 1}, 'Synthetic membership counts')
    readings = enumerate_records(optionals)['records']
    require(len(readings) == 64 and len({r['id'] for r in readings}) == 64, 'Synthetic record count')
    require(all(r['text'] == '' and not r['selectedWordIds'] for r in readings[:8]),
            'Synthetic all-omitted readings')
    require([r['id'] for r in readings[8:12]] ==
            [f'001/forward/{mode}' for mode in MODES], 'Synthetic assignment ordering')
    require([r['text'] for r in readings[8:12]] == ['Ḃ.', 'Ḃ.', 'Ḃ', 'Ḃ'],
            'Synthetic leftmost-bit convention')
    require([r['text'] for r in readings[-8:]] ==
            ['(中ø?) “Äb-2!” Ḃ.', '(中ø?)“Äb-2!”Ḃ.', '中ÄḂ', 'ø2Ḃ',
             'Ḃ. “Äb-2!” (中ø?)', 'Ḃ.“Äb-2!”(中ø?)', 'ḂÄ中', 'Ḃ2ø'],
            'Synthetic word order, punctuation and Unicode edges')
    require(readings[-8]['selectedWordIds'] == ['X', 'A', 'B']
            and readings[-1]['selectedWordIds'] == ['B', 'A', 'X'], 'Synthetic source ID ordering')
    for invalid in (records[::-1], records[:3], [{**records[0], 'selectorMembership':
                    {'opposite-color': 'unresolved'}}, *records[1:]]):
        try:
            join_membership(by_page, invalid, PAIRS[:2])
        except ValueError:
            continue
        raise ValueError('Synthetic malformed membership accepted')


def bounded_read(path):
    require(path.is_file() and path.stat().st_size <= MAX_FILE, 'Registered file unavailable or oversized')
    data = path.read_bytes()
    require(len(data) <= MAX_FILE, 'Registered file grew during read')
    return data


def corpus_file(research, relative):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(),
            'Invalid corpus-relative path')
    resolved = (research / relative).resolve(strict=True)
    require(resolved.is_relative_to(research) and relative == resolved.relative_to(research).as_posix(),
            'Corpus path alias or escape')
    return resolved


def committed_inputs(research, protocol, commit):
    require(re.fullmatch('[0-9a-f]{40}', commit) is not None, 'Invalid registration commit')
    require(research.name == 'research' and research.parent.name == 'public', 'Expected public research directory')
    checkout = research.parent.parent

    def git(*args):
        return subprocess.run(['git', '-C', str(checkout), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout

    require(Path(os.fsdecode(git('rev-parse', '--show-toplevel')).strip()) == checkout
            and git('cat-file', '-t', commit) == b'commit\n', 'Expected registered Git commit')
    protocol_relative = protocol.relative_to(research).as_posix()
    require(protocol_relative == PROTOCOL, 'Wrong protocol path')

    def registered(relative):
        current = bounded_read(corpus_file(research, relative))
        git_path = f'{commit}:public/research/{relative}'
        require(int(git('cat-file', '-s', git_path)) <= MAX_FILE, 'Oversized registered blob')
        require(current == git('show', git_path), 'Current file differs from registration')
        return current

    protocol_bytes = registered(protocol_relative)
    spec = json.loads(protocol_bytes)
    sources = spec['sourceHashes']
    scripts = spec['scriptHashes']
    require(all(sources.get(name) == digest for name, digest in PINS.items())
            and scripts.get(SCRIPT) == sha(bounded_read(Path(__file__)))
            and PRIMARY in scripts, 'Source or running code pin changed')
    require(not set(sources) & set(scripts), 'Overlapping pin lists')
    inputs = {}
    for name, digest in {**sources, **scripts}.items():
        data = registered(name)
        require(sha(data) == digest, 'Registered file SHA mismatch')
        if name in PINS:
            inputs[name] = data
    return inputs


def output_path(path, checkout):
    require(path.is_absolute() and not path.exists() and not path.is_symlink(),
            'Provide a fresh absolute output directory')
    parent = path.parent.resolve(strict=True)
    require(parent.is_dir() and not parent.is_relative_to(checkout)
            and not any(part.lower() == 'public' for part in parent.parts)
            and path == parent / path.name, 'Output must be outside the checkout and public paths')
    return path


def verify_source(inputs):
    saved = {name: json.loads(data) for name, data in inputs.items()}
    result, independent, registration = (saved[name] for name in (RESULT, INDEPENDENT, AUDIT_REGISTRATION))
    require(registration['registrationCommit'] == AUDIT_COMMIT and registration['remoteHeadMatches'] is True
            and independent['registrationCommit'] == AUDIT_COMMIT and independent['verificationPassed'] is True
            and independent['allOrderedMetadataFieldsMatch'] is True
            and independent['primaryInventorySha256'] == PINS[MEMBERSHIP]
            and independent['primaryResultSha256'] == PINS[RESULT]
            and independent['registrationReceiptSha256'] == PINS[AUDIT_REGISTRATION]
            and result['inventory']['sha256'] == PINS[MEMBERSHIP], 'Prior source audit receipt mismatch')
    require(all(doc['sourceModelComplete'] is True
                and doc['globalSelectors']['opposite-color'] == EXPECTED
                for doc in (result, independent)), 'Opposite-color population not certified')
    rows = saved[LINES]['rows']
    require(len(rows) == 142 and sum(len(row['text'].split()) for row in rows) == 1258,
            'Canonical source count changed')
    by_page = lexical_positions(rows, saved[GEOMETRY]['rows'])
    require(sum(map(len, by_page.values())) == 1243
            and [len(by_page[target]) for _, target in PAIRS] == [263, 274, 226, 199],
            'Target lexical population changed')
    optionals, counts = join_membership(by_page, saved[MEMBERSHIP]['wordRecords'], PAIRS)
    require(tuple(word_id for word_id, _ in optionals) == OPTIONAL_IDS
            and counts == {'optional': 3, 'out': 959}, 'Frozen opposite-color scope changed')
    return optionals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--self-test', action='store_true')
    action.add_argument('--run', action='store_true')
    parser.add_argument('--research', type=Path)
    parser.add_argument('--protocol', type=Path)
    parser.add_argument('--registration-commit')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        self_test()
        if args.self_test:
            require(not any((args.research, args.protocol, args.registration_commit, args.out)),
                    'Synthetic controls accept no target arguments')
            print('PASS synthetic opposite-color controls')
            return
        require(all((args.research, args.protocol, args.registration_commit, args.out)),
                'Run requires research, protocol, registration commit and output')
        research = args.research.resolve(strict=True)
        out = output_path(args.out, research.parent.parent)
        inputs = committed_inputs(research, args.protocol.resolve(strict=True), args.registration_commit)
        readings = enumerate_records(verify_source(inputs))
        out.mkdir(mode=0o700)
        payload = (json.dumps(readings, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        with os.fdopen(os.open(out / 'READINGS.private.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                       'wb') as handle:
            handle.write(payload)
        print('PASS 64 independent nominal records written privately')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        print('Incomplete opposite-color enumeration', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
