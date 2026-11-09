#!/usr/bin/env python3
"""Audit old greedy phrase geometry without modifying any historical artifacts."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis_outputs/continuation_20261109/phrase_box_audit'
OUT.mkdir(parents=True,exist_ok=True)
M=json.loads((ROOT/'analysis_outputs/3d_article_map/article_3d_map_data.json').read_text())
OLD=json.loads((ROOT/'analysis_outputs/3d_article_map/exact_highres_reflection_geometry.json').read_text())
G=json.loads((ROOT/'analysis_outputs/3d_article_map/reflected_highlight_graph.json').read_text())
P={p['page']:p for p in M['pages']}
norm=lambda x:re.sub('[^a-z0-9]','',x.lower())
def tokens(x):return [norm(t) for t in re.findall(r"[A-Za-z0-9’'$%-]+",x) if norm(t)]
def bbox(words):
 return [min(w['box'][0] for w in words),min(w['box'][1] for w in words),max(w['box'][2] for w in words),max(w['box'][3] for w in words)]
rows=[]
for r in OLD['rows']:
 ws=P[r['page']]['words'];ts=[norm(w.get('token') or w['text']) for w in ws];wanted=tokens(r['text']);exact=[]
 for i in range(len(ts)-len(wanted)+1):
  if ts[i:i+len(wanted)]==wanted:exact.append([w['index'] for w in ws[i:i+len(wanted)]])
 # Spacing/hyphen-insensitive exact match, preserving complete word boundaries.
 compact=''.join(ts);starts=[];pos=0
 for t in ts:starts.append(pos);pos+=len(t)
 ends=[p+len(t) for p,t in zip(starts,ts)];want=''.join(wanted);compact_matches=[];pos=compact.find(want)
 while pos>=0:
  if pos in starts and pos+len(want) in ends:
   i=starts.index(pos);j=ends.index(pos+len(want));compact_matches.append(dict(indices=[w['index'] for w in ws[i:j+1]],box=bbox(ws[i:j+1])))
  pos=compact.find(want,pos+1)
 indices=r['wordIndexes'];oldcontig=bool(indices) and all(b-a==1 for a,b in zip(indices,indices[1:]));edges=[e for e in G['edges'] if e['targetId']==r['id'] and e['strength'] in ['strong','medium']]
 rows.append(dict(id=r['id'],page=r['page'],text=r['text'],oldMatchedWords=r['matchedWords'],oldMatchRatio=r['matchRatio'],oldIndices=indices,oldIndicesContiguous=oldcontig,oldBox=r['box'],exactTokenMatches=exact,compactExactMatches=compact_matches,mediumStrongEdges=len(edges)))
summary=dict(rows=len(rows),oldFullRatio=sum(r['oldMatchRatio']==1 for r in rows),oldContiguousIndices=sum(r['oldIndicesContiguous'] for r in rows),strictContiguousExact=sum(bool(r['exactTokenMatches']) for r in rows),compactContiguousExact=sum(bool(r['compactExactMatches']) for r in rows),mediumStrongEdges=sum(r['mediumStrongEdges'] for r in rows),mediumStrongTargetRows=sum(bool(r['mediumStrongEdges']) for r in rows),mediumStrongTargetsWithExactCompact=sum(bool(r['mediumStrongEdges']) and bool(r['compactExactMatches']) for r in rows),mediumStrongEdgesWithNoncontiguousOldIndices=sum(r['mediumStrongEdges'] for r in rows if not r['oldIndicesContiguous']))
result=dict(summary=summary,rows=rows,dependency=['analyze_exact_highres_reflection_geometry.py:62-78 greedily scans forward across entire page and skips wanted tokens it cannot find.','analyze_exact_highres_reflection_geometry.py:104-105 unions every matched word regardless contiguity/completeness.','analyze_reflected_highlight_graph.py:17 consumes the resulting exact_highres_reflection_geometry.json.','analyze_reflected_highlight_graph.py:47-70 promotes those overlap records into medium/strong graph edges.'],scope='Invalidates the all-17 graph statistic as evidence for intentional phrase-aligned overlap. Does not invalidate later independent scan-native target boxes or independently supported p76 clues.')
(OUT/'phrase_box_audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
lines=['# Historical phrase geometry audit','','## Summary','',json.dumps(summary,indent=2),'','## Cause and dependency','',*result['dependency'],'',result['scope'],'','## Per-span audit','','| ID | Page | Old ratio | Old indices contiguous | Exact compact phrase found | Medium/strong edges |','|---|---:|---:|---|---|---:|']
for r in rows:lines.append(f"| {r['id']} | {r['page']} | {r['oldMatchRatio']} | {r['oldIndicesContiguous']} | {bool(r['compactExactMatches'])} | {r['mediumStrongEdges']} |")
lines+=['','## Examples','']
for r in rows:
 if r['page']==76:
  lines+=['- '+r['text']+': old box `'+str(r['oldBox'])+'`, indices `'+str(r['oldIndices'])+'`; exact compact matches `'+str(r['compactExactMatches'])+'`.']
(OUT/'phrase_box_audit.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary))
