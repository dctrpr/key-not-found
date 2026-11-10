#!/usr/bin/env python3
"""Independent G07 saved-output adapter; no primary runner is imported.

The frozen a4bf independent pure form/common4/minikey26 functions are reused;
common4 shape/validation mathematics remains the same pinned shared engine.
--self-test is synthetic/support-only. --verify requires an actual public Git
commit and all declared current/registered bytes before target JSON parsing.
Python3.9+ and the registration commit object are required; no ZIP bypass.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import types
import json
from pathlib import Path
import subprocess
import sys

TEST_ID = 'g07-supplemental-fixed-formats'
BATCH_ID = 'keiser-g07-supplemental-fixed-formats-20261110'
SELF_REL = 'scripts/verify_g07_supplemental.py'
PROTOCOL_REL = 'analysis_outputs/continuation_20261110/g07_supplemental/PROTOCOL.json'
SOURCE_REL = 'analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json'
OLD_RESULT_REL = 'analysis_outputs/continuation_20261110/batch20/G07/RESULT.json'
OLD_CHECK_REL = 'analysis_outputs/continuation_20261110/batch20/G07/INDEPENDENT_CHECK.json'
CORE_REL = 'scripts/verify_batch20_supplemental.py'
CORE_SHA = 'a4bf930523eb29c0da942439eb6005514fc60d0dfb4f6deede2171380bd4389c'
COMMON4 = ['extended_private', 'bip38', 'address', 'sec_public']
_CORE = None
_COMMON = None

class GuardError(Exception):
    pass

def need(value, code):
    if not value:
        raise GuardError(code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)

SOURCE_PINS = {'analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json': 'e934e778c07cba19c00c6e4fb7cb8f858042f904d320f0d919a59fa1e4c3e7da',
 'analysis_outputs/continuation_20261110/batch20/G07/RESULT.json': 'fc3ab1acf7e97b6061341065d3e9c9a64626b37ee985a86db9147aa412742513',
 'analysis_outputs/continuation_20261110/batch20/G07/INDEPENDENT_CHECK.json': 'f57582748af54a9ba5bec0a1db67f74ca69471f57b7859217a2de7bd432c1d4a',
 'scripts/batch20_support/vision-datamatrix-control.png': '4f395fb1356cfa598ef08f3aaa07d372e1b836c6bc7bc08a6820a4584db2facc',
 'scripts/batch20_support/vision-datamatrix-control.txt': '84d89877f0d4041efb6bf91a16f0248f2fd573e6af05c19f96bedb9f882f7882',
 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',
 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b',
 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}
SCRIPT_PATHS = {'scripts/batch20_common.py',
 'scripts/batch20_supplemental_formats.py',
 'scripts/g07_supplemental_formats.py',
 'scripts/verify_batch20_supplemental.py',
 'scripts/verify_g07_supplemental.py'}
FIXED_CODE_PINS = {'scripts/batch20_supplemental_formats.py': '385524773ef0c20a2af1858bbf1d1f15cb45fd47fdf08627b0b97d2dda2754ac',
 'scripts/verify_batch20_supplemental.py': 'a4bf930523eb29c0da942439eb6005514fc60d0dfb4f6deede2171380bd4389c',
 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}
EXPECTATIONS = {'labeledStreams': 1038,
 'uniqueStreams': 833,
 'uniqueForms': 1464,
 'emptyTexts': 14,
 'maxTextCodepoints': 1748,
 'totalTextCodepoints': 42110,
 'legacyMinikeyShapeOccurrences': 4,
 'legacyMinikeyUniqueShapes': 3}
CAPS = {'sourceJsonBytes': 2000000,
 'registeredBlobBytes': 20000000,
 'protocolBytes': 1000000,
 'privateArtifactBytes': 20000000,
 'totalSourceCodepoints': 50000,
 'totalFormCodepoints': 100000,
 'streamCodepoints': 2000,
 'shapeOccurrencesPerCohort': 1000000,
 'uniqueShapesPerCohort': 500000}
EXPECTED_ACTIVITY = {'ocrReruns': 0,
 'sourceSelectorRegenerations': 0,
 'newTransformsBeyondExistingForms': 0,
 'newJoinsOrRepairs': 0,
 'oldSharedMinikeyCalls': 0,
 'minikeyScalarHashes': 0,
 'proseToKeyHashes': 0,
 'scalarDerivations': 0,
 'addressDerivations': 0,
 'seedDerivations': 0,
 'childKeyDerivations': 0,
 'networkQueries': 0,
 'transactions': 0}
LIMITATIONS = ['Compatibility replay of the exact saved G07 OCR outputs, not a new extraction theory or source-selection '
 'test.',
 'OCR misses, unusual/damaged text, and the quality of original112detector views remain outside added-format '
 'coverage.',
 'Four shared validators are unchanged and shared; a weak8bit minikey or on-curve SEC is only a review lead, '
 'not ownership/funding/prize proof.',
 'No semantic recognition, source geometry conclusion or whole-puzzle exclusion is computed.']
NORMATIVE_TEST_SHA256 = '97787e748c2cefa4ac312389744cc4e3a9eecac0288c06171448017e626cf75a'

def core():
    global _CORE
    if _CORE is None:
        sibling = Path(__file__).resolve().parent / 'verify_batch20_supplemental.py'
        fallback = Path(__file__).resolve().parents[3] / 'site/public/research/scripts/verify_batch20_supplemental.py'
        file = sibling if sibling.is_file() else fallback
        need(file.is_file() and file.stat().st_size <= 2_000_000, 'frozen-independent-core-file-guard')
        raw = file.read_bytes()
        need(digest(raw) == CORE_SHA, 'frozen-independent-core-pin-mismatch')
        module = types.ModuleType('g07_independent_frozen_core')
        module.__file__ = str(file)
        exec(compile(raw, str(file), 'exec'), module.__dict__)
        _CORE = module
    return _CORE


def load_common():
    global _COMMON
    if _COMMON is None:
        file = Path(core().__file__).resolve().parent / 'batch20_common.py'
        need(file.is_file() and file.stat().st_size <= 2_000_000, 'shared-common-file-guard')
        raw = file.read_bytes()
        need(digest(raw) == SOURCE_PINS['scripts/batch20_common.py'], 'shared-common-byte-pin-mismatch')
        for name in ['english.txt', 'controls.json']:
            support = file.parent / 'batch20_support' / name
            need(support.is_file() and support.stat().st_size <= 2_000_000 and
                 digest(support.read_bytes()) == SOURCE_PINS['scripts/batch20_support/' + name],
                 'shared-support-byte-pin-mismatch')
        module = types.ModuleType('g07_pinned_shared_four')
        module.__file__ = str(file)
        exec(compile(raw, str(file), 'exec'), module.__dict__)
        _COMMON = module
    return _COMMON


def validate_test(test):
    need(isinstance(test, dict) and digest(canonical(test).encode('utf-8')) == NORMATIVE_TEST_SHA256,
         'normative-protocol-test-mismatch')


def registration(protocol_path, commit):
    helper = core()
    need(isinstance(commit, str) and len(commit) == 40 and all(c in '0123456789abcdef' for c in commit),
         'full-Git-registration-commit-required')
    research = Path(__file__).resolve().parent.parent
    need((research / SELF_REL).resolve() == Path(__file__).resolve(), 'installed-public-verifier-required')
    need(Path(protocol_path).resolve() == (research / PROTOCOL_REL).resolve(), 'fixed-protocol-path-required')
    helper.verify_commit_object(research, commit)
    protocol, raw = helper.read_json(protocol_path, CAPS['protocolBytes'])
    need(protocol.get('version') == 1 and protocol.get('batchId') == BATCH_ID, 'protocol-identity-mismatch')
    validate_test(protocol.get('test'))
    sources, scripts = protocol.get('sourceHashes'), protocol.get('scriptHashes')
    need(canonical(sources) == canonical(SOURCE_PINS) and isinstance(scripts, dict) and
         set(scripts) == SCRIPT_PATHS and all(scripts.get(name) == pin for name, pin in FIXED_CODE_PINS.items()),
         'source-or-code-pin-set-mismatch')
    pins = dict(sources)
    pins.update(scripts)
    pins[PROTOCOL_REL] = digest(raw)
    for relative, expected in pins.items():
        need(isinstance(expected, str) and len(expected) == 64 and
             all(c in '0123456789abcdef' for c in expected), 'invalid-SHA256-pin')
        file = (research / relative).resolve()
        need(file.is_relative_to(research) and file.is_file() and
             file.stat().st_size <= CAPS['registeredBlobBytes'], 'registered-current-file-guard')
        need(digest(file.read_bytes()) == expected, 'current-byte-pin-mismatch')
        saved = subprocess.run(['git', 'show', commit + ':public/research/' + relative], cwd=research,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        need(saved.returncode == 0 and len(saved.stdout) <= CAPS['registeredBlobBytes'] and
             digest(saved.stdout) == expected, 'registered-byte-pin-mismatch')
    return protocol, digest(raw), research


def validate_source(streams, production=True):
    need(isinstance(streams, list) and 0 < len(streams) <= EXPECTATIONS['labeledStreams'], 'invalid-saved-stream-list')
    identifiers, lengths = [], []
    for record in streams:
        need(isinstance(record, dict) and set(record) == {'id', 'text'} and
             isinstance(record['id'], str) and record['id'] and isinstance(record['text'], str),
             'invalid-saved-id-text-record')
        need(len(record['text']) <= CAPS['streamCodepoints'], 'individual-stream-codepoint-cap')
        identifiers.append(record['id'])
        lengths.append(len(record['text']))
    need(len(set(identifiers)) == len(identifiers) and sum(lengths) <= CAPS['totalSourceCodepoints'],
         'source-ID-or-total-codepoint-guard')
    if production:
        need(len(streams) == EXPECTATIONS['labeledStreams'] and
             len({record['text'] for record in streams}) == EXPECTATIONS['uniqueStreams'] and
             lengths.count(0) == EXPECTATIONS['emptyTexts'] and max(lengths) == EXPECTATIONS['maxTextCodepoints'] and
             sum(lengths) == EXPECTATIONS['totalTextCodepoints'], 'fixed-G07-source-population-mismatch')
    return streams


def legacy_witnesses(result, check):
    need(isinstance(result, dict) and result.get('testId') == 'G07' and
         isinstance(result.get('evaluation'), dict), 'old-result-identity-mismatch')
    evaluation = result['evaluation']
    need(evaluation.get('streamCount') == 1038 and evaluation.get('uniqueStreamCount') == 833 and
         evaluation.get('uniqueFormCount') == 1464 and
         evaluation.get('formats') == ['wif', 'minikey', 'hex64', 'bip39'], 'old-result-scope-mismatch')
    need(canonical(evaluation.get('validCounts')) == canonical({'wif': 0, 'minikey': 0, 'hex64': 0, 'bip39': 0}) and
         evaluation.get('shapeCounts', {}).get('minikey') == 4 and
         evaluation.get('uniqueShapeCounts', {}).get('minikey') == 3, 'old-result-shape-witness-mismatch')
    need(isinstance(check, dict) and check.get('testId') == 'G07' and check.get('passed') is True and
         check.get('streamCount') == 1038 and check.get('uniqueFormCount') == 1464 and
         canonical(check.get('shapeCounts')) == canonical(evaluation['shapeCounts']) and
         canonical(check.get('uniqueShapeCounts')) == canonical(evaluation['uniqueShapeCounts']) and
         type(check.get('validRecords')) is int and check['validRecords'] == 0 and
         type(check.get('networkQueries')) is int and check['networkQueries'] == 0, 'old-independent-witness-mismatch')


def derive_expected(streams, production=True):
    validate_source(streams, production)
    helper = core()
    forms = helper.reconstruct_forms(streams)
    need(sum(len(text) for text in forms) <= CAPS['totalFormCodepoints'] and
         (not production or len(forms) == EXPECTATIONS['uniqueForms']), 'fixed-form-count-or-codepoint-cap')
    common = load_common()
    shared, raw_shapes, raw_positives = helper.evaluate_common4(forms, common)
    raw_mini = helper.independent_mini26(forms)
    mini = {'status': 'checked', 'enumerated': True, 'length': 26,
            'shapeOccurrences': raw_mini['shapeCount'], 'uniqueShapeCount': raw_mini['uniqueShapeCount'],
            'checksumCalls': raw_mini['checksumCalls'], 'validCount': raw_mini['validCount'],
            'privateReviewRequired': raw_mini['privateReviewRequired'], 'fingerprintRule': helper.FINGERPRINT_RULE,
            'proof': None}
    private_forms = {'schemaVersion': 1, 'testId': TEST_ID, 'sourceArtifactSha256': SOURCE_PINS[SOURCE_REL],
                     'streams': streams, 'forms': forms}
    private_validation = {'schemaVersion': 1, 'testId': TEST_ID, 'common4': shared,
                          'rawShapeValues': raw_shapes, 'rawPositives': raw_positives,
                          'minikey26': mini, 'minikey26Shapes': raw_mini['shapeValues'],
                          'minikey26Positives': raw_mini['validRecords']}
    return private_forms, private_validation


def safe_parts(forms, validation):
    shared, mini = validation['common4'], validation['minikey26']
    counts = {'labeledStreams': len(forms['streams']), 'uniqueStreams': len({r['text'] for r in forms['streams']}),
              'uniqueForms': len(forms['forms']), 'totalValidRecords': sum(shared['validCounts'].values()) + mini['validCount']}
    safe_common = {key: shared[key] for key in ['formats', 'shapeCounts', 'uniqueShapeCounts', 'validationCalls', 'validCounts']}
    safe_mini = {key: mini[key] for key in ['status', 'enumerated', 'shapeOccurrences', 'uniqueShapeCount', 'checksumCalls', 'validCount']}
    return counts, safe_common, safe_mini


def verify(args):
    helper = core()
    output = helper.private_path(args.out, False)
    result_path = helper.private_path(args.result)
    forms_path = helper.private_path(args.forms)
    validation_path = helper.private_path(args.validation)
    protocol, protocol_sha, research = registration(args.protocol, args.registration_commit)
    # All source/code/registration gates above complete before target parsing.
    streams, _ = helper.read_json(research / SOURCE_REL, CAPS['sourceJsonBytes'])
    old_result, _ = helper.read_json(research / OLD_RESULT_REL, CAPS['sourceJsonBytes'])
    old_check, _ = helper.read_json(research / OLD_CHECK_REL, CAPS['sourceJsonBytes'])
    legacy_witnesses(old_result, old_check)
    expected_forms, expected_validation = derive_expected(streams)
    actual_forms, forms_bytes = helper.read_json(forms_path, CAPS['privateArtifactBytes'])
    actual_validation, validation_bytes = helper.read_json(validation_path, CAPS['privateArtifactBytes'])
    need(canonical(actual_forms) == canonical(expected_forms), 'complete-stream-object-and-form-mismatch')
    need(canonical(actual_validation) == canonical(expected_validation), 'complete-raw-validation-mismatch')
    need(all(a.encode('utf-8') == b.encode('utf-8') for a, b in zip(actual_forms['forms'], expected_forms['forms'])),
         'full-form-UTF8-mismatch')
    result, result_bytes = helper.read_json(result_path, CAPS['sourceJsonBytes'])
    top = {'version', 'testId', 'batchId', 'status', 'startedAtUTC', 'completedAtUTC', 'registrationCommit',
           'protocolSha256', 'sourceHashes', 'scriptHashes', 'scopeComplete', 'supplementalGatesComplete',
           'sourceRegenerated', 'ocrRerun', 'semanticReviewPerformed', 'privateReviewRequired', 'counts',
           'common4', 'minikey26', 'privateArtifactIntegrity', 'activity', 'limitations'}
    need(set(result) == top and result.get('version') == 1 and result.get('testId') == TEST_ID and
         result.get('batchId') == BATCH_ID and result.get('status') == 'g07-fixed-artifact-supplemental-scope-complete',
         'safe-result-identity-or-field-mismatch')
    need(result.get('registrationCommit') == args.registration_commit and result.get('protocolSha256') == protocol_sha and
         result.get('sourceHashes') == protocol['sourceHashes'] and result.get('scriptHashes') == protocol['scriptHashes'],
         'safe-result-provenance-mismatch')
    need(result.get('scopeComplete') is True and result.get('supplementalGatesComplete') is True and
         result.get('sourceRegenerated') is False and result.get('ocrRerun') is False and
         result.get('semanticReviewPerformed') is False, 'safe-result-completion-mismatch')
    counts, shared, mini = safe_parts(expected_forms, expected_validation)
    need(canonical(result.get('counts')) == canonical(counts) and canonical(result.get('common4')) == canonical(shared) and
         canonical(result.get('minikey26')) == canonical(mini), 'safe-result-aggregate-mismatch')
    private_review = expected_validation['common4']['privateReviewRequired'] or expected_validation['minikey26']['privateReviewRequired']
    need(result.get('privateReviewRequired') is private_review, 'safe-result-lead-flag-mismatch')
    artifact_pins = {'FORMS.private.json': digest(forms_bytes), 'VALIDATION.private.json': digest(validation_bytes)}
    need(result.get('privateArtifactIntegrity') == artifact_pins and canonical(result.get('activity')) == canonical(EXPECTED_ACTIVITY)
         and result.get('limitations') == LIMITATIONS, 'safe-result-integrity-activity-or-limitations-mismatch')
    try:
        start = datetime.fromisoformat(result['startedAtUTC'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(result['completedAtUTC'].replace('Z', '+00:00'))
        need(start.tzinfo is not None and end.tzinfo is not None and start <= end, 'safe-result-time-order-mismatch')
    except (TypeError, ValueError, KeyError):
        raise GuardError('safe-result-time-format-mismatch') from None
    receipt = {'version': 1, 'testId': TEST_ID, 'status': 'PASS', 'passed': True,
               'completedAtUTC': datetime.now(timezone.utc).isoformat(), 'registrationCommit': args.registration_commit,
               'protocolSha256': protocol_sha, 'primaryResultSha256': digest(result_bytes),
               'sourceArtifactSha256': SOURCE_PINS[SOURCE_REL], 'independentCoreSha256': CORE_SHA,
               'privateArtifactIntegrity': artifact_pins,
               'comparisons': {'labeledStreams': 1038, 'uniqueStreams': 833, 'uniqueForms': 1464,
                               'fullOriginalObjectsOrderAndUTF8': True, 'fullFormsAndRawValidation': True,
                               'safeCountsAndScope': True},
               'methodDependency': 'Pinnedindependentform/26core reused; fourformat shape/validation engine deliberately shared.',
               'newSourceSelectorOrOCR': False, 'semanticReviewPerformed': False,
               'scalarDerivations': 0, 'addressDerivations': 0, 'networkQueries': 0, 'publicEdits': 0}
    output.mkdir(mode=0o700)
    helper.write_private(output / 'VERIFICATION.json', receipt)
    return receipt

def full_mock_source():
    # Exactly reproduce the declared population statistics with synthetic text,
    # not target bytes:832nonemptyunique values,192duplicates,14empty records.
    texts = ['M' + str(i).zfill(3) + (' q' if i < 631 else '') for i in range(832)]
    texts[0] += 'x' * (1748 - len(texts[0]))
    order = list(range(832)) + list(range(1, 193))
    total = sum(len(texts[i]) for i in order)
    remaining = 42110 - total
    need(remaining >= 0, 'synthetic-source-size-construction')
    for i in range(193, 832):
        addition = min(remaining, 1747 - len(texts[i]))
        texts[i] += 'x' * addition
        remaining -= addition
    need(remaining == 0, 'synthetic-total-source-size-construction')
    values = [texts[i] for i in order] + [''] * 14
    return [{'id': 'g07-synthetic-' + str(i), 'text': text} for i, text in enumerate(values)]


def self_test():
    helper = core()
    common_module = load_common()
    need(helper.__loader__ is None and helper.__spec__ is None and
         common_module.__loader__ is None and common_module.__spec__ is None,
         'verified-byte-direct-compile-required')
    # The frozen helper's older SourceFileLoader path must never be invoked.
    def forbidden_legacy_common_loader():
        raise GuardError('legacy-bytecode-capable-common-loader-forbidden')
    helper.load_common = forbidden_legacy_common_loader
    fixture = full_mock_source()
    validate_source(fixture)
    forms, validation = derive_expected(fixture)
    need(len(forms['forms']) == 1464 and forms['streams'] is fixture and '' in forms['forms'],
         'synthetic-complete-source-object-form-and-empty-preservation')
    counts, shared, mini = safe_parts(forms, validation)
    need(counts['labeledStreams'] == 1038 and counts['uniqueStreams'] == 833 and counts['uniqueForms'] == 1464,
         'synthetic-full-G07-counts')
    need(mini['enumerated'] is True and validation['minikey26']['length'] == 26 and
         validation['minikey26']['proof'] is None, 'synthetic-direct26-scope')
    rejected = 0
    for mutation in ['count', 'duplicate-id', 'record-field', 'text-type', 'max-length', 'empty-count', 'total-length']:
        changed = json.loads(json.dumps(fixture))
        if mutation == 'count': changed.pop()
        elif mutation == 'duplicate-id': changed[1]['id'] = changed[0]['id']
        elif mutation == 'record-field': changed[1]['extra'] = True
        elif mutation == 'text-type': changed[1]['text'] = 4
        elif mutation == 'max-length': changed[0]['text'] += 'x' * 300
        elif mutation == 'empty-count': changed[-1]['text'] = 'nonempty'
        else: changed[1]['text'] += 'x'
        try:
            validate_source(changed)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-invalid-G07-population-accepted')
    for bad in [None, {}, {'id': TEST_ID}, {'sourceModel': {'expectations': EXPECTATIONS}}]:
        try:
            validate_test(bad)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-invalid-normative-contract-accepted')
    shapes = {'wif': 0, 'minikey': 4, 'hex64': 0, 'bip39': 0}
    uniques = {'wif': 0, 'minikey': 3, 'hex64': 0, 'bip39': 0}
    old = {'testId': 'G07', 'evaluation': {'streamCount': 1038, 'uniqueStreamCount': 833,
            'uniqueFormCount': 1464, 'formats': ['wif', 'minikey', 'hex64', 'bip39'],
            'shapeCounts': shapes, 'uniqueShapeCounts': uniques, 'validCounts': {key: 0 for key in shapes}}}
    check = {'testId': 'G07', 'passed': True, 'streamCount': 1038, 'uniqueFormCount': 1464,
             'shapeCounts': shapes, 'uniqueShapeCounts': uniques, 'validRecords': 0, 'networkQueries': 0}
    legacy_witnesses(old, check)
    for mutation in ['identity', 'count', 'formats', 'old-shape', 'old-unique', 'passed', 'network']:
        a, b = json.loads(json.dumps(old)), json.loads(json.dumps(check))
        if mutation == 'identity': a['testId'] = 'G03'
        elif mutation == 'count': a['evaluation']['streamCount'] += 1
        elif mutation == 'formats': a['evaluation']['formats'].pop()
        elif mutation == 'old-shape': a['evaluation']['shapeCounts']['minikey'] = 0
        elif mutation == 'old-unique': a['evaluation']['uniqueShapeCounts']['minikey'] = 0
        elif mutation == 'passed': b['passed'] = False
        else: b['networkQueries'] = 1
        try:
            legacy_witnesses(a, b)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-invalid-legacy-witness-accepted')
    whitespace = [{'id': 'a', 'text': 'A\u00a0B\tC\nD\u2003E'}, {'id': 'b', 'text': 'F\u241e G'}]
    need(helper.reconstruct_forms(whitespace) == sorted({'A\u00a0B\tC\nD\u2003E', 'ABCDE', 'F\u241e G', 'F\u241eG'}),
         'synthetic-Unicode-whitespace-and-hard-boundary')
    common = load_common()
    controls = json.loads((helper.common_path().parent / 'batch20_support/controls.json').read_text())
    positive_texts = [controls[k] for k in ['bip32_extended_private', 'bip38_encrypted_private', 'legacy_address', 'sec_compressed_generator']]
    shared, _, _ = helper.evaluate_common4(positive_texts, common)
    need(all(shared['validCounts'][kind] >= 1 for kind in COMMON4), 'synthetic-four-shared-positive-families')
    aliases = [controls['segwit_v0'], controls['segwit_v0'].upper()]
    alias_summary, _, aliases_raw = helper.evaluate_common4(aliases, common)
    need(alias_summary['validCounts']['address'] == 1 and
         len([r for r in aliases_raw if r['format'] == 'address' and r['value'] in aliases]) == 2,
         'synthetic-canonical-address-alias-dedup')
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    good = None
    for number in range(65536):
        n, suffix = number, ''
        for _ in range(8):
            n, digit = divmod(n, 58)
            suffix = alphabet[digit] + suffix
        value = 'S' + '2' * 17 + suffix
        if hashlib.sha256((value + '?').encode('ascii')).digest()[0] == 0:
            good = value
            break
    need(good is not None, 'synthetic-mini26-positive-within-bound')
    need(helper.independent_mini26(['prefix::' + good + '::suffix'])['validCount'] == 1 and
         helper.independent_mini26(['S' * 29])['shapeCount'] == 4 and
         helper.independent_mini26([good[:22]])['shapeCount'] == 0,
         'synthetic-26-embedded-overlap-and-short-tail')
    bad = next(good[:-1] + char for char in alphabet
               if hashlib.sha256((good[:-1] + char + '?').encode('ascii')).digest()[0] != 0)
    need(helper.independent_mini26([bad])['validCount'] == 0 and
         helper.independent_mini26([good[:13] + '\u241e' + good[13:]])['shapeCount'] == 0,
         'synthetic-26-invalid-checksum-and-barrier')
    separated = [{'id': 'a', 'text': good[:13]}, {'id': 'b', 'text': good[13:]}]
    need(helper.independent_mini26(helper.reconstruct_forms(separated))['shapeCount'] == 0,
         'synthetic-no-cross-record-join')
    for path in [helper.site_root() / 'dist/synthetic-private-output', Path('/tmp/public/synthetic-private-output')]:
        try:
            helper.private_path(path, False)
        except helper.GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-public-output-accepted')
    for protocol, commit in [('/synthetic/wrong', 'bad'), ('/synthetic/wrong', '0' * 40)]:
        try:
            registration(protocol, commit)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-invalid-registration-accepted')
    actual_run = helper.subprocess.run
    class MockGit:
        def __init__(self, code, raw): self.returncode, self.stdout = code, raw
    try:
        helper.subprocess.run = lambda *a, **k: MockGit(0, b'commit\n')
        helper.verify_commit_object(Path('/synthetic'), '1' * 40)
        for output in [b'tag\n', b'tree\n', b'blob\n', b'']:
            helper.subprocess.run = lambda *a, _output=output, **k: MockGit(0, _output)
            try:
                helper.verify_commit_object(Path('/synthetic'), '1' * 40)
            except helper.GuardError:
                rejected += 1
            else:
                raise GuardError('synthetic-noncommit-object-accepted')
    finally:
        helper.subprocess.run = actual_run
    return {'version': 1, 'status': 'PASS', 'syntheticCompleteSavedRecords': 1038,
            'syntheticUniqueStreams': 833, 'syntheticUniqueForms': 1464,
            'syntheticEmptyStringsRetained': 14, 'rejectionControls': rejected,
            'sharedFormatPositiveControls': 4, 'independentCoreSha256': CORE_SHA, 'directVerifiedByteCompilation': True,
            'legacyCommonLoaderCalls': 0, 'targetInputsOpened': 0, 'targetFormsOrShapesConstructed': 0, 'primaryRunnerImports': 0,
            'scalarDerivations': 0, 'addressDerivations': 0, 'networkQueries': 0}


def main():
    seen = set()
    for argument in sys.argv[1:]:
        if argument.startswith('--'):
            key = argument.split('=', 1)[0]
            need(key not in seen, 'duplicate-command-argument')
            seen.add(key)
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--definition', action='store_true')
    mode.add_argument('--self-test', action='store_true')
    mode.add_argument('--verify', action='store_true')
    for name in ['protocol', 'registration-commit', 'result', 'forms', 'validation', 'out']:
        parser.add_argument('--' + name)
    args = parser.parse_args()
    if args.definition:
        response = {'testId': TEST_ID, 'protocolPath': PROTOCOL_REL, 'sourcePins': SOURCE_PINS,
                    'scriptPaths': sorted(SCRIPT_PATHS), 'fixedCodePins': FIXED_CODE_PINS,
                    'normativeProtocolTestCanonicalSha256': NORMATIVE_TEST_SHA256,
                    'expectations': EXPECTATIONS, 'reusedIndependentFunctions': ['reconstruct_forms', 'evaluate_common4', 'independent_mini26'],
                    'fourValidatorMathematicsIndependentClaimed': False}
    elif args.self_test:
        response = self_test()
    else:
        need(all(getattr(args, key) for key in ['protocol', 'registration_commit', 'result', 'forms', 'validation', 'out']),
             'required-verification-arguments-missing')
        response = verify(args)
    print(json.dumps(response, indent=2, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except GuardError as error:
        print(json.dumps({'status': 'FAIL-INCONCLUSIVE', 'errorCode': str(error)}))
        raise SystemExit(2)
    except Exception:
        print(json.dumps({'status': 'FAIL-INCONCLUSIVE', 'errorCode': 'unexpected-verification-failure'}))
        raise SystemExit(2)
