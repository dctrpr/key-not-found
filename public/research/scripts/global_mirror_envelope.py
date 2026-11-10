#!/usr/bin/env python3
"""Registered global mirror-boundary language audit; offline standard library.

No target extraction or validation occurs at import, --list or --self-test.
A target run requires public protocol/source/code pins and a fresh private out.
The audit covers candidate SETS over the full DAG language, not occurrences or
an expanded list of millions of full readings. No wallet or network operations.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,re,sys
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
SOURCE_MODEL='analysis_outputs/continuation_20261110/mirror_boundary_review/SOURCE_MODEL.json'
WORDS='sources/word-geometry-20261110.json'
PRINTED='sources/printed-lines.json'
MASK_MODEL='analysis_outputs/3d_article_map/article_3d_map_data.json'
INVERTED='analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json'
ENGLISH='scripts/batch20_support/english.txt'
CONTROLS='scripts/batch20_support/controls.json'
INPUTS=(SOURCE_MODEL,WORDS,PRINTED,MASK_MODEL,INVERTED,ENGLISH,CONTROLS)
SCRIPTS=('scripts/global_mirror_envelope.py','scripts/global_mirror_dag.py','scripts/batch20_common.py')
FORMATS=('wif','minikey','hex64','bip39')
PAIRS=((76,77),(77,76),(78,79),(79,78))
FAMILY_COUNTS={('orange','leftmost'):27095040,('orange','rightmost'):15482880,
 ('black','leftmost'):139968,('black','rightmost'):629856}
MAX_STATES=2000000
MAX_CANDIDATES=1000000
DEFINITION={
 'id':'mirror-global-envelope','title':'Global mirror boundary language audit',
 'family':'mirror-firstword-global-uncertainty-envelope','branchId':'mirror-layout',
 'inputPaths':list(INPUTS),'implementationPaths':list(SCRIPTS),
 'parameters':{
  'pairOrder':[list(p) for p in PAIRS],'sameColorAndEdgeAcrossPairs':True,
  'maskClasses':['orange','black'],'wordEdges':['leftmost','rightmost'],
  'rowOrders':['forward','reverse-entire-concatenated-row-sequence'],
  'projections':['words-spaced','words-joined','initials'],
  'forms':['exact','whitespace-only-compacted'],'formats':list(FORMATS),
  'sourceModel':'Exact frozen row word/omission choices in SOURCE_MODEL.json; no new geometry fit.',
  'sourceModelChecks':'All 16 pair/color/edge scopes, printed row order, canonical word IDs, membership states and first/last options verified; masks retained as pinned provenance.',
  'sourceTokenInvariant':'Every possible selected token must be a nonempty string, have an alphanumeric code point, and contain no Unicode whitespace; violation is inconclusive.',
  'formLanguageReduction':'Compacted spaced equals joined; joined and initials contain no whitespace. Thus 24 language descriptors cover the exact/compact union. They need not be disjoint.',
  'globalFamilies':4,'languageDescriptors':24,'globalSelectionPaths':43347744,
  'theoreticalLabeledReadings':260086464,'fullReadingExpansionPerformed':False,
  'candidateSemantics':'Set union of reachable shaped records across all modeled paths/languages. No occurrence counts, unique-text counts or unique-form counts are claimed.',
  'wifShape':'Embedded [5KL] plus Base58 characters, total 51/52.',
  'minikeyShape':'Embedded S plus Base58 characters, total 22/30.',
  'hexShape':'Exactly 64hex code points with realizable nonhex/start and nonhex/EOF boundaries.',
  'bip39Tokenization':'Lowercase unfiltered ASCII lexical tokens matching [A-Za-z0-9]+ with internal straight/curly apostrophe joins; ordinary punctuation boundaries; invalid decoded group ␞ is a hard region boundary.',
  'bip39Windows':[12,15,18,21,24],
  'maximumProductPrefixStateVisits':MAX_STATES,'maximumUniqueCandidateInsertions':MAX_CANDIDATES,
  'capPolicy':'Any cap exceedance makes scope incomplete and result inconclusive; partial candidates remain private and are separately assessed.',
  'rawAsciiScalars':False,'proseHashWrappers':False,'networkQueries':0,'transactions':0,
 },
 'controls':['846-exact-synthetic-DAG-vs-exhaustive-candidate-set-comparisons',
  'conditional-space-and-row-omission','reverse-entire-sequence',
  'embedded-WIF-minikey','64hex-left-right-boundaries',
  'BIP39-dictionary-prefix-vs-word','BIP39-apostrophe-lookahead-and-hard-barrier',
  'state-cap-fails-inconclusive','candidate-cap-preserves-private-partial-set','source-option-structure','shared-format-controls'],
 'negativeCriterion':'A complete zero-valid-record result excludes only the four declared literal formats from the exact registered global modeled language union at the pinned bytes. It does not calibrate scan errors, establish a creator-selected stencil, or exhaust mirror/first-word ciphers.',
 'limitations':['The frozen source guard squares and rectangle masks are heuristic investigator conventions, not calibrated physical error bounds or creator instructions.',
  'Independent memberships admit physically inconsistent choices. This enlarges the tested set; a weak checksum match has no implied intentionality or likelihood.',
  'Results count unique shaped values and validated records, not expanded full readings, unique strings, occurrences or independent theories.',
  'Other page orders, masks, selection conventions, projections, encodings and wallet interpretations remain outside this exact test.']}

def utc():return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def sha(data):return hashlib.sha256(data).hexdigest()
def require(condition,message):
 if not condition:raise ValueError(message)
def read_json(path):return json.loads(path.read_text(encoding='utf-8'))
def private_json(path,value):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',encoding='utf-8') as out:
  json.dump(value,out,indent=2);out.write('\n')

def expected_options(states,edge):
 require(edge in ('leftmost','rightmost'),'Unexpected edge')
 require(all(x in ('in','out','unknown') for x in states),'Unexpected membership state')
 order=range(len(states)) if edge=='leftmost' else range(len(states)-1,-1,-1)
 result=[]
 for i in order:
  if states[i]=='out':continue
  result.append(i)
  if states[i]=='in':return result
 return result+[None]

def checked_source_families():
 """Source/count/length checks only. Does not inspect candidate shapes.

 The numeric/word-ID model is the pinned source of selection alternatives.
 Raw mask inputs are pinned provenance, not newly fitted or reinterpreted here.
 """
 printed=read_json(ROOT/PRINTED)['rows'];geometry=read_json(ROOT/WORDS)
 require(len(printed)==142 and all(r['section']=='body' for r in printed),'Unexpected printed source rows')
 counts={p:sum(r['page']==p for r in printed) for p in range(75,80)}
 require(counts=={75:32,76:31,77:32,78:22,79:25},'Unexpected printed page counts')
 row_order={p:[r['id'] for r in printed if r['page']==p] for p in range(75,80)}
 byrow={};word_values={}
 for row in geometry['rows']:
  require(row['id'] not in byrow,'Duplicate canonical row ID')
  words=[w for w in row['words'] if any(c.isalnum() for c in w.get('text',''))]
  require(row.get('status')=='complete' and all(w.get('verified') is True for w in words),'Incomplete canonical source geometry')
  require(all(isinstance(w.get('box'),list) and len(w['box'])==4 and all(math.isfinite(v) for v in w['box']) for w in words),'Invalid source word boxes')
  words=sorted(words,key=lambda w:(w['box'][0]+w['box'][2])/2)
  byrow[row['id']]=[w['id'] for w in words]
  for w in words:
   require(w['id'] not in word_values,'Duplicate canonical word ID')
   word_values[w['id']]=w['text']
 require(len(byrow)==142 and len(word_values)==1243,'Canonical source coverage changed')
 require(set(byrow)=={r['id'] for r in printed},'Canonical/printed row identities differ')
 model=read_json(ROOT/SOURCE_MODEL);lookup={}
 require(isinstance(model,list) and len(model)==16,'Unexpected frozen source scopes')
 for scope in model:
  key=(scope['source'],scope['target'],scope['color'],scope['edge'])
  require(key not in lookup and key[:2] in PAIRS and key[2] in ('orange','black') and key[3] in ('leftmost','rightmost'),'Unexpected source scope')
  require(scope['id']==f'{key[0]}-to-{key[1]}:{key[2]}:{key[3]}','Source scope ID mismatch')
  require([r['rowId'] for r in scope['rows']]==row_order[key[1]],'Source row ordering changed')
  rows=[]
  for r in scope['rows']:
   require(r['wordIds']==byrow[r['rowId']],'Source word ordering/identity mismatch')
   require(len(r['states'])==len(r['wordIds']),'Source state count mismatch')
   require(r['options']==expected_options(r['states'],key[3]),'Source selected-edge options mismatch')
   choices=[]
   for i in r['options']:
    if i is None:choices.append(None);continue
    require(isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(r['wordIds']),'Invalid selected source index')
    token=word_values[r['wordIds'][i]]
    require(isinstance(token,str) and bool(token) and any(c.isalnum() for c in token) and not any(c.isspace() for c in token),'Source token invariant failed')
    choices.append(token)
   rows.append(choices)
  require(math.prod(len(r) for r in rows)==scope['selectionPaths'],'Pair-local path count mismatch')
  lookup[key]=rows
 expected={(a,b,c,e) for a,b in PAIRS for c in ('orange','black') for e in ('leftmost','rightmost')}
 require(set(lookup)==expected,'Missing source scope')
 families=[]
 for color in ('orange','black'):
  for edge in ('leftmost','rightmost'):
   rows=[row for a,b in PAIRS for row in lookup[a,b,color,edge]]
   paths=math.prod(len(r) for r in rows)
   require(len(rows)==110 and paths==FAMILY_COUNTS[color,edge],'Global family structure/count mismatch')
   selected_min=sum(min(v is not None for v in row) for row in rows)
   selected_max=sum(max(v is not None for v in row) for row in rows)
   families.append({'id':color+':'+edge,'color':color,'edge':edge,'rows':rows,'selectionPaths':paths,
    'rowCount':len(rows),'selectedWordsMin':selected_min,'selectedWordsMax':selected_max})
 require(sum(f['selectionPaths'] for f in families)==43347744,'Global source universe changed')
 return families

def public_source_counts(families):
 return {'globalFamilies':4,'globalSelectionPaths':43347744,'theoreticalLabeledReadings':260086464,
  'languageDescriptors':24,'expandedFullReadings':0,
  'scopeCounts':[{k:v for k,v in f.items() if k!='rows'} for f in families],
  'sourceTokenInvariantVerified':True,
  'candidateCountPolicy':'Unique shaped value sets only; no occurrence or unique-text/form cardinalities.'}

def self_test():
 import batch20_common as common
 from global_mirror_dag import self_test as dag_self_test
 require(expected_options(['out','unknown','in','unknown'],'leftmost')==[1,2],'First selection control')
 require(expected_options(['unknown','in','unknown','out'],'rightmost')==[2,1],'Last selection control')
 require(expected_options(['out','unknown'],'leftmost')==[1,None],'Omission control')
 return {'passed':True,'dag':dag_self_test(common),'shared':common.self_test(),
  'sourceOptionStructureControls':3,'targetInputsRead':False,'targetShapeChecks':0,'targetChecksumChecks':0,'networkQueries':0}

def validate_protocol(protocol,registration_commit):
 require(protocol.get('version')==1 and protocol.get('batchId')=='keiser-global-mirror-envelope-20261110','Unexpected registered protocol')
 require(re.fullmatch(r'[0-9a-f]{40}',registration_commit or '') is not None,'Missing public registration commit')
 require(protocol.get('test',{}).get('parameters')==DEFINITION['parameters'],'Registered parameters differ')
 checked={};scripts={}
 for key,paths,destination in [('sourceHashes',INPUTS,checked),('scriptHashes',SCRIPTS,scripts)]:
  for relative in paths:
   actual=sha((ROOT/relative).read_bytes())
   require(protocol.get(key,{}).get(relative)==actual,'Registered input or implementation hash mismatch')
   destination[relative]=actual
 return checked,scripts

def assess_candidates(candidates):
 import batch20_common as common
 _,indexes=common.wordlist();valid={kind:{} for kind in FORMATS}
 for kind in FORMATS:
  for value in sorted(candidates[kind]):
   result=common.validate_record(kind,value,indexes)
   if result is not None:
    canonical,_=result;fp=common.fingerprint(kind,canonical)
    valid[kind].setdefault(fp,{'format':kind,'fingerprint':fp})
 return {'uniqueShapeCounts':{kind:len(candidates[kind]) for kind in FORMATS},
  'validatorCalls':sum(len(candidates[kind]) for kind in FORMATS),
  'validCounts':{kind:len(valid[kind]) for kind in FORMATS},
  'hits':[hit for kind in FORMATS for _,hit in sorted(valid[kind].items())],
  'fingerprintRule':common.FINGERPRINT_RULE,'privateReviewRequired':any(valid[kind] for kind in FORMATS),
  'countPolicy':'Unique candidate sets. No occurrences, expanded readings, unique texts or unique forms counted.',
  'networkQueries':0,'rawAsciiScalarInterpretations':0}

def run(args):
 from global_mirror_dag import graph,candidate_union,Budget
 began=utc();out=Path(args.out).resolve();require(not out.exists(),'Fresh output directory required')
 out.mkdir(parents=True,mode=0o700)
 base={'schemaVersion':1,'batchId':'keiser-global-mirror-envelope-20261110','testId':DEFINITION['id'],
  'title':DEFINITION['title'],'startedAtUTC':began,'registrationCommit':args.registration_commit,
  'scopeComplete':False,'completeNegative':False,'privateReviewRequired':False,
  'candidateAssessment':'not-run','networkQueries':0,'transactions':0}
 candidates={kind:set() for kind in FORMATS};details=[];budget=Budget(MAX_STATES,MAX_CANDIDATES);extraction_started=False
 try:
  protocol_bytes=Path(args.protocol).read_bytes();protocol=json.loads(protocol_bytes)
  sources,scripts=validate_protocol(protocol,args.registration_commit)
  controls=self_test();families=checked_source_families()
  base.update(sourceHashes=sources,scriptHashes=scripts,protocolSha256=sha(protocol_bytes),
   parameters=DEFINITION['parameters'],controls=controls,sourceCounts=public_source_counts(families),
   negativeCriterion=DEFINITION['negativeCriterion'],limitations=DEFINITION['limitations'])
  import batch20_common as common
  words,_=common.wordlist();extraction_started=True
  for family in families:
   for reverse in (False,True):
    for mode in ('words-spaced','words-joined','initials'):
     descriptor={'family':family['id'],'rowOrder':'reverse-entire-sequence' if reverse else 'forward','projection':mode,'complete':False}
     details.append(descriptor);before=budget.states;previous={k:len(candidates[k]) for k in FORMATS}
     language=graph(family['rows'],mode,reverse)
     descriptor['graphNodes']=language['nodes']
     try:candidate_union(language,words,budget,candidates);descriptor['complete']=True
     finally:
      descriptor['productPrefixStateVisits']=budget.states-before
      descriptor['newUniqueShapes']={k:len(candidates[k])-previous[k] for k in FORMATS}
  require(len(details)==24 and all(d['complete'] for d in details),'Incomplete language coverage')
  require(sum(len(v) for v in candidates.values())==budget.candidates,'Candidate insertion accounting mismatch')
  base['scopeComplete']=True
 except Exception as error:
  base.update(errorClass=type(error).__name__,error='Control, source/code pin, completeness cap or execution failure. No complete negative is claimed.')
  private_json(out/'ERROR.private.json',{'class':type(error).__name__,'message':str(error).replace(str(ROOT),'<research>').replace(str(out),'<output>')})
 finally:
  base['languageChecks']=details
  base['resourceCounts']={'productPrefixStateVisits':budget.states,'uniqueCandidateInsertions':budget.candidates,
   'maximumProductPrefixStateVisits':MAX_STATES,'maximumUniqueCandidateInsertions':MAX_CANDIDATES}
  if extraction_started:
   private_json(out/'CANDIDATES.private.json',{'candidateSemantics':'Unique shaped value sets, not occurrences.',
    'candidates':{k:sorted(v) for k,v in candidates.items()}})
   try:
    base['evaluation']=assess_candidates(candidates);base['candidateAssessment']='complete-for-saved-candidate-set'
    base['privateReviewRequired']=base['evaluation']['privateReviewRequired']
   except Exception as error:
    base.update(scopeComplete=False,candidateAssessment='validation-incomplete',validationErrorClass=type(error).__name__)
  if base['scopeComplete']:
   base['completeNegative']=not base['privateReviewRequired']
   base['outcome']='finding-private-review-required' if base['privateReviewRequired'] else 'no-valid-record-in-registered-global-language-union'
  else:
   base['completeNegative']=False
   base['outcome']='finding-private-review-required-incomplete-scope' if base['privateReviewRequired'] else 'inconclusive-control-source-cap-or-execution'
  base['completedAtUTC']=utc();private_json(out/'RESULT.json',base)
 print(json.dumps({k:base[k] for k in ['testId','outcome','scopeComplete','completeNegative','completedAtUTC','privateReviewRequired','networkQueries']},indent=2))
 return base

def main():
 parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
 group.add_argument('--list',action='store_true');group.add_argument('--self-test',action='store_true')
 group.add_argument('--run',action='store_true')
 parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out');args=parser.parse_args()
 if args.list:print(json.dumps(DEFINITION,indent=2));return
 if args.self_test:print(json.dumps(self_test(),indent=2));return
 require(args.protocol and args.registration_commit and args.out,'Run requires protocol, registration commit and fresh output directory')
 result=run(args)
 if not result['scopeComplete']:sys.exit(2)
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('Global envelope preparation failed: '+type(error).__name__+'. No complete exclusion claimed.',file=sys.stderr);sys.exit(1)
