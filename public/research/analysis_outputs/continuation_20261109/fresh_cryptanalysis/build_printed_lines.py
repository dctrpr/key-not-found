from pathlib import Path
import json, re, difflib, hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
source=OUT/'printed_lines.txt'
canonical=json.loads((ROOT/'analysis_outputs/3d_article_map/canonical_char_model.json').read_text())
page=None;section=None;para=0;rows=[];extras=[]
for raw in source.read_text().splitlines():
 if raw.startswith('# PAGE '):
  page=int(raw.split()[-1]); section='body';para=0
 elif raw.startswith('# GRAPHIC '): page=int(raw.split()[-1]);section='graphic';para=0
 elif raw.startswith('# SIGNATURE '): page=int(raw.split()[-1]);section='signature';para=0
 elif raw.startswith('# DISPLAY '): extras.append({'page':page,'section':'title','paragraph':0,'text':raw[len('# DISPLAY '):]})
 elif raw.strip():
  d={'page':page,'section':section,'paragraph':para,'text':raw.strip()}
  (rows if section=='body' else extras).append(d)
 else: para+=1

def bands(page,region,angle=0):
 im=Image.open(ROOT/f'analysis_outputs/3d_article_map/page_{page}_upright.jpg').convert('RGB')
 if angle: im=im.rotate(angle,fillcolor='white')
 a=np.asarray(im); x0,y0,x1,y1=region; g=a[y0:y1,x0:x1].mean(2)
 mask=g>175 if page==77 else g<95
 count=mask.sum(1); groups=[]
 for y in np.where(count>50)[0]:
  y=int(y)
  if groups and y-groups[-1][-1]<10: groups[-1].append(y)
  else: groups.append([y])
 return [{'box':[x0,g[0]+y0,x1,g[-1]+y0+1],'rotate_ccw_degrees':angle,'coordinate_space':'2544x3264 scan, fixed center rotation without expansion','selection_note':'Broad locator band; x extent is analysis crop, not glyph-tight text boundary.'} for g in groups if g[-1]-g[0]>5]
locators={
 75:bands(75,(350,520,2250,2990)),
 76:bands(76,(420,350,2240,1650))+bands(76,(420,1900,2000,3020)),
 77:bands(77,(380,350,2260,2050))+bands(77,(850,2150,2260,3000)),
 78:bands(78,(425,350,2240,2200)),
 79:bands(79,(500,360,2240,1550),2.5)+bands(79,(500,1750,2240,2490)),
}
highlighted={75:[6,7,9,10,17,18,19,22,24,25,27],76:[1,2,7,8,14,16,21,24,26,31],77:[5,6,7,11,12,14,15,30],78:[8,9,10,12,13,14,20],79:[1,2,3,4,5,7,8,20,21]}
def toks(s):
 return [v for token in s.split() if (v := re.sub(r"^[^A-Za-z0-9$]+|[^A-Za-z0-9]+$", "", token)) and any(c.isalnum() for c in v)]
def norm(s):return ''.join(c for c in s.lower() if c.isalnum())
for page in range(75,80):
 pr=[r for r in rows if r['page']==page]
 assert len(pr)==len(locators[page]),(page,len(pr),len(locators[page]))
 source_words=[t for r in pr for t in toks(r['text'])]
 cwords=canonical['pages'][f'p{page-74}']['words']
 a=[norm(w) for w in source_words];b=[norm(w['text']) for w in cwords]
 mapping={}
 for match in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_matching_blocks():
  for k in range(match.size):mapping[match.a+k]=cwords[match.b+k]
 off=0
 for i,r in enumerate(pr):
  words=toks(r['text']); maps=[mapping.get(off+k) for k in range(len(words))];off+=len(words)
  r.update({'printed_row':i+1,'id':f'p{page}r{i+1:02d}','locator':locators[page][i],
            'highlighted_printed_row':i+1 in highlighted[page],
            'annotation_bold_any':any(w and w['hasBold'] for w in maps),
            'annotation_bold_all':all(w and w['allBold'] for w in maps),
            'first_word':words[0],'last_word':words[-1],
            'bold_label_note':'Aligned to investigator Markdown annotations, not original font metadata.'})
result={'date':'2026-11-09','source':'magazine.pdf, printed pages75–79, visually transcribed against page scans',
        'source_transcript_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'method':'Manually reconstructed actual printed baselines; locator bands independently found by scan ink row-projection. Page79 first paragraph rotated counterclockwise2.5degrees solely to separate tilted printed baselines, not to select text.',
        'counts':{p:sum(r['page']==p for r in rows) for p in range(75,80)},'rows':rows,'optional_display_rows':extras,
        'limitations':['Paragraph grouping follows visible whitespace; it is a hypothesis for parity reset, not a public instruction.','Locators identify rows but approximate entire analysis crop width; rotated-page79 locators are in the stated transformed image coordinates.','P75Really?Yes. is one printed baseline. Title, graphic quotation and signature are separate optional display units.','Bold annotations are secondary/manual; highlight row membership was reviewed directly in scanned pages.','Original scan contains apostrophe/punctuation ambiguities; these do not affect word boundary reading except explicitly preserved apostrophes and dash conventions.']}
(OUT/'printed_lines.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'counts':result['counts'],'total':len(rows),'highlighted_rows':sum(r['highlighted_printed_row'] for r in rows),'any_bold_rows':sum(r['annotation_bold_any'] for r in rows),'all_bold_rows':sum(r['annotation_bold_all'] for r in rows)},indent=2))
