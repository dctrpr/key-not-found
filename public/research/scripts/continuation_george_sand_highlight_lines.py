#!/usr/bin/env python3
"""Test source-linked Sand/Musset methods on actual highlighted physical lines.
No wordlist filtering, character-alphabet filtering, prose hashes, or network calls.
"""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis_outputs/continuation_20261109/george_sand';OUT.mkdir(parents=True,exist_ok=True)
# Manually transcribed physical highlight fragments, in visual page/line order.
# fullFirst is the first word of the entire printed article line, including unhighlighted prefix.
R=[]
def add(p,color,text,fullfirst,line):R.append(dict(page=p,color=color,text=text,fullFirst=fullfirst,physicalLine=line))
for args in [
(75,'orange','They are the sum of','the',1),(75,'orange','all our neuroses.','all',2),(75,'grey','money printers, banking','arose',3),(75,'grey','terrorists, stock traders, central bank arsonists,','terrorists',4),(75,'orange','Layer 1','Look',5),(75,'orange','Fact: It’s Layer 1 for every great thing','Fact',6),(75,'orange','that’s ever been invented or discovered.','that’s',7),(75,'orange','“Maximalist”','Vitalik',8),(75,'grey','Don’t fall for shitcoinery.','Don’t',9),(75,'orange','Keep your dignity.','Keep',10),(75,'orange','Layer 1','the',11),
(76,'orange','Get some toxicity. Get some bitcoin. Open your heart to','Get',1),(76,'orange','Bitcoin.','Bitcoin',2),(76,'grey','Gotta be this way. Forty years of dumb post-1971 fiat money','Gotta',3),(76,'grey','nonsense','nonsense',4),(76,'orange','by the rancid catnip of fiat money.','by',5),(76,'grey','It’s a stun gun to the genitals.','laundering',6),(76,'orange','“buying the dip.”','He’s',7),(76,'grey','$1 billion','$1',8),(76,'grey','“Volcano Bonds”','collateralized',9),(76,'orange','shitcoiner at heart.','Maybe',10),
(77,'orange','Toxic Bitcoin Maximalists within six months.','country',1),(77,'grey','(Sorry Bhutan, you fell for that snake oil salesmen over','(Sorry',2),(77,'grey','at XRP. Get ready to experience shitcoin hell.','at',3),(77,'grey','Faketoshi','Particularly',4),(77,'orange','harass old women and children','London',5),(77,'grey','shitcoiners,','legal',6),(77,'grey','useless Royals,','useless',7),(77,'grey','It does this by monetizing,','the',8),
(78,'orange','The numbers don’t lie.','and',1),(78,'grey','gargantuanly wasteful','The',2),(78,'grey','money printing','and',3),(78,'grey','wars to keep it going','and',3),(78,'orange','America left $85','and',4),(78,'orange','BILLION worth of hate toys in Afghanistan,','BILLION',5),(78,'orange','$2 trillion fiat cuck-bucks.','that',6),(78,'orange','the game-theorized Bitcoin protocol,','It’s',7),
(79,'grey','war and violence','To',1),(79,'grey','economy','economy',2),(79,'orange','infinitely more efficient','of',3),(79,'orange','to transact and store wealth in than fiat, shitcoins','to',4),(79,'orange','or gold','or',5),(79,'orange','That’s right, Bitcoin will take','drops',6),(79,'orange','all the energy.','all',7),(79,'orange','Everyone will live their own experience in the rabbit hole.','Everyone',8),(79,'orange','We are getting our souls back and our minds.','We',9)
]:add(*args)
def wordlist(s):return re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z]+)?",s)
# Merge the two separated black spans lying on the same printed p78 baseline.
rows=[]
for r in R:
 if rows and (rows[-1]['page'],rows[-1]['physicalLine'])==(r['page'],r['physicalLine']):rows[-1]['text']+=' '+r['text']
 else:rows.append(r.copy())
streams={}
for color in ['all','orange','grey']:
 for p in ['all',75,76,77,78,79]:
  chosen=[r for r in rows if (color=='all' or r['color']==color) and (p=='all' or r['page']==p)]
  for parity in ['all','odd','even']:
   rr=chosen if parity=='all' else chosen[0 if parity=='odd' else 1::2]
   for direction in ['forward','reverse']:
    ss=rr if direction=='forward' else rr[::-1]
    if not ss:continue
    base=f'{color}:p{p}:{parity}:{direction}'
    fragmentfirst=[wordlist(r['text'])[0] for r in ss]
    fullfirst=[wordlist(r['fullFirst'])[0] for r in ss]
    initials=''.join(w[0] for w in fragmentfirst)
    fullinitials=''.join(w[0] for w in fullfirst)
    streams[base+':fragment_first_words']=' '.join(fragmentfirst)
    streams[base+':full_line_first_words']=' '.join(fullfirst)
    streams[base+':fragment_initials']=initials
    streams[base+':full_line_initials']=fullinitials
    streams[base+':fragment_lines']=' '.join(r['text'] for r in ss)
WL=json.loads((ROOT/'node_modules/bip39/src/wordlists/english.json').read_text());WM={w:i for i,w in enumerate(WL)}
def bip(s):
 ws=s.lower().replace('’',"'").split()
 if len(ws) not in [12,15,18,21,24] or any(w not in WM for w in ws):return False
 bits=''.join(f'{WM[w]:011b}' for w in ws);cs=len(ws)//3;ent=bits[:-cs];h=hashlib.sha256(int(ent,2).to_bytes(len(ent)//8,'big')).digest()
 return bits[-cs:]==''.join(f'{b:08b}' for b in h)[:cs]
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def wif(s):
 try:
  n=0
  for c in s:n=n*58+B58.index(c)
  raw=n.to_bytes((n.bit_length()+7)//8,'big');raw=b'\0'*(len(s)-len(s.lstrip('1')))+raw
  return len(raw) in [37,38] and raw[0]==128 and (len(raw)==37 or raw[-5]==1) and hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4]==raw[-4:]
 except ValueError:return False
hits=[]
for label,s in streams.items():
 # Normalize whitespace only for literal key encodings; preserve every non-whitespace character.
 compact=''.join(s.split())
 for direction,v in [('normal',compact),('mirror',compact[::-1])]:
  for z in re.findall(r'[5KL][1-9A-HJ-NP-Za-km-z]{50,51}',v):
   if wif(z):hits.append(dict(stream=label,direction=direction,type='wif',candidate=z))
  for z in re.findall(r'(?<![0-9A-Fa-f])[0-9A-Fa-f]{64}(?![0-9A-Fa-f])',v):hits.append(dict(stream=label,direction=direction,type='hex',candidate=z))
  for ln in [22,30]:
   for i in range(max(0,len(v)-ln+1)):
    z=v[i:i+ln]
    if z.startswith('S') and all(c in B58 for c in z) and hashlib.sha256((z+'?').encode()).digest()[0]==0:hits.append(dict(stream=label,direction=direction,type='minikey',candidate=z))
 if label.endswith('_words'):
  ws=s.lower().split()
  for ln in [12,15,18,21,24]:
   for i in range(max(0,len(ws)-ln+1)):
    z=' '.join(ws[i:i+ln])
    if bip(z):hits.append(dict(stream=label,direction='normal',type='bip39',candidate=z))
result=dict(source='High-res manual highlight reading JSON plus upright scanned pages, manually restored physical line breaks.',methods='Sand alternate whole highlighted physical lines; Musset first words of each highlighted physical line; all/orange/grey; global/page-local; forward/reverse. Also tests first words of complete printed lines containing highlights. No BIP word deletion, hashing, or arbitrary character selection.',fragments=R,physicalRows=rows,streams=streams,hits=hits,summary=dict(fragments=len(R),physicalRows=len(rows),streams=len(streams),hits=len(hits)),caveats=['Highlighted fragment is not the same unit as full article line; both first-word forms are recorded.','Alternation is applied within selected highlighted-line lists, not all body lines.','No address or chain checks were run.','Manual physical rows preserve source typography; p78 two black fields share one baseline.'])
(OUT/'highlight_physical_lines.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
lines=['# George Sand / Musset on highlighted physical lines','',result['methods'],'',str(result['summary']),'','## Global first-word streams','']
for l,s in streams.items():
 if ':pall:all:forward:' in l and l.endswith('_words'):lines.append(f'- `{l}`: {s}')
lines+=['','## Hits','',str(hits),'','## Limits','',*result['caveats']]
(OUT/'highlight_physical_lines.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(result['summary']))
