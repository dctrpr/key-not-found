#!/usr/bin/env python3
"""Independent fixed duplex mask experiment; no translate/rotate fitting or hashes."""
from pathlib import Path
import json,re,hashlib
import numpy as np
import fitz
import io
from PIL import Image, ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis_outputs/continuation_20261109/inverted_duplex'
OUT.mkdir(parents=True,exist_ok=True)
D=json.loads((ROOT/'analysis_outputs/3d_article_map/article_3d_map_data.json').read_text())
P={p['page']:p for p in D['pages']}

def smooth(a,kw=41,kh=17):
 b=np.pad(a,((kh//2,kh//2),(kw//2,kw//2)))
 z=np.pad(b.cumsum(0,dtype=np.int32).cumsum(1,dtype=np.int32),((1,0),(1,0)))
 return (z[kh:,kw:]-z[:-kh,kw:]-z[kh:,:-kw]+z[:-kh,:-kw])/(kw*kh)

def components(a):
 # Fast run-based connected components, sufficient for separated long highlighter bars.
 runs=[];last=[];parent=[]
 def find(i):
  while parent[i]!=i: parent[i]=parent[parent[i]];i=parent[i]
  return i
 for y,row in enumerate(a):
  z=np.diff(np.r_[False,row,False].astype(np.int8)); starts=np.where(z==1)[0];ends=np.where(z==-1)[0]
  cur=[]
  for x1,x2 in zip(starts,ends):
   if x2-x1<20: continue
   i=len(runs);runs.append((int(x1),int(y),int(x2),int(y+1)));parent.append(i);cur.append(i)
   for j in last:
    if runs[j][0]<x2 and x1<runs[j][2]: parent[find(i)]=find(j)
  last=cur
 groups={}
 for i,b in enumerate(runs):
  j=find(i)
  if j not in groups:groups[j]=list(b)
  else:
   c=groups[j];c[0]=min(c[0],b[0]);c[1]=min(c[1],b[1]);c[2]=max(c[2],b[2]);c[3]=max(c[3],b[3])
 return list(groups.values())

images={p:Image.open(ROOT/'analysis_outputs/3d_article_map'/P[p]['image']).convert('RGB') for p in P}
doc=fitz.open(ROOT/'magazine.pdf')
ref=doc[1].get_images()[0][0]
images[74]=Image.open(io.BytesIO(doc.extract_image(ref)['image'])).convert('RGB').rotate(180)
boxes={}
for p,im in images.items():
 if p==80:continue
 a=np.asarray(im);gray=a.mean(2);spread=a.max(2).astype(int)-a.min(2).astype(int)
 # Pages 77/79 are printed on dark ground, so inverted bars are white.
 m=(gray>180)&(spread<70) if p == 77 else (gray<150)&(spread<70)
 sm=smooth(m)
 comps=components(sm>.62)
 boxes[p]=[b for b in comps if 160<b[2]-b[0]<2250 and 16<b[3]-b[1]<115 and (b[2]-b[0])/(b[3]-b[1])>3 and b[1]>250 and b[3]<3100]

# Merge overlapping detector fragments from a single physical bar; pad a fixed 12 px.
for p,bs in boxes.items():
 merged=[]
 for b in bs:
  found=False
  for a in merged:
   ov=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
   ar=min((a[2]-a[0])*(a[3]-a[1]),(b[2]-b[0])*(b[3]-b[1]))
   if ov/max(1,ar)>.75:
    a[:]=[min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3])];found=True;break
  if not found:merged.append(b[:])
 boxes[p]=[[max(0,b[0]-12),max(0,b[1]-12),min(images[p].width,b[2]+12),min(images[p].height,b[3]+12)] for b in merged]
# Page 74 is a full-page field/cash illustration, not text; its dark patches are detector artifacts.
boxes[74]=[]

# A strict mask-center extraction from valid front/back physical pairs.
rows=[]
for a,b in [(74,75),(76,77),(78,79)]:
 for s,t in [(a,b),(b,a)]:
  tp=P.get(t,{'chars':[]});w,h=images[t].size
  for k,bb in enumerate(sorted(boxes[s],key=lambda q:(q[1],q[0]))):
   # Source and target same scan dimensions; mirror through vertical leaf axis only.
   rb=[w-bb[2],bb[1],w-bb[0],bb[3]]
   chosen=[c for c in tp['chars'] if rb[0]<=c['x']<rb[2] and rb[1]<=c['y']<rb[3]]
   # Source char model order is the PDF text order; no sorting across inferred lines.
   text=''.join(c['c'] for c in chosen).strip()
   rows.append(dict(source=s,target=t,span=k+1,sourceBox=bb,targetBox=rb,chars=text,charCount=len(chosen)))

# Label visual regions so a human can judge detector quality before trusting results.
thumbs=[]
for p in [75,76,77,78,79]:
 im=images[p].copy();d=ImageDraw.Draw(im)
 for k,b in enumerate(sorted(boxes[p],key=lambda q:(q[1],q[0]))):
  d.rectangle(b,outline='red',width=5);d.text((b[0],b[1]-25),str(k+1),fill='red',font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',26))
 im.thumbnail((420,550));panel=Image.new('RGB',(450,590),'white');panel.paste(im,(10,35));ImageDraw.Draw(panel).text((10,8),f'Page {p}: {len(boxes[p])} inverted bars',fill='black');thumbs.append(panel)
sheet=Image.new('RGB',(450*5,590),'white')
for i,im in enumerate(thumbs):sheet.paste(im,(450*i,0))
sheet.save(OUT/'detected_inverted_bars.jpg')

# Show each source bar and its fixed reflected target crop at legible scale.
plates=[]
for r in rows:
 s,t=r['source'],r['target'];a=images[s].crop(r['sourceBox']);b=images[t].crop(r['targetBox'])
 width=max(a.width,b.width);panel=Image.new('RGB',(width+30,180),'white');dd=ImageDraw.Draw(panel)
 dd.text((10,5),f"{s}->{t}, source bar {r['span']} (top source; bottom reflected target)",fill='black')
 a.thumbnail((2200,65));b.thumbnail((2200,65));panel.paste(a,(10,30));panel.paste(b,(10,105));plates.append(panel)
maxw=max(z.width for z in plates);sheet=Image.new('RGB',(maxw,sum(z.height for z in plates)),'white');yy=0
for z in plates:sheet.paste(z,(0,yy));yy+=z.height
sheet.save(OUT/'all_duplex_inverted_crops.jpg')

# Each selected band separately, then fixed page-order concatenations, both normal and reverse.
streams={}
for r in rows:streams[f"{r['source']}->{r['target']}:bar{r['span']}"]=r['chars']
for s,t in [(74,75),(75,74),(76,77),(77,76),(78,79),(79,78)]:streams[f'{s}->{t}:all']=''.join(r['chars'] for r in rows if r['source']==s and r['target']==t)
BASE58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def valid_wif(s):
 try:
  n=0
  for c in s:n=n*58+BASE58.index(c)
  raw=n.to_bytes((n.bit_length()+7)//8,'big');raw=b'\0'*(len(s)-len(s.lstrip('1')))+raw
  return len(raw) in (37,38) and raw[0]==128 and (len(raw)==37 or raw[-5]==1) and hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4]==raw[-4:]
 except ValueError:return False
hits=[]
for name,s in streams.items():
 for variant,v in [('normal',s),('reverse',s[::-1])]:
  # Only remove whitespace, retaining punctuation/case rather than filtering allowed alphabet.
  v=''.join(v.split())
  for z in re.findall(r'(?<![1-9A-HJ-NP-Za-km-z])(?:5[1-9A-HJ-NP-Za-km-z]{50}|[KL][1-9A-HJ-NP-Za-km-z]{51})(?![1-9A-HJ-NP-Za-km-z])',v):
   if valid_wif(z):hits.append(dict(stream=name,variant=variant,encoding='wif',candidate=z))
  for z in re.findall(r'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])',v):hits.append(dict(stream=name,variant=variant,encoding='hex',candidate=z))
result=dict(method='Fixed horizontal mirror of scan-detected inverted bars on physical leaves 74/75, 76/77, and 78/79; no shifts or fitted target constraints. Fixed 12-pixel source-box padding retains complete glyphs; no target fitting.',boxes=boxes,rows=rows,streams=streams,keyShapeHits=hits,caveats=['Heuristic scan-native bar detector must be visually verified.','OCR char boxes inherit source registration uncertainty.','No key activity/address checks or transactions performed.'])
(OUT/'inverted_duplex.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
lines=['# Corrected physical leaves: inverted-bar extraction','',result['method'],'','Detected candidate boxes: '+str({p:len(b) for p,b in boxes.items()}),'','## Fixed mirror character streams','']
for n,s in streams.items():lines.append(f'- `{n}`: `{s}`')
lines+=['','Strict whole-window WIF/64-hex hits: '+str(len(hits))+'.','',*result['caveats']]
(OUT/'inverted_duplex.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'boxes':{p:len(b) for p,b in boxes.items()},'rows':len(rows),'keyShapeHits':len(hits)}))
