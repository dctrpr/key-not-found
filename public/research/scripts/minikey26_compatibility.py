#!/usr/bin/env python3
"""Separate26-character compatibility replay. Old scripts/results stay unchanged.

--definition/--self-test never open target data. --preflight checks pinned bytes
only. --run requires public protocol/local Git bytes and fresh private outputs.
The imported old Node module also defines address/network functions; this runner
invokes only its unchanged source builders. No downstream action is performed.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,re,subprocess,sys
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if (HERE/'global_mirror_dag.py').is_file() else Path(__file__).resolve().parents[3]/'site/public/research'
sys.path.insert(0,str(ROOT/'scripts'))
LITERAL='analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json'
OLD_LITERAL='analysis_outputs/continuation_20261110/minikey_windows/RESULT.json'
OLD_GLOBAL='analysis_outputs/continuation_20261110/mirror_global_envelope/RESULT.json'
HISTORY='analysis_outputs/continuation_20261110/minikey26_compatibility/HISTORICAL_SOURCE.json'
BATCH_ID='keiser-minikey26-original-compatibility-20261110'
B58=frozenset('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
DOMAIN=b'KEY404/batch20/record-fingerprint/v1\x00minikey\x00'
FINGERPRINT_RULE={'algorithm':'SHA-256','domainText':'KEY404/batch20/record-fingerprint/v1','separatorHex':'00','rule':'SHA256(domain || 0x00 || ASCII(minikey) || 0x00 || ASCII(candidate))'}


SOURCE_PINS={'analysis_outputs/continuation_20261110/mirror_boundary_review/SOURCE_MODEL.json': '8b378d6c88f4f132af9697482ef9e49024694791bccae87d4437c367091273e6',
 'sources/word-geometry-20261110.json': 'e3348d0d60d3097b05d0afdb0a1fccf66409274408af9ae7a9369c37fe596e9f',
 'sources/printed-lines.json': 'c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe',
 'analysis_outputs/3d_article_map/article_3d_map_data.json': '22c2285a6cd53f6bdda7bdd284d556c52ff55dea0a55cd1b549acbb81443eac3',
 'analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json': '4d6d029bf5f7e90acfa1d456bc94e790913c7865b923c9367212c219867742f3',
 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',
 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b',
 'analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json': '1651a33dab46babf36f56439ddb409058cfa36712d96ead7d4200962b80817b9',
 'analysis_outputs/continuation_20261110/minikey_windows/RESULT.json': '49cc574ebb4ae9276ae9fec357558cbab0daf6b495b5c55b8a468e7e41e1921f',
 'analysis_outputs/continuation_20261110/mirror_global_envelope/RESULT.json': 'e3c0aceba6eb16d862710f474a6433ea31628f0522e2dca214bfc8af20cf4f8c',
 'analysis_outputs/continuation_20261110/minikey26_compatibility/HISTORICAL_SOURCE.json': '8f38c33fd22cb300615a43b6dcac466812cb9df9ddc787a21d757c94dff0e07d'}
SOURCE_BYTES={'analysis_outputs/continuation_20261110/mirror_boundary_review/SOURCE_MODEL.json': 607215,
 'sources/word-geometry-20261110.json': 4660187,
 'sources/printed-lines.json': 116759,
 'analysis_outputs/3d_article_map/article_3d_map_data.json': 2307412,
 'analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json': 8694,
 'scripts/batch20_support/english.txt': 13116,
 'scripts/batch20_support/controls.json': 817,
 'analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json': 16852358,
 'analysis_outputs/continuation_20261110/minikey_windows/RESULT.json': 111658,
 'analysis_outputs/continuation_20261110/mirror_global_envelope/RESULT.json': 16689,
 'analysis_outputs/continuation_20261110/minikey26_compatibility/HISTORICAL_SOURCE.json': 1069}
SCRIPTS=('scripts/minikey26_compatibility.py', 'scripts/minikey_window_audit.cjs', 'scripts/global_mirror_envelope.py', 'scripts/global_mirror_dag.py', 'scripts/verify_minikey26_compatibility.py')
FIXED_CODE_PINS={'scripts/minikey_window_audit.cjs': '189c6f359a057021adbc060ddeaa8caa29e6f58c40a6976daeda62025d2182f0',
 'scripts/global_mirror_envelope.py': '61538c617f74b9ab1dde922cd263e88436eb9ccc430b2072dcc003c49a50d712',
 'scripts/global_mirror_dag.py': '8134260ef4811830e5653a9d5294acec9b154eb9df3d11c9b558e50fe20ca12d'}
DEFINITION={'id': 'minikey26-original-compatibility',
 'title': 'Historical26-character minikey compatibility in frozen Issue24 populations',
 'family': 'literal-format-compatibility-replay',
 'branchId': 'text-lines',
 'inputPaths': ['analysis_outputs/continuation_20261110/mirror_boundary_review/SOURCE_MODEL.json',
                'sources/word-geometry-20261110.json',
                'sources/printed-lines.json',
                'analysis_outputs/3d_article_map/article_3d_map_data.json',
                'analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json',
                'scripts/batch20_support/english.txt',
                'scripts/batch20_support/controls.json',
                'analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json',
                'analysis_outputs/continuation_20261110/minikey_windows/RESULT.json',
                'analysis_outputs/continuation_20261110/mirror_global_envelope/RESULT.json',
                'analysis_outputs/continuation_20261110/minikey26_compatibility/HISTORICAL_SOURCE.json'],
 'implementationPaths': ['scripts/minikey26_compatibility.py',
                         'scripts/minikey_window_audit.cjs',
                         'scripts/global_mirror_envelope.py',
                         'scripts/global_mirror_dag.py',
                         'scripts/verify_minikey26_compatibility.py'],
 'parameters': {'lengths': [26],
                'alphabet': '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
                'prefix': 'S',
                'checksum': 'First byte of SHA256(ASCII(candidate + question-mark)) equals zero; no scalar '
                            'derivation.',
                'literalPopulation': {'frozenStreams': 22,
                                      'exactOrWhitespaceCompactedForms': 42,
                                      'potentialPositionWindows26': 113662,
                                      'wordOrCharacterTransformAdded': False},
                'globalPopulation': {'globalFamilies': 4,
                                     'languageDescriptors': 24,
                                     'selectionPaths': 43347744,
                                     'builder': 'Unchanged checked_source_families and graph functions; '
                                                'unchanged pair, color, edge, row order, projection and '
                                                'omission choices.',
                                     'candidateSemantics': 'Unique reachable26-character shapes, not '
                                                           'occurrences or expanded full-reading counts.'},
                'maximumProductPrefixStateVisits': 2000000,
                'maximumUniqueCandidateInsertions': 1000000,
                'maximumLiteralPositions': 113662,
                'maximumSourceBlobBytes': 20000000,
                'maximumNodeBuilderOutputBytes': 2000000,
                'networkAddressQueries': 0,
                'scalarDerivations': 0,
                'addressDerivations': 0,
                'transactions': 0,
                'automaticHistoryFollowup': False,
                'rawArtifacts': ['FORMS.private.json', 'CANDIDATES.private.json'],
                'candidateFingerprint': 'Existing batch20 domain-separated minikey fingerprint; never '
                                        'SHA256(candidate).',
                'preflight': 'Exact source/code/protocol byte-pin checks only; no target parsing, '
                             'enumeration or checksum work.'},
 'historicalSource': {'schemaVersion': 1,
                      'sourceURL': 'https://github.com/casascius/Bitcoin-Address-Utility/blob/e493d51e4a1da7536fc8e8aea38eeaee38abf4cb/Model/MiniKeyPair.cs',
                      'rawURL': 'https://raw.githubusercontent.com/casascius/Bitcoin-Address-Utility/e493d51e4a1da7536fc8e8aea38eeaee38abf4cb/Model/MiniKeyPair.cs',
                      'commit': 'e493d51e4a1da7536fc8e8aea38eeaee38abf4cb',
                      'commitDate': '2013-02-02T06:30:48Z',
                      'sourceBytes': 6544,
                      'sourceSha256': '80e65113831f35efee29bef828efd6705a9cb8418d4067e183d2478e4aa3f99c',
                      'sourceLines': {'lengthGuard': 144,
                                      'checksum': 148,
                                      'success': 149,
                                      'prefix': 145,
                                      'alphabet': 146},
                      'acceptedLengths': [22, 26, 30],
                      'compatibilityInterpretation': 'Historical implementation support; not a claim that '
                                                     'every specification requires26 or that the puzzle '
                                                     'creator selected26.',
                      'newReplayLengths': [26],
                      'sourceCodeRedistributed': False,
                      'retrievalVerification': 'Independent raw-source bytes matched the retained copy, and '
                                               'GitHub commit metadata independently confirmed the date.'},
 'controls': ['synthetic-valid-invalid26-only',
              'old22-30-validator-gap-control',
              'unchanged-Node-source-builder-with-synthetic-prose',
              'DAG26-vs-exhaustive-toys',
              'omission-conditional-space-reversal-embedded-windows',
              'state-candidate-cap-inconclusive',
              'protocol-schema-pin-and-Git-byte-guards',
              'safe-output-allowlist'],
 'negativeCriterion': 'A complete zero excludes only historical26-character minikey compatibility in the '
                      'declared frozen42-form and24-DAG populations. Existing22/30 results remain unchanged.',
 'limitations': ['Historical implementation support is not evidence that the creator used26 characters or '
                 'that every specification requires26.',
                 'The eight-bit checksum is weak under repeated trials; a pass is private review, not puzzle '
                 'authentication.',
                 'Global source membership/geometry conventions are investigator hypotheses, not calibrated '
                 'physical bounds.',
                 'No new source reading, geometry, word filter, other length, scalar/address derivation, '
                 'wallet action or network lookup is included.']}

def code_definition():
    return deepcopy(DEFINITION)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

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

def private_output(value):
    out = Path(value).expanduser().resolve()
    require(not any(part.lower() == 'public' for part in out.parts), 'Private output required')
    require(not out.exists() and not out.is_symlink(), 'Fresh output required')
    require(out.parent.is_dir(), 'Existing private output parent required')
    return out

def verify_registered_bytes(registration, files, reader):
    # Pure equality helper; controls supply synthetic bytes and a mock reader.
    for relative, content in files.items():
        require(reader(registration, relative) == content, 'Registration bytes differ')


def sha(data):return hashlib.sha256(data).hexdigest()
def shape26(value):return isinstance(value,str) and len(value)==26 and value.startswith('S') and all(c in B58 for c in value)
def check26(value):return shape26(value) and hashlib.sha256((value+'?').encode('ascii')).digest()[0]==0
def fingerprint(value):return sha(DOMAIN+value.encode('ascii'))

class LimitExceeded(RuntimeError):pass
class Budget:
    def __init__(self,states=2000000,candidates=1000000):self.states=0;self.candidates=0;self.maxStates=states;self.maxCandidates=candidates
    def visit(self):
        self.states+=1
        if self.states>self.maxStates:raise LimitExceeded('State cap; incomplete')
    def insert(self):
        self.candidates+=1
        if self.candidates>self.maxCandidates:raise LimitExceeded('Candidate cap; incomplete')

def union26(graph,budget,result):
    # Exact specialization of the old S/Base58 prefix walk: stop at26 only.
    # Start at every reachable S node; embedded values need no outer boundary.
    chars=graph['chars'];nexts=graph['next'];visited=set()
    stack=[(node,'S') for node,char in chars.items() if char=='S']
    while stack:
        node,value=stack.pop();state=(node,value)
        if state in visited:continue
        visited.add(state);budget.visit()
        if len(value)==26:
            if value not in result:result.add(value);budget.insert()
        else:
            stack.extend((n,value+chars[n]) for n in nexts[node] if n!=-1 and chars[n] in B58)
    return result

NODE_BUILDER = r"""
const fs=require('node:fs');
const helpers=require(process.argv[1]);
const data=JSON.parse(fs.readFileSync(0,'utf8'));
const selected=helpers.selectStreams(data);
const forms=helpers.makeForms(selected);
process.stdout.write(JSON.stringify({streamCount:selected.length,forms:forms.map(f=>f.text)}));
"""
def source_forms(raw):
    # require() does not execute the old module's CLI: require.main !== module.
    run=subprocess.run(['node','-e',NODE_BUILDER,str(ROOT/'scripts/minikey_window_audit.cjs')],input=raw,capture_output=True,timeout=30,check=False)
    require(run.returncode==0 and len(run.stdout)<=2000000,'Source builder failed/capped')
    data=json.loads(run.stdout,object_pairs_hook=unique_json_object)
    require(set(data)=={'streamCount','forms'} and type(data['streamCount']) is int and isinstance(data['forms'],list),'Source builder schema changed')
    require(all(isinstance(s,str) and len(s)>30 for s in data['forms']) and len(set(data['forms']))==len(data['forms']),'Source forms changed')
    return data

def flat26(forms):
    values=set();occurrences=0;positions=0
    for text in forms:
        positions+=max(0,len(text)-25)
        require(positions<=113662,'Literal position cap exceeded')
        for match in re.finditer(r'(?=(S[1-9A-HJ-NP-Za-km-z]{25}))',text):
            values.add(match.group(1));occurrences+=1
    return values,positions,occurrences

def check_code_dependencies():
    for relative,expected in FIXED_CODE_PINS.items():
        require(sha(capped_read(ROOT/relative,200000))==expected,'Frozen source-builder code changed')

def registered_blob(commit,relative):
    name=commit+':public/research/'+relative
    size=subprocess.run(['git','cat-file','-s',name],cwd=ROOT,capture_output=True,timeout=30)
    require(size.returncode==0 and re.fullmatch(rb'[0-9]+\n',size.stdout) and len(size.stdout)<=20,'Missing registration size')
    count=int(size.stdout);require(count<=20000000,'Registration cap exceeded')
    blob=subprocess.run(['git','cat-file','blob',name],cwd=ROOT,capture_output=True,timeout=30)
    require(blob.returncode==0 and len(blob.stdout)==count,'Missing registration bytes')
    return blob.stdout

def protocol_header(protocol):
    require(isinstance(protocol,dict) and set(protocol)=={'version','batchId','test','sourceHashes','scriptHashes'},'Protocol schema changed')
    require(type(protocol['version']) is int and protocol['version']==1 and protocol['batchId']==BATCH_ID and protocol['test']==code_definition(),'Protocol differs from code')
    require(protocol['sourceHashes']==SOURCE_PINS,'Source pins changed')
    require(isinstance(protocol['scriptHashes'],dict) and set(protocol['scriptHashes'])==set(SCRIPTS),'Script pins changed')
    require(all(isinstance(v,str) and re.fullmatch(r'[0-9a-f]{64}',v) for v in protocol['scriptHashes'].values()),'Invalid script pin')
    require(all(protocol['scriptHashes'][p]==h for p,h in FIXED_CODE_PINS.items()),'Frozen builder pin changed')

def validate_protocol(argument,commit=None,git_required=False,reader=None):
    file=Path(argument).resolve(strict=True);require(file.is_file() and file.is_relative_to(ROOT),'Public protocol required')
    raw=capped_read(file,1000000);protocol=json.loads(raw,object_pairs_hook=unique_json_object);protocol_header(protocol)
    files={}
    for relative,expected in {**SOURCE_PINS,**protocol['scriptHashes']}.items():
        path=(ROOT/relative).resolve(strict=True);require(path.is_relative_to(ROOT) and path.is_file(),'Pinned path escapes root')
        content=capped_read(path,20000000)
        if relative in SOURCE_BYTES:require(len(content)==SOURCE_BYTES[relative],'Pinned source byte length changed')
        require(sha(content)==expected,'Pinned bytes changed');files[relative]=content
    rel=file.relative_to(ROOT).as_posix();require(rel not in files,'Protocol replaces source');files[rel]=raw
    if git_required or commit:
        require(re.fullmatch(r'[0-9a-f]{40}',commit or '') is not None,'Full registration commit required')
        verify_registered_bytes(commit,files,reader or registered_blob)
    return protocol,sha(raw),files

def assess(candidates):
    hits=[]
    for value in sorted(candidates):
        require(shape26(value),'Non26 shape reached validation')
        if check26(value):hits.append({'format':'minikey','length':26,'checkBits':8,'fingerprint':fingerprint(value),'private':True})
    return {'lengths':[26],'uniqueShapeCount':len(candidates),'checksumValidCount':len(hits),'checksumCalls':len(candidates),
            'hits':hits,'fingerprintRule':FINGERPRINT_RULE,'privateReviewRequired':bool(hits)}

def self_test():
    check_code_dependencies()
    from global_mirror_dag import graph,plain_readings
    good=None
    for n in range(65536):
        alphabet='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';v=n;suffix=''
        while True:
            v,k=divmod(v,58);suffix=alphabet[k]+suffix
            if not v:break
        value='S'+'2'*19+suffix.rjust(6,'2')
        if check26(value):good=value;break
    require(good is not None,'Synthetic26 control generation failed')
    bad=next(good[:-1]+c for c in alphabet if not check26(good[:-1]+c))
    require(shape26(bad) and not check26(bad),'Bad checksum control failed')
    require(all(not check26(s) for s in ['T'+good[1:],'S0'+good[2:],good[:-1],good+'1','S'+'2'*21,'S'+'2'*29]),'Length/prefix/alphabet gate failed')
    # Old validator compatibility was static-reviewed; a synthetic26 shape never
    # appears in its hardcoded22/30 shape API. Do not change or invoke it on targets.
    from global_mirror_dag import candidate_union
    require(good not in candidate_union(graph([[good]]),[],result={k:set() for k in ('wif','minikey','hex64','bip39')})['minikey'],'Old API unexpectedly included26')
    fixture='prefix :: '+good+' :: suffix'
    metadata={'frame':'body','subset':'all','parityBase':'all_printed_rows','reset':'global','projection':'first_words','phase':'all','direction':'down','textDirection':'normal'}
    built=source_forms(json.dumps({'candidates':[{'sha256':sha(fixture.encode()),'text':fixture,'variants':[metadata]}]}).encode())
    require(built['streamCount']==1 and len(built['forms'])==2 and all(good in s for s in built['forms']),'Unchanged source builder control failed')
    values,_,_=flat26(built['forms']);require(good in values,'Embedded flat26 control failed')
    cases=[[[None,'!'],[good[:13]],[good[13:]],[None,'!']],[[good[:12],good[:11]+'0'],[None],[good[12:]]],[[good+'S'+'2'*25]],[[None],[None]],[['S'],['2'*24],['2','0'],['!',None]],[[good[:10]],[good[10:20]],[good[20:]],[None,'S']]]
    comparisons=0
    for rows in cases:
        for mode in ('words-spaced','words-joined','initials'):
            for reverse in (False,True):
                readings=list(plain_readings(rows,mode,reverse));expected={m.group(1) for s in readings for m in re.finditer(r'(?=(S[1-9A-HJ-NP-Za-km-z]{25}))',s)}
                actual=union26(graph(rows,mode,reverse),Budget(),set());require(actual==expected,'DAG26 exhaustive control mismatch');comparisons+=1
    for budget in (Budget(states=0),Budget(candidates=0)):
        partial=set()
        try:union26(graph([[good]]),budget,partial)
        except LimitExceeded:pass
        else:raise ValueError('Cap did not fail')
    safe=assess({good,bad});require(safe['checksumValidCount']==1 and good not in json.dumps(safe),'Safe output failed')
    mock={'version':1,'batchId':BATCH_ID,'test':code_definition(),'sourceHashes':dict(SOURCE_PINS),'scriptHashes':{**{relative:'1'*64 for relative in SCRIPTS},**FIXED_CODE_PINS}}
    protocol_header(mock)
    changed=deepcopy(mock);changed['test']['parameters']['lengths']=[22,26,30]
    for invalid in [changed,{**mock,'sourceHashes':{}},{**mock,'scriptHashes':{}},{**mock,'version':True}]:
        try:protocol_header(invalid)
        except ValueError:pass
        else:raise ValueError('Protocol drift accepted')
    files={'synthetic':b'control'};verify_registered_bytes('1'*40,files,lambda c,p:files[p])
    try:verify_registered_bytes('1'*40,files,lambda c,p:files[p]+b'x')
    except ValueError:pass
    else:raise ValueError('Registration drift accepted')
    return {'passed':True,'syntheticDAGComparisons':comparisons,'syntheticValid26':1,'syntheticInvalid26':1,'syntheticCapsRejected':2,'protocolDriftRejections':5,'targetSourcesParsed':False,'target26ShapesEnumerated':0,'target26Checksums':0,'scalarDerivations':0,'addressDerivations':0,'networkAddressQueries':0}

def run(args):
    require(re.fullmatch(r'[0-9a-f]{40}',args.registration_commit or '') is not None,'Full registration commit required')
    out=private_output(args.out);out.mkdir(mode=0o700)
    base={'schemaVersion':1,'batchId':BATCH_ID,'testId':DEFINITION['id'],'startedAtUTC':utc(),'registrationCommit':args.registration_commit,'scopeComplete':False,'completeNegative':False,'privateReviewRequired':False,'candidateAssessment':'not-run','scalarDerivations':0,'addressDerivations':0,'networkAddressQueries':0,'transactions':0}
    literal=set();global_values=set();budget=Budget();details=[];started=False;extraction_complete=False
    try:
        controls=self_test();protocol,protocol_hash,files=validate_protocol(args.protocol,args.registration_commit,True)
        require(json.loads(files[OLD_LITERAL])['scope']=={'recordedStreams':22,'uniqueForms':42,'positionWindows22':113830,'positionWindows30':113494,'totalPositionWindows':227324},'Prior literal scope changed')
        require(json.loads(files[OLD_GLOBAL])['scopeComplete'] is True,'Prior global scope incomplete')
        require(json.loads(files[HISTORY])==DEFINITION['historicalSource'],'Historical receipt differs')
        base.update(protocolSha256=protocol_hash,sourceHashes=protocol['sourceHashes'],scriptHashes=protocol['scriptHashes'],parameters=DEFINITION['parameters'],controls=controls)
        built=source_forms(files[LITERAL]);require(built['streamCount']==22 and len(built['forms'])==42,'Literal source population changed')
        private_json(out/'FORMS.private.json',built);started=True
        literal,positions,occurrences=flat26(built['forms']);require(positions==113662,'Literal position count differs')
        base['literalCounts']={'frozenStreams':22,'uniqueForms':42,'positionWindows26':positions,'shapeCompatibleOccurrences':occurrences,'uniqueShapes':len(literal)}
        from global_mirror_envelope import checked_source_families
        from global_mirror_dag import graph
        families=checked_source_families();require(len(families)==4,'Global source family population differs')
        for family in families:
            for reverse in (False,True):
                for mode in ('words-spaced','words-joined','initials'):
                    item={'family':family['id'],'rowOrder':'reverse-entire-sequence' if reverse else 'forward','projection':mode,'complete':False};details.append(item)
                    before_states=budget.states;before_shapes=len(global_values)
                    try:union26(graph(family['rows'],mode,reverse),budget,global_values);item['complete']=True
                    finally:item.update(stateVisits=budget.states-before_states,newUniqueShapes=len(global_values)-before_shapes)
        require(len(details)==24 and all(d['complete'] for d in details),'Global language coverage incomplete')
        require(len(global_values)==budget.candidates,'Global insertion accounting differs')
        require(len(literal|global_values)<=1000000,'Combined candidate cap exceeded')
        extraction_complete=True
    except Exception as error:
        base.update(outcome='inconclusive-control-pin-source-cap-or-execution',errorClass=type(error).__name__,error='Registered compatibility replay failed; no negative claim.')
        private_json(out/'ERROR.private.json',{'errorClass':type(error).__name__,'error':'Registered compatibility replay failed.'})
    finally:
        base['languageChecks']=details;base['resourceCounts']={'productPrefixStateVisits':budget.states,'globalUniqueCandidateInsertions':budget.candidates,'stateCap':2000000,'candidateCap':1000000}
        if started:
            private_json(out/'CANDIDATES.private.json',{'length':26,'literal':sorted(literal),'global':sorted(global_values),'union':sorted(literal|global_values)})
            try:
                evaluation=assess(literal|global_values);base.update(evaluation=evaluation,candidateAssessment='complete-for-saved-set',privateReviewRequired=evaluation['privateReviewRequired'])
                base['cohortCounts']={'literalUniqueShapes':len(literal),'globalUniqueShapes':len(global_values),'combinedUniqueShapes':len(literal|global_values),'overlap':len(literal&global_values)}
            except Exception as error:
                extraction_complete=False;base.update(candidateAssessment='incomplete',validationErrorClass=type(error).__name__)
        base['scopeComplete']=extraction_complete and base['candidateAssessment']=='complete-for-saved-set'
        base['completeNegative']=base['scopeComplete'] and not base['privateReviewRequired']
        base['outcome']=('finding-private-review-required' if base['privateReviewRequired'] else 'no-valid26-record-in-declared-populations') if base['scopeComplete'] else ('finding-private-review-required-incomplete-scope' if base['privateReviewRequired'] else 'inconclusive-control-pin-source-cap-or-execution')
        base.update(completedAtUTC=utc(),negativeCriterion=DEFINITION['negativeCriterion'],limitations=DEFINITION['limitations'])
        private_json(out/'RESULT.json',base)
    print(json.dumps({k:base[k] for k in ['testId','outcome','scopeComplete','completeNegative','privateReviewRequired','scalarDerivations','addressDerivations','networkAddressQueries']}))
    return base


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('Invalid arguments')


def main(argv=None):
    parser=SafeParser(description=__doc__,allow_abbrev=False);actions=parser.add_mutually_exclusive_group(required=True)
    for action in ('definition','self-test','preflight','run'):actions.add_argument('--'+action,action='store_true')
    parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out')
    arguments=list(sys.argv[1:] if argv is None else argv)
    for option in ('--definition','--self-test','--preflight','--run','--protocol','--registration-commit','--out'):
        require(sum(v==option or v.startswith(option+'=') for v in arguments)<=1,'Duplicate argument')
    args=parser.parse_args(arguments)
    if args.definition or args.self_test:
        require(not any((args.protocol,args.registration_commit,args.out)),'Mixed action arguments')
        print(json.dumps(code_definition() if args.definition else self_test(),indent=2));return 0
    if args.preflight:
        require(args.protocol and not args.out,'Preflight requires protocol and no output path')
        protocol,checksum,_=validate_protocol(args.protocol,args.registration_commit,bool(args.registration_commit))
        print(json.dumps({'passed':True,'protocolSha256':checksum,'sourcePins':len(SOURCE_PINS),'scriptPins':len(SCRIPTS),'registrationBytesVerified':bool(args.registration_commit),'targetSourcesParsed':False,'target26ShapesEnumerated':0,'target26Checksums':0}));return 0
    require(args.protocol and args.registration_commit and args.out,'Run requires protocol, registration and fresh private output')
    return 0 if run(args)['scopeComplete'] else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        print(json.dumps({'outcome':'inconclusive-before-execution','scopeComplete':False,'completeNegative':False,'targetScanCompleted':False}),file=sys.stderr);sys.exit(1)
