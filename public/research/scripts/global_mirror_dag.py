#!/usr/bin/env python3
"""Exact candidate-set union over a finite text DAG.
Import and --self-test do not read puzzle inputs. The separate registered runner
supplies source DAGs only after protocol/source/code pin validation.
"""
from __future__ import annotations
from collections import deque
from functools import lru_cache
import itertools,re

B58=set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
HEX=set('0123456789abcdefABCDEF')
PHRASE_LENGTHS=(12,15,18,21,24)
END=-1

class LimitExceeded(RuntimeError):pass
class Budget:
 def __init__(self,states=1000000,candidates=1000000):self.maximumStates=states;self.maximumCandidates=candidates;self.states=0;self.candidates=0
 def state(self):
  self.states+=1
  if self.states>self.maximumStates:raise LimitExceeded('State cap exceeded; no complete negative')
 def candidate(self):
  self.candidates+=1
  if self.candidates>self.maximumCandidates:raise LimitExceeded('Candidate cap exceeded; no complete negative')


def graph(rows,mode='words-joined',reverse=False):
 """Each row option is a nonempty source token or None for row omission.

 Spaces in spaced form appear only between selected words. A pair of boundary
 states remembers whether a word has already been selected. Initials use the
 first Unicode alphanumeric code point, exactly as the existing projection.
 """
 if mode not in ('words-spaced','words-joined','initials'):raise ValueError('mode')
 rows=list(reversed(rows)) if reverse else rows
 if any(not row or any(v is not None and (not isinstance(v,str) or not v) for v in row) for row in rows):raise ValueError('Invalid source alternatives')
 boundary={(i,started):2*i+int(started) for i in range(len(rows)+1) for started in (False,True)}
 edges={x:set() for x in boundary.values()};chars={};next_id=len(edges)
 for i,options in enumerate(rows):
  for started in (False,True):
   for option in options:
    src=boundary[i,started]
    if option is None:edges[src].add(boundary[i+1,started]);continue
    text=option if mode!='initials' else next((c for c in option if c.isalnum()),'')
    if mode=='words-spaced' and started:text=' '+text
    target=boundary[i+1,True]
    if not text:edges[src].add(target);continue
    ids=list(range(next_id,next_id+len(text)));next_id+=len(text)
    for node,c in zip(ids,text):chars[node]=c;edges[node]=set()
    edges[src].add(ids[0])
    for a,b in zip(ids,ids[1:]):edges[a].add(b)
    edges[ids[-1]].add(target)
 terminal={boundary[len(rows),False],boundary[len(rows),True]}
 @lru_cache(None)
 def closure(node):
  if node in chars:return frozenset([node])
  if node in terminal:return frozenset([END])
  return frozenset(y for x in edges[node] for y in closure(x))
 first=set(closure(boundary[0,False]));successor={n:set(y for x in edges[n] for y in closure(x)) for n in chars}
 reachable=set();queue=list(first)
 while queue:
  node=queue.pop()
  if node in reachable:continue
  reachable.add(node)
  if node!=END:queue.extend(successor[node])
 chars={n:chars[n] for n in reachable if n!=END};successor={n:successor[n] for n in chars}
 return {'first':first,'chars':chars,'next':successor,'nodes':len(reachable)}


def candidate_union(g,dictionary,budget=None,result=None):
 """Return unique shape values, not stream occurrences or unique-form counts.

 A complete zero result can be validated using the pinned strict validators.
 Any cap failure invalidates completeness. Four formats match batch20_common.
 """
 budget=budget or Budget();result=result if result is not None else {k:set() for k in ('wif','minikey','hex64','bip39')};chars=g['chars'];nexts=g['next']
 def add(kind,value):
  if value not in result[kind]:
   result[kind].add(value)
   budget.candidate()
 # WIF/minikey are substring patterns with no external boundary requirement.
 for kind,starts,lengths in [('wif',set('5KL'),(51,52)),('minikey',{'S'},(22,30))]:
  visited=set();stack=[(n,c) for n,c in chars.items() if c in starts]
  while stack:
   node,value=stack.pop();state=(node,value)
   if state in visited:continue
   visited.add(state);budget.state()
   if len(value) in lengths:add(kind,value)
   if len(value)<max(lengths):
    stack.extend((n,value+chars[n]) for n in nexts[node] if n!=END and chars[n] in B58)
 # Exact 64hex records need a realizable nonhex (or stream edge) on both sides.
 predecessors={n:set() for n in chars}
 for n,ns in nexts.items():
  for m in ns:
   if m!=END:predecessors[m].add(n)
 start_allowed={n for n,c in chars.items() if c in HEX and (n in g['first'] or any(chars[p] not in HEX for p in predecessors[n]))}
 visited=set();stack=[(n,chars[n]) for n in start_allowed]
 while stack:
  node,value=stack.pop();state=(node,value)
  if state in visited:continue
  visited.add(state);budget.state()
  if len(value)==64:
   if any(n==END or chars[n] not in HEX for n in nexts[node]):add('hex64',value)
  else:stack.extend((n,value+chars[n]) for n in nexts[node] if n!=END and chars[n] in HEX)
 # Incremental ASCII lexical tokenizer. Common's only non-ASCII token character
 # is the curly apostrophe. Pending apostrophes require one-character lookahead.
 dictionary=set(dictionary);prefixes={w[:i] for w in dictionary for i in range(1,len(w)+1)}
 def complete(prefix,history):
  if not prefix:return (),history
  if prefix not in dictionary:return (),()
  new=history+(prefix,)
  for length in PHRASE_LENGTHS:
   if len(new)>=length:add('bip39',' '.join(new[-length:]))
  return (),new[-23:]
 def consume(state,c):
  prefix,pending,history=state
  alnum=c.isascii() and c.isalnum();apostrophe=c in ("'",'’')
  if c=='␞':
   _,history=complete(prefix,history)
   return '',False,()
  if pending:
   if alnum:return '#',False,()  # one regex token containing an apostrophe
   _,history=complete(prefix,history);prefix='';pending=False
  if alnum:
   text=prefix+c.lower() if prefix!='#' else '#'
   if text not in prefixes:return '#',False,()
   return text,False,history
  if apostrophe and prefix:return prefix,True,history
  _,history=complete(prefix,history)
  return '',False,history
 initial=('',False,());visited=set();stack=[(n,initial) for n in g['first']]
 while stack:
  node,state=stack.pop();mark=(node,state)
  if mark in visited:continue
  visited.add(mark);budget.state()
  if node==END:
   complete(state[0],state[2]);continue
  new=consume(state,chars[node]);stack.extend((n,new) for n in nexts[node])
 return result


def plain_readings(rows,mode,reverse=False):
 for path in itertools.product(*rows):
  words=[w for w in path if w is not None]
  if reverse:words=words[::-1]
  if mode=='words-spaced':yield ' '.join(words)
  elif mode=='words-joined':yield ''.join(words)
  else:yield ''.join(next((c for c in w if c.isalnum()),'') for w in words)


def self_test(common):
 words,indexes=common.wordlist();cases=[]
 mini='S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'
 wif=common.b58encode(b'\x80'+bytes.fromhex('00'*31+'01')+b'\x01'+common.sha256(common.sha256(b'\x80'+bytes.fromhex('00'*31+'01')+b'\x01'))[:4])
 cases.extend([
  [[None,'prefix::'],[mini[:14],mini[:13]+'n'],[mini[14:]],[None,'::suffix']],
  [['!',None,'A'],['0'*31],['0'*32+'1'],['!',None,'F']],
  [[wif[:17]],[wif[17:35]],[wif[35:]],['x',None]],
  [[w] for w in ['abandon']*11+['about']],
 ])
 cases.extend([
  [['abandon']]*5+[['abandon','INVALID']]+[['abandon']]*5+[['about']],
  [['abandon']]*6+[['␞']]+[['abandon']]*5+[['about']],
  [['abandon']]*10+[['aban'],['don']]+[['about']],
  [['abandon']]*10+[["abandon'",'abandon’'],[':',None]]+[['about']],
  [['abandon']]*10+[["aban'",'aban’'],['don']]+[['about']],
  [['abandon']]*10+[["abandon''about",'abandon’’about']],
  [[None],[None]],
 ])
 import random
 rng=random.Random(20261110)
 pool=[None,'a','abandon','about','ability','aban','don',"'",'’',':','␞','I','S',mini[:15],mini[15:],'0'*16,'A'*16,'12','é','—']
 for _ in range(100):
  cases.append([[rng.choice(pool) for __ in range(rng.randint(1,3))] for ___ in range(rng.randint(2,5))])
 for _ in range(30):
  rows=[[w] for w in ['abandon']*11+['about']]
  for pos in rng.sample(range(12),3):rows[pos]=[rng.choice(['abandon','ability','about','INVALID',None,"abandon'",'␞']) for __ in range(2)]
  cases.append(rows)
 controls=0
 for rows in cases:
  for mode in ('words-spaced','words-joined','initials'):
   for reverse in (False,True):
    forms=set(plain_readings(rows,mode,reverse));expected={k:set(v for text in forms for v in common.shape_values(k,text,indexes)) for k in ('wif','minikey','hex64','bip39')}
    b=Budget();actual=candidate_union(graph(rows,mode,reverse),words,b)
    assert actual==expected,(controls,mode,reverse,{k:(len(actual[k]),len(expected[k])) for k in expected})
    controls+=1
 # A cap failure cannot be a zero candidate result.
 try:candidate_union(graph([['alpha']]),words,Budget(states=0))
 except LimitExceeded:pass
 else:raise AssertionError('State cap must fail')
 partial={k:set() for k in ('wif','minikey','hex64','bip39')}
 try:candidate_union(graph([[mini]]),words,Budget(candidates=0),partial)
 except LimitExceeded:assert sum(map(len,partial.values()))==1
 else:raise AssertionError('Candidate cap must fail and preserve partial candidate')
 return {'passed':True,'syntheticGraphCases':controls,'targetInputsRead':False,'targetShapeChecks':0,'targetChecksumChecks':0,'networkQueries':0}

if __name__=='__main__':
 import argparse,json
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--self-test',action='store_true',required=True)
 p.parse_args()
 import batch20_common
 print(json.dumps(self_test(batch20_common),indent=2))
