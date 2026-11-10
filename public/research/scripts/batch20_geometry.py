#!/usr/bin/env python3
"""Ten fixed KEY404 geometry/image procedures. No target work at import/self-test.

Run only after public registration, always with a fresh explicit --out directory.
Raw streams/images/OCR stay in *.private artifacts; RESULT.json is allowlisted.
Requires Pillow, NumPy and PyMuPDF. Vision procedures also require macOS/Swift.
No network, wallet access, arbitrary scalar windows or text-to-key hashing.
"""
from __future__ import annotations
import argparse,collections,datetime,hashlib,io,itertools,json,math,os,re,subprocess,sys,time
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PDF='magazine.pdf'; LINES='sources/printed-lines.json'
MODEL='analysis_outputs/3d_article_map/article_3d_map_data.json'
INVERTED='analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json'
CAPSULE='analysis_outputs/source_audit/opener_pill_cash_inventory/opener_pill_cash_inventory.json'
FRAGMENTS='analysis_outputs/continuation_20261109/george_sand/highlight_physical_lines.json'
WORD_GEOMETRY='sources/word-geometry-20261110.json'
SWIFT='scripts/batch20_vision.swift'
DATAMATRIX='scripts/batch20_support/vision-datamatrix-control.png'
DATAMATRIX_TEXT='scripts/batch20_support/vision-datamatrix-control.txt'
COMMON_INPUTS=['scripts/batch20_support/english.txt','scripts/batch20_support/controls.json']
FIXED_PINS={
 PDF:'a30c61f8c49674afb7bccc6680d6477f6e919175386a2422de0a944db4e76c13',
 LINES:'c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe',
 MODEL:'22c2285a6cd53f6bdda7bdd284d556c52ff55dea0a55cd1b549acbb81443eac3',
 INVERTED:'4d6d029bf5f7e90acfa1d456bc94e790913c7865b923c9367212c219867742f3',
 CAPSULE:'2a13fb6be27a69acdace3b5382bf96a7652ac2d46582e69b6d793b5385a29095',
 FRAGMENTS:'cc3b71163cd186c19337462639551f6ab97c407268e5e478ee5f101d716763f9',
 DATAMATRIX:'4f395fb1356cfa598ef08f3aaa07d372e1b836c6bc7bc08a6820a4584db2facc',
 DATAMATRIX_TEXT:'84d89877f0d4041efb6bf91a16f0248f2fd573e6af05c19f96bedb9f882f7882',
 WORD_GEOMETRY:'e3348d0d60d3097b05d0afdb0a1fccf66409274408af9ae7a9369c37fe596e9f'}
PAIRS=((76,77),(77,76),(78,79),(79,78))
DECODERS={'baconAlphabets':['ABCDEFGHIKLMNOPQRSTUWXYZ','ABCDEFGHIJKLMNOPQRSTUVWXYZ'],
 'baconPhases':[0,1,2,3,4],'asciiPhases':list(range(8)),
 'bitAssignments':['original','complement'],'orders':['forward','reverse'],
 'incompleteBlocks':'Record unused prefix/suffix; no padding or guessed bits.',
 'invalidDecodedGroup':'␞ hard boundary; no deletion, word joining or format window across invalid groups/bytes.'}
FORMATS=['wif','minikey','hex64','bip39']
NON_TEXT_TRANSLATION={n:'␞' for n in range(256) if n not in (9,10,13) and not 32<=n<=126}
def definition(id,title,family,priority,inputs,parameters,controls,negative,limits):
 return dict(id=id,title=title,family=family,priority=priority,inputPaths=inputs,
  parameters=parameters,controls=controls,negativeCriterion=negative,limitations=limits)
TEST_DEFINITIONS=[
 definition('G01','Mirror first, then first selected word','mirror-firstword-composition','primary',
 [PDF,LINES,MODEL,INVERTED,WORD_GEOMETRY],
 {'pairs':[list(p) for p in PAIRS],'maskClasses':['orange','black'],'scopeCount':5,
  'horizontal':['leftmost','rightmost'],'vertical':['down','up'],
  'projections':['words-spaced','words-joined','initials'],'boundaryUncertaintyPx':12,'wordCenterGuard':'max(12,frozen centerUncertaintyPx)',
  'geometry':'Word centers inverse-transformed from the documented row deskew frame; fixed horizontal page mirror only.',
  'maximumLabeledStreams':120},['synthetic-mask-firstword','synthetic-mirror-involution','shared-format-controls'],
 'No validated literal key in complete, unambiguous frozen readings excludes only these exact readings.',
 ['Incomplete or boundary-ambiguous selected word geometry makes the affected stream inconclusive.',
  'Direction/projection variants are not independent theories.75→74 has no target body and is outside this scope.']),
 definition('G02','Two-sided printed highlight stencil','duplex-color-truth-table','coverage-correction',
 [PDF,LINES,MODEL,INVERTED,WORD_GEOMETRY],
 {'pairs':[list(p) for p in PAIRS],'selectors':['same-color','opposite-color','source-only','target-only'],
  'orders':['forward','reverse'],'projections':['words-spaced','initials','finals'],
  'scopeCount':5,'boundaryUncertaintyPx':12,'wordCenterGuard':'max(12,frozen centerUncertaintyPx)','maximumLabeledStreams':120},
 ['synthetic-three-state-truth-table','shared-format-controls'],
 'No validated literal key excludes only the declared word-center truth tables with complete geometry.',
 ['Uses corrected physical pairs and actual printed masks, not old chosen-p76 phrase boxes.',
  'Ambiguous target geometry/color is preserved and prevents a complete negative for affected readings.']),
 definition('G03','Orange/black two-alphabet channel','printed-highlight-state','exploratory',
 [LINES,FRAGMENTS],{'unitTypes':['fragment','word','letter'],'scopes':['global',75,76,77,78,79],
 'fragmentCount':46,'decoders':DECODERS,'maximumLabeledDecodes':1296},
 ['synthetic-bacon-24-and-26','synthetic-ascii','incomplete-block-recording','shared-format-controls'],
 'No validated literal key excludes the exact declared color-state serializations/decodes.',
 ['Color encoding was not specified by the creator; no DOCM/manual partial-bold state is used.',
  'Readable-looking fragments or a weak checksum do not establish intentional encoding.']),
 definition('G04','Fixed interword-gap binary channel','interword-spacing','conditional',
 [PDF,LINES,WORD_GEOMETRY],{'scopes':['global',75,76,77,78,79],
 'threshold':1.5,'measurement':'Original ink extents inside frozen lexical-word regions; consecutive ink gap divided by row median.',
 'foreground':'Per-scanline edge-column background median maxRGB>170 chooses black maxRGB<130; otherwise white minRGB>170 and spread<70.',
 'inkColumnMinimum':2,'edgeGuardPx':1,'glyphVerticalMarginPx':2,
 'verticalBounds':'Full frozen word-box envelope plus2px, bounded by adjacent row-center midpoints; robust ink touching a vertical boundary is unknown.',
 'deskewResampler':'Nearest-neighbor, fixed center, no expansion',
 'equalityBit':0,'decoders':DECODERS,'maximumLabeledDecodes':432},
 ['synthetic-doubled-space-measurement','shared-format-controls'],
 'No literal validated key excludes the exact1.5×median measured ink-gap serialization, not all spacing ciphers.',
 ['Word boxes are machine-verified source geometry, not a claim of original font metadata.',
  'Incomplete rows, nonpositive gaps or unknown geometry make relevant scope inconclusive.']),
 definition('G05','Printed-line displacement channel','line-shift','conditional',
 [PDF,LINES,WORD_GEOMETRY],{'scopes':['global',75,76,77,78,79],
 'measurement':'75th percentile of original ink-column bottoms inside frozen lexical-word regions; paragraph affine line-number detrend.',
 'foreground':'Per-scanline edge-column background median maxRGB>170 chooses black maxRGB<130; otherwise white minRGB>170 and spread<70.',
 'inkColumnMinimum':2,'residualRoundDecimals':6,'glyphVerticalMarginPx':2,
 'verticalBounds':'Full frozen word-box envelope plus2px, bounded by adjacent row-center midpoints; robust ink touching a vertical boundary is unknown.',
 'deskewResampler':'Nearest-neighbor, fixed center, no expansion',
 'bitRule':'Residual>0 is1; residual<=0 is0. No threshold fitting.',
 'reportDisplacementPx':2,'decoders':DECODERS,'maximumLabeledDecodes':432},
 ['synthetic-plus-minus-two-pixel-shifts','synthetic-zero-shift-grid','shared-format-controls'],
 'No literal validated key excludes only the registered ink-bottom residual-sign channel.',
 ['The ink-bottom quantile is an optical baseline proxy, not original font metadata or an exact typographic baseline.',
  'Font/glyph shape, printing and scan noise can create residuals. No general baseline-steganography absence claim.']),
 definition('G06','Reused capsule interior differences','repeated-artwork-difference','source-audit',
 [PDF,CAPSULE,DATAMATRIX,DATAMATRIX_TEXT],{'pairing':'Five source-locked p73/p79 capsule pairs; stored affine only.',
 'interiorErosionPx':2,'channels':['R','G','B','luminance'],'residualViews':20,'combinedChannelStreams':4,
 'controls':10,'differenceMapping':'clip(127+sourceWarp-target,0,255)',
 'ocr':'Apple Vision revision3 accurate en-US, correction off, 8× nearest upscale.'},
 ['same-source-affine-resampling','planted-difference-text','shared-format-controls'],
 'No OCR-readable validated literal key excludes the declared20 registered residual views only.',
 ['Differences may be interpolation/compositing/printing artifacts. Shape reuse alone is not a selector.',
  'Vision failures or positive-control failure prevent a complete negative. Manual review remains useful.']),
 definition('G07','Spectral color-isolation OCR','color-isolation-ocr','coverage-check',
 [PDF,DATAMATRIX,DATAMATRIX_TEXT],{'pages':list(range(73,81)),'differences':['R-G','G-B','B-R'],
 'mapping':'clip((signedDifference+255)/2,0,255)',
 'polarities':['normal','inverted'],'orientations':['normal','horizontal-mirror'],
 'differenceViews':96,'baselineViews':16,'maximumViews':112,
 'ocr':'Apple Vision revision3 accurate en-US, correction off, minimumTextHeight.001'},
 ['synthetic-spectral-key-ocr','synthetic-plain-ocr','no-payload-ocr','shared-format-controls'],
 'No OCR-readable validated literal key excludes only these112 fixed detector views.',
 ['No posthoc contrast/threshold/character substitution. OCR errors can hide genuine text.',
  'This is full-source extraction coverage; earlier RGB registration gates were p76 statistical diagnostics.']),
 definition('G08','Literal machine-readable codes','qr-barcode','sanity-check',
 [PDF,DATAMATRIX,DATAMATRIX_TEXT],{'pages':list(range(73,81)),'rotations':[0,90,180,270],
 'mirrors':[False,True],'invert':[False,True],'scales':[0.5,1,2],
 'symbologies':['QR','DataMatrix','Aztec','Code128'],'views':384,
 'engine':'Apple Vision barcode revision3','decodedUrls':'Never automatically visited or executed.'},
 ['synthetic-QR-Aztec-Code128','pinned-ZXing-DataMatrix','synthetic-mirror-invert-rotations','no-code-image'],
 'No decoded payload excludes only the declared Vision-readable code formats/views.',
 ['No explicit creator QR clue known. Nonstandard, damaged or artistic codes remain possible.',
  'DataMatrix control is a pinned unmodified official ZXing fixture; other controls are CoreImage generated.']),
 definition('G09','Corrected-leaf alignment specificity','duplex-alignment-control','coverage-correction',
 [PDF,LINES,MODEL,INVERTED],{'trueUnorderedPairs':[[76,77],[78,79]],
 'bodyPages':[75,76,77,78,79],'resize':[256,328],'primary':'Mean IoU of the two true horizontally mirrored highlight unions.',
 'wrongPairs':8,'translationGrid':[16,16],'excludeIdentityShift':True,'jointNullShifts':255,
 'retainThreshold':'Primary exceeds every wrong-pair score and at least95% of the fixed joint-shift null.'},
 ['identity-IoU','empty-mask-IoU','planted-alignment-shift'],
 'Failure to distinguish exact normalized alignment from the declared controls does not support that alignment claim.',
 ['Evidence audit, not a key decoder. Nonsignificance is not absence proof.',
  'Old leaf controls largely used wrong pairs; symmetric directions are not independent observations.']),
 definition('G10','Current raster least-bit payload','raster-lsb','low-priority-reserve',
 [PDF],{'pages':list(range(73,81)),'channels':['R','G','B'],'bit':0,
 'orientations':['normal','horizontal-mirror'],'bitOrders':['big','little'],
 'phases':list(range(8)),'maximumStreams':768,
 'decoder':'ASCII text with ␞ hard boundary for nontext bytes; strict literal format validators only; no raw scalar windows.'},
 ['synthetic-channel-LSB-payload','byte-order-and-phase','no-payload-raster','shared-format-controls'],
 'No validated literal key excludes only these768 current-raster serializations.',
 ['A weak file sanity check: physical printing/scanning/JPEG may erase an earlier digital payload.',
  'No arbitrary pixel-buffer hashes or32-byte scalar guesses. This does not rule out print-origin encoding.'])]
for _definition in TEST_DEFINITIONS:
 _definition['inputPaths']=list(dict.fromkeys(_definition['inputPaths']+COMMON_INPUTS))
DEFINITIONS={x['id']:x for x in TEST_DEFINITIONS}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def sha(data):return hashlib.sha256(data).hexdigest()
def read_json(path):return json.loads(path.read_text(encoding='utf-8'))
def save_json(path,value):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',encoding='utf-8') as h:json.dump(value,h,indent=2,ensure_ascii=False);h.write('\n')
def require(condition,message):
 if not condition:raise ValueError(message)
def norm(text):return re.sub(r'[^a-z0-9]','',text.casefold())
def lazy_image():
 import numpy as np
 from PIL import Image,ImageOps,ImageDraw,ImageFont
 return np,Image,ImageOps,ImageDraw,ImageFont
def point_rotate(x,y,deg,w=2544,h=3264):
 # Same fixed-center, no-expand rotation as Pillow: positive is CCW in image coordinates.
 a=math.radians(deg);dx=x-w/2;dy=y-h/2
 return (w/2+math.cos(a)*dx+math.sin(a)*dy,h/2-math.sin(a)*dx+math.cos(a)*dy)
def center(box):return ((box[0]+box[2])/2,(box[1]+box[3])/2)
def within(point,boxes,margin=0):
 x,y=point;hit=False;uncertain=False
 for a,b,c,d in boxes:
  if a<=x<c and b<=y<d:hit=True
  if a-margin<=x<c+margin and b-margin<=y<d+margin:
   if min(abs(x-a),abs(x-c),abs(y-b),abs(y-d))<=margin:uncertain=True
 return hit,uncertain

def load_images():
 import fitz
 np,Image,*_=lazy_image();images={};details=[]
 with fitz.open(ROOT/PDF) as document:
  require(len(document)==8,'Expected eight source pages')
  for index in range(8):
   page=document[index];image_refs=page.get_images(full=True)
   require(len(image_refs)==1,'Expected one authoritative embedded image per page')
   raw=document.extract_image(image_refs[0][0])['image']
   image=Image.open(io.BytesIO(raw)).convert('RGB').transpose(Image.Transpose.ROTATE_180)
   require(image.size==(2544,3264),'Unexpected authoritative image size')
   images[73+index]=image
   details.append(dict(page=73+index,embeddedImageSha256=sha(raw),
    uprightRGBSha256=sha(image.tobytes()),width=2544,height=3264,rotationDegrees=180))
 return images,details

def get_masks(model,inverted):
 result={}
 for p in model['pages']:
  number=p['page']
  if not 75<=number<=79:continue
  orange=[h['box'] for h in p['highlights'] if not(number==79 and int(h['id'].rsplit('_',1)[1])>=6)]
  black=inverted['boxes'].get(str(number),[])
  result[number]={'orange':orange,'black':black}
 return result

def load_geometry(rows):
 data=read_json(ROOT/WORD_GEOMETRY);by_id={r['id']:r for r in data['rows']};result=[]
 for canonical in rows:
  rec=by_id.get(canonical['id']);item=dict(canonical)
  if rec is None:item.update(words=[],geometryStatus='unmapped')
  else:
   words=[w for w in rec.get('words',[]) if any(c.isalnum() for c in w.get('text',''))];tokens=[t for t in canonical['text'].split() if any(c.isalnum() for c in t)]
   exact=len(words)==len(tokens) and all(w.get('text')==t for w,t in zip(words,tokens))
   bounded=all(isinstance(w.get('box'),list) and len(w['box'])==4 and
    0<=w['box'][0]<w['box'][2]<=2544 and 0<=w['box'][1]<w['box'][3]<=3264 for w in words)
   verified=all(w.get('verified') is True for w in words)
   status='complete' if rec.get('status')=='complete' and exact and bounded and verified else 'ambiguous'
   item.update(words=words,geometryStatus=status,
    geometryRotationCCW=rec.get('rotationCCWDegrees',canonical['locator'].get('rotate_ccw_degrees',0)))
  result.append(item)
 return result,data

def stream(id,text,**meta):return dict(id=id,text=text,**meta)
def projections(words,kinds):
 out={}
 for kind in kinds:
  if kind in ('words-spaced','words'):out[kind]=' '.join(words)
  elif kind=='words-joined':out[kind]=''.join(words)
  elif kind=='initials':out[kind]=''.join(next((c for c in w if c.isalnum()),'') for w in words)
  elif kind=='finals':out[kind]=''.join(next((c for c in reversed(w) if c.isalnum()),'') for w in words)
 return out

def binary_decodes(items,prefix):
 # items[{page,bits:[0,1,...]}]. All incomplete bits are recorded in private metadata.
 streams=[]
 for scope in ['global',75,76,77,78,79]:
  bits=[b for item in items if scope=='global' or item['page']==scope for b in item['bits']]
  for complement in [False,True]:
   assigned=[b^int(complement) for b in bits]
   for order in ['forward','reverse']:
    seq=assigned if order=='forward' else assigned[::-1]
    for alphabet in DECODERS['baconAlphabets']:
     for phase in range(5):
      groups=[seq[k:k+5] for k in range(phase,len(seq)-4,5)]
      nums=[sum(b<<(4-i) for i,b in enumerate(g)) for g in groups]
      text=''.join(alphabet[n] if n<len(alphabet) else '␞' for n in nums)
      streams.append(stream(f'{prefix}:scope{scope}:c{int(complement)}:{order}:bacon{len(alphabet)}:p{phase}',text,
       sourceBits=len(bits),unusedPrefix=seq[:phase],unusedSuffix=seq[phase+5*len(groups):]))
    for phase in range(8):
     groups=[seq[k:k+8] for k in range(phase,len(seq)-7,8)]
     nums=[sum(b<<(7-i) for i,b in enumerate(g)) for g in groups]
     text=''.join(chr(n) if n in (9,10,13) or 32<=n<=126 else '␞' for n in nums)
     streams.append(stream(f'{prefix}:scope{scope}:c{int(complement)}:{order}:ascii:p{phase}',text,
       sourceBits=len(bits),unusedPrefix=seq[:phase],unusedSuffix=seq[phase+8*len(groups):]))
 return streams

def source_preflight(test_id=None):
 ids=[test_id] if test_id else list(DEFINITIONS)
 paths=sorted({p for id in ids for p in DEFINITIONS[id]['inputPaths']})
 report={'files':{},'rowCount':None,'capsulePairs':None}
 for rel in paths:
  p=ROOT/rel
  report['files'][rel]={'available':p.is_file()}
  if p.is_file():report['files'][rel].update(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
 if (ROOT/LINES).exists():report['rowCount']=len(read_json(ROOT/LINES)['rows'])
 if (ROOT/CAPSULE).exists():
  capsule=read_json(ROOT/CAPSULE);report['capsulePairs']=min(len(capsule['p73CapsulesTopToBottom']),len(capsule['p79PillFragmentsFromManualOrangeBoxes']))
 if (ROOT/WORD_GEOMETRY).exists():
  rows,_=load_geometry(read_json(ROOT/LINES)['rows'])
  report['geometryRows']=dict(collections.Counter(r['geometryStatus'] for r in rows))
 return report

def validate_registration(protocol_path,test_id,registration_commit):
 protocol=read_json(protocol_path)
 require(protocol.get('batchId')=='keiser-20261110-batch20','Unexpected registered batch')
 require(re.fullmatch(r'[a-f0-9]{40}',registration_commit or '') is not None,'Missing registration commit')
 tests=protocol.get('tests',[])
 entry=next((x for x in tests if x.get('id')==test_id),None)
 require(entry is not None,'Test absent from registered protocol')
 expected=DEFINITIONS[test_id]
 require(entry.get('parameters')==expected['parameters'],'Registered parameters differ from implementation')
 for rel in expected['inputPaths']:
  p=ROOT/rel
  require(p.is_file(),'A registered source is unavailable')
  actual=sha(p.read_bytes())
  require(protocol.get('sourceHashes',{}).get(rel)==actual,'Registered source hash mismatch')
  if rel in FIXED_PINS:require(FIXED_PINS[rel]==actual,'Original source pin mismatch')
 for rel in ['scripts/batch20_geometry.py',SWIFT,'scripts/batch20_common.py']:
  require(protocol.get('scriptHashes',{}).get(rel)==sha((ROOT/rel).read_bytes()),'Registered implementation hash mismatch')
 return protocol,entry

def compile_vision(out):
 binary=out/'vision-reader';require(not binary.exists(),'Vision output already exists')
 (out/'swift-temp.private').mkdir()
 env=dict(os.environ,TMPDIR=str(out/'swift-temp.private'),CLANG_MODULE_CACHE_PATH=str(out/'swift-module-cache.private'))
 r=subprocess.run(['swiftc','-O','-module-cache-path',str(out/'swift-module-cache.private'),str(ROOT/SWIFT),'-o',str(binary)],capture_output=True,text=True,timeout=180,env=env)
 require(r.returncode==0,'Local Swift/Vision helper could not compile')
 return binary

def vision_jobs(out,jobs,binary):
 # Every path stays below the fresh explicit output directory.
 manifest=out/'vision-jobs.private.json';raw=out/'vision-observations.private.json'
 save_json(manifest,{'jobs':jobs})
 p=subprocess.run([str(binary),'--manifest',str(manifest),'--out',str(raw)],capture_output=True,text=True,timeout=3600)
 require(p.returncode==0,'Local Vision job failed')
 return read_json(raw)

def make_control_views(out,binary):
 np,Image,ImageOps,ImageDraw,ImageFont=lazy_image()
 control=out/'vision-controls.private'
 subprocess.run([str(binary),'--make-controls',str(control)],check=True,capture_output=True,timeout=60)
 cfg=read_json(control/'controls.json');jobs=[]
 for path in [DATAMATRIX,DATAMATRIX_TEXT]:require(sha((ROOT/path).read_bytes())==FIXED_PINS[path],'Pinned DataMatrix control changed')
 fixture=Image.open(ROOT/DATAMATRIX).convert('RGB');fixture=fixture.resize((fixture.width*8,fixture.height*8),Image.Resampling.NEAREST);fixture.save(control/'datamatrix.png')
 cfg['generated'].append({'id':'datamatrix','path':'datamatrix.png','payload':(ROOT/DATAMATRIX_TEXT).read_text()})
 expected_by_family={entry['id']:entry['payload'] for entry in cfg['generated']}
 for entry in cfg['generated']:
  base=Image.open(control/entry['path']).convert('RGB')
  for turn,mirror,invert in [(0,False,False),(90,False,False),(180,True,False),(270,True,True)]:
   image=base.rotate(turn,expand=True)
   if mirror:image=ImageOps.mirror(image)
   if invert:image=ImageOps.invert(image)
   name=f'{entry["id"]}-r{turn}-m{int(mirror)}-i{int(invert)}.png';image.save(control/name)
   jobs.append(dict(id='control-'+name,path='vision-controls.private/'+name,mode='barcode'))
 text=Image.open(control/'text.png').convert('RGB');text.save(control/'plain-text.png')
 jobs.append(dict(id='control-text',path='vision-controls.private/plain-text.png',mode='ocr'))
 Image.new('RGB',(800,400),'white').save(control/'blank.png')
 jobs.append(dict(id='control-blank',path='vision-controls.private/blank.png',mode='barcode'))
 # A colored foreground key on slightly different paper; R-G isolates the ink.
 a=np.asarray(text).copy();ink=a.mean(2)<128;a[:]=[220,210,205];a[ink]=[220,170,90]
 colored=Image.fromarray(a);colored.save(control/'colored.png')
 ar=np.asarray(colored).astype('int16');diff=((ar[:,:,0]-ar[:,:,1]+255)/2).astype('uint8')
 Image.fromarray(diff).convert('RGB').save(control/'spectral.png')
 jobs.append(dict(id='control-spectral',path='vision-controls.private/spectral.png',mode='ocr'))
 # Planted difference glyphs and same-source resampling are synthetic, never target crops.
 residual=np.clip(127+(255-np.asarray(text).mean(2)),0,255).astype('uint8')
 Image.fromarray(residual).convert('RGB').save(control/'residual.png')
 jobs.append(dict(id='control-residual',path='vision-controls.private/residual.png',mode='ocr'))
 save_json(out/'control-jobs.private.json',{'jobs':jobs})
 r=subprocess.run([str(binary),'--manifest',str(out/'control-jobs.private.json'),'--out',str(out/'control-observations.private.json')],capture_output=True,timeout=180)
 require(r.returncode==0,'Vision control execution failed')
 raw=read_json(out/'control-observations.private.json');payload=cfg['expectedPayload']
 barcode=[x for x in raw['jobs'] if x['mode']=='barcode' and x['id']!='control-blank']
 by_family=collections.defaultdict(list)
 for row in barcode:
  family=row['id'].split('-')[1];by_family[family].append(any(o.get('payload')==expected_by_family[family] for o in row['observations']))
 texts={x['id']:' '.join(o['text'] for o in x['observations']) for x in raw['jobs'] if x['mode']=='ocr'}
 blank=next(x for x in raw['jobs'] if x['id']=='control-blank')
 return dict(engine=raw['metadata'],barcodeByFamily={k:dict(views=len(v),recovered=sum(v)) for k,v in by_family.items()},
  barcodeAllRecovered=all(any(v) for v in by_family.values()) and len(by_family)==4,
  barcodeControlRule='Each controlled code must be recovered in at least one declared orientation/polarity view; view failures are counted, not hidden.',
  plainTextExact='S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy' in texts.get('control-text',''),
  spectralTextExact='S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy' in texts.get('control-spectral',''),
  residualTextExact='S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy' in texts.get('control-residual',''),
  noCodeBlank=not blank['observations'],dataMatrixSyntheticControl=True)

def basic_self_test():
 # Synthetic-only arithmetic/serialization/selector controls; no ROOT input reads.
 a=(120,330);require(point_rotate(*point_rotate(*a,2.5),-2.5)==a or math.dist(point_rotate(*point_rotate(*a,2.5),-2.5),a)<1e-7,'Rotation inverse failed')
 require(within((5,5),[(0,0,10,10)],1)==(True,False),'Mask center control failed')
 require(within((0.5,5),[(0,0,10,10)],1)==(True,True),'Mask boundary control failed')
 matrix={(s,t):('same-color' if s==t and s else 'opposite-color' if s and t else 'source-only' if s else 'target-only' if t else 'neither') for s in range(3) for t in range(3)}
 require(matrix[(1,1)]=='same-color' and matrix[(1,2)]=='opposite-color' and matrix[(2,0)]=='source-only' and matrix[(0,2)]=='target-only','Truth table failed')
 # A synthetic ASCII and Bacon payload must survive the registered decode pipeline.
 bits=[int(b) for b in ''.join(f'{ord(c):08b}' for c in 'KEY404')]
 d=binary_decodes([dict(page=75,bits=bits)],'synthetic')
 require(any(x['text']=='KEY404' for x in d),'ASCII control failed')
 for alphabet in DECODERS['baconAlphabets']:
  bits=[int(b) for c in 'KEY' for b in f'{alphabet.index(c):05b}']
  require(any(x['text']=='KEY' for x in binary_decodes([dict(page=75,bits=bits)],'synthetic')),'Bacon control failed')
 gaps=[10,20,10,20];median=15
 require([int(x/median>1.5) for x in gaps]==[0,0,0,0],'Gap threshold control failed')
 gaps=[10,10,10,20];median=10
 require([int(x/median>1.5) for x in gaps]==[0,0,0,1],'Doubled gap control failed')
 # The synthetic regular line grid carries no displacement; alternating±2px is recovered.
 import numpy as np
 x=np.arange(20,dtype=float);base=50+40*x;observed=base+np.array([-2,2]*10)
 coeff=np.polyfit(x,observed,1);res=observed-np.polyval(coeff,x)
 require([int(v>0) for v in res]==[0,1]*10,'Line displacement control failed')
 require(float(np.max(abs(base-np.polyval(np.polyfit(x,base,1),x))))<1e-8,'Zero displacement control failed')
 small=np.array([[0,1],[1,0]],dtype=bool)
 require(iou(small,small)==1 and iou(small,~small)==0,'IoU control failed')
 raw=b'KEY404';bits=np.unpackbits(np.frombuffer(raw,dtype=np.uint8))
 require(np.packbits(bits,bitorder='big').tobytes()==raw,'Bit packing control failed')
 np,Image,ImageOps,ImageDraw,ImageFont=lazy_image()
 im=Image.new('RGB',(240,40),'white');draw=ImageDraw.Draw(im)
 wordboxes=[]
 for left,right in [(20,39),(50,69),(80,99),(120,139)]:
  draw.rectangle((left,10,right,25),fill='black');wordboxes.append({'text':'control','box':[left,8,right+1,28]})
 row={'locator':{'box':[0,0,240,40]},'words':wordboxes,'geometryRotationCCW':0}
 regions,err=ink_word_regions(im,row);require(err is None,'Synthetic ink-gap segmentation failed')
 measured=[b['inkLeft']-a['inkRight']-1 for a,b in zip(regions,regions[1:])]
 require(measured==[10,10,20],'Synthetic ink gaps incorrect')
 require([int(g/float(np.median(measured))>1.5) for g in measured]==[0,0,1],'Synthetic ink gap channel incorrect')
 baselines=[]
 for shift in [-2,2]*10:
  im=Image.new('RGB',(100,40),'white');ImageDraw.Draw(im).rectangle((20,10+shift,39,25+shift),fill='black')
  row={'locator':{'box':[0,0,100,40]},'words':[{'text':'control','box':[20,7,40,30]}],'geometryRotationCCW':0}
  regions,err=ink_word_regions(im,row);require(err is None,'Synthetic ink baseline segmentation failed')
  baselines.append(float(np.quantile(regions[0]['columnBottoms'],.75)))
 x=np.arange(20,dtype=float);res=np.round(np.array(baselines)-np.polyval(np.polyfit(x,baselines,1),x),6)
 require([int(v>0) for v in res]==[0,1]*10,'Synthetic pixel baseline channel incorrect')
 from batch20_common import self_test,scan_streams
 common=self_test()
 fixed=[{'id':'a','text':' prefix S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy suffix '},
  {'id':'b','text':' prefix S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy suffix '},
  {'id':'c','text':'prefixS6c56bnXQiBjk9mqSYE7ykVQ7NzrRysuffix'},
  {'id':'d','text':'abandon abandon␞abandon '+ 'abandon '*10+'about'}]
 require(scan_streams_incrementally(iter(fixed))==scan_streams(fixed),'Incremental/full shared scanner agreement failed')
 return dict(passed=True,targetInputsRead=False,targetFormatChecks=0,networkQueries=0,
  controls=['mask-center-boundary','deskew-inverse','three-state-truth-table','Bacon24/26','ASCII','doubled-gap','line-shift±2px','zero-shift-grid','IoU','bit-packing','incremental-full-scanner-agreement','shared-format-controls'],
  common=common)

def g01(context):
 rows=context['geometry'];masks=context['masks'];streams=[];details=[];unknown=[]
 per={}
 for s,t in PAIRS:
  for color in ['orange','black']:
   for edge in ['leftmost','rightmost']:
    selected=[];uncertain=[]
    for row in [r for r in rows if r['page']==t]:
     loc=row['locator']['box'];rotation=row.get('geometryRotationCCW',loc and row['locator'].get('rotate_ccw_degrees',0))
     # Unknown rows are relevant only when a projected mask crosses their row band.
     projected=[[2544-b[2],b[1],2544-b[0],b[3]] for b in masks[s][color]]
     if row['geometryStatus']!='complete':
      corners=[point_rotate(x,y,-rotation) for x,y in [(loc[0],loc[1]),(loc[2],loc[1]),(loc[0],loc[3]),(loc[2],loc[3])]]
      band=[min(y for x,y in corners),max(y for x,y in corners)]
      if any(b[1]-12<band[1] and band[0]<b[3]+12 for b in projected):uncertain.append(row['id']+':incomplete-word-geometry')
      continue
     words=[];row_unknown=False
     for w in row['words']:
      x,y=point_rotate(*center(w['box']),-rotation)
      guard=max(12,float(w.get('centerUncertaintyPx',12)))
      hit,tie=within((x,y),projected,guard)
      if tie:row_unknown=True
      if hit:words.append(w)
     if row_unknown:uncertain.append(row['id']+':mask-boundary-uncertainty')
     if words:
      words.sort(key=lambda w:center(w['box'])[0]);chosen=words[0 if edge=='leftmost' else -1]
      selected.append(dict(rowId=row['id'],text=chosen['text'],wordBox=chosen['box']))
    per[(s,t,color,edge)]=(selected,uncertain)
    details.append(dict(source=s,target=t,color=color,edge=edge,selected=selected,unknown=uncertain))
 for color,edge,order in itertools.product(['orange','black'],['leftmost','rightmost'],['down','up']):
  for scope in [*PAIRS,'global']:
   keys=[(s,t,color,edge) for s,t in PAIRS] if scope=='global' else [(*scope,color,edge)]
   selected=[x for k in keys for x in per[k][0]];u=[x for k in keys for x in per[k][1]]
   if order=='up':selected=selected[::-1]
   prefix=f'G01:{scope}:{color}:{edge}:{order}'
   if u:unknown.append(dict(scope=prefix,reasons=u));continue
   for kind,text in projections([x['text'] for x in selected],['words-spaced','words-joined','initials']).items():streams.append(stream(prefix+':'+kind,text))
 return streams,dict(pairs=4,labeledStreamLimit=120,completeStreams=len(streams),inconclusiveReadingScopes=len(unknown),selectionDetails=details,unknownScopes=unknown),bool(unknown)

def color_at(point,masks,guard=12):
 states=[];unknown=False
 for c,n in [('orange',1),('black',2)]:
  hit,tie=within(point,masks[c],guard);unknown|=tie
  if hit:states.append(n)
 return (states[0] if len(states)==1 else 0),unknown or len(states)>1

def g02(context):
 rows=context['geometry'];masks=context['masks'];streams=[];details=[];unknown=[];per={}
 for s,t in PAIRS:
  selected={k:[] for k in DEFINITIONS['G02']['parameters']['selectors']};u=[]
  for row in [r for r in rows if r['page']==t]:
   if row['geometryStatus']!='complete':
    loc=row['locator']['box'];rotation=row.get('geometryRotationCCW',row['locator'].get('rotate_ccw_degrees',0))
    corners=[point_rotate(x,y,-rotation) for x,y in [(loc[0],loc[1]),(loc[2],loc[1]),(loc[0],loc[3]),(loc[2],loc[3])]]
    band=[min(y for x,y in corners),max(y for x,y in corners)]
    relevant=[*masks[t]['orange'],*masks[t]['black'],*masks[s]['orange'],*masks[s]['black']]
    if any(b[1]-12<band[1] and band[0]<b[3]+12 for b in relevant):u.append(row['id']+':incomplete-word-geometry')
    continue
   rotation=row.get('geometryRotationCCW',row['locator'].get('rotate_ccw_degrees',0))
   for w in row['words']:
    x,y=point_rotate(*center(w['box']),-rotation)
    guard=max(12,float(w.get('centerUncertaintyPx',12)))
    a,au=color_at((2544-x,y),masks[s],guard);b,bu=color_at((x,y),masks[t],guard)
    if au or bu:u.append(row['id']+':color-boundary-uncertainty');continue
    kind='same-color' if a==b and a else 'opposite-color' if a and b else 'source-only' if a else 'target-only' if b else None
    if kind:selected[kind].append(w['text'])
  per[(s,t)]=(selected,u);details.append(dict(source=s,target=t,selected=selected,unknown=u))
 for selector,order in itertools.product(DEFINITIONS['G02']['parameters']['selectors'],['forward','reverse']):
  for scope in [*PAIRS,'global']:
   keys=PAIRS if scope=='global' else [scope]
   words=[w for k in keys for w in per[k][0][selector]];u=[x for k in keys for x in per[k][1]]
   prefix=f'G02:{scope}:{selector}:{order}'
   if u:unknown.append(dict(scope=prefix,reasons=u));continue
   if order=='reverse':words=words[::-1]
   for kind,text in projections(words,['words-spaced','initials','finals']).items():streams.append(stream(prefix+':'+kind,text))
 return streams,dict(pairs=4,labeledStreamLimit=120,completeStreams=len(streams),inconclusiveReadingScopes=len(unknown),selectionDetails=details,unknownScopes=unknown),bool(unknown)

def g03(context):
 fragments=read_json(ROOT/FRAGMENTS)['fragments'];require(len(fragments)==46,'Unexpected frozen physical-fragment count')
 streams=[];inventory={}
 for unit in ['fragment','word','letter']:
  items=[]
  for f in fragments:
   color=f['color'];require(color in ['orange','grey'],'Unexpected printed fragment color')
   count=1 if unit=='fragment' else len(f['text'].split()) if unit=='word' else sum(c.isalpha() for c in f['text'])
   items.append(dict(page=f['page'],bits=[int(color=='orange')]*count))
  inventory[unit]=dict(units=sum(len(x['bits']) for x in items),perPage={str(p):sum(len(x['bits']) for x in items if x['page']==p) for p in range(75,80)})
  streams+=binary_decodes(items,'G03:'+unit)
 return streams,dict(physicalFragments=46,unitInventory=inventory,labeledDecodes=len(streams)),False

def ink_word_regions(image,row,neighbors=None):
 np,Image,*_=lazy_image()
 rotation=row.get('geometryRotationCCW',row['locator'].get('rotate_ccw_degrees',0))
 if rotation:image=image.rotate(rotation,resample=Image.Resampling.NEAREST,expand=False)
 words=sorted(row['words'],key=lambda w:w['box'][0]);regions=[]
 if not words:return [],'no-lexical-words'
 y0=math.floor(min(w['box'][1] for w in words))-2
 y1=math.ceil(max(w['box'][3] for w in words))+2
 row_center=center([min(w['box'][0] for w in words),min(w['box'][1] for w in words),max(w['box'][2] for w in words),max(w['box'][3] for w in words)])
 lower=0;upper=3264
 for other in neighbors or []:
  if other['id']==row['id'] or other['page']!=row['page'] or not other.get('words'):continue
  other_words=other['words'];other_center=center([min(w['box'][0] for w in other_words),min(w['box'][1] for w in other_words),max(w['box'][2] for w in other_words),max(w['box'][3] for w in other_words)])
  other_rotation=other.get('geometryRotationCCW',other['locator'].get('rotate_ccw_degrees',0))
  original_center=point_rotate(*other_center,-other_rotation)
  _,oy=point_rotate(*original_center,rotation)
  if oy<row_center[1]:lower=max(lower,math.floor((oy+row_center[1])/2)+1)
  elif oy>row_center[1]:upper=min(upper,math.ceil((oy+row_center[1])/2))
 y0=max(lower,0,y0);y1=min(upper,3264,y1)
 if y1-y0<3:return [],'insufficient-vertical-glyph-region'
 for i,word in enumerate(words):
  box=word['box']
  left=math.floor((words[i-1]['box'][2]+box[0])/2) if i else math.floor(box[0]-12)
  right=math.ceil((box[2]+words[i+1]['box'][0])/2) if i+1<len(words) else math.ceil(box[2]+12)
  left=max(0,left);right=min(2544,right)
  if right<=left:return [],'nonpositive-word-region'
  pixels=np.asarray(image.crop((left,y0,right,y1))).astype('int16')
  edge_pixels=np.concatenate([pixels[:,:min(3,pixels.shape[1])],pixels[:,-min(3,pixels.shape[1]):]],axis=1)
  background=np.median(edge_pixels,axis=1);light=background.max(1)>170
  black=pixels.max(2)<130;white=(pixels.min(2)>170)&((pixels.max(2)-pixels.min(2))<70)
  ink=np.where(light[:,None],black,white)
  occupied_rows=np.flatnonzero(ink.sum(1)>=2)
  if not len(occupied_rows):return [],'no-robust-ink-rows'
  if int(occupied_rows[0])<1 or int(occupied_rows[-1])>=y1-y0-1:return [],'ink-touches-vertical-region-boundary'
  column_count=ink.sum(0);occupied=np.flatnonzero(column_count>=2)
  if not len(occupied):return [],'no-robust-ink-columns'
  first,last=int(occupied[0]),int(occupied[-1])
  if first<1 or last>=right-left-1:return [],'ink-touches-word-region-boundary'
  bottoms=[y0+int(np.flatnonzero(ink[:,c])[-1]) for c in occupied]
  regions.append(dict(word=word['text'],inkLeft=left+first,inkRight=left+last,
   columnBottoms=bottoms,sourceRegion=[left,y0,right,y1],polarity='scanline-adaptive-from-edge-background'))
 return regions,None

def g04(context):
 np,*_=lazy_image();items=[];measurement=[];unknown=[]
 for row in context['geometry']:
  if row['geometryStatus']!='complete':unknown.append(dict(rowId=row['id'],reason='incomplete-word-geometry'));continue
  regions,reason=ink_word_regions(context['images'][row['page']],row,context['geometry'])
  if reason:unknown.append(dict(rowId=row['id'],reason=reason));continue
  gaps=[b['inkLeft']-a['inkRight']-1 for a,b in zip(regions,regions[1:])]
  if not gaps:continue
  if min(gaps)<=0:unknown.append(dict(rowId=row['id'],reason='nonpositive-measured-gap'));continue
  median=float(np.median(gaps));bits=[int(g/median>1.5) for g in gaps]
  items.append(dict(page=row['page'],bits=bits));measurement.append(dict(rowId=row['id'],gaps=gaps,median=median,bits=bits,wordRegions=regions))
 unknown_ids={u['rowId'] for u in unknown}
 complete_pages={p for p in range(75,80) if not any(r['id'] in unknown_ids for r in context['geometry'] if r['page']==p)}
 streams=binary_decodes(items,'G04')
 if unknown:streams=[s for s in streams if any(f':scope{p}:' in s['id'] for p in complete_pages)]
 return streams,dict(rowsMeasured=len(measurement),gapsMeasured=sum(len(x['gaps']) for x in measurement),completePages=sorted(complete_pages),unknownRows=unknown,measurements=measurement,labeledDecodes=len(streams)),bool(unknown)

def g05(context):
 np,Image,*_=lazy_image();measure=[];unknown=[];bypara=collections.defaultdict(list)
 for row in context['geometry']:
  if row['geometryStatus']!='complete':unknown.append(dict(rowId=row['id'],reason='incomplete-word-geometry'));continue
  regions,reason=ink_word_regions(context['images'][row['page']],row,context['geometry'])
  if reason:unknown.append(dict(rowId=row['id'],reason=reason));continue
  bottoms=[y for region in regions for y in region['columnBottoms']]
  if not bottoms:unknown.append(dict(rowId=row['id'],reason='no-ink-bottoms'));continue
  value=float(np.quantile(bottoms,.75))
  bypara[(row['page'],row['paragraph'])].append((row,value))
 for key,entries in bypara.items():
  if len(entries)<3:unknown.extend(dict(rowId=r['id'],reason='paragraph-too-short-to-detrend') for r,v in entries);continue
  x=np.array([r['printed_row'] for r,v in entries],dtype=float);y=np.array([v for r,v in entries]);coef=np.polyfit(x,y,1);res=np.round(y-np.polyval(coef,x),6)
  for (row,value),residual in zip(entries,res):measure.append(dict(rowId=row['id'],page=row['page'],inkBottomQuantileY=value,residualPx=float(residual),bit=int(residual>0),above2px=bool(abs(residual)>2)))
 lookup={m['rowId']:m for m in measure};items=[dict(page=r['page'],bits=[lookup[r['id']]['bit']]) for r in context['geometry'] if r['id'] in lookup]
 unknown_ids={u['rowId'] for u in unknown}
 complete_pages={p for p in range(75,80) if not any(r['id'] in unknown_ids for r in context['geometry'] if r['page']==p)}
 streams=binary_decodes(items,'G05')
 if unknown:streams=[s for s in streams if any(f':scope{p}:' in s['id'] for p in complete_pages)]
 return streams,dict(rowsMeasured=len(measure),unknownRows=unknown,measurements=measure,labeledDecodes=len(streams),positionProxy='75th percentile of original ink-column bottoms; not exact font baseline'),bool(unknown)

def image_job(image,out,name,mode,jobs):
 folder=out/'images.private';folder.mkdir(exist_ok=True)
 image.save(folder/name)
 jobs.append(dict(id=name.removesuffix('.png'),path='images.private/'+name,mode=mode))

def observations_to_streams(raw,prefix):
 streams=[];failures=[];counts=[]
 for job in raw['jobs']:
  if job['status']!='ok':failures.append(job['id']);continue
  obs=job['observations'];counts.append(dict(id=job['id'],observations=len(obs)))
  if job['mode']=='ocr':
   ordered=sorted(obs,key=lambda o:(-o['box'][3],o['box'][0]));text='\n'.join(o['text'] for o in ordered)
   streams.append(stream(prefix+':'+job['id']+':whole',text))
   for n,o in enumerate(ordered):streams.append(stream(prefix+':'+job['id']+f':observation{n}',o['text']))
  else:
   for n,o in enumerate(obs):
    if isinstance(o.get('payload'),str):streams.append(stream(prefix+':'+job['id']+f':code{n}',o['payload'],symbology=o['symbology']))
 return streams,failures,counts

def g06(context):
 np,Image,*_=lazy_image();out=context['out'];capsule=read_json(ROOT/CAPSULE)
 src=capsule['p73CapsulesTopToBottom'];targets=capsule['p79PillFragmentsFromManualOrangeBoxes']
 require(len(src)==len(targets)==5,'Expected five frozen capsule pairs')
 a=np.array(capsule['p73CapsulesToP79FragmentsFit']['affine']['matrixRowsXYPrediction']);mat=np.vstack([a,[0,0,1]]);inv=np.linalg.inv(mat)
 source=context['images'][73];target=context['images'][79]
 warped=source.transform(target.size,Image.Transform.AFFINE,tuple(inv[:2].reshape(-1)),resample=Image.Resampling.BICUBIC)
 # Same-source resampling control, not a new semantic alignment fit.
 back=warped.transform(source.size,Image.Transform.AFFINE,tuple(mat[:2].reshape(-1)),resample=Image.Resampling.BICUBIC)
 roundtrip=back.transform(target.size,Image.Transform.AFFINE,tuple(inv[:2].reshape(-1)),resample=Image.Resampling.BICUBIC)
 jobs=[];measure=[]
 for i,entry in enumerate(targets):
  x0,y0,x1,y1=map(int,entry['box']);box=(x0+2,y0+2,x1-2,y1-2)
  require(box[2]>box[0] and box[3]>box[1],'Capsule interior too small')
  s=np.asarray(warped.crop(box)).astype(float);t=np.asarray(target.crop(box)).astype(float);c=np.asarray(roundtrip.crop(box)).astype(float)
  for k,name in enumerate(['R','G','B','luminance']):
   aa=s[:,:,k] if k<3 else s.mean(2);bb=t[:,:,k] if k<3 else t.mean(2);cc=c[:,:,k] if k<3 else c.mean(2)
   residual=np.clip(127+aa-bb,0,255).astype('uint8');image=Image.fromarray(residual).convert('RGB');image=image.resize((image.width*8,image.height*8),Image.Resampling.NEAREST)
   image_job(image,out,f'capsule{i+1}-{name}.png','ocr',jobs)
   measure.append(dict(pair=i+1,channel=name,meanAbsoluteDifference=float(np.mean(abs(aa-bb))),roundtripMeanAbsoluteDifference=float(np.mean(abs(aa-cc)))))
  # Ten fixed neighboring patches, two per capsule, same dimensions and mapping.
  for side,direction in [('left',-1),('right',1)]:
   width=box[2]-box[0];b=(max(0,min(2544-width,box[0]+direction*width)),box[1],max(0,min(2544-width,box[0]+direction*width))+width,box[3])
   aa=np.asarray(warped.crop(b)).astype(float).mean(2);bb=np.asarray(target.crop(b)).astype(float).mean(2)
   im=Image.fromarray(np.clip(127+aa-bb,0,255).astype('uint8')).convert('RGB');im.save(out/'images.private'/f'capsule{i+1}-neighbor-{side}.png')
 raw=vision_jobs(out,jobs,context['visionBinary']);streams,failures,counts=observations_to_streams(raw,'G06')
 for name in ['R','G','B','luminance']:
  texts=[]
  for j in raw['jobs']:
   if j['id'].endswith('-'+name) and j['status']=='ok':texts.append('\n'.join(o['text'] for o in sorted(j['observations'],key=lambda o:(-o['box'][3],o['box'][0]))))
  streams.append(stream('G06:all-capsules:'+name,'\n'.join(texts)))
 return streams,dict(capsulePairs=5,residualViews=len(jobs),neighborControls=10,measurements=measure,detectorObservationCounts=counts,failedViews=failures,engine=raw['metadata']),bool(failures) or not(context['visionControls']['plainTextExact'] and context['visionControls']['residualTextExact'])

def g07(context):
 np,Image,ImageOps,*_=lazy_image();jobs=[];out=context['out']
 for p,image in context['images'].items():
  a=np.asarray(image).astype('int16')
  for mirror in [False,True]:
   baseline=ImageOps.mirror(image) if mirror else image
   image_job(baseline,out,f'p{p}-baseline-m{int(mirror)}.png','ocr',jobs)
  for c,d,name in [(0,1,'R-G'),(1,2,'G-B'),(2,0,'B-R')]:
   diff=np.clip((a[:,:,c]-a[:,:,d]+255)/2,0,255).astype('uint8');base=Image.fromarray(diff).convert('RGB')
   for invert,mirror in itertools.product([False,True],repeat=2):
    view=ImageOps.invert(base) if invert else base
    if mirror:view=ImageOps.mirror(view)
    image_job(view,out,f'p{p}-{name}-i{int(invert)}-m{int(mirror)}.png','ocr',jobs)
 require(len(jobs)==112,'Spectral view-count mismatch')
 raw=vision_jobs(out,jobs,context['visionBinary']);streams,failures,counts=observations_to_streams(raw,'G07')
 controls=context['visionControls'];unknown=bool(failures) or not(controls['plainTextExact'] and controls['spectralTextExact'])
 return streams,dict(views=112,failedViews=failures,detectorObservationCounts=counts,engine=raw['metadata']),unknown

def g08(context):
 np,Image,ImageOps,*_=lazy_image();jobs=[];out=context['out']
 for p,image in context['images'].items():
  gray=ImageOps.grayscale(image).convert('RGB')
  for turn,mirror,invert,scale in itertools.product([0,90,180,270],[False,True],[False,True],[0.5,1,2]):
   view=gray.rotate(turn,expand=True)
   if mirror:view=ImageOps.mirror(view)
   if invert:view=ImageOps.invert(view)
   view=view.resize((round(view.width*scale),round(view.height*scale)),Image.Resampling.NEAREST)
   image_job(view,out,f'p{p}-r{turn}-m{int(mirror)}-i{int(invert)}-s{scale}.png','barcode',jobs)
 require(len(jobs)==384,'Barcode view-count mismatch')
 raw=vision_jobs(out,jobs,context['visionBinary']);streams,failures,counts=observations_to_streams(raw,'G08')
 unknown=bool(failures) or not(context['visionControls']['barcodeAllRecovered'] and context['visionControls']['noCodeBlank'])
 return streams,dict(views=384,decodedPayloadOccurrences=len(streams),distinctPayloads=len({s['text'] for s in streams}),failedViews=failures,detectorObservationCounts=counts,engine=raw['metadata']),unknown

def iou(a,b):
 import numpy as np
 union=int(np.logical_or(a,b).sum());return float(np.logical_and(a,b).sum()/union) if union else 0.0

def g09(context):
 np,Image,ImageOps,ImageDraw,ImageFont=lazy_image();masks={};metrics=[]
 for p in range(75,80):
  a=np.asarray(context['images'][p]).astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
  orange=(r>170)&(g>65)&(g<185)&(b<105)&((r-b)>85)&((r-g)>25)
  brightness=(r+g+b)/3;barink=(brightness>185) if p==77 else (brightness<130)
  eligible_image=Image.new('1',context['images'][p].size,0);draw=ImageDraw.Draw(eligible_image)
  for row in context['rows']:
   if row['page']!=p:continue
   x0,y0,x1,y1=row['locator']['box'];rotation=row['locator'].get('rotate_ccw_degrees',0)
   polygon=[point_rotate(x,y,-rotation) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
   draw.polygon(polygon,fill=1)
  eligible=np.asarray(eligible_image,dtype=bool);highlight=np.zeros_like(eligible)
  for color in ['orange','black']:
   for box in context['masks'][p][color]:
    x0,y0,x1,y1=map(int,box);highlight[y0:y1,x0:x1]|=(orange if color=='orange' else barink)[y0:y1,x0:x1]
  mask=(highlight&eligible).astype('uint8')*255
  # Fixed nearest-neighbor binary resampling; no alignment fitting.
  masks[p]=np.asarray(Image.fromarray(mask).resize((256,328),Image.Resampling.NEAREST))>0
  metrics.append(dict(page=p,maskPixels=int(masks[p].sum())))
 true=[(76,77),(78,79)];true_scores=[iou(np.fliplr(masks[a]),masks[b]) for a,b in true];primary=sum(true_scores)/2
 wrong=[dict(pair=[a,b],iou=iou(np.fliplr(masks[a]),masks[b])) for a,b in itertools.combinations(range(75,80),2) if (a,b) not in true]
 null=[]
 for gx,gy in itertools.product(range(16),repeat=2):
  if gx==gy==0:continue
  score=sum(iou(np.roll(np.fliplr(masks[a]),(round(328*gy/16),round(256*gx/16)),axis=(0,1)),masks[b]) for a,b in true)/2
  null.append(dict(grid=[gx,gy],score=score))
 require(len(wrong)==8 and len(null)==255,'Specificity-control count mismatch')
 pvalue=(1+sum(x['score']>=primary for x in null))/256
 retained=primary>max(x['iou'] for x in wrong) and pvalue<=.05
 return [],dict(trueUnorderedPairs=2,trueScores=true_scores,primaryMeanIoU=primary,wrongPairControls=wrong,shiftControls=null,shiftRankP=pvalue,retainedByRegisteredScreen=retained,maskPixels=metrics),False

def scan_streams_incrementally(streams,on_stream=None,formats=FORMATS):
 # Same frozen shared validators and dedup semantics, bounded live memory.
 # Hashes below are domain-separated equality indexes, never key derivations.
 from batch20_common import shape_values,validate_record,wordlist,fingerprint,FINGERPRINT_RULE
 indexes=wordlist()[1] if 'bip39' in formats else None
 minimum_phrase_chars=12*min(map(len,indexes))+11 if indexes else 0
 large_region=re.compile(r'[^␞]{'+str(minimum_phrase_chars)+r'}') if indexes else None
 text_seen=set();form_seen=set();tested={k:set() for k in formats};valid={k:{} for k in formats}
 shapes={k:0 for k in formats};stream_count=0
 for record in streams:
  require(isinstance(record.get('id'),str) and isinstance(record.get('text'),str),'Invalid incremental stream')
  stream_count+=1
  if on_stream:on_stream(record)
  text=record['text'];text_seen.add(sha(b'KEY404/batch20/incremental/text/v1\0'+text.encode('utf-8')))
  for form in [text,re.sub(r'\s','',text)]:
   mark=sha(b'KEY404/batch20/incremental/form/v1\0'+form.encode('utf-8'))
   if mark in form_seen:continue
   form_seen.add(mark)
   for kind in formats:
    if kind=='bip39' and not large_region.search(form):continue
    for value in shape_values(kind,form,indexes):
     shapes[kind]+=1
     if value in tested[kind]:continue
     tested[kind].add(value);checked=validate_record(kind,value,indexes)
     if checked is not None:
      canonical,metadata=checked;fp=fingerprint(kind,canonical)
      valid[kind].setdefault(fp,dict(format=kind,fingerprint=fp,**metadata))
 hits=[hit for kind in formats for _,hit in sorted(valid[kind].items())]
 return dict(streamCount=stream_count,uniqueStreamCount=len(text_seen),uniqueFormCount=len(form_seen),
  formats=list(formats),shapeCounts=shapes,uniqueShapeCounts={k:len(tested[k]) for k in formats},
  executionCount=sum(len(v) for v in tested.values()),validCounts={k:len(valid[k]) for k in formats},
  hits=hits,privateReviewRequired=bool(hits),fingerprintRule=FINGERPRINT_RULE,networkQueries=0,rawAsciiScalarInterpretations=0)

def g10(context):
 np,Image,ImageOps,*_=lazy_image();inventory=[];planes=[];out=context['out']
 folder=out/'bitplanes.private';folder.mkdir(mode=0o700)
 details=dict(labeledStreams=768,inventory=inventory,basePlanes=planes,
  rawStorage='24 exact packed original bitplanes plus deterministic per-view descriptors. Decoded text is streamed into the validators, not retained in memory.')
 def records():
  count=0
  for p,image in context['images'].items():
   original=np.asarray(image)
   for k,c in enumerate(['R','G','B']):
    base=(original[:,:,k].reshape(-1)&1).astype('uint8')
    plane_name=f'p{p}-{c}.packbits';packed=np.packbits(base,bitorder='big').tobytes()
    with (folder/plane_name).open('xb') as handle:handle.write(packed)
    planes.append(dict(page=p,channel=c,path='bitplanes.private/'+plane_name,bits=len(base),bytes=len(packed),width=image.width,height=image.height))
    for mirror in [False,True]:
     bits=(np.fliplr(original[:,:,k]) if mirror else original[:,:,k]).reshape(-1)&1
     for order in ['big','little']:
      for phase in range(8):
       complete=(len(bits)-phase)//8*8;raw=np.packbits(bits[phase:phase+complete],bitorder=order).tobytes()
       text=raw.decode('latin1').translate(NON_TEXT_TRANSLATION)
       meta=dict(sourcePlane='bitplanes.private/'+plane_name,sourceBits=len(bits),page=p,channel=c,mirror=mirror,bitOrder=order,phase=phase,packedBytes=len(raw),unusedSuffixBits=len(bits)-phase-complete,
        renderedStreamFingerprint=sha(b'KEY404/batch20/G10/rendered/v1\0'+text.encode('utf-8')),
        rawViewFingerprint=sha(b'KEY404/batch20/G10/raw-view/v1\0'+raw))
       inventory.append(meta);count+=1
       yield stream(f'G10:p{p}:{c}:m{int(mirror)}:{order}:p{phase}',text,**meta)
  require(count==768,'Raster stream-count mismatch')
 return records(),details,False

PROCEDURES={'G01':g01,'G02':g02,'G03':g03,'G04':g04,'G05':g05,'G06':g06,'G07':g07,'G08':g08,'G09':g09,'G10':g10}
def safe_details(value):
 # Raw OCR/text/word selections and per-view images remain private artifacts.
 if isinstance(value,dict):return {k:safe_details(v) for k,v in value.items() if k not in ['text','selected','selectionDetails','unknownScopes','measurements','shiftControls','inventory']}
 if isinstance(value,list):return [safe_details(v) for v in value]
 return value

def run(args):
 from batch20_common import scan_streams
 began=utc();tick=time.perf_counter();out=Path(args.out).resolve()
 require(not out.exists(),'Refusing existing output directory');out.mkdir(parents=True,mode=0o700)
 base=dict(schemaVersion=1,batchId='keiser-20261110-batch20',testId=args.run,
  startedAtUTC=began,registrationCommit=args.registration_commit,
  protocolSha256=sha(Path(args.protocol).read_bytes()) if Path(args.protocol).is_file() else None,
  scriptSha256=sha(Path(__file__).read_bytes()),swiftSha256=sha((ROOT/SWIFT).read_bytes()),
  networkQueries=0,privateReviewRequired=False)
 try:
  controls=basic_self_test();protocol,registered=validate_registration(Path(args.protocol),args.run,args.registration_commit)
  definition=DEFINITIONS[args.run]
  base.update(title=definition['title'],family=definition['family'],priority=definition['priority'],
   sourceHashes={p:sha((ROOT/p).read_bytes()) for p in definition['inputPaths']},
   parameters=definition['parameters'],limitations=definition['limitations'],controls=controls)
  context={'out':out}
  if LINES in definition['inputPaths']:context['rows']=read_json(ROOT/LINES)['rows']
  if WORD_GEOMETRY in definition['inputPaths']:context['geometry'],context['geometryArtifact']=load_geometry(context['rows'])
  if MODEL in definition['inputPaths']:context['masks']=get_masks(read_json(ROOT/MODEL),read_json(ROOT/INVERTED))
  if PDF in definition['inputPaths']:
   context['images'],base['sourceImageInventory']=load_images()
  if args.run in ['G06','G07','G08']:
   context['visionBinary']=compile_vision(out);context['visionControls']=make_control_views(out,context['visionBinary']);base['visionControls']=context['visionControls']
  streams,details,inconclusive=PROCEDURES[args.run](context)
  if args.run=='G10':
   descriptors=[]
   evaluation=scan_streams_incrementally(streams,on_stream=lambda rec:descriptors.append({k:v for k,v in rec.items() if k!='text'}),formats=FORMATS)
   save_json(out/'streams.private.json',dict(storage='bitplanes.private + deterministic descriptors',streams=descriptors))
   base['incrementalEvaluation']=True
   base['streamInventory']=[{k:v for k,v in rec.items() if k!='sourcePlane'} for rec in descriptors]
  else:
   save_json(out/'streams.private.json',streams)
   evaluation=scan_streams(streams,formats=FORMATS)
  save_json(out/'DETAILS.private.json',details)
  # Raw artifact hashes are domain separated: no plain scalar-equivalent key fingerprints.
  base['privateArtifactNames']=['streams.private.json','DETAILS.private.json']
  base['evaluation']=evaluation;base['procedureCounts']=safe_details(details)
  base['privateReviewRequired']=bool(evaluation.get('privateReviewRequired'))
  if args.run=='G08' and details.get('decodedPayloadOccurrences',0):base['privateReviewRequired']=True
  if base['privateReviewRequired']:outcome='finding-private-review-required'
  elif inconclusive:outcome='inconclusive-source-or-detector-coverage'
  elif args.run=='G09':outcome='alignment-screen-retained' if details['retainedByRegisteredScreen'] else 'alignment-claim-not-supported-by-controls'
  elif args.run=='G08':outcome='no-decodable-machine-readable-payload-in-declared-views'
  else:outcome='no-valid-literal-key-in-declared-complete-readings'
  base.update(outcome=outcome,completeNegative=not inconclusive and not base['privateReviewRequired'] and not(args.run=='G09' and details.get('retainedByRegisteredScreen')), 
   negativeCriterion=definition['negativeCriterion'])
 except Exception as error:
  # An execution/control/input failure is never a successful exclusion.
  base.update(outcome='inconclusive-execution-or-precondition-failure',completeNegative=False,
   errorClass=type(error).__name__,error='Procedure could not complete its registered controls/inputs/execution. Inspect private local environment; no negative claim.')
  save_json(out/'ERROR.private.json',{'class':type(error).__name__,'message':str(error).replace(str(ROOT),'<research>').replace(str(out),'<explicit-output>')[:1200]})
 finally:
  base.update(completedAtUTC=utc(),durationMs=round((time.perf_counter()-tick)*1000))
  save_json(out/'RESULT.json',base)
 print(json.dumps({k:base[k] for k in ['testId','outcome','completeNegative','startedAtUTC','completedAtUTC','durationMs','networkQueries','privateReviewRequired'] if k in base},indent=2))
 return base

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 group=parser.add_mutually_exclusive_group(required=True)
 group.add_argument('--self-test',action='store_true');group.add_argument('--preflight',action='store_true');group.add_argument('--definitions','--list',dest='definitions',action='store_true');group.add_argument('--run',choices=sorted(DEFINITIONS))
 parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out')
 args=parser.parse_args()
 if args.definitions:print(json.dumps(TEST_DEFINITIONS,indent=2));return
 if args.preflight:print(json.dumps(source_preflight(),indent=2));return
 if args.self_test:
  report=basic_self_test()
  if args.out:
   out=Path(args.out).resolve();require(not out.exists(),'Refusing existing self-test output');out.mkdir(parents=True,mode=0o700)
   binary=compile_vision(out);report['vision']=make_control_views(out,binary);save_json(out/'SELF_TEST.json',report)
  print(json.dumps(report,indent=2));return
 require(args.protocol and args.registration_commit and args.out,'Run requires protocol, registration commit and fresh output directory')
 run(args)
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('Geometry procedure failed before execution: '+type(error).__name__+'. No exclusion claimed.',file=sys.stderr);sys.exit(1)
