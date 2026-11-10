#!/usr/bin/env python3
"""Independent, offline regex/hashlib reproduction of the fixed minikey audit.
Run from the corpus: python3 scripts/verify_minikey_window_audit.py <new-output.json>.
No network, keys printed, or wallet actions. Requires Python standard library only.
"""
import hashlib,json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='1651a33dab46babf36f56439ddb409058cfa36712d96ead7d4200962b80817b9'
data=json.loads(source.read_text())
def allowed(v):
 return v['frame']=='body' and v['subset']=='all' and v['parityBase']=='all_printed_rows' and v['reset'] in ['global','page'] and ((v['projection']=='complete_lines' and v['phase'] in ['odd','even']) or (v['projection'] in ['first_words','first_word_initials'] and v['phase']=='all'))
selected=[c for c in data['candidates'] if any(allowed(v) for v in c['variants'])]
forms={s for c in selected for s in (c['text'],re.sub(r'\s','',c['text']))}
assert len(selected)==22 and len(forms)==42
windows={22:0,30:0}; shaped={};positions=0
for form in sorted(forms):
 for n in [22,30]:
  windows[n]+=max(0,len(form)-n+1)
  for match in re.finditer(r'(?=(S[1-9A-HJ-NP-Za-km-z]{'+str(n-1)+r'}))',form):
   value=match.group(1)
   fingerprint=hashlib.sha256(b'KEY404/minikey-window-audit/fingerprint/v1\0'+value.encode('ascii')).hexdigest()
   shaped[fingerprint]={'length':len(value),'valid':hashlib.sha256((value+'?').encode('ascii')).digest()[0]==0}
   positions+=1
assert windows=={22:113830,30:113494}
out={'implementation':'independent Python regex lookahead + hashlib','streams':len(selected),'forms':len(forms),'positionWindows':windows,'shapeOccurrences':positions,'uniqueShapedWindows':len(shaped),'checksumValid':sum(x['valid'] for x in shaped.values()),'candidates':shaped}
with Path(sys.argv[1]).open('x', encoding='utf-8') as handle:
 handle.write(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='candidates'}))
