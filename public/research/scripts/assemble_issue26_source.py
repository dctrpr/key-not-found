#!/usr/bin/env python3
"""Source-only assembly from frozen issue26 OCR and visual first-word decisions.
No candidate streams, cryptographic decoders, key checks or network access.
"""
import argparse,json,hashlib,re
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def topbox(b,m):
 x0,y0,x1,y1=b;w=m['box'][2]-m['box'][0];h=m['box'][3]-m['box'][1]
 return [m['box'][0]+x0*w,m['box'][1]+(1-y1)*h,m['box'][0]+x1*w,m['box'][1]+(1-y0)*h]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--views',type=Path,required=True);p.add_argument('--zone-ocr',type=Path,required=True);p.add_argument('--full-ocr',type=Path,required=True);p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--decisions',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise ValueError('Refusing existing output')
 meta=read(a.views);ocr=read(a.zone_ocr);full=read(a.full_ocr);review=read(a.decisions);jobs={j['id']:j for j in ocr['jobs']};decisions={d['id']:d for d in review['decisions']};rows=[];labels=[];counters={};paratext=[]
 images=[]
 for n in [3,4,5]:
  name=f'page_{n:02d}.jpg';expected=review['sourceImageHashes'][name]
  if sha(a.source_dir/name)!=expected:raise ValueError('Source image changed')
  images.append({'path':name,'printedPage':n+99,'sha256':expected,'width':2040,'height':2805})
 for m in meta['views']:
  if not m['id'].endswith('-native'):continue
  native=jobs[m['id']]
  if native['status']!='ok':raise ValueError('OCR view failed')
  if m['zone']=='title':
   for i,o in enumerate(sorted(native['observations'],key=lambda x:(-x['box'][3],x['box'][0]))):
    paratext.append({'id':f'p{m["page"]}-title{i+1}','page':m['page'],'role':'subtitle' if i==3 else 'display-title','textOCR':o['text'],'box':topbox(o['box'],m),'bodyScope':False,'fullTextSourceReviewed':False,'note':'Black redaction bars may create spurious OCR strokes; title is not source body text.'})
   continue
  alt_m=next(v for v in meta['views'] if v['page']==m['page'] and v['zone']==m['zone'] and v['id'].endswith('-gray-auto-2x'));alt=jobs[alt_m['id']]
  ordered=sorted(native['observations'],key=lambda x:(-x['box'][3],x['box'][0]))
  if m['zone']=='stop':ordered.sort(key=lambda x:(x['text'].strip()=='STOP!',-x['box'][3],x['box'][0]))
  for o in ordered:
   page=m['page'];counters[page]=counters.get(page,0)+1;rowid=f'p{page}r{counters[page]:02d}';words=[]
   for i,w in enumerate(o.get('words',[])):
    words.append({'id':rowid+f'w{i+1:02d}','text':w['text'],'box':topbox(w['box'],m) if isinstance(w.get('box'),list) else None})
   first=next((w for w in words if re.search('[A-Za-z0-9]',w['text'])),None);d=decisions[rowid]
   if first is None or first['text']!=d['expectedFirstTokenOCR'] or first['box']!=d['expectedFirstTokenBox']:raise ValueError('A recorded first-token observation changed; source review required')
   box=topbox(o['box'],m);cy=(box[1]+box[3])/2;alternatives=[]
   for alt_o in alt['observations']:
    ab=topbox(alt_o['box'],alt_m)
    if abs((ab[1]+ab[3])/2-cy)<25:alternatives.append({'text':alt_o['text'],'box':ab,'firstTokens':[w['text'] for w in alt_o.get('words',[])[:3]]})
   role=d['role'];row={'id':rowid,'page':page,'sourceImage':f'page_{page-99:02d}.jpg','flowBlock':f'p{page}-{m["zone"]}','flowBlockOrder':d['flowBlockOrder'],'paragraph':d['paragraph'],'column':d['column'],'role':role,'colorClass':d['colorClass'],'box':box,'textOCR':o['text'],'wordsOCR':words,'comparisonViews':alternatives,'firstTokenOCR':first['text'],'firstWordSource':d['firstWordSource'],'firstLexicalWordSource':d['firstLexicalWordSource'],'firstWordStatus':'verified-source-pixels','firstWordReview':{'type':'Codex visual source-pixel review','recordedAtUTC':review['recordedAtUTC'],'plate':d['reviewPlate'],'plateSha256':d['reviewPlateSha256']},'fullLineStatus':'unverified-ocr','fullLineUnknownEnd':page==102 and m['zone'] in ['intro','brand','rightcol'],'uncertainties':d['uncertainties']}
   if role=='display-label':row['bodyScope']=False;labels.append(row)
   else:rows.append(row)
 if len(rows)!=113 or len(labels)!=1 or {p:sum(r['page']==p for r in rows) for p in [102,103,104]}!={102:42,103:52,104:19}:raise ValueError('Body source row counts changed')
 for i,r in enumerate(rows):r['articleReadingIndex']=i+1;r['pageReadingIndex']=sum(x['page']==r['page'] for x in rows[:i+1]);r['flowReadingIndex']=sum(x['flowBlock']==r['flowBlock'] for x in rows[:i+1])
 # Keep native full-page marginal/header/footer observations separately.
 for j in full['jobs']:
  page=int(j['id'][1:])
  for i,o in enumerate(sorted(j['observations'],key=lambda x:(-x['box'][3],x['box'][0]))):
   x0,y0,x1,y1=o['box'];b=[x0*2040,(1-y1)*2805,x1*2040,(1-y0)*2805]
   if b[3]<150 or b[1]>2450 or (b[2]<180 or b[0]>1800):
    role='header' if b[3]<150 else 'footer' if b[1]>2450 else 'margin'
    paratext.append({'id':f'p{page}-paratext{i+1:02d}','page':page,'role':role,'textOCR':o['text'],'box':b,'bodyScope':False,'fullTextSourceReviewed':False})
 out={'version':1,'sourceOnly':True,'targetDecodings':0,'recordChecks':0,'sourceImages':images,'imageFrame':'2040x2805 source JPEG; top-left pixel coordinates; no deskew/reflow/rotation applied','articleIdentity':{'inheritedLabel':'Issue26 comparison','visibleTitle':'Censorship, Dematerialization and Bitcoin','visibleSubtitle':'Without Freaks, America Is Nothing','printedPages':[102,103,104],'provenanceLimit':'Retained comparison JPEG witnesses; original PDF unavailable. Filename alone is not issue authentication.'},'transcriptionPolicy':{'firstWordSource':'First nonempty whitespace-derived printed token, with only outer punctuation stripped; internal punctuation and genuine fused spelling preserved. Leading standalone dash is separate punctuation. See present,how and thepursuit decisions.','firstLexicalWordSource':'Alternative conventional lexical word at the line start; keeps printed hyphenation fragments. It differs from literal printed-token form for present,how.','literalCharacters':'Visible first-word letters and case preserved. Internal apostrophes/hyphens use the stated OCR transcription surface; raster glyphs do not establish original digital Unicode code points. Outer punctuation and leading standalone dashes are stripped only in first-word fields, not deleted from raw OCR/source.', 'fullText':'Raw OCR is retained, unverified; page102 gutter blur prevents full-line exclusion.','ordering':'Full-width introductory flow, then each independent column, then full-width closing flows; no row merging between columns.','labels':'Standalone STOP is separate from regular text rows. Title/subtitle/headers/margins/footers remain paratext.','paragraphs':'Visual source-reading classification, not author-controlled manuscript metadata.'},'sourceReview':{'recordedAtUTC':review['recordedAtUTC'],'firstWordsReviewed':113,'displayLabelFirstWordsReviewed':1,'fullLineReviewClaim':False,'decisionArtifactSha256':sha(a.decisions),'plateArtifacts':review['plateArtifacts']},'stats':{'bodyRows':113,'rowsByPage':{'102':42,'103':52,'104':19},'standaloneLabels':1,'flowBlocks':len({r['flowBlock'] for r in rows}),'fullLineUnknownEndRows':sum(r['fullLineUnknownEnd'] for r in rows)},'rows':rows,'standaloneLabels':labels,'paratext':paratext}
 a.out.parent.mkdir(parents=True,exist_ok=True)
 with a.out.open('x') as h:json.dump(out,h,indent=2);h.write('\n')
 print(json.dumps({'sourceRows':113,'standaloneLabels':1,'firstWordsReviewed':114,'targetDecodings':0,'sha256':sha(a.out)}))
if __name__=='__main__':main()
