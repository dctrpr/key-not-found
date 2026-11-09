#!/usr/bin/env python3
"""Align the two repeated copies and inspect only actual rewrap differences."""
from pathlib import Path
import json,re,hashlib
P=Path(__file__).resolve().parent
D=json.loads((P/'printed_lines_and_streams.json').read_text())
RR={r['rawLine']:r for r in D['rows'] if r['page']==3 and r['region']=='col2'}
shared=RR[40]['text'];cut=shared.index('Those')
C1=[dict(row=i,text=RR[i]['text']) for i in range(35,40)]+[dict(row=40,text=shared[:cut].strip())]
C2=[dict(row=40,text=shared[cut:].strip())]+[dict(row=i,text=RR[i]['text']) for i in range(41,46)]
# 12-step is one lexical token; line-ending hyphen after Shitcoiners remains in source text.
RX=r"[A-Za-z0-9]+(?:[-’'][A-Za-z0-9]+)*"
def toks(s):return re.findall(RX,s)
def describe(C):
 out=[];ws=[]
 for r in C:
  t=toks(r['text']);start=len(ws)+1;ws+=t
  out.append(dict(**r,tokenStart=start,tokenEnd=len(ws),tokens=t,first=t[0],last=t[-1],chars=len(r['text'])))
 return dict(lines=out,words=ws,firstwords=' '.join(x['first'] for x in out),lastwords=' '.join(x['last'] for x in out),initials=''.join(x['first'][0] for x in out),terminals=''.join(x['last'][-1] for x in out),boundaries=[x['tokenEnd'] for x in out])
A,B=describe(C1),describe(C2)
assert A['words']==B['words']
changes=[]
for i,(a,b) in enumerate(zip(A['lines'],B['lines']),1):
 if a['first']!=b['first'] or a['last']!=b['last'] or a['chars']!=b['chars']:
  changes.append(dict(fragmentLine=i,row1=a['row'],row2=b['row'],first1=a['first'],first2=b['first'],last1=a['last'],last2=b['last'],chars1=a['chars'],chars2=b['chars'],charDelta=b['chars']-a['chars']))
alignment=[]
for i,w in enumerate(A['words'],1):
 a=next(x for x in A['lines'] if x['tokenStart']<=i<=x['tokenEnd']);b=next(x for x in B['lines'] if x['tokenStart']<=i<=x['tokenEnd'])
 alignment.append(dict(index=i,word=w,row1=a['row'],row2=b['row'],first1=i==a['tokenStart'],first2=i==b['tokenStart'],last1=i==a['tokenEnd'],last2=i==b['tokenEnd']))
only1=sorted(set(A['boundaries'])-set(B['boundaries']));only2=sorted(set(B['boundaries'])-set(A['boundaries']))
# Source directly singles out rewrap difference: the words crossed by the moved boundary.
moved=[r for r in alignment if r['row1']-35 != r['row2']-40]
# Read region-local first/last words and letters, retaining both whole lines and copy fragments.
streams={}
for label,C in [('copy1',A),('copy2',B)]:
 for parity,ii in [('all',None),('odd',0),('even',1)]:
  ls=C['lines'] if ii is None else C['lines'][ii::2]
  for order,ls2 in [('forward',ls),('reverse',ls[::-1])]:
   for method in ['first','last']:
    ww=[x[method] for x in ls2]
    streams[f'{label}:{parity}:{order}:{method}_words']=' '.join(ww)
    streams[f'{label}:{parity}:{order}:{method}_initials']=''.join(w[0] for w in ww)
    streams[f'{label}:{parity}:{order}:{method}_terminals']=''.join(w[-1] for w in ww)
   streams[f'{label}:{parity}:{order}:whole_fragments']='\n'.join(x['text'] for x in ls2)
for label,rows in [('physical_span1',range(35,41)),('physical_span2',range(40,46))]:
 for method in ['first','last']:
  ww=[toks(RR[i]['text'])[0 if method=='first' else -1] for i in rows]
  streams[label+':'+method+'_words']=' '.join(ww)
  streams[label+':'+method+'_initials']=''.join(w[0] for w in ww)
for field in ['first','last']:
 changes_at_edge=[(a[field],b[field]) for a,b in zip(A['lines'],B['lines']) if a[field]!=b[field]]
 streams[field+'_changed_pairs']=' / '.join(a+' -> '+b for a,b in changes_at_edge)
 streams[field+'_changed_copy1_words']=' '.join(a for a,b in changes_at_edge)
 streams[field+'_changed_copy2_words']=' '.join(b for a,b in changes_at_edge)
streams['rewrap_displaced_tokens']=' '.join(r['word'] for r in moved)
rec=[r for r in D['rows'] if r['page']==2 and r['region']=='col2' and r['rawLine']>=39]
for method in ['first','last']:
 ww=[toks(r['text'])[0 if method=='first' else -1] for r in rec]
 streams['recursion_paragraph:'+method+'_words']=' '.join(ww)
 streams['recursion_paragraph:'+method+'_initials']=''.join(w[0] for w in ww)
# Direct literal checks. No secret derivation hashes; hashing is WIF checksum only.
BASE58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def valid_wif(s):
 try:
  n=0
  for c in s:n=n*58+BASE58.index(c)
  bb=n.to_bytes((n.bit_length()+7)//8,'big');bb=b'\0'*(len(s)-len(s.lstrip('1')))+bb
  return len(bb) in (37,38) and bb[0]==128 and (len(bb)==37 or bb[-5]==1) and hashlib.sha256(hashlib.sha256(bb[:-4]).digest()).digest()[:4]==bb[-4:]
 except ValueError:return False
hits=[]
for k,s in streams.items():
 for direction,v in [('normal',''.join(s.split())),('reverse',''.join(s.split())[::-1])]:
  for w in re.findall(r'(?<![1-9A-HJ-NP-Za-km-z])[5KL][1-9A-HJ-NP-Za-km-z]{50,51}(?![1-9A-HJ-NP-Za-km-z])',v):
   if valid_wif(w):hits.append(dict(stream=k,direction=direction,type='WIF',value=w))
  for w in re.findall(r'(?<![A-Za-z0-9])[a-fA-F0-9]{64}(?![A-Za-z0-9])',v):hits.append(dict(stream=k,direction=direction,type='hex64',value=w))
  if len(v)==32 and v.isascii():hits.append(dict(stream=k,direction=direction,type='ASCII32_shape_only',value=v))
out=dict(copies={'1':A,'2':B},alignment=alignment,changedLines=changes,boundariesOnly1=only1,boundariesOnly2=only2,rewrapDisplacedTokens=moved,streams=streams,hits=hits,summary=dict(lexicalTokensPerCopy=len(A['words']),numberSplitTokensPerCopy=len(re.findall(r'[A-Za-z]+|[0-9]+',' '.join(A['words']))),sameLexicalTokens=A['words']==B['words'],copyFragmentsPerCopy=6,changedBoundaryCount=1,streams=len(streams),literalHits=len(hits)))
(P/'duplicate_wrap_alignment.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
lines=['# Duplicate paragraph: exact wrap comparison','','Printed p80, center column. Both copies have 27 lexical tokens (28 if 12-step is split into numeric 12 and word step). The source differs in physical wrapping and the terminal Shitcoiners hyphen. The duplicate is not byte-for-byte identical.','', '| Fragment | Copy1 row | Copy1 text | Copy2 row | Copy2 text |','|---|---|---|---|---|']
for i,(a,b) in enumerate(zip(A['lines'],B['lines']),1):lines.append(f"|{i}|{a['row']}|{a['text']}|{b['row']}|{b['text']}|")
lines+=['','Copy2 starts inside physical row 40; copy-fragment first words are therefore distinct from genuine whole-line first words. Both are saved, with no choosing between them.','','## Results','',f"- Token equality after punctuation/linebreak normalization: {out['summary']['sameLexicalTokens']}",f"- Line-end token positions, copy1: {A['boundaries']}",f"- Line-end token positions, copy2: {B['boundaries']}",f"- Word crossed by moved line boundary: {streams['rewrap_displaced_tokens']}",f"- Copy1 fragment first words: {A['firstwords']}",f"- Copy2 fragment first words: {B['firstwords']}",f"- Copy1 fragment last words: {A['lastwords']}",f"- Copy2 fragment last words: {B['lastwords']}",f"- Firstword change: {streams['first_changed_pairs']}",f"- Lastword change: {streams['last_changed_pairs']}",f"- Declared streams: {len(streams)}; literal key hits: {len(hits)}.",'','The rewrap moves exactly the already printed term 12-step between the first two fragments. Reading changed first words supplies recovery and 12-step, which only reconstruct the article’s existing recovery-program phrase. Odd/even fragment readings, their initials, reversed orders, true physical-line leaders and endings, and the nearby recursion-paragraph line edges produce no independently readable new instruction or standard key. No plaintext was hashed into a secret; no wordlist filtering or arbitrary deletion was performed. This is a negative result for the bounded rewrap hypothesis, not proof that the column contains no key.','', '## All declared streams','']
for k,s in streams.items():lines+=['### '+k,'','```text',s,'```','']
(P/'duplicate_wrap_report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(out['summary']));print('moved',streams['rewrap_displaced_tokens']);print('hits',hits)
