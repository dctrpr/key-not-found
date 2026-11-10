#!/usr/bin/env python3
"""Independent saved-output/count/checksum audit for mirror-envelope zero results.
Does not independently regenerate the image geometry or selector.
Usage: python3 scripts/verify_mirror_boundary_envelope.py RESULT.json READINGS.jsonl.gz NEW_CHECK.json
"""
import gzip,json,sys,tempfile
from pathlib import Path
from verify_batch20_text import verify

def main():
 result,readings,destination=map(Path,sys.argv[1:])
 if destination.exists():raise ValueError('Use a new output file')
 records=[];ids=set()
 with gzip.open(readings,'rt',encoding='utf-8') as handle:
  for line in handle:
   item=json.loads(line)
   if not isinstance(item.get('id'),str) or not isinstance(item.get('text'),str):raise ValueError('Invalid saved reading')
   if item['id'] in ids:raise ValueError('Duplicate labeled reading ID')
   ids.add(item['id']);records.append({'id':item['id'],'text':item['text']})
 r=json.loads(result.read_text())
 if len(records)!=r['procedureCounts']['labeledReadings']:raise ValueError('Incomplete saved envelope')
 with tempfile.TemporaryDirectory(prefix='key404-envelope-audit-') as folder:
  source=Path(folder)/'streams.json';source.write_text(json.dumps({'streams':records}))
  report=verify(result,source)
 report['uniqueLabeledReadingIDs']=len(ids)
 report['scope']='Independent saved-output completeness/form/count and actual shape checksum audit. Does not independently regenerate the geometry or selector; unsupported candidate types stop the audit.'
 with destination.open('x') as out:json.dump(report,out,indent=2);out.write('\n')
 print(json.dumps({'passed':report['passed'],'readings':len(records),'validRecords':report['validRecords']}))
if __name__=='__main__':main()
