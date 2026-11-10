#!/usr/bin/env python3
"""Source-only issue26 zone crops for fixed OCR comparison; no cipher logic."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps
ZONES={
102:[('title',[230,235,1840,830],'display-title'),('intro',[240,850,1840,1285],'body-prose'),('stop',[310,1290,1430,1530],'callout'),('brand',[240,1540,1840,1735],'body-prose'),('leftcol',[240,1740,1020,2210],'body-prose'),('rightcol',[1030,1740,1810,2205],'body-prose'),('redcallout',[1030,2205,1640,2355],'callout')],
103:[('intro',[180,245,1770,605],'body-prose-and-heading'),('leftcol',[175,620,930,1110],'body-prose'),('rightcol',[975,630,1760,1250],'body-prose-and-heading'),('centercallout',[600,1265,1320,1380],'callout'),('wideprose',[285,1400,1625,1845],'body-prose'),('redcaption',[760,1845,1145,1920],'callout'),('boldprose',[305,1915,1595,2165],'body-prose'),('closing',[340,2155,1540,2320],'body-prose')],
104:[('intro',[390,240,1715,550],'body-prose'),('redcallout',[440,575,1690,785],'callout'),('body',[390,805,1725,1030],'body-prose'),('closing',[780,1050,1330,1195],'body-prose'),('final',[710,1240,1480,1355],'display-closer')]}
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 jobs=[];views=[]
 for page,zones in ZONES.items():
  f=a.source_dir/f'page_{page-99:02d}.jpg';im=Image.open(f).convert('RGB');assert im.size==(2040,2805)
  for zone,box,role in zones:
   crop=im.crop(box)
   for name,view,scale in [('native',crop,1),('gray-auto-2x',ImageOps.autocontrast(ImageOps.grayscale(crop)).resize((crop.width*2,crop.height*2)),2)]:
    key=f'p{page}-{zone}-{name}';filename=key+'.png';view.save(a.out/filename);jobs.append({'id':key,'path':filename,'mode':'ocr'});views.append({'id':key,'page':page,'zone':zone,'role':role,'box':box,'scale':scale,'file':filename,'sha256':hashlib.sha256((a.out/filename).read_bytes()).hexdigest()})
 (a.out/'jobs.json').write_text(json.dumps({'jobs':jobs},indent=2)+'\n');(a.out/'views.json').write_text(json.dumps({'version':1,'sourceOnly':True,'sourceDimensions':[2040,2805],'views':views},indent=2)+'\n');print(json.dumps({'sourceOnlyViews':len(views),'targetDecodings':0}))
if __name__=='__main__':main()
