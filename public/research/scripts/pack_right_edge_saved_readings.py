#!/usr/bin/env python3
"""Privately copy exactly two registered existing right-edge readings."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

TEST_ID = 'issue24-saved-right-edge-reading-review'
SOURCE = 'analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json'
SOURCE_SHA = '1651a33dab46babf36f56439ddb409058cfa36712d96ead7d4200962b80817b9'
SCRIPT = 'scripts/pack_right_edge_saved_readings.py'
PROTOCOL = 'analysis_outputs/continuation_20261111/right_edge_reading_review/PROTOCOL.json'
SELECTOR = {'frame':'body','subset':'all','parityBase':'all_printed_rows','reset':'global',
            'phase':'all','projection':'last_words','textDirection':'normal'}
MEMBERS = [
    {'id':'right-edge-down','candidateIndex':4,'variantIndex':0,'direction':'down',
     'sha256':'8e240128fa4018c16a2716621ca8ccc09524110b87f6c3e9034e8a65376bb995',
     'utf8Bytes':972,'codepoints':972,'selectedRows':142,'aliasCount':6},
    {'id':'right-edge-up','candidateIndex':830,'variantIndex':0,'direction':'up',
     'sha256':'d6ad5dbbb8bbed97ed7711ec609f7c905c2c62b6ba5aa8756baa863c6d3a368c',
     'utf8Bytes':972,'codepoints':972,'selectedRows':142,'aliasCount':6},
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(root, relative):
    p = (root / relative).resolve(strict=True)
    require(p.is_relative_to(root) and p.relative_to(root).as_posix() == relative,
            'Unsafe or aliased registered path')
    return p


def member_record(candidates, member):
    candidate = candidates[member['candidateIndex']]
    aliases = candidate['variants']
    variant = aliases[member['variantIndex']]
    require(len(aliases) == member['aliasCount']
            and all(variant[key] == value for key, value in SELECTOR.items())
            and variant['direction'] == member['direction'], 'Saved selector changed')
    rows = variant['selectedRows']
    require(len(rows) == len(set(rows)) == member['selectedRows'], 'Saved rows changed')
    text = candidate['text']
    raw = text.encode('utf-8')
    require(candidate['sha256'] == sha(raw) == member['sha256']
            and len(raw) == member['utf8Bytes'] and len(text) == member['codepoints'],
            'Stored text bytes changed')
    return {'id':member['id'],'text':text}, rows


def make_packet(candidates, members):
    selected = [member_record(candidates, member) for member in members]
    require(len(selected) == 2 and selected[0][1] == selected[1][1][::-1],
            'Two saved row orders do not match')
    return {'records':[record for record, _ in selected]}


def self_test():
    texts = ('Ño x', 'x Ño')
    candidates, members = [], []
    for index, (text, direction) in enumerate(zip(texts, ('down','up'))):
        raw = text.encode('utf-8')
        digest = sha(raw)
        candidates.append({'sha256':digest,'text':text,'variants':[
            {**SELECTOR,'direction':direction,'selectedRows':['r1','r2'][::1 if index == 0 else -1]}]})
        members.append({'id':direction,'candidateIndex':index,'variantIndex':0,'direction':direction,
                        'sha256':digest,'utf8Bytes':len(raw),'codepoints':len(text),
                        'selectedRows':2,'aliasCount':1})
    packet = make_packet(candidates, members)
    require(tuple(r['text'] for r in packet['records']) == texts, 'Synthetic copy changed bytes')
    for key, value in [('sha256','0'*64), ('utf8Bytes',4), ('direction','up'), ('selectedRows',3)]:
        try:
            make_packet(candidates, [{**members[0],key:value}, members[1]])
        except ValueError:
            continue
        raise ValueError('Invalid synthetic membership accepted')
    print('PASS two exact synthetic copies and four rejection controls')


def read_registered(research, protocol, commit, receipt_path):
    require(re.fullmatch('[0-9a-f]{40}',commit) is not None, 'Invalid registration commit')
    require(research.name == 'research' and research.parent.name == 'public', 'Wrong research root')
    checkout = research.parent.parent
    require(protocol == canonical(research, PROTOCOL), 'Wrong protocol path')

    def git(*args):
        return subprocess.run(['git','-C',str(checkout),*args],check=True,
                              stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).stdout

    require(Path(os.fsdecode(git('rev-parse','--show-toplevel')).strip()) == checkout
            and git('cat-file','-t',commit) == b'commit\n', 'Expected actual registered commit')

    def verified(relative, cap):
        path = canonical(research, relative)
        blob = f'{commit}:public/research/{relative}'
        require(path.is_file() and path.stat().st_size <= cap
                and int(git('cat-file','-s',blob)) <= cap, 'Unexpected blob size')
        data = path.read_bytes()
        require(len(data) <= cap and data == git('show',blob), 'Current file differs from registration')
        return data

    raw = verified(PROTOCOL, 1_000_000)
    digest = sha(raw)
    protocol_doc = json.loads(raw)
    require(protocol_doc['testId'] == TEST_ID and protocol_doc['selector'] == SELECTOR
            and protocol_doc['members'] == MEMBERS, 'Protocol scope changed')
    require(protocol_doc['sourceHashes'] == {SOURCE:SOURCE_SHA}
            and protocol_doc['scriptHashes'] == {SCRIPT:sha(Path(__file__).read_bytes())},
            'Wrong source or executing code pin')
    require(sha(verified(SCRIPT, 1_000_000)) == protocol_doc['scriptHashes'][SCRIPT],
            'Wrong registered script')
    require(receipt_path.is_file() and receipt_path.stat().st_size <= 1_000_000, 'Invalid registration receipt')
    receipt_raw = receipt_path.read_bytes()
    receipt = json.loads(receipt_raw)
    require(receipt['registrationCommit'] == commit and receipt['protocolSha256'] == digest
            and receipt['remoteHeadMatched'] is True
            and receipt['targetReadingsOpenedAtVerification'] is False
            and type(receipt['pinnedBlobsVerified']) is int and receipt['pinnedBlobsVerified'] >= 3,
            'Expected verified public registration receipt')
    stamp = receipt['verifiedAtUTC']
    require(isinstance(stamp,str) and stamp.endswith('Z')
            and datetime.fromisoformat(stamp[:-1]+'+00:00') <= datetime.now(timezone.utc),
            'Invalid registration timestamp')
    source_raw = verified(SOURCE, 20_000_000)
    require(sha(source_raw) == SOURCE_SHA, 'Stored source digest changed')
    return json.loads(source_raw), digest, sha(receipt_raw)


def save(path, data):
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:
        f.write(raw)
    return sha(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test',action='store_true')
    group.add_argument('--definition',action='store_true')
    group.add_argument('--pack',action='store_true')
    for name in ('research','protocol','registration-receipt','out'):
        parser.add_argument(f'--{name}',type=Path)
    parser.add_argument('--registration-commit')
    args = parser.parse_args()
    try:
        if not args.pack:
            require(not any((args.research,args.protocol,args.registration_commit,
                             args.registration_receipt,args.out)), 'Control modes accept no source paths')
            if args.definition:
                print(json.dumps({'testId':TEST_ID,'selector':SELECTOR,'members':MEMBERS},indent=2))
            else:
                self_test()
            return 0
        require(all((args.research,args.protocol,args.registration_commit,args.registration_receipt,args.out)),
                'Incomplete registered pack inputs')
        research = args.research.resolve(strict=True)
        out = args.out
        parent = out.parent.resolve(strict=True)
        require(out.is_absolute() and out == parent / out.name and not out.exists() and not out.is_symlink()
                and not out.is_relative_to(research.parent.parent)
                and not any(part.lower() == 'public' for part in out.parts), 'Private fresh output required')
        data, protocol_sha, receipt_sha = read_registered(
            research,args.protocol.resolve(strict=True),args.registration_commit,args.registration_receipt)
        packet = make_packet(data['candidates'], MEMBERS)
        out.mkdir(mode=0o700)
        digest = save(out/'READINGS.private.json',packet)
        save(out/'MANIFEST.json',{'version':1,'testId':TEST_ID,'registrationCommit':args.registration_commit,
             'protocolSha256':protocol_sha,'registrationReceiptSha256':receipt_sha,'sourceSha256':SOURCE_SHA,
             'packetSha256':digest,'members':MEMBERS,'readings':2,'utf8Bytes':1944,'codepoints':1944,
             'newTransforms':0,'keyChecks':0})
        print('PASS two exact existing readings written privately')
        return 0
    except (OSError,ValueError,TypeError,KeyError,IndexError,AttributeError,subprocess.SubprocessError):
        print('Incomplete right-edge packet',file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
