#!/usr/bin/env python3
"""Independent26 verifier: controls only unless --verify is explicit.

Unchanged source builders define the frozen cohorts. New extraction uses a
rolling character window and backward memoized predecessor recursion, never
the new primary walker/checksum or the old candidate_union implementation.
Only question-mark checksum and domain-separated fingerprints touch candidates.
No scalar/address derivation, networking, Git, raw-value or locator output.
"""
from __future__ import annotations
import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if (HERE / 'global_mirror_dag.py').is_file() else Path(__file__).resolve().parents[3] / 'site/public/research'
SELF_PATH = 'scripts/verify_minikey26_compatibility.py'
LITERAL_PATH = 'analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json'
SCRIPTS = ('scripts/minikey26_compatibility.py', 'scripts/minikey_window_audit.cjs',
           'scripts/global_mirror_envelope.py', 'scripts/global_mirror_dag.py', SELF_PATH)
HELPER_PINS = {
    'scripts/minikey_window_audit.cjs': '189c6f359a057021adbc060ddeaa8caa29e6f58c40a6976daeda62025d2182f0',
    'scripts/global_mirror_envelope.py': '61538c617f74b9ab1dde922cd263e88436eb9ccc430b2072dcc003c49a50d712',
    'scripts/global_mirror_dag.py': '8134260ef4811830e5653a9d5294acec9b154eb9df3d11c9b558e50fe20ca12d',
}
B58 = frozenset('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
DOMAIN = b'KEY404/batch20/record-fingerprint/v1\x00minikey\x00'
FP_RULE = {'algorithm': 'SHA-256', 'domainText': 'KEY404/batch20/record-fingerprint/v1', 'separatorHex': '00',
           'rule': 'SHA256(domain || 0x00 || ASCII(minikey) || 0x00 || ASCII(candidate))'}
END = -1


def require(value):
    if not value:
        raise ValueError('Independent validation failed')


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value)
        value[key] = item
    return value


def exact(left, right):
    return json.dumps(left, sort_keys=True, ensure_ascii=True, separators=(',', ':')) == json.dumps(right, sort_keys=True, ensure_ascii=True, separators=(',', ':'))


def read_bytes(file, cap=20000000):
    require(file.is_file() and file.stat().st_size <= cap)
    with file.open('rb') as handle:
        value = handle.read(cap + 1)
    require(len(value) <= cap)
    return value


def private_path(value, existing=False):
    file = Path(value).expanduser().resolve()
    require(not any(part.lower() == 'public' for part in file.parts))
    if existing:
        require(file.is_file() and file.stat().st_mode & 0o077 == 0)
    return file


def load_helper(relative):
    file = (ROOT / relative).resolve(strict=True)
    require(file.is_relative_to(ROOT) and hashlib.sha256(read_bytes(file, 100000)).hexdigest() == HELPER_PINS[relative])
    spec = importlib.util.spec_from_file_location('_unchanged_' + file.stem, file)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def shape26(value):
    return isinstance(value, str) and len(value) == 26 and value[0] == 'S' and all(char in B58 for char in value)


def assess(values):
    require(all(shape26(value) for value in values))
    hits = []
    for value in sorted(values):
        if hashlib.sha256((value + '?').encode('ascii')).digest()[0] == 0:
            hits.append({'format': 'minikey', 'length': 26, 'checkBits': 8,
                         'fingerprint': hashlib.sha256(DOMAIN + value.encode('ascii')).hexdigest(), 'private': True})
    return {'lengths': [26], 'uniqueShapeCount': len(values), 'checksumValidCount': len(hits),
            'checksumCalls': len(values), 'hits': sorted(hits, key=lambda hit: hit['fingerprint']),
            'fingerprintRule': FP_RULE, 'privateReviewRequired': bool(hits)}


def literal_windows(text):
    window = deque(maxlen=26)
    for char in text:
        if char not in B58:
            window.clear()
            continue
        window.append(char)
        if len(window) == 26 and window[0] == 'S':
            yield ''.join(window)


class SuffixBudget:
    def __init__(self, states=2000000, insertions=2000000, candidates=1000000):
        self.state_cap, self.insertion_cap, self.candidate_cap = states, insertions, candidates
        self.states = self.insertions = 0

    def state(self):
        self.states += 1
        require(self.states <= self.state_cap)

    def insertion(self):
        self.insertions += 1
        require(self.insertions <= self.insertion_cap)


def predecessor_windows(graph, budget=None):
    """Unique26 substrings ending at each node, recursing to predecessors.

    Cache key is (end node, exact remaining length), not (start node, prefix).
    Reachability/co-reachability guards ensure a complete language path exists.
    """
    budget = budget or SuffixBudget()
    chars, successors = graph['chars'], graph['next']
    require(set(chars) == set(successors) and END not in chars)
    require(all(isinstance(char, str) and len(char) == 1 for char in chars.values()))
    predecessors = {node: set() for node in chars}
    predecessors[END] = set()
    for node, next_nodes in successors.items():
        for following in next_nodes:
            require(following == END or following in chars)
            predecessors[following].add(node)
    reachable, pending = set(), list(graph['first'])
    while pending:
        node = pending.pop()
        require(node == END or node in chars)
        if node not in reachable:
            reachable.add(node)
            if node != END:
                pending.extend(successors[node])
    require(END in reachable)
    returning, pending = {END}, [END]
    while pending:
        for node in predecessors[pending.pop()]:
            if node not in returning:
                returning.add(node)
                pending.append(node)
    alive = (reachable & returning) - {END}
    indegree = {node: len(predecessors[node] & alive) for node in alive}
    queue = deque(node for node in alive if not indegree[node])
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for following in successors[node] & alive:
            indegree[following] -= 1
            if indegree[following] == 0:
                queue.append(following)
    require(visited == len(alive))
    cache = {}
    def suffixes(node, length):
        key = node, length
        if key not in cache:
            budget.state()
            char = chars[node]
            values = set()
            if length == 1:
                if char == 'S':
                    values.add(char)
                    budget.insertion()
            else:
                for previous in predecessors[node] & alive:
                    if chars[previous] not in B58:
                        continue
                    for prefix in suffixes(previous, length - 1):
                        value = prefix + char
                        if value not in values:
                            values.add(value)
                            budget.insertion()
            cache[key] = frozenset(values)
        return cache[key]
    result = set()
    for node in sorted(alive):
        if chars[node] in B58:
            result.update(suffixes(node, 26))
            require(len(result) <= budget.candidate_cap)
    require(all(shape26(value) for value in result))
    return result


def exhaustive_toy(rows, mode, reverse):
    result = set()
    for choices in itertools.product(*rows):
        selected = [word for word in choices if word is not None]
        if reverse:
            selected.reverse()
        if mode == 'words-spaced':
            text = ' '.join(selected)
        elif mode == 'words-joined':
            text = ''.join(selected)
        else:
            text = ''.join(next((char for char in word if char.isalnum()), '') for word in selected)
        result.update(literal_windows(text))
    return result


def self_test():
    builder = load_helper('scripts/global_mirror_dag.py')
    sample = None
    alphabet = ''.join(sorted(B58))
    for counter in range(65536):
        remaining, tail = counter, ''
        while True:
            remaining, digit = divmod(remaining, 58)
            tail = alphabet[digit] + tail
            if remaining == 0:
                break
        value = 'S' + '2' * 19 + tail.rjust(6, '2')
        if assess({value})['checksumValidCount']:
            sample = value
            break
    require(sample is not None and shape26(sample))
    require(set(literal_windows('1' + sample + '1')) == {sample})
    require(not list(literal_windows(sample[:12] + '🧪' + sample[12:])))
    require(all(not shape26('S' + char * 25) for char in ('0', 'O', 'I', 'l', 'é')))
    require(not shape26('S' + '2' * 21) and not shape26('S' + '2' * 29))
    cases = [
        [[None, '::'], [sample[:9], sample[:8] + '0'], [None, sample[9:18]], [sample[18:]], ['::', None]],
        [[sample[13:]], [sample[:13]]],
        [[char] for char in sample],
        [[None], [None]],
        [['éS', '🧪S'], ['2' * 25]],
        [[sample[:12]], ['\u2003', None], [sample[12:]]],
        [[sample[:12]], ['\ufeff', None], [sample[12:]]],
    ]
    rng = random.Random(20261110)
    pool = [None, 'S', '2' * 13, sample[:12], sample[12:], '0', 'I', 'l', 'é', '🧪', '—', 'abc']
    for _ in range(15):
        cases.append([[rng.choice(pool) for _ in range(rng.randint(1, 3))] for _ in range(rng.randint(2, 5))])
    comparisons = 0
    for rows in cases:
        for mode in ('words-spaced', 'words-joined', 'initials'):
            for reverse in (False, True):
                require(predecessor_windows(builder.graph(rows, mode, reverse)) == exhaustive_toy(rows, mode, reverse))
                comparisons += 1
    for budget in (SuffixBudget(states=0), SuffixBudget(insertions=0), SuffixBudget(candidates=0)):
        try:
            predecessor_windows(builder.graph([[sample]]), budget)
        except ValueError:
            pass
        else:
            require(False)
    assessment = assess({sample})
    require(assessment['checksumValidCount'] == 1 and sample not in json.dumps(assessment))
    require(assessment['hits'][0]['fingerprint'] == hashlib.sha256(b'KEY404/batch20/record-fingerprint/v1\0minikey\0' + sample.encode('ascii')).hexdigest())
    return {'status': 'PASS', 'syntheticDAGComparisons': comparisons, 'capGuards': 3,
            'controls': ['cross-branch', 'omission-conditional-space', 'reverse-whole-sequence',
                         'Unicode-codepoint-barriers', 'Base58-exclusions', '26-only-positive-checksum',
                         'safe-domain-fingerprint'],
            'targetInputsRead': False, 'target26Scans': 0, 'targetChecksumChecks': 0, 'networkQueries': 0}


def canonical_literal_forms():
    program = "const fs=require('node:fs');const a=require(process.argv[1]);const x=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const s=a.selectStreams(x);process.stdout.write(JSON.stringify({streamCount:s.length,forms:a.makeForms(s).map(f=>f.text)}));"
    result = subprocess.run(['node', '-e', program, str(ROOT / 'scripts/minikey_window_audit.cjs'), str(ROOT / LITERAL_PATH)],
                            capture_output=True, timeout=30, check=False)
    require(result.returncode == 0 and len(result.stdout) <= 2000000)
    value = json.loads(result.stdout, object_pairs_hook=unique_object)
    require(value.get('streamCount') == 22 and len(value.get('forms', [])) == 42)
    require(all(isinstance(text, str) and len(text) > 30 for text in value['forms']))
    return value


def save_private(file, value):
    with os.fdopen(os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


def verify(args):
    out = private_path(args.out)
    require(not out.exists() and out.parent.is_dir())
    out.mkdir(mode=0o700)
    receipt = {'status': 'FAIL', 'passed': False, 'scopeComplete': False, 'networkQueries': 0}
    try:
        controls = self_test()
        result = json.loads(read_bytes(private_path(args.result, True)), object_pairs_hook=unique_object)
        require(result.get('testId') == 'minikey26-original-compatibility' and result.get('batchId') == 'keiser-minikey26-original-compatibility-20261110')
        require(result.get('scopeComplete') is True and result.get('candidateAssessment') == 'complete-for-saved-set')
        require(re.fullmatch(r'[0-9a-f]{40}', result.get('registrationCommit', '')))
        require(re.fullmatch(r'[0-9a-f]{64}', result.get('protocolSha256', '')))
        require(len(result.get('sourceHashes', {})) == 11 and set(result.get('scriptHashes', {})) == set(SCRIPTS))
        for relative, expected in {**result['sourceHashes'], **result['scriptHashes']}.items():
            require(isinstance(expected, str) and re.fullmatch(r'[0-9a-f]{64}', expected))
            file = (ROOT / relative).resolve(strict=True)
            require(file.is_relative_to(ROOT) and hashlib.sha256(read_bytes(file)).hexdigest() == expected)
        require(all(result['scriptHashes'][relative] == expected for relative, expected in HELPER_PINS.items()))
        own_hash = hashlib.sha256(read_bytes(Path(__file__).resolve(), 100000)).hexdigest()
        require(result['scriptHashes'][SELF_PATH] == own_hash)
        forms = canonical_literal_forms()
        saved_forms = json.loads(read_bytes(private_path(args.forms, True), 2000000), object_pairs_hook=unique_object)
        require(exact(forms, saved_forms))
        literal = set()
        occurrences = 0
        for text in forms['forms']:
            for value in literal_windows(text):
                occurrences += 1
                literal.add(value)
        positions = sum(max(0, len(text) - 25) for text in forms['forms'])
        require(positions == 113662)
        literal_counts = {'frozenStreams': 22, 'uniqueForms': 42, 'positionWindows26': positions,
                          'shapeCompatibleOccurrences': occurrences, 'uniqueShapes': len(literal)}
        require(exact(result.get('literalCounts'), literal_counts))
        source = load_helper('scripts/global_mirror_envelope.py')
        builder = load_helper('scripts/global_mirror_dag.py')
        families = source.checked_source_families()
        require(len(families) == 4)
        global_values = set()
        budget = SuffixBudget()
        descriptors = []
        for family in families:
            for reverse in (False, True):
                for projection in ('words-spaced', 'words-joined', 'initials'):
                    before = len(global_values)
                    global_values.update(predecessor_windows(builder.graph(family['rows'], projection, reverse), budget))
                    require(len(global_values) <= budget.candidate_cap)
                    descriptors.append({'family': family['id'], 'rowOrder': 'reverse-entire-sequence' if reverse else 'forward',
                                        'projection': projection, 'complete': True, 'newUniqueShapes': len(global_values) - before})
        require(len(descriptors) == 24 and len(result.get('languageChecks', [])) == 24)
        for actual, expected in zip(result['languageChecks'], descriptors):
            actual = dict(actual)
            require(type(actual.pop('stateVisits')) is int)
            require(exact(actual, expected))
        union = literal | global_values
        require(len(union) <= budget.candidate_cap)
        candidate_sets = {'length': 26, 'literal': sorted(literal), 'global': sorted(global_values), 'union': sorted(union)}
        saved_sets = json.loads(read_bytes(private_path(args.candidates, True)), object_pairs_hook=unique_object)
        require(exact(saved_sets, candidate_sets))
        cohort_counts = {'literalUniqueShapes': len(literal), 'globalUniqueShapes': len(global_values),
                         'combinedUniqueShapes': len(union), 'overlap': len(literal & global_values)}
        require(exact(result.get('cohortCounts'), cohort_counts))
        evaluation = assess(union)
        actual_evaluation = dict(result.get('evaluation', {}))
        actual_evaluation['hits'] = sorted(actual_evaluation.get('hits', []), key=lambda hit: hit['fingerprint'])
        require(exact(actual_evaluation, evaluation))
        require(result.get('privateReviewRequired') is evaluation['privateReviewRequired'])
        require(result.get('completeNegative') is (not evaluation['privateReviewRequired']))
        require(all(result.get(key) == 0 for key in ('scalarDerivations', 'addressDerivations', 'networkAddressQueries', 'transactions')))
        receipt.update(status='PASS', passed=True, scopeComplete=True, verifierSha256=own_hash,
                       registrationCommit=result['registrationCommit'], protocolSha256=result['protocolSha256'],
                       fullPrivateCandidateSetsMatch=True, frozenFormsMatch=True, languageDescriptorsMatched=24,
                       literalCounts=literal_counts, cohortCounts=cohort_counts, evaluation=evaluation,
                       independentResources={'suffixMemoStates': budget.states, 'suffixStringInsertions': budget.insertions},
                       controls=controls, scope='Independent26-only fixed-cohort candidate sets and checksums; no downstream action or broader puzzle exclusion')
    except Exception as error:
        receipt.update(errorClass=type(error).__name__, error='Independent replay failed; no agreement or exclusion claim.')
    receipt['completedAtUTC'] = datetime.now(timezone.utc).isoformat()
    save_private(out / 'INDEPENDENT_CHECK.json', receipt)
    print(json.dumps({'status': receipt['status'], 'passed': receipt['passed'], 'scopeComplete': receipt['scopeComplete'], 'networkQueries': 0}))
    return 0 if receipt['passed'] else 1


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('Invalid arguments')


def main(argv=None):
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--self-test', action='store_true')
    actions.add_argument('--verify', action='store_true')
    for name in ('result', 'forms', 'candidates', 'out'):
        parser.add_argument('--' + name)
    arguments = list(sys.argv[1:] if argv is None else argv)
    for option in ('--self-test', '--verify', '--result', '--forms', '--candidates', '--out'):
        require(sum(value == option or value.startswith(option + '=') for value in arguments) <= 1)
    args = parser.parse_args(arguments)
    values = args.result, args.forms, args.candidates, args.out
    if args.self_test:
        require(not any(values))
        print(json.dumps(self_test(), indent=2))
        return 0
    require(all(values))
    return verify(args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        print(json.dumps({'status': 'FAIL', 'passed': False, 'scopeComplete': False, 'networkQueries': 0}), file=sys.stderr)
        sys.exit(1)
