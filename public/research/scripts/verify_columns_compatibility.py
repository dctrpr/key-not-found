#!/usr/bin/env python3
"""Independent saved-output verifier for four frozen creator-column cohorts.

Original literal readings are reconstructed solely by the frozen original rules;
all four complete original artifact byte identities pass before any validator.
Independent form/minikey26 enumeration reuses the pinned independent core. Shared
literal validators remain deliberately shared, not an independent crypto engine.
Only --verify reads targets, after actual Git-commit byte gates. Python3.9+.
"""
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import types

class GuardError(Exception):
    pass

def need(value, code):
    if not value:
        raise GuardError(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)

# Frozen metadata is inserted from the author-agreed contract, never target text.
TEST_ID = 'columns-fixed-output-compatibility'
BATCH_ID = 'keiser-columns-fixed-output-compatibility-20261110'
SELF_REL = 'scripts/verify_columns_compatibility.py'
PROTOCOL_REL = 'analysis_outputs/continuation_20261110/columns_compatibility/PROTOCOL.json'
SOURCE_PINS = {'analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.json': '26a681bc40ddb6a1d9d471cf7e70f7f7c3c0c6a588b2f3400a4c083a1e59f15e',
 'analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.md': '824bd796a124ee94e49c3feb50daa370c0c8b42d2bfc62dab5015ba00ccfde86',
 'analysis_outputs/continuation_20261110/funky_sand_direct/RESULT.json': 'c260981ee58f2575951fbf1c51c197e78b25c4009ff79f1be38eac9e59ed3c89',
 'analysis_outputs/continuation_20261110/funky_sand_direct/RESULT.md': 'b101fef0e977bc5ca0a4afc6c077e3be17d021544b1b55af668fdee4e639a4d3',
 'analysis_outputs/continuation_20261110/funky_sand_direct/INDEPENDENT_CHECK.json': 'a30f75596e51e3b5635f1ce879da986f13f1eef00e0e91d4a7d6ef9688ce8a7b',
 'analysis_outputs/continuation_20261110/funky_sand_direct/EXECUTION.json': 'dcc173a36d0e49bf01cfa2ced4497b726822296e93e004e19d8e0c0f7c3afa0f',
 'scripts/funky_sand_direct.py': '4eec6a4ce0ab8466875ddfc8568e1a38debf767a8d619eb5d8d1809ddaf7c8b1',
 'scripts/verify_funky_sand_direct.py': '7e7c5c9c2234b4934665b287848d6383d787949935ff99248c11f2f2083163d5',
 'sources/funky-upheaval/physical-lines.json': '12ef2d85578b89a164a109c7f5045e9fd28b88fd7ce5c58e30632e242a60eb11',
 'sources/funky-upheaval/SOURCE_REGISTER.json': 'fb756e12d376af208c619b6e46ea17366df9d90214992e53673cc10fda106b2f',
 'sources/funky-upheaval/pages/108.jpg': '1557e2974d4f04579aea3015b6f885f35b2b966f06ac5944d39c70439ee8fb6c',
 'sources/funky-upheaval/pages/109.jpg': 'bc12df605c993055ef761f27b413d9c8bc781d70c83533a7d9ae119034554814',
 'sources/funky-upheaval/pages/110.jpg': '2f5cbca356f01887acf84cabcf6d5d8b5a5ec56547ae88329fd7de923a84601f',
 'sources/funky-upheaval/pages/111.jpg': '40092c66f44296988a7f397563915e30f3926a6e265c512aa61b01057e970f50',
 'analysis_outputs/continuation_20261109/george_sand_research.md': '8a619cf8c6ab246fc4dc1c2086648e5d245bfa1ca751011febcbf74be42dd1ff',
 'analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.json': '8ec335eae647d695f14f0024027d281975265d02ba11eb3811ad8480f2255d3d',
 'analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.md': 'cce61a4e76206c0e488922bc188e2ffbc82c6df115210457fae26b4924dae6ac',
 'analysis_outputs/continuation_20261110/issue26_firstwords/RESULT.json': '11d77df1a463382011ca6c17b6ecc670f5e1639e833313b0e09d9166038590a0',
 'analysis_outputs/continuation_20261110/issue26_firstwords/RESULT.md': 'f8238669dc2f6d89a34849663dcf62bc2722fbf42880755f76d4c05f63232105',
 'analysis_outputs/continuation_20261110/issue26_firstwords/INDEPENDENT_CHECK.json': 'c7c3dbfe083c49b8db87c40fa8dd90913c5fbad6f8393db4e929f68ffbaea3ea',
 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d',
 'scripts/batch20_geometry.py': 'e7786acc472fa3f7a294fe6391e74bd6f8840017e30d9f54941544019dbafb9a',
 'scripts/issue26_firstword_probe.py': '79b3a93d38760208ffc728e1e9ada6dcefd430f1ae155ca467aa5d34e8c04b56',
 'scripts/verify_firstword_readings.py': '30dc5a126c666e65a7b4379155742d807b1b061142ff938c59b66cfc1ef46170',
 'sources/issue26/issue26-source.json': '1ff7a0a26c1e91fb2bfef9817693419979fdf39381d4124c2c9e5e7739f73c67',
 'sources/issue26/page_03.jpg': 'bd88ecc69fe5215aaf370a97520cb7668d9b67c43395f4d36544cd3b5a6081f7',
 'sources/issue26/page_04.jpg': 'f7eaedb88bf75249c45a61e5abd9bfa7cc5c59c472d63c84aa30bad7334c75da',
 'sources/issue26/page_05.jpg': 'de13717ccc0d51fa6442ab1f6c8591162d1b3db2a910e36c2cdfedeedb89250d',
 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',
 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b',
 'analysis_outputs/continuation_20261110/issue26_firstwords/READINGS.jsonl.gz': '83fe1bbf4fbe7e4f93a82b136445d314225816943e41e6c027ded89939e7e98a',
 'analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.json': '6e5a4bf93303c29e4447c0e18c22f3e844509c30b9c6e3ee4202df2aa6c3ca69',
 'analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.md': 'da0312f8741893ff18aa043012e4b0a7f9fb590b4d658e0c7a267ebf235dbc23',
 'analysis_outputs/continuation_20261110/issue27_stride12/RESULT.json': '102d1f0459b371292250080cb72692db187a40bae204937673c0be18b0e286d1',
 'analysis_outputs/continuation_20261110/issue27_stride12/RESULT.md': '615f088b8c4c6cb40d89e35d2cabf24aecf6ee59e15bd7c4c426f745fab56659',
 'analysis_outputs/continuation_20261110/issue27_stride12/INDEPENDENT_CHECK.json': '43870042280d9cecf78fc48e6e9fe8e7a816e937e0fe7f695478d38119e00347',
 'scripts/issue27_stride12.py': '84a061444a73fbedc14f8068f8d3cce1fb7ef990b4bef65181e78f234dcbfd01',
 'scripts/verify_issue27_saved.py': '97cace8ee5f9b2707cc1344c08e46e068db327edc504a8625fb825481261422b',
 'scripts/verify_issue27_stride12.py': '1f482648945fe1508a211628ba7ec826c23cdbeed317bbf05426595b5be1ebae',
 'analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json': '783cc6676edf9b135d1eeff04d8bf8636088c1334f9e983f0d9f07dc579bff27',
 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json': 'f5f441345ebe411ee769cdcb624c0717a2b4f790b7eadc50d10dc12d37da07bb',
 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_01.jpg': 'd4cca9f4326ba21a959551e8537596846bccdea42efe37f463506cd2d423fb8c',
 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_02.jpg': 'e18e02e521444c9ea760c6e1d80a39bbee08d65a7839e970629ab81b4fd83610',
 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_03.jpg': 'b7f120860b1a76aa6ba97c836bb56388477ee8878665d75414098f9b8a38a1b5',
 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_04.jpg': '60da7f7ed64764e8c9bb347bce163eb2f8dc4c4ad20abbd00182bced3ad3343a',
 'analysis_outputs/continuation_20261110/issue27_stride12/POLICY_PROPOSAL.json': '5c6d4a7b406f99515b1bb16c7f7874df6444c64c3be2e6a32c0798ac08e0d1e5',
 'analysis_outputs/continuation_20261110/issue27_stream_coverage/PROTOCOL.json': '0f4699ac1bddbc661c7b583fc638f0adbcfc98e7372d604bfed81b770a9a0343',
 'analysis_outputs/continuation_20261110/issue27_stream_coverage/PROTOCOL.md': 'c91e8bf8660a430da344ae5371e2fc122cc423f836f0c321dc646059fcc56d45',
 'analysis_outputs/continuation_20261110/issue27_stream_coverage/RESULT.json': '6cbe0570fc7e03e05eb1369ed98e5456d193c2c8527b7c47fbf83fbf69b059ba',
 'analysis_outputs/continuation_20261110/issue27_stream_coverage/RESULT.md': 'a3493bff6d92f2c872bd9bfe3f1d8303f08c5f95ee461a2b32fd5fa040a4ec2a',
 'analysis_outputs/continuation_20261110/issue27_stream_coverage/INDEPENDENT_CHECK.json': '5fc0254fa4b750472b264690f2aa302f1796d05adea8ab324c9ed7a4e526689b',
 'analysis_outputs/continuation_20261110/issue27_stream_coverage/INDEPENDENT_CHECKER_PIN.json': '229f243de559dd6d55d2ae4bdfd398d2a88710cea4055375e48717f202e7ab8d',
 'scripts/issue27_stream_coverage.py': '7e045510592b19bc1399ca896cd19d601f3a9fc6fee8e8306a1d4115cf812e61',
 'analysis_outputs/continuation_20261109/george_sand_issue27/analyze_printed_lines.py': '78108c23acf33596985b674cc89a033efe19ba7599b8fde521f7ea5efe837184',
 'analysis_outputs/continuation_20261109/george_sand_issue27/REPORT.md': '76c23544624cd5e81d18deadf83113135c9ce425c181fd43e60d11a677abb74f',
 'analysis_outputs/continuation_20261109/george_sand_issue27/regions.json': 'faabd124ade630330beee9ed99c376af65512172f0a3eeed551f865d769efce9',
 'analysis_outputs/continuation_20261109/george_sand_issue27/vision_raw.json': 'c6cdf7de5fa6c34e33c0eba25b6727057a32f953ae55d428d3b77292265c0df3'}
SCRIPT_PATHS = ['scripts/columns_compatibility.py',
 'scripts/verify_columns_compatibility.py',
 'scripts/batch20_supplemental_formats.py',
 'scripts/verify_batch20_supplemental.py',
 'scripts/batch20_common.py']
FIXED_CODE_PINS = {'scripts/batch20_supplemental_formats.py': '385524773ef0c20a2af1858bbf1d1f15cb45fd47fdf08627b0b97d2dda2754ac',
 'scripts/verify_batch20_supplemental.py': 'a4bf930523eb29c0da942439eb6005514fc60d0dfb4f6deede2171380bd4389c',
 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}
COHORT_ORDER = ['funky-sand-direct', 'issue26-first-words', 'issue27-body-stride12', 'issue27-frozen-stream-coverage']
COHORTS = {'funky-sand-direct': {'id': 'funky-sand-direct',
                       'readingFile': 'FUNKY_READINGS.private.json',
                       'rawBytes': 8272,
                       'rawSha256': '033513555f835cdec0193732751118a6ca0a09b9558537edf323c46658d15c61',
                       'rawSchema': 'funky-json',
                       'recordKeys': ['id', 'selectedRowCount', 'text'],
                       'recordCount': 3,
                       'uniqueTextCount': 3,
                       'emptyTexts': 0,
                       'minimumTextCodepoints': 703,
                       'maximumTextCodepoints': 3541,
                       'totalTextCodepoints': 7689,
                       'expectedForms': None,
                       'maximumForms': 6,
                       'commonFormats': ['wif',
                                         'minikey',
                                         'hex64',
                                         'bip39',
                                         'extended_private',
                                         'bip38',
                                         'address',
                                         'sec_public'],
                       'minikey26': True,
                       'originalReadingReconstruction': True,
                       'artifactPinAuthority': 'prior-public-execution',
                       'strictKnown': None},
 'issue26-first-words': {'id': 'issue26-first-words',
                         'readingFile': 'ISSUE26_READINGS.private.jsonl',
                         'rawBytes': 25477680,
                         'rawSha256': '53e24a093652064a7965b57a9c2195e88f555b6e13f2d83b9f02d96958edf054',
                         'rawSchema': 'jsonl',
                         'recordKeys': ['STOPPolicy',
                                        'characterOrder',
                                        'id',
                                        'parityOrigin',
                                        'phase',
                                        'population',
                                        'projection',
                                        'rowOrder',
                                        'selectedRowIds',
                                        'surface',
                                        'text',
                                        'tokenSourceIds',
                                        'unit'],
                         'recordCount': 39744,
                         'uniqueTextCount': 1746,
                         'emptyTexts': 10752,
                         'minimumTextCodepoints': 0,
                         'maximumTextCodepoints': 765,
                         'totalTextCodepoints': 934320,
                         'expectedForms': 1746,
                         'maximumForms': 1746,
                         'commonFormats': [],
                         'minikey26': True,
                         'originalReadingReconstruction': False,
                         'artifactPinAuthority': 'public-gzip-plus-registered-decompressed-identity',
                         'strictKnown': None},
 'issue27-body-stride12': {'id': 'issue27-body-stride12',
                           'readingFile': 'STRIDE_READINGS.private.jsonl',
                           'rawBytes': 46984,
                           'rawSha256': 'b2b33f3eb8440cdf3fa949355b59f443e8aa545b8809500b45d406b364a93225',
                           'rawSchema': 'jsonl',
                           'recordKeys': ['direction',
                                          'id',
                                          'phase',
                                          'projection',
                                          'selectedTokenCount',
                                          'sourceCompleteForProjection',
                                          'text',
                                          'uncertainSelectedTokens'],
                           'recordCount': 72,
                           'uniqueTextCount': 72,
                           'emptyTexts': 0,
                           'minimumTextCodepoints': 168,
                           'maximumTextCodepoints': 1027,
                           'totalTextCodepoints': 32038,
                           'expectedForms': 96,
                           'maximumForms': 96,
                           'commonFormats': ['extended_private', 'bip38', 'address', 'sec_public'],
                           'minikey26': True,
                           'originalReadingReconstruction': True,
                           'artifactPinAuthority': 'newly-registered-original-artifact-identity',
                           'strictKnown': {'recordCount': 60,
                                           'formCount': 78,
                                           'sourceAffectedRecords': 12,
                                           'projectionCounts': {'words': 18, 'initials': 18, 'finals': 24},
                                           'nestedInNominal': True,
                                           'physicalSourceComplete': False}},
 'issue27-frozen-stream-coverage': {'id': 'issue27-frozen-stream-coverage',
                                    'readingFile': 'FROZEN_READINGS.private.jsonl',
                                    'rawBytes': 2044672,
                                    'rawSha256': 'f397d4932969dd6282dd8b2f1562ec0cbec7165a19a7038aecf131b4a3789030',
                                    'rawSchema': 'jsonl',
                                    'recordKeys': ['characterOrder', 'id', 'sourceLabel', 'text'],
                                    'recordCount': 3880,
                                    'uniqueTextCount': 2133,
                                    'emptyTexts': 0,
                                    'minimumTextCodepoints': 1,
                                    'maximumTextCodepoints': 13698,
                                    'totalTextCodepoints': 1329528,
                                    'expectedForms': 3709,
                                    'maximumForms': 3709,
                                    'commonFormats': ['extended_private', 'bip38', 'address', 'sec_public'],
                                    'minikey26': True,
                                    'originalReadingReconstruction': True,
                                    'artifactPinAuthority': 'newly-registered-original-artifact-identity',
                                    'strictKnown': None}}
CAPS = {'registeredBlobBytes': 20000000,
 'sourceJsonBytes': 2000000,
 'protocolBytes': 1000000,
 'gzipCompressedBytes': 1000000,
 'decompressedBytes': 26000000,
 'jsonlLineBytes': 131072,
 'rawArtifactBytes': 30000000,
 'privateArtifactBytes': 64000000,
 'totalPrivateOutputBytes': 128000000,
 'maximumRecordCount': 39744,
 'maximumTextCodepoints': 15000,
 'totalTextCodepoints': 2400000,
 'totalFormCodepoints': 6000000,
 'shapeOccurrencesPerCohort': 1000000,
 'uniqueShapesPerCohort': 500000}
ISSUE26_GZIP_REL = 'analysis_outputs/continuation_20261110/issue26_firstwords/READINGS.jsonl.gz'
NORMATIVE_TEST_SHA256 = '649f5bfeb78765b53e85bc310fc1cae667246621ee37562b3d84652b77b5ebc4'
CONTRACT_SHA256 = '6f23a8e475e27ab902e15401b85ed866d5fbacff31d501d6bb59ef5a46c5635f'
SAFE_RESULT_KEYS = ['version',
 'testId',
 'batchId',
 'status',
 'startedAtUTC',
 'completedAtUTC',
 'registrationCommit',
 'protocolSha256',
 'sourceHashes',
 'scriptHashes',
 'scopeComplete',
 'compatibilityGatesComplete',
 'allOriginalArtifactIdentitiesVerified',
 'originalReadingReconstruction',
 'newSelectorIntroduced',
 'ocrRerun',
 'sourceRepairs',
 'semanticReviewPerformed',
 'privateReviewRequired',
 'cohorts',
 'counts',
 'privateArtifactIntegrity',
 'activity',
 'limitations']
SAFE_COHORT_KEYS = ['id',
 'recordCount',
 'uniqueTextCount',
 'formCount',
 'rawReadingBytes',
 'rawReadingSha256',
 'artifactPinAuthority',
 'originalReadingReconstruction',
 'common',
 'minikey26',
 'strictKnown',
 'privateReviewRequired']
SAFE_COMMON_KEYS = ['formats', 'shapeCounts', 'uniqueShapeCounts', 'validationCalls', 'validCounts']
SAFE_MINI_KEYS = ['status', 'enumerated', 'shapeOccurrences', 'uniqueShapeCount', 'checksumCalls', 'validCount']
SAFE_STATUS = 'four-cohort-fixed-output-compatibility-scope-complete'
EXPECTED_ACTIVITY = {'originalReadingReconstructionCohorts': 3,
 'gzipArtifactsDecompressed': 1,
 'newSelectors': 0,
 'newReversalVariants': 0,
 'ocrReruns': 0,
 'sourceRepairs': 0,
 'bareMinikeyScalarHashes': 0,
 'proseToKeyHashes': 0,
 'scalarDerivations': 0,
 'seedDerivations': 0,
 'addressDerivations': 0,
 'childKeyDerivations': 0,
 'networkQueries': 0,
 'historyQueries': 0,
 'transactions': 0,
 'legacyValidatorsOutsideFunky': 0}
LIMITATIONS = ['One compatibility matrix over four correlated recorded-output cohorts, not four new theories or a global '
 'independent-trial count.',
 'Funky first8shared-format coverage and26gate includes a newly registered <=6 exact/whitespace-only form '
 'surface; issue/date and December eligibility remain unverified.',
 'Issue26 only26 gate; addedfour not repeated. Direct exact/compact set equality is checked after '
 'registration. Firstword proof does not repair23 blurred lineendings or recover its missingPDF.',
 'Stride60source-known records/78forms are nested within72/96, preserving three uncertain prefixes; no '
 'complete physical-source exclusion.',
 'Historical3880wrapper reproduces existing1940exact/reversed rules on old79–81OCRmodel; it adds no '
 'opener/source repairs and does not claim priorpublic rawEXEC pins.',
 'Funky rawJSON identity has a priorpublic executionpin; stride/frozen rawJSONL identities are newly '
 'registered for this replay.',
 'Four-format validators are shared and reused; separate frozen form/26 implementations do not establish '
 'independent mathematics for sharedvalidators.',
 'No semantic recognition, scalar/seed/address derivation, funding/historyquery, wallet activity or '
 'whole-puzzle exclusion is computed; puzzle remains unsolved.']

_CACHE = {}

def public_file(research, relative):
    base = Path(research).resolve()
    relative = Path(relative)
    need(not relative.is_absolute() and '..' not in relative.parts, 'relative-public-source-path-required')
    path = (base / relative).resolve()
    need(path.is_relative_to(base), 'public-source-symlink-escape-rejected')
    return path


def public_scripts():
    here = Path(__file__).resolve()
    if here.parent.name == 'scripts' and (here.parent / 'batch20_common.py').is_file():
        return here.parent
    fallback = here.parents[3] / 'site/public/research/scripts'
    need(fallback.is_dir(), 'public-code-dependency-directory-required')
    return fallback


def pinned_module(relative):
    if relative not in _CACHE:
        need(relative in SOURCE_PINS or relative in FIXED_CODE_PINS, 'undeclared-code-dependency')
        path = public_file(public_scripts().parent, relative)
        expected = SOURCE_PINS.get(relative, FIXED_CODE_PINS.get(relative))
        need(path.is_file() and path.stat().st_size <= 2_000_000, 'code-dependency-size-guard')
        raw = path.read_bytes()
        need(sha(raw) == expected, 'code-dependency-byte-pin-mismatch')
        module = types.ModuleType('columns_independent_' + path.stem)
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        need(module.__loader__ is None and module.__spec__ is None, 'direct-verified-byte-compile-required')
        _CACHE[relative] = module
    return _CACHE[relative]


def core():
    return pinned_module('scripts/verify_batch20_supplemental.py')


def common():
    for name in ['english.txt', 'controls.json']:
        relative = 'scripts/batch20_support/' + name
        path = public_file(public_scripts().parent, relative)
        need(path.is_file() and path.stat().st_size <= 2_000_000 and
             sha(path.read_bytes()) == SOURCE_PINS[relative], 'shared-support-byte-pin-mismatch')
    return pinned_module('scripts/batch20_common.py')


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate-JSON-key')
        result[key] = value
    return result


def decode_json(raw):
    need(not raw.startswith(b'\xef\xbb\xbf'), 'UTF8-without-BOM-required')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(GuardError('nonfinite-JSON-number')))
    except (UnicodeError, ValueError):
        raise GuardError('invalid-UTF8-or-JSON') from None


def bounded_bytes(path, maximum):
    path = Path(path)
    need(path.is_file() and path.stat().st_size <= maximum, 'file-size-or-existence-guard')
    with path.open('rb') as handle:
        raw = handle.read(maximum + 1)
    need(len(raw) <= maximum, 'file-byte-cap')
    return raw


def private(path, existing=True):
    return core().private_path(path, existing)


def write_bytes(path, raw, maximum):
    need(len(raw) <= maximum, 'private-artifact-byte-cap')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(raw)


def write_json(path, value):
    write_bytes(path, (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8'),
                CAPS['privateArtifactBytes'])


def registration(protocol_path, commit):
    need(isinstance(commit, str) and len(commit) == 40 and all(c in '0123456789abcdef' for c in commit),
         'full-registration-commit-required')
    research = Path(__file__).resolve().parent.parent
    need((research / SELF_REL).resolve() == Path(__file__).resolve(), 'installed-public-verifier-required')
    fixed_protocol = public_file(research, PROTOCOL_REL)
    need(Path(protocol_path).resolve() == fixed_protocol, 'fixed-protocol-required')
    core().verify_commit_object(research, commit)
    raw = bounded_bytes(public_file(research, PROTOCOL_REL), CAPS['protocolBytes'])
    protocol = decode_json(raw)
    need(isinstance(protocol, dict) and protocol.get('version') == 1 and protocol.get('batchId') == BATCH_ID,
         'protocol-identity-mismatch')
    need(sha(canonical(protocol.get('test')).encode('utf-8')) == NORMATIVE_TEST_SHA256,
         'normative-protocol-test-mismatch')
    need(protocol.get('sourceHashes') == SOURCE_PINS and isinstance(protocol.get('scriptHashes'), dict) and
         set(protocol['scriptHashes']) == set(SCRIPT_PATHS), 'exact-source-and-code-population-required')
    need(all(protocol['scriptHashes'].get(path) == value for path, value in FIXED_CODE_PINS.items()),
         'fixed-code-pin-mismatch')
    all_pins = dict(SOURCE_PINS)
    for path, expected in protocol['scriptHashes'].items():
        need(path not in all_pins or all_pins[path] == expected, 'duplicate-pin-disagreement')
        need(isinstance(expected, str) and len(expected) == 64 and all(c in '0123456789abcdef' for c in expected),
             'invalid-code-pin')
        all_pins[path] = expected
    all_pins[PROTOCOL_REL] = sha(raw)
    for relative, expected in all_pins.items():
        current = bounded_bytes(public_file(research, relative), CAPS['registeredBlobBytes'])
        need(sha(current) == expected, 'current-source-code-or-protocol-byte-mismatch')
        previous = subprocess.run(['git', 'show', commit + ':public/research/' + relative], cwd=research,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        need(previous.returncode == 0 and len(previous.stdout) <= CAPS['registeredBlobBytes'] and
             previous.stdout == current, 'registered-source-code-or-protocol-byte-mismatch')
    return research, protocol, sha(raw)


def jsonl_bytes(records):
    return b''.join((json.dumps(record, ensure_ascii=True, allow_nan=False) + '\n').encode('utf-8')
                    for record in records)


def funky_original(model, production=True):
    reader = pinned_module('scripts/verify_funky_sand_direct.py')
    if production:
        need(isinstance(model, dict) and model.get('version') == 1 and
             model.get('modelId') == 'funky-upheaval-physical-lines-v1', 'Funky-source-model-mismatch')
    readings = reader.build_readings(model['rows'], production=production)
    source_sha = SOURCE_PINS['sources/funky-upheaval/physical-lines.json']
    envelope = {'schemaVersion': 1, 'testId': 'funky-sand-direct', 'sourceSha256': source_sha,
                'readings': readings}
    raw = (json.dumps(envelope, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    return readings, raw


def stride_original(source, production=True):
    reader = pinned_module('scripts/verify_issue27_stride12.py')
    rows = reader.source_rows(source) if production else source['rows']
    tokens = reader.tokens_from_rows(rows)
    if production:
        need(len(tokens) == 2018 and sum(bool(t['uncertainForProjections']) for t in tokens) == 3,
             'stride-source-token-population-mismatch')
    records = []
    # Independent fixed loop, avoiding the legacy helper's incidental form tail.
    for reverse in (False, True):
        sequence = list(reversed(tokens)) if reverse else tokens
        direction = 'reverse' if reverse else 'forward'
        for offset in range(12):
            chosen = [token for index, token in enumerate(sequence) if index % 12 == offset]
            for projection in ('words', 'initials', 'finals'):
                affected = sum(projection in t['uncertainForProjections'] for t in chosen)
                if projection == 'words':
                    text = ' '.join(t['text'] for t in chosen)
                elif projection == 'initials':
                    text = ''.join(t['text'][0] for t in chosen)
                else:
                    text = ''.join(t['text'][-1] for t in chosen)
                records.append({'id': direction + ':phase' + str(offset + 1).zfill(2) + ':' + projection,
                                'direction': direction, 'phase': offset + 1, 'projection': projection,
                                'selectedTokenCount': len(chosen), 'sourceCompleteForProjection': affected == 0,
                                'uncertainSelectedTokens': affected, 'text': text})
    need(len(records) == 72, 'stride-reading-count-mismatch')
    return records, jsonl_bytes(records)


def frozen_original(source, production=True):
    need(isinstance(source, dict) and set(source) == {'sourcePages', 'rows', 'streams', 'hits', 'summary'},
         'frozen-source-envelope-mismatch')
    streams = source['streams']
    need(isinstance(streams, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in streams.items()),
         'frozen-stream-type-mismatch')
    if production:
        need(source['sourcePages'] == {'2': 79, '3': 80, '4': 81} and len(source['rows']) == 356 and
             len(streams) == 1940, 'frozen-source-population-mismatch')
    records = []
    for label in sorted(streams):
        for order in ('exact', 'reversed-codepoints'):
            text = streams[label] if order == 'exact' else ''.join(reversed(streams[label]))
            records.append({'id': label + ':' + order, 'sourceLabel': label, 'characterOrder': order, 'text': text})
    return records, jsonl_bytes(records)


def expanded_gzip(raw, expected_size, maximum_line):
    need(len(raw) <= CAPS['gzipCompressedBytes'], 'gzip-compressed-byte-cap')
    result = bytearray()
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode='rb') as handle:
            while True:
                chunk = handle.read(min(65536, expected_size + 1 - len(result)))
                if not chunk:
                    break
                result.extend(chunk)
                need(len(result) <= expected_size, 'gzip-uncompressed-byte-cap')
    except (OSError, EOFError, ValueError):
        raise GuardError('invalid-bounded-gzip') from None
    need(len(result) == expected_size and result.endswith(b'\n') and b'\r\n' not in result,
         'gzip-raw-size-or-LF-mismatch')
    lines = bytes(result).splitlines(keepends=True)
    need(all(line.endswith(b'\n') and len(line) <= maximum_line for line in lines), 'gzip-JSONL-line-cap')
    return bytes(result)


def parse_records(raw, cohort):
    metadata = COHORTS[cohort]
    if cohort == 'funky-sand-direct':
        envelope = decode_json(raw)
        need(set(envelope) == {'schemaVersion', 'testId', 'sourceSha256', 'readings'} and
             envelope['schemaVersion'] == 1 and envelope['testId'] == 'funky-sand-direct' and
             envelope['sourceSha256'] == SOURCE_PINS['sources/funky-upheaval/physical-lines.json'],
             'Funky-artifact-envelope-mismatch')
        records = envelope['readings']
    else:
        need(raw.endswith(b'\n') and b'\r\n' not in raw, 'artifact-LF-JSONL-required')
        lines = raw.split(b'\n')[:-1]
        need(all(0 < len(line) + 1 <= CAPS['jsonlLineBytes'] for line in lines), 'artifact-JSONL-line-cap')
        records = [decode_json(line) for line in lines]
    need(isinstance(records, list) and len(records) == metadata['recordCount'], 'artifact-record-count-mismatch')
    ids, lengths = [], []
    for record in records:
        need(isinstance(record, dict) and set(record) == set(metadata['recordKeys']), 'artifact-record-schema-mismatch')
        need(isinstance(record['id'], str) and record['id'] and isinstance(record['text'], str),
             'artifact-record-field-type-mismatch')
        ids.append(record['id'])
        lengths.append(len(record['text']))
    need(len(set(ids)) == len(ids) and len({r['text'] for r in records}) == metadata['uniqueTextCount'] and
         sum(lengths) == metadata['totalTextCodepoints'] and lengths.count(0) == metadata['emptyTexts'] and
         max(lengths) == metadata['maximumTextCodepoints'] and min(lengths) == metadata['minimumTextCodepoints'],
         'artifact-complete-population-mismatch')
    return records


def original_artifacts(research):
    raw_by_cohort = {}
    funky = decode_json(bounded_bytes(public_file(research, 'sources/funky-upheaval/physical-lines.json'), CAPS['sourceJsonBytes']))
    _, raw_by_cohort['funky-sand-direct'] = funky_original(funky)
    body_rel = 'analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json'
    body = decode_json(bounded_bytes(public_file(research, body_rel), CAPS['sourceJsonBytes']))
    _, raw_by_cohort['issue27-body-stride12'] = stride_original(body)
    frozen_rel = 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json'
    frozen = decode_json(bounded_bytes(public_file(research, frozen_rel), CAPS['sourceJsonBytes']))
    _, raw_by_cohort['issue27-frozen-stream-coverage'] = frozen_original(frozen)
    compressed = bounded_bytes(public_file(research, ISSUE26_GZIP_REL), CAPS['gzipCompressedBytes'])
    meta = COHORTS['issue26-first-words']
    raw_by_cohort['issue26-first-words'] = expanded_gzip(compressed, meta['rawBytes'], CAPS['jsonlLineBytes'])
    # Complete byte identity of ALL FOUR passes before parsing or any format gate.
    for cohort in COHORT_ORDER:
        metadata = COHORTS[cohort]
        raw = raw_by_cohort[cohort]
        need(len(raw) == metadata['rawBytes'] and sha(raw) == metadata['rawSha256'],
             'original-artifact-whole-byte-identity-mismatch')
    records = {cohort: parse_records(raw_by_cohort[cohort], cohort) for cohort in COHORT_ORDER}
    return records, raw_by_cohort


def forms_for(records, cohort, production=True):
    forms = core().reconstruct_forms(records)
    meta = COHORTS[cohort]
    need(len(forms) <= meta['maximumForms'] and sum(map(len, forms)) <= CAPS['totalFormCodepoints'],
         'cohort-form-resource-cap')
    if production and meta['expectedForms'] is not None:
        need(len(forms) == meta['expectedForms'], 'fixed-form-population-mismatch')
    if cohort == 'issue26-first-words':
        need(set(forms) == {r['text'] for r in records}, 'Issue26-exact-text-form-union-mismatch')
    return forms


def evaluate_formats(forms, formats):
    engine = common()
    if formats == ['extended_private', 'bip38', 'address', 'sec_public']:
        return core().evaluate_common4(forms, engine)
    need(formats in ([], ['wif', 'minikey', 'hex64', 'bip39', 'extended_private', 'bip38', 'address', 'sec_public']),
         'undeclared-common-format-matrix')
    indexes = engine.wordlist()[1] if 'bip39' in formats else None
    occurrences, candidates = {kind: 0 for kind in formats}, {kind: set() for kind in formats}
    for form in forms:
        for kind in formats:
            for value in engine.shape_values(kind, form, indexes):
                occurrences[kind] += 1
                candidates[kind].add(value)
                need(sum(occurrences.values()) <= CAPS['shapeOccurrencesPerCohort'] and
                     sum(map(len, candidates.values())) <= CAPS['uniqueShapesPerCohort'], 'common-shape-resource-cap')
    shapes = {kind: sorted(candidates[kind]) for kind in formats}
    positives, fingerprints = [], {kind: set() for kind in formats}
    for kind in formats:
        for value in shapes[kind]:
            checked = engine.validate_record(kind, value, indexes)
            if checked is not None:
                encoded, metadata = checked
                fingerprint = engine.fingerprint(kind, encoded)
                positives.append({'format': kind, 'value': value, 'fingerprint': fingerprint, 'metadata': metadata})
                fingerprints[kind].add(fingerprint)
    summary = {'formats': formats, 'shapeCounts': occurrences,
               'uniqueShapeCounts': {kind: len(candidates[kind]) for kind in formats},
               'validationCalls': sum(map(len, candidates.values())),
               'validCounts': {kind: len(fingerprints[kind]) for kind in formats},
               'privateReviewRequired': bool(positives), 'fingerprintRule': core().FINGERPRINT_RULE}
    return summary, shapes, positives


def evaluation(forms, cohort):
    shared, shapes, positives = evaluate_formats(forms, COHORTS[cohort]['commonFormats'])
    raw = core().independent_mini26(forms)
    mini = {'status': 'checked', 'enumerated': True, 'length': 26,
            'shapeOccurrences': raw['shapeCount'], 'uniqueShapeCount': raw['uniqueShapeCount'],
            'checksumCalls': raw['checksumCalls'], 'validCount': raw['validCount'],
            'privateReviewRequired': raw['privateReviewRequired'], 'fingerprintRule': core().FINGERPRINT_RULE,
            'proof': None}
    return {'common': shared, 'rawShapeValues': shapes, 'rawPositives': positives,
            'minikey26': mini, 'minikey26Shapes': raw['shapeValues'], 'minikey26Positives': raw['validRecords']}


def restricted_evaluation(forms, nominal, formats):
    # Whole-reading subset only. Enumerate membership, then reuse nominal verdicts
    # and fingerprints; this never calls a validator or a question-mark hash.
    counts, sets = {kind: 0 for kind in formats}, {kind: set() for kind in formats}
    engine = common()
    for form in forms:
        for kind in formats:
            for value in engine.shape_values(kind, form):
                counts[kind] += 1
                sets[kind].add(value)
                need(sum(counts.values()) <= CAPS['shapeOccurrencesPerCohort'] and
                     sum(map(len, sets.values())) <= CAPS['uniqueShapesPerCohort'], 'strict-common-shape-resource-cap')
    shapes = {kind: sorted(sets[kind]) for kind in formats}
    need(all(sets[kind] <= set(nominal['rawShapeValues'][kind]) for kind in formats),
         'strict-common-shape-not-in-nominal')
    positives = [record for record in nominal['rawPositives'] if record['value'] in sets[record['format']]]
    valid = {kind: len({record['fingerprint'] for record in positives if record['format'] == kind}) for kind in formats}
    shared = {'formats': formats, 'shapeCounts': counts,
              'uniqueShapeCounts': {kind: len(sets[kind]) for kind in formats}, 'validationCalls': 0,
              'validCounts': valid, 'privateReviewRequired': bool(positives), 'fingerprintRule': core().FINGERPRINT_RULE}
    alphabet = frozenset('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
    occurrences, mini_values = 0, set()
    for form in forms:
        for start in range(max(0, len(form) - 25)):
            if form[start] == 'S':
                value = form[start:start + 26]
                if all(char in alphabet for char in value):
                    occurrences += 1
                    mini_values.add(value)
                    need(occurrences <= CAPS['shapeOccurrencesPerCohort'] and
                         len(mini_values) <= CAPS['uniqueShapesPerCohort'], 'strict-mini-shape-resource-cap')
    need(mini_values <= set(nominal['minikey26Shapes']), 'strict-mini-shape-not-in-nominal')
    mini_positives = [record for record in nominal['minikey26Positives'] if record['value'] in mini_values]
    mini = {'status': 'derived-from-nominal-validation', 'enumerated': True, 'length': 26,
            'shapeOccurrences': occurrences, 'uniqueShapeCount': len(mini_values), 'checksumCalls': 0,
            'validCount': len(mini_positives), 'privateReviewRequired': bool(mini_positives),
            'fingerprintRule': core().FINGERPRINT_RULE, 'proof': {'nominalValidationReused': True, 'nestedSubset': True}}
    return {'common': shared, 'rawShapeValues': shapes, 'rawPositives': positives, 'minikey26': mini,
            'minikey26Shapes': sorted(mini_values), 'minikey26Positives': mini_positives}


def derive_expected(records_by_cohort, production=True):
    form_cohorts, validation_cohorts = [], []
    total_form_codepoints = 0
    for cohort in COHORT_ORDER:
        records = records_by_cohort[cohort]
        forms = forms_for(records, cohort, production)
        nominal_evaluation = evaluation(forms, cohort)
        known_forms, known_evaluation = None, None
        if cohort == 'issue27-body-stride12':
            known = [record for record in records if record['sourceCompleteForProjection'] is True]
            need(all(type(record['sourceCompleteForProjection']) is bool and
                     record['sourceCompleteForProjection'] == (record['uncertainSelectedTokens'] == 0)
                     for record in records), 'stride-uncertainty-flag-mismatch')
            known_forms = core().reconstruct_forms(known)
            need(set(known_forms) <= set(forms), 'strict-known-not-nested-in-nominal')
            if production:
                need(len(known) == 60 and len(known_forms) == 78 and
                     {projection: sum(r['projection'] == projection for r in known)
                      for projection in ['words', 'initials', 'finals']} == {'words': 18, 'initials': 18, 'finals': 24},
                     'strict-known-source-population-mismatch')
            known_evaluation = restricted_evaluation(known_forms, nominal_evaluation, COHORTS[cohort]['commonFormats'])
        total_form_codepoints += sum(map(len, forms))
        need(total_form_codepoints <= CAPS['totalFormCodepoints'], 'total-form-codepoint-cap')
        form_cohorts.append({'id': cohort, 'forms': forms, 'strictKnownForms': known_forms})
        validation_cohorts.append({'id': cohort, 'evaluationAll': nominal_evaluation,
                                   'evaluationStrictKnown': known_evaluation})
    return ({'schemaVersion': 1, 'testId': TEST_ID, 'cohorts': form_cohorts},
            {'schemaVersion': 1, 'testId': TEST_ID, 'cohorts': validation_cohorts})


def safe_evaluation(value):
    return ({key: value['common'][key] for key in SAFE_COMMON_KEYS},
            {key: value['minikey26'][key] for key in SAFE_MINI_KEYS},
            value['common']['privateReviewRequired'] or value['minikey26']['privateReviewRequired'])


def safe_parts(records_by_cohort, forms, validation):
    safe_cohorts, valid_total = [], 0
    for meta, saved_forms, checked in zip(COHORTS.values(), forms['cohorts'], validation['cohorts']):
        cohort = meta['id']
        need(saved_forms['id'] == checked['id'] == cohort, 'private-cohort-order-mismatch')
        shared, mini, private_review = safe_evaluation(checked['evaluationAll'])
        strict = None
        if checked['evaluationStrictKnown'] is not None:
            shared_known, mini_known, lead_known = safe_evaluation(checked['evaluationStrictKnown'])
            strict = {'recordCount': 60, 'formCount': 78, 'nestedInNominal': True, 'physicalSourceComplete': False,
                      'common': shared_known, 'minikey26': mini_known, 'privateReviewRequired': lead_known}
        safe_cohorts.append({'id': cohort, 'recordCount': len(records_by_cohort[cohort]),
                             'uniqueTextCount': len({r['text'] for r in records_by_cohort[cohort]}),
                             'formCount': len(saved_forms['forms']), 'rawReadingBytes': meta['rawBytes'],
                             'rawReadingSha256': meta['rawSha256'], 'artifactPinAuthority': meta['artifactPinAuthority'],
                             'originalReadingReconstruction': meta['originalReadingReconstruction'],
                             'common': shared, 'minikey26': mini, 'strictKnown': strict,
                             'privateReviewRequired': private_review})
        valid_total += sum(shared['validCounts'].values()) + mini['validCount']
    counts = {'cohorts': 4, 'labeledRecords': sum(len(v) for v in records_by_cohort.values()),
              'textCodepoints': sum(len(r['text']) for records in records_by_cohort.values() for r in records),
              'sumPerCohortForms': sum(len(v['forms']) for v in forms['cohorts']),
              'globalUnionComputed': False, 'strictKnownIsNested': True, 'sumNominalValidRecords': valid_total}
    return safe_cohorts, counts, any(cohort['privateReviewRequired'] for cohort in safe_cohorts)


def result_checks(result, protocol, protocol_sha, commit, records, forms, validation, artifact_hashes):
    need(isinstance(result, dict) and set(result) == set(SAFE_RESULT_KEYS) and result.get('version') == 1 and
         result.get('testId') == TEST_ID and result.get('batchId') == BATCH_ID and result.get('status') == SAFE_STATUS,
         'safe-result-identity-or-field-mismatch')
    need(result.get('registrationCommit') == commit and result.get('protocolSha256') == protocol_sha and
         result.get('sourceHashes') == protocol['sourceHashes'] and result.get('scriptHashes') == protocol['scriptHashes'],
         'safe-result-provenance-mismatch')
    need(all(result.get(key) is True for key in ['scopeComplete', 'compatibilityGatesComplete', 'allOriginalArtifactIdentitiesVerified']) and
         all(result.get(key) is False for key in ['newSelectorIntroduced', 'ocrRerun', 'sourceRepairs', 'semanticReviewPerformed']),
         'safe-result-completion-or-scope-flag-mismatch')
    expected_reconstruction = {cohort: COHORTS[cohort]['originalReadingReconstruction'] for cohort in COHORT_ORDER}
    need(result.get('originalReadingReconstruction') == expected_reconstruction, 'safe-result-reconstruction-claim-mismatch')
    cohorts, counts, private_review = safe_parts(records, forms, validation)
    need(canonical(result.get('cohorts')) == canonical(cohorts) and canonical(result.get('counts')) == canonical(counts) and
         result.get('privateReviewRequired') is private_review, 'safe-result-aggregate-or-lead-flag-mismatch')
    need(result.get('privateArtifactIntegrity') == artifact_hashes and result.get('activity') == EXPECTED_ACTIVITY and
         result.get('limitations') == LIMITATIONS, 'safe-result-artifact-activity-or-limitation-mismatch')
    try:
        first = datetime.fromisoformat(result['startedAtUTC'].replace('Z', '+00:00'))
        last = datetime.fromisoformat(result['completedAtUTC'].replace('Z', '+00:00'))
        need(first.tzinfo is not None and last.tzinfo is not None and first <= last, 'safe-result-time-order-mismatch')
    except (TypeError, ValueError, KeyError):
        raise GuardError('safe-result-time-format-mismatch') from None
    return counts


def verify(args):
    output = private(args.out, False)
    result_path, forms_path, validation_path = [private(getattr(args, name)) for name in ['result', 'forms', 'validation']]
    artifacts_dir = Path(args.artifacts_dir).expanduser().resolve()
    need(artifacts_dir.is_dir() and artifacts_dir.stat().st_mode & 0o777 == 0o700,
         'private-original-artifact-directory-mode-required')
    paths = {cohort: private(artifacts_dir / COHORTS[cohort]['readingFile']) for cohort in COHORT_ORDER}
    for path in [result_path, forms_path, validation_path] + list(paths.values()):
        need(path.stat().st_mode & 0o777 == 0o600 and path.parent.stat().st_mode & 0o777 == 0o700,
             'private-input-exact-file-directory-modes-required')
    need(output.parent.stat().st_mode & 0o777 == 0o700, 'private-output-parent-mode-required')
    research, protocol, protocol_sha = registration(args.protocol, args.registration_commit)
    expected_records, originals = original_artifacts(research)
    artifact_hashes = {}
    total_private = 0
    # Original bytes compared in full, before form reconstruction or validation.
    for cohort in COHORT_ORDER:
        meta = COHORTS[cohort]
        raw = bounded_bytes(paths[cohort], CAPS['rawArtifactBytes'])
        need(raw == originals[cohort], 'complete-original-saved-artifact-byte-mismatch')
        artifact_hashes[meta['readingFile']] = sha(raw)
        total_private += len(raw)
    expected_forms, expected_validation = derive_expected(expected_records)
    forms_raw = bounded_bytes(forms_path, CAPS['privateArtifactBytes'])
    validation_raw = bounded_bytes(validation_path, CAPS['privateArtifactBytes'])
    total_private += len(forms_raw) + len(validation_raw)
    need(total_private <= CAPS['totalPrivateOutputBytes'], 'total-private-artifact-byte-cap')
    actual_forms, actual_validation = decode_json(forms_raw), decode_json(validation_raw)
    need(canonical(actual_forms) == canonical(expected_forms), 'complete-private-form-object-mismatch')
    need(canonical(actual_validation) == canonical(expected_validation), 'complete-private-validation-object-mismatch')
    artifact_hashes.update({'FORMS.private.json': sha(forms_raw), 'VALIDATION.private.json': sha(validation_raw)})
    raw_result = bounded_bytes(result_path, CAPS['sourceJsonBytes'])
    result = decode_json(raw_result)
    counts = result_checks(result, protocol, protocol_sha, args.registration_commit, expected_records,
                           expected_forms, expected_validation, artifact_hashes)
    receipt = {'version': 1, 'testId': TEST_ID, 'status': 'PASS', 'passed': True,
               'completedAtUTC': datetime.now(timezone.utc).isoformat(), 'registrationCommit': args.registration_commit,
               'protocolSha256': protocol_sha, 'primaryResultSha256': sha(raw_result),
               'privateArtifactIntegrity': artifact_hashes, 'comparisons': counts,
               'fullOriginalArtifactBytesCompared': True, 'fullReadingObjectsOrderAndUTF8Compared': True,
               'fullFormsAndRawValidationCompared': True, 'safeCountsAndScopeCompared': True,
               'originalReadingReconstruction': {key: COHORTS[key]['originalReadingReconstruction'] for key in COHORT_ORDER},
               'newSelectorIntroduced': False, 'semanticReviewPerformed': False,
               'methodDependency': 'Original independentFunky/stride token routines, independentfixed reading wrappers, reused independentform/26core; common literal validator math deliberately shared.',
               'scalarDerivations': 0, 'addressDerivations': 0, 'networkQueries': 0, 'publicEdits': 0}
    output.mkdir(mode=0o700)
    write_json(output / 'VERIFICATION.json', receipt)
    return receipt


def synthetic_minikey(length):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    for ordinal in range(65536):
        n, suffix = ordinal, ''
        for _ in range(8):
            n, digit = divmod(n, 58)
            suffix = alphabet[digit] + suffix
        value = 'S' + '2' * (length - 9) + suffix
        if hashlib.sha256((value + '?').encode('ascii')).digest()[0] == 0:
            return value
    raise GuardError('synthetic-checksum-control-bound-exceeded')


def self_test():
    helper, engine = core(), common()
    reader_funky = pinned_module('scripts/verify_funky_sand_direct.py')
    reader_stride = pinned_module('scripts/verify_issue27_stride12.py')
    # These original module functions are deliberately never called by this adapter.
    def forbidden(*args, **kwargs):
        raise GuardError('forbidden-legacy-loader-or-evaluator')
    helper.load_common = forbidden
    reader_stride.load_evaluator = forbidden
    reader_stride.readings_from_tokens = forbidden
    for module in [helper, engine, reader_funky, reader_stride]:
        need(module.__spec__ is None and module.__loader__ is None, 'synthetic-no-pyc-loader')
    rejected = 0
    def reject(function, *args):
        nonlocal rejected
        try:
            function(*args)
        except Exception:
            rejected += 1
        else:
            raise GuardError('synthetic-negative-control-accepted')
    import tempfile
    with tempfile.TemporaryDirectory(prefix='key404-synthetic-public-boundary-') as fixture:
        fixture = Path(fixture)
        root = fixture / 'research'
        root.mkdir(mode=0o700)
        outside = fixture / 'synthetic-outside.txt'
        outside.write_bytes(b'synthetic source-boundary fixture')
        inside = root / 'synthetic-inside.txt'
        inside.write_bytes(b'synthetic source-boundary fixture')
        link = root / 'escaped-source.txt'
        link.symlink_to(outside)
        need(public_file(root, 'synthetic-inside.txt') == inside.resolve(), 'synthetic-in-root-source-path')
        reject(public_file, root, 'escaped-source.txt')
        reject(public_file, root, '../synthetic-outside.txt')
        reject(public_file, root, str(outside))
    rows = []
    page_counts = {108: 11, 109: 41, 110: 29, 111: 34}
    for page, count in page_counts.items():
        for number in range(count):
            ordinal = len(rows) + 1
            rows.append({'id': 'synthetic-row-' + str(ordinal), 'ordinal': ordinal, 'printedPage': page,
                         'role': 'title' if ordinal <= 4 else 'body', 'block': 'mock', 'lineInBlock': number + 1,
                         'printedText': ('Title' if ordinal <= 4 else 'Word' + str(ordinal) + ',') + ' Line-É'})
    funky, funky_raw = funky_original({'version': 1, 'modelId': 'funky-upheaval-physical-lines-v1', 'rows': rows})
    need([r['selectedRowCount'] for r in funky] == [111, 56, 55] and
         funky[0]['text'].startswith('Word5, Word6,') and 'Title' not in funky[0]['text'] and
         funky[1]['text'].split('\n')[3] == rows[10]['printedText'] and
         funky[2]['text'].split('\n')[3] == rows[11]['printedText'],
         'synthetic-title-exclusion-global-parity-page-boundary')
    need(funky_raw.endswith(b'\n') and b'\\u00c9' not in funky_raw and b'\xc3\x89' in funky_raw and
         list(decode_json(funky_raw)) == ['schemaVersion', 'testId', 'sourceSha256', 'readings'],
         'synthetic-Funky-UTF8-insertion-order-and-serializer')
    broken = [dict(row) for row in rows]
    broken[5]['printedText'] = ' Space'
    reject(funky_original, {'version': 1, 'modelId': 'funky-upheaval-physical-lines-v1', 'rows': broken})
    broken = [dict(row) for row in rows]
    broken[5]['printedText'] = 'Word\tGap'
    reject(funky_original, {'version': 1, 'modelId': 'funky-upheaval-physical-lines-v1', 'rows': broken})
    tokens = ['x' + str(n).zfill(4) for n in range(2018)]
    synthetic_rows = []
    for start, end in [(0, 7), (7, 14), (14, 2018)]:
        synthetic_rows.append({'rowId': 'synthetic-' + str(start), 'modelText': ' '.join(tokens[start:end]),
                               'uncertainForProjections': ['words', 'initials'], 'uncertainTokenIndices': [0]})
    stride, stride_raw = stride_original({'rows': synthetic_rows}, production=False)
    known = [r for r in stride if r['sourceCompleteForProjection']]
    need(len(stride) == 72 and len(known) == 60 and
         all(r['sourceCompleteForProjection'] for r in stride if r['projection'] == 'finals'),
         'synthetic-stride-nested-whole-reading-uncertainty')
    need(stride[0]['text'] == ' '.join(tokens[::12]) and
         stride[36]['text'] == ' '.join(list(reversed(tokens))[::12]) and
         stride[1]['text'] == 'x' * len(tokens[::12]) and
         stride[2]['text'] == ''.join(t[-1] for t in tokens[::12]),
         'synthetic-stride-direction-phase-and-three-projections')
    need(stride_raw.splitlines()[0].startswith(b'{"id": "forward:phase01:words", "direction": "forward"') and
         stride_raw == jsonl_bytes(stride), 'synthetic-stride-original-dict-serialization-order')
    toy_frozen = {'sourcePages': {}, 'rows': [], 'streams': {'z': 'é A\nB', 'a': 'C\u0301D'}, 'hits': {}, 'summary': {}}
    frozen, frozen_raw = frozen_original(toy_frozen, production=False)
    need([r['id'] for r in frozen] == ['a:exact', 'a:reversed-codepoints', 'z:exact', 'z:reversed-codepoints'] and
         frozen[1]['text'] == 'D\u0301C' and frozen[3]['text'] == 'B\nA é' and
         b'\\u0301' in frozen_raw and b'\\u00e9' in frozen_raw,
         'synthetic-frozen-sorted-label-existing-codepoint-reversal-and-ASCII-JSON')
    issue26 = [{'id': 'synthetic-' + str(i), 'text': text} for i, text in enumerate(['ABC', '', 'DEF', 'ABC'])]
    raw_issue26 = jsonl_bytes(issue26)
    zipped = gzip.compress(raw_issue26, mtime=0)
    need(expanded_gzip(zipped, len(raw_issue26), CAPS['jsonlLineBytes']) == raw_issue26,
         'synthetic-bounded-gzip-exact-original-bytes')
    reject(expanded_gzip, zipped, len(raw_issue26) - 1, CAPS['jsonlLineBytes'])
    reject(expanded_gzip, zipped, len(raw_issue26) + 1, CAPS['jsonlLineBytes'])
    reject(expanded_gzip, zipped, len(raw_issue26), 8)
    reject(expanded_gzip, zipped[:-3], len(raw_issue26), CAPS['jsonlLineBytes'])
    reject(expanded_gzip, gzip.compress(b'{}', mtime=0), 2, CAPS['jsonlLineBytes'])
    reject(decode_json, b'{"a":1,"a":2}')
    reject(decode_json, b'\xef\xbb\xbf{}')
    reject(decode_json, b'{"a":NaN}')
    reject(decode_json, b'\xff')
    need(helper.reconstruct_forms([{'id': 'a', 'text': 'A\u00a0B\tC\nD\u2003E'},
                                   {'id': 'b', 'text': 'F\u241e G'}, {'id': 'c', 'text': ''}]) ==
         sorted({'A\u00a0B\tC\nD\u2003E', 'ABCDE', 'F\u241e G', 'F\u241eG', ''}),
         'synthetic-Unicode-whitespace-only-empty-retention-and-hard-barrier')
    reject(forms_for, [{'id': 'bad', 'text': 'A B'}], 'issue26-first-words', False)
    fixtures = {'funky-sand-direct': funky, 'issue26-first-words': issue26,
                'issue27-body-stride12': stride, 'issue27-frozen-stream-coverage': frozen}
    forms, validation = derive_expected(fixtures, production=False)
    need(len(forms['cohorts']) == 4 and len(validation['cohorts']) == 4 and
         set(forms['cohorts'][2]['strictKnownForms']) <= set(forms['cohorts'][2]['forms']) and
         all(v['strictKnownForms'] is None for i, v in enumerate(forms['cohorts']) if i != 2),
         'synthetic-four-cohort-complete-objects-strict-nesting')
    controls = decode_json(bounded_bytes(public_file(public_scripts().parent, 'scripts/batch20_support/controls.json'), 200000))
    key22, key26, key30 = [synthetic_minikey(n) for n in [22, 26, 30]]
    payload = b'\x80' + bytes(31) + b'\x01' + b'\x01'
    wif = engine.b58encode(payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4])
    positives = [controls[k] for k in ['bip32_extended_private', 'bip38_encrypted_private', 'bip39_valid',
                                      'legacy_address', 'sec_compressed_generator']]
    positives += [wif, '0' * 63 + '1', key22, key30]
    summary, _, raw_positives = evaluate_formats(positives, COHORTS['funky-sand-direct']['commonFormats'])
    need(all(summary['validCounts'][kind] > 0 for kind in summary['formats']) and
         engine.validate_record('minikey', key22) is not None and engine.validate_record('minikey', key30) is not None,
         'synthetic-all-eight-Funky-positive-controls')
    four = ['extended_private', 'bip38', 'address', 'sec_public']
    alias_summary, _, alias_positives = evaluate_formats([controls['segwit_v0'], controls['segwit_v0'].upper()], four)
    need(alias_summary['validCounts']['address'] == 1 and
         sum(r['format'] == 'address' for r in alias_positives) == 2,
         'synthetic-raw-aliases-preserved-canonical-dedup')
    no_common = evaluate_formats(positives, [])
    need(no_common[0]['formats'] == [] and no_common[0]['validationCalls'] == 0 and no_common[1:] == ({}, []),
         'synthetic-Issue26-no-repeated-common-gates')
    reject(evaluate_formats, [], ['wif'])
    need(helper.independent_mini26(['prefix::' + key26 + '::suffix'])['validCount'] == 1 and
         helper.independent_mini26(['S' * 29])['shapeCount'] == 4 and
         helper.independent_mini26([key26[:22]])['shapeCount'] == 0 and
         helper.independent_mini26([key26[:13] + '\u241e' + key26[13:]])['shapeCount'] == 0 and
         helper.independent_mini26(helper.reconstruct_forms([{'id': 'a', 'text': key26[:13]},
                                                            {'id': 'b', 'text': key26[13:]}]))['shapeCount'] == 0,
         'synthetic-mini26-positive-overlap-tail-hardseparator-and-no-join')
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    bad26 = next(key26[:-1] + ch for ch in alphabet
                 if hashlib.sha256((key26[:-1] + ch + '?').encode('ascii')).digest()[0] != 0)
    need(helper.independent_mini26([bad26])['validCount'] == 0, 'synthetic-mini26-invalid-checksum')
    nominal = evaluation(positives + [key26], 'issue27-body-stride12')
    actual_validator, actual_mini, actual_fingerprint = engine.validate_record, helper.independent_mini26, engine.fingerprint
    try:
        engine.validate_record = forbidden
        helper.independent_mini26 = forbidden
        engine.fingerprint = forbidden
        derived = restricted_evaluation(positives + [key26], nominal, four)
        need(derived['common']['validationCalls'] == 0 and derived['minikey26']['checksumCalls'] == 0 and
             derived['minikey26']['status'] == 'derived-from-nominal-validation' and
             derived['minikey26']['proof'] == {'nominalValidationReused': True, 'nestedSubset': True} and
             derived['rawPositives'] == nominal['rawPositives'] and
             derived['minikey26Positives'] == nominal['minikey26Positives'],
             'synthetic-strict-known-cached-positives-no-validation-checksum-or-FP')
    finally:
        engine.validate_record, helper.independent_mini26, engine.fingerprint = actual_validator, actual_mini, actual_fingerprint

    safe, _, _ = safe_parts(fixtures, forms, validation)
    safe_text = canonical(safe)
    need(all(key not in safe_text for key in [key22, key26, key30]) and
         all(set(item) == set(SAFE_COHORT_KEYS) for item in safe) and
         not any('rawShapeValues' in item for item in safe), 'synthetic-safe-field-and-secret-omission')
    for path in [helper.site_root() / 'dist/synthetic-originals', Path('/tmp/public/synthetic-originals')]:
        reject(private, path, False)
    reject(registration, '/synthetic/wrong', 'bad')
    reject(registration, '/synthetic/wrong', '0' * 40)
    run = helper.subprocess.run
    class MockGit:
        def __init__(self, raw): self.returncode, self.stdout = 0, raw
    try:
        helper.subprocess.run = lambda *a, **k: MockGit(b'commit\n')
        helper.verify_commit_object(Path('/synthetic'), '1' * 40)
        for raw in [b'tag\n', b'tree\n', b'blob\n', b'']:
            helper.subprocess.run = lambda *a, _raw=raw, **k: MockGit(_raw)
            reject(helper.verify_commit_object, Path('/synthetic'), '1' * 40)
    finally:
        helper.subprocess.run = run
    return {'version': 1, 'status': 'PASS', 'syntheticCohorts': 4, 'syntheticOriginalSerializationRoutines': 3,
            'syntheticStrideReadings': 72, 'syntheticStrictKnownReadings': 60,
            'positiveSharedFamilies': 8, 'minikeyChecksumLengths': [22, 26, 30], 'rejectionControls': rejected,
            'directVerifiedByteCompilation': True, 'targetInputsOpened': 0, 'targetFormsOrShapesConstructed': 0,
            'primaryRunnerImports': 0, 'legacyLoaderCalls': 0, 'scalarDerivations': 0,
            'addressDerivations': 0, 'networkQueries': 0,
            'methodDependency': 'Reused frozen independent form/26 routines and deliberately shared literal validators.'}


def main():
    seen = set()
    for value in sys.argv[1:]:
        if value.startswith('--'):
            option = value.split('=', 1)[0]
            need(option not in seen, 'duplicate-command-argument')
            seen.add(option)
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--definition', action='store_true')
    mode.add_argument('--self-test', action='store_true')
    mode.add_argument('--verify', action='store_true')
    for name in ['protocol', 'registration-commit', 'result', 'forms', 'validation', 'artifacts-dir', 'out']:
        parser.add_argument('--' + name)
    args = parser.parse_args()
    if args.definition:
        result = {'testId': TEST_ID, 'protocolPath': PROTOCOL_REL, 'sourcePins': SOURCE_PINS,
                  'scriptPaths': SCRIPT_PATHS, 'fixedCodePins': FIXED_CODE_PINS,
                  'normativeProtocolTestCanonicalSha256': NORMATIVE_TEST_SHA256,
                  'normativeContractSha256': CONTRACT_SHA256, 'cohorts': list(COHORTS.values()),
                  'reusedIndependentPureFunctions': ['build_readings', 'source_rows', 'tokens_from_rows',
                                                     'reconstruct_forms', 'evaluate_common4', 'independent_mini26'],
                  'sharedValidatorMathematicsIndependentClaimed': False}
    elif args.self_test:
        result = self_test()
    else:
        need(all(getattr(args, name) for name in ['protocol', 'registration_commit', 'result', 'forms', 'validation',
                                                'artifacts_dir', 'out']), 'required-verification-arguments-missing')
        result = verify(args)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except GuardError as error:
        print(json.dumps({'status': 'FAIL-INCONCLUSIVE', 'errorCode': str(error)}))
        raise SystemExit(2)
    except Exception:
        print(json.dumps({'status': 'FAIL-INCONCLUSIVE', 'errorCode': 'unexpected-verification-failure'}))
        raise SystemExit(2)
