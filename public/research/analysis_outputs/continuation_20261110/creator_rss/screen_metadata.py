#!/usr/bin/env python3
"""Offline fixed-term RSS metadata index. No audio, network or key checks."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET

TERMS = ('bitcoin magazine','george sand','hidden key','private key','mirror','20 btc','20 bitcoin','10 btc','10 bitcoin')
FIELDS = {'title':'title','description':'description',
 'content:encoded':'{http://purl.org/rss/1.0/modules/content/}encoded',
 'itunes:summary':'{http://www.itunes.com/dtds/podcast-1.0.dtd}summary',
 'itunes:subtitle':'{http://www.itunes.com/dtds/podcast-1.0.dtd}subtitle'}
SOURCE_SHA256='0e497db47f546759778ee26c249785de25bed82746f954cf31aed6ee0f9c7b06'
SOURCE_BYTES=342832
ITEMS=165
RADIUS=100
BLOCKS={'br','p','div','li','blockquote','h1','h2','h3','h4','h5','h6','section','article','table','tr','td','th','dl','dt','dd','hr','pre','ul','ol'}
PATTERNS={term:re.compile(re.escape(term),re.IGNORECASE|re.ASCII) for term in TERMS}

class Text(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.parts=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag.split(':')[-1].lower() in BLOCKS:self.parts.append('\n')
  if tag.split(':')[-1].lower()=='a':
   for name,value in attrs:
    if name.lower()=='href' and value is not None:self.links.append(value)
 def handle_endtag(self,tag):
  if tag.split(':')[-1].lower() in BLOCKS:self.parts.append('\n')
 def handle_data(self,data):self.parts.append(data)

def text_field(element):
 # Preserve direct character data and nested markup; ET does not fetch URLs.
 markup=(element.text or '')+''.join(ET.tostring(child,encoding='unicode') for child in element)
 parser=Text();parser.feed(markup);parser.close()
 return ' '.join(''.join(parser.parts).split()),parser.links

def plain(item,tag):
 node=item.find(tag)
 return ''.join(node.itertext()).strip() if node is not None else None

def screen(raw,expected_count):
 if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('DTD/entity declarations outside this screen')
 root=ET.fromstring(raw)
 if root.tag!='rss' or len(root.findall('channel'))!=1:raise ValueError('Unexpected RSS container')
 items=root.findall('./channel/item')
 if len(items)!=expected_count:raise ValueError('Unexpected item population')
 coverage={field:{'presentItems':0,'missingItems':0,'emptyItems':0,'nonemptyItems':0,'mixedItems':0,'elements':0,'emptyElements':0} for field in FIELDS}
 item_coverage=[];hits=[];byterm=Counter();byfield=Counter();itemterm=Counter();hitfields=0
 for ordinal,item in enumerate(items,1):
  guid=plain(item,'guid');states={};itemhits=[];seen_terms=set()
  for field,tag in FIELDS.items():
   elements=item.findall(tag);stats=coverage[field]
   if not elements:stats['missingItems']+=1;states[field]='missing';continue
   stats['presentItems']+=1;stats['elements']+=len(elements);nonempty=0
   for occurrence,element in enumerate(elements,1):
    text,links=text_field(element)
    if not text:stats['emptyElements']+=1
    else:nonempty+=1
    field_had_hit=False
    for term,pattern in PATTERNS.items():
     for match in pattern.finditer(text):
      byterm[term]+=1;byfield[field]+=1;seen_terms.add(term);field_had_hit=True
      lo=max(0,match.start()-RADIUS);hi=min(len(text),match.end()+RADIUS)
      itemhits.append({'field':field,'fieldOccurrence':occurrence,'term':term,
       'matchStartCodepoint':match.start(),'matchEndCodepoint':match.end(),
       'contextStartCodepoint':lo,'context':text[lo:hi],
       'normalizedFieldCodepoints':len(text),'observedUnvisitedFieldHrefs':links})
    if field_had_hit:hitfields+=1
   if nonempty:stats['nonemptyItems']+=1
   else:stats['emptyItems']+=1
   if 0<nonempty<len(elements):stats['mixedItems']+=1;states[field]='mixed'
   else:states[field]='nonempty' if nonempty else 'empty'
  for term in seen_terms:itemterm[term]+=1
  item_coverage.append({'itemOrdinal':ordinal,'guid':guid,'fields':states})
  if itemhits:
   title=item.find('title');normalized_title=text_field(title)[0] if title is not None else None
   hits.append({'itemOrdinal':ordinal,'guid':guid,'title':normalized_title,'pubDate':plain(item,'pubDate'),'hits':itemhits})
 for stats in coverage.values():
  if stats['missingItems']+stats['emptyItems']+stats['nonemptyItems']!=expected_count:raise ValueError('Coverage incomplete')
 return {'itemsScreened':len(items),'fieldCoverage':coverage,'itemFieldCoverage':item_coverage,
  'counts':{'itemsWithAnyHit':len(hits),'hitFieldOccurrences':hitfields,'literalOccurrences':sum(byterm.values()),
   'occurrencesByTerm':{term:byterm[term] for term in TERMS},'itemsByTerm':{term:itemterm[term] for term in TERMS},
   'occurrencesByField':{field:byfield[field] for field in FIELDS}},'hitItems':hits}

def self_test():
 x=ET.fromstring('<description>bit&lt;b&gt;coin&lt;/b&gt;&amp;nbsp;magazine&lt;br&gt;PRIVATE KEY</description>')
 assert text_field(x)[0]=='bitcoin magazine PRIVATE KEY'
 x=ET.fromstring('<description><![CDATA[MiRrOr private-key private keys <!-- george sand -->]]></description>')
 text,_=text_field(x);assert len(list(PATTERNS['mirror'].finditer(text)))==1 and len(list(PATTERNS['private key'].finditer(text)))==1 and not PATTERNS['george sand'].search(text)
 raw=b'<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><item><title>MIRROR</title><description/><itunes:summary/><itunes:summary>20 BTC</itunes:summary><content:encoded>10 bitcoin</content:encoded><guid>synthetic1</guid></item><item><title>plain</title></item></channel></rss>'
 r=screen(raw,2);assert r['counts']['literalOccurrences']==3 and r['counts']['itemsWithAnyHit']==1
 assert r['fieldCoverage']['itunes:summary']=={'presentItems':1,'missingItems':1,'emptyItems':0,'nonemptyItems':1,'mixedItems':1,'elements':2,'emptyElements':1}
 assert r['fieldCoverage']['description']['emptyItems']==1 and r['fieldCoverage']['itunes:subtitle']['missingItems']==2
 try:screen(raw,3)
 except ValueError:pass
 else:raise AssertionError('Population mismatch accepted')
 return {'passed':True,'syntheticControls':6,'targetRSSOpened':False,'requests':0}

def main():
 parser=argparse.ArgumentParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True)
 action.add_argument('--self-test',action='store_true');action.add_argument('--run',action='store_true')
 parser.add_argument('--source');parser.add_argument('--out');args=parser.parse_args()
 if args.self_test:
  if args.source or args.out:raise ValueError('Self-test takes no target input')
  print(json.dumps(self_test()));return
 if not args.source or not args.out:raise ValueError('Source and private output required')
 out=Path(args.out).resolve();plan_path=Path(__file__).resolve().parent/'PLAN.json';plan_bytes=plan_path.read_bytes();plan=json.loads(plan_bytes)
 if tuple(plan['terms'])!=TERMS or tuple(plan['fields'])!=tuple(FIELDS) or plan['source']['sha256']!=SOURCE_SHA256 or plan['contextRadiusCodepoints']!=RADIUS:raise ValueError('Frozen plan differs')
 if any(p.lower()=='public' for p in out.parts) or not out.is_dir():raise ValueError('Existing private output directory required')
 source=Path(args.source);raw=source.read_bytes()
 if len(raw)!=SOURCE_BYTES or hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:raise ValueError('Source bytes differ')
 started=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
 result=screen(raw,ITEMS)
 result={'schemaVersion':1,'screenId':plan['screenId'],'startedAtUTC':started,'completedAtUTC':datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z'),
  'source':{'sha256':SOURCE_SHA256,'bytes':len(raw),'expectedItems':ITEMS},'planSha256':hashlib.sha256(plan_bytes).hexdigest(),
  'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'definition':{'terms':list(TERMS),'fields':list(FIELDS),'contextRadiusCodepoints':RADIUS,'literalCaseRule':'re.IGNORECASE|re.ASCII; no stemming or word boundaries'},
  **result,'classification':'metadata-index-audit; not decoding or independent theory','audioOrCreatorHistoryAbsenceClaimed':False,
  'actions':{'networkRequests':0,'audioRequests':0,'keyOrCryptoChecks':0,'publicEdits':0,'gitActions':0}}
 payload=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 with os.fdopen(os.open(out/'RESULT.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as handle:handle.write(payload)
 print(json.dumps({'itemsScreened':result['itemsScreened'],'counts':result['counts'],'fieldCoverage':result['fieldCoverage'],'resultBytes':len(payload),'resultSha256':hashlib.sha256(payload).hexdigest()},indent=2))

if __name__=='__main__':
 os.umask(0o077);main()
