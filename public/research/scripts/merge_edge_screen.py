#!/usr/bin/env python3
"""Validate two independent perimeter reviews and merge their agreed markings."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

PAGES = (76, 77, 78, 79)
LEAVES = ((76, 77), (78, 79))
X = (0, 306, 1734, 2040)
Y = (0, 421, 2384, 2805)
MAX_JSON = 1_000_000
SHA256 = re.compile(r'[a-f0-9]{64}')
COMMIT = re.compile(r'[a-f0-9]{40}')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require_fields(value, expected, message):
    require(isinstance(value, dict) and set(value) == set(expected), message)


def strict_json(data):
    def unique_fields(pairs):
        fields = dict(pairs)
        require(len(fields) == len(pairs), 'Repeated JSON field')
        return fields

    def invalid_number(_):
        raise ValueError('Nonfinite JSON number')

    return json.loads(data.decode('utf-8'), object_pairs_hook=unique_fields, parse_constant=invalid_number)


def read_bytes(path, limit=MAX_JSON):
    require(path.is_file() and path.stat().st_size <= limit, 'Input file missing or oversized')
    data = path.read_bytes()
    require(len(data) <= limit, 'Input size changed')
    return data


def check_interval(value, minimum, maximum):
    require(isinstance(value, list) and len(value) == 2
            and all(type(x) is int for x in value)
            and minimum <= value[0] <= value[1] <= maximum, 'Invalid pixel interval')


def overlap_union(first, second):
    if max(first[0], second[0]) > min(first[1], second[1]):
        return None
    return [min(first[0], second[0]), max(first[1], second[1])]

TEST_ID = 'g02-perimeter-visibility'
PROTOCOL = 'analysis_outputs/continuation_20261110/g02_edge_screen/PROTOCOL.json'
SCRIPT = 'scripts/merge_edge_screen.py'
PDF = 'keyser bitcoin .pdf'
PDF_SHA = 'dcd13efd0e46c49927dc8ec2e38a96fffc20d92fde7434151250fd6b9c62e6f4'
SIDES = ('top', 'right', 'bottom', 'left')
TRANSECTS = {'top': (510, 1020, 1530), 'bottom': (510, 1020, 1530),
             'left': (701, 1402, 2103), 'right': (701, 1402, 2103)}
AXIS_BOUNDS = {'top': (0, Y[1] - 1), 'bottom': (Y[2], Y[3] - 1),
               'left': (0, X[1] - 1), 'right': (X[2], X[3] - 1)}
WINDOW_LAYOUT = (('NW', 0, 0), ('N', 1, 0), ('NE', 2, 0), ('E', 2, 1),
                 ('SE', 2, 2), ('S', 1, 2), ('SW', 0, 2), ('W', 0, 1))
WINDOWS = {f'p{page}-{code}': (page, [X[x], Y[y], X[x+1], Y[y+1]])
           for page in PAGES for code, x, y in WINDOW_LAYOUT}
CORNERS = {key: value for key, value in WINDOWS.items() if len(key.split('-')[1]) == 2}
EDGES = {f'p{page}-{side}': (page, side) for page in PAGES for side in SIDES}
CROSSINGS = {f'{edge}-{n}': (page, side, n)
             for edge, (page, side) in EDGES.items() for n in TRANSECTS[side]}
NONTRIM = {'binding', 'adjacent-leaf-shadow', 'image-crop', 'obscured', 'ambiguous'}
CURVATURE = {'straight-looking', 'curved', 'insufficient'}


def timestamp(value):
    require(isinstance(value, str)
            and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z', value),
            'Expected UTC timestamp')
    return datetime.fromisoformat(value[:-1] + '+00:00')


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def check_digest(value):
    require(isinstance(value, str) and SHA256.fullmatch(value), 'Invalid SHA-256 identity')


def index_records(records, expected, fields):
    require(isinstance(records, list) and len(records) == len(expected), 'Incomplete record population')
    indexed = {}
    for record in records:
        require_fields(record, fields, 'Unexpected record fields')
        name = record['id']
        require(isinstance(name, str) and name in expected and name not in indexed,
                'Unknown or repeated record ID')
        indexed[name] = record
    return indexed


def fore_side(page):
    return 'right' if page in (76, 78) else 'left'


def trim_label(page, side):
    if side == 'top':
        return 'head'
    if side == 'bottom':
        return 'foot'
    return 'fore-edge' if side == fore_side(page) else None


def validate_review(doc, reviewer, commit, packet_sha, prepared_at):
    require_fields(doc, ('version', 'reviewerId', 'registrationCommit', 'packetManifestSha256',
                         'startedAtUTC', 'completedAtUTC', 'peerMarksSeen', 'priorShapeOutcomesSeen',
                         'windows', 'crossings', 'edges', 'corners'), 'Unexpected review fields')
    require(type(doc['version']) is int and doc['version'] == 1 and doc['reviewerId'] == reviewer
            and doc['registrationCommit'] == commit and doc['packetManifestSha256'] == packet_sha,
            'Reader or source identity mismatch')
    require(doc['peerMarksSeen'] is False and doc['priorShapeOutcomesSeen'] is False,
            'Review exposure conflicts with protocol')
    require(prepared_at < timestamp(doc['startedAtUTC']) <= timestamp(doc['completedAtUTC']),
            'Review timing conflicts with packet identity')
    windows = index_records(doc['windows'], WINDOWS, ('id', 'note'))
    crossings = index_records(doc['crossings'], CROSSINGS, ('id', 'label', 'interval', 'note'))
    edges = index_records(doc['edges'], EDGES, ('id', 'runs', 'curvature', 'note'))
    corners = index_records(doc['corners'], CORNERS, ('id', 'label', 'box', 'note'))
    for record in (*windows.values(), *crossings.values(), *edges.values(), *corners.values()):
        require(isinstance(record['note'], str), 'Expected reader note')
    for key, (page, side, _) in CROSSINGS.items():
        rec = crossings[key]
        expected = trim_label(page, side)
        if expected is not None and rec['label'] == expected:
            check_interval(rec['interval'], *AXIS_BOUNDS[side])
        else:
            require(rec['label'] in NONTRIM and rec['interval'] is None,
                    'Unexpected physical crossing label or interval')
    for key, (page, side) in EDGES.items():
        rec = edges[key]
        runs = rec['runs']
        require(isinstance(runs, list) and rec['curvature'] in CURVATURE, 'Malformed edge run')
        require(trim_label(page, side) is not None or runs == [], 'Binding side has a trim run')
        axis_max = X[-1] - 1 if side in ('top', 'bottom') else Y[-1] - 1
        previous_end = -1
        for run in runs:
            check_interval(run, 0, axis_max)
            require(previous_end < run[0], 'Repeated, overlapping or unsorted edge runs')
            previous_end = run[1]
    for key, (page, (x0, y0, x1, y1)) in CORNERS.items():
        rec = corners[key]
        if rec['label'] == 'visible-trim-corner':
            box = rec['box']
            require(key.endswith('E' if fore_side(page) == 'right' else 'W')
                    and isinstance(box, list) and len(box) == 4, 'Unexpected visible trim corner')
            check_interval([box[0], box[2]], x0, x1 - 1)
            check_interval([box[1], box[3]], y0, y1 - 1)
        else:
            require(rec['label'] in NONTRIM and rec['box'] is None,
                    'Unexpected corner label or box')
    return {'windows': windows, 'crossings': crossings, 'edges': edges, 'corners': corners}


def merged_mark(first, second, label, position_key):
    matching = first['label'] == second['label'] == label
    agreed = None
    if matching and position_key == 'interval':
        agreed = overlap_union(first[position_key], second[position_key])
    elif matching:
        a, b = first[position_key], second[position_key]
        x = overlap_union([a[0], a[2]], [b[0], b[2]])
        y = overlap_union([a[1], a[3]], [b[1], b[3]])
        if x is not None and y is not None:
            agreed = [x[0], y[0], x[1], y[1]]
    if agreed is not None:
        status = 'accepted'
    elif matching or first['label'] != second['label'] or first['label'] == 'ambiguous':
        status = 'unresolved'
    else:
        status = 'no-trim-agreement'
    return {'id': first['id'], 'status': status, position_key: agreed,
            'readers': [{k: rec[k] for k in ('label', position_key)} for rec in (first, second)]}


def merge_reviews(a, b):
    marks = [merged_mark(a['crossings'][key], b['crossings'][key], trim_label(page, side), 'interval')
             for key, (page, side, _) in CROSSINGS.items()]
    corner_marks = [merged_mark(a['corners'][key], b['corners'][key], 'visible-trim-corner', 'box')
                    for key in CORNERS]
    counts = {edge: {status: sum(
        m['status'] == status and m['id'].rsplit('-', 1)[0] == edge for m in marks)
        for status in ('accepted', 'unresolved', 'no-trim-agreement')} for edge in EDGES}
    edge_records = [{'id': edge, 'trimLabel': trim_label(page, side),
                     'crossingCounts': counts[edge],
                     'readers': [{k: review['edges'][edge][k] for k in ('runs', 'curvature')}
                                 for review in (a, b)]}
                    for edge, (page, side) in EDGES.items()]
    faces = []
    for page in PAGES:
        face_edges = [edge for edge in edge_records if EDGES[edge['id']][0] == page]
        face_corners = [m for m in corner_marks if CORNERS[m['id']][0] == page]
        faces.append({'page': page, 'windowsReviewedPerReader': 8, 'edges': face_edges,
                      'acceptedCorners': sum(m['status'] == 'accepted' for m in face_corners),
                      'unresolvedCorners': sum(m['status'] == 'unresolved' for m in face_corners)})
    leaves = []
    for pair in LEAVES:
        horizontal = [label for side, label in (('top', 'head'), ('bottom', 'foot'))
                      if all(counts[f'p{page}-{side}']['accepted'] >= 2 for page in pair)]
        fore = [counts[f'p{page}-{fore_side(page)}']['accepted'] for page in pair]
        evidence = bool(horizontal) and all(n >= 2 for n in fore)
        leaves.append({'pages': list(pair), 'sharedHorizontalEdges': horizontal,
                       'foreEdgeAcceptedCrossings': fore, 'twoAxisEdgeEvidence': evidence,
                       'separateTransferStudyAdmitted': evidence})
    return {'windowIds': list(WINDOWS), 'crossings': marks, 'corners': corner_marks,
            'pages': faces, 'leaves': leaves}


def checked_path(root, relative):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(),
            'Expected a relative registered path')
    path = (root / relative).resolve(strict=True)
    require(path.is_relative_to(root) and path.relative_to(root).as_posix() == relative,
            'Registered path alias or escape')
    return path


def verify_registration(research, protocol, commit, receipt_path):
    require(isinstance(commit, str) and COMMIT.fullmatch(commit), 'Invalid Git commit')
    require(research.name == 'research' and research.parent.name == 'public', 'Wrong research root')
    checkout = research.parent.parent
    require(protocol == checked_path(research, PROTOCOL), 'Wrong protocol path')

    def git(*args):
        return subprocess.run(['git', '-C', str(checkout), *args], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, check=True).stdout

    require(Path(os.fsdecode(git('rev-parse', '--show-toplevel')).strip()) == checkout
            and git('cat-file', '-t', commit) == b'commit\n', 'Invalid registered Git object')

    def compare_blob(relative, limit):
        path = checked_path(research, relative)
        blob = f'{commit}:public/research/{relative}'
        require(int(git('cat-file', '-s', blob)) <= limit, 'Registered blob exceeds cap')
        current = read_bytes(path, limit)
        require(current == git('show', blob), 'Current file differs from registered blob')
        return current

    protocol_bytes = compare_blob(PROTOCOL, MAX_JSON)
    protocol_sha = sha(protocol_bytes)
    spec = strict_json(protocol_bytes)
    require(spec['testId'] == TEST_ID, 'Wrong protocol test')
    sources, scripts = spec['sourceHashes'], spec['scriptHashes']
    require(isinstance(sources, dict) and isinstance(scripts, dict) and not set(sources) & set(scripts)
            and sources.get(PDF) == PDF_SHA and scripts.get(SCRIPT) == sha(read_bytes(Path(__file__))),
            'Registered source or executing code identity changed')
    pins = {**sources, **scripts}
    require(len(pins) <= 24, 'Unexpected registered file count')
    receipt_bytes = read_bytes(receipt_path)
    receipt = strict_json(receipt_bytes)
    require(receipt['registrationCommit'] == commit and receipt['protocolSha256'] == protocol_sha
            and receipt['remoteHeadMatched'] is True
            and receipt['targetPixelsOpenedAtVerification'] is False, 'No verified pre-pixel registration')
    verified = receipt['pinnedBlobsVerified']
    require(type(verified) is int and verified >= len(pins) + 1, 'Incomplete registration receipt')
    verified_at = timestamp(receipt['verifiedAtUTC'])
    for relative, digest in pins.items():
        check_digest(digest)
        require(sha(compare_blob(relative, 32_000_000)) == digest, 'Registered file hash changed')
    return protocol_sha, verified_at, sha(receipt_bytes)


def validate_packet(doc, commit, protocol_sha, verified_at, verify_asset):
    require(type(doc['version']) is int and doc['version'] == 1 and doc['testId'] == TEST_ID
            and doc['registrationCommit'] == commit and doc['protocolSha256'] == protocol_sha
            and doc['sourcePdfSha256'] == PDF_SHA, 'Packet source or registration changed')
    prepared = timestamp(doc['preparedAtUTC'])
    require(verified_at < prepared, 'Packet creation predates registration')
    windows = index_records(doc['windows'], WINDOWS, ('id', 'page', 'box', 'path', 'sha256'))
    guides = index_records(doc['guides'], EDGES, ('id', 'page', 'side', 'path', 'sha256'))
    pages = {f'p{page}': page for page in PAGES}
    overview = index_records(doc['overview'], pages, ('id', 'page', 'path', 'sha256'))
    for key, (page, box) in WINDOWS.items():
        record = windows[key]
        require(type(record['page']) is int and record['page'] == page
                and isinstance(record['box'], list) and len(record['box']) == 4
                and all(type(value) is int for value in record['box'])
                and record['box'] == box, 'Wrong perimeter window geometry')
    for key, (page, side) in EDGES.items():
        record = guides[key]
        require(type(record['page']) is int and record['page'] == page and record['side'] == side,
                'Wrong edge guide identity')
    for key, page in pages.items():
        require(type(overview[key]['page']) is int and overview[key]['page'] == page,
                'Wrong overview identity')
    for prefix, records in (('window', windows), ('guide', guides), ('overview', overview)):
        for key, record in records.items():
            check_digest(record['sha256'])
            require(record['path'] == f'{prefix}-{key}.png', 'Wrong packet asset path')
            verify_asset(record['path'], record['sha256'])
    return prepared


def merge_registered(args):
    research = args.research.resolve(strict=True)
    checkout = research.parent.parent
    out = args.out
    parent = out.parent.resolve(strict=True)
    require(out.is_absolute() and out == parent / out.name and not out.exists() and not out.is_symlink()
            and not out.is_relative_to(checkout)
            and not any(part.lower() == 'public' for part in out.parts), 'Output must be fresh and private')
    protocol_sha, verified_at, receipt_sha = verify_registration(
        research, args.protocol.resolve(strict=True), args.registration_commit, args.registration_receipt)
    started = utc()
    manifest = args.packet_manifest.resolve(strict=True)
    packet_dir = args.packet_directory.resolve(strict=True) if args.packet_directory else manifest.parent
    manifest_bytes = read_bytes(manifest)
    manifest_sha = sha(manifest_bytes)

    def verify_asset(path, digest):
        require(sha(read_bytes(checked_path(packet_dir, path), 16_000_000)) == digest,
                'Packet asset hash changed')

    prepared = validate_packet(strict_json(manifest_bytes), args.registration_commit,
                               protocol_sha, verified_at, verify_asset)
    reviews, review_hashes = [], {}
    for reviewer, path in (('A', args.reader_a), ('B', args.reader_b)):
        data = read_bytes(path)
        review_hashes[reviewer] = sha(data)
        reviews.append(validate_review(strict_json(data), reviewer, args.registration_commit,
                                       manifest_sha, prepared))
    merged = merge_reviews(*reviews)
    common = {'version': 1, 'testId': TEST_ID, 'registrationCommit': args.registration_commit,
              'protocolSha256': protocol_sha, 'registrationReceiptSha256': receipt_sha,
              'sourcePdfSha256': PDF_SHA, 'packetManifestSha256': manifest_sha, 'readerHashes': review_hashes}
    detail = {**common, **merged}
    detail_bytes = (json.dumps(detail, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    result = {**common, 'startedAtUTC': started, 'completedAtUTC': utc(), 'scopeComplete': True,
              'counts': {'readers': 2, 'windowsPerReader': 32, 'crossingsPerReader': 48,
                         'edgesPerReader': 16, 'cornersPerReader': 16, 'packetAssetHashesVerified': 52,
                         'acceptedCrossings': sum(m['status'] == 'accepted' for m in merged['crossings']),
                         'unresolvedCrossings': sum(m['status'] == 'unresolved' for m in merged['crossings']),
                         'acceptedCorners': sum(m['status'] == 'accepted' for m in merged['corners'])},
              'pages': merged['pages'], 'leaves': merged['leaves'],
              'physicalRange': None, 'activity': {'pixelDecodes': 0, 'transformFits': 0,
                                                   'stencilReadings': 0, 'keyChecks': 0},
              'mergedArtifactSha256': sha(detail_bytes)}
    out.mkdir(mode=0o700)
    for filename, data in (('MERGED.json', detail_bytes),
                           ('RESULT.json', (json.dumps(result, indent=2) + '\n').encode('utf-8'))):
        with os.fdopen(os.open(out / filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as stream:
            stream.write(data)


def self_test():
    from copy import deepcopy

    commit = '1' * 40
    digest = '2' * 64
    protocol_sha = '3' * 64
    verified = timestamp('2026-01-01T00:00:00Z')
    prepared_str = '2026-01-01T00:00:01Z'

    def entry(prefix, key, page, **metadata):
        return {'id': key, 'page': page, 'path': f'{prefix}-{key}.png',
                'sha256': digest, **metadata}

    packet = {'version': 1, 'testId': TEST_ID, 'registrationCommit': commit,
              'protocolSha256': protocol_sha, 'preparedAtUTC': prepared_str,
              'sourcePdfSha256': PDF_SHA,
              'windows': [entry('window', key, page, box=box)
                          for key, (page, box) in WINDOWS.items()],
              'guides': [entry('guide', key, page, side=side)
                         for key, (page, side) in EDGES.items()],
              'overview': [entry('overview', f'p{page}', page) for page in PAGES]}
    checks = []
    prepared = validate_packet(packet, commit, protocol_sha, verified,
                               lambda path, pin: checks.append((path, pin)))
    require(len(checks) == len(set(checks)) == 52 and prepared == timestamp(prepared_str),
            'Synthetic packet asset population')

    def make_review(reader, shift):
        doc = {'version': 1, 'reviewerId': reader, 'registrationCommit': commit,
               'packetManifestSha256': digest, 'startedAtUTC': '2026-01-01T00:00:02Z',
               'completedAtUTC': '2026-01-01T00:00:03Z',
               'peerMarksSeen': False, 'priorShapeOutcomesSeen': False,
               'windows': [{'id': key, 'note': ''} for key in WINDOWS],
               'crossings': [],
               'edges': [{'id': key, 'runs': [], 'curvature': 'insufficient', 'note': ''}
                         for key in EDGES],
               'corners': [{'id': key, 'label': 'obscured', 'box': None, 'note': ''} for key in CORNERS]}
        for key, (page, side, transect) in CROSSINGS.items():
            visible = ((side == fore_side(page) or side == ('bottom' if page == 79 else 'top'))
                       and transect in TRANSECTS[side][:2])
            start = AXIS_BOUNDS[side][0] + 10 + shift
            doc['crossings'].append({'id': key, 'label': trim_label(page, side) if visible else 'obscured',
                                     'interval': [start, start + 2] if visible else None, 'note': ''})
        doc['corners'][1].update(label='visible-trim-corner',
                                 box=[1800 + shift, 20, 1810 + shift, 30])
        return doc

    a, b = make_review('A', 0), make_review('B', 2)

    def reviewed(doc, who):
        return validate_review(doc, who, commit, digest, prepared)

    merged = merge_reviews(reviewed(a, 'A'), reviewed(b, 'B'))
    require(len(merged['crossings']) == 48 and len(merged['corners']) == 16,
            'Synthetic reader population mismatch')
    require(merged['crossings'][0]['interval'] == [10, 14], 'Touching intervals do not merge correctly')
    require(merged['corners'][1]['box'] == [1800, 20, 1812, 30], 'Synthetic corner union mismatch')
    require([leaf['twoAxisEdgeEvidence'] for leaf in merged['leaves']] == [True, False],
            'Different horizontal edges incorrectly satisfy shared leaf gate')
    disjoint = deepcopy(b)
    disjoint['crossings'][0]['interval'] = [40, 42]
    merged = merge_reviews(reviewed(a, 'A'), reviewed(disjoint, 'B'))
    require(merged['crossings'][0]['status'] == 'unresolved'
            and not merged['leaves'][0]['twoAxisEdgeEvidence'], 'Disjoint crossing must remain unresolved')

    def rejects(operation):
        try:
            operation()
        except (ValueError, TypeError):
            return
        raise ValueError('Synthetic invalid input accepted')

    for field, updates in (
            ('crossings', {'label': 'fore-edge'}),
            ('crossings', {'interval': [True, 5]}),
            ('crossings', {'interval': [0, 421]}),
            ('corners', {'label': 'visible-trim-corner', 'box': [10, 10, 20, 20]}),
            ('edges', {'runs': [[30, 100], [80, 120]]}),
            ('windows', {'id': 'p80-NW'})):
        invalid = deepcopy(a)
        invalid[field][0].update(updates)
        rejects(lambda: reviewed(invalid, 'A'))
    for update in ({'peerMarksSeen': True}, {'priorShapeOutcomesSeen': True},
                   {'packetManifestSha256': '5' * 64}, {'registrationCommit': '5' * 40},
                   {'startedAtUTC': prepared_str}, {'version': True}, {'windows': a['windows'][:-1]},
                   {'corners': [a['corners'][0], *a['corners'][:-1]]}):
        rejects(lambda: reviewed({**a, **update}, 'A'))
    invalid_packet = deepcopy(packet)
    invalid_packet['windows'][0]['box'][0] = -1
    rejects(lambda: validate_packet(invalid_packet, commit, protocol_sha, verified, lambda *_: None))
    rejects(lambda: validate_packet(packet, commit, protocol_sha, prepared, lambda *_: None))
    rejects(lambda: strict_json(b'{"x":1,"x":2}'))
    print('PASS synthetic edge-screen controls: 52 assets, 2 complete reviews, 17 rejection cases')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--self-test', action='store_true')
    action.add_argument('--merge', action='store_true')
    for flag in ('research', 'protocol', 'registration-receipt', 'packet-manifest', 'reader-a',
                 'reader-b', 'out', 'packet-directory'):
        parser.add_argument(f'--{flag}', type=Path)
    parser.add_argument('--registration-commit')
    args = parser.parse_args()
    options = (args.research, args.protocol, args.registration_commit, args.registration_receipt,
               args.packet_manifest, args.reader_a, args.reader_b, args.out)
    try:
        if args.self_test:
            require(not any(options) and args.packet_directory is None,
                    'Synthetic controls accept no target arguments')
            self_test()
        else:
            require(all(options), 'Merge requires all registered and private input paths')
            merge_registered(args)
            print('PASS complete private edge-screen merge')
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        print('Incomplete edge-screen merge', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
