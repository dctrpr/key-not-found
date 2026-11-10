#!/usr/bin/env python3
"""Independent checksum/count audit of published T01–T10 outputs; stdlib only.
Does not regenerate selectors or prove the completeness of a cipher family.
Usage: python3 scripts/verify_batch20_text.py RESULT.json STREAMS.json NEW_CHECK.json
"""
import hashlib,json,re,sys
from pathlib import Path
ALPHABET='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
BECH='qpzry9x8gf2tvdw0s3jn54khce6mua7l'
def checksum_ok(s):
 try:
  n=sum(ALPHABET.index(c)*58**i for i,c in enumerate(reversed(s)))
  raw=b'\0'*(len(s)-len(s.lstrip('1')))+(n.to_bytes((n.bit_length()+7)//8,'big') if n else b'')
  return len(raw)>=5 and hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4]==raw[-4:]
 except ValueError:return False
def verify(result_path,streams_path):
 result=json.loads(result_path.read_text());raw=json.loads(streams_path.read_text());streams=raw['streams'] if isinstance(raw,dict) else raw
 unique={x['text'] for x in streams};forms=unique|{''.join(t.split()) for t in unique}
 ev=result['evaluation'];formats=ev['formats'];counts={k:0 for k in formats};values={k:set() for k in formats}
 words=(Path(__file__).resolve().parent/'batch20_support/english.txt').read_text().splitlines();dictionary=set(words)
 def add(k,s):counts[k]+=1;values[k].add(s)
 for text in forms:
  for k in formats:
   if k in ('wif','minikey','extended_private','bip38'):
    lengths={'wif':[51,52],'minikey':[22,30],'extended_private':[111],'bip38':[58]}[k]
    prefixes={'wif':('5','K','L'),'minikey':('S',),'extended_private':('xprv','yprv','zprv','Yprv','Zprv'),'bip38':('6P',)}[k]
    for pos in range(len(text)):
     for length in lengths:
      s=text[pos:pos+length]
      if len(s)==length and s.startswith(prefixes) and all(c in ALPHABET for c in s):add(k,s)
   elif k in ('hex64','sec_public'):
    lengths=[64] if k=='hex64' else [66,130]
    for n in lengths:
     for m in re.finditer(r'(?<![0-9a-fA-F])[0-9a-fA-F]{'+str(n)+r'}(?![0-9a-fA-F])',text):
      s=m.group()
      if k=='hex64' or (n==66 and s[:2] in ('02','03')) or (n==130 and s.startswith('04')):add(k,s)
   elif k=='bip39':
    for region in text.split('␞'):
     tokens=re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*",region.lower())
     for n in (12,15,18,21,24):
      for pos in range(len(tokens)-n+1):
       chunk=tokens[pos:pos+n]
       if all(w in dictionary for w in chunk):add(k,' '.join(chunk))
   elif k=='address':
    for pos in range(len(text)):
     if text[pos] in '13':
      for n in range(26,36):
       s=text[pos:pos+n]
       if len(s)==n and all(c in ALPHABET for c in s):add(k,s)
    for m in re.finditer(r'(?i)(?=(bc1['+BECH+r']{11,87}))',text):
     for n in range(14,len(m[1])+1):add(k,m[1][:n])
 assert counts==ev['shapeCounts'],'Shape occurrence disagreement'
 assert {k:len(v) for k,v in values.items()}==ev['uniqueShapeCounts'],'Unique shape disagreement'
 assert len(streams)==ev['streamCount'] and len(unique)==ev['uniqueStreamCount'] and len(forms)==ev['uniqueFormCount']
 # This audit is deliberately scoped to this zero-result batch. Unknown positives
 # stop publication instead of relying on a copied primary validator.
 for k,ss in values.items():
  if k=='minikey':assert all(hashlib.sha256((s+'?').encode('ascii')).digest()[0]!=0 for s in ss)
  elif k in ('wif','extended_private','bip38'):assert all(not checksum_ok(s) for s in ss)
  elif k=='address':
   assert not any(s.lower().startswith('bc1') for s in ss),'Witness candidate needs separate review'
   assert all(not checksum_ok(s) for s in ss)
  else:assert not ss,'Non-checksum candidate needs separate review'
 assert all(n==0 for n in ev['validCounts'].values()) and not result['privateReviewRequired']
 return {'testId':result['testId'],'passed':True,'streamCount':len(streams),'uniqueFormCount':len(forms),'shapeCounts':counts,'uniqueShapeCounts':{k:len(v) for k,v in values.items()},'validRecords':0,'networkQueries':0,'scope':'Independent form/count and actual shape checksum recheck; does not independently regenerate the extraction. Stops on unsupported candidate types.'}
if __name__=='__main__':
 a,b,c=map(Path,sys.argv[1:]);out=verify(a,b)
 with c.open('x') as h:json.dump(out,h,indent=2);h.write('\n')
 print(json.dumps({'testId':out['testId'],'passed':out['passed'],'validRecords':0}))
