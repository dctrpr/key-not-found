#!/usr/bin/env python3
"""Independent saved-reading verifier; stdlib only, no shared scanner import.

--self-test opens only the pinned public wordlist/controls. Explicit --verify
requires result, readings, frozen primary, and a fresh private output directory.
Never prints/persists a candidate, scalar, mnemonic, address or record locator.
There is no network, wallet, address derivation, seed derivation or Git code.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
SUPPORT = Path(__file__).resolve().parent / 'batch20_support'
if not SUPPORT.is_dir():
    # Original private staging location under outputs/research-next-*/<task>.
    SUPPORT = Path(__file__).resolve().parents[3] / 'site/public/research/scripts/batch20_support'
PRIMARY_SHA256 = 'f5f441345ebe411ee769cdcb624c0717a2b4f790b7eadc50d10dc12d37da07bb'
ENGLISH_SHA256 = '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda'
CONTROLS_SHA256 = 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b'
PRIMARY_RELATIVE = 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json'
FORMATS = ('wif', 'minikey', 'hex64', 'bip39')
BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
BASE58_INDEX = {char: index for index, char in enumerate(BASE58)}
HEX = set('0123456789abcdefABCDEF')
ORDER_BYTES = bytes.fromhex('fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141')
DOMAIN = b'KEY404/batch20/record-fingerprint/v1\x00'
FINGERPRINT_RULE = {'algorithm': 'SHA-256', 'domainText': 'KEY404/batch20/record-fingerprint/v1',
                    'separatorHex': '00',
                    'rule': 'SHA256(domain || 0x00 || ASCII(format) || 0x00 || canonical record bytes)'}
MAX_RECORDS = 3880
MAX_FORMS = 7760
MAX_SUBMITTED_CHARACTERS = 2000000
MAX_FORM_CHARACTERS = 4000000


def require(condition):
    if not condition:
        raise ValueError('Independent validation failed')


def digest(data):
    return hashlib.sha256(data).digest()


def record_fingerprint(kind, canonical):
    return hashlib.sha256(DOMAIN + kind.encode('ascii') + b'\x00' + canonical).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result)
        result[key] = value
    return result


def bounded_bytes(file, maximum):
    require(file.is_file() and file.stat().st_size <= maximum)
    with file.open('rb') as handle:
        content = handle.read(maximum + 1)
    require(len(content) <= maximum)
    return content


def wordlist():
    raw = bounded_bytes(SUPPORT / 'english.txt', 20000)
    require(hashlib.sha256(raw).hexdigest() == ENGLISH_SHA256)
    words = raw.decode('ascii').splitlines()
    require(len(words) == len(set(words)) == 2048)
    return words, {word: index for index, word in enumerate(words)}


def scalar_bytes_valid(value):
    return len(value) == 32 and any(value) and value < ORDER_BYTES


def decode_base58check(text):
    # Independent positional decoder; leading-zero bytes and checksum retained.
    number = 0
    for char in text:
        if char not in BASE58_INDEX:
            return None
        number = number * 58 + BASE58_INDEX[char]
    leading = len(text) - len(text.lstrip('1'))
    raw = b'\0' * leading + (number.to_bytes((number.bit_length() + 7) // 8, 'big') if number else b'')
    if len(raw) < 5 or digest(digest(raw[:-4]))[:4] != raw[-4:]:
        return None
    return raw[:-4]


def mnemonic_checksum(words, indexes):
    if len(words) not in (12, 15, 18, 21, 24) or any(word not in indexes for word in words):
        return False
    # Accumulate 11-bit indices, split checksum with masks, hash only entropy.
    packed = 0
    for word in words:
        packed = (packed << 11) | indexes[word]
    checksum_length = len(words) // 3
    entropy_length = len(words) * 11 - checksum_length
    entropy = (packed >> checksum_length).to_bytes(entropy_length // 8, 'big')
    supplied = packed & ((1 << checksum_length) - 1)
    expected = digest(entropy)[0] >> (8 - checksum_length)
    return supplied == expected


def validate(kind, value, indexes):
    if kind == 'minikey':
        if len(value) in (22, 30) and value.startswith('S') and all(c in BASE58_INDEX for c in value):
            encoded = value.encode('ascii')
            if digest(encoded + b'?')[0] == 0:
                return encoded, {'length': len(value), 'checkBits': 8, 'private': True}
    elif kind == 'wif':
        payload = decode_base58check(value)
        if payload and len(payload) in (33, 34) and payload[0] == 0x80:
            if (len(payload) == 33 or payload[33] == 1) and scalar_bytes_valid(payload[1:33]):
                return payload, {'compressed': len(payload) == 34, 'checkBits': 32, 'private': True}
    elif kind == 'hex64':
        if len(value) == 64 and all(char in HEX for char in value):
            raw = bytes.fromhex(value)
            if scalar_bytes_valid(raw):
                return raw, {'checkBits': 0, 'private': True}
    elif kind == 'bip39':
        words = value.split(' ')
        if mnemonic_checksum(words, indexes):
            return value.encode('ascii'), {'wordCount': len(words), 'checkBits': len(words) // 3, 'private': True}
    return None


def ascii_alnum(char):
    return 'a' <= char <= 'z' or 'A' <= char <= 'Z' or '0' <= char <= '9'


def lexical_tokens(region):
    # Manual lexer equivalent to ASCII alnum+(apostrophe+alnum+)*. Unknown
    # words, numbers and internal apostrophes remain tokens, never deletions.
    offset = 0
    while offset < len(region):
        if not ascii_alnum(region[offset]):
            offset += 1
            continue
        start = offset
        offset += 1
        while offset < len(region):
            if ascii_alnum(region[offset]):
                offset += 1
            elif region[offset] in ("'", '’') and offset + 1 < len(region) and ascii_alnum(region[offset + 1]):
                offset += 2
            else:
                break
        yield region[start:offset].lower()


def shapes(kind, text, indexes):
    if kind in ('wif', 'minikey'):
        starts, lengths = (('5KL', (51, 52)) if kind == 'wif' else ('S', (22, 30)))
        for offset, first in enumerate(text):
            if first not in starts:
                continue
            for length in lengths:
                end = offset + length
                if end <= len(text):
                    value = text[offset:end]
                    if all(char in BASE58_INDEX for char in value):
                        yield value
    elif kind == 'hex64':
        offset = 0
        while offset < len(text):
            if text[offset] not in HEX:
                offset += 1
                continue
            start = offset
            while offset < len(text) and text[offset] in HEX:
                offset += 1
            if offset - start == 64:
                yield text[start:offset]
    elif kind == 'bip39':
        for region in text.split('␞'):
            tokens = list(lexical_tokens(region))
            for length in (12, 15, 18, 21, 24):
                for offset in range(len(tokens) - length + 1):
                    chunk = tokens[offset:offset + length]
                    if all(token in indexes for token in chunk):
                        yield ' '.join(chunk)


def evaluate(records, indexes):
    require(isinstance(records, list) and len(records) <= MAX_RECORDS)
    require(all(isinstance(record, dict) and isinstance(record.get('text'), str) for record in records))
    require(sum(len(record['text']) for record in records) <= MAX_SUBMITTED_CHARACTERS)
    unique = {record['text'] for record in records}
    forms = unique | {''.join(char for char in text if not char.isspace()) for text in unique}
    require(len(forms) <= MAX_FORMS and sum(map(len, forms)) <= MAX_FORM_CHARACTERS)
    counts = {kind: 0 for kind in FORMATS}
    tested = {kind: set() for kind in FORMATS}
    valid = {kind: {} for kind in FORMATS}
    for text in sorted(forms):
        for kind in FORMATS:
            for value in shapes(kind, text, indexes):
                counts[kind] += 1
                if value in tested[kind]:
                    continue
                tested[kind].add(value)
                result = validate(kind, value, indexes)
                if result is not None:
                    canonical, metadata = result
                    fingerprint = record_fingerprint(kind, canonical)
                    valid[kind].setdefault(fingerprint, {'format': kind, 'fingerprint': fingerprint, **metadata})
    hits = [value for kind in FORMATS for _, value in sorted(valid[kind].items())]
    return {'streamCount': len(records), 'uniqueStreamCount': len(unique), 'uniqueFormCount': len(forms),
            'formats': list(FORMATS), 'shapeCounts': counts,
            'uniqueShapeCounts': {kind: len(tested[kind]) for kind in FORMATS},
            'executionCount': sum(map(len, tested.values())),
            'validCounts': {kind: len(valid[kind]) for kind in FORMATS},
            'hits': hits, 'privateReviewRequired': bool(hits), 'fingerprintRule': FINGERPRINT_RULE,
            'networkQueries': 0, 'rawAsciiScalarInterpretations': 0}


def compare_saved_to_primary(primary, records):
    require(isinstance(primary, dict) and set(primary) == {'sourcePages', 'rows', 'streams', 'hits', 'summary'})
    require(primary['sourcePages'] == {'2': 79, '3': 80, '4': 81} and len(primary['rows']) == 356)
    streams = primary['streams']
    require(isinstance(streams, dict) and len(streams) == 1940 and len(records) == 3880)
    position = 0
    for label in sorted(streams):
        require(isinstance(label, str) and isinstance(streams[label], str))
        for order, text in (('exact', streams[label]), ('reversed-codepoints', streams[label][::-1])):
            expected = {'id': label + ':' + order, 'sourceLabel': label, 'characterOrder': order, 'text': text}
            require(records[position] == expected)
            position += 1
    require(position == 3880 and len({record['id'] for record in records}) == 3880)


def encode_base58check(payload):
    # Public/synthetic controls only; verification never encodes target secrets.
    raw = payload + digest(digest(payload))[:4]
    number = int.from_bytes(raw, 'big')
    result = ''
    while number:
        number, remainder = divmod(number, 58)
        result = BASE58[remainder] + result
    return '1' * (len(raw) - len(raw.lstrip(b'\0'))) + result


def synthetic_mnemonic(entropy, words):
    # Independent control generator uses bit strings rather than validator math.
    entropy_bits = ''.join(format(octet, '08b') for octet in entropy)
    check_length = len(entropy_bits) // 32
    bit_string = entropy_bits + ''.join(format(octet, '08b') for octet in digest(entropy))[:check_length]
    return ' '.join(words[int(bit_string[offset:offset + 11], 2)] for offset in range(0, len(bit_string), 11))


def self_test():
    words, indexes = wordlist()
    control_bytes = bounded_bytes(SUPPORT / 'controls.json', 2000)
    require(hashlib.sha256(control_bytes).hexdigest() == CONTROLS_SHA256)
    controls = json.loads(control_bytes, object_pairs_hook=unique_object)
    sample = 'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'
    require(validate('minikey', sample, indexes) is not None)
    short = None
    for number in range(65536):
        encoded, remaining = '', number
        while True:
            remaining, digit = divmod(remaining, 58)
            encoded = BASE58[digit] + encoded
            if not remaining:
                break
        control = 'S' + '2' * 15 + encoded.rjust(6, '2')
        if validate('minikey', control, indexes):
            short = control
            break
    require(short is not None and len(short) == 22)
    require(sample in set(shapes('minikey', '1' + sample + '1', indexes)))
    require(short in set(shapes('minikey', '1' + short + '1', indexes)))
    require(validate('minikey', 'T' + sample[1:], indexes) is None)
    require(validate('minikey', 'S0' + sample[2:], indexes) is None)
    bad_checksum = next(sample[:-1] + last for last in BASE58
                        if digest((sample[:-1] + last).encode('ascii') + b'?')[0] != 0)
    require(validate('minikey', bad_checksum, indexes) is None)
    one = bytes(31) + b'\x01'
    uncompressed = encode_base58check(b'\x80' + one)
    compressed = encode_base58check(b'\x80' + one + b'\x01')
    require(uncompressed == '5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3kEsreAnchuDf')
    require(compressed == 'KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn')
    require(validate('wif', uncompressed, indexes)[0] == b'\x80' + one)
    require(validate('wif', compressed, indexes)[0] == b'\x80' + one + b'\x01')
    require(compressed in set(shapes('wif', '1' + compressed + '1', indexes)))
    for payload in (b'\x80' + bytes(32), b'\x80' + ORDER_BYTES, b'\x80' + one + b'\x02', b'\xef' + one):
        require(validate('wif', encode_base58check(payload), indexes) is None)
    require(validate('wif', compressed[:-1] + ('1' if compressed[-1] != '1' else '2'), indexes) is None)
    require(validate('hex64', one.hex(), indexes)[0] == one)
    require(validate('hex64', '0' * 64, indexes) is None)
    require(validate('hex64', ORDER_BYTES.hex(), indexes) is None)
    require(list(shapes('hex64', 'Z' + one.hex() + 'G', indexes)) == [one.hex()])
    require(not list(shapes('hex64', 'a' + one.hex(), indexes)))
    require(not list(shapes('hex64', one.hex() + 'f', indexes)))
    phrase = controls['bip39_valid']
    require(mnemonic_checksum(phrase.split(), indexes))
    require(not mnemonic_checksum(['abandon'] * 12, indexes))
    phrases = [synthetic_mnemonic(bytes(size), words) for size in (16, 20, 24, 28, 32)]
    require(all(mnemonic_checksum(phrase.split(), indexes) for phrase in phrases))
    base = phrase.split()
    for barrier in ('unknownword', '12345', "can't", 'can’t', '␞'):
        interrupted = ' '.join(base[:6] + [barrier] + base[6:])
        require(not list(shapes('bip39', interrupted, indexes)))
    require(phrase in list(shapes('bip39', ', '.join(base).upper() + '.', indexes)))
    fixture = [sample, short, uncompressed, compressed, one.hex(), '0' * 64, phrase, phrase.upper()] + phrases
    records = [{'text': text} for text in fixture]
    evaluated = evaluate(records, indexes)
    require(evaluated['validCounts']['minikey'] >= 2 and evaluated['validCounts']['wif'] == 2)
    require(evaluated['validCounts']['hex64'] == 1 and evaluated['validCounts']['bip39'] == 5)
    require(evaluate(list(reversed(records)), indexes) == evaluated)
    for kind, value in (('minikey', sample), ('minikey', short), ('wif', uncompressed),
                        ('wif', compressed), ('hex64', one.hex()), ('bip39', phrase)):
        canonical, metadata = validate(kind, value, indexes)
        expected = hashlib.sha256(b'KEY404/batch20/record-fingerprint/v1\x00' + kind.encode('ascii') + b'\x00' + canonical).hexdigest()
        require(any(hit == {'format': kind, 'fingerprint': expected, **metadata} for hit in evaluated['hits']))
    safe = json.dumps(evaluated)
    require(all(value not in safe for value in (sample, short, uncompressed, compressed, phrase, one.hex())))
    require(list(lexical_tokens("A12 can't can’t ab''CD x_y")) == ['a12', "can't", 'can’t', 'ab', 'cd', 'x', 'y'])
    for lexical_fixture in ("can't''can’t", 'Alpha123 Ω beta café XéY', 'a\u2003b\nC', "ab’CD'ef", '␞ab:12_c'):
        oracle = [match.group(0).lower() for match in re.finditer(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*", lexical_fixture)]
        require(list(lexical_tokens(lexical_fixture)) == oracle)
    synthetic_primary = {'sourcePages': {'2': 79, '3': 80, '4': 81}, 'rows': [None] * 356,
                         'streams': {'control-' + str(n).zfill(4): 'Alpha\u2003Beta' for n in range(1940)},
                         'hits': [], 'summary': {}}
    synthetic_saved = []
    for label in sorted(synthetic_primary['streams']):
        text = synthetic_primary['streams'][label]
        for order, value in (('exact', text), ('reversed-codepoints', text[::-1])):
            synthetic_saved.append({'id': label + ':' + order, 'sourceLabel': label,
                                    'characterOrder': order, 'text': value})
    compare_saved_to_primary(synthetic_primary, synthetic_saved)
    synthetic_saved[0] = {**synthetic_saved[0], 'text': 'Changed control'}
    try:
        compare_saved_to_primary(synthetic_primary, synthetic_saved)
    except ValueError:
        pass
    else:
        raise ValueError('Independent validation failed')
    return {'status': 'PASS', 'controlFamilies': ['published-minikey30', 'bounded-synthetic-minikey22',
            'published-scalar-one-WIF-compressed-uncompressed', 'WIF-invalid-version-marker-checksum-scalars',
            'hex-boundaries-and-scalar-range', 'BIP39-all-five-lengths', 'BIP39-unfiltered-five-barriers',
            'independent-positive-fingerprints', 'deterministic-counts', 'safe-output'],
            'validControlRecords': sum(evaluated['validCounts'].values()), 'formats': list(FORMATS),
            'syntheticSourceComparisonRecords': 3880, 'lexicalOracleCases': 5,
            'targetInputsRead': False, 'targetShapeScans': 0, 'targetChecksumValidations': 0,
            'networkQueries': 0}


def private_path(value, existing=False):
    file = Path(value).expanduser().resolve()
    require(not any(part.lower() == 'public' for part in file.parts))
    if existing:
        require(file.is_file() and file.stat().st_mode & 0o077 == 0)
    return file


def save_private(file, value):
    with os.fdopen(os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=True)
        handle.write('\n')


def verify(args):
    # Target I/O occurs ONLY through this explicit post-registration entry.
    out = private_path(args.out)
    require(not out.exists() and out.parent.is_dir())
    out.mkdir(mode=0o700)
    receipt = {'status': 'FAIL', 'passed': False, 'scopeComplete': False, 'networkQueries': 0}
    try:
        controls = self_test()
        result_file = private_path(args.result, existing=True)
        readings_file = private_path(args.readings, existing=True)
        result = json.loads(bounded_bytes(result_file, 16000000), object_pairs_hook=unique_object)
        require(result.get('batchId') == 'keiser-issue27-stream-coverage-20261110')
        require(result.get('testId') == 'issue27-frozen-stream-coverage')
        require(result.get('scopeComplete') is True and result.get('networkQueries') == 0 and result.get('transactions') == 0)
        require(re.fullmatch(r'[0-9a-f]{40}', result.get('registrationCommit', '')))
        require(re.fullmatch(r'[0-9a-f]{64}', result.get('protocolSha256', '')))
        require(result.get('sourceHashes', {}).get(PRIMARY_RELATIVE) == PRIMARY_SHA256)
        records = []
        saved_bytes = bounded_bytes(readings_file, 32000000)
        submitted_characters = 0
        for line in saved_bytes.decode('utf-8').splitlines():
            require(len(line) <= 1000000 and len(records) < MAX_RECORDS)
            record = json.loads(line, object_pairs_hook=unique_object)
            require(isinstance(record, dict) and isinstance(record.get('text'), str))
            submitted_characters += len(record['text'])
            require(submitted_characters <= MAX_SUBMITTED_CHARACTERS)
            records.append(record)
        primary_file = Path(args.primary).expanduser().resolve(strict=True)
        primary_bytes = bounded_bytes(primary_file, 2000000)
        require(len(primary_bytes) == 946620 and hashlib.sha256(primary_bytes).hexdigest() == PRIMARY_SHA256)
        primary = json.loads(primary_bytes, object_pairs_hook=unique_object)
        compare_saved_to_primary(primary, records)
        _, indexes = wordlist()
        evaluation = evaluate(records, indexes)
        require(evaluation == result.get('evaluation'))
        require(result.get('privateReviewRequired') is evaluation['privateReviewRequired'])
        require(result.get('completeNegative') is (not evaluation['privateReviewRequired']))
        receipt = {'schemaVersion': 1, 'status': 'PASS', 'passed': True, 'scopeComplete': True,
                   'testId': result['testId'], 'registrationCommit': result['registrationCommit'],
                   'protocolSha256': result['protocolSha256'], 'primarySha256': PRIMARY_SHA256,
                   'savedReadingsExactlyMatchPrimary': True, 'verifiedSubmittedRecords': len(records),
                   'evaluation': evaluation, 'controls': controls, 'networkQueries': 0,
                   'scope': 'Independent saved-reading source equality, forms, actual positive/negative validation and domain-separated fingerprints; no new readings or downstream key/address use'}
    except Exception as error:
        receipt.update(errorClass=type(error).__name__, error='Independent validation failed; no agreement claim.')
    receipt['completedAtUTC'] = datetime.now(timezone.utc).isoformat()
    save_private(out / 'INDEPENDENT_CHECK.json', receipt)
    print(json.dumps({'status': receipt['status'], 'passed': receipt['passed'],
                      'scopeComplete': receipt['scopeComplete'], 'networkQueries': 0}))
    return 0 if receipt['passed'] else 1


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('Invalid arguments')


def main(argv=None):
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--self-test', action='store_true')
    actions.add_argument('--verify', action='store_true')
    parser.add_argument('--result')
    parser.add_argument('--readings')
    parser.add_argument('--primary')
    parser.add_argument('--out')
    arguments = list(sys.argv[1:] if argv is None else argv)
    for option in ('--self-test', '--verify', '--result', '--readings', '--primary', '--out'):
        require(sum(value == option or value.startswith(option + '=') for value in arguments) <= 1)
    args = parser.parse_args(arguments)
    if args.self_test:
        require(not any((args.result, args.readings, args.primary, args.out)))
        print(json.dumps(self_test(), indent=2))
        return 0
    require(all((args.result, args.readings, args.primary, args.out)))
    return verify(args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        print(json.dumps({'status': 'FAIL', 'passed': False, 'scopeComplete': False, 'networkQueries': 0}), file=sys.stderr)
        sys.exit(1)
