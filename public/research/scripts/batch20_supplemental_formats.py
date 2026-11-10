#!/usr/bin/env python3
"""Fixed saved-artifact supplemental literal gates, offline. Python3.10+ stdlib.

--self-test opens only pinned common code and published support controls.
--run requires the fixed public script/protocol in an actual local Git checkout
with the supplied registration object. Prior remote publication is separate.
Raw output must be fresh, outside the entire site checkout, with0700parent.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,importlib.util,json,os,re,stat,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve()
ROOT=HERE.parent.parent if (HERE.parent/'batch20_common.py').is_file() else HERE.parents[3]/'site/public/research'
ROOT=ROOT.resolve()
COMMON='scripts/batch20_common.py'
ENGLISH='scripts/batch20_support/english.txt'
CONTROLS='scripts/batch20_support/controls.json'
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
LEGACY_FORMATS=('wif','minikey','hex64','bip39')
TEST_ID='batch20-supplemental-fixed-formats'
BATCH_ID='keiser-batch20-supplemental-fixed-formats-20261110'
MANIFEST='analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json'
MANIFEST_SHA='18c24b63f78a135f0cb43b380451184532fe443af4c118f2e71d2c638efc5b35'
PROTOCOL='analysis_outputs/continuation_20261110/batch20_supplemental/PROTOCOL.json'
INPUTS=('analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T01/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T01/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T02/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T02/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T02/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T03/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T03/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T04/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T04/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T04/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T05/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T05/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T05/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T06/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T06/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T06/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/G03/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/G03/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/G03/INDEPENDENT_CHECK.json', 'scripts/batch20_support/controls.json', 'scripts/batch20_support/english.txt', 'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json')
SOURCE_PINS={'analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json': '2900473b467c74c18ee29f841f0fbb150376ffa42ab8e9862d9d0957fce8b395', 'analysis_outputs/continuation_20261110/batch20/T01/RESULT.json': 'f96c512124f8ab5314db28fe28627f6217d84a166f880c547c017b6f1acf386c', 'analysis_outputs/continuation_20261110/batch20/T01/INDEPENDENT_CHECK.json': 'c635f12fdf2ae8a22db366748cd38653259e446a59c23359608054ec899ba4e9', 'analysis_outputs/continuation_20261110/batch20/T02/STREAMS.json': 'b417af72e5cbacd69e928f561e811a71fee3e2ce2e68c0d29527a24863301e77', 'analysis_outputs/continuation_20261110/batch20/T02/RESULT.json': '40a4cd340eec86befea09a2636ff9d31a42c726db2933a2a24656c521d0bd93a', 'analysis_outputs/continuation_20261110/batch20/T02/INDEPENDENT_CHECK.json': 'e72a074973f060255fe9fe549d8bd097a2fe135954d624295d5a3c9b9192967e', 'analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json': '8977b65a1f14ddb36b97e05e58df145519f36f56ad18bf30957b328ec8d6c90f', 'analysis_outputs/continuation_20261110/batch20/T03/RESULT.json': '7322a06a7ee5218d6d49de9a4b840633d98fa3589bf004ca9d81401e94575ab6', 'analysis_outputs/continuation_20261110/batch20/T03/INDEPENDENT_CHECK.json': '4ef1781f09a6d8eec238250409994e5cb467e0ddf41867aff7a60e35d8f8d35b', 'analysis_outputs/continuation_20261110/batch20/T04/STREAMS.json': '9cb31c843434c66b640f7b31c96e308f10fe97f885880a115aac8b0eb7918958', 'analysis_outputs/continuation_20261110/batch20/T04/RESULT.json': '6884aeef447a581678172251db0f8db91bc6128339553b37e43409930d31dfcd', 'analysis_outputs/continuation_20261110/batch20/T04/INDEPENDENT_CHECK.json': 'e008d8d3f7d588a4da4c00dad1cd0d3e94fd2c65fcfa4e9325af3d0e620f4f46', 'analysis_outputs/continuation_20261110/batch20/T05/STREAMS.json': '5039524f203d542fa4d072185cd299e4703f5e3b559a1da322cfbf1fa3e86fad', 'analysis_outputs/continuation_20261110/batch20/T05/RESULT.json': 'dbe4ca0d3b0fcfe1d35dd0a7480828b9764f6e91da3c78235bcf69891d95346d', 'analysis_outputs/continuation_20261110/batch20/T05/INDEPENDENT_CHECK.json': 'd131b5081e559bdfe5073888159d9ebba8d0e7167017137b3b8aa21383edbccc', 'analysis_outputs/continuation_20261110/batch20/T06/STREAMS.json': '5f377eef671eac7a3211c4581fd74c68dbb9695e77113db9153b176059f965cf', 'analysis_outputs/continuation_20261110/batch20/T06/RESULT.json': '46c2a6391d344bfbbd6f049d212a5d882a303f2b1b65c390960cee51d046e07e', 'analysis_outputs/continuation_20261110/batch20/T06/INDEPENDENT_CHECK.json': '635798d6590d9deef9cec7a4f43f9a11e88ba6b49c99391100277e3dd0dd0561', 'analysis_outputs/continuation_20261110/batch20/G03/STREAMS.json': 'd2880ebef4d78bcc95d9d6d143ef29a1b9d1a4ac3540cafae821d7ddbb942211', 'analysis_outputs/continuation_20261110/batch20/G03/RESULT.json': '1dd11d9068514514d1812b34925d4da2fa005872f19d01edae55a4a1069385a2', 'analysis_outputs/continuation_20261110/batch20/G03/INDEPENDENT_CHECK.json': 'acfbdd79451b6a2443e325f1f35a0d78223adf62f1e9bbce1bae13ae9bd9422d', 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b', 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda', 'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json': '18c24b63f78a135f0cb43b380451184532fe443af4c118f2e71d2c638efc5b35'}
SCRIPTS=('scripts/batch20_supplemental_formats.py', 'scripts/verify_batch20_supplemental.py', 'scripts/batch20_common.py')
COMMON_SHA='48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'
FORMATS=('extended_private', 'bip38', 'address', 'sec_public')
COHORT_ORDER=('T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'G03')
EXPECTATIONS={'T01': {'testId': 'T01', 'streamCount': 196, 'uniqueStreamCount': 152, 'uniqueFormCount': 236, 'legacyMinikeyShapeOccurrences': 21}, 'T02': {'testId': 'T02', 'streamCount': 628, 'uniqueStreamCount': 628, 'uniqueFormCount': 1120, 'legacyMinikeyShapeOccurrences': 38}, 'T03': {'testId': 'T03', 'streamCount': 120, 'uniqueStreamCount': 120, 'uniqueFormCount': 168, 'legacyMinikeyShapeOccurrences': 16}, 'T04': {'testId': 'T04', 'streamCount': 252, 'uniqueStreamCount': 244, 'uniqueFormCount': 316, 'legacyMinikeyShapeOccurrences': 1}, 'T05': {'testId': 'T05', 'streamCount': 42, 'uniqueStreamCount': 42, 'uniqueFormCount': 54, 'legacyMinikeyShapeOccurrences': 6}, 'T06': {'testId': 'T06', 'streamCount': 60, 'uniqueStreamCount': 58, 'uniqueFormCount': 66, 'legacyMinikeyShapeOccurrences': 12}, 'G03': {'testId': 'G03', 'streamCount': 1296, 'uniqueStreamCount': 615, 'uniqueFormCount': 616, 'legacyMinikeyShapeOccurrences': 0}}
CAPS={'sourceJsonBytes': 2000000, 'registeredBlobBytes': 20000000, 'protocolBytes': 1000000, 'privateArtifactBytes': 20000000, 'streamCodepoints': 100000, 'totalSourceCodepoints': 2000000, 'totalFormCodepoints': 4000000, 'shapeOccurrencesPerCohort': 1000000, 'uniqueShapesPerCohort': 500000}
DEFINITION={'id': 'batch20-supplemental-fixed-formats', 'title': 'Supplemental literal formats on seven unchanged frozen batch20 artifacts', 'family': 'fixed-artifact-format-compatibility', 'branchId': 'text-lines', 'inputPaths': ['analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T01/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T01/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T02/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T02/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T02/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T03/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T03/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T04/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T04/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T04/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T05/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T05/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T05/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/T06/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/T06/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/T06/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/batch20/G03/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/G03/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/G03/INDEPENDENT_CHECK.json', 'scripts/batch20_support/controls.json', 'scripts/batch20_support/english.txt', 'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json'], 'implementationPaths': ['scripts/batch20_supplemental_formats.py', 'scripts/verify_batch20_supplemental.py', 'scripts/batch20_common.py'], 'protocolPath': 'analysis_outputs/continuation_20261110/batch20_supplemental/PROTOCOL.json', 'manifest': {'path': 'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json', 'sha256': '18c24b63f78a135f0cb43b380451184532fe443af4c118f2e71d2c638efc5b35'}, 'cohortOrder': ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'G03'], 'sourceExpectations': [{'testId': 'T01', 'streamCount': 196, 'uniqueStreamCount': 152, 'uniqueFormCount': 236, 'legacyMinikeyShapeOccurrences': 21}, {'testId': 'T02', 'streamCount': 628, 'uniqueStreamCount': 628, 'uniqueFormCount': 1120, 'legacyMinikeyShapeOccurrences': 38}, {'testId': 'T03', 'streamCount': 120, 'uniqueStreamCount': 120, 'uniqueFormCount': 168, 'legacyMinikeyShapeOccurrences': 16}, {'testId': 'T04', 'streamCount': 252, 'uniqueStreamCount': 244, 'uniqueFormCount': 316, 'legacyMinikeyShapeOccurrences': 1}, {'testId': 'T05', 'streamCount': 42, 'uniqueStreamCount': 42, 'uniqueFormCount': 54, 'legacyMinikeyShapeOccurrences': 6}, {'testId': 'T06', 'streamCount': 60, 'uniqueStreamCount': 58, 'uniqueFormCount': 66, 'legacyMinikeyShapeOccurrences': 12}, {'testId': 'G03', 'streamCount': 1296, 'uniqueStreamCount': 615, 'uniqueFormCount': 616, 'legacyMinikeyShapeOccurrences': 0}], 'fixedWitnessHashes': {'analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json': '2900473b467c74c18ee29f841f0fbb150376ffa42ab8e9862d9d0957fce8b395', 'analysis_outputs/continuation_20261110/batch20/T01/RESULT.json': 'f96c512124f8ab5314db28fe28627f6217d84a166f880c547c017b6f1acf386c', 'analysis_outputs/continuation_20261110/batch20/T01/INDEPENDENT_CHECK.json': 'c635f12fdf2ae8a22db366748cd38653259e446a59c23359608054ec899ba4e9', 'analysis_outputs/continuation_20261110/batch20/T02/STREAMS.json': 'b417af72e5cbacd69e928f561e811a71fee3e2ce2e68c0d29527a24863301e77', 'analysis_outputs/continuation_20261110/batch20/T02/RESULT.json': '40a4cd340eec86befea09a2636ff9d31a42c726db2933a2a24656c521d0bd93a', 'analysis_outputs/continuation_20261110/batch20/T02/INDEPENDENT_CHECK.json': 'e72a074973f060255fe9fe549d8bd097a2fe135954d624295d5a3c9b9192967e', 'analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json': '8977b65a1f14ddb36b97e05e58df145519f36f56ad18bf30957b328ec8d6c90f', 'analysis_outputs/continuation_20261110/batch20/T03/RESULT.json': '7322a06a7ee5218d6d49de9a4b840633d98fa3589bf004ca9d81401e94575ab6', 'analysis_outputs/continuation_20261110/batch20/T03/INDEPENDENT_CHECK.json': '4ef1781f09a6d8eec238250409994e5cb467e0ddf41867aff7a60e35d8f8d35b', 'analysis_outputs/continuation_20261110/batch20/T04/STREAMS.json': '9cb31c843434c66b640f7b31c96e308f10fe97f885880a115aac8b0eb7918958', 'analysis_outputs/continuation_20261110/batch20/T04/RESULT.json': '6884aeef447a581678172251db0f8db91bc6128339553b37e43409930d31dfcd', 'analysis_outputs/continuation_20261110/batch20/T04/INDEPENDENT_CHECK.json': 'e008d8d3f7d588a4da4c00dad1cd0d3e94fd2c65fcfa4e9325af3d0e620f4f46', 'analysis_outputs/continuation_20261110/batch20/T05/STREAMS.json': '5039524f203d542fa4d072185cd299e4703f5e3b559a1da322cfbf1fa3e86fad', 'analysis_outputs/continuation_20261110/batch20/T05/RESULT.json': 'dbe4ca0d3b0fcfe1d35dd0a7480828b9764f6e91da3c78235bcf69891d95346d', 'analysis_outputs/continuation_20261110/batch20/T05/INDEPENDENT_CHECK.json': 'd131b5081e559bdfe5073888159d9ebba8d0e7167017137b3b8aa21383edbccc', 'analysis_outputs/continuation_20261110/batch20/T06/STREAMS.json': '5f377eef671eac7a3211c4581fd74c68dbb9695e77113db9153b176059f965cf', 'analysis_outputs/continuation_20261110/batch20/T06/RESULT.json': '46c2a6391d344bfbbd6f049d212a5d882a303f2b1b65c390960cee51d046e07e', 'analysis_outputs/continuation_20261110/batch20/T06/INDEPENDENT_CHECK.json': '635798d6590d9deef9cec7a4f43f9a11e88ba6b49c99391100277e3dd0dd0561', 'analysis_outputs/continuation_20261110/batch20/G03/STREAMS.json': 'd2880ebef4d78bcc95d9d6d143ef29a1b9d1a4ac3540cafae821d7ddbb942211', 'analysis_outputs/continuation_20261110/batch20/G03/RESULT.json': '1dd11d9068514514d1812b34925d4da2fa005872f19d01edae55a4a1069385a2', 'analysis_outputs/continuation_20261110/batch20/G03/INDEPENDENT_CHECK.json': 'acfbdd79451b6a2443e325f1f35a0d78223adf62f1e9bbce1bae13ae9bd9422d', 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b', 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda', 'analysis_outputs/continuation_20261110/batch20_supplemental/MANIFEST.json': '18c24b63f78a135f0cb43b380451184532fe443af4c118f2e71d2c638efc5b35'}, 'forms': {'rule': 'Per cohort: unique exact text union Unicode-whitespace-only compaction via re.sub(r"\\s", "", text), deduplicated/sorted by Python string order. Empty strings retained. No cross-cohort dedup.', 'selectorRegeneration': False, 'perCohortCountsRequired': True}, 'literalValidation': {'commonFormats': ['extended_private', 'bip38', 'address', 'sec_public'], 'commonImplementationUnchanged': True, 'commonSha256': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d', 'oldMinikeyCheckerCalled': False, 'uniqueRawValuesValidatedOncePerFormatPerCohort': True, 'validCountsDeduplicateCanonicalFingerprints': True, 'minikey26': {'cohorts': ['T01', 'T02', 'T03', 'T04', 'T05', 'T06'], 'length': 26, 'shape': 'Every overlapping embedded exact26 S-prefixed Base58 window, no outer boundaries.', 'checksum': 'SHA256(ASCII(value + question mark))[0]==0; weak8bit check only.', 'fingerprint': 'Existing batch20 domain-separated record fingerprint on ASCII value, private only.', 'G03': 'No enumeration/checksum: same frozen forms plus saved zero legacy22/30 shape counter and independent check imply zero26 shapes by22-prefix inclusion.', 'scalarHash': False}}, 'registrationGate': 'Public executing path; full40hex local Git registration object; fixed protocol and all24source/3code current bytes must equal registered blobs before target JSON parsing. Remote publication established separately by operator.', 'caps': {'sourceJsonBytes': 2000000, 'registeredBlobBytes': 20000000, 'protocolBytes': 1000000, 'privateArtifactBytes': 20000000, 'streamCodepoints': 100000, 'totalSourceCodepoints': 2000000, 'totalFormCodepoints': 4000000, 'shapeOccurrencesPerCohort': 1000000, 'uniqueShapesPerCohort': 500000}, 'outputPolicy': {'rawArtifacts': ['FORMS.private.json', 'VALIDATION.private.json'], 'rawOutsideEntireSiteCheckout': True, 'directoryMode': '0700', 'fileMode': '0600', 'publicReceipt': 'Aggregate per-cohort/total counts, scope and whole-artifact integrity only; no values, fingerprints, addresses, SEC text or hit locators.', 'semanticConclusionComputed': False}, 'activityBoundary': {'selectorRegenerations': 0, 'newTransformsBeyondExistingForms': 0, 'oldSharedMinikeyCalls': 0, 'G03Minikey26Enumerations': 0, 'G03Minikey26ChecksumCalls': 0, 'minikeyScalarHashes': 0, 'proseToKeyHashes': 0, 'scalarDerivations': 0, 'addressDerivations': 0, 'seedDerivations': 0, 'childKeyDerivations': 0, 'networkQueries': 0, 'transactions': 0}, 'limitations': ['This supplements record-format gates on seven exact saved artifacts; it does not regenerate, extend or validate their source selectors.', 'The four shared validators are unchanged; shape and validation logic for those four formats is shared, not an independent implementation.', 'SEC on-curve matches and weak8bit minikey checks are leads only; BIP38 is structure/checksum validation, not decryption.', 'No semantic recognition, physical geometry conclusion, prize authentication, funding check or whole-puzzle exclusion is computed.', 'G03 minikey26 coverage is a recorded zero22-shape prefix implication on identical forms, not a new26 enumeration.']}
MAX_REGISTERED_BLOB_BYTES=20000000

def require(condition, message):
    if not condition:
        raise ValueError(message)

def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')

def digest(data):
    """File and UTF-8 output-integrity identifiers, never candidate/key hashes."""
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=True, allow_nan=False)

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field')
        result[key] = value
    return result

def load_json(raw):
    def no_constant(value):
        raise ValueError('Nonfinite JSON constant')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object, parse_constant=no_constant)

def code_definition():
    return deepcopy(DEFINITION)

def capped_read(path, limit):
    require(path.is_file() and path.stat().st_size <= limit, 'File byte cap exceeded')
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, 'File grew beyond byte cap')
    return raw

def registered_blob(registration, relative):
    require(relative in INPUTS+SCRIPTS+(PROTOCOL,), 'Unregistered blob path')
    obj=registration+':public/research/'+relative
    size=subprocess.run(['git','cat-file','-s',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(size.returncode==0 and len(size.stdout)<=20 and re.fullmatch(rb'[0-9]+\n',size.stdout), 'Registration blob missing')
    n=int(size.stdout)
    require(n<=MAX_REGISTERED_BLOB_BYTES, 'Registered blob cap exceeded')
    data=subprocess.run(['git','cat-file','blob',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(data.returncode==0 and len(data.stdout)==n, 'Registration blob unavailable')
    return data.stdout

def verify_payloads(protocol, protocol_bytes, registration, current_reader, blob_reader):
    # Registration of the protocol itself is checked before target file opens.
    require(blob_reader(registration,PROTOCOL)==protocol_bytes, 'Protocol registration bytes differ')
    contents={}
    for field,paths in (('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)):
        for relative in paths:
            registered=blob_reader(registration,relative)
            require(len(registered)<=MAX_REGISTERED_BLOB_BYTES, 'Registered content cap exceeded')
            require(digest(registered)==protocol[field][relative], 'Registered file pin differs')
            current=current_reader(relative)
            require(current==registered, 'Current and registered bytes differ')
            contents[relative]=current
    return contents

def json_bytes(value):
    return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')

def private_output(value):
    raw=Path(value).expanduser();require(not raw.exists() and not raw.is_symlink(),'Fresh private output required')
    out=raw.resolve();require(not any(p.casefold()=='public' for p in out.parts) and not out.is_relative_to(ROOT.parent.parent),'Output outside entire site checkout required')
    require(out.parent.is_dir() and stat.S_IMODE(out.parent.stat().st_mode)==0o700,'Private0700 output parent required')
    return out

def private_write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.fchmod(fd,0o600)
    with os.fdopen(fd,'wb') as handle:handle.write(raw)

def load_common():
    require(digest(capped_read(ROOT/COMMON,CAPS['sourceJsonBytes']))==COMMON_SHA,'Common byte pin changed')
    for relative in (ENGLISH,CONTROLS):
        require(digest(capped_read(ROOT/relative,CAPS['sourceJsonBytes']))==SOURCE_PINS[relative],'Support byte pin changed')
    spec=importlib.util.spec_from_file_location('supplemental_shared_common',ROOT/COMMON)
    common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
    require(tuple(common.ALL_FORMATS[-4:])==FORMATS,'Shared format population changed')
    return common


def validate_protocol_header(protocol,registration):
    require(isinstance(registration,str) and re.fullmatch('[0-9a-f]{40}',registration),'Full registration commit required')
    require(isinstance(protocol,dict) and {'version','batchId','test','sourceHashes','scriptHashes'}<=set(protocol),'Protocol schema changed')
    require(type(protocol['version']) is int and protocol['version']==1 and protocol['batchId']==BATCH_ID,'Protocol identity changed')
    require(canonical(protocol['test'])==canonical(DEFINITION),'Protocol code definition changed')
    for field,paths in [('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)]:
        require(isinstance(protocol[field],dict) and set(protocol[field])==set(paths),'Protocol pin population changed')
        require(all(isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) for v in protocol[field].values()),'Protocol pin invalid')
    require(protocol['sourceHashes']==SOURCE_PINS,'Exact frozen witness pins required')
    require(protocol['scriptHashes'][COMMON]==COMMON_SHA,'Common code pin changed')
    if 'registeredAtUTC' in protocol:
        parsed=datetime.fromisoformat(protocol['registeredAtUTC'].replace('Z','+00:00'))
        require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds()==0,'Registration metadata must be UTC')


def validate_protocol(path,registration):
    require(HERE==(ROOT/SCRIPTS[0]).resolve(),'Actual run requires fixed public implementation path')
    path=Path(path).expanduser().resolve(strict=True)
    require(path==(ROOT/PROTOCOL).resolve() and path.is_relative_to(ROOT),'Fixed public protocol required')
    raw=capped_read(path,CAPS['protocolBytes']);protocol=load_json(raw);validate_protocol_header(protocol,registration)
    kind=subprocess.run(['git','cat-file','-t',registration],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(kind.returncode==0 and kind.stdout==b'commit\n','Actual Git commit object required')
    def current(relative):
        file=(ROOT/relative).resolve(strict=True)
        require(file.is_relative_to(ROOT),'Research path escape')
        return capped_read(file,CAPS['sourceJsonBytes'] if relative in INPUTS else CAPS['registeredBlobBytes'])
    files=verify_payloads(protocol,raw,registration,current,registered_blob)
    require(files[SCRIPTS[0]]==HERE.read_bytes(),'Executing script differs from registration')
    return protocol,raw,files


def validate_manifest(manifest):
    require(isinstance(manifest,dict) and type(manifest.get('version')) is int and manifest['version']==1,'Manifest schema changed')
    cohorts=manifest.get('cohorts');require(isinstance(cohorts,list) and len(cohorts)==7,'Manifest cohort population changed')
    for cohort,tid in zip(cohorts,COHORT_ORDER):
        expected=EXPECTATIONS[tid]
        require(isinstance(cohort,dict) and cohort.get('testId')==tid,'Manifest order changed')
        for manifest_key,expected_key in [('labeledStreamCount','streamCount'),('uniqueStreamCountReported','uniqueStreamCount'),('uniqueFormCountReported','uniqueFormCount'),('legacyMinikeyShapeOccurrences','legacyMinikeyShapeOccurrences')]:
            require(type(cohort.get(manifest_key)) is int and cohort[manifest_key]==expected[expected_key],'Manifest counts changed')
        stem='analysis_outputs/continuation_20261110/batch20/'+tid+'/'
        require(cohort.get('publicArtifact')==stem+'STREAMS.json' and cohort.get('publicArtifactSha256')==SOURCE_PINS[stem+'STREAMS.json'],'Manifest source identity changed')
        require(cohort.get('safeResultSha256')==SOURCE_PINS[stem+'RESULT.json'] and cohort.get('independentCheckSha256')==SOURCE_PINS[stem+'INDEPENDENT_CHECK.json'],'Manifest witness identity changed')
        require(cohort.get('declaredFormats')==list(LEGACY_FORMATS) and cohort.get('minikeyLengthsFromPinnedCode')==[22,30],'Manifest old gate scope changed')
        require(cohort.get('allDeclaredValidCountsZero') is True and cohort.get('originalAndPublicArtifactByteIdentical') is True,'Manifest old evidence changed')
        require(cohort.get('logicalMinikey26ShapeExclusionFromZero22Prefix') is (tid=='G03'),'Manifest prefix scope changed')
    return {c['testId']:c for c in cohorts}


def validate_saved_source(cohortId,raw,oldResult,oldCheck,manifestCohort):
    expected=EXPECTATIONS[cohortId]
    if cohortId=='G03':
        require(isinstance(raw,list),'G03 saved list required');streams=raw
    else:
        require(isinstance(raw,dict) and set(raw)=={'testId','streams'} and raw.get('testId')==cohortId,'Saved source schema changed')
        streams=raw['streams']
    require(isinstance(streams,list) and len(streams)==expected['streamCount'],'Saved stream population changed')
    for stream in streams:
        require(isinstance(stream,dict) and isinstance(stream.get('id'),str) and isinstance(stream.get('text'),str),'Saved stream record schema changed')
        require(len(stream['id'])<=1000 and len(stream['text'])<=CAPS['streamCodepoints'],'Saved stream length cap exceeded')
        stream['text'].encode('utf-8')
    require(len({s['text'] for s in streams})==expected['uniqueStreamCount'],'Saved unique stream population changed')
    require(isinstance(oldResult,dict) and oldResult.get('testId')==cohortId,'Old result identity changed')
    ev=oldResult.get('evaluation');require(isinstance(ev,dict) and ev.get('formats')==list(LEGACY_FORMATS),'Old result format scope changed')
    for key in ('streamCount','uniqueStreamCount','uniqueFormCount'):
        require(type(ev.get(key)) is int and ev[key]==expected[key],'Old result counts changed')
    require(isinstance(ev.get('shapeCounts'),dict) and set(ev['shapeCounts'])==set(LEGACY_FORMATS),'Old shape counter schema changed')
    require(all(type(n) is int and n>=0 for n in ev['shapeCounts'].values()),'Old shape counter invalid')
    require(ev['shapeCounts']['minikey']==expected['legacyMinikeyShapeOccurrences'],'Old mini shape counter changed')
    require(ev.get('validCounts')==dict.fromkeys(LEGACY_FORMATS,0),'Old valid counter changed')
    require(isinstance(oldCheck,dict) and oldCheck.get('testId')==cohortId and oldCheck.get('passed') is True,'Old independent check changed')
    for key in ('streamCount','uniqueFormCount'):
        require(type(oldCheck.get(key)) is int and oldCheck[key]==expected[key],'Old check counts changed')
    require(oldCheck.get('shapeCounts')==ev['shapeCounts'] and type(oldCheck.get('validRecords')) is int and oldCheck['validRecords']==0 and type(oldCheck.get('networkQueries')) is int and oldCheck['networkQueries']==0,'Old check gate changed')
    require(manifestCohort.get('testId')==cohortId and manifestCohort.get('logicalMinikey26ShapeExclusionFromZero22Prefix') is (cohortId=='G03'),'Manifest witness scope changed')
    return streams


def make_forms(streams):
    require(isinstance(streams,list) and all(isinstance(s,dict) and isinstance(s.get('text'),str) for s in streams),'Form source schema changed')
    texts={s['text'] for s in streams}
    forms=sorted(texts|{re.sub(r'\s','',text) for text in texts})
    require(sum(map(len,forms))<=CAPS['totalFormCodepoints'],'Form codepoint cap exceeded')
    return forms


def evaluate_common4(forms,common):
    counts=dict.fromkeys(FORMATS,0);shapes={kind:set() for kind in FORMATS}
    for text in forms:
        for kind in FORMATS:
            for value in common.shape_values(kind,text):
                counts[kind]+=1;shapes[kind].add(value)
                require(sum(counts.values())<=CAPS['shapeOccurrencesPerCohort'] and sum(map(len,shapes.values()))<=CAPS['uniqueShapesPerCohort'],'Shape population cap exceeded')
    rawShapes={kind:sorted(shapes[kind]) for kind in FORMATS};positives=[];valid={kind:set() for kind in FORMATS}
    for kind in FORMATS:
        for value in rawShapes[kind]:
            checked=common.validate_record(kind,value)
            if checked is not None:
                canonical_bytes,metadata=checked;fp=common.fingerprint(kind,canonical_bytes);valid[kind].add(fp)
                positives.append({'format':kind,'value':value,'fingerprint':fp,'metadata':metadata})
    summary={'formats':list(FORMATS),'shapeCounts':counts,'uniqueShapeCounts':{kind:len(shapes[kind]) for kind in FORMATS},'validationCalls':sum(map(len,shapes.values())),
      'validCounts':{kind:len(valid[kind]) for kind in FORMATS},'privateReviewRequired':bool(positives),'fingerprintRule':deepcopy(common.FINGERPRINT_RULE)}
    return summary,rawShapes,positives


def minikey26_shape(value):
    return isinstance(value,str) and len(value)==26 and value.startswith('S') and all(c in B58 for c in value)


def minikey26_valid(value):
    return minikey26_shape(value) and hashlib.sha256((value+'?').encode('ascii')).digest()[0]==0


def scan_minikey26_forms(forms,common):
    shapes=set();count=0
    pattern=re.compile(r'(?=(S[1-9A-HJ-NP-Za-km-z]{25}))')
    for text in forms:
        for match in pattern.finditer(text):
            count+=1;shapes.add(match.group(1))
            require(count<=CAPS['shapeOccurrencesPerCohort'] and len(shapes)<=CAPS['uniqueShapesPerCohort'],'Mini shape population cap exceeded')
    values=sorted(shapes);positives=[]
    for value in values:
        if minikey26_valid(value):
            positives.append({'format':'minikey','length':26,'checkBits':8,'private':True,'fingerprint':common.fingerprint('minikey',value.encode('ascii')),'value':value})
    summary={'status':'checked','enumerated':True,'length':26,'shapeOccurrences':count,'uniqueShapeCount':len(values),'checksumCalls':len(values),'validCount':len(positives),
      'privateReviewRequired':bool(positives),'fingerprintRule':deepcopy(common.FINGERPRINT_RULE),'proof':None}
    return summary,values,positives


def evaluate_cohort(cohortId,streams,manifestCohort,common):
    forms=make_forms(streams);expected=EXPECTATIONS[cohortId]
    require(len(forms)==expected['uniqueFormCount'],'Frozen unique form population changed')
    common4,rawShapes,rawPositives=evaluate_common4(forms,common)
    if cohortId=='G03':
        require(expected['legacyMinikeyShapeOccurrences']==0 and manifestCohort['logicalMinikey26ShapeExclusionFromZero22Prefix'] is True,'G03 prefix proof unavailable')
        mini={'status':'inferred-no-shapes-from-zero-legacy22','enumerated':False,'length':26,'shapeOccurrences':0,'uniqueShapeCount':0,'checksumCalls':0,'validCount':0,
          'privateReviewRequired':False,'fingerprintRule':deepcopy(common.FINGERPRINT_RULE),'proof':{'legacyMinikeyShapeOccurrences':0,'legacyCheckPassed':True,'legacyCheckValidRecords':0,'prefixLength':22,'extendedLength':26,'outerBoundaryRequired':False,'sameFrozenForms':True}}
        miniShapes=[];miniPositives=[]
    else:mini,miniShapes,miniPositives=scan_minikey26_forms(forms,common)
    forms_record={'testId':cohortId,'sourceArtifactSha256':manifestCohort['publicArtifactSha256'],'streams':streams,'forms':forms}
    validation={'testId':cohortId,'common4':common4,'rawShapeValues':rawShapes,'rawPositives':rawPositives,'minikey26':mini,'minikey26Shapes':miniShapes,'minikey26Positives':miniPositives}
    return forms_record,validation


def safe_result(protocol,pbytes,registration,forms_records,validation,started,integrity):
    cohorts=[]
    for formrec,record in zip(forms_records,validation):
        tid=record['testId'];c=record['common4'];m=record['minikey26']
        cohorts.append({'testId':tid,'streamCount':len(formrec['streams']),'uniqueStreamCount':len({s['text'] for s in formrec['streams']}),'uniqueFormCount':len(formrec['forms']),
          'common4':{key:deepcopy(c[key]) for key in ('formats','shapeCounts','uniqueShapeCounts','validationCalls','validCounts')},
          'minikey26':{key:m[key] for key in ('status','enumerated','shapeOccurrences','uniqueShapeCount','checksumCalls','validCount')}})
    totals={'cohorts':len(cohorts),'labeledStreams':sum(c['streamCount'] for c in cohorts),'sumPerCohortUniqueForms':sum(c['uniqueFormCount'] for c in cohorts),
      'commonShapeCounts':{f:sum(c['common4']['shapeCounts'][f] for c in cohorts) for f in FORMATS},
      'commonUniqueShapeCountsSum':{f:sum(c['common4']['uniqueShapeCounts'][f] for c in cohorts) for f in FORMATS},
      'commonValidationCalls':sum(c['common4']['validationCalls'] for c in cohorts),
      'commonValidCountsSum':{f:sum(c['common4']['validCounts'][f] for c in cohorts) for f in FORMATS},
      'minikey26ShapeOccurrences':sum(c['minikey26']['shapeOccurrences'] for c in cohorts),'minikey26UniqueShapesSum':sum(c['minikey26']['uniqueShapeCount'] for c in cohorts),
      'minikey26ChecksumCalls':sum(c['minikey26']['checksumCalls'] for c in cohorts),'minikey26ValidCountSum':sum(c['minikey26']['validCount'] for c in cohorts)}
    return {'version':1,'testId':TEST_ID,'batchId':BATCH_ID,'status':'supplemental-fixed-artifact-scope-complete','startedAtUTC':started,'completedAtUTC':utc(),
      'registrationCommit':registration,'protocolSha256':digest(pbytes),'sourceHashes':deepcopy(protocol['sourceHashes']),'scriptHashes':deepcopy(protocol['scriptHashes']),'manifestSha256':MANIFEST_SHA,
      'scopeComplete':True,'supplementalGatesComplete':True,'selectorRegenerated':False,'semanticReviewPerformed':False,
      'privateReviewRequired':any(c['common4']['privateReviewRequired'] or c['minikey26']['privateReviewRequired'] for c in validation),
      'cohorts':cohorts,'totals':totals,'privateArtifactIntegrity':integrity,'activity':deepcopy(DEFINITION['activityBoundary']),'limitations':deepcopy(DEFINITION['limitations'])}


def run(protocol_path,registration,out_value):
    started=utc();out=private_output(out_value)
    protocol,pbytes,files=validate_protocol(protocol_path,registration)
    # Only now are any saved target/witness JSON bytes parsed.
    manifest=validate_manifest(load_json(files[MANIFEST]));sources={}
    for tid in COHORT_ORDER:
        stem='analysis_outputs/continuation_20261110/batch20/'+tid+'/'
        sources[tid]=validate_saved_source(tid,load_json(files[stem+'STREAMS.json']),load_json(files[stem+'RESULT.json']),load_json(files[stem+'INDEPENDENT_CHECK.json']),manifest[tid])
    require(sum(len(s['text']) for streams in sources.values() for s in streams)<=CAPS['totalSourceCodepoints'],'Total saved source cap exceeded')
    common=load_common();forms_records=[];validation=[]
    for tid in COHORT_ORDER:
        forms_record,record=evaluate_cohort(tid,sources[tid],manifest[tid],common);forms_records.append(forms_record);validation.append(record)
    require(sum(len(text) for c in forms_records for text in c['forms'])<=CAPS['totalFormCodepoints'],'Total form cap exceeded')
    payloads={'FORMS.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,'manifestSha256':MANIFEST_SHA,'cohorts':forms_records}),
      'VALIDATION.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,'manifestSha256':MANIFEST_SHA,'cohorts':validation})}
    require(all(len(raw)<=CAPS['privateArtifactBytes'] for raw in payloads.values()),'Private artifact byte cap exceeded')
    result=safe_result(protocol,pbytes,registration,forms_records,validation,started,{name:digest(raw) for name,raw in payloads.items()})
    result_bytes=json_bytes(result);out.mkdir(mode=0o700);os.chmod(out,0o700)
    try:
        for name,raw in payloads.items():private_write(out/name,raw)
        private_write(out/'RESULT.json',result_bytes)
    except Exception:
        try:private_write(out/'FAILURE.json',json_bytes({'version':1,'testId':TEST_ID,'scopeComplete':False,'status':'inconclusive-private-write-failure'}))
        except Exception:pass
        raise
    return result
def synthetic_minikey26():
    for counter in range(65536):
        number=counter;suffix=''
        while number:number,remainder=divmod(number,58);suffix=B58[remainder]+suffix
        value='S'+'2'*21+(suffix or '1').rjust(4,'1')
        if minikey26_valid(value):return value
    raise AssertionError('Synthetic checksum control unavailable')


def self_test():
    checks=0
    def reject(call):
        nonlocal checks
        try:call()
        except (ValueError,UnicodeError):checks+=1
        else:raise AssertionError('Expected source-free rejection')
    assert make_forms([{'id':'x','text':' A\tB\nC\u00a0D\u2003E\u2028F '},{'id':'y','text':' A\tB\nC\u00a0D\u2003E\u2028F '},{'id':'z','text':''}])==['',' A\tB\nC\u00a0D\u2003E\u2028F ','ABCDEF'];checks+=1
    assert make_forms([{'text':'A-B/♥\u200b C'},{'text':'A-B/♥\u200b C'}])==['A-B/♥\u200b C','A-B/♥\u200bC'];checks+=1
    assert make_forms([{'text':' '},{'text':''}])==['',' '];checks+=1
    reject(lambda:make_forms([{'text':123}]))
    reject(lambda:load_json(b'{"a":1,"a":2}'));reject(lambda:load_json(b'{"a":NaN}'))
    common=load_common();controls=load_json(capped_read(ROOT/CONTROLS,CAPS['sourceJsonBytes']))
    old_hash=hashlib.sha256;old_shape=common.shape_values;old_validate=common.validate_record
    forbidden={'bareMinikeyHashes':0,'nonSupplementalSharedCalls':0}
    def guarded_hash(data=b'',*args,**kwargs):
        raw=bytes(data)
        if len(raw) in (22,26,30) and raw.startswith(b'S') and all(chr(c) in B58 for c in raw):
            forbidden['bareMinikeyHashes']+=1;raise AssertionError('Bare minikey SHA forbidden')
        return old_hash(data,*args,**kwargs)
    def guarded_shape(kind,*args,**kwargs):
        if kind not in FORMATS:
            forbidden['nonSupplementalSharedCalls']+=1;raise AssertionError('Only added four formats permitted')
        return old_shape(kind,*args,**kwargs)
    def guarded_validate(kind,*args,**kwargs):
        if kind not in FORMATS:
            forbidden['nonSupplementalSharedCalls']+=1;raise AssertionError('Only added four formats permitted')
        return old_validate(kind,*args,**kwargs)
    hashlib.sha256=guarded_hash;common.shape_values=guarded_shape;common.validate_record=guarded_validate
    try:
        fixture_pairs=[('extended_private','bip32_extended_private'),('bip38','bip38_encrypted_private'),('address','legacy_address'),('address','segwit_v0'),('address','segwit_v1'),('sec_public','sec_compressed_generator'),('sec_public','sec_uncompressed_generator')]
        for kind,key in fixture_pairs:
            assert common.validate_record(kind,controls[key]);checks+=1
        control_forms=[controls[key] for _,key in fixture_pairs]
        summary,shapes,positives=evaluate_common4(sorted(set(control_forms)),common)
        assert all(summary['validCounts'][kind]>=1 for kind in FORMATS) and summary['privateReviewRequired'];checks+=1
        assert summary['validationCalls']==sum(summary['uniqueShapeCounts'].values());checks+=1
        assert [p['value'] for p in positives if p['format']=='sec_public']==sorted([controls['sec_compressed_generator'],controls['sec_uncompressed_generator']]);checks+=1
        assert summary['validCounts']['sec_public']==1 and len([p for p in positives if p['format']=='sec_public'])==2;checks+=1
        assert all(shapes[kind]==sorted(set(shapes[kind])) for kind in FORMATS);checks+=1
        for kind,key in fixture_pairs:
            value=controls[key]
            if kind in ('extended_private','bip38','address') and not value.lower().startswith('bc1'):
                broken=value[:-1]+next(c for c in B58 if c!=value[-1] and common.validate_record(kind,value[:-1]+c) is None)
                assert common.validate_record(kind,broken) is None;checks+=1
        mini=synthetic_minikey26();assert len(mini)==26 and minikey26_valid(mini);checks+=1
        one,one_shapes,one_records=scan_minikey26_forms([mini],common)
        assert one['shapeOccurrences']==one['uniqueShapeCount']==one['checksumCalls']==one['validCount']==1 and one_shapes==[mini];checks+=1
        assert one_records==[{'format':'minikey','length':26,'checkBits':8,'private':True,'fingerprint':common.fingerprint('minikey',mini.encode('ascii')),'value':mini}];checks+=1
        for text in ['S'*22,'S'*25,mini[:22],mini[:25],'not-a-shape']:
            s,v,p=scan_minikey26_forms([text],common)
            assert s['shapeOccurrences']==s['uniqueShapeCount']==s['checksumCalls']==s['validCount']==0 and v==p==[];checks+=1
        s,v,p=scan_minikey26_forms(['S'*26],common)
        assert s['shapeOccurrences']==s['uniqueShapeCount']==s['checksumCalls']==1 and v==['S'*26];checks+=1
        s,v,p=scan_minikey26_forms(['S'*27],common)
        assert s['shapeOccurrences']==2 and s['uniqueShapeCount']==s['checksumCalls']==1 and v==['S'*26];checks+=1
        s,v,p=scan_minikey26_forms(['SS'+'1'*25],common)
        assert s['shapeOccurrences']==s['uniqueShapeCount']==s['checksumCalls']==2 and len(v)==2;checks+=1
        s,v,p=scan_minikey26_forms(['!'+mini+'!',mini],common)
        assert s['shapeOccurrences']==2 and s['uniqueShapeCount']==s['checksumCalls']==s['validCount']==1;checks+=1
        for text in [mini+'1',mini[:-1],'s'+mini[1:],'Ｓ'+mini[1:],mini[:4]+'0'+mini[5:],mini[:4]+'O'+mini[5:],mini[:4]+'I'+mini[5:],mini[:4]+'l'+mini[5:]]:
            assert not minikey26_shape(text);checks+=1
        invalid=next(mini[:-1]+c for c in B58 if not minikey26_valid(mini[:-1]+c))
        assert minikey26_shape(invalid) and not minikey26_valid(invalid);checks+=1
        s,v,p=scan_minikey26_forms(['!'+mini+'1!'],common)
        assert s['shapeOccurrences']==1 and v==[mini];checks+=1
        s,v,p=scan_minikey26_forms(make_forms([{'text':mini[:13]+'\u00a0'+mini[13:]}]),common)
        assert s['uniqueShapeCount']==1 and p[0]['value']==mini;checks+=1
    finally:
        hashlib.sha256=old_hash;common.shape_values=old_shape;common.validate_record=old_validate
    return finish_self_test(checks,forbidden,common)


def finish_self_test(checks,forbidden,common):
    def reject(call):
        nonlocal checks
        try:call()
        except (ValueError,UnicodeError):checks+=1
        else:raise AssertionError('Expected source-free rejection')
    # All records/witnesses here are fabricated metadata and strings.
    synthetic_streams=[{'id':'control-'+str(i),'text':'alpha beta','extra':{'preserved':True}} for i in range(EXPECTATIONS['T01']['streamCount'])]
    old_expect=EXPECTATIONS['T01'];EXPECTATIONS['T01']={**old_expect,'uniqueStreamCount':1,'uniqueFormCount':2}
    ev={'streamCount':len(synthetic_streams),'uniqueStreamCount':1,'uniqueFormCount':2,'formats':list(LEGACY_FORMATS),'shapeCounts':dict.fromkeys(LEGACY_FORMATS,0),'validCounts':dict.fromkeys(LEGACY_FORMATS,0)}
    ev['shapeCounts']['minikey']=old_expect['legacyMinikeyShapeOccurrences']
    result={'testId':'T01','evaluation':ev};check={'testId':'T01','passed':True,'streamCount':len(synthetic_streams),'uniqueFormCount':2,'shapeCounts':deepcopy(ev['shapeCounts']),'validRecords':0,'networkQueries':0}
    mc={'testId':'T01','logicalMinikey26ShapeExclusionFromZero22Prefix':False,'publicArtifactSha256':'0'*64}
    source={'testId':'T01','streams':synthetic_streams}
    try:
        assert validate_saved_source('T01',source,result,check,mc) is synthetic_streams;checks+=1
        formrec,validation=evaluate_cohort('T01',synthetic_streams,mc,common)
        assert formrec['streams'] is synthetic_streams and formrec['forms']==['alpha beta','alphabeta'];checks+=1
        for field,value in [('passed',False),('validRecords',1),('networkQueries',1),('testId','T02')]:
            bad=deepcopy(check);bad[field]=value;reject(lambda b=bad:validate_saved_source('T01',source,result,b,mc))
        bad=deepcopy(result);bad['evaluation']['streamCount']-=1;reject(lambda:validate_saved_source('T01',source,bad,check,mc))
        bad=deepcopy(source);bad['streams'][0]['text']=1;reject(lambda:validate_saved_source('T01',bad,result,check,mc))
        bad=deepcopy(source);bad['streams'][0]['text']='x'*(CAPS['streamCodepoints']+1);reject(lambda:validate_saved_source('T01',bad,result,check,mc))
        reject(lambda:evaluate_cohort('T01',[{'id':'bad','text':'other'}],mc,common))
    finally:EXPECTATIONS['T01']=old_expect
    g03_expect=EXPECTATIONS['G03'];EXPECTATIONS['G03']={**g03_expect,'uniqueFormCount':2}
    original_walker=globals()['scan_minikey26_forms']
    def forbidden_g03(*args):raise AssertionError('G03 enumeration forbidden')
    globals()['scan_minikey26_forms']=forbidden_g03
    try:
        gmc={'publicArtifactSha256':'1'*64,'logicalMinikey26ShapeExclusionFromZero22Prefix':True}
        fr,val=evaluate_cohort('G03',[{'id':'control','text':'alpha beta'}],gmc,common)
        assert val['minikey26']['status']=='inferred-no-shapes-from-zero-legacy22' and not val['minikey26']['enumerated'] and val['minikey26Shapes']==val['minikey26Positives']==[];checks+=1
        bad=deepcopy(gmc);bad['logicalMinikey26ShapeExclusionFromZero22Prefix']=False
        reject(lambda:evaluate_cohort('G03',[{'id':'control','text':'alpha beta'}],bad,common))
    finally:
        EXPECTATIONS['G03']=g03_expect;globals()['scan_minikey26_forms']=original_walker
    proto={'version':1,'batchId':BATCH_ID,'test':code_definition(),'sourceHashes':deepcopy(SOURCE_PINS),'scriptHashes':{s:COMMON_SHA if s==COMMON else '0'*64 for s in SCRIPTS}}
    validate_protocol_header(proto,'0'*40);checks+=1
    for field in ('sourceHashes','scriptHashes'):
        bad=deepcopy(proto);bad[field].pop(next(iter(bad[field])));reject(lambda b=bad:validate_protocol_header(b,'0'*40))
    for registration in ['main','a'*39,'A'*40,'a'*41]:reject(lambda r=registration:validate_protocol_header(proto,r))
    for field,value in [('version',True),('batchId','other'),('test',{})]:
        bad=deepcopy(proto);bad[field]=value;reject(lambda b=bad:validate_protocol_header(b,'0'*40))
    bad=deepcopy(proto);bad['sourceHashes'][MANIFEST]='0'*64;reject(lambda:validate_protocol_header(bad,'0'*40))
    # Pure in-memory registered-blob/current-byte oracle, no Git subprocess.
    rawfiles={p:('source-free-control:'+p).encode() for p in INPUTS+SCRIPTS}
    fakeproto={'sourceHashes':{p:digest(rawfiles[p]) for p in INPUTS},'scriptHashes':{p:digest(rawfiles[p]) for p in SCRIPTS}}
    pbytes=b'controlled protocol';rawfiles[PROTOCOL]=pbytes;current_reads=[]
    def blob(reg,path):return rawfiles[path]
    def current(path):current_reads.append(path);return rawfiles[path]
    got=verify_payloads(fakeproto,pbytes,'0'*40,current,blob)
    assert set(got)==set(INPUTS+SCRIPTS) and len(current_reads)==27;checks+=1
    current_reads.clear();reject(lambda:verify_payloads(fakeproto,b'changed','0'*40,current,blob));assert not current_reads;checks+=1
    def changed_current(path):return rawfiles[path]+b'changed'
    reject(lambda:verify_payloads(fakeproto,pbytes,'0'*40,changed_current,blob))
    with tempfile.TemporaryDirectory(prefix='batch20-supplemental-control-') as tmp:
        parent=Path(tmp);os.chmod(parent,0o700);out=private_output(parent/'fresh')
        out.mkdir(mode=0o700);private_write(out/'control.json',b'{}\n')
        assert stat.S_IMODE(out.stat().st_mode)==0o700 and stat.S_IMODE((out/'control.json').stat().st_mode)==0o600;checks+=1
        try:private_write(out/'control.json',b'overwrite')
        except FileExistsError:checks+=1
        else:raise AssertionError('Exclusive write required')
        reject(lambda:private_output(out))
        reject(lambda:private_output(ROOT.parent.parent/'dist'/'raw-control'))
        reject(lambda:private_output(parent/'public'/'raw-control'))
        os.chmod(parent,0o755);reject(lambda:private_output(parent/'other'));os.chmod(parent,0o700)
    assert forbidden=={'bareMinikeyHashes':0,'nonSupplementalSharedCalls':0};checks+=1
    return {'version':1,'testId':TEST_ID,'status':'PASS','selfTestChecks':checks,'targetArtifactsOpened':False,'targetFormsConstructed':False,
      'bareMinikeyHashes':0,'oldSharedMinikeyCalls':0,'nonSupplementalSharedCalls':0,'G03Minikey26Enumerations':0,'scalarDerivations':0,'addressDerivations':0,'seedDerivations':0,'networkQueries':0}


class QuietParser(argparse.ArgumentParser):
    def error(self,message):raise ValueError('Invalid command arguments')


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    flags=('--definition','--self-test','--run','--protocol','--registration-commit','--out')
    require(all(argv.count(flag)<=1 for flag in flags),'Duplicate command argument')
    parser=QuietParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--definition',action='store_true');action.add_argument('--self-test',action='store_true');action.add_argument('--run',action='store_true')
    parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out');args=parser.parse_args(argv)
    extra=(args.protocol,args.registration_commit,args.out)
    if not args.run:require(not any(extra),'Run-only arguments require run')
    if args.definition:return code_definition()
    if args.self_test:return self_test()
    require(all(extra),'Protocol registration and private output required')
    return run(args.protocol,args.registration_commit,args.out)


if __name__=='__main__':
    os.umask(0o077)
    try:print(json.dumps(main(),ensure_ascii=False,allow_nan=False))
    except Exception:
        print(json.dumps({'version':1,'testId':TEST_ID,'status':'inconclusive','scopeComplete':False,'error':'Validation or execution failed; no result or semantic conclusion.'}),file=sys.stderr)
        raise SystemExit(1)
