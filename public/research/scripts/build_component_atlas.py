#!/usr/bin/env python3
"""Source-only eight-connected foreground-component atlas; no gap/bit operations.

Both candidate layers are preserved without filtering, clipping, joining or repair.
The atlas does not certify glyph ownership. A separate source-only visual proof
must assign components to canonical tokens or mark them non-glyph/unknown.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

sys.dont_write_bytecode = True
PLAN = {
    'version': 1,
    'purpose': 'source-only foreground-component inventory, not a cipher test',
    'connectivity': 8,
    'dark': 'maxRGB < 130',
    'light': 'minRGB > 170 and maxRGB-minRGB < 70',
    'coordinateConvention': 'integer XYXY, right/bottom exclusive; native row crop',
    'componentOrdering': 'minimum occupied (y,x) in raster order, per layer',
    'retention': 'ALL components, including single pixels, border components and background fields',
    'componentGeometry': 'exact run-length pixel membership, bounding box, area and crop-border flag only',
    'ownership': 'unassigned; no automatic glyph/background or token certification',
    'forbidden': ['gap calculation', 'gap median', 'bits', 'decoders', 'candidate checks',
                  'morphology', 'resampling', 'component deletion', 'network'],
    'caps': {'nativeWidth': 2544, 'nativeHeight': 200, 'rows': 142,
             'canonicalTokens': 1258, 'outBytes': 60000000},
}

def need(value, message):
    if not value:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def components(mask):
    """RLE union-find; adjacent scanline runs join at a shared edge or corner."""
    import numpy as np
    height, width = mask.shape
    runs = []
    parents = []
    previous = []
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parents[max(a,b)] = min(a,b)
    for y in range(height):
        padded = np.concatenate(([False], mask[y], [False])).astype('int8')
        changes = np.diff(padded)
        starts = np.flatnonzero(changes == 1)
        ends = np.flatnonzero(changes == -1)
        current = []
        left_previous = 0
        for start, end in zip(starts, ends):
            x0, x1 = int(start), int(end)
            i = len(runs)
            runs.append([y, x0, x1]); parents.append(i)
            current.append(i)
            while left_previous < len(previous) and runs[previous[left_previous]][2] < x0:
                left_previous += 1
            j = left_previous
            # A previous run [a,b) diagonally touches [x0,x1) iff b>=x0 and a<=x1.
            while j < len(previous) and runs[previous[j]][1] <= x1:
                p = previous[j]
                if runs[p][2] >= x0:
                    union(i, p)
                j += 1
        previous = current
    groups = {}
    for i, run in enumerate(runs):
        groups.setdefault(find(i), []).append(run)
    answer = []
    for number, group in enumerate(groups.values(), 1):
        x0 = min(r[1] for r in group); x1 = max(r[2] for r in group)
        y0 = group[0][0]; y1 = group[-1][0]+1
        answer.append({'number':number, 'box':[x0,y0,x1,y1],
                       'area':sum(r[2]-r[1] for r in group), 'runs':group,
                       'touchesCropBorder':x0==0 or y0==0 or x1==width or y1==height,
                       'sourceOwnership':'unassigned'})
    return answer

def layers(rgb):
    import numpy as np
    pix = np.asarray(rgb).astype('int16')
    low, high = pix.min(2), pix.max(2)
    return {'dark':high < 130, 'light':(low > 170)&((high-low) < 70)}

def self_test():
    import numpy as np
    from PIL import Image
    checks = 0
    for raw, expected in [([[0]],0), ([[1]],1), ([[1,0,1]],2),
                          ([[1,0],[0,1]],1), ([[1,0,0],[0,0,1]],2),
                          ([[1,0,1],[1,1,1]],1), ([[1,1,1],[1,0,1],[1,1,1]],1)]:
        m = np.array(raw,dtype=bool); records = components(m)
        need(len(records)==expected,'synthetic-connectivity')
        rebuilt = np.zeros_like(m)
        for c in records:
            for y,a,b in c['runs']:
                need(not rebuilt[y,a:b].any(),'synthetic-overlap')
                rebuilt[y,a:b] = True
            need(c['area']==sum(b-a for y,a,b in c['runs']),'synthetic-area')
        need(np.array_equal(rebuilt,m),'synthetic-pixel-roundtrip')
        checks += 1
    p = Image.new('RGB',(6,1)); p.putdata([(0,0,0),(129,129,129),(130,130,130),
                                         (170,170,170),(171,171,171),(240,150,60)])
    ls = layers(p)
    need(ls['dark'].tolist()==[[True,True,False,False,False,False]],'synthetic-dark-strict')
    need(ls['light'].tolist()==[[False,False,False,False,True,False]],'synthetic-light-strict')
    checks += 2
    rgb = Image.new('RGB',(9,7),'white')
    rgb.paste('black',(2,1,7,6)); rgb.putpixel((4,3),(255,255,255))
    records = components(layers(rgb)['light'])
    need(len(records)==2 and records[0]['touchesCropBorder'] and not records[1]['touchesCropBorder'],
         'synthetic-paper-vs-enclosed-light-candidate')
    need(all(r['sourceOwnership']=='unassigned' for r in records),'synthetic-no-auto-certification')
    checks += 2
    return {'passed':True,'syntheticAssertions':checks,'targetSourceReads':0,'gapOrBitOperations':0}

def run(args):
    from PIL import Image
    started = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    manifest_path = Path(args.manifest).resolve()
    need(manifest_path.stat().st_size <= 1000000, 'manifest-cap')
    raw = manifest_path.read_bytes()
    need(sha(raw)==args.expected_manifest_sha,'manifest-hash')
    source = json.loads(raw)
    rows = source['rows']
    need(len(rows)==142 and len({r['id'] for r in rows})==142,'row-population')
    need(sum(len(r['canonicalTokens']) for r in rows)==1258,'token-population')
    root = manifest_path.parent
    out = Path(args.out).resolve()
    need(not out.exists() and out.parent.is_dir(),'fresh-private-output')
    need(not any(x.casefold()=='public' for x in out.parts),'output-not-public')
    need(not any((p/'.git').exists() for p in out.parents),'output-outside-any-git-checkout')
    need(stat.S_IMODE(out.parent.stat().st_mode)==0o700,'private-parent-mode-required')
    all_rows = []
    for row in rows:
        relative = Path(row['cropPath'])
        need(not relative.is_absolute() and '..' not in relative.parts,'crop-path')
        p = (root/relative).resolve()
        need(p.is_relative_to(root),'crop-symlink-escape')
        need(p.stat().st_size <= 1000000, 'crop-byte-cap')
        b = p.read_bytes()
        need(sha(b)==row['cropSha256'],'native-crop-hash')
        im = Image.open(p).convert('RGB')
        need(im.width==2544 and 1<=im.height<=200,'native-crop-dimensions')
        records = {}
        for name, mask in layers(im).items():
            cs = components(mask)
            for c in cs:
                c['id'] = row['id']+'-'+name+'-'+str(c.pop('number')).zfill(4)
            records[name] = cs
        all_rows.append({'rowId':row['id'],'page':row['page'],
                         'sourceCropSHA256':row['cropSha256'],
                         'sourceCropBox':row['cropBox'],
                         'rotationCCWDegrees':row['rotationCCWDegrees'],
                         'dimensions':[im.width,im.height],'layers':records})
    artifact = {'version':1,'plan':PLAN,'startedAtUTC':started,
                'completedAtUTC':datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                'manifestSHA256':sha(raw),'codeSHA256':sha(Path(__file__).read_bytes()),
                'sourceRows':all_rows,'controls':self_test(),
                'measurementReady':False,'ownershipAssigned':False,
                'activity':{'gapOrMedianOrBitOrDecoderOperations':0,'candidateChecks':0,'network':0}}
    blob = (json.dumps(artifact,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    need(len(blob)<=PLAN['caps']['outBytes'],'output-cap')
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(blob)
    counts={name:sum(len(r['layers'][name]) for r in all_rows) for name in ['dark','light']}
    print(json.dumps({'status':'source-components-unassigned','rows':len(all_rows),
                      'components':counts,'bytes':len(blob),'sha256':sha(blob),
                      'measurementReady':False}))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    a=p.add_mutually_exclusive_group(required=True)
    a.add_argument('--definition',action='store_true');a.add_argument('--self-test',action='store_true');a.add_argument('--run',action='store_true')
    for n in ['manifest','expected-manifest-sha','out']:p.add_argument('--'+n)
    x=p.parse_args()
    if x.definition: print(json.dumps(PLAN,indent=2));return
    if x.self_test:print(json.dumps(self_test(),indent=2));return
    need(all([x.manifest,x.expected_manifest_sha,x.out]),'target-arguments-required')
    run(x)

if __name__=='__main__':main()
