#!/usr/bin/env python3
"""Source-linked printed-line checks on Issue27, without corpus word filtering/hashes."""
import json,re,csv,hashlib,statistics
from pathlib import Path
OUT=Path(__file__).resolve().parent
raw=json.loads((OUT/'vision_raw.json').read_text())
# Corrections made by direct visual comparison with the three supplied page scans.
fix={
(2,'wide_quote',1):'"You cannot centralize power and',
(2,'wide_intro',1):'This Tweet from Stacy Herbert is so frickin awesome. It sums up the political debate surrounding',
(2,'wide_intro',2):"Bitcoin in 11 words. It’s a beauty of concision. A masterpiece of brevity. I can’t stop thinking",
(2,'wide_intro',3):"about it. I’ll make it the basis of my work in 2022 wherein all shitcoins and nocoiners must die.",
(2,'col1',2):'We cannot let the only chance',
(2,'col3',8):'few times, it’s clear he sees Bitcoin as',
(3,'col3',6):'the way, America (read: CIA) has sent',
(3,'col3',9):'priests, as part of America’s colonial',
(3,'col3',20):'in the aforementioned El Salvador hit',
(3,'col2',38):'help them recover from their disease.',
(4,'wide_intro',1):'Unmentioned, President Bukele is dealing with a domestic terrorism crisis at the moment. Again, for those in the cheap',
(4,'wide_intro',4):'and distract and distort. Hopefully, nobody reading this (including so-called Bitcoin friendly “Human Rights Activists”) is',
(4,'col1_top',1):'El Salvador’s gang violence problem',
(4,'col1_top',2):'will be dead soon. It’ll shock folks at',
(4,'col1_top',3):'the New York Times rooting for the',
(4,'col1_top',4):'terrorists. Already, deadly violence',
(4,'col1_top',5):'has collapsed. The numbers don’t lie.',
(4,'col1_top',6):'El Salvador is now one of the safest',
(4,'col1_top',8):'doesn’t help the Gringo psychos ben-',
(4,'col1_top',9):'efiting from the deaths in the name',
(4,'col1_top',10):'of corporate profits, so the New York',
(4,'col1_top',11):'Times propagandizes harder. They',
(4,'col1_top',12):'put the lies on the front page with',
(4,'col2_top',3):'how the world reached out to offer',
(4,'col3',20):'it fails miserably. It’s just more fiat-',
(4,'col3',29):'If you’re American, and you know',
}
# Separate pull quotes / headings without changing their source text.
def kind(p,g,n):
 if p==2 and g=='wide_quote':return 'pullquote'
 if p==2 and g=='wide_intro':return 'intro'
 if p==2 and g=='col1' and (15<=n<=17 or 40<=n<=44):return 'pullquote'
 if p==2 and g=='col2' and n==12:return 'pullquote'
 if p==2 and g=='col3' and (n<=6 or n>=38):return 'pullquote'
 if p==3 and g=='wide_intro' and n<=3:return 'intro'
 if p==3 and g=='col1' and 35<=n<=37:return 'pullquote'
 if p==3 and g=='col2' and 32<=n<=34:return 'pullquote'
 if p==4 and g=='facts_wide':
  if n in [1,6,13,17,25]:return 'heading'
  if n in [2,3,4,5]:return 'intro'
 if p==4 and g=='col3' and n>=40:return 'pullquote'
 return 'body'
rows=[]
for r in raw:
 k=(r['page'],r['region'],r['line'])
 if k==(2,'col1',1):continue # isolated drop cap merged into actual first line
 r=r.copy();r['rawLine']=r['line'];r['text']=fix.get(k,r['text']);r['corrected']=k in fix
 r['kind']=kind(*k)
 r['firstword']=re.sub(r'^[^A-Za-z0-9]+','',r['text']).split()[0].rstrip('.,;:!?"”’')
 r['lastword']=re.sub(r'^[^A-Za-z0-9]+','',r['text'].split()[-1]).rstrip('.,;:!?"”’')
 r['initial']=next((c for c in r['firstword'] if c.isalnum()),'')
 r['terminal']=next((c for c in reversed(r['lastword']) if c.isalnum()),'')
 rows.append(r)
# Per-region physical line numbering after drop-cap merge.
groups={}
for r in rows:
 key=f"p{r['page']}_{r['region']}";groups.setdefault(key,[]).append(r)
 r['line']=len(groups[key])
streams={}
units=dict(groups)
for p in [2,3,4]:units[f'p{p}_all_regions']=[r for r in rows if r['page']==p]
units['article_all_regions']=rows
for scope,rr in units.items():
 for selection in ['all','body','body_intro','emphasis']:
  ss=[r for r in rr if selection=='all' or (selection=='body' and r['kind']=='body') or (selection=='body_intro' and r['kind'] in ['body','intro']) or (selection=='emphasis' and r['kind'] in ['intro','pullquote'])]
  if not ss:continue
  for parity,start in [('all',None),('odd',0),('even',1)]:
   tt=ss if start is None else ss[start::2]
   if not tt:continue
   for direction,vs in [('forward',tt),('reverse_lines',tt[::-1])]:
    label=f'{scope}:{selection}:{parity}:{direction}'
    # Lastwords/terminals retained as mirror controls; OCR interior/lastedges have stated limits.
    for method,txt in [
     ('firstwords',' '.join(r['firstword'] for r in vs)),
     ('initials',''.join(r['initial'] for r in vs)),
     ('lastwords',' '.join(r['lastword'] for r in vs)),
     ('terminals',''.join(r['terminal'] for r in vs)),
     ('whole_lines','\n'.join(r['text'] for r in vs))]:streams[label+':'+method]=txt
# Direct encoding checks: no deleting non-alphabet characters and no deriving secrets by hashing.
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def wif(s):
 try:
  n=0
  for c in s:n=n*58+B58.index(c)
  b=n.to_bytes((n.bit_length()+7)//8,'big');b=b'\0'*(len(s)-len(s.lstrip('1')))+b
  return len(b) in [37,38] and b[0]==128 and (len(b)==37 or b[-5]==1) and hashlib.sha256(hashlib.sha256(b[:-4]).digest()).digest()[:4]==b[-4:]
 except ValueError:return False
hits=[]
for label,s in streams.items():
 for orientation,v in [('normal',s),('reverse_characters',s[::-1])]:
  compact=''.join(v.split())
  for z in re.findall(r'(?<![1-9A-HJ-NP-Za-km-z])[5KL][1-9A-HJ-NP-Za-km-z]{50,51}(?![1-9A-HJ-NP-Za-km-z])',compact):
   if wif(z):hits.append(dict(label=label,orientation=orientation,type='wif',value=z))
  for z in re.findall(r'(?<![A-Za-z0-9])[0-9a-fA-F]{64}(?![A-Za-z0-9])',compact):hits.append(dict(label=label,orientation=orientation,type='hex64',value=z))
result={'sourcePages':{'2':79,'3':80,'4':81},'rows':rows,'streams':streams,'hits':hits,'summary':{'rawObservations':len(raw),'physicalLines':len(rows),'regions':len(groups),'streams':len(streams),'corrections':len(fix),'directEncodingHits':len(hits)}}
(OUT/'printed_lines_and_streams.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
with (OUT/'printed_lines.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['page','region','line','kind','firstword','initial','text'])
 for r in rows:w.writerow([r[k] for k in ['page','region','line','kind','firstword','initial','text']])
lines=['# Issue27 printed-line streams','',str(result['summary']),'','All first words were visually reviewed against the supplied scans. Interior/last words are OCR text with specified corrections, not a fully proofread transcript. Source region order is conventional: spanning lead, left column, center column, right column. Page81 has top left/center blocks, then a double-width facts block, then right column. Line numbers restart in each region.','']
for scope,rr in groups.items():
 lines += ['## '+scope,'','First words: '+' '.join(r['firstword'] for r in rr),'','First letters: `'+''.join(r['initial'] for r in rr)+'`','','Odd first words: '+' '.join(r['firstword'] for r in rr[::2]),'','Even first words: '+' '.join(r['firstword'] for r in rr[1::2]),'']
(OUT/'firstword_streams.md').write_text('\n'.join(lines)+'\n')
(OUT/'all_streams.txt').write_text('\n\n'.join(k+'\n'+v for k,v in streams.items())+'\n')
print(json.dumps(result['summary']));print('hits',hits)
