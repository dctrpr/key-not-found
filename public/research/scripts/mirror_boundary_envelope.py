#!/usr/bin/env python3
"""Registered pair-local first/last-word uncertainty envelope. Offline, stdlib only.

No target work at import, --list, or --self-test. --source-audit reads geometry
only; --run requires frozen source/code pins and a public registration commit.
Raw streams and row alternatives are private until separately reviewed.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,math,os,re,sys
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=('scripts/mirror_boundary_envelope.py','scripts/batch20_geometry.py','scripts/batch20_common.py')
INPUTS=('sources/printed-lines.json','sources/word-geometry-20261110.json',
 'analysis_outputs/3d_article_map/article_3d_map_data.json',
 'analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json',
 'scripts/batch20_support/english.txt','scripts/batch20_support/controls.json')
FORMATS=('wif','minikey','hex64','bip39')
PAIRS=((76,77),(77,76),(78,79),(79,78))
DEFINITION={
 'id':'mirror-boundary-envelope','title':'All pair-local mirror boundary alternatives',
 'family':'mirror-firstword-uncertainty-envelope','branchId':'mirror-layout',
 'inputPaths':list(INPUTS),'implementationPaths':list(SCRIPTS),
 'parameters':{
  'pairs':[list(p) for p in PAIRS], 'maskClasses':['orange','black'],
  'wordEdges':['leftmost','rightmost'],'rowOrders':['forward','reverse'],
  'projections':['words-spaced','words-joined','initials'],'formats':list(FORMATS),
  'forms':['exact','whitespace-only-compacted'],
  'bip39Tokenization':'Lowercase unfiltered lexical words; ordinary punctuation boundaries; invalid decoded group ␞ is a hard region boundary.',
  'hexMatching':'64hex scalar records require non-hex boundaries; WIF and minikey shape windows may be embedded in a longer string.',
  'geometry':'Frozen token-box centers inverse-rotated to upright page; horizontal page reflection only.',
  'guardPx':'max(12, frozen word.centerUncertaintyPx)',
  'centerDomain':'Closed axis-aligned square [x-g,x+g] × [y-g,y+g] in original upright pixels.',
  'maskDomain':'Exact union of frozen horizontally reflected half-open rectangles [left,right) × [top,bottom).',
  'membership':'in if every point of the closed center square is in mask union; out if no point is; unknown otherwise.',
  'selection':'First/last possible selected word before the first guaranteed-in word; include no-word option iff no guaranteed-in word exists.',
  'coupling':'Independent uncertain memberships/row choices overapproximate correlated measurement errors; no likelihood or calibration claim.',
  'emptyRow':'Omit row when the no-word alternative is chosen; no padding or replacement text.',
  'maximumPairLocalSelectionPaths':20000,
  'maximumLabeledReadings':120000,
  'globalPairConcatenation':False,
  'rawAsciiScalars':False,'proseHashWrappers':False,'networkQueries':0,'transactions':0,
 },
 'controls':['exhaustive-five-position-membership-oracle','first-last-irrelevant-boundary',
  'empty-row-option','half-open-boundary','overlapping-union-coverage','mask-gap',
  'forward-reverse-projection','incremental-full-scanner-agreement','shared-format-controls'],
 'negativeCriterion':'A complete zero-result run excludes only the declared literal records from the registered pair-local modeled superset, at the pinned source/code bytes. It does not calibrate scan errors, test global concatenation or exhaust mirror/first-word ciphers.',
 'limitations':['The 12-pixel and frozen center guards are review heuristics, not statistically calibrated measurement-error bounds.',
  'Independent memberships admit physically inconsistent joint choices. This broadens the tested set and supplies no evidence of intentional encoding or candidate likelihood.',
  'Global concatenations across page-pair readings are deferred; their large path count is not silently tested or ruled out.',
  'Exact rectangle masks and the center-based selection convention are declared assumptions, not creator-specified instructions.']}

def utc():return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def sha(data):return hashlib.sha256(data).hexdigest()
def require(condition,message):
 if not condition:raise ValueError(message)
def private_json(path,value):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',encoding='utf-8') as out:
  json.dump(value,out,indent=2);out.write('\n')
def read_json(path):return json.loads(path.read_text(encoding='utf-8'))

def membership(center,boxes,guard):
 """Exact finite partition of a closed square against half-open rectangle union.

 Each membership predicate changes only at a rectangle's x/y edges. Evaluate
 every partition endpoint and one point in every intervening open interval.
 The Cartesian product therefore covers every distinct Boolean cell, including
 zero-area boundary cells. No raster rounding or geometric fitting is used.
 """
 x,y=center;g=float(guard)
 require(math.isfinite(g) and g>=0,'Invalid word guard')
 require(all(math.isfinite(v) for v in (x,y)),'Invalid word center')
 xs={x-g,x+g};ys={y-g,y+g}
 for a,b,c,d in boxes:
  require(all(math.isfinite(v) for v in (a,b,c,d)) and a<c and b<d,'Invalid mask rectangle')
  xs.update(v for v in (a,c) if x-g<=v<=x+g)
  ys.update(v for v in (b,d) if y-g<=v<=y+g)
 xs=sorted(xs);ys=sorted(ys)
 xx=xs+[(a+b)/2 for a,b in zip(xs,xs[1:])]
 yy=ys+[(a+b)/2 for a,b in zip(ys,ys[1:])]
 found=set()
 for u,v in itertools.product(xx,yy):
  found.add(any(a<=u<c and b<=v<d for a,b,c,d in boxes))
  if len(found)==2:return 'unknown'
 return 'in' if found=={True} else 'out'

def selection_options(states,edge):
 """Return word indexes/None reachable under independent unknown memberships.

 At the first guaranteed-in word in the requested direction, all later words
 are irrelevant to which word is first/last. Every preceding unknown word can
 be the selected one by setting earlier unknowns out. If no guaranteed-in word
 exists, setting every unknown out gives the explicit no-word alternative.
 """
 require(edge in ('leftmost','rightmost'),'Invalid selection edge')
 require(all(s in ('in','out','unknown') for s in states),'Invalid membership state')
 indexes=range(len(states)) if edge=='leftmost' else range(len(states)-1,-1,-1)
 options=[]
 for i in indexes:
  if states[i]=='out':continue
  options.append(i)
  if states[i]=='in':return options
 return options+[None]

def project(words,kind):
 if kind=='words-spaced':return ' '.join(words)
 if kind=='words-joined':return ''.join(words)
 if kind=='initials':return ''.join(next((c for c in w if c.isalnum()),'') for w in words)
 raise ValueError('Invalid projection')

def self_test():
 from batch20_common import self_test as shared_self_test,scan_streams
 from batch20_geometry import scan_streams_incrementally
 configs=0
 for states in itertools.product(('in','out','unknown'),repeat=5):
  unknown=[i for i,s in enumerate(states) if s=='unknown']
  for edge in ('leftmost','rightmost'):
   oracle=set()
   for bits in itertools.product((False,True),repeat=len(unknown)):
    hits=[s=='in' for s in states]
    for i,b in zip(unknown,bits):hits[i]=b
    selected=[i for i,v in enumerate(hits) if v]
    oracle.add(selected[0 if edge=='leftmost' else -1] if selected else None)
   assert set(selection_options(states,edge))==oracle
  configs+=1
 assert selection_options(['in','unknown'],'leftmost')==[0]
 assert selection_options(['unknown','in'],'rightmost')==[1]
 assert selection_options(['out','out'],'leftmost')==[None]
 assert selection_options(['unknown','out'],'leftmost')==[0,None]
 assert membership((1,1),[(0,0,2,2)],0)=='in'
 assert membership((2,1),[(0,0,2,2)],0)=='out'
 assert membership((1,1),[(0,0,2,2)],1)=='unknown' # closed square touches excluded right/top edges
 assert membership((1,1),[(-1,-1,1,3),(1,-1,3,3)],1)=='in' # internal union boundary cannot matter
 assert membership((1,1),[(-1,-1,.9,3),(1.1,-1,3,3)],1)=='unknown'
 assert membership((5,5),[(0,0,2,2)],1)=='out'
 assert project(['alpha','!Beta'],'initials')=='aB'
 assert project(['alpha','!Beta'][::-1],'words-joined')=='!Betaalpha'
 fixture=[{'id':'one','text':'alpha beta'},{'id':'two','text':'alpha beta'},
          {'id':'empty','text':''},{'id':'barrier','text':'alpha ␞ beta'},
          {'id':'known-public-control','text':'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'}]
 assert scan_streams_incrementally(iter(fixture),formats=FORMATS)==scan_streams(fixture,FORMATS)
 shared=shared_self_test()
 return {'passed':True,'exhaustiveSyntheticMembershipConfigurations':configs,
  'controls':DEFINITION['controls'],'shared':shared,'targetInputsRead':False,'targetKeyChecks':0,'networkQueries':0}

def source_model():
 # Frozen helper routines supply only source parsing/frame transforms; no target
 # procedure g01..g10 or validator is called while constructing this model.
 import batch20_geometry as g
 rows=g.read_json(ROOT/INPUTS[0])['rows']
 require(len(rows)==142 and all(r['section']=='body' for r in rows),'Unexpected canonical body rows')
 geometry,_=g.load_geometry(rows)
 require(all(r['geometryStatus']=='complete' for r in geometry),'Incomplete source word geometry')
 masks=g.get_masks(g.read_json(ROOT/INPUTS[2]),g.read_json(ROOT/INPUTS[3]))
 model=[]
 for source,target in PAIRS:
  for color in ('orange','black'):
   rectangles=[[2544-b[2],b[1],2544-b[0],b[3]] for b in masks[source][color]]
   prepared=[]
   for row in [r for r in geometry if r['page']==target]:
    words=sorted(row['words'],key=lambda w:g.center(w['box'])[0])
    require(bool(words),'Empty lexical source row')
    centers=[g.point_rotate(*g.center(w['box']),-row['geometryRotationCCW']) for w in words]
    guards=[max(12,float(w.get('centerUncertaintyPx',12))) for w in words]
    states=[membership(c,rectangles,guard) for c,guard in zip(centers,guards)]
    prepared.append({'rowId':row['id'],'wordIds':[w['id'] for w in words],
      'states':states,'centersUpright':centers,'guardsPx':guards,'words':[w['text'] for w in words]})
   for edge in ('leftmost','rightmost'):
    scope={'id':f'{source}-to-{target}:{color}:{edge}','source':source,'target':target,
      'color':color,'edge':edge,'rows':[]}
    for row in prepared:
     item=dict(row);item['options']=selection_options(row['states'],edge);scope['rows'].append(item)
    scope['selectionPaths']=math.prod(len(r['options']) for r in scope['rows'])
    model.append(scope)
 return model

def safe_model(model):
 return [{k:([{kk:vv for kk,vv in r.items() if kk!='words'} for r in v] if k=='rows' else v)
          for k,v in scope.items()} for scope in model]

def model_counts(model):
 total=sum(s['selectionPaths'] for s in model)
 return {'pairLocalScopes':len(model),'selectionPaths':total,'labeledReadings':total*6,
  'scopeCounts':[{'scopeId':s['id'],'rows':len(s['rows']),'selectionPaths':s['selectionPaths'],
    'ambiguousRowChoices':sum(len(r['options'])>1 for r in s['rows'])} for s in model],
  'globalPairConcatenationTested':False}

def readings(model):
 # Choices are enumerated in frozen row order and in fixed options order. A
 # single record at a time reaches the shared incremental scanner.
 for scope in model:
  for path_number,choice in enumerate(itertools.product(*(r['options'] for r in scope['rows']))):
   selected=[row['words'][i] for row,i in zip(scope['rows'],choice) if i is not None]
   word_ids=[row['wordIds'][i] for row,i in zip(scope['rows'],choice) if i is not None]
   for order in ('forward','reverse'):
    words=selected if order=='forward' else selected[::-1]
    ids=word_ids if order=='forward' else word_ids[::-1]
    for kind in ('words-spaced','words-joined','initials'):
     yield {'id':scope['id']+f':path{path_number}:{order}:{kind}','text':project(words,kind),
      'scopeId':scope['id'],'selectionPath':path_number,'rowOrder':order,'projection':kind,
      'selectedWordIds':ids,'rowChoiceIndexes':list(choice)}

def validate_protocol(protocol,registration_commit):
 require(protocol.get('version')==1 and protocol.get('batchId')=='keiser-mirror-boundary-envelope-20261110','Unexpected registered protocol')
 require(re.fullmatch(r'[0-9a-f]{40}',registration_commit or '') is not None,'Missing registration commit')
 require(protocol.get('test',{}).get('parameters')==DEFINITION['parameters'],'Registered parameters differ')
 checked={};scripts={}
 for key,paths,destination in [('sourceHashes',INPUTS,checked),('scriptHashes',SCRIPTS,scripts)]:
  for relative in paths:
   require(protocol.get(key,{}).get(relative)==sha((ROOT/relative).read_bytes()),'Registered source or implementation pin mismatch')
   destination[relative]=protocol[key][relative]
 return checked,scripts

def run(args):
 began=utc();out=Path(args.out).resolve();require(not out.exists(),'Fresh output directory required')
 out.mkdir(parents=True,mode=0o700)
 base={'schemaVersion':1,'batchId':'keiser-mirror-boundary-envelope-20261110',
  'testId':DEFINITION['id'],'title':DEFINITION['title'],'startedAtUTC':began,
  'registrationCommit':args.registration_commit,'networkQueries':0,'transactions':0,
  'privateReviewRequired':False,'scopeComplete':False,'completeNegative':False}
 try:
  protocol_bytes=Path(args.protocol).read_bytes();protocol=json.loads(protocol_bytes)
  source_hashes,script_hashes=validate_protocol(protocol,args.registration_commit)
  controls=self_test();model=source_model();counts=model_counts(model)
  require(counts['pairLocalScopes']==16,'Unexpected pair-local scope count')
  require(counts['selectionPaths']<=DEFINITION['parameters']['maximumPairLocalSelectionPaths'],'Selection-path cap exceeded')
  require(counts['labeledReadings']<=DEFINITION['parameters']['maximumLabeledReadings'],'Reading cap exceeded')
  private_json(out/'SOURCE_MODEL.private.json',safe_model(model))
  from batch20_geometry import scan_streams_incrementally
  raw=out/'READINGS.private.jsonl'
  with os.fdopen(os.open(raw,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',encoding='utf-8') as handle:
   def record(rec):handle.write(json.dumps(rec,ensure_ascii=False)+'\n')
   evaluation=scan_streams_incrementally(readings(model),on_stream=record,formats=FORMATS)
  require(evaluation['streamCount']==counts['labeledReadings'],'Execution count did not match complete envelope')
  lead=evaluation['privateReviewRequired']
  base.update(sourceHashes=source_hashes,scriptHashes=script_hashes,
   protocolSha256=sha(protocol_bytes),parameters=DEFINITION['parameters'],controls=controls,
   procedureCounts=counts,evaluation=evaluation,scopeComplete=True,
   privateReviewRequired=lead,completeNegative=not lead,
   outcome='finding-private-review-required' if lead else 'no-valid-record-in-registered-pair-local-envelope',
   negativeCriterion=DEFINITION['negativeCriterion'],limitations=DEFINITION['limitations'],
   privateArtifacts=['SOURCE_MODEL.private.json','READINGS.private.jsonl'])
 except Exception as error:
  private_json(out/'ERROR.private.json',{'class':type(error).__name__,'message':str(error).replace(str(ROOT),'<research>').replace(str(out),'<output>')})
  base.update(outcome='inconclusive-control-source-or-execution',errorClass=type(error).__name__,
   error='Registered controls, source pins, completeness cap or execution failed. No negative claim.')
 finally:
  base['completedAtUTC']=utc();private_json(out/'RESULT.json',base)
 print(json.dumps({k:base[k] for k in ['testId','outcome','scopeComplete','completeNegative','completedAtUTC','privateReviewRequired','networkQueries']},indent=2))
 return base

def main():
 parser=argparse.ArgumentParser(description=__doc__);actions=parser.add_mutually_exclusive_group(required=True)
 actions.add_argument('--list',action='store_true');actions.add_argument('--self-test',action='store_true')
 actions.add_argument('--source-audit',action='store_true');actions.add_argument('--run',action='store_true')
 parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out');args=parser.parse_args()
 if args.list:print(json.dumps(DEFINITION,indent=2));return
 if args.self_test:print(json.dumps(self_test(),indent=2));return
 if args.source_audit:
  require(args.out,'Source audit requires a fresh explicit output directory');out=Path(args.out).resolve();require(not out.exists(),'Fresh source-audit output required');out.mkdir(parents=True,mode=0o700)
  model=source_model();counts=model_counts(model);private_json(out/'SOURCE_MODEL.json',safe_model(model));private_json(out/'COUNTS.json',counts)
  print(json.dumps(counts,indent=2));return
 require(args.protocol and args.registration_commit and args.out,'Run requires registered protocol, commit and fresh output directory')
 run(args)
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('Envelope preparation failed: '+type(error).__name__+'. No exclusion claimed.',file=sys.stderr);sys.exit(1)
