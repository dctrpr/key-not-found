#!/usr/bin/env python3
"""Copy three exact issue26 source JPEGs and write a local source OCR manifest."""
import argparse,json,hashlib,shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);jobs=[];sources=[]
 for page,n in [(102,3),(103,4),(104,5)]:
  f=a.source_dir/f'page_{n:02d}.jpg';name=f'p{page}.jpg';shutil.copyfile(f,a.out/name);jobs.append({'id':f'p{page}','path':name,'mode':'ocr'});sources.append({'printedPage':page,'file':name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 (a.out/'jobs.json').write_text(json.dumps({'jobs':jobs},indent=2)+'\n');(a.out/'sources.json').write_text(json.dumps({'sourceOnly':True,'sources':sources,'targetDecodings':0},indent=2)+'\n');print(json.dumps({'sourceOnlyViews':3,'targetDecodings':0}))
if __name__=='__main__':main()
