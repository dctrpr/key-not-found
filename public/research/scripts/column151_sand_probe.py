#!/usr/bin/env python3
"""Fixed column151 Sand readings and literal-format coverage, offline.

Python3.10+ stdlib. Controls read only pinned shared code/support. Actual --run
requires fixed public bytes in a Git registration object. Raw artifacts remain
outside the entire site checkout; stdout contains counts/integrity only.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib, importlib.util, json, os, re, stat, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve()
ROOT=HERE.parent.parent if (HERE.parent/'batch20_common.py').is_file() else HERE.parents[3]/'site/public/research'
ROOT=ROOT.resolve()
PRIMARY='sources/issue24-column151/SOURCE.json'
COMMON='scripts/batch20_common.py'
ENGLISH='scripts/batch20_support/english.txt'
CONTROLS='scripts/batch20_support/controls.json'
PROTOCOL='analysis_outputs/continuation_20261110/column151_sand/PROTOCOL.json'
WITNESSES=('sources/issue24-column151/NATIVE_SOURCE_PROVENANCE.json',
 'sources/issue24-column151/INDEPENDENT_SOURCE_REVIEW.json',
 'sources/issue24-column151/native-contexts/p73-opener.png',
 'sources/issue24-column151/native-contexts/p75-article-title.png',
 'sources/issue24-column151/native-contexts/p78-display-quote.png',
 'sources/issue24-column151/native-contexts/p79-signature.png',
 'sources/printed-lines.json','magazine.pdf')
INPUTS=(PRIMARY,ENGLISH,CONTROLS)+WITNESSES
SCRIPTS=('scripts/column151_sand_probe.py','scripts/verify_column151_sand.py',COMMON)
TEST_ID='column151-sand-three-readings'
BATCH_ID='keiser-column151-sand-three-readings-20261110'
MODEL_ID='issue24-declared-column151-physical-units-v1'
READING_IDS=('COLUMN151-FW-ALL','COLUMN151-ODD-LINES','COLUMN151-EVEN-CONTROL')
NON_MINI_FORMATS=('wif','hex64','bip39','extended_private','bip38','address','sec_public')
MINI_LENGTHS=(22,26,30)
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
COMMON_SHA='48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'
PRIMARY_SHA='24242d3a31469a7bff5765a756fa51f6f8cfbd40f4a51737d852a172cd117c02'
SUPPORT_PINS={ENGLISH:'2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',CONTROLS:'d37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b'}
MAX_INPUT_BYTES=2_000_000
MAX_REGISTERED_BLOB_BYTES=20_000_000
MAX_PROTOCOL_BYTES=1_000_000
MAX_ROW_CODEPOINTS=2000
MAX_SOURCE_CODEPOINTS=100_000
MAX_OUTPUT_CODEPOINTS=200_000
MAX_FORM_CODEPOINTS=400_000
PAGE_COUNTS={'73':2,'75':33,'76':31,'77':32,'78':26,'79':27}
ROLE_COUNTS={'column-name':1,'byline':1,'article-title':1,'body':142,'display-quotation':4,'signature':2}
TOP_KEYS='schemaVersion modelId status preparedAtUTC scope upstreamSources nativeContexts counts normalization orderingPolicy exclusions reviewBoundary rows'.split()
ROW_REQUIRED=('ordinal','id','printedPage','role','printedText')

ROW_LAYOUT=((1, 'p73-opener-name', 73, 'column-name'), (2, 'p73-opener-byline', 73, 'byline'), (3, 'p75_title_0', 75, 'article-title'), (4, 'p75r01', 75, 'body'), (5, 'p75r02', 75, 'body'), (6, 'p75r03', 75, 'body'), (7, 'p75r04', 75, 'body'), (8, 'p75r05', 75, 'body'), (9, 'p75r06', 75, 'body'), (10, 'p75r07', 75, 'body'), (11, 'p75r08', 75, 'body'), (12, 'p75r09', 75, 'body'), (13, 'p75r10', 75, 'body'), (14, 'p75r11', 75, 'body'), (15, 'p75r12', 75, 'body'), (16, 'p75r13', 75, 'body'), (17, 'p75r14', 75, 'body'), (18, 'p75r15', 75, 'body'), (19, 'p75r16', 75, 'body'), (20, 'p75r17', 75, 'body'), (21, 'p75r18', 75, 'body'), (22, 'p75r19', 75, 'body'), (23, 'p75r20', 75, 'body'), (24, 'p75r21', 75, 'body'), (25, 'p75r22', 75, 'body'), (26, 'p75r23', 75, 'body'), (27, 'p75r24', 75, 'body'), (28, 'p75r25', 75, 'body'), (29, 'p75r26', 75, 'body'), (30, 'p75r27', 75, 'body'), (31, 'p75r28', 75, 'body'), (32, 'p75r29', 75, 'body'), (33, 'p75r30', 75, 'body'), (34, 'p75r31', 75, 'body'), (35, 'p75r32', 75, 'body'), (36, 'p76r01', 76, 'body'), (37, 'p76r02', 76, 'body'), (38, 'p76r03', 76, 'body'), (39, 'p76r04', 76, 'body'), (40, 'p76r05', 76, 'body'), (41, 'p76r06', 76, 'body'), (42, 'p76r07', 76, 'body'), (43, 'p76r08', 76, 'body'), (44, 'p76r09', 76, 'body'), (45, 'p76r10', 76, 'body'), (46, 'p76r11', 76, 'body'), (47, 'p76r12', 76, 'body'), (48, 'p76r13', 76, 'body'), (49, 'p76r14', 76, 'body'), (50, 'p76r15', 76, 'body'), (51, 'p76r16', 76, 'body'), (52, 'p76r17', 76, 'body'), (53, 'p76r18', 76, 'body'), (54, 'p76r19', 76, 'body'), (55, 'p76r20', 76, 'body'), (56, 'p76r21', 76, 'body'), (57, 'p76r22', 76, 'body'), (58, 'p76r23', 76, 'body'), (59, 'p76r24', 76, 'body'), (60, 'p76r25', 76, 'body'), (61, 'p76r26', 76, 'body'), (62, 'p76r27', 76, 'body'), (63, 'p76r28', 76, 'body'), (64, 'p76r29', 76, 'body'), (65, 'p76r30', 76, 'body'), (66, 'p76r31', 76, 'body'), (67, 'p77r01', 77, 'body'), (68, 'p77r02', 77, 'body'), (69, 'p77r03', 77, 'body'), (70, 'p77r04', 77, 'body'), (71, 'p77r05', 77, 'body'), (72, 'p77r06', 77, 'body'), (73, 'p77r07', 77, 'body'), (74, 'p77r08', 77, 'body'), (75, 'p77r09', 77, 'body'), (76, 'p77r10', 77, 'body'), (77, 'p77r11', 77, 'body'), (78, 'p77r12', 77, 'body'), (79, 'p77r13', 77, 'body'), (80, 'p77r14', 77, 'body'), (81, 'p77r15', 77, 'body'), (82, 'p77r16', 77, 'body'), (83, 'p77r17', 77, 'body'), (84, 'p77r18', 77, 'body'), (85, 'p77r19', 77, 'body'), (86, 'p77r20', 77, 'body'), (87, 'p77r21', 77, 'body'), (88, 'p77r22', 77, 'body'), (89, 'p77r23', 77, 'body'), (90, 'p77r24', 77, 'body'), (91, 'p77r25', 77, 'body'), (92, 'p77r26', 77, 'body'), (93, 'p77r27', 77, 'body'), (94, 'p77r28', 77, 'body'), (95, 'p77r29', 77, 'body'), (96, 'p77r30', 77, 'body'), (97, 'p77r31', 77, 'body'), (98, 'p77r32', 77, 'body'), (99, 'p78r01', 78, 'body'), (100, 'p78r02', 78, 'body'), (101, 'p78r03', 78, 'body'), (102, 'p78r04', 78, 'body'), (103, 'p78r05', 78, 'body'), (104, 'p78r06', 78, 'body'), (105, 'p78r07', 78, 'body'), (106, 'p78r08', 78, 'body'), (107, 'p78r09', 78, 'body'), (108, 'p78r10', 78, 'body'), (109, 'p78r11', 78, 'body'), (110, 'p78r12', 78, 'body'), (111, 'p78r13', 78, 'body'), (112, 'p78r14', 78, 'body'), (113, 'p78r15', 78, 'body'), (114, 'p78r16', 78, 'body'), (115, 'p78r17', 78, 'body'), (116, 'p78r18', 78, 'body'), (117, 'p78r19', 78, 'body'), (118, 'p78r20', 78, 'body'), (119, 'p78r21', 78, 'body'), (120, 'p78r22', 78, 'body'), (121, 'p78_graphic_0', 78, 'display-quotation'), (122, 'p78_graphic_1', 78, 'display-quotation'), (123, 'p78_graphic_2', 78, 'display-quotation'), (124, 'p78_graphic_3', 78, 'display-quotation'), (125, 'p79r01', 79, 'body'), (126, 'p79r02', 79, 'body'), (127, 'p79r03', 79, 'body'), (128, 'p79r04', 79, 'body'), (129, 'p79r05', 79, 'body'), (130, 'p79r06', 79, 'body'), (131, 'p79r07', 79, 'body'), (132, 'p79r08', 79, 'body'), (133, 'p79r09', 79, 'body'), (134, 'p79r10', 79, 'body'), (135, 'p79r11', 79, 'body'), (136, 'p79r12', 79, 'body'), (137, 'p79r13', 79, 'body'), (138, 'p79r14', 79, 'body'), (139, 'p79r15', 79, 'body'), (140, 'p79r16', 79, 'body'), (141, 'p79r17', 79, 'body'), (142, 'p79r18', 79, 'body'), (143, 'p79r19', 79, 'body'), (144, 'p79r20', 79, 'body'), (145, 'p79r21', 79, 'body'), (146, 'p79r22', 79, 'body'), (147, 'p79r23', 79, 'body'), (148, 'p79r24', 79, 'body'), (149, 'p79r25', 79, 'body'), (150, 'p79_signature_0', 79, 'signature'), (151, 'p79_signature_1', 79, 'signature'))

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


DEFINITION={
 'id':TEST_ID,'title':'Three fixed Sand readings of the declared column151 source',
 'family':'fixed-literal-source-reading','branchId':'text-lines',
 'inputPaths':list(INPUTS),'implementationPaths':list(SCRIPTS),'protocolPath':PROTOCOL,
 'sourceModel':{'id':MODEL_ID,'sha256':PRIMARY_SHA,'physicalUnits':151,'byPrintedPage':PAGE_COUNTS,'byRole':ROLE_COUNTS,
   'selection':'All151 stored units, including2 opener units and149 prior display-inclusive units; no role exclusion.',
   'ordering':'Exact ordinal/id/page/role layout in code; one global index, no page/block reset.',
   'encoding':'Preserve every printedText UTF-8 string; no case, punctuation, Unicode or wrap normalization.',
   'originalTypesettingBytesRecovered':False},
 'readings':[
  {'id':READING_IDS[0],'selectedRowCount':151,'rule':'First whitespace-delimited chunk of each row, retaining punctuation; join with one U+0020.'},
  {'id':READING_IDS[1],'selectedRowCount':76,'rule':'Whole rows at global1-based odd positions1,3,...,151; join with LF.'},
  {'id':READING_IDS[2],'selectedRowCount':75,'rule':'Whole rows at global1-based even positions2,4,...,150; join with LF; parity control.'}],
 'forms':{'rule':'Exactly each unique saved text and its whitespace-only compacted form, deduplicated globally and sorted by Python string order.',
   'maximumReadings':3,'maximumForms':6,'otherTransforms':False},
 'literalValidation':{'commonFormats':list(NON_MINI_FORMATS),'commonImplementationUnchanged':True,
   'commonSha256':COMMON_SHA,'commonOldMinikeyCheckerCalled':False,
   'minikey':{'lengths':list(MINI_LENGTHS),'shape':'Every overlapping embedded S-prefixed Base58 window of exactly22/26/30characters; no outer token boundary requirement.',
     'validation':'SHA256(ASCII(value + question mark))[0]==0;8bit weak check only.',
     'scalarSHA256OfMinikey':False,'recordFingerprint':'Existing batch20 domain-separated record fingerprint; private only.'},
   'zeroCheckBitFormatsAreOnlyShapeOrRangeLeads':True},
 'registrationGate':'Full40hex Git commit; protocol and all source/code/support blobs equal actual registered public/research bytes and current bytes; fixed public executing path.',
 'caps':{'targetJSONAndPrivateArtifactBytes':MAX_INPUT_BYTES,'registeredBlobBytes':MAX_REGISTERED_BLOB_BYTES,
   'protocolBytes':MAX_PROTOCOL_BYTES,'rowCodepoints':MAX_ROW_CODEPOINTS,
   'sourceCodepoints':MAX_SOURCE_CODEPOINTS,'readingCodepoints':MAX_OUTPUT_CODEPOINTS,'totalFormCodepoints':MAX_FORM_CODEPOINTS},
 'outputPolicy':{'rawArtifacts':['READINGS.private.json','READINGS.private.txt','FORMS.private.json','VALIDATION.private.json'],
   'rawOutsideEntireSiteCheckout':True,'directoryMode':'0700','fileMode':'0600',
   'publicReceipt':'Counts, declared scope and whole-artifact integrity only; no values, record fingerprints, addresses, SEC text or locators.',
   'keyOutputsPublic':False,'semanticConclusionComputed':False},
 'activityBoundary':{'newSelectors':0,'reversals':0,'initialsOrFinals':0,'arbitraryScalarWindows':0,
   'proseToKeyHashes':0,'minikeyScalarHashes':0,'addressDerivations':0,'seedDerivations':0,'childKeyDerivations':0,'networkQueries':0,'transactions':0},
 'limitations':['This is a declared151-unit transcription/ordering model, not original typesetting bytes or authenticated extraction instructions.',
   'Three readings and fixed literal-format gates do not exclude readable messages, other readings, unknown record families or the whole column.',
   'Weak minikey checksum, scalar-range-only hex and on-curve SEC matches are leads, not solutions or prize/funding proof.',
   'Registration check is a local Git-object byte check; prior remote publication is separately established by the operator.']}


def validate_source(data):
    require(isinstance(data,dict) and set(data)==set(TOP_KEYS),'Source top schema changed')
    require(type(data['schemaVersion']) is int and data['schemaVersion']==1 and data['modelId']==MODEL_ID,'Source model changed')
    rows=data['rows'];require(isinstance(rows,list) and len(rows)==151,'Source population changed')
    require(isinstance(data['normalization'],dict) and data['normalization'].get('encoding')=='UTF-8','Source encoding changed')
    total=0
    for row,expected in zip(rows,ROW_LAYOUT):
        require(isinstance(row,dict) and set(ROW_REQUIRED)<=set(row),'Source row schema changed')
        require(type(row['ordinal']) is int and type(row['printedPage']) is int,'Source ordinal type changed')
        require(isinstance(row['id'],str) and isinstance(row['role'],str),'Source identity type changed')
        require(tuple(row[k] for k in ROW_REQUIRED[:-1])==expected,'Source row order/identity changed')
        text=row['printedText'];require(isinstance(text,str) and 0<len(text)<=MAX_ROW_CODEPOINTS,'Source text length invalid')
        require(text==text.strip(' ') and '  ' not in text,'Source spacing changed')
        require(all(ch==' ' or (ch.isprintable() and not ch.isspace()) for ch in text),'Source row control/whitespace changed')
        text.encode('utf-8');total+=len(text)
    require(total<=MAX_SOURCE_CODEPOINTS,'Source codepoint cap exceeded')
    require(dict(Counter(str(r['printedPage']) for r in rows))==PAGE_COUNTS,'Source page counts changed')
    require(dict(Counter(r['role'] for r in rows))==ROLE_COUNTS,'Source role counts changed')
    expected_counts={'physicalUnits':151,'newOpenerUnits':2,'reusedBodyUnits':142,'reusedOptionalDisplayUnits':7,'nonbodyUnits':9,'byPrintedPage':PAGE_COUNTS,'byRole':ROLE_COUNTS}
    require(canonical(data['counts'])==canonical(expected_counts),'Source declared counts changed')
    return rows


def literal_readings(rows):
    texts=[r['printedText'] for r in rows]
    return [{'id':READING_IDS[0],'selectedRowCount':len(texts),'selectedRowIds':[r['id'] for r in rows],
       'text':' '.join(t.split(maxsplit=1)[0] for t in texts)},
      {'id':READING_IDS[1],'selectedRowCount':len(texts[::2]),'selectedRowIds':[r['id'] for r in rows[::2]],'text':'\n'.join(texts[::2])},
      {'id':READING_IDS[2],'selectedRowCount':len(texts[1::2]),'selectedRowIds':[r['id'] for r in rows[1::2]],'text':'\n'.join(texts[1::2])}]


def make_forms(readings):
    require(len(readings)<=3 and all(isinstance(r,dict) and isinstance(r.get('text'),str) for r in readings),'Reading schema changed')
    texts={r['text'] for r in readings};forms=sorted(texts|{re.sub(r'\s','',text) for text in texts})
    require(len(forms)<=6 and sum(map(len,forms))<=MAX_FORM_CODEPOINTS,'Form population cap exceeded')
    return forms


def load_common():
    require(digest(capped_read(ROOT/COMMON,MAX_INPUT_BYTES))==COMMON_SHA,'Unchanged common validator required')
    for relative,pin in SUPPORT_PINS.items():require(digest(capped_read(ROOT/relative,MAX_INPUT_BYTES))==pin,'Support byte pin changed')
    spec=importlib.util.spec_from_file_location('column151_common',ROOT/COMMON)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    require(tuple(f for f in mod.ALL_FORMATS if f!='minikey')==NON_MINI_FORMATS,'Common format population changed')
    return mod


def minikey_shape(value):
    return isinstance(value,str) and len(value) in MINI_LENGTHS and value.startswith('S') and all(c in B58 for c in value)


def minikey_valid(value):
    return minikey_shape(value) and hashlib.sha256((value+'?').encode('ascii')).digest()[0]==0


def scan_minikey_forms(forms,common):
    shapes={n:set() for n in MINI_LENGTHS};occurrences={str(n):0 for n in MINI_LENGTHS}
    for text in forms:
        for start,char in enumerate(text):
            if char!='S':continue
            for length in MINI_LENGTHS:
                value=text[start:start+length]
                if len(value)==length and minikey_shape(value):occurrences[str(length)]+=1;shapes[length].add(value)
    records=[]
    for length in MINI_LENGTHS:
        for value in sorted(shapes[length]):
            if minikey_valid(value):records.append({'format':'minikey','length':length,'checkBits':8,'private':True,
              'fingerprint':common.fingerprint('minikey',value.encode('ascii')),'value':value})
    evaluation={'lengths':list(MINI_LENGTHS),'shapeCounts':occurrences,
      'uniqueShapeCounts':{str(n):len(shapes[n]) for n in MINI_LENGTHS},
      'checksumCalls':sum(map(len,shapes.values())),
      'validCounts':{str(n):sum(r['length']==n for r in records) for n in MINI_LENGTHS},
      'privateReviewRequired':bool(records),'fingerprintRule':deepcopy(common.FINGERPRINT_RULE)}
    return evaluation,[{'length':n,'value':v} for n in MINI_LENGTHS for v in sorted(shapes[n])],records


def evaluate(readings,common):
    forms=make_forms(readings)
    common7=common.scan_streams(readings,formats=NON_MINI_FORMATS)
    require(common7['uniqueFormCount']==len(forms) and tuple(common7['formats'])==NON_MINI_FORMATS,'Common form/format contract changed')
    mini,shapes,records=scan_minikey_forms(forms,common)
    return forms,{'common7':common7,'minikey':mini,'minikeyShapeValues':shapes,'minikeyValidRecords':records}


def validate_protocol_header(protocol,registration):
    require(isinstance(registration,str) and re.fullmatch('[0-9a-f]{40}',registration),'Full registration commit required')
    require(isinstance(protocol,dict) and {'version','batchId','test','sourceHashes','scriptHashes'}<=set(protocol),'Protocol schema changed')
    require(type(protocol['version']) is int and protocol['version']==1 and protocol['batchId']==BATCH_ID,'Protocol identity changed')
    require(canonical(protocol['test'])==canonical(code_definition()),'Protocol code definition changed')
    for field,paths in [('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)]:
        require(isinstance(protocol[field],dict) and set(protocol[field])==set(paths),'Protocol pin population changed')
        require(all(isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) for v in protocol[field].values()),'Invalid protocol byte pin')
    require(protocol['scriptHashes'][COMMON]==COMMON_SHA,'Common pin differs')
    require(protocol['sourceHashes'][PRIMARY]==PRIMARY_SHA,'Accepted source pin differs')
    require(all(protocol['sourceHashes'][p]==v for p,v in SUPPORT_PINS.items()),'Support pin differs')
    if 'registeredAtUTC' in protocol:
        parsed=datetime.fromisoformat(protocol['registeredAtUTC'].replace('Z','+00:00'))
        require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds()==0,'Registration metadata must be UTC')


def validate_protocol(path,registration):
    require(HERE==(ROOT/SCRIPTS[0]).resolve(),'Actual run requires fixed public implementation path')
    protocol_path=Path(path).expanduser().resolve(strict=True)
    require(protocol_path==(ROOT/PROTOCOL).resolve() and protocol_path.is_relative_to(ROOT),'Fixed public protocol required')
    raw=capped_read(protocol_path,MAX_PROTOCOL_BYTES);protocol=load_json(raw);validate_protocol_header(protocol,registration)
    def current(relative):
        file=(ROOT/relative).resolve(strict=True);require(file.is_relative_to(ROOT),'Research path escape')
        return capped_read(file,MAX_INPUT_BYTES if relative==PRIMARY else MAX_REGISTERED_BLOB_BYTES)
    files=verify_payloads(protocol,raw,registration,current,registered_blob)
    require(files[SCRIPTS[0]]==HERE.read_bytes(),'Executing script differs from registration')
    return protocol,raw,files


def private_output(value):
    raw=Path(value).expanduser();require(not raw.exists() and not raw.is_symlink(),'Fresh private output required')
    out=raw.resolve();require(not any(p.casefold()=='public' for p in out.parts) and not out.is_relative_to(ROOT.parent.parent),'Output outside entire site checkout required')
    require(out.parent.is_dir() and stat.S_IMODE(out.parent.stat().st_mode)==0o700,'Private0700 output parent required')
    return out


def private_write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.fchmod(fd,0o600)
    with os.fdopen(fd,'wb') as handle:handle.write(raw)


def safe_result(protocol,pbytes,registration,readings,validation,started,artifacts):
    common7=validation['common7'];mini=validation['minikey'];valid=dict(common7['validCounts']);valid['minikey']=sum(mini['validCounts'].values())
    return {'version':1,'testId':TEST_ID,'batchId':BATCH_ID,'status':'registered-literal-scope-complete',
      'startedAtUTC':started,'completedAtUTC':utc(),'registrationCommit':registration,'protocolSha256':digest(pbytes),
      'sourceHashes':deepcopy(protocol['sourceHashes']),'scriptHashes':deepcopy(protocol['scriptHashes']),
      'sourceModel':{'id':MODEL_ID,'physicalUnits':151,'byPrintedPage':PAGE_COUNTS,'originalTypesettingBytesRecovered':False},
      'scopeComplete':True,'readingsGenerated':True,'literalFormatGatesComplete':True,'semanticReviewComplete':False,
      'privateReviewRequired':any(valid.values()),
      'counts':{'readings':3,'selectedRows':[r['selectedRowCount'] for r in readings],
        'submittedCodepoints':sum(len(r['text']) for r in readings),'uniqueStreams':common7['uniqueStreamCount'],
        'uniqueForms':common7['uniqueFormCount'],'commonShapeCounts':common7['shapeCounts'],
        'commonUniqueShapeCounts':common7['uniqueShapeCounts'],'commonExecutionCount':common7['executionCount'],
        'minikeyShapeCountsByLength':mini['shapeCounts'],'minikeyUniqueShapesByLength':mini['uniqueShapeCounts'],
        'minikeyQuestionmarkChecksumCalls':mini['checksumCalls'],'minikeyValidCountsByLength':mini['validCounts'],
        'validCounts':valid,'totalValidRecords':sum(valid.values())},
      'privateArtifactIntegrity':artifacts,'activity':deepcopy(DEFINITION['activityBoundary']),
      'limitations':deepcopy(DEFINITION['limitations'])}


def text_export(readings):
    return 'KEY404 / registered column151 Sand readings\n\n'+'\n\n'.join('['+r['id']+']\nSelected rows: '+str(r['selectedRowCount'])+'\n'+r['text'] for r in readings)+'\n'


def run(protocol_path,registration,out_value):
    started=utc();out=private_output(out_value)
    protocol,pbytes,files=validate_protocol(protocol_path,registration)
    rows=validate_source(load_json(files[PRIMARY]));readings=literal_readings(rows)
    require([r['selectedRowCount'] for r in readings]==[151,76,75] and len(readings)==3,'Reading population changed')
    require(sum(len(r['text']) for r in readings)<=MAX_OUTPUT_CODEPOINTS,'Reading codepoint cap exceeded')
    common=load_common();forms,validation=evaluate(readings,common)
    payloads={'READINGS.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,'sourceSha256':protocol['sourceHashes'][PRIMARY],'readings':readings}),
      'READINGS.private.txt':text_export(readings).encode('utf-8'),
      'FORMS.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,'forms':forms}),
      'VALIDATION.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,**validation})}
    require(all(len(v)<=MAX_INPUT_BYTES for v in payloads.values()),'Private artifact byte cap exceeded')
    integrity={name:digest(raw) for name,raw in payloads.items()}
    result=safe_result(protocol,pbytes,registration,readings,validation,started,integrity)
    out.mkdir(mode=0o700);os.chmod(out,0o700)
    try:
        for name,raw in payloads.items():private_write(out/name,raw)
        private_write(out/'RESULT.json',json_bytes(result))
    except Exception:
        try:private_write(out/'FAILURE.json',json_bytes({'version':1,'testId':TEST_ID,'scopeComplete':False,'status':'inconclusive-private-write-failure'}))
        except Exception:pass
        raise
    return result


def synthetic_source():
    data={key:None for key in TOP_KEYS}
    data.update(schemaVersion=1,modelId=MODEL_ID,status='synthetic-control',preparedAtUTC='control',
      normalization={'encoding':'UTF-8'},counts={'physicalUnits':151,'newOpenerUnits':2,'reusedBodyUnits':142,
      'reusedOptionalDisplayUnits':7,'nonbodyUnits':9,'byPrintedPage':deepcopy(PAGE_COUNTS),'byRole':deepcopy(ROLE_COUNTS)})
    data['rows']=[dict(zip(ROW_REQUIRED,layout+(f'Synthetic{i:03d}, literal-{i}',))) for i,layout in enumerate(ROW_LAYOUT,1)]
    return data


def synthetic_minikey(length):
    for counter in range(65536):
        number=counter;suffix=''
        while number:number,remainder=divmod(number,58);suffix=B58[remainder]+suffix
        value='S'+'2'*(length-5)+(suffix or '1').rjust(4,'1')
        if minikey_valid(value):return value
    raise AssertionError('Synthetic checksum control not found')


def self_test():
    checks=0
    def reject(call):
        nonlocal checks
        try:call()
        except (ValueError,UnicodeError):checks+=1
        else:raise AssertionError('Expected control rejection')
    toy=[{'id':f't{i}','printedText':text} for i,text in enumerate(['OVERDOSE','By Tester,','?! punctuation','A B-','♥ Love','line— End','“Case” preserved'])]
    oracle=[{'id':READING_IDS[0],'selectedRowCount':7,'selectedRowIds':['t0','t1','t2','t3','t4','t5','t6'],
       'text':'OVERDOSE By ?! A ♥ line— “Case”'},
      {'id':READING_IDS[1],'selectedRowCount':4,'selectedRowIds':['t0','t2','t4','t6'],'text':'OVERDOSE\n?! punctuation\n♥ Love\n“Case” preserved'},
      {'id':READING_IDS[2],'selectedRowCount':3,'selectedRowIds':['t1','t3','t5'],'text':'By Tester,\nA B-\nline— End'}]
    assert literal_readings(toy)==oracle;checks+=1
    source=synthetic_source();rows=validate_source(source);readings=literal_readings(rows)
    assert [r['selectedRowCount'] for r in readings]==[151,76,75]
    assert readings[1]['selectedRowIds'][1]=='p75_title_0' and readings[2]['selectedRowIds'][0]=='p73-opener-byline';checks+=1
    assert set(make_forms([{'id':'a','text':'a A\n♥'},{'id':'b','text':'a A\n♥'}]))=={'a A\n♥','aA♥'};checks+=1
    for text in ['', ' leading','trailing ','two  spaces','tab\tword','line\nword','return\rword','non\u00a0breaking','zero\u200bwidth']:
        bad=deepcopy(source);bad['rows'][0]['printedText']=text;reject(lambda b=bad:validate_source(b))
    for key,value in [('ordinal',True),('id','unexpected'),('printedPage',75),('role','body')]:
        bad=deepcopy(source);bad['rows'][0][key]=value;reject(lambda b=bad:validate_source(b))
    for kind in ['remove','swap','count','model','long']:
        bad=deepcopy(source)
        if kind=='remove':bad['rows'].pop()
        elif kind=='swap':bad['rows'][0],bad['rows'][1]=bad['rows'][1],bad['rows'][0]
        elif kind=='count':bad['counts']['physicalUnits']=150
        elif kind=='model':bad['modelId']='other'
        else:bad['rows'][0]['printedText']='x'*(MAX_ROW_CODEPOINTS+1)
        reject(lambda b=bad:validate_source(b))
    reject(lambda:load_json(b'{"a":1,"a":2}'));reject(lambda:load_json(b'{"a":NaN}'))
    common=load_common();controls=load_json(capped_read(ROOT/CONTROLS,MAX_INPUT_BYTES))
    _,indexes=common.wordlist()
    fixture_keys={'bip39':'bip39_valid','extended_private':'bip32_extended_private','bip38':'bip38_encrypted_private',
      'address':'legacy_address','sec_public':'sec_compressed_generator'}
    for kind,key in fixture_keys.items():assert common.validate_record(kind,controls[key],indexes);checks+=1
    payload=b'\x80'+bytes(31)+b'\x01\x01'
    wif=common.b58encode(payload+hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4])
    assert common.validate_record('wif',wif) and common.validate_record('hex64','0'*63+'1');checks+=1
    for key in ['segwit_v0','segwit_v1']:assert common.validate_record('address',controls[key]);checks+=1
    assert common.validate_record('sec_public',controls['sec_uncompressed_generator']);checks+=1
    published22='SzavMBLoXU6kDrqtUVmffv';published30='S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'
    original_hash=hashlib.sha256;original_shape=common.shape_values;original_validate=common.validate_record
    forbidden={'bareMinikeyHashes':0,'oldMinikeyCalls':0}
    def checked_hash(data=b'',*args,**kwargs):
        raw=bytes(data)
        if len(raw) in MINI_LENGTHS and raw.startswith(b'S') and all(chr(c) in B58 for c in raw):
            forbidden['bareMinikeyHashes']+=1;raise AssertionError('Bare minikey hash forbidden')
        return original_hash(data,*args,**kwargs)
    def checked_shape(kind,*args,**kwargs):
        if kind=='minikey':forbidden['oldMinikeyCalls']+=1;raise AssertionError('Old minikey checker forbidden')
        return original_shape(kind,*args,**kwargs)
    def checked_validate(kind,*args,**kwargs):
        if kind=='minikey':forbidden['oldMinikeyCalls']+=1;raise AssertionError('Old minikey checker forbidden')
        return original_validate(kind,*args,**kwargs)
    hashlib.sha256=checked_hash;common.shape_values=checked_shape;common.validate_record=checked_validate
    try:
        synthetic26=synthetic_minikey(26)
        assert minikey_valid(published22) and minikey_valid(published30) and minikey_valid(synthetic26);checks+=1
        tail22,tail22shapes,tail22records=scan_minikey_forms([published22],common)
        assert tail22['shapeCounts']=={'22':1,'26':0,'30':0} and tail22['uniqueShapeCounts']=={'22':1,'26':0,'30':0}
        assert tail22['validCounts']=={'22':1,'26':0,'30':0} and [(r['length'],len(r['value'])) for r in tail22records]==[(22,22)]
        assert tail22shapes==[{'length':22,'value':published22}];checks+=1
        tail26,tail26shapes,tail26records=scan_minikey_forms([synthetic26],common)
        assert tail26['shapeCounts']=={'22':1,'26':1,'30':0} and tail26['uniqueShapeCounts']=={'22':1,'26':1,'30':0}
        assert tail26['validCounts']['26']==1 and tail26['validCounts']['30']==0
        assert all(item['length']==len(item['value']) for item in tail26shapes+tail26records);checks+=1
        repeated22,_,_=scan_minikey_forms(['S'*22],common)
        repeated26,_,_=scan_minikey_forms(['S'*26],common)
        assert repeated22['shapeCounts']=={'22':1,'26':0,'30':0}
        assert repeated26['shapeCounts']=={'22':5,'26':1,'30':0}
        assert repeated26['uniqueShapeCounts']=={'22':1,'26':1,'30':0};checks+=1
        for value in [published30[:21],published30+'1','s'+synthetic26[1:],'Ｓ'+synthetic26[1:]]:
            assert not minikey_shape(value);checks+=1
        for badchar in '0OIl':assert not minikey_shape(synthetic26[:5]+badchar+synthetic26[6:]);checks+=1
        invalid=next(synthetic26[:-1]+c for c in B58 if not minikey_valid(synthetic26[:-1]+c))
        assert minikey_shape(invalid) and not minikey_valid(invalid);checks+=1
        overlap,shapevalues,_=scan_minikey_forms(['SS'+'1'*40],common)
        assert overlap['shapeCounts']=={'22':2,'26':2,'30':2} and len(shapevalues)==6;checks+=1
        controltext=' || '.join([wif,'0'*63+'1',controls['bip39_valid'],controls['bip32_extended_private'],
          controls['bip38_encrypted_private'],controls['legacy_address'],controls['segwit_v0'],controls['segwit_v1'],
          controls['sec_compressed_generator'],controls['sec_uncompressed_generator'],published22,synthetic26,published30])
        controlreadings=[{'id':'fixture-a','text':controltext},{'id':'fixture-b','text':synthetic26[:12]+' '+synthetic26[12:]}]
        forms,validation=evaluate(controlreadings,common)
        assert all(validation['common7']['validCounts'][k]>=1 for k in NON_MINI_FORMATS);checks+=1
        assert all(validation['minikey']['validCounts'][str(n)]>=1 for n in MINI_LENGTHS);checks+=1
        assert synthetic26 in {r['value'] for r in validation['minikeyValidRecords']};checks+=1
        assert not any(forbidden.values());checks+=1
    finally:
        hashlib.sha256=original_hash;common.shape_values=original_shape;common.validate_record=original_validate
    protocol={'version':1,'batchId':BATCH_ID,'test':code_definition(),
      'sourceHashes':{p:'0'*64 for p in INPUTS},'scriptHashes':{p:'1'*64 for p in SCRIPTS}}
    protocol['sourceHashes'].update(SUPPORT_PINS);protocol['sourceHashes'][PRIMARY]=PRIMARY_SHA;protocol['scriptHashes'][COMMON]=COMMON_SHA
    commit='a'*40;validate_protocol_header(protocol,commit);checks+=1
    reject(lambda:validate_protocol_header(protocol,'short'))
    for key in ['sourceHashes','scriptHashes']:
        bad=deepcopy(protocol);bad[key].pop(next(iter(bad[key])));reject(lambda b=bad:validate_protocol_header(b,commit))
    bad=deepcopy(protocol);bad['test']['readings'][0]['selectedRowCount']=149;reject(lambda:validate_protocol_header(bad,commit))
    files={p:('synthetic-file '+p).encode() for p in INPUTS+SCRIPTS};mock=deepcopy(protocol)
    for key,paths in [('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)]:
        for p in paths:mock[key][p]=digest(files[p])
    pbytes=b'synthetic-protocol';blobs={**files,PROTOCOL:pbytes};calls=[]
    def blob(commit,path):calls.append(path);return blobs[path]
    assert verify_payloads(mock,pbytes,commit,files.__getitem__,blob)==files
    assert calls[0]==PROTOCOL and len(calls)==1+len(INPUTS)+len(SCRIPTS);checks+=1
    reject(lambda:verify_payloads(mock,b'wrong-protocol',commit,files.__getitem__,blob))
    damaged=dict(files);damaged[PRIMARY]=b'changed-source';reject(lambda:verify_payloads(mock,pbytes,commit,damaged.__getitem__,blob))
    safe=safe_result(protocol,b'synthetic-protocol',commit,readings,validation,'control-start',{'fixture':'2'*64})
    safe_text=json.dumps(safe)
    assert all(v not in safe_text for v in [published22,published30,synthetic26,wif,controls['legacy_address'],controls['sec_compressed_generator']])
    assert all(k not in safe_text for k in ['selectedRowIds','fingerprint','publicKey','printedText']);checks+=1
    with tempfile.TemporaryDirectory(prefix='column151-control-') as temp:
        parent=Path(temp);os.chmod(parent,0o700);new=private_output(parent/'fresh');new.mkdir(mode=0o700)
        private_write(new/'control.txt',b'control');assert stat.S_IMODE(new.stat().st_mode)==0o700 and stat.S_IMODE((new/'control.txt').stat().st_mode)==0o600;checks+=1
        reject(lambda:private_output(new));(parent/'public').mkdir();reject(lambda:private_output(parent/'public'/'fresh'))
        reject(lambda:private_output(ROOT.parent.parent/'private-control-output'))
        try:private_write(new/'control.txt',b'replace')
        except FileExistsError:checks+=1
        else:raise AssertionError('Existing output overwritten')
    return {'version':1,'testId':TEST_ID,'passed':True,'checks':checks,
      'controls':'Hand-written chunk/parity oracle; synthetic151source/registration/privacy guards; published7-format controls; published22/30+synthetic26 minikey controls.',
      'targetSourceOpened':False,'targetReadingsGenerated':False,'oldMinikeyCheckerCalls':forbidden['oldMinikeyCalls'],
      'bareMinikeyHashes':forbidden['bareMinikeyHashes'],'addressDerivations':0,'seedDerivations':0,'networkQueries':0}


class QuietParser(argparse.ArgumentParser):
    def error(self,message):raise ValueError('Invalid command arguments')


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    flags=('--definition','--self-test','--run','--protocol','--registration-commit','--out')
    require(all(argv.count(f)<=1 for f in flags),'Duplicate command argument')
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
        print(json.dumps({'version':1,'testId':TEST_ID,'status':'inconclusive','scopeComplete':False,
          'error':'Validation or execution failed; no result or semantic conclusion.'}),file=sys.stderr)
        raise SystemExit(1)
