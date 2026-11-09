#!/usr/bin/env python3
"""Inventory explicit printed body numbers and test declared direct binary encodings."""
from pathlib import Path
import json,re,hashlib,math,collections
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis_outputs/continuation_20261109/numeric_inventory';OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'analysis_outputs/continuation_20261109/fresh_cryptanalysis/printed_lines.json'
d=json.loads(SRC.read_text());rows=[r for r in d['rows'] if r['section']=='body'];events=[];indef=[]
for ri,r in enumerate(rows):
 text=r['text']
 for m in re.finditer(r'\d[\d,]*|\b(?:Forty|six|zero|ONE|first|billions)\b',text,re.I):
  tok=m.group();kind='digits' if tok[0].isdigit() else {'forty':'cardinal_quantity','six':'cardinal_quantity','zero':'cardinal_quantity','one':'pronoun_one','first':'ordinal_first','billions':'indefinite_scale'}[tok.lower()]
  e=dict(id=f"n{len(events)+1:02}",rowId=r['id'],page=r['page'],printedRow=r['printed_row'],start=m.start(),end=m.end(),surface=tok,category=kind,sourceText=text,locator=r['locator'])
  if kind=='indefinite_scale':
   indef.append(e);continue
  n=int(tok.replace(',','')) if kind=='digits' else {'forty':40,'six':6,'zero':0,'one':1,'first':1}[tok.lower()]
  e.update(mantissa=n,multiplier=1,value=n,scaleSurface=None,scaleRowId=None,unit='percent' if text[m.end():].startswith('%') else ('USD' if m.start()>0 and text[m.start()-1]=='$' else None))
  tail=text[m.end():];sm=re.match(r'\s+(billion|trillion)\b',tail,re.I);scaleRow=r['id']
  if not sm and tail.strip()=='' and ri+1<len(rows) and rows[ri+1]['page']==r['page']:
   sm=re.match(r'\s*(BILLION|trillion)\b',rows[ri+1]['text'],re.I);scaleRow=rows[ri+1]['id']
  if sm:
   e.update(multiplier={'billion':10**9,'trillion':10**12}[sm[1].lower()],scaleSurface=sm[1],scaleRowId=scaleRow)
   e['value']=n*e['multiplier']
  e['minimalBinary']=format(e['value'],'b');e['minimalBitLength']=len(e['minimalBinary']);events.append(e)
# Keep exact lexical source order; no sorting by value or dropping to force length.
selected=[e for e in events if e['category'] in ['digits','cardinal_quantity']]
bits=''.join(e['minimalBinary'] for e in selected)
assert len(rows)==142 and len(selected)==24 and len(bits)==256
candidates=[]
for direction,s in [('source_order',bits),('complete_bit_reversal',bits[::-1]),('reverse_number_order',''.join(e['minimalBinary'] for e in selected[::-1])),('reverse_bits_within_each_number',''.join(e['minimalBinary'][::-1] for e in selected))]:
 candidates.append(dict(direction=direction,bits=s,bitLength=len(s),scalarHex=f'{int(s,2):064x}',eventIds=[e['id'] for e in selected],orderedEventIds=[e['id'] for e in (selected[::-1] if direction in ['complete_bit_reversal','reverse_number_order'] else selected)],explanation={'source_order':'Concatenate each number’s minimal base-2 integer representation in printed source order; zero contributes one 0 bit.','complete_bit_reversal':'Reverse the complete declared256-bit string (both number order and within-number bit order).','reverse_number_order':'Reverse source number order while preserving each number’s own minimal binary representation.','reverse_bits_within_each_number':'Reverse bits within each minimal binary number while retaining source number order.'}[direction]))
scopes={
 'digits_only':lambda e:e['category']=='digits',
 'digits_and_quantity_cardinals':lambda e:e['category'] in ['digits','cardinal_quantity'],
 'digits_quantity_and_pronoun_one':lambda e:e['category'] in ['digits','cardinal_quantity','pronoun_one'],
 'digits_quantity_and_ordinals':lambda e:e['category'] in ['digits','cardinal_quantity','ordinal_first'],
 'all_explicit_finite_including_pronoun_and_ordinal':lambda e:True,
}
variants=[]
for scope,pred in scopes.items():
 es=[e for e in events if pred(e)]
 for scale in ['mantissa_only','full_decimal_scales','scale_as_separate_integer_token']:
  vals=[]
  for e in es:
   if scale=='full_decimal_scales':vals.append(e['value'])
   else:
    vals.append(e['mantissa'])
    if scale=='scale_as_separate_integer_token' and e['multiplier']!=1:vals.append(e['multiplier'])
  for enc in ['minimal_integer_binary','whole_byte_integer_binary']:
   chunks=[format(v,'b') if enc=='minimal_integer_binary' else format(v,f'0{max(1,(v.bit_length()+7)//8)*8}b') for v in vals]
   s=''.join(chunks)
   variants.append(dict(scope=scope,scale=scale,encoding=enc,numbers=len(vals),bitLength=len(s),equals256=len(s)==256,equals264=len(s)==264,values=vals))
result=dict(source=str(SRC.relative_to(ROOT)),sourceSha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),bodyLineCount=len(rows),numericEvents=events,indefiniteQuantities=indef,selectedRule='All digit-written body numbers plus spelled finite quantity words Forty, six, zero; apply explicit billion/trillion decimal scales to monetary amounts; exclude ordinal first and pronoun ONE in EVERY SINGLE ONE OF. Body only; titles/art/page folios are separate source classes.',selectedEventIds=[e['id'] for e in selected],selectedValues=[e['value'] for e in selected],candidates=candidates,representationVariants=variants,summary=dict(bodyLines=len(rows),digitEvents=sum(e['category']=='digits' for e in events),quantityCardinalEvents=sum(e['category']=='cardinal_quantity' for e in events),pronounOneEvents=sum(e['category']=='pronoun_one' for e in events),ordinalFirstEvents=sum(e['category']=='ordinal_first' for e in events),indefiniteBillions=len(indef),selectedNumbers=len(selected),selectedBitLength=len(bits),variants=len(variants),exact256Variants=sum(v['equals256'] for v in variants),exact264Variants=sum(v['equals264'] for v in variants)),limitations=['The 256-bit result depends on the linguistic distinction between finite quantity cardinals and pronouns/ordinals; all alternatives are disclosed.','Percentages are encoded as the printed integer magnitude (42,51,95), not as fractions. Their exact rational values /100 have nonterminating binary expansions and cannot be losslessly represented by finite minimal integer bits.','Commas in 20,000/100,000/12,000 are thousands separators. There is no printed decimal point in these body numbers.','Indefinite plural billions occurs twice and has no determinate integer value. No million occurrence exists in this body.','Body-only excludes page folios, package copy, graphic lettering and bill serial numbers. These are not silently mixed into the body-number claim.','No arbitrary trimming, zero-padding to32bytes, modulo, dropped occurrences, salt, or hash is used for the four declared mirror-family candidates.'])
(OUT/'numeric_inventory.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
# Full 142-line ledger with source coordinates, even where no number is present.
lines=['# Numeric inventory: all142 printed body lines','','Coordinates are broad source locator bands, not glyph-tight boxes. Page79 first-paragraph bands use the declared fixed rotation recorded in the locator.','', '| Row | Locator box; rotation CCW | Explicit numerical readings | Printed text |','|---|---|---|---|']
for r in rows:
 es=[e for e in events+indef if e['rowId']==r['id']]
 desc='; '.join(f"{e['surface']}→{e.get('value','indefinite')} ({e['category']})"+(f" ×scale {e['scaleSurface']} on {e['scaleRowId']}" if e.get('scaleSurface') else '') for e in es)
 scales=[e for e in events if e.get('scaleRowId')==r['id'] and e['rowId']!=r['id']]
 if scales:desc += ('; ' if desc else '') + '; '.join(f"{e['scaleSurface']} scale attached to {e['id']} on {e['rowId']}" for e in scales)
 loc=r['locator'];escaped_text=r['text'].replace('|',chr(92)+'|');lines.append(f"| {r['id']} | `{loc['box']}`; {loc['rotate_ccw_degrees']}° | {desc or '—'} | {escaped_text} |")
(OUT/'all_142_source_lines.md').write_text('\n'.join(lines)+'\n')
report=['# Reconstructing the community256/264-bit claim','',result['selectedRule'],'',str(result['summary']),'','## Selected source-order values','',str(result['selectedValues']),'','## Representation variants','','| Scope | Scale handling | Binary encoding | Values | Bits |','|---|---|---|---:|---:|']
for v in variants:report.append(f"| {v['scope']} | {v['scale']} | {v['encoding']} | {v['numbers']} | {v['bitLength']} |")
report+=['','## Boundaries and uncertainty','',*result['limitations'],'','## Four declared direct candidates','']
for c in candidates:report += [f"- {c['direction']}: {c['bitLength']} bits, hex `{c['scalarHex']}`."]
(OUT/'numeric_inventory.md').write_text('\n'.join(report)+'\n')
print(json.dumps(result['summary']));print(json.dumps(candidates))
