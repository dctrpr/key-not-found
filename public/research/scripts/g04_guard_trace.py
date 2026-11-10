#!/usr/bin/env python3
"""Bit-free, unrepaired G04 optical-guard trace. Definition/self-test use no sources.

Target execution requires public Git registration and a fresh private output path.
No gaps, row medians, gap bits, decoders, candidates or network are implemented.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True

TEST_ID = 'g04-guard-trace'
BATCH_ID = 'keiser-g04-guard-trace-20261110'
SELF_REL = 'scripts/g04_guard_trace.py'
OLD_REL = 'scripts/batch20_geometry.py'
PROTOCOL_REL = 'analysis_outputs/continuation_20261110/g04_guard_trace/PROTOCOL.json'
BASELINE_REL = 'analysis_outputs/continuation_20261110/batch20/G04/RESULT.json'
SOURCES = {
 'magazine.pdf':'a30c61f8c49674afb7bccc6680d6477f6e919175386a2422de0a944db4e76c13',
 'sources/printed-lines.json':'c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe',
 'sources/word-geometry-20261110.json':'e3348d0d60d3097b05d0afdb0a1fccf66409274408af9ae7a9369c37fe596e9f',
 BASELINE_REL:'b3f920064b245c74cc0c1855ebd744b2d30f3c88a6ff50d89cc76c70a45185f4',
 'analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json':'e69215cd826a8fd63c588d5fe9295a71a1807278fd499b9a77cff119c48d4f53'}
OLD_SHA = 'e7786acc472fa3f7a294fe6391e74bd6f8840017e30d9f54941544019dbafb9a'
WORD_GUARDS = ('nonpositive-word-region', 'no-robust-ink-rows',
 'ink-touches-vertical-region-boundary', 'no-robust-ink-columns',
 'ink-touches-word-region-boundary')
DEFINITION = {
 'id':TEST_ID, 'family':'source-measurement-diagnostic', 'branchId':'numbers-type',
 'title':'Bit-free trace of the original G04 optical guards',
 'sourcePaths':list(SOURCES), 'implementationPaths':[OLD_REL, SELF_REL],
 'protocolPath':PROTOCOL_REL,
 'population':{'physicalRows':142,'lexicalWords':1243,'standalonePunctuationTokens':15,
  'allRowsIncluded':True,'allLexicalWordRegionsRecorded':True},
 'recordedBaseline':{'opticalFirstFailureRows':38,'rowsWithSavedGapMeasurements':104,
  'savedMeasuredGapCount':811,'completePages':0,'retainedDecodedStreams':0,
  'gapValuesNeverRecomputedByThisDiagnostic':True},
 'measurement':'Exact original ink_word_regions geometry, resampler, foreground and guard order; no repair. Original edge-background medians are retained for polarity; gap-row medians are not computed.',
 'polarity':'selectedByOriginalRule only: scanline edge median maxRGB>170 selects black(maxRGB<130), otherwise white(minRGB>170 and spread<70). Not source ground truth.',
 'guardOrder':{'row':['incomplete-word-geometry','no-lexical-words','insufficient-vertical-glyph-region'],
  'word':list(WORD_GUARDS)},
 'continuation':'After first word failure, continue every remaining lexical word only as counterfactual-after-first-word-failure. Earlier guard failures retain their baseline priority; later-stage column flags are diagnostic only.',
 'rowGuardPolicy':'A pre-word-loop row guard has NULL failedWordID/index. Do not invent per-word pixel diagnostics after an invalid row envelope.',
 'comparison':'Compare first optical failure or optical pass for all142 rows to the pinned original G04 RESULT. No post-span nonpositive-gap check is performed.',
 'punctuation':'Report the15 pinned punctuation records and NULL boxes; do not locate, repair or assign glyphs.',
 'caps':{'sourceOrRegisteredBlobBytes':20000000,'protocolBytes':1000000,
  'physicalRows':142,'lexicalWords':1243,'punctuationTokens':15,'traceBytes':24000000},
 'privateArtifacts':['TRACE.private.json'],
 'safeResult':'Aggregate source/guard/continuation counts and integrity pins only; no row IDs, word IDs, coordinates, polarity runs or source text.',
 'prohibited':{'gapCalculation':False,'gapRowMedians':False,'gapBits':False,'decoders':False,
  'candidateOrFormatChecks':False,'pixelOrCropOutputs':False,'foregroundRepair':False,
  'networkRequests':0,'walletOperations':0},
 'limitations':['This is a diagnostic, not a puzzle/key result or repaired measurement.',
  'Only first optical guards are comparable to the original short-circuit row receipt.',
  'Continuation after failure and column flags after an earlier guard are counterfactual diagnostics.',
  'No source support/polarity correction or downstream gap guard is tested.']}

class GuardError(Exception):
 pass

def need(condition, message):
 if not condition: raise GuardError(message)

def utc():
 return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')

def digest(data):
 return hashlib.sha256(data).hexdigest()  # file-integrity identifiers only

def dependencies():
 import numpy as np
 from PIL import Image
 return np, Image

def rotate_point(x,y,deg):
 a=math.radians(deg); dx=x-2544/2; dy=y-3264/2
 return (2544/2+math.cos(a)*dx+math.sin(a)*dy,
         3264/2-math.sin(a)*dx+math.cos(a)*dy)

def center(box):
 return ((box[0]+box[2])/2,(box[1]+box[3])/2)

def envelope(words):
 return [min(w['box'][0] for w in words),min(w['box'][1] for w in words),
         max(w['box'][2] for w in words),max(w['box'][3] for w in words)]

def rotation(row):
 return row.get('geometryRotationCCW',row['locator'].get('rotate_ccw_degrees',0))

def polarity_runs(light):
 result=[]
 for i,value in enumerate(light):
  selected='black' if bool(value) else 'white'
  if result and result[-1]['selectedByOriginalRule']==selected:
   result[-1]['endScanlineExclusive']=i+1
  else:result.append({'startScanline':i,'endScanlineExclusive':i+1,'selectedByOriginalRule':selected})
 return result

def trace_word(image, words, index, y0, y1, counterfactual):
 """Clone original per-word operations, record all guard flags, never gaps."""
 np,_=dependencies(); word=words[index]; box=word['box']
 left=math.floor((words[index-1]['box'][2]+box[0])/2) if index else math.floor(box[0]-12)
 right=math.ceil((box[2]+words[index+1]['box'][0])/2) if index+1<len(words) else math.ceil(box[2]+12)
 left=max(0,left);right=min(2544,right)
 rec={'wordID':word['id'],'lexicalWordIndex1':index+1,'frozenWordBox':box,
  'sourceRegion':[left,y0,right,y1],
  'evaluationStage':'counterfactual-after-first-word-failure' if counterfactual else 'original-path',
  'firstGuardReason':None,'selectedByOriginalRule':None,'robustInkRowCount':None,
  'robustInkColumnCount':None,'boundaryFlags':None,'firstGuardBoundarySides':[],
  'columnDiagnosticsCounterfactual':False}
 if right<=left:rec['firstGuardReason']='nonpositive-word-region';return rec
 pixels=np.asarray(image.crop((left,y0,right,y1))).astype('int16')
 edges=np.concatenate([pixels[:,:min(3,pixels.shape[1])],pixels[:,-min(3,pixels.shape[1]):]],axis=1)
 background=np.median(edges,axis=1);light=background.max(1)>170
 black=pixels.max(2)<130;white=(pixels.min(2)>170)&((pixels.max(2)-pixels.min(2))<70)
 ink=np.where(light[:,None],black,white)
 occupied_rows=np.flatnonzero(ink.sum(1)>=2)
 occupied=np.flatnonzero(ink.sum(0)>=2)
 top=bool(len(occupied_rows) and int(occupied_rows[0])<1)
 bottom=bool(len(occupied_rows) and int(occupied_rows[-1])>=y1-y0-1)
 left_flag=bool(len(occupied) and int(occupied[0])<1)
 right_flag=bool(len(occupied) and int(occupied[-1])>=right-left-1)
 rec['selectedByOriginalRule']={'blackScanlines':int(light.sum()),'whiteScanlines':int((~light).sum()),
  'runs':polarity_runs(light),'groundTruthClaimed':False}
 rec.update(robustInkRowCount=int(len(occupied_rows)),robustInkColumnCount=int(len(occupied)),
  boundaryFlags={'top':top,'bottom':bottom,'left':left_flag,'right':right_flag})
 # Baseline priority matches the original early returns. Column statistics above
 # are explicitly counterfactual if the original returned at a row/vertical test.
 if not len(occupied_rows):rec['firstGuardReason']='no-robust-ink-rows'
 elif top or bottom:rec['firstGuardReason']='ink-touches-vertical-region-boundary'
 elif not len(occupied):rec['firstGuardReason']='no-robust-ink-columns'
 elif left_flag or right_flag:rec['firstGuardReason']='ink-touches-word-region-boundary'
 if rec['firstGuardReason']=='ink-touches-vertical-region-boundary':
  rec['firstGuardBoundarySides']=[side for side,value in [('top',top),('bottom',bottom)] if value]
 elif rec['firstGuardReason']=='ink-touches-word-region-boundary':
  rec['firstGuardBoundarySides']=[side for side,value in [('left',left_flag),('right',right_flag)] if value]
 rec['columnDiagnosticsCounterfactual']=rec['firstGuardReason'] in (
  'no-robust-ink-rows','ink-touches-vertical-region-boundary')
 return rec

def trace_row(image,row,neighbors):
 np,Image=dependencies(); words=sorted(row['words'],key=lambda w:w['box'][0])
 result={'rowID':row['id'],'page':row['page'],'rotationCCWDegrees':rotation(row),
  'rowLevelGuard':None,'firstFailureReason':None,'firstFailedWordID':None,
  'firstFailedLexicalWordIndex1':None,'firstFailureBoundarySides':None,
  'rowRegionY':None,'words':[]}
 if row['geometryStatus']!='complete':result['rowLevelGuard']='incomplete-word-geometry'
 elif not words:result['rowLevelGuard']='no-lexical-words'
 if result['rowLevelGuard']:
  result['firstFailureReason']=result['rowLevelGuard']
  result['words']=[{'wordID':w['id'],'lexicalWordIndex1':i+1,'frozenWordBox':w['box'],
   'evaluationStage':'not-reached-row-level-guard','sourceRegion':None} for i,w in enumerate(words)]
  return result
 angle=rotation(row)
 if angle:image=image.rotate(angle,resample=Image.Resampling.NEAREST,expand=False)
 y0=math.floor(min(w['box'][1] for w in words))-2
 y1=math.ceil(max(w['box'][3] for w in words))+2
 row_center=center(envelope(words));lower=0;upper=3264
 for other in neighbors:
  if other['id']==row['id'] or other['page']!=row['page'] or not other.get('words'):continue
  other_center=center(envelope(other['words']));original_center=rotate_point(*other_center,-rotation(other))
  _,oy=rotate_point(*original_center,angle)
  if oy<row_center[1]:lower=max(lower,math.floor((oy+row_center[1])/2)+1)
  elif oy>row_center[1]:upper=min(upper,math.ceil((oy+row_center[1])/2))
 y0=max(lower,0,y0);y1=min(upper,3264,y1);result['rowRegionY']=[y0,y1]
 if y1-y0<3:
  result['rowLevelGuard']=result['firstFailureReason']='insufficient-vertical-glyph-region'
  result['words']=[{'wordID':w['id'],'lexicalWordIndex1':i+1,'frozenWordBox':w['box'],
   'evaluationStage':'not-reached-row-level-guard','sourceRegion':None} for i,w in enumerate(words)]
  return result
 for index in range(len(words)):
  rec=trace_word(image,words,index,y0,y1,result['firstFailureReason'] is not None)
  result['words'].append(rec)
  if result['firstFailureReason'] is None and rec['firstGuardReason']:
   result.update(firstFailureReason=rec['firstGuardReason'],firstFailedWordID=rec['wordID'],
    firstFailedLexicalWordIndex1=index+1,firstFailureBoundarySides=rec['firstGuardBoundarySides'])
 return result

def compare_baseline(rows, baseline):
 unknown=baseline['procedureCounts']['unknownRows'];expected={r['rowId']:r['reason'] for r in unknown}
 optical={'incomplete-word-geometry','no-lexical-words','insufficient-vertical-glyph-region',*WORD_GUARDS}
 excluded=[rid for rid,reason in expected.items() if reason not in optical]
 compared=[r for r in rows if r['rowID'] not in excluded]
 mismatches=[{'rowID':r['rowID'],'expected':expected.get(r['rowID']),'actual':r['firstFailureReason']}
  for r in compared if expected.get(r['rowID'])!=r['firstFailureReason']]
 return {'scope':'First optical guard only; post-span nonpositive-gap guard is not evaluated.',
  'comparedRows':len(compared),'excludedPostOpticalBaselineRows':len(excluded),
  'matchingRows':len(compared)-len(mismatches),'mismatches':mismatches,'allComparedMatch':not mismatches}

def private_output(path,research):
 path=Path(path).resolve();checkout=research.parent.parent
 need(not any(p.casefold()=='public' for p in path.parts),'output-must-be-private')
 need(not path.is_relative_to(checkout),'output-must-be-outside-entire-checkout')
 need(not path.exists() and path.parent.is_dir(),'fresh-output-parent-required')
 return path

def registered_inputs(protocol_path,research,registration):
 need(re.fullmatch('[0-9a-f]{40}',registration or '') is not None,'registration-SHA-required')
 need(protocol_path.resolve()==(research/PROTOCOL_REL).resolve(),'protocol-path-mismatch')
 need(protocol_path.stat().st_size<=1000000,'protocol-cap')
 protocol_bytes=protocol_path.read_bytes();protocol=json.loads(protocol_bytes)
 need(protocol.get('version')==1 and protocol.get('batchId')==BATCH_ID,'protocol-identity')
 need(protocol.get('definition')==DEFINITION,'protocol-definition-mismatch')
 need(protocol.get('sourceHashes')==SOURCES,'source-pin-population-or-value-mismatch')
 scripts=protocol.get('scriptHashes');need(isinstance(scripts,dict) and set(scripts)=={OLD_REL,SELF_REL},'script-pin-population')
 need(scripts[OLD_REL]==OLD_SHA,'old-detector-source-pin')
 pins={**SOURCES,**scripts,PROTOCOL_REL:digest(protocol_bytes)}
 for relative,expected in pins.items():
  need(re.fullmatch('[0-9a-f]{64}',expected or '') is not None,'invalid-pin')
  path=(research/relative).resolve();need(path.is_relative_to(research),'pin-path-escape')
  need(path.is_file() and path.stat().st_size<=20000000,'source-blob-cap-or-missing')
  need(digest(path.read_bytes())==expected,'working-file-pin-mismatch')
  saved=subprocess.run(['git','show',registration+':public/research/'+relative],cwd=research,
   stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20,check=False)
  need(saved.returncode==0 and digest(saved.stdout)==expected,'registration-Git-blob-mismatch')
 return protocol,digest(protocol_bytes)

def safe_summary(rows,comparison):
 reasons=Counter(r['firstFailureReason'] or 'optical-pass' for r in rows)
 words=[w for r in rows for w in r['words']]
 return {'rows':len(rows),'wordRegionsRecorded':len(words),
  'wordRegionsOpticallyEvaluated':sum('firstGuardReason' in w for w in words),
  'rowFirstGuardCounts':dict(reasons),'wordFirstGuardCounts':dict(Counter(
   w['firstGuardReason'] or 'optical-pass' for w in words if 'firstGuardReason' in w)),
  'counterfactualAfterFirstWordFailureRegions':sum(w['evaluationStage']=='counterfactual-after-first-word-failure' for w in words),
  'columnDiagnosticsAfterEarlierGuard':sum(w.get('columnDiagnosticsCounterfactual',False) for w in words),
  'baselineComparedRows':comparison['comparedRows'],'baselineMatchingRows':comparison['matchingRows'],
  'baselineMismatchingRows':len(comparison['mismatches']),
  'postOpticalBaselineRowsExcluded':comparison['excludedPostOpticalBaselineRows']}

def self_test():
 np,Image=dependencies();checks=0
 def word(i,x):return {'id':'synthetic-w'+str(i),'text':'Control','box':[x,20,x+10,30]}
 def row(words,id='synthetic-row',status='complete'):
  return {'id':id,'page':75,'words':words,'geometryStatus':status,'geometryRotationCCW':0,
   'locator':{'rotate_ccw_degrees':0}}
 def rectangle(image,box,color):image.paste(color,box)
 ws=[word(1,20),word(2,50),word(3,80)];r=row(ws)
 image=Image.new('RGB',(120,60),'white')
 for w in ws:rectangle(image,(int(w['box'][0]),20,int(w['box'][0])+9,29),'black')
 good=trace_row(image,r,[r]);need(good['firstFailureReason'] is None and len(good['words'])==3,'synthetic-ordinary-glyph');checks+=1
 bad=image.copy();rectangle(bad,(8,20,9,27),'black');rectangle(bad,(80,18,89,19),'black')
 traced=trace_row(bad,r,[r]);need(traced['firstFailureReason']=='ink-touches-word-region-boundary' and traced['firstFailedWordID']=='synthetic-w1','synthetic-first-failure');checks+=1
 need(traced['words'][1]['evaluationStage']=='counterfactual-after-first-word-failure' and traced['words'][2]['firstGuardReason']=='ink-touches-vertical-region-boundary','synthetic-continue-all-words');checks+=1
 vertical=image.copy();rectangle(vertical,(20,18,29,19),'black');v=trace_row(vertical,r,[r])
 need(v['firstFailureReason']=='ink-touches-vertical-region-boundary' and v['firstFailedWordID']=='synthetic-w1' and v['words'][0]['columnDiagnosticsCounterfactual'],'synthetic-in-word-vertical-guard');checks+=1
 blank=Image.new('RGB',(120,60),'white');b=trace_row(blank,r,[r]);need(b['firstFailureReason']=='no-robust-ink-rows' and b['firstFailedWordID']=='synthetic-w1','synthetic-in-word-no-rows');checks+=1
 sparse=blank.copy();sparse.putpixel((20,20),(0,0,0));sparse.putpixel((22,20),(0,0,0))
 need(trace_row(sparse,r,[r])['firstFailureReason']=='no-robust-ink-columns','synthetic-no-columns');checks+=1
 orange=Image.new('RGB',(120,60),(240,150,60))
 for w in ws:rectangle(orange,(int(w['box'][0]),20,int(w['box'][0])+9,29),'white')
 o=trace_row(orange,r,[r]);need(o['firstFailureReason']=='no-robust-ink-rows' and o['words'][0]['selectedByOriginalRule']['whiteScanlines']==0,'synthetic-unrepaired-orange-polarity');checks+=1
 inverse=Image.new('RGB',(120,60),'black')
 for w in ws:rectangle(inverse,(int(w['box'][0]),20,int(w['box'][0])+9,29),'white')
 need(trace_row(inverse,r,[r])['firstFailureReason'] is None,'synthetic-white-on-black');checks+=1
 mixed=Image.new('RGB',(120,60),'black');rectangle(mixed,(0,25,120,60),'white')
 for w in ws:
  x=int(w['box'][0]);rectangle(mixed,(x,20,x+9,25),'white');rectangle(mixed,(x,25,x+9,29),'black')
 pm=trace_row(mixed,r,[r])['words'][0]['selectedByOriginalRule'];need(pm['blackScanlines']==7 and pm['whiteScanlines']==7 and len(pm['runs'])==2,'synthetic-scanline-polarity-summary');checks+=1
 inc=trace_row(image,row(ws,status='ambiguous'),[]);need(inc['firstFailedWordID'] is None and inc['rowLevelGuard']=='incomplete-word-geometry' and len(inc['words'])==3,'synthetic-row-guard-null-word');checks+=1
 empty=trace_row(image,row([]),[]);need(empty['rowLevelGuard']=='no-lexical-words' and empty['firstFailedWordID'] is None,'synthetic-empty-row-null-word');checks+=1
 near=[]
 for label,y in [('above',24.25),('below',24.75)]:
  rr=row([word(1,20)],id=label);rr['words'][0]['box']=[20,y,30,y+1];near.append(rr)
 tiny=trace_row(image,r,near);need(tiny['rowLevelGuard']=='insufficient-vertical-glyph-region' and tiny['firstFailedWordID'] is None,'synthetic-pre-loop-envelope-null-word');checks+=1
 comp=compare_baseline([good,traced],{'procedureCounts':{'unknownRows':[{'rowId':'synthetic-row','reason':'ink-touches-word-region-boundary'}]}})
 need(comp['matchingRows']==1 and len(comp['mismatches'])==1,'synthetic-baseline-mismatch-detected');checks+=1
 summary=safe_summary([traced],compare_baseline([traced],{'procedureCounts':{'unknownRows':[{'rowId':'synthetic-row','reason':traced['firstFailureReason']}]}}))
 need('synthetic-w' not in json.dumps(summary) and 'sourceRegion' not in json.dumps(summary),'synthetic-safe-aggregate');checks+=1
 return {'passed':True,'syntheticAssertions':checks,'targetSourceReads':0,'targetMeasurements':0,
  'gapCalculations':0,'gapBits':0,'decoders':0,'candidateChecks':0,'networkRequests':0,
  'controls':['ordinary-black/white','horizontal-and-vertical-first-guard','continue-after-first-failure',
   'no-row/no-column','unrepaired-orange-polarity','scanline-polarity-runs','row-guard-null-word',
   'baseline-mismatch','aggregate-no-identifiers']}

def run(args):
 started=utc();research=Path(__file__).resolve().parent.parent
 need(Path(__file__).resolve()==(research/SELF_REL).resolve(),'run-only-published-script')
 out=private_output(args.out,research)
 protocol,protocol_sha=registered_inputs(Path(args.protocol),research,args.registration_commit)
 controls=self_test();out.mkdir(mode=0o700)
 result={'version':1,'testId':TEST_ID,'batchId':BATCH_ID,'startedAtUTC':started,
  'registrationCommit':args.registration_commit,'protocolSha256':protocol_sha,
  'sourceHashes':protocol['sourceHashes'],'scriptHashes':protocol['scriptHashes'],
  'controls':controls,'scopeComplete':False,'status':'execution-incomplete','counts':{},
  'postSpanGapGuardChecked':False,'semanticOrKeyConclusion':None,
  'activity':{'gapCalculations':0,'gapRowMedians':0,'gapBits':0,'decoders':0,'candidateChecks':0,
   'formatChecks':0,'networkRequests':0,'pixelOrCropOutputs':0,'sourceRepair':0}}
 try:
  spec=importlib.util.spec_from_file_location('frozen_geometry_source_loaders',research/OLD_REL)
  old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
  def forbidden(*_a,**_k):raise GuardError('forbidden-legacy-target-function')
  for name in ['g04','binary_decodes','run','basic_self_test']:setattr(old,name,forbidden)
  canonical=json.loads((research/'sources/printed-lines.json').read_text())['rows']
  geometry,artifact=old.load_geometry(canonical);images,image_inventory=old.load_images()
  need(len(geometry)==142 and sum(len(r['words']) for r in geometry)==1243,'source-population-mismatch')
  punct=[{'rowID':r['id'],'tokenID':p['id'],'text':p['text'],'box':p.get('box'),
   'center':p.get('center'),'originalUprightPolygon':p.get('originalUprightPolygon'),
   'verified':p.get('verified')} for r in artifact['rows'] for p in r['punctuationOnlyTokens']]
  need(len(punct)==15 and all(p['box'] is None and p['center'] is None and p['originalUprightPolygon'] is None for p in punct),'punctuation-population-or-null-model-mismatch')
  rows=[trace_row(images[row['page']],row,geometry) for row in geometry]
  baseline=json.loads((research/BASELINE_REL).read_text());need(baseline['testId']=='G04','baseline-identity')
  saved=baseline['procedureCounts']
  need(len(saved['unknownRows'])==38 and saved['rowsMeasured']==104 and saved['gapsMeasured']==811
   and saved['completePages']==[] and saved['labeledDecodes']==0,'recorded-baseline-counts-mismatch')
  comparison=compare_baseline(rows,baseline)
  trace={'version':1,'testId':TEST_ID,'registrationCommit':args.registration_commit,
   'sourceImages':image_inventory,'rows':rows,'punctuationUnlocated':punct,
   'baselineOpticalComparison':comparison,'postSpanGapGuardChecked':False,
   'sourceRepairPerformed':False,'counterfactualDiagnosticsAreNotLegacyBaseline':True}
  trace_bytes=(json.dumps(trace,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
  need(len(trace_bytes)<=24000000,'trace-output-cap')
  fd=os.open(out/'TRACE.private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(trace_bytes)
  result.update(counts=safe_summary(rows,comparison),punctuationTokens=15,
   punctuationAllBoxesNull=True,traceSHA256=digest(trace_bytes),scopeComplete=True,
   status='trace-complete-baseline-match' if comparison['allComparedMatch'] else 'trace-complete-baseline-mismatch')
 except Exception as error:
  result.update(status='inconclusive-execution-failure',errorClass=type(error).__name__,
   error='Source trace failed; inspect private environment. No source/key exclusion.')
 finally:
  result['completedAtUTC']=utc()
  fd=os.open(out/'RESULT.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:result[k] for k in ['testId','status','scopeComplete','counts','completedAtUTC']}))

def main():
 parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
 group.add_argument('--definition',action='store_true');group.add_argument('--self-test',action='store_true');group.add_argument('--run',action='store_true')
 for name in ['protocol','registration-commit','out']:parser.add_argument('--'+name)
 args=parser.parse_args()
 if not args.run:
  need(not any([args.protocol,args.registration_commit,args.out]),'definition-controls-reject-target-arguments')
  print(json.dumps(DEFINITION if args.definition else self_test(),indent=2));return
 need(all([args.protocol,args.registration_commit,args.out]),'run-requires-protocol-registration-out')
 run(args)

if __name__=='__main__':
 try:main()
 except Exception as error:
  print(json.dumps({'status':'inconclusive-precondition-failure','errorClass':type(error).__name__,
   'detail':'Precondition/control failed; no target conclusion.'}),file=sys.stderr)
  sys.exit(2)
