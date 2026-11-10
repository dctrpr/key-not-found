#!/usr/bin/env python3
"""Three-row source-feasibility fragments for frozen printed-field polygons.

This NEW visible-field model is not a repair certificate for original glyphs.
No interword measurements, bits, decoders, candidate checks or network.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib,importlib.util,json,os,stat
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

PINS={'build_component_atlas.py':'60bae29d6d043175008040becd731a7a065ba65203f1ff12a7ee50166ceab168',
      'field_fragment_kernel.py':'f8cab8c73e14aa6b34c2024f3a57b7eccc87e8542dba18fff6c01b18642bc026'}
INVENTORY_SHA='a63192daa4b713d90f3e87cc379866d74df494ccf9aa1bc1251504cd32820a7d'
ATLAS_SHA='d4cea4ad782883917153c590ef1d801e961784940a3d11dcb2e0b726881597b5'
APERTURE_SHA='2140d714cb2a7a6c9ae6a910503a9df0a613c814c35e271c2f39de4dba56718d'

def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def module(name):
    p=Path(__file__).with_name(name);need(sha(p)==PINS[name],'kernel-byte-pin')
    spec=importlib.util.spec_from_file_location(name.replace('.','_'),p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def main():
    os.umask(0o077)
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['inventory','atlas','apertures','out']:p.add_argument('--'+name,required=True)
    a=p.parse_args();inventory_path=Path(a.inventory).resolve();atlas_path=Path(a.atlas).resolve()
    aperture_path=Path(a.apertures).resolve();out=Path(a.out).resolve()
    need(sha(inventory_path)==INVENTORY_SHA and sha(atlas_path)==ATLAS_SHA and sha(aperture_path)==APERTURE_SHA,'source-pins')
    need(not out.exists() and out.parent.is_dir(),'fresh-output')
    need(not any(x.casefold()=='public' for x in out.parts),'private-output-only')
    need(not any((x/'.git').exists() for x in out.parents),'outside-git-checkout')
    need(stat.S_IMODE(out.parent.stat().st_mode)==0o700,'private-output-parent')
    atlas_mod=module('build_component_atlas.py');kernel=module('field_fragment_kernel.py')
    controls={'component':atlas_mod.self_test(),'aperture':kernel.self_test()}
    inv=json.loads(inventory_path.read_text());atlas=json.loads(atlas_path.read_text());proposal=json.loads(aperture_path.read_text())
    need(proposal['sourceInventorySHA256']==INVENTORY_SHA,'aperture-inventory-pin')
    need(len(proposal['rows'])==3 and {r['rowId'] for r in proposal['rows']}=={'p77r30','p78r09','p78r10'},'three-row-population')
    need(sum(len(r['fields']) for r in proposal['rows'])==7 and sum(len(r['tokens']) for r in proposal['rows'])==34,'field-token-population')
    need(len({f['fieldId'] for r in proposal['rows'] for f in r['fields']})==7,'unique-fields')
    need(sum(f['kind']=='printed-inverse-field' for r in proposal['rows'] for f in r['fields'])==4,'inverse-field-population')
    need(all(sum(f['kind']=='base-page-complement' for f in r['fields'])==1 for r in proposal['rows']),'one-base-field-per-row')
    need(not proposal['newFragmentsGenerated'] and not proposal['measurementReady'],'source-proposal-state')
    native={r['id']:r for r in inv['rows']};oldrows={r['rowId']:r for r in atlas['sourceRows']}
    started=now();resultrows=[];out.mkdir(mode=0o700)
    for row in proposal['rows']:
        rid=row['rowId'];src=native[rid];old=oldrows[rid]
        need(row['sourceCropSHA256']==src['cropSha256'] and row['sourceCropBox']==src['cropBox'],'row-source-pin')
        image_path=(inventory_path.parent/src['cropPath']).resolve()
        need(image_path.is_relative_to(inventory_path.parent),'native-path-escape')
        need(sha(image_path)==src['cropSha256'],'native-crop-pin')
        image=Image.open(image_path).convert('RGB');width,height=image.size
        need(row['dimensions']==[width,height],'dimensions')
        masks={f['fieldId']:kernel.aperture_mask(width,height,f['polygonCropPixelEdges']) for f in row['fields']}
        inverse=[f for f in row['fields'] if f['kind']=='printed-inverse-field']
        seen=np.zeros((height,width),dtype=bool)
        for f in inverse:
            m=masks[f['fieldId']];need(not (seen&m).any(),'inverse-fields-overlap');seen|=m
        for f in row['fields']:
            if f['kind']=='base-page-complement':
                need(set(f['excludeFieldIDs'])=={x['fieldId'] for x in inverse},'base-complement-declaration')
                masks[f['fieldId']] &= ~seen
        owner_count=np.zeros((height,width),dtype='uint8')
        for m in masks.values():owner_count += m
        need((owner_count==1).all(),'field-domain-partition')
        candidate=atlas_mod.layers(image);labels={};oldids={}
        for name in ['dark','light']:
            lab=np.zeros((height,width),dtype='int32');ids={}
            for i,c in enumerate(old['layers'][name],1):
                ids[i]=c
                for y,x0,x1 in c['runs']:lab[y,x0:x1]=i
            labels[name]=lab;oldids[name]=ids
            need(np.array_equal(lab>0,candidate[name]),'old-atlas-pixel-membership')
        fields=[];display=np.full((height,width,3),18,dtype='uint8')
        palette=[(255,70,140),(20,215,255),(170,240,30),(225,135,255),(255,175,45),(20,245,180),(245,245,245)]
        for i,f in enumerate(row['fields']):
            name=f['glyphForeground'];aperture=masks[f['fieldId']];mask=candidate[name]&aperture
            boundary=kernel.inner_boundary(aperture);cs=atlas_mod.components(mask)
            for c in cs:
                c['id']=f['fieldId']+'-'+name+'-fragment-'+str(c.pop('number')).zfill(4)
                c['sourceOwnership']='unassigned-new-visible-field-fragment'
                parents=set();contact=False
                for y,x0,x1 in c['runs']:
                    parents.update(int(v) for v in np.unique(labels[name][y,x0:x1]));contact|=bool(boundary[y,x0:x1].any())
                    display[y,x0:x1]=palette[i%len(palette)]
                need(len(parents)==1 and 0 not in parents,'restriction-must-not-merge-old-components')
                parent=oldids[name][next(iter(parents))]
                c['oldParentAtlasComponentID']=parent['id'];c['oldParentTouchesCropBorder']=parent['touchesCropBorder']
                c['touchesApertureBoundary']=contact;c['fullOriginalGlyphContainmentCertified']=False
            fields.append({'fieldId':f['fieldId'],'kind':f['kind'],'glyphForeground':name,
                           'polygonCropPixelEdges':f['polygonCropPixelEdges'],'canonicalTokenIDs':f['canonicalTokenIDs'],
                           'aperturePixels':int(aperture.sum()),'candidatePixels':int(mask.sum()),'fragments':cs,
                           'ownershipAssigned':False,'originalGlyphContainmentCertified':False})
        # RGB source is copied unchanged in the upper panel; lower panel is an
        # explicitly derived candidate display, not source pixels or token proof.
        view=Image.new('RGB',(width,height*2+56),'#dddddd');draw=ImageDraw.Draw(view)
        draw.text((8,5),rid+' | original native RGB',fill='black');view.paste(image,(0,28))
        draw.text((8,height+33),'NEW visible-field fragments; unassigned; glyph-edge uncertainty retained',fill='black')
        view.paste(Image.fromarray(display),(0,height+56));view.save(out/(rid+'-VISIBLE-FIELD.png'))
        resultrows.append({'rowId':rid,'sourceCropSHA256':src['cropSha256'],'sourceCropBox':src['cropBox'],
                           'tokens':row['tokens'],'fields':fields,'measurementReady':False})
    artifact={'version':1,'status':'source-feasibility-fragments-unassigned','startedAtUTC':started,'completedAtUTC':now(),
              'inventorySHA256':INVENTORY_SHA,'atlasSHA256':ATLAS_SHA,'apertureProposalSHA256':APERTURE_SHA,
              'scriptSHA256':sha(Path(__file__)),'kernelSHA256s':PINS,'definition':kernel.DEFINITION,'controls':controls,
              'rows':resultrows,'ownershipAssigned':False,'measurementReady':False,
              'activity':{'interwordMeasurements':0,'gapMedians':0,'bits':0,'decodes':0,'candidateChecks':0,'networkRequests':0}}
    data=(json.dumps(artifact,separators=(',',':'),ensure_ascii=False)+'\n').encode();need(len(data)<15000000,'output-cap')
    fd=os.open(out/'FRAGMENTS.private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(data)
    summary={'version':1,'completedAtUTC':artifact['completedAtUTC'],'status':artifact['status'],
             'sourceRows':3,'fields':7,'inverseFields':4,'canonicalTokens':34,
             'sourceEdgeContactTokens':sum(t['sourceEdgeContactRecognized'] for r in resultrows for t in r['tokens']),
             'fragments':sum(len(f['fragments']) for r in resultrows for f in r['fields']),
             'apertureBoundaryContactFragments':sum(c['touchesApertureBoundary'] for r in resultrows for f in r['fields'] for c in f['fragments']),
             'fragmentSHA256':hashlib.sha256(data).hexdigest(),'measurementReady':False,'activity':artifact['activity']}
    (out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))

if __name__=='__main__':main()
