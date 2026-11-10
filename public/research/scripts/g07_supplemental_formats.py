#!/usr/bin/env python3
"""G07 fixed saved-output compatibility adapter, offline; Python3.9+ stdlib.

Controls use only pinned source code and published support controls. Actualrun
requires the fixed public script/protocol in a Git checkout containing the
full40hex registration commit. Raw output must be fresh/outside all site files,
with0700 parent/directory and0600 files. Remote publication is checked separately.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,os,re,stat,subprocess,sys,tempfile,types
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve()
ROOT=(HERE.parent.parent if (HERE.parent/'batch20_common.py').is_file() else HERE.parents[3]/'site/public/research').resolve()
COMMON='scripts/batch20_common.py'
CORE='scripts/batch20_supplemental_formats.py'
ENGLISH='scripts/batch20_support/english.txt'
CONTROLS='scripts/batch20_support/controls.json'
LEGACY_FORMATS=('wif','minikey','hex64','bip39')
TEST_ID='g07-supplemental-fixed-formats'
BATCH_ID='keiser-g07-supplemental-fixed-formats-20261110'
PRIMARY='analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json'
OLD_RESULT='analysis_outputs/continuation_20261110/batch20/G07/RESULT.json'
OLD_CHECK='analysis_outputs/continuation_20261110/batch20/G07/INDEPENDENT_CHECK.json'
PROTOCOL='analysis_outputs/continuation_20261110/g07_supplemental/PROTOCOL.json'
SOURCE_PINS={'analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json': 'e934e778c07cba19c00c6e4fb7cb8f858042f904d320f0d919a59fa1e4c3e7da', 'analysis_outputs/continuation_20261110/batch20/G07/RESULT.json': 'fc3ab1acf7e97b6061341065d3e9c9a64626b37ee985a86db9147aa412742513', 'analysis_outputs/continuation_20261110/batch20/G07/INDEPENDENT_CHECK.json': 'f57582748af54a9ba5bec0a1db67f74ca69471f57b7859217a2de7bd432c1d4a', 'scripts/batch20_support/vision-datamatrix-control.png': '4f395fb1356cfa598ef08f3aaa07d372e1b836c6bc7bc08a6820a4584db2facc', 'scripts/batch20_support/vision-datamatrix-control.txt': '84d89877f0d4041efb6bf91a16f0248f2fd573e6af05c19f96bedb9f882f7882', 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda', 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b', 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}
INPUTS=('analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/G07/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/G07/INDEPENDENT_CHECK.json', 'scripts/batch20_support/vision-datamatrix-control.png', 'scripts/batch20_support/vision-datamatrix-control.txt', 'scripts/batch20_support/english.txt', 'scripts/batch20_support/controls.json', 'scripts/batch20_common.py')
SCRIPTS=('scripts/g07_supplemental_formats.py', 'scripts/verify_g07_supplemental.py', 'scripts/batch20_supplemental_formats.py', 'scripts/verify_batch20_supplemental.py', 'scripts/batch20_common.py')
FIXED_CODE_PINS={'scripts/batch20_supplemental_formats.py': '385524773ef0c20a2af1858bbf1d1f15cb45fd47fdf08627b0b97d2dda2754ac', 'scripts/verify_batch20_supplemental.py': 'a4bf930523eb29c0da942439eb6005514fc60d0dfb4f6deede2171380bd4389c', 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}
EXPECTATIONS={'labeledStreams': 1038, 'uniqueStreams': 833, 'uniqueForms': 1464, 'emptyTexts': 14, 'maxTextCodepoints': 1748, 'totalTextCodepoints': 42110, 'legacyMinikeyShapeOccurrences': 4, 'legacyMinikeyUniqueShapes': 3}
FORMATS=('extended_private', 'bip38', 'address', 'sec_public')
CAPS={'sourceJsonBytes': 2000000, 'registeredBlobBytes': 20000000, 'protocolBytes': 1000000, 'privateArtifactBytes': 20000000, 'totalSourceCodepoints': 50000, 'totalFormCodepoints': 100000, 'streamCodepoints': 2000, 'shapeOccurrencesPerCohort': 1000000, 'uniqueShapesPerCohort': 500000}
DEFINITION={'id': 'g07-supplemental-fixed-formats', 'title': 'Supplemental literal formats on unchanged saved G07 OCR streams', 'family': 'fixed-artifact-format-compatibility', 'branchId': 'text-lines', 'inputPaths': ['analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json', 'analysis_outputs/continuation_20261110/batch20/G07/RESULT.json', 'analysis_outputs/continuation_20261110/batch20/G07/INDEPENDENT_CHECK.json', 'scripts/batch20_support/vision-datamatrix-control.png', 'scripts/batch20_support/vision-datamatrix-control.txt', 'scripts/batch20_support/english.txt', 'scripts/batch20_support/controls.json', 'scripts/batch20_common.py'], 'implementationPaths': ['scripts/g07_supplemental_formats.py', 'scripts/verify_g07_supplemental.py', 'scripts/batch20_supplemental_formats.py', 'scripts/verify_batch20_supplemental.py', 'scripts/batch20_common.py'], 'protocolPath': 'analysis_outputs/continuation_20261110/g07_supplemental/PROTOCOL.json', 'sourceModel': {'id': 'batch20-G07-frozen-saved-streams', 'sourcePath': 'analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json', 'expectations': {'labeledStreams': 1038, 'uniqueStreams': 833, 'uniqueForms': 1464, 'emptyTexts': 14, 'maxTextCodepoints': 1748, 'totalTextCodepoints': 42110, 'legacyMinikeyShapeOccurrences': 4, 'legacyMinikeyUniqueShapes': 3}, 'fixedWitnessHashes': {'analysis_outputs/continuation_20261110/batch20/G07/STREAMS.json': 'e934e778c07cba19c00c6e4fb7cb8f858042f904d320f0d919a59fa1e4c3e7da', 'analysis_outputs/continuation_20261110/batch20/G07/RESULT.json': 'fc3ab1acf7e97b6061341065d3e9c9a64626b37ee985a86db9147aa412742513', 'analysis_outputs/continuation_20261110/batch20/G07/INDEPENDENT_CHECK.json': 'f57582748af54a9ba5bec0a1db67f74ca69471f57b7859217a2de7bd432c1d4a', 'scripts/batch20_support/vision-datamatrix-control.png': '4f395fb1356cfa598ef08f3aaa07d372e1b836c6bc7bc08a6820a4584db2facc', 'scripts/batch20_support/vision-datamatrix-control.txt': '84d89877f0d4041efb6bf91a16f0248f2fd573e6af05c19f96bedb9f882f7882', 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda', 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b', 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}, 'encoding': 'Exact saved UTF-8 strings and record order; original OCR source model unchanged.', 'ocrRerun': False, 'sourceSelectorRegenerated': False}, 'forms': {'rule': 'Unchanged per-artifact exact strings and Unicode-whitespace-only compaction, deduplicated and Python-string sorted; empty retained; no other transforms or joins.', 'maximumForms': 1464, 'otherTransforms': False}, 'literalValidation': {'commonFormats': ['extended_private', 'bip38', 'address', 'sec_public'], 'minikeyLengths': [26], 'minikeyShape': 'Overlapping embedded exact26 S-prefixed Base58 windows, no outer boundary.', 'minikeyChecksum': 'SHA256(ASCII(value + question mark))[0]==0; weak8bit only.', 'minikeyScalarHash': False, 'fingerprint': 'Existing batch20 domain-separated record fingerprint; private only.', 'rawAliasesPreservedCanonicalFingerprintsDeduplicated': True}, 'implementationDependencies': {'fixedCodePins': {'scripts/batch20_supplemental_formats.py': '385524773ef0c20a2af1858bbf1d1f15cb45fd47fdf08627b0b97d2dda2754ac', 'scripts/verify_batch20_supplemental.py': 'a4bf930523eb29c0da942439eb6005514fc60d0dfb4f6deede2171380bd4389c', 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}, 'primaryReuse': ['make_forms', 'evaluate_common4', 'scan_minikey26_forms'], 'independentReuse': ['reconstruct_forms', 'evaluate_common4', 'independent_mini26'], 'sharedFourFormatEngine': 'Unchanged batch20_common.py; both implementations share its four shape/validation routines. Independent forms/26 core is structurally separate; no claim of independent shared4 validator mathematics.'}, 'registrationGate': 'Fixed public script/protocol paths; full40hex actual local Git commit; all8source/5code/protocol current bytes equal registered blobs before target JSON parsing. Remote publication separately established by operator.', 'caps': {'sourceJsonBytes': 2000000, 'registeredBlobBytes': 20000000, 'protocolBytes': 1000000, 'privateArtifactBytes': 20000000, 'totalSourceCodepoints': 50000, 'totalFormCodepoints': 100000, 'streamCodepoints': 2000, 'shapeOccurrencesPerCohort': 1000000, 'uniqueShapesPerCohort': 500000}, 'outputPolicy': {'rawArtifacts': ['FORMS.private.json', 'VALIDATION.private.json'], 'rawOutsideEntireSiteCheckout': True, 'directoryMode': '0700', 'fileMode': '0600', 'publicReceipt': 'Aggregate counts, scope and whole-artifact integrity only; no raw values, fingerprints, addresses, SEC text or hit locators.', 'semanticConclusionComputed': False}, 'activityBoundary': {'ocrReruns': 0, 'sourceSelectorRegenerations': 0, 'newTransformsBeyondExistingForms': 0, 'newJoinsOrRepairs': 0, 'oldSharedMinikeyCalls': 0, 'minikeyScalarHashes': 0, 'proseToKeyHashes': 0, 'scalarDerivations': 0, 'addressDerivations': 0, 'seedDerivations': 0, 'childKeyDerivations': 0, 'networkQueries': 0, 'transactions': 0}, 'limitations': ['Compatibility replay of the exact saved G07 OCR outputs, not a new extraction theory or source-selection test.', 'OCR misses, unusual/damaged text, and the quality of original112detector views remain outside added-format coverage.', 'Four shared validators are unchanged and shared; a weak8bit minikey or on-curve SEC is only a review lead, not ownership/funding/prize proof.', 'No semantic recognition, source geometry conclusion or whole-puzzle exclusion is computed.']}

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

def json_bytes(value):
    return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')

def capped_read(path, limit):
    require(path.is_file() and path.stat().st_size <= limit, 'File byte cap exceeded')
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, 'File grew beyond byte cap')
    return raw

def private_output(value):
    raw=Path(value).expanduser();require(not raw.exists() and not raw.is_symlink(),'Fresh private output required')
    out=raw.resolve();require(not any(p.casefold()=='public' for p in out.parts) and not out.is_relative_to(ROOT.parent.parent),'Output outside entire site checkout required')
    require(out.parent.is_dir() and stat.S_IMODE(out.parent.stat().st_mode)==0o700,'Private0700 output parent required')
    return out

def private_write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.fchmod(fd,0o600)
    with os.fdopen(fd,'wb') as handle:handle.write(raw)

def code_definition():return deepcopy(DEFINITION)


def registered_blob(registration,relative):
    require(relative in set(INPUTS+SCRIPTS+(PROTOCOL,)),'Unregistered blob path')
    obj=registration+':public/research/'+relative
    size=subprocess.run(['git','cat-file','-s',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(size.returncode==0 and re.fullmatch(rb'[0-9]+\n',size.stdout) and len(size.stdout)<=20,'Registered blob missing')
    count=int(size.stdout);require(count<=CAPS['registeredBlobBytes'],'Registered blob cap exceeded')
    data=subprocess.run(['git','cat-file','blob',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(data.returncode==0 and len(data.stdout)==count,'Registered blob unavailable')
    return data.stdout


def validate_protocol_header(protocol,registration):
    require(isinstance(registration,str) and re.fullmatch('[0-9a-f]{40}',registration),'Full40hex registration required')
    require(isinstance(protocol,dict) and {'version','batchId','test','sourceHashes','scriptHashes'}<=set(protocol),'Protocol schema changed')
    require(type(protocol['version']) is int and protocol['version']==1 and protocol['batchId']==BATCH_ID,'Protocol identity changed')
    require(canonical(protocol['test'])==canonical(DEFINITION),'Protocol code definition changed')
    require(protocol['sourceHashes']==SOURCE_PINS,'Exact eight witness pins required')
    require(isinstance(protocol['scriptHashes'],dict) and set(protocol['scriptHashes'])==set(SCRIPTS),'Five code pins required')
    require(all(isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) for h in protocol['scriptHashes'].values()),'Invalid code pin')
    require(all(protocol['scriptHashes'][p]==h for p,h in FIXED_CODE_PINS.items()),'Frozen dependency pin changed')
    if 'registeredAtUTC' in protocol:
        stamp=datetime.fromisoformat(protocol['registeredAtUTC'].replace('Z','+00:00'))
        require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds()==0,'Registration metadata must be UTC')


def verify_payloads(protocol,pbytes,registration,current_reader,blob_reader):
    # Protocol byte proof comes before any target file opens.
    require(blob_reader(registration,PROTOCOL)==pbytes,'Protocol registered bytes differ')
    files={};pins={**protocol['sourceHashes'],**protocol['scriptHashes']}
    for relative in dict.fromkeys(INPUTS+SCRIPTS):
        registered=blob_reader(registration,relative)
        require(len(registered)<=CAPS['registeredBlobBytes'] and digest(registered)==pins[relative],'Registered content pin differs')
        current=current_reader(relative);require(current==registered,'Current bytes differ from registration')
        files[relative]=current
    return files


def require_commit(registration,runner=None):
    runner=subprocess.run if runner is None else runner
    kind=runner(['git','cat-file','-t',registration],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(kind.returncode==0 and kind.stdout==b'commit\n','Actual Git commit object required')


def validate_protocol(path,registration):
    require(HERE==(ROOT/SCRIPTS[0]).resolve(),'Actual run requires fixed public script')
    path=Path(path).expanduser().resolve(strict=True)
    require(path==(ROOT/PROTOCOL).resolve() and path.is_relative_to(ROOT),'Fixed public protocol required')
    pbytes=capped_read(path,CAPS['protocolBytes']);protocol=load_json(pbytes);validate_protocol_header(protocol,registration)
    require_commit(registration)
    def current(relative):
        file=(ROOT/relative).resolve(strict=True);require(file.is_relative_to(ROOT),'Research path escape')
        return capped_read(file,CAPS['sourceJsonBytes'] if relative in INPUTS else CAPS['registeredBlobBytes'])
    files=verify_payloads(protocol,pbytes,registration,current,registered_blob)
    require(files[SCRIPTS[0]]==HERE.read_bytes(),'Executing bytes differ')
    return protocol,pbytes,files


def compiled_module(relative,pin):
    path=ROOT/relative;raw=capped_read(path,CAPS['registeredBlobBytes'])
    require(digest(raw)==pin,'Dependency byte pin changed')
    # Compile the verified source bytes directly; do not execute cached pyc files.
    module=types.ModuleType('g07_frozen_'+Path(relative).stem);module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def load_engines():
    for relative in (ENGLISH,CONTROLS):
        require(digest(capped_read(ROOT/relative,CAPS['sourceJsonBytes']))==SOURCE_PINS[relative],'Support byte pin changed')
    core=compiled_module(CORE,FIXED_CODE_PINS[CORE]);common=compiled_module(COMMON,FIXED_CODE_PINS[COMMON])
    require(tuple(core.FORMATS)==FORMATS and tuple(common.ALL_FORMATS[-4:])==FORMATS,'Frozen format list changed')
    return core,common


def source_stats(streams):
    require(isinstance(streams,list) and all(isinstance(s,dict) and set(s)=={'id','text'} and isinstance(s['id'],str) and isinstance(s['text'],str) for s in streams),'Saved source schema changed')
    require(all(len(s['id'])<=1000 and len(s['text'])<=CAPS['streamCodepoints'] for s in streams),'Saved record cap exceeded')
    lengths=[len(s['text']) for s in streams]
    for s in streams:s['text'].encode('utf-8')
    require(sum(lengths)<=CAPS['totalSourceCodepoints'],'Source codepoint cap exceeded')
    return {'labeledStreams':len(streams),'uniqueStreams':len({s['text'] for s in streams}),'emptyTexts':sum(n==0 for n in lengths),'maxTextCodepoints':max(lengths,default=0),'totalTextCodepoints':sum(lengths)}


def validate_legacy_witnesses(result,check):
    require(isinstance(result,dict) and result.get('testId')=='G07','Old result identity changed')
    ev=result.get('evaluation');require(isinstance(ev,dict) and ev.get('formats')==list(LEGACY_FORMATS),'Old formats changed')
    for field,want in [('streamCount',1038),('uniqueStreamCount',833),('uniqueFormCount',1464)]:
        require(type(ev.get(field)) is int and ev[field]==want,'Old population changed')
    for field in ('shapeCounts','uniqueShapeCounts'):
        require(isinstance(ev.get(field),dict) and set(ev[field])==set(LEGACY_FORMATS) and all(type(n) is int and n>=0 for n in ev[field].values()),'Old shape metadata changed')
    require(ev['shapeCounts']['minikey']==4 and ev['uniqueShapeCounts']['minikey']==3,'Old minikey shape metadata changed')
    require(ev.get('validCounts')==dict.fromkeys(LEGACY_FORMATS,0),'Old valid counts changed')
    require(isinstance(check,dict) and check.get('testId')=='G07' and check.get('passed') is True,'Old independent check failed')
    for field,want in [('streamCount',1038),('uniqueFormCount',1464),('validRecords',0),('networkQueries',0)]:
        require(type(check.get(field)) is int and check[field]==want,'Old independent metadata changed')
    require(check.get('shapeCounts')==ev['shapeCounts'] and check.get('uniqueShapeCounts')==ev['uniqueShapeCounts'],'Old independent shape metadata changed')


def validate_saved_source(streams,result,check):
    stats=source_stats(streams)
    require(stats=={k:EXPECTATIONS[k] for k in stats},'Frozen G07 population changed')
    validate_legacy_witnesses(result,check)
    return streams


def evaluate(streams,core,common):
    forms=core.make_forms(streams)
    require(len(forms)==1464 and sum(map(len,forms))<=CAPS['totalFormCodepoints'],'Frozen form population/cap changed')
    c,shapes,positives=core.evaluate_common4(forms,common)
    mini,mshapes,mpositives=core.scan_minikey26_forms(forms,common)
    return forms,{'common4':c,'rawShapeValues':shapes,'rawPositives':positives,'minikey26':mini,'minikey26Shapes':mshapes,'minikey26Positives':mpositives}


def safe_result(protocol,pbytes,registration,streams,forms,validation,started,integrity):
    common=validation['common4'];mini=validation['minikey26'];total=sum(common['validCounts'].values())+mini['validCount']
    return {'version':1,'testId':TEST_ID,'batchId':BATCH_ID,'status':'g07-fixed-artifact-supplemental-scope-complete',
      'startedAtUTC':started,'completedAtUTC':utc(),'registrationCommit':registration,'protocolSha256':digest(pbytes),'sourceHashes':deepcopy(protocol['sourceHashes']),'scriptHashes':deepcopy(protocol['scriptHashes']),
      'scopeComplete':True,'supplementalGatesComplete':True,'sourceRegenerated':False,'ocrRerun':False,'semanticReviewPerformed':False,'privateReviewRequired':bool(total),
      'counts':{'labeledStreams':len(streams),'uniqueStreams':len({s['text'] for s in streams}),'uniqueForms':len(forms),'totalValidRecords':total},
      'common4':{k:deepcopy(common[k]) for k in ('formats','shapeCounts','uniqueShapeCounts','validationCalls','validCounts')},
      'minikey26':{k:mini[k] for k in ('status','enumerated','shapeOccurrences','uniqueShapeCount','checksumCalls','validCount')},
      'privateArtifactIntegrity':integrity,'activity':deepcopy(DEFINITION['activityBoundary']),'limitations':deepcopy(DEFINITION['limitations'])}


def run(protocol_path,registration,out_value):
    started=utc();out=private_output(out_value);protocol,pbytes,files=validate_protocol(protocol_path,registration)
    # Target JSON parsing occurs only after all registered/current byte proofs.
    streams=validate_saved_source(load_json(files[PRIMARY]),load_json(files[OLD_RESULT]),load_json(files[OLD_CHECK]))
    core,common=load_engines();forms,validation=evaluate(streams,core,common)
    payloads={'FORMS.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,'sourceArtifactSha256':SOURCE_PINS[PRIMARY],'streams':streams,'forms':forms}),
      'VALIDATION.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,**validation})}
    require(all(len(raw)<=CAPS['privateArtifactBytes'] for raw in payloads.values()),'Private artifact byte cap exceeded')
    result=safe_result(protocol,pbytes,registration,streams,forms,validation,started,{name:digest(raw) for name,raw in payloads.items()})
    result_bytes=json_bytes(result);out.mkdir(mode=0o700);os.chmod(out,0o700)
    try:
        for name,raw in payloads.items():private_write(out/name,raw)
        private_write(out/'RESULT.json',result_bytes)
    except Exception:
        try:private_write(out/'FAILURE.json',json_bytes({'version':1,'testId':TEST_ID,'scopeComplete':False,'status':'inconclusive-private-write-failure'}))
        except Exception:pass
        raise
    return result
def self_test():
    checks=0
    def reject(call):
        nonlocal checks
        try:call()
        except (ValueError,UnicodeError):checks+=1
        else:raise AssertionError('Expected source-free rejection')
    core,common=load_engines();controls=load_json(capped_read(ROOT/CONTROLS,CAPS['sourceJsonBytes']))
    toy=[{'id':'a','text':' A\tB\nC\u00a0D\u2003E\u2028F '},{'id':'b','text':' A\tB\nC\u00a0D\u2003E\u2028F '},{'id':'c','text':''}]
    assert core.make_forms(toy)==['',' A\tB\nC\u00a0D\u2003E\u2028F ','ABCDEF'];checks+=1
    assert core.make_forms([{'text':'a-♥\u200b\u241e b'}])==['a-♥\u200b\u241e b','a-♥\u200b\u241eb'];checks+=1
    assert source_stats([{'id':'a','text':''},{'id':'b','text':'ab'},{'id':'c','text':'ab'}])=={'labeledStreams':3,'uniqueStreams':2,'emptyTexts':1,'maxTextCodepoints':2,'totalTextCodepoints':4};checks+=1
    for bad in [{},[{'id':'a','text':1}],[{'id':2,'text':'a'}],[{'id':'a','text':'a','extra':1}],[{'id':'a','text':'x'*(CAPS['streamCodepoints']+1)}]]:
        reject(lambda value=bad:source_stats(value))
    reject(lambda:load_json(b'{"a":1,"a":2}'));reject(lambda:load_json(b'{"a":NaN}'))
    ev={'streamCount':1038,'uniqueStreamCount':833,'uniqueFormCount':1464,'formats':list(LEGACY_FORMATS),'shapeCounts':dict.fromkeys(LEGACY_FORMATS,0),'uniqueShapeCounts':dict.fromkeys(LEGACY_FORMATS,0),'validCounts':dict.fromkeys(LEGACY_FORMATS,0)}
    ev['shapeCounts']['minikey']=4;ev['uniqueShapeCounts']['minikey']=3
    old_result={'testId':'G07','evaluation':ev};old_check={'testId':'G07','passed':True,'streamCount':1038,'uniqueFormCount':1464,'shapeCounts':deepcopy(ev['shapeCounts']),'uniqueShapeCounts':deepcopy(ev['uniqueShapeCounts']),'validRecords':0,'networkQueries':0}
    validate_legacy_witnesses(old_result,old_check);checks+=1
    for key,value in [('passed',False),('networkQueries',1),('validRecords',1),('streamCount',1037),('testId','other')]:
        bad=deepcopy(old_check);bad[key]=value;reject(lambda b=bad:validate_legacy_witnesses(old_result,b))
    for field in ('shapeCounts','uniqueShapeCounts','validCounts'):
        bad=deepcopy(old_result);bad['evaluation'][field]['minikey']+=1;reject(lambda b=bad:validate_legacy_witnesses(b,old_check))
    reject(lambda:validate_saved_source([],old_result,old_check))
    old_hash=hashlib.sha256;old_shape=common.shape_values;old_validate=common.validate_record
    forbidden={'bareMinikeyHashes':0,'nonSupplementalSharedCalls':0,'wholeCoreSelfTests':0}
    def guarded_hash(data=b'',*args,**kwargs):
        raw=bytes(data)
        if len(raw) in (22,26,30) and raw.startswith(b'S') and all(chr(c) in core.B58 for c in raw):
            forbidden['bareMinikeyHashes']+=1;raise AssertionError('Bare minikey SHA forbidden')
        return old_hash(data,*args,**kwargs)
    def guarded_shape(kind,*args,**kwargs):
        if kind not in FORMATS:
            forbidden['nonSupplementalSharedCalls']+=1;raise AssertionError('Only added four formats allowed')
        return old_shape(kind,*args,**kwargs)
    def guarded_validate(kind,*args,**kwargs):
        if kind not in FORMATS:
            forbidden['nonSupplementalSharedCalls']+=1;raise AssertionError('Only added four formats allowed')
        return old_validate(kind,*args,**kwargs)
    def forbidden_self_test(*args):
        forbidden['wholeCoreSelfTests']+=1;raise AssertionError('Whole dependency self-test forbidden')
    core.self_test=forbidden_self_test;common.self_test=forbidden_self_test
    hashlib.sha256=guarded_hash;common.shape_values=guarded_shape;common.validate_record=guarded_validate
    try:
        pairs=[('extended_private','bip32_extended_private'),('bip38','bip38_encrypted_private'),('address','legacy_address'),('address','segwit_v0'),('address','segwit_v1'),('sec_public','sec_compressed_generator'),('sec_public','sec_uncompressed_generator')]
        for kind,key in pairs:assert common.validate_record(kind,controls[key]);checks+=1
        mini=None
        for counter in range(65536):
            n=counter;suffix=''
            while n:n,remainder=divmod(n,58);suffix=core.B58[remainder]+suffix
            value='S'+'2'*21+(suffix or '1').rjust(4,'1')
            if core.minikey26_valid(value):mini=value;break
        assert mini is not None and len(mini)==26;checks+=1
        values=[controls[key] for _,key in pairs]+[mini]
        values+=['control'+str(i).zfill(5) for i in range(1464-len(values))]
        streams=[{'id':'control-'+str(i),'text':text} for i,text in enumerate(values)]
        forms,validation=evaluate(streams,core,common)
        assert len(forms)==1464 and all(validation['common4']['validCounts'][kind]>=1 for kind in FORMATS) and validation['minikey26']['validCount']==1;checks+=1
        sec=[p for p in validation['rawPositives'] if p['format']=='sec_public']
        assert len(sec)==2 and validation['common4']['validCounts']['sec_public']==1;checks+=1
        assert validation['minikey26Positives'][0]['fingerprint']==common.fingerprint('minikey',mini.encode('ascii'));checks+=1
        for text in ['S'*22,'S'*25,mini[:25],'s'+mini[1:],'Ｓ'+mini[1:],mini[:4]+'0'+mini[5:]]:
            summary,shapes,positives=core.scan_minikey26_forms([text],common)
            assert summary['shapeOccurrences']==summary['checksumCalls']==0 and shapes==positives==[];checks+=1
        summary,shapes,positives=core.scan_minikey26_forms(['S'*27],common)
        assert summary['shapeOccurrences']==2 and summary['uniqueShapeCount']==summary['checksumCalls']==1;checks+=1
        summary,shapes,positives=core.scan_minikey26_forms(['!'+mini+'1!',mini],common)
        assert summary['shapeOccurrences']==2 and summary['uniqueShapeCount']==summary['checksumCalls']==summary['validCount']==1;checks+=1
        split=mini[:13]+'\u241e'+mini[13:]
        assert core.scan_minikey26_forms(core.make_forms([{'text':split}]),common)[0]['shapeOccurrences']==0;checks+=1
        reject(lambda:evaluate([{'id':'few','text':'alpha beta'}],core,common))
        proto={'version':1,'batchId':BATCH_ID,'test':code_definition(),'sourceHashes':deepcopy(SOURCE_PINS),'scriptHashes':{p:FIXED_CODE_PINS.get(p,'0'*64) for p in SCRIPTS}}
        receipt=safe_result(proto,b'control protocol','0'*40,streams,forms,validation,'control',{'FORMS.private.json':'1'*64,'VALIDATION.private.json':'2'*64})
        assert receipt['privateReviewRequired'] and receipt['counts']['totalValidRecords']>=7;checks+=1
        rendered=json_bytes(receipt)
        for raw in [mini.encode(),*(controls[key].encode() for _,key in pairs),*(p['fingerprint'].encode() for p in validation['rawPositives'])]:
            assert raw not in rendered
        assert b'fingerprint' not in rendered and b'locators' not in rendered and b'rawShapeValues' not in rendered;checks+=1
    finally:
        hashlib.sha256=old_hash;common.shape_values=old_shape;common.validate_record=old_validate
    validate_protocol_header(proto,'0'*40);checks+=1
    for field in ('sourceHashes','scriptHashes'):
        bad=deepcopy(proto);bad[field].pop(next(iter(bad[field])));reject(lambda b=bad:validate_protocol_header(b,'0'*40))
    for reg in ['main','a'*39,'A'*40,'a'*41]:reject(lambda r=reg:validate_protocol_header(proto,r))
    bad=deepcopy(proto);bad['test']['forms']['maximumForms']=1;reject(lambda:validate_protocol_header(bad,'0'*40))
    bad=deepcopy(proto);bad['scriptHashes'][CORE]='0'*64;reject(lambda:validate_protocol_header(bad,'0'*40))
    for code,kind in [(0,b'tree\n'),(0,b'tag\n'),(1,b'commit\n'),(0,b''),(0,b'commit\nextra')]:
        def runner(*args,c=code,k=kind,**kwargs):return types.SimpleNamespace(returncode=c,stdout=k)
        reject(lambda r=runner:require_commit('0'*40,r))
    require_commit('0'*40,lambda *a,**k:types.SimpleNamespace(returncode=0,stdout=b'commit\n'));checks+=1
    rawfiles={p:('source-free-control:'+p).encode() for p in dict.fromkeys(INPUTS+SCRIPTS)}
    fakeproto={'sourceHashes':{p:digest(rawfiles[p]) for p in INPUTS},'scriptHashes':{p:digest(rawfiles[p]) for p in SCRIPTS}}
    pbytes=b'control protocol';rawfiles[PROTOCOL]=pbytes;reads=[]
    def blob(reg,path):return rawfiles[path]
    def current(path):reads.append(path);return rawfiles[path]
    assert set(verify_payloads(fakeproto,pbytes,'0'*40,current,blob))==set(INPUTS+SCRIPTS) and len(reads)==12;checks+=1
    reads.clear();reject(lambda:verify_payloads(fakeproto,b'changed','0'*40,current,blob));assert reads==[];checks+=1
    reject(lambda:verify_payloads(fakeproto,pbytes,'0'*40,lambda p:rawfiles[p]+b'changed',blob))
    with tempfile.TemporaryDirectory(prefix='g07-supplemental-control-') as tmp:
        parent=Path(tmp);os.chmod(parent,0o700);out=private_output(parent/'fresh');out.mkdir(mode=0o700);private_write(out/'control.json',b'{}\n')
        assert stat.S_IMODE(out.stat().st_mode)==0o700 and stat.S_IMODE((out/'control.json').stat().st_mode)==0o600;checks+=1
        reject(lambda:private_output(out));reject(lambda:private_output(ROOT.parent.parent/'dist'/'raw-control'));reject(lambda:private_output(parent/'public'/'raw-control'))
        try:private_write(out/'control.json',b'overwrite')
        except FileExistsError:checks+=1
        else:raise AssertionError('Exclusive write required')
        os.chmod(parent,0o755);reject(lambda:private_output(parent/'other'));os.chmod(parent,0o700)
    assert forbidden=={'bareMinikeyHashes':0,'nonSupplementalSharedCalls':0,'wholeCoreSelfTests':0};checks+=1
    return {'version':1,'testId':TEST_ID,'status':'PASS','selfTestChecks':checks,'targetArtifactsOpened':False,'targetFormsConstructed':False,'bareMinikeyHashes':0,'oldSharedMinikeyCalls':0,'nonSupplementalSharedCalls':0,'wholeCoreSelfTests':0,'ocrReruns':0,'sourceSelectorRegenerations':0,'scalarDerivations':0,'addressDerivations':0,'networkQueries':0}


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
