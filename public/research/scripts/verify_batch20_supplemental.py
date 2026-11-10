#!/usr/bin/env python3
"""Independent saved-output verifier for the fixed batch20 supplemental gates.

--self-test and --definition are source-free. --verify requires source/code/
protocol bytes in the actual public Git registration object. No primary runner
is imported. Four format checks deliberately reuse the pinned shared engine;
this is byte agreement, not an independent implementation of those formats.
Only26-character minikey windows of T01-T06 are independently enumerated here.
G03 uses its existing zero22-shape prefix implication, never a new minikey scan.
Python3.9+ and the actual Git registration commit object are required.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

TEST_ID = 'batch20-supplemental-fixed-formats'
BATCH_ID = 'keiser-batch20-supplemental-fixed-formats-20261110'
PROTOCOL_REL = "analysis_outputs/continuation_20261110/batch20_supplemental/PROTOCOL.json"
MANIFEST_REL = "analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json"
SELF_REL = "scripts/verify_batch20_supplemental.py"
PRIMARY_REL = "scripts/batch20_supplemental_formats.py"
COMMON_REL = "scripts/batch20_common.py"
COMMON_SHA = "48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d"
ENGLISH_SHA = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
CONTROLS_SHA = "d37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b"
COHORTS = ["T01", "T02", "T03", "T04", "T05", "T06", "G03"]
COMMON4 = ["extended_private", "bip38", "address", "sec_public"]
SCRIPT_PATHS = {PRIMARY_REL, SELF_REL, COMMON_REL}
B58 = frozenset("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
FP_DOMAIN_TEXT = "KEY404/batch20/record-fingerprint/v1"
FINGERPRINT_RULE = {"algorithm": "SHA-256", "domainText": FP_DOMAIN_TEXT,
                    "separatorHex": "00", "rule": "SHA256(domain || 0x00 || ASCII(format) || 0x00 || canonical record bytes)"}
CAP_INPUT = 2_000_000
CAP_PROTOCOL = 1_000_000
CAP_PRIVATE = 20_000_000
CAP_OCCURRENCES = 1_000_000
CAP_UNIQUE_SHAPES = 500_000
CAP_REGISTERED_BLOB = 20_000_000
EXPECTED_TEST = {'id': 'batch20-supplemental-fixed-formats',
 'title': 'Supplemental literal formats on seven unchanged frozen batch20 artifacts',
 'family': 'fixed-artifact-format-compatibility',
 'branchId': 'text-lines',
 'inputPaths': ['analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json',
                'analysis_outputs/continuation_20261110/batch20/T01/RESULT.json',
                'analysis_outputs/continuation_20261110/batch20/T01/INDEPENDENT_CHECK.json',
                'analysis_outputs/continuation_20261110/batch20/T02/STREAMS.json',
                'analysis_outputs/continuation_20261110/batch20/T02/RESULT.json',
                'analysis_outputs/continuation_20261110/batch20/T02/INDEPENDENT_CHECK.json',
                'analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json',
                'analysis_outputs/continuation_20261110/batch20/T03/RESULT.json',
                'analysis_outputs/continuation_20261110/batch20/T03/INDEPENDENT_CHECK.json',
                'analysis_outputs/continuation_20261110/batch20/T04/STREAMS.json',
                'analysis_outputs/continuation_20261110/batch20/T04/RESULT.json',
                'analysis_outputs/continuation_20261110/batch20/T04/INDEPENDENT_CHECK.json',
                'analysis_outputs/continuation_20261110/batch20/T05/STREAMS.json',
                'analysis_outputs/continuation_20261110/batch20/T05/RESULT.json',
                'analysis_outputs/continuation_20261110/batch20/T05/INDEPENDENT_CHECK.json',
                'analysis_outputs/continuation_20261110/batch20/T06/STREAMS.json',
                'analysis_outputs/continuation_20261110/batch20/T06/RESULT.json',
                'analysis_outputs/continuation_20261110/batch20/T06/INDEPENDENT_CHECK.json',
                'analysis_outputs/continuation_20261110/batch20/G03/STREAMS.json',
                'analysis_outputs/continuation_20261110/batch20/G03/RESULT.json',
                'analysis_outputs/continuation_20261110/batch20/G03/INDEPENDENT_CHECK.json',
                'scripts/batch20_support/controls.json',
                'scripts/batch20_support/english.txt',
                'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json'],
 'implementationPaths': ['scripts/batch20_supplemental_formats.py',
                         'scripts/verify_batch20_supplemental.py',
                         'scripts/batch20_common.py'],
 'protocolPath': 'analysis_outputs/continuation_20261110/batch20_supplemental/PROTOCOL.json',
 'manifest': {'path': 'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json',
              'sha256': '18c24b63f78a135f0cb43b380451184532fe443af4c118f2e71d2c638efc5b35'},
 'cohortOrder': ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'G03'],
 'sourceExpectations': [{'testId': 'T01',
                         'streamCount': 196,
                         'uniqueStreamCount': 152,
                         'uniqueFormCount': 236,
                         'legacyMinikeyShapeOccurrences': 21},
                        {'testId': 'T02',
                         'streamCount': 628,
                         'uniqueStreamCount': 628,
                         'uniqueFormCount': 1120,
                         'legacyMinikeyShapeOccurrences': 38},
                        {'testId': 'T03',
                         'streamCount': 120,
                         'uniqueStreamCount': 120,
                         'uniqueFormCount': 168,
                         'legacyMinikeyShapeOccurrences': 16},
                        {'testId': 'T04',
                         'streamCount': 252,
                         'uniqueStreamCount': 244,
                         'uniqueFormCount': 316,
                         'legacyMinikeyShapeOccurrences': 1},
                        {'testId': 'T05',
                         'streamCount': 42,
                         'uniqueStreamCount': 42,
                         'uniqueFormCount': 54,
                         'legacyMinikeyShapeOccurrences': 6},
                        {'testId': 'T06',
                         'streamCount': 60,
                         'uniqueStreamCount': 58,
                         'uniqueFormCount': 66,
                         'legacyMinikeyShapeOccurrences': 12},
                        {'testId': 'G03',
                         'streamCount': 1296,
                         'uniqueStreamCount': 615,
                         'uniqueFormCount': 616,
                         'legacyMinikeyShapeOccurrences': 0}],
 'fixedWitnessHashes': {'analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json': '2900473b467c74c18ee29f841f0fbb150376ffa42ab8e9862d9d0957fce8b395',
                        'analysis_outputs/continuation_20261110/batch20/T01/RESULT.json': 'f96c512124f8ab5314db28fe28627f6217d84a166f880c547c017b6f1acf386c',
                        'analysis_outputs/continuation_20261110/batch20/T01/INDEPENDENT_CHECK.json': 'c635f12fdf2ae8a22db366748cd38653259e446a59c23359608054ec899ba4e9',
                        'analysis_outputs/continuation_20261110/batch20/T02/STREAMS.json': 'b417af72e5cbacd69e928f561e811a71fee3e2ce2e68c0d29527a24863301e77',
                        'analysis_outputs/continuation_20261110/batch20/T02/RESULT.json': '40a4cd340eec86befea09a2636ff9d31a42c726db2933a2a24656c521d0bd93a',
                        'analysis_outputs/continuation_20261110/batch20/T02/INDEPENDENT_CHECK.json': 'e72a074973f060255fe9fe549d8bd097a2fe135954d624295d5a3c9b9192967e',
                        'analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json': '8977b65a1f14ddb36b97e05e58df145519f36f56ad18bf30957b328ec8d6c90f',
                        'analysis_outputs/continuation_20261110/batch20/T03/RESULT.json': '7322a06a7ee5218d6d49de9a4b840633d98fa3589bf004ca9d81401e94575ab6',
                        'analysis_outputs/continuation_20261110/batch20/T03/INDEPENDENT_CHECK.json': '4ef1781f09a6d8eec238250409994e5cb467e0ddf41867aff7a60e35d8f8d35b',
                        'analysis_outputs/continuation_20261110/batch20/T04/STREAMS.json': '9cb31c843434c66b640f7b31c96e308f10fe97f885880a115aac8b0eb7918958',
                        'analysis_outputs/continuation_20261110/batch20/T04/RESULT.json': '6884aeef447a581678172251db0f8db91bc6128339553b37e43409930d31dfcd',
                        'analysis_outputs/continuation_20261110/batch20/T04/INDEPENDENT_CHECK.json': 'e008d8d3f7d588a4da4c00dad1cd0d3e94fd2c65fcfa4e9325af3d0e620f4f46',
                        'analysis_outputs/continuation_20261110/batch20/T05/STREAMS.json': '5039524f203d542fa4d072185cd299e4703f5e3b559a1da322cfbf1fa3e86fad',
                        'analysis_outputs/continuation_20261110/batch20/T05/RESULT.json': 'dbe4ca0d3b0fcfe1d35dd0a7480828b9764f6e91da3c78235bcf69891d95346d',
                        'analysis_outputs/continuation_20261110/batch20/T05/INDEPENDENT_CHECK.json': 'd131b5081e559bdfe5073888159d9ebba8d0e7167017137b3b8aa21383edbccc',
                        'analysis_outputs/continuation_20261110/batch20/T06/STREAMS.json': '5f377eef671eac7a3211c4581fd74c68dbb9695e77113db9153b176059f965cf',
                        'analysis_outputs/continuation_20261110/batch20/T06/RESULT.json': '46c2a6391d344bfbbd6f049d212a5d882a303f2b1b65c390960cee51d046e07e',
                        'analysis_outputs/continuation_20261110/batch20/T06/INDEPENDENT_CHECK.json': '635798d6590d9deef9cec7a4f43f9a11e88ba6b49c99391100277e3dd0dd0561',
                        'analysis_outputs/continuation_20261110/batch20/G03/STREAMS.json': 'd2880ebef4d78bcc95d9d6d143ef29a1b9d1a4ac3540cafae821d7ddbb942211',
                        'analysis_outputs/continuation_20261110/batch20/G03/RESULT.json': '1dd11d9068514514d1812b34925d4da2fa005872f19d01edae55a4a1069385a2',
                        'analysis_outputs/continuation_20261110/batch20/G03/INDEPENDENT_CHECK.json': 'acfbdd79451b6a2443e325f1f35a0d78223adf62f1e9bbce1bae13ae9bd9422d',
                        'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b',
                        'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',
                        'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json': '18c24b63f78a135f0cb43b380451184532fe443af4c118f2e71d2c638efc5b35'},
 'forms': {'rule': 'Per cohort: unique exact text union Unicode-whitespace-only compaction via '
                   're.sub(r"\\s", "", text), deduplicated/sorted by Python string order. Empty strings '
                   'retained. No cross-cohort dedup.',
           'selectorRegeneration': False,
           'perCohortCountsRequired': True},
 'literalValidation': {'commonFormats': ['extended_private', 'bip38', 'address', 'sec_public'],
                       'commonImplementationUnchanged': True,
                       'commonSha256': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d',
                       'oldMinikeyCheckerCalled': False,
                       'uniqueRawValuesValidatedOncePerFormatPerCohort': True,
                       'validCountsDeduplicateCanonicalFingerprints': True,
                       'minikey26': {'cohorts': ['T01', 'T02', 'T03', 'T04', 'T05', 'T06'],
                                     'length': 26,
                                     'shape': 'Every overlapping embedded exact26 S-prefixed Base58 window, '
                                              'no outer boundaries.',
                                     'checksum': 'SHA256(ASCII(value + question mark))[0]==0; weak8bit check '
                                                 'only.',
                                     'fingerprint': 'Existing batch20 domain-separated record fingerprint on '
                                                    'ASCII value, private only.',
                                     'G03': 'No enumeration/checksum: same frozen forms plus saved zero '
                                            'legacy22/30 shape counter and independent check imply zero26 '
                                            'shapes by22-prefix inclusion.',
                                     'scalarHash': False}},
 'registrationGate': 'Public executing path; full40hex local Git registration object; fixed protocol and '
                     'all24source/3code current bytes must equal registered blobs before target JSON '
                     'parsing. Remote publication established separately by operator.',
 'caps': {'sourceJsonBytes': 2000000,
          'registeredBlobBytes': 20000000,
          'protocolBytes': 1000000,
          'privateArtifactBytes': 20000000,
          'streamCodepoints': 100000,
          'totalSourceCodepoints': 2000000,
          'totalFormCodepoints': 4000000,
          'shapeOccurrencesPerCohort': 1000000,
          'uniqueShapesPerCohort': 500000},
 'outputPolicy': {'rawArtifacts': ['FORMS.private.json', 'VALIDATION.private.json'],
                  'rawOutsideEntireSiteCheckout': True,
                  'directoryMode': '0700',
                  'fileMode': '0600',
                  'publicReceipt': 'Aggregate per-cohort/total counts, scope and whole-artifact integrity '
                                   'only; no values, fingerprints, addresses, SEC text or hit locators.',
                  'semanticConclusionComputed': False},
 'activityBoundary': {'selectorRegenerations': 0,
                      'newTransformsBeyondExistingForms': 0,
                      'oldSharedMinikeyCalls': 0,
                      'G03Minikey26Enumerations': 0,
                      'G03Minikey26ChecksumCalls': 0,
                      'minikeyScalarHashes': 0,
                      'proseToKeyHashes': 0,
                      'scalarDerivations': 0,
                      'addressDerivations': 0,
                      'seedDerivations': 0,
                      'childKeyDerivations': 0,
                      'networkQueries': 0,
                      'transactions': 0},
 'limitations': ['This supplements record-format gates on seven exact saved artifacts; it does not '
                 'regenerate, extend or validate their source selectors.',
                 'The four shared validators are unchanged; shape and validation logic for those four '
                 'formats is shared, not an independent implementation.',
                 'SEC on-curve matches and weak8bit minikey checks are leads only; BIP38 is '
                 'structure/checksum validation, not decryption.',
                 'No semantic recognition, physical geometry conclusion, prize authentication, funding check '
                 'or whole-puzzle exclusion is computed.',
                 'G03 minikey26 coverage is a recorded zero22-shape prefix implication on identical forms, '
                 'not a new26 enumeration.']}
EXPECTED_ACTIVITY = {'selectorRegenerations': 0,
 'newTransformsBeyondExistingForms': 0,
 'oldSharedMinikeyCalls': 0,
 'G03Minikey26Enumerations': 0,
 'G03Minikey26ChecksumCalls': 0,
 'minikeyScalarHashes': 0,
 'proseToKeyHashes': 0,
 'scalarDerivations': 0,
 'addressDerivations': 0,
 'seedDerivations': 0,
 'childKeyDerivations': 0,
 'networkQueries': 0,
 'transactions': 0}

class GuardError(Exception):
    pass

SOURCE_PINS = {'analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json': '2900473b467c74c18ee29f841f0fbb150376ffa42ab8e9862d9d0957fce8b395',
 'analysis_outputs/continuation_20261110/batch20/T01/RESULT.json': 'f96c512124f8ab5314db28fe28627f6217d84a166f880c547c017b6f1acf386c',
 'analysis_outputs/continuation_20261110/batch20/T01/INDEPENDENT_CHECK.json': 'c635f12fdf2ae8a22db366748cd38653259e446a59c23359608054ec899ba4e9',
 'analysis_outputs/continuation_20261110/batch20/T02/STREAMS.json': 'b417af72e5cbacd69e928f561e811a71fee3e2ce2e68c0d29527a24863301e77',
 'analysis_outputs/continuation_20261110/batch20/T02/RESULT.json': '40a4cd340eec86befea09a2636ff9d31a42c726db2933a2a24656c521d0bd93a',
 'analysis_outputs/continuation_20261110/batch20/T02/INDEPENDENT_CHECK.json': 'e72a074973f060255fe9fe549d8bd097a2fe135954d624295d5a3c9b9192967e',
 'analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json': '8977b65a1f14ddb36b97e05e58df145519f36f56ad18bf30957b328ec8d6c90f',
 'analysis_outputs/continuation_20261110/batch20/T03/RESULT.json': '7322a06a7ee5218d6d49de9a4b840633d98fa3589bf004ca9d81401e94575ab6',
 'analysis_outputs/continuation_20261110/batch20/T03/INDEPENDENT_CHECK.json': '4ef1781f09a6d8eec238250409994e5cb467e0ddf41867aff7a60e35d8f8d35b',
 'analysis_outputs/continuation_20261110/batch20/T04/STREAMS.json': '9cb31c843434c66b640f7b31c96e308f10fe97f885880a115aac8b0eb7918958',
 'analysis_outputs/continuation_20261110/batch20/T04/RESULT.json': '6884aeef447a581678172251db0f8db91bc6128339553b37e43409930d31dfcd',
 'analysis_outputs/continuation_20261110/batch20/T04/INDEPENDENT_CHECK.json': 'e008d8d3f7d588a4da4c00dad1cd0d3e94fd2c65fcfa4e9325af3d0e620f4f46',
 'analysis_outputs/continuation_20261110/batch20/T05/STREAMS.json': '5039524f203d542fa4d072185cd299e4703f5e3b559a1da322cfbf1fa3e86fad',
 'analysis_outputs/continuation_20261110/batch20/T05/RESULT.json': 'dbe4ca0d3b0fcfe1d35dd0a7480828b9764f6e91da3c78235bcf69891d95346d',
 'analysis_outputs/continuation_20261110/batch20/T05/INDEPENDENT_CHECK.json': 'd131b5081e559bdfe5073888159d9ebba8d0e7167017137b3b8aa21383edbccc',
 'analysis_outputs/continuation_20261110/batch20/T06/STREAMS.json': '5f377eef671eac7a3211c4581fd74c68dbb9695e77113db9153b176059f965cf',
 'analysis_outputs/continuation_20261110/batch20/T06/RESULT.json': '46c2a6391d344bfbbd6f049d212a5d882a303f2b1b65c390960cee51d046e07e',
 'analysis_outputs/continuation_20261110/batch20/T06/INDEPENDENT_CHECK.json': '635798d6590d9deef9cec7a4f43f9a11e88ba6b49c99391100277e3dd0dd0561',
 'analysis_outputs/continuation_20261110/batch20/G03/STREAMS.json': 'd2880ebef4d78bcc95d9d6d143ef29a1b9d1a4ac3540cafae821d7ddbb942211',
 'analysis_outputs/continuation_20261110/batch20/G03/RESULT.json': '1dd11d9068514514d1812b34925d4da2fa005872f19d01edae55a4a1069385a2',
 'analysis_outputs/continuation_20261110/batch20/G03/INDEPENDENT_CHECK.json': 'acfbdd79451b6a2443e325f1f35a0d78223adf62f1e9bbce1bae13ae9bd9422d',
 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b',
 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',
 'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json': '18c24b63f78a135f0cb43b380451184532fe443af4c118f2e71d2c638efc5b35'}
COHORT_METADATA = {'T01': {'records': 196,
         'uniqueTexts': 152,
         'forms': 236,
         'streamsSha256': '2900473b467c74c18ee29f841f0fbb150376ffa42ab8e9862d9d0957fce8b395',
         'resultSha256': 'f96c512124f8ab5314db28fe28627f6217d84a166f880c547c017b6f1acf386c',
         'checkSha256': 'c635f12fdf2ae8a22db366748cd38653259e446a59c23359608054ec899ba4e9'},
 'T02': {'records': 628,
         'uniqueTexts': 628,
         'forms': 1120,
         'streamsSha256': 'b417af72e5cbacd69e928f561e811a71fee3e2ce2e68c0d29527a24863301e77',
         'resultSha256': '40a4cd340eec86befea09a2636ff9d31a42c726db2933a2a24656c521d0bd93a',
         'checkSha256': 'e72a074973f060255fe9fe549d8bd097a2fe135954d624295d5a3c9b9192967e'},
 'T03': {'records': 120,
         'uniqueTexts': 120,
         'forms': 168,
         'streamsSha256': '8977b65a1f14ddb36b97e05e58df145519f36f56ad18bf30957b328ec8d6c90f',
         'resultSha256': '7322a06a7ee5218d6d49de9a4b840633d98fa3589bf004ca9d81401e94575ab6',
         'checkSha256': '4ef1781f09a6d8eec238250409994e5cb467e0ddf41867aff7a60e35d8f8d35b'},
 'T04': {'records': 252,
         'uniqueTexts': 244,
         'forms': 316,
         'streamsSha256': '9cb31c843434c66b640f7b31c96e308f10fe97f885880a115aac8b0eb7918958',
         'resultSha256': '6884aeef447a581678172251db0f8db91bc6128339553b37e43409930d31dfcd',
         'checkSha256': 'e008d8d3f7d588a4da4c00dad1cd0d3e94fd2c65fcfa4e9325af3d0e620f4f46'},
 'T05': {'records': 42,
         'uniqueTexts': 42,
         'forms': 54,
         'streamsSha256': '5039524f203d542fa4d072185cd299e4703f5e3b559a1da322cfbf1fa3e86fad',
         'resultSha256': 'dbe4ca0d3b0fcfe1d35dd0a7480828b9764f6e91da3c78235bcf69891d95346d',
         'checkSha256': 'd131b5081e559bdfe5073888159d9ebba8d0e7167017137b3b8aa21383edbccc'},
 'T06': {'records': 60,
         'uniqueTexts': 58,
         'forms': 66,
         'streamsSha256': '5f377eef671eac7a3211c4581fd74c68dbb9695e77113db9153b176059f965cf',
         'resultSha256': '46c2a6391d344bfbbd6f049d212a5d882a303f2b1b65c390960cee51d046e07e',
         'checkSha256': '635798d6590d9deef9cec7a4f43f9a11e88ba6b49c99391100277e3dd0dd0561'},
 'G03': {'records': 1296,
         'uniqueTexts': 615,
         'forms': 616,
         'streamsSha256': 'd2880ebef4d78bcc95d9d6d143ef29a1b9d1a4ac3540cafae821d7ddbb942211',
         'resultSha256': '1dd11d9068514514d1812b34925d4da2fa005872f19d01edae55a4a1069385a2',
         'checkSha256': 'acfbdd79451b6a2443e325f1f35a0d78223adf62f1e9bbce1bae13ae9bd9422d'}}

def require(value, code):
    if not value:
        raise GuardError(code)

def sha(data):
    """Integrity checks only; minikey checks append '?', never a bare key hash."""
    return hashlib.sha256(data).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)

def common_path():
    sibling = Path(__file__).resolve().parent / "batch20_common.py"
    if sibling.is_file():
        return sibling
    # Authoring/self-test convenience only. --verify requires the installed
    # public runtime path and all registered bytes before source extraction.
    fallback = Path(__file__).resolve().parents[3] / "site/public/research/scripts/batch20_common.py"
    require(fallback.is_file(), "pinned-shared-helper-not-found")
    return fallback

def load_common():
    file = common_path()
    require(file.stat().st_size <= CAP_INPUT and sha(file.read_bytes()) == COMMON_SHA, "shared-helper-pin-mismatch")
    support = file.parent / "batch20_support"
    for name, pin in [("english.txt", ENGLISH_SHA), ("controls.json", CONTROLS_SHA)]:
        require(sha((support / name).read_bytes()) == pin, "shared-support-pin-mismatch")
    spec = importlib.util.spec_from_file_location("supplemental_independent_shared4", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def site_root():
    return common_path().resolve().parents[3]

def private_path(value, existing=True):
    path = Path(value).resolve()
    require(not any(part.casefold() == "public" for part in path.parts) and
            not path.is_relative_to(site_root()), "private-path-outside-entire-public-checkout-required")
    if existing:
        require(path.is_file() and path.stat().st_mode & 0o077 == 0, "private-input-file-permissions-required")
    else:
        require(not path.exists() and path.parent.is_dir() and path.parent.stat().st_mode & 0o077 == 0, "fresh-private-output-required")
    return path

def read_json(path, maximum=CAP_INPUT):
    path = Path(path)
    require(path.is_file() and path.stat().st_size <= maximum, "input-file-size-or-existence-guard")
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), "UTF8-without-BOM-required")
    def unique_keys(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "duplicate-json-key")
            value[key] = item
        return value
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys), raw
    except (UnicodeError, ValueError):
        raise GuardError("invalid-UTF8-or-JSON") from None

def write_private(path, value):
    data = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    require(len(data) <= CAP_INPUT, "private-output-byte-cap")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)

def check_stream_population(streams, cohort, production=True):
    require(cohort in COHORTS and isinstance(streams, list) and 0 < len(streams) <= 2000,
            'invalid-saved-stream-population')
    identifiers, total = [], 0
    for record in streams:
        require(isinstance(record, dict) and isinstance(record.get('id'), str) and
                record['id'] and isinstance(record.get('text'), str) and len(record['text']) <= 100_000, 'invalid-saved-stream-record')
        identifiers.append(record['id'])
        total += len(record['text'])
    require(len(set(identifiers)) == len(identifiers), 'duplicate-saved-stream-id')
    require(total <= 2_000_000, 'saved-cohort-codepoint-cap')
    unique = len({record['text'] for record in streams})
    if production:
        expected = COHORT_METADATA[cohort]
        require(len(streams) == expected['records'] and unique == expected['uniqueTexts'],
                'frozen-cohort-record-or-unique-text-count-mismatch')
    return {'streamCount': len(streams), 'uniqueStreamCount': unique, 'sourceCodepoints': total}


def reconstruct_forms(streams):
    # Every source record is separate. No cross-record concatenation is allowed.
    exact = set()
    compact = set()
    for record in streams:
        text = record['text']
        exact.add(text)
        without_whitespace = []
        for character in text:
            if not character.isspace():
                without_whitespace.append(character)
        compact.add(''.join(without_whitespace))
    forms = sorted(exact | compact)
    require(len(forms) <= 4000 and sum(len(value) for value in forms) <= 4_000_000,
            'saved-cohort-form-count-or-codepoint-cap')
    return forms


def mini26_fingerprint(value):
    return hashlib.sha256((FP_DOMAIN_TEXT + '\x00minikey\x00' + value).encode('ascii')).hexdigest()


def independent_mini26(forms):
    occurrences, values = 0, set()
    for text in forms:
        for start, first in enumerate(text):
            if first != 'S' or start + 26 > len(text):
                continue
            candidate = text[start:start + 26]
            if all(character in B58 for character in candidate):
                occurrences += 1
                values.add(candidate)
                require(occurrences <= CAP_OCCURRENCES and len(values) <= CAP_UNIQUE_SHAPES, 'mini26-resource-cap')
    accepted = []
    for candidate in sorted(values):
        if hashlib.sha256((candidate + '?').encode('ascii')).digest()[0] == 0:
            accepted.append({'format': 'minikey', 'length': 26, 'checkBits': 8, 'private': True,
                             'fingerprint': mini26_fingerprint(candidate), 'value': candidate})
    return {'shapeCount': occurrences, 'uniqueShapeCount': len(values), 'checksumCalls': len(values),
            'validCount': len(accepted), 'privateReviewRequired': bool(accepted),
            'shapeValues': sorted(values), 'validRecords': accepted}


def evaluate_common4(forms, common):
    occurrence = {kind: 0 for kind in COMMON4}
    unique = {kind: set() for kind in COMMON4}
    for text in forms:
        for kind in COMMON4:
            for value in common.shape_values(kind, text):
                occurrence[kind] += 1
                unique[kind].add(value)
                require(sum(occurrence.values()) <= CAP_OCCURRENCES and
                        sum(len(values) for values in unique.values()) <= CAP_UNIQUE_SHAPES,
                        'shared-four-resource-cap')
    raw_shapes = {kind: sorted(unique[kind]) for kind in COMMON4}
    positives, fingerprints = [], {kind: set() for kind in COMMON4}
    for kind in COMMON4:
        for value in raw_shapes[kind]:
            checked = common.validate_record(kind, value)
            if checked is None:
                continue
            encoded, metadata = checked
            fingerprint = common.fingerprint(kind, encoded)
            positives.append({'format': kind, 'value': value, 'fingerprint': fingerprint, 'metadata': metadata})
            fingerprints[kind].add(fingerprint)
    summary = {'formats': COMMON4, 'shapeCounts': occurrence,
               'uniqueShapeCounts': {kind: len(unique[kind]) for kind in COMMON4},
               'validationCalls': sum(len(values) for values in unique.values()),
               'validCounts': {kind: len(fingerprints[kind]) for kind in COMMON4},
               'privateReviewRequired': bool(positives), 'fingerprintRule': FINGERPRINT_RULE}
    return summary, raw_shapes, positives


def shared_four(streams, forms, common):
    # Source-free control adapter. Target evaluation below consumes only the
    # already independently reconstructed forms, not a new source selector.
    require(len(forms) == len(reconstruct_forms(streams)), 'synthetic-form-adapter-population')
    return evaluate_common4(forms, common)[0]


def validate_test(test):
    require(EXPECTED_TEST is not None and isinstance(test, dict), 'frozen-protocol-contract-unavailable')
    require(canonical(test) == canonical(EXPECTED_TEST), 'protocol-normative-test-mismatch')


def verify_commit_object(research, registration):
    checked = subprocess.run(['git', 'cat-file', '-t', registration], cwd=research,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
    require(checked.returncode == 0 and checked.stdout.strip() == b'commit',
            'registration-object-must-be-commit')


def registered_pins(protocol_path, registration):
    require(re.fullmatch(r'[0-9a-f]{40}', registration or '') is not None, 'invalid-registration-commit')
    research = Path(__file__).resolve().parent.parent
    require((research / SELF_REL).resolve() == Path(__file__).resolve(), 'installed-public-verifier-required')
    require(Path(protocol_path).resolve() == (research / PROTOCOL_REL).resolve(), 'fixed-protocol-path-required')
    verify_commit_object(research, registration)
    protocol, raw = read_json(protocol_path, CAP_PROTOCOL)
    require(protocol.get('version') == 1 and protocol.get('batchId') == BATCH_ID, 'protocol-identity-mismatch')
    validate_test(protocol.get('test'))
    sources, scripts = protocol.get('sourceHashes'), protocol.get('scriptHashes')
    require(canonical(sources) == canonical(SOURCE_PINS) and isinstance(scripts, dict) and
            set(scripts) == SCRIPT_PATHS and scripts.get(COMMON_REL) == COMMON_SHA,
            'registered-pin-population-or-value-mismatch')
    pins = dict(sources)
    pins.update(scripts)
    pins[PROTOCOL_REL] = sha(raw)
    for relative, expected in pins.items():
        require(isinstance(expected, str) and re.fullmatch(r'[a-f0-9]{64}', expected) is not None,
                'invalid-SHA256-pin')
        file = (research / relative).resolve()
        require(file.is_relative_to(research) and file.is_file() and file.stat().st_size <= CAP_REGISTERED_BLOB,
                'registered-local-file-guard')
        require(sha(file.read_bytes()) == expected, 'registered-local-byte-mismatch')
        saved = subprocess.run(['git', 'show', registration + ':public/research/' + relative],
                               cwd=research, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        require(saved.returncode == 0 and len(saved.stdout) <= CAP_REGISTERED_BLOB and sha(saved.stdout) == expected,
                'actual-registration-byte-mismatch')
    return protocol, sha(raw), research

def synthetic_source_cohorts():
    cohorts = {}
    for name in COHORTS:
        metadata = COHORT_METADATA[name]
        unique, count = metadata['uniqueTexts'], metadata['records']
        require(unique <= metadata['forms'] <= 2 * unique, 'synthetic-manifest-form-feasibility')
        need_compaction = metadata['forms'] - unique
        texts = [('Synthetic-' + name + '-' + str(i) + (' remainder' if i < need_compaction else ''))
                 for i in range(unique)]
        records = [{'id': 'synthetic-' + name + '-' + str(i), 'text': texts[i % unique]}
                   for i in range(count)]
        check_stream_population(records, name)
        require(len(reconstruct_forms(records)) == metadata['forms'], 'synthetic-full-cohort-form-count')
        cohorts[name] = records
    return cohorts


def core_self_test():
    rejected = 0
    source = [{'id': 'one', 'text': 'A\tB\u00a0C\nD\u2003E'},
              {'id': 'two', 'text': 'F\u241e G'}, {'id': 'three', 'text': 'A\tB\u00a0C\nD\u2003E'}]
    forms = reconstruct_forms(source)
    require(forms == sorted({'A\tB\u00a0C\nD\u2003E', 'ABCDE', 'F\u241e G', 'F\u241eG'}),
            'synthetic-Unicode-whitespace-and-hard-separator-control')
    require(reconstruct_forms([{'id': 'a', 'text': 'left'}, {'id': 'b', 'text': 'right'}]) == ['left', 'right'],
            'synthetic-no-cross-record-join-control')
    mock = synthetic_source_cohorts()
    require(sum(len(records) for records in mock.values()) == 2594 and
            sum(len(reconstruct_forms(records)) for records in mock.values()) == 2576,
            'synthetic-all-seven-cohort-population-control')
    for malformed in [[], {}, [{'id': '', 'text': 'a'}], [{'id': 'a', 'text': 3}],
                      [{'id': 'a', 'text': 'one'}, {'id': 'a', 'text': 'two'}]]:
        try:
            check_stream_population(malformed, 'T01', False)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-invalid-saved-stream-accepted')
    for cohort, records in mock.items():
        changed = records[:-1]
        try:
            check_stream_population(changed, cohort)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-cohort-count-mutation-accepted')
    common = load_common()
    controls = json.loads((common_path().parent / 'batch20_support/controls.json').read_text())
    positives = [{'id': 'synthetic-' + key, 'text': controls[key]} for key in
                 ['bip32_extended_private', 'bip38_encrypted_private', 'legacy_address', 'sec_compressed_generator']]
    result = shared_four(positives, reconstruct_forms(positives), common)
    require(all(result['validCounts'][name] >= 1 for name in COMMON4), 'synthetic-four-format-positive-controls')
    require('minikey' not in COMMON4, 'synthetic-shared-old-minikey-excluded')
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    good = None
    for number in range(65536):
        n, suffix = number, ''
        for _ in range(8):
            n, digit = divmod(n, 58)
            suffix = alphabet[digit] + suffix
        candidate = 'S' + '2' * 17 + suffix
        if hashlib.sha256((candidate + '?').encode('ascii')).digest()[0] == 0:
            good = candidate
            break
    require(good is not None and len(good) == 26, 'synthetic-mini26-positive-within-bound')
    mini = independent_mini26(['prefix::' + good + '::suffix'])
    require(mini['shapeCount'] == 1 and mini['uniqueShapeCount'] == 1 and mini['validCount'] == 1,
            'synthetic-mini26-embedded-positive')
    bad = next(good[:-1] + c for c in alphabet
               if hashlib.sha256((good[:-1] + c + '?').encode('ascii')).digest()[0] != 0)
    require(independent_mini26([bad])['validCount'] == 0, 'synthetic-mini26-invalid-questionmark-checksum')
    require(independent_mini26(['S' * 29])['shapeCount'] == 4, 'synthetic-mini26-overlapping-windows')
    require(independent_mini26([good[:22]])['shapeCount'] == 0 and
            independent_mini26([good[:25]])['shapeCount'] == 0, 'synthetic-short-tail-length-regression')
    require(independent_mini26([good[:13] + '\u241e' + good[13:]])['shapeCount'] == 0 and
            independent_mini26([good[:13] + '0' + good[13:]])['shapeCount'] == 0,
            'synthetic-hard-separator-and-invalid-alphabet-barriers')
    split = [{'id': 'a', 'text': good[:13]}, {'id': 'b', 'text': good[13:]}]
    require(independent_mini26(reconstruct_forms(split))['shapeCount'] == 0,
            'synthetic-no-record-joining-mini-positive')
    spaced = [{'id': 'a', 'text': good[:13] + '\u00a0' + good[13:]}]
    require(independent_mini26(reconstruct_forms(spaced))['validCount'] == 1,
            'synthetic-whitespace-compact-mini-positive')
    dup = independent_mini26([good, good])
    require(dup['shapeCount'] == 2 and dup['uniqueShapeCount'] == 1 and dup['checksumCalls'] == 1,
            'synthetic-mini-occurrence-versus-unique-control')
    for bad_path in [site_root() / 'dist/synthetic-private-output', Path('/tmp/public/synthetic-private-output')]:
        try:
            private_path(bad_path, False)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-public-output-path-accepted')
    return {'syntheticCohorts': 7, 'syntheticLabeledRecords': 2594, 'syntheticPerCohortFormsSum': 2576,
            'sharedFormatPositiveControls': 4, 'rejectionControls': rejected,
            'targetInputsOpened': 0, 'targetShapeChecks': 0, 'networkQueries': 0, 'primaryRunnerImports': 0}

def manifest_cohorts(manifest):
    require(isinstance(manifest, dict) and manifest.get('version') == 1 and
            isinstance(manifest.get('cohorts'), list) and
            [record.get('testId') for record in manifest['cohorts']] == COHORTS,
            'manifest-cohort-population-mismatch')
    answer = {}
    for row in manifest['cohorts']:
        cohort, expected = row['testId'], COHORT_METADATA[row['testId']]
        require(row.get('labeledStreamCount') == expected['records'] and
                row.get('uniqueStreamCountReported') == expected['uniqueTexts'] and
                row.get('uniqueFormCountReported') == expected['forms'] and
                row.get('publicArtifactSha256') == expected['streamsSha256'] and
                row.get('safeResultSha256') == expected['resultSha256'] and
                row.get('independentCheckSha256') == expected['checkSha256'],
                'manifest-expectation-or-witness-pin-mismatch')
        if cohort == 'G03':
            require(row.get('logicalMinikey26ShapeExclusionFromZero22Prefix') is True and
                    row.get('legacyMinikeyShapeOccurrences') == 0, 'G03-manifest-prefix-premise-mismatch')
        answer[cohort] = row
    return answer


def legacy_witnesses(cohort, old_result, old_check, row):
    expected = COHORT_METADATA[cohort]
    require(isinstance(old_result, dict) and old_result.get('testId') == cohort and
            isinstance(old_result.get('evaluation'), dict), 'legacy-result-identity-mismatch')
    evaluation = old_result['evaluation']
    require(evaluation.get('streamCount') == expected['records'] and
            evaluation.get('uniqueStreamCount') == expected['uniqueTexts'] and
            evaluation.get('uniqueFormCount') == expected['forms'] and
            evaluation.get('formats') == ['wif', 'minikey', 'hex64', 'bip39'],
            'legacy-result-count-or-format-mismatch')
    require(isinstance(evaluation.get('shapeCounts'), dict) and
            set(evaluation['shapeCounts']) == {'wif', 'minikey', 'hex64', 'bip39'} and
            all(type(count) is int and count >= 0 for count in evaluation['shapeCounts'].values()) and
            canonical(evaluation.get('validCounts')) == canonical({'wif': 0, 'minikey': 0, 'hex64': 0, 'bip39': 0}) and
            evaluation['shapeCounts']['minikey'] == row.get('legacyMinikeyShapeOccurrences'),
            'legacy-shape-or-negative-count-witness-mismatch')
    require(isinstance(old_check, dict) and old_check.get('testId') == cohort and
            old_check.get('passed') is True and old_check.get('streamCount') == expected['records'] and
            old_check.get('uniqueFormCount') == expected['forms'] and
            canonical(old_check.get('shapeCounts')) == canonical(evaluation['shapeCounts']) and
            type(old_check.get('validRecords')) is int and old_check['validRecords'] == 0 and
            type(old_check.get('networkQueries')) is int and old_check['networkQueries'] == 0,
            'legacy-independent-check-witness-mismatch')
    if cohort == 'G03':
        require(old_result.get('completeNegative') is True and evaluation['shapeCounts']['minikey'] == 0 and
                row.get('logicalMinikey26ShapeExclusionFromZero22Prefix') is True,
                'G03-zero-prefix-implication-unavailable')


def source_streams(raw, cohort):
    if cohort == 'G03':
        require(isinstance(raw, list), 'G03-saved-list-required')
        streams = raw
    else:
        require(isinstance(raw, dict) and isinstance(raw.get('streams'), list), 'text-saved-streams-object-required')
        streams = raw['streams']
    check_stream_population(streams, cohort)
    return streams


def evaluate_cohort(cohort, streams, manifest_row, common):
    forms = reconstruct_forms(streams)
    require(len(forms) == COHORT_METADATA[cohort]['forms'], 'frozen-form-count-mismatch')
    common_summary, raw_shapes, raw_positives = evaluate_common4(forms, common)
    if cohort == 'G03':
        require(manifest_row.get('logicalMinikey26ShapeExclusionFromZero22Prefix') is True and
                manifest_row.get('legacyMinikeyShapeOccurrences') == 0, 'G03-prefix-premise-required')
        mini = {'status': 'inferred-no-shapes-from-zero-legacy22', 'enumerated': False, 'length': 26,
                'shapeOccurrences': 0, 'uniqueShapeCount': 0, 'checksumCalls': 0, 'validCount': 0,
                'privateReviewRequired': False, 'fingerprintRule': FINGERPRINT_RULE,
                'proof': {'legacyMinikeyShapeOccurrences': 0, 'legacyCheckPassed': True,
                          'legacyCheckValidRecords': 0, 'prefixLength': 22, 'extendedLength': 26,
                          'outerBoundaryRequired': False, 'sameFrozenForms': True}}
        mini_shapes, mini_positives = [], []
    else:
        raw_mini = independent_mini26(forms)
        mini = {'status': 'checked', 'enumerated': True, 'length': 26,
                'shapeOccurrences': raw_mini['shapeCount'], 'uniqueShapeCount': raw_mini['uniqueShapeCount'],
                'checksumCalls': raw_mini['checksumCalls'], 'validCount': raw_mini['validCount'],
                'privateReviewRequired': raw_mini['privateReviewRequired'], 'fingerprintRule': FINGERPRINT_RULE,
                'proof': None}
        mini_shapes, mini_positives = raw_mini['shapeValues'], raw_mini['validRecords']
    private_forms = {'testId': cohort, 'sourceArtifactSha256': COHORT_METADATA[cohort]['streamsSha256'],
                     'streams': streams, 'forms': forms}
    validation = {'testId': cohort, 'common4': common_summary, 'rawShapeValues': raw_shapes,
                  'rawPositives': raw_positives, 'minikey26': mini, 'minikey26Shapes': mini_shapes,
                  'minikey26Positives': mini_positives}
    return private_forms, validation


def safe_cohort(forms, validation):
    common = validation['common4']
    mini = validation['minikey26']
    return {'testId': forms['testId'], 'streamCount': len(forms['streams']),
            'uniqueStreamCount': len({record['text'] for record in forms['streams']}),
            'uniqueFormCount': len(forms['forms']),
            'common4': {key: common[key] for key in ['formats', 'shapeCounts', 'uniqueShapeCounts',
                                                   'validationCalls', 'validCounts']},
            'minikey26': {key: mini[key] for key in ['status', 'enumerated', 'shapeOccurrences',
                                                   'uniqueShapeCount', 'checksumCalls', 'validCount']}}


def safe_totals(cohorts):
    return {'cohorts': len(cohorts), 'labeledStreams': sum(row['streamCount'] for row in cohorts),
            'sumPerCohortUniqueForms': sum(row['uniqueFormCount'] for row in cohorts),
            'commonShapeCounts': {kind: sum(row['common4']['shapeCounts'][kind] for row in cohorts) for kind in COMMON4},
            'commonUniqueShapeCountsSum': {kind: sum(row['common4']['uniqueShapeCounts'][kind] for row in cohorts) for kind in COMMON4},
            'commonValidationCalls': sum(row['common4']['validationCalls'] for row in cohorts),
            'commonValidCountsSum': {kind: sum(row['common4']['validCounts'][kind] for row in cohorts) for kind in COMMON4},
            'minikey26ShapeOccurrences': sum(row['minikey26']['shapeOccurrences'] for row in cohorts),
            'minikey26UniqueShapesSum': sum(row['minikey26']['uniqueShapeCount'] for row in cohorts),
            'minikey26ChecksumCalls': sum(row['minikey26']['checksumCalls'] for row in cohorts),
            'minikey26ValidCountSum': sum(row['minikey26']['validCount'] for row in cohorts)}


def verify(args):
    output = private_path(args.out, False)
    forms_path = private_path(args.forms)
    validation_path = private_path(args.validation)
    result_path = private_path(args.result)
    protocol, protocol_sha, research = registered_pins(args.protocol, args.registration_commit)
    # All24witness/current/registered byte checks completed before any target
    # cohort JSON is parsed or a saved form is constructed.
    manifest, _ = read_json(research / MANIFEST_REL)
    metadata = manifest_cohorts(manifest)
    common = load_common()
    expected_forms, expected_validation, safe = [], [], []
    total_source, total_forms = 0, 0
    for cohort in COHORTS:
        base = research / 'analysis_outputs/continuation_20261110/batch20' / cohort
        raw, _ = read_json(base / 'STREAMS.json')
        old_result, _ = read_json(base / 'RESULT.json')
        old_check, _ = read_json(base / 'INDEPENDENT_CHECK.json')
        legacy_witnesses(cohort, old_result, old_check, metadata[cohort])
        streams = source_streams(raw, cohort)
        total_source += sum(len(record['text']) for record in streams)
        forms, validation = evaluate_cohort(cohort, streams, metadata[cohort], common)
        total_forms += sum(len(text) for text in forms['forms'])
        require(total_source <= 2_000_000 and total_forms <= 4_000_000, 'aggregate-source-or-form-codepoint-cap')
        expected_forms.append(forms)
        expected_validation.append(validation)
        safe.append(safe_cohort(forms, validation))
    expected_forms = {'schemaVersion': 1, 'testId': TEST_ID,
                      'manifestSha256': SOURCE_PINS[MANIFEST_REL], 'cohorts': expected_forms}
    expected_validation = {'schemaVersion': 1, 'testId': TEST_ID,
                           'manifestSha256': SOURCE_PINS[MANIFEST_REL], 'cohorts': expected_validation}
    actual_forms, forms_bytes = read_json(forms_path, CAP_PRIVATE)
    actual_validation, validation_bytes = read_json(validation_path, CAP_PRIVATE)
    require(canonical(actual_forms) == canonical(expected_forms), 'complete-original-streams-and-form-text-mismatch')
    require(canonical(actual_validation) == canonical(expected_validation), 'complete-private-validation-mismatch')
    # Equality above includes all complete strings; encoded JSON string values
    # must also preserve exact UTF8, including hard separators and punctuation.
    for actual, expected in zip(actual_forms['cohorts'], expected_forms['cohorts']):
        require(all(a.encode('utf-8') == b.encode('utf-8') for a, b in zip(actual['forms'], expected['forms'])),
                'complete-form-UTF8-mismatch')
    result, result_bytes = read_json(result_path)
    top = {'version', 'testId', 'batchId', 'status', 'startedAtUTC', 'completedAtUTC',
           'registrationCommit', 'protocolSha256', 'sourceHashes', 'scriptHashes', 'manifestSha256',
           'scopeComplete', 'supplementalGatesComplete', 'selectorRegenerated', 'semanticReviewPerformed',
           'privateReviewRequired', 'cohorts', 'totals', 'privateArtifactIntegrity', 'activity', 'limitations'}
    require(set(result) == top and result.get('version') == 1 and result.get('testId') == TEST_ID and
            result.get('batchId') == BATCH_ID and result.get('status') == 'supplemental-fixed-artifact-scope-complete',
            'safe-result-identity-or-allowlist-mismatch')
    require(result.get('registrationCommit') == args.registration_commit and
            result.get('protocolSha256') == protocol_sha and result.get('sourceHashes') == protocol['sourceHashes'] and
            result.get('scriptHashes') == protocol['scriptHashes'] and result.get('manifestSha256') == SOURCE_PINS[MANIFEST_REL],
            'safe-result-provenance-mismatch')
    require(result.get('scopeComplete') is True and result.get('supplementalGatesComplete') is True and
            result.get('selectorRegenerated') is False and result.get('semanticReviewPerformed') is False,
            'safe-result-completion-mismatch')
    require(canonical(result.get('cohorts')) == canonical(safe) and
            canonical(result.get('totals')) == canonical(safe_totals(safe)), 'safe-result-count-mismatch')
    review_required = any(row['common4']['privateReviewRequired'] or row['minikey26']['privateReviewRequired']
                          for row in expected_validation['cohorts'])
    require(result.get('privateReviewRequired') is review_required, 'safe-result-lead-flag-mismatch')
    artifact_pins = {'FORMS.private.json': sha(forms_bytes), 'VALIDATION.private.json': sha(validation_bytes)}
    require(result.get('privateArtifactIntegrity') == artifact_pins, 'private-artifact-integrity-mismatch')
    require(canonical(result.get('activity')) == canonical(EXPECTED_ACTIVITY), 'safe-result-activity-mismatch')
    require(result.get('limitations') == EXPECTED_TEST['limitations'], 'safe-result-limitations-mismatch')
    try:
        begin = datetime.fromisoformat(result['startedAtUTC'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(result['completedAtUTC'].replace('Z', '+00:00'))
        require(begin.tzinfo is not None and end.tzinfo is not None and begin <= end, 'safe-result-time-order-mismatch')
    except (TypeError, ValueError, KeyError):
        raise GuardError('safe-result-time-format-mismatch') from None
    receipt = {'version': 1, 'testId': TEST_ID, 'status': 'PASS', 'passed': True, 'completedAtUTC': now(),
               'registrationCommit': args.registration_commit, 'protocolSha256': protocol_sha,
               'manifestSha256': SOURCE_PINS[MANIFEST_REL], 'primaryResultSha256': sha(result_bytes),
               'privateArtifactIntegrity': artifact_pins,
               'comparisons': {'cohorts': 7, 'savedLabeledRecords': 2594, 'perCohortFormsSum': 2576,
                               'fullOriginalStreamObjectsAndOrder': True, 'completeFormsAndUTF8': True,
                               'rawShapePositiveAndFingerprintMetadata': True, 'safePerCohortAndTotalCounts': True,
                               'independentMini26EnumerationCohorts': 6, 'G03RecordedPrefixImplicationOnly': True},
               'scope': 'Independentform reconstruction and mini26enumeration; fourformat shape/validation routines deliberately shared.',
               'semanticReviewPerformed': False, 'scalarDerivations': 0, 'addressDerivations': 0,
               'networkQueries': 0, 'publicEdits': 0}
    output.mkdir(mode=0o700)
    write_private(output / 'VERIFICATION.json', receipt)
    return receipt

def self_test():
    result = core_self_test()
    rejected = result['rejectionControls']
    validate_test(EXPECTED_TEST)
    for key in ['id', 'inputPaths', 'implementationPaths', 'sourceExpectations', 'fixedWitnessHashes',
                'forms', 'literalValidation', 'registrationGate', 'caps', 'outputPolicy', 'activityBoundary']:
        bad = json.loads(json.dumps(EXPECTED_TEST))
        bad[key] = None
        try:
            validate_test(bad)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-protocol-mutation-accepted')
    for protocol, commit in [('/synthetic/wrong-protocol', 'not-a-commit'),
                             ('/synthetic/wrong-protocol', '0' * 40)]:
        try:
            registered_pins(protocol, commit)
        except GuardError:
            rejected += 1
        else:
            raise GuardError('synthetic-invalid-registration-gate-accepted')
    original_run = subprocess.run
    class MockGitResult:
        def __init__(self, status, output):
            self.returncode, self.stdout = status, output
    try:
        subprocess.run = lambda *args, **kwargs: MockGitResult(0, b'commit\n')
        verify_commit_object(Path('/synthetic'), '1' * 40)
        for status, output in [(0, b'tag\n'), (0, b'tree\n'), (0, b'blob\n'), (0, b''), (1, b'commit\n')]:
            subprocess.run = lambda *args, _status=status, _output=output, **kwargs: MockGitResult(_status, _output)
            try:
                verify_commit_object(Path('/synthetic'), '1' * 40)
            except GuardError:
                rejected += 1
            else:
                raise GuardError('synthetic-noncommit-registration-accepted')
    finally:
        subprocess.run = original_run
    mocks = synthetic_source_cohorts()
    manifest_rows = []
    for index, name in enumerate(COHORTS):
        metadata = COHORT_METADATA[name]
        manifest_rows.append({'testId': name, 'labeledStreamCount': metadata['records'],
                              'uniqueStreamCountReported': metadata['uniqueTexts'],
                              'uniqueFormCountReported': metadata['forms'],
                              'publicArtifactSha256': metadata['streamsSha256'],
                              'safeResultSha256': metadata['resultSha256'],
                              'independentCheckSha256': metadata['checkSha256'],
                              'legacyMinikeyShapeOccurrences': [21, 38, 16, 1, 6, 12, 0][index],
                              'logicalMinikey26ShapeExclusionFromZero22Prefix': name == 'G03'})
    manifest = {'version': 1, 'cohorts': manifest_rows}
    metadata = manifest_cohorts(manifest)
    common = load_common()
    scanner = independent_mini26
    calls = []
    def counting_scanner(forms):
        require(not any('Synthetic-G03-' in text for text in forms), 'synthetic-G03-direct-scan-forbidden')
        calls.append(1)
        return scanner(forms)
    globals()['independent_mini26'] = counting_scanner
    summaries = []
    try:
        for name in COHORTS:
            n = COHORT_METADATA[name]
            streams = mocks[name]
            streams[0]['syntheticOptionalField'] = {'preserve': True, 'array': [1, 2]}
            raw = streams if name == 'G03' else {'streams': streams, 'syntheticParentField': True}
            original = source_streams(raw, name)
            shapes = {'wif': 0, 'minikey': metadata[name]['legacyMinikeyShapeOccurrences'], 'hex64': 0, 'bip39': 0}
            old_result = {'testId': name, 'completeNegative': True,
                          'evaluation': {'streamCount': n['records'], 'uniqueStreamCount': n['uniqueTexts'],
                                         'uniqueFormCount': n['forms'], 'formats': ['wif', 'minikey', 'hex64', 'bip39'],
                                         'shapeCounts': shapes, 'validCounts': {kind: 0 for kind in shapes}}}
            old_check = {'testId': name, 'passed': True, 'streamCount': n['records'],
                         'uniqueFormCount': n['forms'], 'shapeCounts': shapes, 'validRecords': 0, 'networkQueries': 0}
            legacy_witnesses(name, old_result, old_check, metadata[name])
            forms, validation = evaluate_cohort(name, original, metadata[name], common)
            require(forms['streams'] is streams and forms['streams'][0]['syntheticOptionalField']['preserve'] is True,
                    'synthetic-original-object-and-optional-field-preservation')
            summaries.append(safe_cohort(forms, validation))
            if name == 'G03':
                require(validation['minikey26']['enumerated'] is False and
                        validation['minikey26']['checksumCalls'] == 0 and
                        validation['minikey26Shapes'] == [] and validation['minikey26Positives'] == [],
                        'synthetic-G03-zero-prefix-only-contract')
                for mutation in ['result-shapes', 'result-negative', 'check-passed', 'check-count', 'check-network', 'manifest-prefix']:
                    r, c, m = json.loads(json.dumps(old_result)), json.loads(json.dumps(old_check)), dict(metadata[name])
                    if mutation == 'result-shapes': r['evaluation']['shapeCounts']['minikey'] = 1
                    elif mutation == 'result-negative': r['completeNegative'] = False
                    elif mutation == 'check-passed': c['passed'] = False
                    elif mutation == 'check-count': c['streamCount'] += 1
                    elif mutation == 'check-network': c['networkQueries'] = 1
                    else: m['logicalMinikey26ShapeExclusionFromZero22Prefix'] = False
                    try:
                        legacy_witnesses(name, r, c, m)
                    except GuardError:
                        rejected += 1
                    else:
                        raise GuardError('synthetic-G03-invalid-prefix-witness-accepted')
    finally:
        globals()['independent_mini26'] = scanner
    require(len(calls) == 6 and safe_totals(summaries)['labeledStreams'] == 2594 and
            safe_totals(summaries)['sumPerCohortUniqueForms'] == 2576, 'synthetic-all-cohort-aggregate-and-G03-skip')
    controls = json.loads((common_path().parent / 'batch20_support/controls.json').read_text())
    aliases = [controls['segwit_v0'], controls['segwit_v0'].upper()]
    summary, _, positives = evaluate_common4(aliases, common)
    address_aliases = [record for record in positives if record['format'] == 'address' and record['value'] in aliases]
    require(len(address_aliases) == 2 and summary['validCounts']['address'] == 1 and
            address_aliases[0]['fingerprint'] == address_aliases[1]['fingerprint'],
            'synthetic-raw-address-alias-versus-canonical-valid-count')
    summary, _, positives = evaluate_common4([controls['sec_compressed_generator'], controls['sec_uncompressed_generator']], common)
    require(len([record for record in positives if record['format'] == 'sec_public']) == 2 and
            summary['validCounts']['sec_public'] == 1, 'synthetic-raw-SEC-alias-versus-canonical-valid-count')
    previous = CAP_OCCURRENCES
    globals()['CAP_OCCURRENCES'] = 2
    try:
        independent_mini26(['S' * 29])
    except GuardError:
        rejected += 1
    else:
        raise GuardError('synthetic-mini26-occurrence-cap-accepted')
    finally:
        globals()['CAP_OCCURRENCES'] = previous
    previous = CAP_UNIQUE_SHAPES
    globals()['CAP_UNIQUE_SHAPES'] = 1
    try:
        independent_mini26(['S' + '2' * 25, 'S' + '3' * 25])
    except GuardError:
        rejected += 1
    else:
        raise GuardError('synthetic-mini26-unique-cap-accepted')
    finally:
        globals()['CAP_UNIQUE_SHAPES'] = previous
    require(canonical({**EXPECTED_ACTIVITY, 'networkQueries': False}) != canonical(EXPECTED_ACTIVITY),
            'synthetic-strict-typed-activity-control')
    result.update({'status': 'PASS', 'rejectionControls': rejected, 'allSevenCohortMockRun': True,
                   'mini26MockCohortsEnumerated': 6, 'G03Mini26MockEnumerations': 0,
                   'canonicalAliasControls': ['Bech32-case', 'SEC-encoding'],
                   'scalarDerivations': 0, 'addressDerivations': 0})
    return result


def main():
    seen = set()
    for value in sys.argv[1:]:
        if value.startswith('--'):
            key = value.split('=', 1)[0]
            require(key not in seen, 'duplicate-command-argument')
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
        response = {'testId': TEST_ID, 'sourcePaths': list(SOURCE_PINS), 'sourcePins': SOURCE_PINS,
                    'scriptPaths': [PRIMARY_REL, SELF_REL, COMMON_REL], 'protocolPath': PROTOCOL_REL,
                    'cohortMetadata': COHORT_METADATA, 'sharedFormats': COMMON4,
                    'mini26DirectCohorts': COHORTS[:-1], 'G03PrefixImplicationOnly': True,
                    'primaryImports': 0}
    elif args.self_test:
        response = self_test()
    else:
        require(all(getattr(args, key) for key in ['protocol', 'registration_commit', 'result', 'forms', 'validation', 'out']),
                'verify-required-arguments-missing')
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
