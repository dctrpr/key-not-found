#!/usr/bin/env python3
"""Source-only canonical token/observed word geometry alignment, no key tests."""
import argparse,hashlib,json,math,sys
from pathlib import Path

def norm(s):
 letters=''.join(c for c in s.casefold() if c.isalnum())
 return letters if letters else 'punct:'+s

def tables(a,b):
 n,m=len(a),len(b)
 f=[[0]*(m+1) for _ in range(n+1)]
 for i in range(n+1):f[i][0]=i
 for j in range(m+1):f[0][j]=j
 for i in range(n):
  for j in range(m):f[i+1][j+1]=min(f[i][j+1]+1,f[i+1][j]+1,f[i][j]+(a[i]!=b[j]))
 g=[[0]*(m+1) for _ in range(n+1)]
 for i in range(n,-1,-1):g[i][m]=n-i
 for j in range(m,-1,-1):g[n][j]=m-j
 for i in range(n-1,-1,-1):
  for j in range(m-1,-1,-1):g[i][j]=min(g[i+1][j]+1,g[i][j+1]+1,g[i+1][j+1]+(a[i]!=b[j]))
 return f,g

def worldbox(box,crop):
 if not box:return None
 x0,y0,x1,y1=crop;w,h=x1-x0,y1-y0
 a,b,c,d=box
 return [x0+a*w,y0+(1-d)*h,x0+c*w,y0+(1-b)*h]

def upright_polygon(box,angle):
 theta=math.radians(angle);c,s=math.cos(theta),math.sin(theta);cx,cy=1272,1632
 points=[]
 for x,y in [(box[0],box[1]),(box[2],box[1]),(box[2],box[3]),(box[0],box[3])]:
  dx,dy=x-cx,y-cy;points.append([cx+dx*c-dy*s,cy+dx*s+dy*c])
 return points

def merge_duplicates(raw):
 groups=[]
 for item in sorted(raw,key=lambda w:(w['center'][0],w['center'][1])):
  found=None
  for group in groups:
   if norm(group[0]['text'])!=norm(item['text']):continue
   a,b=group[0]['box'],item['box'];ix=max(0,min(a[2],b[2])-max(a[0],b[0]));iy=max(0,min(a[3],b[3])-max(a[1],b[1]));ux=max(a[2],b[2])-min(a[0],b[0]);uy=max(a[3],b[3])-min(a[1],b[1])
   if ux and uy and ix/ux>=0.7 and iy/uy>=0.4:found=group;break
  if found is None:groups.append([item])
  else:found.append(item)
 output=[]
 for group in groups:
  best=max(group,key=lambda w:(len(w['observationText'].split()),len(w['observationText']),w['confidence']))
  row=dict(best);row['duplicateObservations']=[{'id':w['id'],'box':w['box'],'center':w['center']} for w in group]
  row['maxCenterDisagreementPx']=max(math.dist(best['center'],w['center']) for w in group)
  output.append(row)
 return sorted(output,key=lambda w:(w['center'][0],w['center'][1]))

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 crops=json.loads((a.input/'row-crops.json').read_text());vision=json.loads((a.input/'vision.json').read_text());byid={x['id']:x for x in vision['jobs']}
 output=[];totals={'rows':0,'complete':0,'lexicallyComplete':0,'ambiguous':0,'unmapped':0,'canonicalTokens':0,'verifiedTokens':0,'lexicalTokens':0,'verifiedLexicalTokens':0}
 for row in crops['rows']:
  result=byid[row['id']];raw=[]
  for oi,obs in enumerate(result['observations']):
   for wi,word in enumerate(obs.get('words',[])):
    box=worldbox(word.get('box'),row['cropBox']);center=None if not box else [(box[0]+box[2])/2,(box[1]+box[3])/2]
    included=bool(box and box[2]>box[0] and box[3]>box[1] and row['locator'][1]-6<=center[1]<=row['locator'][3]+6)
    raw.append({'id':f'{row["id"]}-o{oi+1}-w{wi+1}','text':word['text'],'box':box,'center':center,'confidence':obs['confidence'],'includedForAlignment':included,'observationText':obs['text']})
  observed=merge_duplicates([x for x in raw if x['includedForAlignment']])
  ca=[norm(x) for x in row['canonicalTokens']];ob=[norm(x['text']) for x in observed];f,g=tables(ca,ob);cost=f[len(ca)][len(ob)];words=[]
  for i,token in enumerate(row['canonicalTokens']):
   matches=[j for j in range(len(ob)) if ca[i]==ob[j] and f[i][j]+g[i+1][j+1]==cost]
   can_delete=any(f[i][j]+1+g[i+1][j]==cost for j in range(len(ob)+1))
   can_substitute=any(ca[i]!=ob[j] and f[i][j]+1+g[i+1][j+1]==cost for j in range(len(ob)))
   match=observed[matches[0]] if len(matches)==1 and not(can_delete or can_substitute) else None
   verified=bool(match and match['confidence']>=0.5)
   box=match['box'] if verified else None
   lexical=any(c.isalnum() for c in token)
   status='unambiguous-normalized-token-match' if verified else 'ambiguous-optimal-alignment' if matches else 'no-exact-normalized-token-match'
   words.append({'id':f'{row["id"]}w{i+1:02d}','text':token,'hasLexicalLettersOrDigits':lexical,'box':box,'center':None if box is None else [(box[0]+box[2])/2,(box[1]+box[3])/2],'originalUprightPolygon':None if box is None else upright_polygon(box,row['rotationCCWDegrees']),'verified':verified,'verifiedBy':'machine: unique normalized token equality in every optimal monotonic edit alignment + observed bbox + Vision confidence>=0.5' if verified else None,'humanVerified':False,'mappingStatus':status,'rawOCRWordId':None if not match else match['id'],'rawOCRText':None if not match else match['text'],'confidence':None if not match else match['confidence'],'punctuationOrCaseDifference':None if not match else token!=match['text'],'centerUncertaintyPx':3+match.get('maxCenterDisagreementPx',0) if verified else None,'duplicateObservations':[] if not match else match.get('duplicateObservations',[]),'possibleRawOCRWordIds':[observed[j]['id'] for j in matches],'couldBeDeletedInOptimalAlignment':can_delete,'couldBeSubstitutedInOptimalAlignment':can_substitute})
  complete=all(x['verified'] for x in words);lexically_complete=all(x['verified'] for x in words if x['hasLexicalLettersOrDigits']);status='complete' if complete else 'ambiguous' if any(x['verified'] for x in words) else 'unmapped'
  output.append({**row,'status':status,'lexicallyComplete':lexically_complete,'visionStatus':result['status'],'rawObservations':result['observations'],'rawWords':raw,'deduplicatedRawWords':observed,'alignment':{'algorithm':'Same-normalized-token overlapping OCR duplicate merge (horizontalIoU>=0.7,verticalIoU>=0.4; prefer longer observed string), then Levenshtein monotonic alignment with all optimal equal-cost paths considered','editDistance':cost,'canonicalTokenCount':len(ca),'observedTokenCount':len(ob),'verifiedTokenCount':sum(x['verified'] for x in words),'verifiedLexicalTokenCount':sum(x['verified'] and x['hasLexicalLettersOrDigits'] for x in words)},'words':words})
  totals['rows']+=1;totals[status]+=1;totals['lexicallyComplete']+=lexically_complete;totals['canonicalTokens']+=len(words);totals['verifiedTokens']+=sum(x['verified'] for x in words);totals['lexicalTokens']+=sum(x['hasLexicalLettersOrDigits'] for x in words);totals['verifiedLexicalTokens']+=sum(x['verified'] and x['hasLexicalLettersOrDigits'] for x in words)
 payload={'version':1,'sourcePdf':crops['sourcePdf'],'sourcePdfSha256':crops['sourcePdfSha256'],'canonicalRows':crops['canonicalRows'],'canonicalRowsSha256':crops['canonicalRowsSha256'],'sourceImages':crops['sourceImages'],'ocrEngine':vision['metadata'],'wordBoxCoordinateSpace':'top-left pixels in the row-specific 2544x3264 frame after stated rotationCCWDegrees; originalUprightPolygon separately maps each matched box back to original upright page','canonicalAuthority':'Existing visually reviewed canonical row text; OCR never replaces canonical text. Whitespace tokens retained exactly.','verifiedMeaning':'Machine geometry alignment only, not human verification. No forced substitution, interpolation, rescaling or approximate string match obtains verified=true.','uncertainty':'Vision ranges are approximate word boxes. 3px center uncertainty is a review guard, not measured calibration. Review selected tokens near mask edges; ambiguous tokens have no usable box.','scope':'Source preflight only. No reflected-mask selection, candidate hashes, private-key detection or blockchain queries.','stats':totals,'rows':output}
 with a.out.open('x',encoding='utf-8') as handle:handle.write(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(totals))
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('Source geometry alignment failed: '+type(error).__name__+'. No source result produced.',file=sys.stderr);sys.exit(1)
