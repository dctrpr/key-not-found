#!/usr/bin/env python3
"""Bounded replay of already frozen Issue27 streams; offline, stdlib only.

Import, --list and --self-test never open the article. --run requires a matching
protocol, exact local Git registration bytes and a fresh private output folder.
Raw replayed readings stay private. No key/address derivation or network code.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PRIMARY = 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json'
PRIMARY_SHA256 = 'f5f441345ebe411ee769cdcb624c0717a2b4f790b7eadc50d10dc12d37da07bb'
SOURCE_DIR = 'analysis_outputs/continuation_20261109/george_sand_issue27/'
INPUTS = (PRIMARY, SOURCE_DIR + 'analyze_printed_lines.py', SOURCE_DIR + 'REPORT.md',
          SOURCE_DIR + 'regions.json', SOURCE_DIR + 'vision_raw.json',
          'scripts/batch20_support/english.txt', 'scripts/batch20_support/controls.json')
SCRIPTS = ('scripts/issue27_stream_coverage.py', 'scripts/batch20_common.py')
FORMATS = ('wif', 'minikey', 'hex64', 'bip39')
BATCH_ID = 'keiser-issue27-stream-coverage-20261110'
SOURCE_PAGES = {'2': 79, '3': 80, '4': 81}
SOURCE_SUMMARY = {'rawObservations': 357, 'physicalLines': 356, 'regions': 14,
                  'streams': 1940, 'corrections': 26, 'directEncodingHits': 0}
ROW_FIELDS = ('confidence', 'line', 'page', 'region', 'text', 'x0', 'x1', 'y0', 'y1',
              'rawLine', 'corrected', 'kind', 'firstword', 'lastword', 'initial', 'terminal')
SCOPES = ('p2_wide_quote', 'p2_wide_intro', 'p2_col1', 'p2_col2', 'p2_col3',
          'p3_wide_intro', 'p3_col1', 'p3_col2', 'p3_col3', 'p4_wide_intro',
          'p4_col1_top', 'p4_col2_top', 'p4_facts_wide', 'p4_col3',
          'p2_all_regions', 'p3_all_regions', 'p4_all_regions', 'article_all_regions')
LABEL_DIMENSIONS = (SCOPES, ('all', 'body', 'body_intro', 'emphasis'),
                    ('all', 'odd', 'even'), ('forward', 'reverse_lines'),
                    ('firstwords', 'initials', 'lastwords', 'terminals', 'whole_lines'))
FINGERPRINT_RULE = {'algorithm': 'SHA-256', 'domainText': 'KEY404/batch20/record-fingerprint/v1',
                    'separatorHex': '00',
                    'rule': 'SHA256(domain || 0x00 || ASCII(format) || 0x00 || canonical record bytes)'}
DEFINITION = {
    'id': 'issue27-frozen-stream-coverage',
    'title': 'Issue27 literal-record coverage of already frozen printed-line streams',
    'family': 'frozen-stream-validator-coverage', 'branchId': 'sources',
    'inputPaths': list(INPUTS), 'implementationPaths': list(SCRIPTS),
    'parameters': {
        'primaryPath': PRIMARY, 'primarySha256': PRIMARY_SHA256, 'primaryBytes': 946620,
        'sourcePages': SOURCE_PAGES, 'sourceSummary': SOURCE_SUMMARY,
        'expectedRows': 356, 'expectedRegions': 14, 'expectedScopeUnits': 18,
        'expectedFrozenStreams': 1940, 'expectedPrimaryCodePoints': 664764,
        'expectedMinimumStreamCodePoints': 1, 'expectedMaximumStreamCodePoints': 13698,
        'labelDimensions': [list(d) for d in LABEL_DIMENSIONS],
        'characterOrders': ['exact', 'reversed-codepoints'],
        'operationOrder': 'Sort frozen labels; emit exact text and text[::-1]; shared exact/whitespace-only-compacted forms; shared deduplication and validators.',
        'expectedSubmittedRecords': 3880, 'maximumSubmittedRecords': 3880,
        'maximumUniqueForms': 7760, 'maximumInputBytes': 2000000,
        'maximumRegisteredBlobBytes': 2000000,
        'maximumSubmittedCodePoints': 2000000, 'maximumUniqueFormCodePoints': 4000000,
        'formats': list(FORMATS), 'forms': ['exact', 'whitespace-only-compacted'],
        'bip39Tokenization': 'Pinned shared unfiltered ASCII lexical tokens; lowercase case; retain digits and internal apostrophes as unknown-word barriers; ordinary punctuation bounds words; missing-group character ␞ is a hard region boundary.',
        'minikeyMatching': 'Overlapping S-prefixed Base58 windows of exactly 22 or 30 characters, including inside longer Base58 runs; validate SHA256(value+question-mark) first byte zero.',
        'wifMatching': 'Embedded 51/52-character mainnet Base58Check WIF; compression marker and scalar range required.',
        'hexMatching': 'Exactly 64 hexadecimal characters with non-hex boundaries; scalar range required; no checksum claim.',
        'newReadings': False, 'transcriptRepairs': False, 'newOCR': False,
        'otherCorpora': False, 'proseHashWrappers': False, 'rawAsciiScalars': False,
        'deriveSeeds': False, 'deriveAddresses': False, 'passphraseGuesses': False,
        'networkQueries': 0, 'transactions': 0,
        'rawArtifacts': ['READINGS.private.jsonl'], 'perStreamHashes': False,
    },
    'fingerprintRule': FINGERPRINT_RULE,
    'controls': ['shared-format-controls', 'exact-and-codepoint-reversal',
                 'empty-palindrome-Unicode-whitespace-deduplication',
                 'BIP39-unknown-numeric-apostrophe-missing-group-barriers',
                 'BIP39-case-and-punctuation', 'safe-result-allowlist',
                 'protocol-byte-registration-guards-with-synthetic-mocks'],
    'negativeCriterion': 'A complete zero result excludes only the four declared literal formats in the exact 1940 frozen Issue27 readings, their already used character reversals and registered whitespace treatment at the pinned bytes.',
    'limitations': [
        'Source identification as Issue27/Fall2022 is inherited from the historical report; recovered title/pages alone do not independently establish issue number/date.',
        'First words were historically visually reviewed; line interiors and last edges retain stated OCR limits. No transcript is rebuilt or repaired here.',
        'Already frozen scopes, typography selections, parity choices and mirror counterparts are correlated conventions, not evidence of author intent.',
        'Eight-bit minikey checks are weak under many trials, and valid-range hex64 has no checksum. Any valid record requires private review.',
        'Extended private keys, BIP38, addresses, SEC points, other articles/issues, arbitrary encodings and new readings are outside this four-format replay.',
        'No address/history check, seed derivation, wallet action or transaction follows automatically.',
    ],
}


def code_definition():
    return deepcopy(DEFINITION)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def sha_bytes(data):
    # Whole-file provenance/registration bytes only. Never called on target
    # streams or target candidate records.
    return hashlib.sha256(data).hexdigest()


def private_json(path, value):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                   'w', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=True)
        handle.write('\n')


def capped_read(file, limit):
    require(file.stat().st_size <= limit, 'File byte cap exceeded')
    with file.open('rb') as handle:
        content = handle.read(limit + 1)
    require(len(content) <= limit, 'File grew beyond byte cap')
    return content


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field')
        result[key] = value
    return result


def research_file(relative):
    require(relative in INPUTS + SCRIPTS, 'Unregistered file path')
    file = (ROOT / relative).resolve(strict=True)
    require(file.is_file() and file.is_relative_to(ROOT), 'Research file escapes root')
    return file


def private_output(value):
    out = Path(value).expanduser().resolve()
    require(not any(part.lower() == 'public' for part in out.parts), 'Private output required')
    require(not out.exists() and not out.is_symlink(), 'Fresh output required')
    require(out.parent.is_dir(), 'Existing private output parent required')
    return out


def submitted_readings(streams):
    for label in sorted(streams):
        text = streams[label]
        yield {'id': label + ':exact', 'sourceLabel': label, 'characterOrder': 'exact', 'text': text}
        yield {'id': label + ':reversed-codepoints', 'sourceLabel': label,
               'characterOrder': 'reversed-codepoints', 'text': text[::-1]}


def validate_source(data):
    require(isinstance(data, dict) and set(data) == {'sourcePages', 'rows', 'streams', 'hits', 'summary'}, 'Source schema changed')
    require(data['sourcePages'] == SOURCE_PAGES and data['summary'] == SOURCE_SUMMARY, 'Source metadata changed')
    require(isinstance(data['rows'], list) and len(data['rows']) == 356, 'Source row count changed')
    for row in data['rows']:
        require(isinstance(row, dict) and set(row) == set(ROW_FIELDS), 'Source row schema changed')
        require(row['page'] in (2, 3, 4) and isinstance(row['text'], str), 'Source row field changed')
    require(len({(row['page'], row['region']) for row in data['rows']}) == 14, 'Source region count changed')
    require(isinstance(data['hits'], list) and not data['hits'], 'Historical hit metadata changed')
    streams = data['streams']
    require(isinstance(streams, dict) and len(streams) == 1940, 'Frozen stream count changed')
    dimensions = [Counter() for _ in LABEL_DIMENSIONS]
    for label, text in streams.items():
        require(isinstance(label, str) and isinstance(text, str), 'Invalid frozen stream field')
        parts = label.split(':')
        require(len(parts) == 5 and all(part in allowed for part, allowed in zip(parts, LABEL_DIMENSIONS)), 'Frozen label changed')
        for counts, part in zip(dimensions, parts):
            counts[part] += 1
    require(set(dimensions[0]) == set(SCOPES), 'Frozen scope coverage changed')
    require(dict(dimensions[3]) == {'forward': 970, 'reverse_lines': 970}, 'Frozen direction coverage changed')
    require(all(dimensions[4][projection] == 388 for projection in LABEL_DIMENSIONS[4]), 'Frozen projection coverage changed')
    lengths = [len(text) for text in streams.values()]
    require(sum(lengths) == 664764 and min(lengths) == 1 and max(lengths) == 13698, 'Frozen length metadata changed')
    return streams


def registered_blob(registration, relative):
    object_name = registration + ':public/research/' + relative
    size = subprocess.run(['git', 'cat-file', '-s', object_name], cwd=ROOT,
                          capture_output=True, timeout=30, check=False)
    require(size.returncode == 0 and len(size.stdout) <= 20 and
            re.fullmatch(rb'[0-9]+\n', size.stdout), 'Missing registration size')
    expected_size = int(size.stdout)
    require(expected_size <= DEFINITION['parameters']['maximumRegisteredBlobBytes'], 'Registered blob cap exceeded')
    result = subprocess.run(['git', 'cat-file', 'blob', object_name],
                            cwd=ROOT, capture_output=True, timeout=30, check=False)
    require(result.returncode == 0 and len(result.stdout) == expected_size, 'Missing registration bytes')
    return result.stdout


def validate_protocol_header(protocol, registration):
    require(re.fullmatch(r'[0-9a-f]{40}', registration or '') is not None, 'Full registration commit required')
    require(isinstance(protocol, dict) and set(protocol) == {'version', 'batchId', 'test', 'sourceHashes', 'scriptHashes'}, 'Protocol schema changed')
    require(type(protocol['version']) is int and protocol['version'] == 1 and
            protocol['batchId'] == BATCH_ID and protocol['test'] == code_definition(), 'Protocol differs from code definition')
    for key, paths in (('sourceHashes', INPUTS), ('scriptHashes', SCRIPTS)):
        require(isinstance(protocol[key], dict) and set(protocol[key]) == set(paths), 'Protocol pin population differs')
        require(all(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)
                    for value in protocol[key].values()), 'Invalid file pin')
    require(protocol['sourceHashes'][PRIMARY] == PRIMARY_SHA256, 'Frozen primary pin differs')


def verify_registered_bytes(registration, files, reader):
    # Pure equality helper; controls supply synthetic bytes and a mock reader.
    for relative, content in files.items():
        require(reader(registration, relative) == content, 'Registration bytes differ')


def validate_protocol(protocol_path, registration, blob_reader=None):
    require(re.fullmatch(r'[0-9a-f]{40}', registration or '') is not None, 'Full registration commit required')
    file = Path(protocol_path).resolve(strict=True)
    require(file.is_file() and file.is_relative_to(ROOT) and file.stat().st_size <= 1000000, 'Public protocol required')
    protocol_bytes = capped_read(file, 1000000)
    protocol = json.loads(protocol_bytes, object_pairs_hook=unique_json_object)
    validate_protocol_header(protocol, registration)
    files = {}
    for key, paths in (('sourceHashes', INPUTS), ('scriptHashes', SCRIPTS)):
        for relative in paths:
            expected = protocol[key][relative]
            pinned_file = research_file(relative)
            limit = DEFINITION['parameters']['maximumInputBytes'] if relative == PRIMARY else DEFINITION['parameters']['maximumRegisteredBlobBytes']
            content = capped_read(pinned_file, limit)
            if relative == PRIMARY:
                require(len(content) == 946620 and len(content) <= DEFINITION['parameters']['maximumInputBytes'], 'Primary byte cap changed')
            require(sha_bytes(content) == expected, 'Pinned file changed')
            files[relative] = content
    reader = blob_reader or registered_blob
    protocol_relative = file.relative_to(ROOT).as_posix()
    # The protocol itself, not merely its declared pins, must match the commit.
    require(protocol_relative not in files, 'Protocol cannot replace a pinned file')
    files[protocol_relative] = protocol_bytes
    verify_registered_bytes(registration, files, reader)
    return protocol, sha_bytes(protocol_bytes)


def safe_evaluation(evaluation):
    expected_keys = {'streamCount', 'uniqueStreamCount', 'uniqueFormCount', 'formats', 'shapeCounts',
                     'uniqueShapeCounts', 'executionCount', 'validCounts', 'hits', 'privateReviewRequired',
                     'fingerprintRule', 'networkQueries', 'rawAsciiScalarInterpretations'}
    require(isinstance(evaluation, dict) and set(evaluation) == expected_keys, 'Unexpected evaluator schema')
    require(evaluation['formats'] == list(FORMATS) and evaluation['fingerprintRule'] == FINGERPRINT_RULE, 'Evaluator scope differs')
    for key in ('streamCount', 'uniqueStreamCount', 'uniqueFormCount', 'executionCount', 'networkQueries', 'rawAsciiScalarInterpretations'):
        require(type(evaluation[key]) is int and evaluation[key] >= 0, 'Invalid evaluator count')
    for key in ('shapeCounts', 'uniqueShapeCounts', 'validCounts'):
        require(isinstance(evaluation[key], dict) and set(evaluation[key]) == set(FORMATS), 'Invalid evaluator count fields')
        require(all(type(value) is int and value >= 0 for value in evaluation[key].values()), 'Invalid evaluator counts')
    require(evaluation['networkQueries'] == 0 and evaluation['rawAsciiScalarInterpretations'] == 0, 'Forbidden evaluator action')
    require(isinstance(evaluation['hits'], list), 'Invalid evaluator hits')
    counts = Counter()
    for hit in evaluation['hits']:
        require(isinstance(hit, dict) and hit.get('format') in FORMATS, 'Unexpected hit format')
        kind = hit['format']
        fields = {'format', 'fingerprint', 'checkBits', 'private'}
        fields |= {'compressed'} if kind == 'wif' else {'length'} if kind == 'minikey' else {'wordCount'} if kind == 'bip39' else set()
        require(set(hit) == fields and hit['private'] is True, 'Unsafe hit metadata')
        require(isinstance(hit['fingerprint'], str) and re.fullmatch(r'[0-9a-f]{64}', hit['fingerprint']), 'Invalid record fingerprint')
        require(type(hit['checkBits']) is int, 'Invalid checksum metadata')
        if kind == 'wif':
            require(type(hit['compressed']) is bool and hit['checkBits'] == 32, 'Invalid WIF metadata')
        elif kind == 'minikey':
            require(type(hit['length']) is int and hit['length'] in (22, 30) and hit['checkBits'] == 8, 'Invalid minikey metadata')
        elif kind == 'hex64':
            require(hit['checkBits'] == 0, 'Invalid hex metadata')
        else:
            require(type(hit['wordCount']) is int and hit['wordCount'] in (12, 15, 18, 21, 24) and hit['checkBits'] == hit['wordCount'] // 3, 'Invalid mnemonic metadata')
        counts[kind] += 1
    require(all(counts[kind] == evaluation['validCounts'][kind] for kind in FORMATS), 'Hit counts disagree')
    require(len({(hit['format'], hit['fingerprint']) for hit in evaluation['hits']}) == len(evaluation['hits']), 'Duplicate safe record')
    require(evaluation['executionCount'] == sum(evaluation['uniqueShapeCounts'].values()), 'Validation execution counts differ')
    require(all(evaluation['shapeCounts'][kind] >= evaluation['uniqueShapeCounts'][kind] >= evaluation['validCounts'][kind]
                for kind in FORMATS), 'Validation count bounds differ')
    require(evaluation['uniqueStreamCount'] <= evaluation['streamCount'] and
            evaluation['uniqueStreamCount'] <= evaluation['uniqueFormCount'] <= 2 * evaluation['uniqueStreamCount'], 'Evaluator form bounds differ')
    require(type(evaluation['privateReviewRequired']) is bool and evaluation['privateReviewRequired'] == bool(evaluation['hits']), 'Lead classification differs')
    return deepcopy(evaluation)


def self_test():
    # This branch imports only shared code and its public controls/wordlist.
    # It never calls validate_source/validate_protocol or opens the target.
    from batch20_common import DEFAULT_FORMATS, fingerprint, self_test as common_self_test
    from batch20_common import scan_streams, shape_values, wordlist, validate_record
    require(DEFAULT_FORMATS == FORMATS, 'Shared default formats changed')
    shared = common_self_test()
    require(shared.get('passed') is True, 'Shared controls failed')
    sample = 'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'  # Published format example.
    fixture = {'synthetic-1': 'ab CD\u2003ef', 'synthetic-2': '', 'synthetic-3': 'aba'}
    readings = list(submitted_readings(fixture))
    require(len(readings) == 6 and len({r['id'] for r in readings}) == 6, 'Submitted reading control failed')
    require([r['text'] for r in readings] == ['ab CD\u2003ef', 'fe\u2003DC ba', '', '', 'aba', 'aba'], 'Literal reversal control failed')
    evaluation = safe_evaluation(scan_streams(readings, FORMATS))
    require(evaluation['streamCount'] == 6 and evaluation['uniqueStreamCount'] == 4 and evaluation['uniqueFormCount'] == 6, 'Deduplication control failed')
    public = safe_evaluation(scan_streams([{'id': 'published-control', 'text': '1' + sample + '1'}], FORMATS))
    require(public['validCounts']['minikey'] >= 1, 'Embedded minikey control failed')
    controls = json.loads((ROOT / 'scripts/batch20_support/controls.json').read_text())
    phrase = controls['bip39_valid'].split()
    indexes = wordlist()[1]
    require(len(phrase) == 12 and validate_record('bip39', ' '.join(phrase), indexes), 'Mnemonic control failed')
    for barrier in ('notaword', '12345', "can't", '␞'):
        interrupted = ' '.join(phrase[:6] + [barrier] + phrase[6:])
        require(not list(shape_values('bip39', interrupted, indexes)), 'Mnemonic barrier was discarded')
    decorated = ', '.join(word.upper() for word in phrase) + '.'
    require(' '.join(phrase) in list(shape_values('bip39', decorated, indexes)), 'Case/punctuation control failed')
    expected_fp = hashlib.sha256(b'KEY404/batch20/record-fingerprint/v1\x00minikey\x00' + sample.encode('ascii')).hexdigest()
    require(fingerprint('minikey', sample.encode('ascii')) == expected_fp, 'Fingerprint domain differs')
    require(expected_fp != hashlib.sha256(sample.encode('ascii')).hexdigest(), 'Unsafe scalar fingerprint')
    corrupted = deepcopy(public)
    corrupted['hits'][0]['value'] = sample
    try:
        safe_evaluation(corrupted)
    except ValueError:
        pass
    else:
        raise ValueError('Unsafe metadata was accepted')
    require(sample not in json.dumps(public), 'Control raw value leaked')
    registration = '1' * 40
    mock_protocol = {'version': 1, 'batchId': BATCH_ID, 'test': code_definition(),
                     'sourceHashes': {relative: '2' * 64 for relative in INPUTS},
                     'scriptHashes': {relative: '3' * 64 for relative in SCRIPTS}}
    mock_protocol['sourceHashes'][PRIMARY] = PRIMARY_SHA256
    validate_protocol_header(mock_protocol, registration)
    changed = deepcopy(mock_protocol)
    changed['test']['parameters']['formats'].append('address')
    invalid_protocols = [changed, dict(mock_protocol, sourceHashes={}), dict(mock_protocol, extra='unregistered')]
    for invalid in invalid_protocols:
        try:
            validate_protocol_header(invalid, registration)
        except ValueError:
            pass
        else:
            raise ValueError('Protocol mismatch was accepted')
    synthetic_files = {'control-protocol': b'{"control": true}\n', 'control-script': b'control bytes\n'}
    verify_registered_bytes(registration, synthetic_files, lambda commit, relative: synthetic_files[relative])
    try:
        verify_registered_bytes(registration, synthetic_files, lambda commit, relative: synthetic_files[relative] + b' ')
    except ValueError:
        pass
    else:
        raise ValueError('Registration byte drift was accepted')
    return {'passed': True, 'controls': DEFINITION['controls'], 'shared': shared,
            'syntheticSubmittedRecords': 6, 'syntheticUniqueForms': 6,
            'mnemonicBarrierCases': 4, 'syntheticProtocolGuards': 5,
            'targetInputsRead': False, 'targetRecordChecks': 0,
            'networkQueries': 0, 'transactions': 0}


def run(args):
    require(re.fullmatch(r'[0-9a-f]{40}', args.registration_commit or '') is not None, 'Full registration commit required')
    out = private_output(args.out)
    out.mkdir(mode=0o700)
    require(out.stat().st_mode & 0o077 == 0, 'Private output mode required')
    result = {'schemaVersion': 1, 'batchId': BATCH_ID, 'testId': DEFINITION['id'],
              'startedAtUTC': utc(), 'registrationCommit': args.registration_commit,
              'scopeComplete': False, 'completeNegative': False, 'privateReviewRequired': False,
              'networkQueries': 0, 'transactions': 0}
    try:
        controls = self_test()
        protocol, protocol_hash = validate_protocol(args.protocol, args.registration_commit)
        # No target text is parsed before controls and all registration pins pass.
        primary_file = research_file(PRIMARY)
        content = capped_read(primary_file, DEFINITION['parameters']['maximumInputBytes'])
        require(len(content) == 946620 and sha_bytes(content) == PRIMARY_SHA256, 'Primary changed after pin validation')
        streams = validate_source(json.loads(content))
        readings = list(submitted_readings(streams))
        p = DEFINITION['parameters']
        require(len(readings) == p['expectedSubmittedRecords'] and len(readings) <= p['maximumSubmittedRecords'], 'Submitted reading cap failed')
        submitted_characters = sum(len(r['text']) for r in readings)
        require(submitted_characters <= p['maximumSubmittedCodePoints'], 'Submitted character cap failed')
        # The shared scanner creates at most two forms per submitted record,
        # each no longer than the original. These are pre-execution upper bounds.
        require(2 * len(readings) <= p['maximumUniqueForms'] and
                2 * submitted_characters <= p['maximumUniqueFormCodePoints'], 'Form resource cap failed')
        with os.fdopen(os.open(out / 'READINGS.private.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                       'w', encoding='utf-8') as handle:
            for reading in readings:
                handle.write(json.dumps(reading, ensure_ascii=True) + '\n')
        from batch20_common import DEFAULT_FORMATS, scan_streams
        require(DEFAULT_FORMATS == FORMATS, 'Shared default formats changed')
        evaluation = safe_evaluation(scan_streams(readings, FORMATS))
        require(evaluation['streamCount'] == 3880 and evaluation['uniqueFormCount'] <= 7760, 'Actual evaluation coverage differs')
        lead = evaluation['privateReviewRequired']
        result.update(protocolSha256=protocol_hash, sourceHashes=protocol['sourceHashes'],
                      scriptHashes=protocol['scriptHashes'], parameters=p, controls=controls,
                      procedureCounts={'sourceRows': 356, 'sourceRegions': 14, 'sourceStreams': 1940,
                                       'submittedRecords': len(readings), 'submittedCodePoints': submitted_characters,
                                       'uniqueFormsMaximum': 7760, 'perStreamHashes': False},
                      evaluation=evaluation, scopeComplete=True, completeNegative=not lead,
                      privateReviewRequired=lead,
                      outcome='finding-private-review-required' if lead else 'no-valid-record-in-registered-issue27-streams',
                      negativeCriterion=DEFINITION['negativeCriterion'], limitations=DEFINITION['limitations'],
                      privateArtifacts=['READINGS.private.jsonl'])
    except Exception as error:
        private_json(out / 'ERROR.private.json', {'errorClass': type(error).__name__, 'error': 'Registered execution failed; no negative claim.'})
        result.update(outcome='inconclusive-control-pin-source-or-execution', errorClass=type(error).__name__,
                      error='Controls, registration bytes, frozen source, bounds or evaluation failed. No negative claim.')
    result['completedAtUTC'] = utc()
    private_json(out / 'RESULT.json', result)
    print(json.dumps({key: result[key] for key in ('testId', 'outcome', 'scopeComplete',
                                                 'completeNegative', 'privateReviewRequired', 'networkQueries')}))
    return result


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('Invalid arguments')


def main(argv=None):
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true')
    group.add_argument('--self-test', action='store_true')
    group.add_argument('--run', action='store_true')
    parser.add_argument('--protocol')
    parser.add_argument('--registration-commit')
    parser.add_argument('--out')
    arguments = sys.argv[1:] if argv is None else list(argv)
    for option in ('--list', '--self-test', '--run', '--protocol', '--registration-commit', '--out'):
        require(sum(value == option or value.startswith(option + '=') for value in arguments) <= 1, 'Duplicate argument')
    args = parser.parse_args(arguments)
    if args.list or args.self_test:
        require(not args.protocol and not args.registration_commit and not args.out, 'Mixed action arguments')
        print(json.dumps(code_definition() if args.list else self_test(), indent=2))
        return 0
    require(args.protocol and args.registration_commit and args.out, 'Run requires protocol, registration commit and fresh private output')
    result = run(args)
    return 0 if result['scopeComplete'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        print(json.dumps({'outcome': 'inconclusive-before-execution', 'scopeComplete': False,
                          'completeNegative': False, 'networkQueries': 0}), file=sys.stderr)
        sys.exit(1)
