#!/usr/bin/env python3
"""Source-only printed-field aperture primitives; no spacing/key operations.

This is a NEW visible-field model, not the old whole-component atlas. Pixel
centres and an explicit closed even-odd polygon rule define the aperture.
No field coordinates or target sources are read by the synthetic controls.
"""
from __future__ import annotations
import numpy as np

DEFINITION = {
    'classification':'source-feasibility-only, new visible-field model',
    'pixelCoordinates':'native crop integer pixels; evaluate centre (x+0.5,y+0.5)',
    'numericContract':{'integerWidthRange':[1,2544],'integerHeightRange':[1,200],'integerVerticesOnly':True},
    'polygonConvention':'even-odd ray crossing OR point exactly on a polygon segment; integer pixel-edge vertices',
    'candidateIntersection':'fixed atlas polarity predicate AND frozen printed-field aperture',
    'newFragmentConnectivity':8,
    'ownership':'unassigned; fragments are not claimed to be old whole components or full original glyphs',
    'edgeContact':'any retained fragment pixel on the inner eight-neighbour aperture boundary',
    'uncertainty':'glyph-edge contacts remain explicit; no font continuation or missing support inferred',
    'thresholdChanges':False,'morphology':False,'sizeFiltering':False,
    'interwordGapMedianBitOrDecoderOperations':0,'candidateChecks':0,'networkRequests':0,
}

def aperture_mask(width, height, polygon):
    if not (type(width) is int and type(height) is int and 1<=width<=2544 and 1<=height<=200):
        raise ValueError('native-dimension-contract')
    p=np.asarray(polygon,dtype=float)
    if not (p.ndim==2 and p.shape[1]==2 and len(p)>=3 and np.isfinite(p).all() and (p==np.rint(p)).all()):
        raise ValueError('invalid-polygon')
    if not (0<=p[:,0].min() and p[:,0].max()<=width and
            0<=p[:,1].min() and p[:,1].max()<=height):
        raise ValueError('polygon-outside-native-crop')
    yy,xx=np.mgrid[0:height,0:width];x=xx+0.5;y=yy+0.5
    result=np.zeros((height,width),dtype=bool)
    boundary=np.zeros((height,width),dtype=bool)
    for i in range(len(p)):
        ax,ay=p[i];bx,by=p[(i+1)%len(p)]
        # Integer vertices and half-integer centres make these bounded products
        # exactly representable, including diagonal pixel-centre contacts.
        cross=(x-ax)*(by-ay)-(y-ay)*(bx-ax)
        boundary |= (cross==0)&(x>=min(ax,bx))&(x<=max(ax,bx))&(y>=min(ay,by))&(y<=max(ay,by))
        if ay==by:continue
        crosses=(ay>y)!=(by>y)
        crossing=ax+(bx-ax)*(y-ay)/(by-ay)
        result ^= crosses & (x<crossing)
    return result | boundary

def inner_boundary(mask):
    height,width=mask.shape
    padded=np.pad(mask,1,constant_values=False)
    interior=mask.copy()
    for dy in [-1,0,1]:
        for dx in [-1,0,1]:
            if (dy,dx)!=(0,0):interior &= padded[1+dy:1+dy+height,1+dx:1+dx+width]
    return mask & ~interior

def self_test():
    checks=0
    m=aperture_mask(7,6,[[1,1],[5,1],[5,4],[1,4]])
    expected=np.zeros((6,7),dtype=bool);expected[1:4,1:5]=True
    assert np.array_equal(m,expected);checks+=1
    assert np.array_equal(aperture_mask(7,6,[[1,4],[5,4],[5,1],[1,1]]),m);checks+=1
    assert np.array_equal(aperture_mask(7,6,[[5,1],[5,4],[1,4],[1,1]]),m);checks+=1
    b=inner_boundary(m);assert b.sum()==10 and not b[2,2] and not b[2,3];checks+=1
    all_pixels=aperture_mask(7,6,[[0,0],[7,0],[7,6],[0,6]])
    assert all_pixels.all() and inner_boundary(all_pixels).sum()==22;checks+=1
    triangle=aperture_mask(4,4,[[0,0],[4,0],[0,4]])
    assert triangle.tolist()==[[True,True,True,True],[True,True,True,False],
                               [True,True,False,False],[True,False,False,False]];checks+=1
    fragmented=(np.indices(m.shape).sum(0)%2==0)&m
    assert not (fragmented&~m).any() and fragmented.sum()==6;checks+=1
    for poly in [[],[[0,0],[1,1]],[[0,0],[8,0],[0,2]],[[0,0],[1,float('nan')],[0,2]],[[0,0],[1.25,1],[0,2]]]:
        try:aperture_mask(7,6,poly)
        except ValueError:checks+=1
        else:raise AssertionError('invalid-polygon-accepted')
    for width,height in [(0,6),(2545,6),(7,201)]:
        try:aperture_mask(width,height,[[0,0],[1,0],[0,1]])
        except ValueError:checks+=1
        else:raise AssertionError('invalid-dimensions-accepted')
    return {'passed':True,'assertions':checks,'targetSourceReads':0,
            'gapOrMedianOrBitOrDecoderOperations':0}

if __name__=='__main__':
    import json
    print(json.dumps({'definition':DEFINITION,'controls':self_test()},indent=2))
