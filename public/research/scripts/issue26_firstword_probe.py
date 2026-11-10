#!/usr/bin/env python3
"""Fixed Issue26 printed-first-word procedure. Offline, Python stdlib only.

Import, --list and --self-test do not read the article or validate its readings.
--run requires a public registration SHA, pinned protocol and fresh private out.
Full-line OCR is never used to construct candidate text.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,os,re,sys
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
CANONICAL='sources/issue26/issue26-source.json'
CANONICAL_SHA='1ff7a0a26c1e91fb2bfef9817693419979fdf39381d4124c2c9e5e7739f73c67'
INPUTS=(CANONICAL,'sources/issue26/page_03.jpg','sources/issue26/page_04.jpg',
 'sources/issue26/page_05.jpg','scripts/batch20_support/english.txt','scripts/batch20_support/controls.json')
SCRIPTS=('scripts/issue26_firstword_probe.py','scripts/batch20_geometry.py','scripts/batch20_common.py')
FORMATS=('wif','minikey','hex64','bip39','extended_private','bip38','address','sec_public')
SURFACES=('firstWordSource','firstLexicalWordSource')
POPULATIONS=('all-text','prose-only','emphasis-only')
STOP_POLICIES=('exclude-side-label','replace-anchored-row-token','insert-label-before-anchor')
PHASES=('all','odd','even')
PARITY_ORIGINS=('policy-rows-before-population-filter','population-after-filter')
ORDERS=('forward','reverse')
PROJECTIONS=('words-spaced','words-joined','initials','finals')
CHAR_ORDERS=('exact','reversed-codepoints')
ANCHOR='p102r10'
BATCH_ID='keiser-issue26-firstwords-20261110'
DEFINITION={
 'id':'issue26-first-words','title':'Issue26 faithful printed-first-word readings',
 'family':'printed-firstword-null-cipher','branchId':'sources',
 'inputPaths':list(INPUTS),'implementationPaths':list(SCRIPTS),
 'parameters':{
  'units':['whole-article','each-printed-page','each-source-flow-block'],
  'expectedUnitCount':23,'expectedFlowBlocks':19,'printedPages':[102,103,104],
  'sourceBodyRows':113,'sourceRowsByPage':{'102':42,'103':52,'104':19},
  'sourceProseRows':94,'sourceEmphasisRows':19,'standaloneSTOPLabels':1,
  'populations':list(POPULATIONS),
  'populationRules':{'all-text':'All source text rows, including inserted label when that policy is selected.',
   'prose-only':'role exactly body-prose; standalone label is excluded.',
   'emphasis-only':'role other than body-prose, including inserted label.'},
  'tokenSurfaces':list(SURFACES),
  'surfaceMeaning':'Use the frozen reviewed fields literally; outer punctuation already stripped by source convention; internal punctuation, fused forms and printed hyphenation retained. Raster witnesses do not establish original digital Unicode codepoints.',
  'STOPPolicies':list(STOP_POLICIES),'STOPAnchorRowId':ANCHOR,
  'STOPPolicyMeaning':'Exclude the side label; replace the anchored row token with STOP without changing that row role/rank; or insert the separate label immediately before the anchor. Units without the anchor are unchanged.',
  'parityPhases':list(PHASES),'parityOrigins':list(PARITY_ORIGINS),
  'parityDefinition':'One-based rank within the current unit after STOP policy; either before or after population filtering. Source ID suffixes never determine parity.',
  'rowOrder':list(ORDERS),'operationOrder':'Unit -> STOP policy -> population/rank -> parity -> row order -> projection -> character order.',
  'projections':list(PROJECTIONS),'initialFinalRule':'First/last Unicode alphanumeric character of each reviewed token, with case preserved.',
  'characterOrder':list(CHAR_ORDERS),'formats':list(FORMATS),
  'forms':['exact','whitespace-only-compacted'],
  'bip39Tokenization':'Lowercase unfiltered lexical tokens; ordinary punctuation bounds words; invalid decoded group ␞ is a hard region boundary. Non-dictionary tokens are not discarded.',
  'hexMatching':'64hex and SEC records require non-hex boundaries. Other registered record shapes may be embedded in longer text.',
  'fullLineOCRUsed':False,'unknownFirstWordPolicy':'Any unverified, empty or malformed source first-word field prevents a complete result; never silently omit or guess it.',
  'emptyUnits':'Retain labeled empty readings; deduplicate actual forms in the shared evaluator.',
  'expectedLabeledReadings':39744,'maximumLabeledReadings':50000,
  'rawAsciiScalars':False,'proseHashWrappers':False,'deriveChildKeys':False,
  'deriveAddresses':False,'passphraseGuesses':False,'networkQueries':0,'transactions':0},
 'controls':['STOP-exclude-replace-insert','source-ID-gap-independent-parity',
  'before-after-filter-parity','unit-local-ranks','mixed-flow-column-order',
  'prose-emphasis-partition','empty-unit-retention','fused-token-Unicode-hyphen-preservation',
  'row-and-codepoint-reversal','shared-eight-format-controls','incremental-bulk-scanner-agreement'],
 'negativeCriterion':'A complete zero result excludes only the declared literal/private/public records in these fixed first-word-derived readings from the pinned Issue26 witnesses. It does not test full alternate lines, another source, arbitrary ciphers or authenticate the 20-BTC claim.',
 'limitations':['This eligible pre-December2022 column is not authenticated as the March2023 20-BTC target.',
  'Printed line starts are reviewed; full-line OCR is unverified, including23 obscured page102 endings. Full-line/alternate-line exclusion is outside scope.',
  'STOP placement, population, parity and mirror variants are correlated declared conventions, not independent theories or evidence of intent.',
  'First-word surfaces are raster transcription conventions; original digital punctuation/Unicode bytes are unavailable.',
  'A valid private record, encrypted record, address or public point is only a lead requiring separate review; no wallet action follows.']}

def utc():return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def private_json(path,value):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',encoding='utf-8') as out:json.dump(value,out,indent=2);out.write('\n')
def has_word(value):return isinstance(value,str) and bool(value) and not any(c.isspace() for c in value) and any(c.isalnum() for c in value)

def validate_source(data):
 rows=data.get('rows',[]);labels=data.get('standaloneLabels',[])
 require(len(rows)==113 and len(labels)==1,'Canonical row/label coverage changed')
 require(len({r.get('id') for r in rows+labels})==114,'Duplicate source object IDs')
 rows=sorted(rows,key=lambda r:r['articleReadingIndex'])
 require([r['articleReadingIndex'] for r in rows]==list(range(1,114)),'Article reading indices changed')
 require({str(p):sum(r['page']==p for r in rows) for p in [102,103,104]}=={'102':42,'103':52,'104':19},'Page coverage changed')
 require(sum(r['role']=='body-prose' for r in rows)==94,'Source role counts changed')
 for row in rows+labels:
  require(row.get('firstWordStatus')=='verified-source-pixels','Unverified source first word')
  require(all(has_word(row.get(surface)) for surface in SURFACES),'Unknown/empty/malformed reviewed first word')
 blocks=list(dict.fromkeys(r['flowBlock'] for r in rows))
 require(len(blocks)==19,'Source flow-block count changed')
 require([next(r['flowBlockOrder'] for r in rows if r['flowBlock']==b) for b in blocks]==list(range(1,20)),'Source block flow changed')
 for page in [102,103,104]:require([r['pageReadingIndex'] for r in rows if r['page']==page]==list(range(1,1+sum(r['page']==page for r in rows))),'Page reading indices changed')
 for block in blocks:
  members=[r for r in rows if r['flowBlock']==block]
  require([r['flowReadingIndex'] for r in members]==list(range(1,len(members)+1)),'Flow reading indices changed')
 require(sum(r['id']==ANCHOR for r in rows)==1 and labels[0]['id']=='p102r15','STOP anchoring changed')
 require(all(labels[0][s]=='STOP' for s in SURFACES),'STOP label changed')
 return rows,labels[0]

def source_units(rows):
 blocks=list(dict.fromkeys(r['flowBlock'] for r in rows))
 return [('article',rows)]+[(f'p{p}',[r for r in rows if r['page']==p]) for p in [102,103,104]]+[(b,[r for r in rows if r['flowBlock']==b]) for b in blocks]

def policy_rows(rows,label,policy):
 require(policy in STOP_POLICIES,'Unknown STOP policy');out=[]
 for source in rows:
  row=dict(source);row['tokenSourceId']=source['id']
  if source['id']==ANCHOR:
   if policy=='insert-label-before-anchor':
    inserted=dict(label);inserted['tokenSourceId']=label['id'];out.append(inserted)
   elif policy=='replace-anchored-row-token':
    for surface in SURFACES:row[surface]=label[surface]
    row['tokenSourceId']=label['id']
  out.append(row)
 return out

def select_rows(rows,population,phase,origin,order):
 require(population in POPULATIONS and phase in PHASES and origin in PARITY_ORIGINS and order in ORDERS,'Unknown selection convention')
 def included(r):return population=='all-text' or (r['role']=='body-prose' if population=='prose-only' else r['role']!='body-prose')
 selected=[(i+1,r) for i,r in enumerate(rows) if included(r)]
 ranked=[(i+1,r) for i,(_,r) in enumerate(selected)] if origin=='population-after-filter' else selected
 chosen=[r for rank,r in ranked if phase=='all' or rank%2==int(phase=='odd')]
 return chosen if order=='forward' else chosen[::-1]

def project(words,kind):
 if kind=='words-spaced':return ' '.join(words)
 if kind=='words-joined':return ''.join(words)
 if kind=='initials':return ''.join(next(c for c in w if c.isalnum()) for w in words)
 if kind=='finals':return ''.join(next(c for c in reversed(w) if c.isalnum()) for w in words)
 raise ValueError('Unknown projection')

def readings(units,label):
 for unit_id,unit_rows in units:
  for stop in STOP_POLICIES:
   policy=policy_rows(unit_rows,label,stop)
   for population,surface,phase,origin,order in itertools.product(POPULATIONS,SURFACES,PHASES,PARITY_ORIGINS,ORDERS):
    selected=select_rows(policy,population,phase,origin,order);words=[r[surface] for r in selected]
    for projection,char_order in itertools.product(PROJECTIONS,CHAR_ORDERS):
     text=project(words,projection)
     if char_order=='reversed-codepoints':text=text[::-1]
     yield {'id':f'{unit_id}:{stop}:{population}:{surface}:{phase}:{origin}:{order}:{projection}:{char_order}',
      'text':text,'unit':unit_id,'STOPPolicy':stop,'population':population,'surface':surface,
      'phase':phase,'parityOrigin':origin,'rowOrder':order,'projection':projection,'characterOrder':char_order,
      'selectedRowIds':[r['id'] for r in selected],'tokenSourceIds':[r['tokenSourceId'] for r in selected]}

def self_test():
 # Entirely synthetic row/token fixtures. No article files are opened.
 def row(id,role,a,b=None,page=102,block='synthetic'):
  return {'id':id,'role':role,'firstWordSource':a,'firstLexicalWordSource':b or a,'page':page,'flowBlock':block}
 synthetic=[row('source-gap-02','body-prose','Alpha'),row(ANCHOR,'callout','Take'),row('source-gap-99','body-prose','present,how','present')]
 label=row('label','display-label','STOP')
 excluded=policy_rows(synthetic,label,STOP_POLICIES[0]);replaced=policy_rows(synthetic,label,STOP_POLICIES[1]);inserted=policy_rows(synthetic,label,STOP_POLICIES[2])
 assert [r['firstWordSource'] for r in excluded]==['Alpha','Take','present,how']
 assert [r['firstWordSource'] for r in replaced]==['Alpha','STOP','present,how']
 assert [r['firstWordSource'] for r in inserted]==['Alpha','STOP','Take','present,how']
 assert replaced[1]['role']=='callout' and replaced[1]['id']==ANCHOR
 assert len(select_rows(inserted,'prose-only','all',PARITY_ORIGINS[0],'forward'))==2
 assert len(select_rows(inserted,'emphasis-only','all',PARITY_ORIGINS[0],'forward'))==2
 assert [r['id'] for r in select_rows(excluded,'prose-only','even',PARITY_ORIGINS[0],'forward')]==[]
 assert [r['id'] for r in select_rows(excluded,'prose-only','even',PARITY_ORIGINS[1],'forward')]==['source-gap-99']
 assert [r['id'] for r in select_rows(excluded,'all-text','odd',PARITY_ORIGINS[0],'forward')]==['source-gap-02','source-gap-99']
 assert [r['id'] for r in select_rows(excluded,'all-text','odd',PARITY_ORIGINS[0],'reverse')]==['source-gap-99','source-gap-02']
 assert select_rows(excluded,'emphasis-only','even',PARITY_ORIGINS[1],'forward')==[]
 assert [r['firstWordSource'] for r in policy_rows([synthetic[0]],label,STOP_POLICIES[2])]==['Alpha']
 # Unit-local rank starts at1 despite arbitrary original IDs/global positions.
 assert select_rows([excluded[2]],'all-text','odd',PARITY_ORIGINS[0],'forward')[0]['id']=='source-gap-99'
 ordered=[dict(synthetic[0],articleReadingIndex=1,page=102,flowBlock='wide'),
  dict(synthetic[2],articleReadingIndex=2,page=103,flowBlock='left-column'),
  dict(synthetic[1],articleReadingIndex=3,page=103,flowBlock='right-column')]
 grouped=source_units(ordered)
 assert [r['id'] for r in grouped[0][1]]==['source-gap-02','source-gap-99',ANCHOR]
 assert [r['id'] for r in dict(grouped)['p103']]==['source-gap-99',ANCHOR]
 assert [id for id,_ in grouped[4:]]==['wide','left-column','right-column']
 assert dict(grouped)['p104']==[]
 assert project(['present,how','thepursuit','tele­','world-','Don’t'],'words-spaced')=='present,how thepursuit tele­ world- Don’t'
 assert project(['!Alpha','Beta?'],'initials')=='AB' and project(['!Alpha','Beta?'],'finals')=='aa'
 assert project(['ab','CD'],'words-joined')[::-1]=='DCba'
 unit=[('synthetic',synthetic)]
 generated=list(readings(unit,label));expected=3*3*2*3*2*2*4*2
 assert len(generated)==expected==1728 and len({r['id'] for r in generated})==expected
 assert any(r['text']=='' for r in generated)
 from batch20_common import self_test as shared_self_test,scan_streams
 from batch20_geometry import scan_streams_incrementally
 shared=shared_self_test()
 fixture=[{'id':'normal','text':'alpha beta'},{'id':'same','text':'alphabeta'},
  {'id':'barrier','text':'alpha ␞ beta'},{'id':'known-public-control','text':'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'}]
 assert scan_streams_incrementally(iter(fixture),formats=FORMATS)==scan_streams(fixture,FORMATS)
 return {'passed':True,'controls':DEFINITION['controls'],'syntheticLabeledReadings':expected,
  'shared':shared,'targetInputsRead':False,'targetRecordChecks':0,'networkQueries':0}

def validate_protocol(protocol,registration_commit):
 require(protocol.get('version')==1 and protocol.get('batchId')==BATCH_ID,'Unexpected registered protocol')
 require(re.fullmatch(r'[0-9a-f]{40}',registration_commit or '') is not None,'Registration commit must be a full lowercase SHA')
 require(protocol.get('test',{}).get('parameters')==DEFINITION['parameters'],'Registered parameters differ')
 hashes={};scripts={}
 for key,paths,dest in [('sourceHashes',INPUTS,hashes),('scriptHashes',SCRIPTS,scripts)]:
  for rel in paths:
   actual=sha((ROOT/rel).read_bytes());require(protocol.get(key,{}).get(rel)==actual,'Registered source or implementation pin mismatch');dest[rel]=actual
 require(hashes[CANONICAL]==CANONICAL_SHA,'Frozen canonical source changed')
 return hashes,scripts

def run(args):
 began=utc();out=Path(args.out).resolve();require(not out.exists(),'Fresh explicit output directory required');out.mkdir(parents=True,mode=0o700)
 base={'schemaVersion':1,'batchId':BATCH_ID,'testId':DEFINITION['id'],'title':DEFINITION['title'],
  'startedAtUTC':began,'registrationCommit':args.registration_commit,'networkQueries':0,'transactions':0,
  'privateReviewRequired':False,'scopeComplete':False,'completeNegative':False}
 try:
  protocol_bytes=Path(args.protocol).read_bytes();protocol=json.loads(protocol_bytes)
  hashes,scripts=validate_protocol(protocol,args.registration_commit);controls=self_test()
  rows,label=validate_source(json.loads((ROOT/CANONICAL).read_text()));units=source_units(rows)
  require(len(units)==DEFINITION['parameters']['expectedUnitCount'],'Declared unit coverage changed')
  count=len(units)*len(STOP_POLICIES)*len(POPULATIONS)*len(SURFACES)*len(PHASES)*len(PARITY_ORIGINS)*len(ORDERS)*len(PROJECTIONS)*len(CHAR_ORDERS)
  require(count==DEFINITION['parameters']['expectedLabeledReadings'] and count<=DEFINITION['parameters']['maximumLabeledReadings'],'Declared reading completeness/cap failed')
  counts={'sourceRows':len(rows),'sourceLabels':1,'sourceProseRows':sum(r['role']=='body-prose' for r in rows),
   'sourceEmphasisRows':sum(r['role']!='body-prose' for r in rows),'units':len(units),
   'unitCounts':[{'id':id,'sourceRows':len(rr)} for id,rr in units],
   'labeledReadings':count,'fullLineOCRUsed':False,'sourceIDParityUsed':False}
  from batch20_geometry import scan_streams_incrementally
  with os.fdopen(os.open(out/'READINGS.private.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',encoding='utf-8') as handle:
   def record(rec):handle.write(json.dumps(rec,ensure_ascii=False)+'\n')
   evaluation=scan_streams_incrementally(readings(units,label),on_stream=record,formats=FORMATS)
  require(evaluation['streamCount']==count,'Actual reading count differs from complete declared set')
  lead=evaluation['privateReviewRequired']
  base.update(sourceHashes=hashes,scriptHashes=scripts,protocolSha256=sha(protocol_bytes),
   parameters=DEFINITION['parameters'],controls=controls,procedureCounts=counts,evaluation=evaluation,
   scopeComplete=True,privateReviewRequired=lead,completeNegative=not lead,
   outcome='finding-private-review-required' if lead else 'no-valid-record-in-registered-firstword-readings',
   negativeCriterion=DEFINITION['negativeCriterion'],limitations=DEFINITION['limitations'],
   privateArtifacts=['READINGS.private.jsonl'])
 except Exception as error:
  private_json(out/'ERROR.private.json',{'class':type(error).__name__,'message':str(error).replace(str(ROOT),'<research>').replace(str(out),'<output>')})
  base.update(outcome='inconclusive-source-control-or-execution',errorClass=type(error).__name__,error='Pinned source, controls, completeness or execution failed. No negative claim.')
 finally:
  base['completedAtUTC']=utc();private_json(out/'RESULT.json',base)
 print(json.dumps({k:base[k] for k in ['testId','outcome','scopeComplete','completeNegative','completedAtUTC','privateReviewRequired','networkQueries']},indent=2))
 return base

def main():
 p=argparse.ArgumentParser(description=__doc__);a=p.add_mutually_exclusive_group(required=True)
 a.add_argument('--list',action='store_true');a.add_argument('--self-test',action='store_true');a.add_argument('--run',action='store_true')
 p.add_argument('--protocol');p.add_argument('--registration-commit');p.add_argument('--out');args=p.parse_args()
 if args.list:print(json.dumps(DEFINITION,indent=2));return
 if args.self_test:print(json.dumps(self_test(),indent=2));return
 require(args.protocol and args.registration_commit and args.out,'Run requires protocol, registration commit and fresh output')
 run(args)
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('First-word procedure failed before execution: '+type(error).__name__+'. No exclusion claimed.',file=sys.stderr);sys.exit(1)
