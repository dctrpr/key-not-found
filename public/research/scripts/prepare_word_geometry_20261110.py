#!/usr/bin/env python3
"""Source-only word geometry preflight; no cipher extraction or key tests."""
import argparse,hashlib,json,io,sys
from pathlib import Path
from PIL import Image
import fitz

def digest(data):return hashlib.sha256(data).hexdigest()
def require(condition,message):
 if not condition:raise ValueError(message)
def main():
 p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=False);(a.out/'crops').mkdir();(a.out/'frames').mkdir()
 source=a.corpus/'magazine.pdf';rows_source=a.corpus/'sources/printed-lines.json'
 source_bytes=source.read_bytes();row_bytes=rows_source.read_bytes()
 require(digest(source_bytes)=='a30c61f8c49674afb7bccc6680d6477f6e919175386a2422de0a944db4e76c13','Source PDF hash mismatch')
 require(digest(row_bytes)=='c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe','Canonical rows hash mismatch')
 model=json.loads(row_bytes);doc=fitz.open(source);frames={};source_images=[]
 for page in range(75,80):
  pdfpage=doc[page-73];images=pdfpage.get_images(full=True);require(len(images)==1,'Unexpected source image count')
  embedded=doc.extract_image(images[0][0]);image=Image.open(io.BytesIO(embedded['image'])).convert('RGB').rotate(180)
  require(image.size==(2544,3264),'Unexpected source image dimensions')
  frames[(page,0.0)]=image;image.save(a.out/'frames'/f'p{page}-upright.png')
  source_images.append({'page':page,'embeddedImageSha256':digest(embedded['image']),'width':image.width,'height':image.height,'uprightRotationDegrees':180})
 jobs=[];records=[]
 for row in model['rows']:
  loc=row['locator'];angle=float(loc['rotate_ccw_degrees']);key=(row['page'],angle)
  if key not in frames:
   frames[key]=frames[(row['page'],0.0)].rotate(angle,fillcolor='white')
   frames[key].save(a.out/'frames'/f'p{row["page"]}-ccw{angle:g}.png')
  image=frames[key];x0,y0,x1,y1=loc['box'];crop_box=[0,max(0,y0-12),2544,min(3264,y1+12)]
  crop=image.crop(crop_box);filename='crops/'+row['id']+'.png';crop.save(a.out/filename)
  jobs.append({'id':row['id'],'path':filename,'mode':'ocr'})
  records.append({'id':row['id'],'page':row['page'],'canonicalText':row['text'],'canonicalTokens':row['text'].split(),'rotationCCWDegrees':angle,'coordinateSpace':'2544x3264 fixed-center rotated scan; top-left origin','locator':loc['box'],'cropBox':crop_box,'cropPath':filename,'cropSha256':digest((a.out/filename).read_bytes())})
 metadata={'sourcePdf':'magazine.pdf','sourcePdfSha256':digest(source_bytes),'canonicalRows':'sources/printed-lines.json','canonicalRowsSha256':digest(row_bytes),'method':'Extract exact embedded JPEG, rotate180 upright; canonical locator row crop full width with fixed12px verticalpadding. p79 firstparagraph fixed2.5CCW nearest-neighbor noexpansion, exactly as locator source. No text model fitting.','sourceImages':source_images,'rows':records}
 for name,value in [('jobs.json',{'jobs':jobs}),('row-crops.json',metadata)]:
  q=a.out/name;require(not q.exists(),'Output already exists');q.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'preparedRows':len(records),'jobs':len(jobs),'imageFrames':len(frames),'targetKeyChecks':0}))
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('Source geometry preparation failed: '+type(error).__name__+'. No source result produced.',file=sys.stderr);sys.exit(1)
