#!/usr/bin/env python3
"""Source-only joint-color feasibility audit. Never generates text or checks keys."""
from __future__ import annotations
import argparse, hashlib, itertools, json, math, os, re, sys, tempfile, types
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode = True

PAIRS = ((76, 77), (77, 76), (78, 79), (79, 78))
SELECTORS = ('same-color', 'opposite-color', 'source-only', 'target-only')
INPUTS = (
    'sources/printed-lines.json', 'sources/word-geometry-20261110.json',
    'analysis_outputs/3d_article_map/article_3d_map_data.json',
    'analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json',
    'analysis_outputs/continuation_20261110/batch20/G02/RESULT.json',
    'analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json',
)
SCRIPTS = ('scripts/g02_joint_source_audit.py', 'scripts/verify_g02_joint_source_audit.py',
           'scripts/batch20_geometry.py')
DEFINITION = {
    'id': 'g02-joint-color-source-audit',
    'pairs': [list(pair) for pair in PAIRS], 'selectors': list(SELECTORS),
    'sourcePopulation': 'All original G02 target lexical word objects, preserving row/token order and IDs.',
    'geometry': 'Owning load_geometry and point_rotate helpers; no OCR, image operation, fitting or repair.',
    'guard': 'max(12, frozen centerUncertaintyPx)',
    'numericDomain': 'Freeze owning finite float centers/guards/mask coordinates as exact binary rationals. Evaluate the closed square without clipping, rounding or added tolerance.',
    'sourcePredicate': 'a <= 2544-x < c and b <= y < d in original source rectangles.',
    'targetPredicate': 'a <= x < c and b <= y < d in original target rectangles.',
    'coupling': 'Source and target colors are evaluated at the same displaced point.',
    'partition': 'All rectangle edge coordinates, reflected source x edges, square endpoints, and one midpoint of every open interval; all Cartesian endpoint/interior cells.',
    'overlap': 'Any cell with both colors on either side makes the whole word unresolved. No color or zero state is guessed.',
    'compatibility': 'Compare nominal exact-rational colors with original float predicates; compare every original guard-unambiguous class with the full new class set. Any disagreement leaves the word unresolved.',
    'membership': 'must if every classifiable cell selects the word; optional if some do; out if none do; unresolved if any overlap or compatibility disagreement occurs.',
    'pathCounts': '2^optional per selector is only an independent-word assignment upper bound; null for any unresolved word. No strings or paths are generated.',
    'maximumCanonicalRows': 142, 'canonicalTokens': 1258, 'canonicalLexicalWords': 1243,
    'targetWordPositionsByPair': [263, 274, 226, 199],
    'maximumTotalPartitionPoints': 200000, 'newCipherOutputs': 0,
    'keyChecks': 0, 'derivations': 0, 'historyQueries': 0, 'walletActions': 0,
    'negativeResultClaimed': False,
}

def require(ok, message):
    if not ok: raise ValueError(message)

def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())

def rational(value):
    require(not isinstance(value, bool) and isinstance(value, (int, float, Fraction)), 'Non-numeric coordinate')
    require(not isinstance(value, float) or math.isfinite(value), 'Non-finite coordinate')
    return Fraction(value)

def rectangles(masks):
    require(set(masks) == {'orange', 'black'}, 'Unexpected mask classes')
    result = {}
    for color, boxes in masks.items():
        result[color] = []
        for box in boxes:
            require(len(box) == 4, 'Invalid rectangle')
            a, b, c, d = map(rational, box)
            require(a < c and b < d, 'Empty rectangle')
            result[color].append((a, b, c, d))
    return result

def category(a, b):
    if a and a == b: return 'same-color'
    if a and b: return 'opposite-color'
    if a: return 'source-only'
    if b: return 'target-only'
    return 'neither'

def colors_at(x, y, masks):
    return [i for color, i in [('orange', 1), ('black', 2)]
            if any(a <= x < c and b <= y < d for a, b, c, d in masks[color])]

def point_colors(x, y, source, target, width):
    a = colors_at(width-x, y, source); b = colors_at(x, y, target)
    if len(a) > 1 or len(b) > 1: return None
    return (a[0] if a else 0, b[0] if b else 0)

def partition_axis(values):
    ordered = sorted(values)
    return ordered + [(a+b)/2 for a, b in zip(ordered, ordered[1:])]

def classify_joint(center, guard, source_masks, target_masks, width=2544):
    x, y = map(rational, center); guard = rational(guard); width = rational(width)
    require(guard >= 0 and width > 0, 'Invalid domain')
    source, target = rectangles(source_masks), rectangles(target_masks)
    xs, ys = {x-guard, x+guard}, {y-guard, y+guard}
    for label, masks in [('source', source), ('target', target)]:
        for boxes in masks.values():
            for a, b, c, d in boxes:
                xx = (width-a, width-c) if label == 'source' else (a, c)
                xs.update(v for v in xx if x-guard <= v <= x+guard)
                ys.update(v for v in (b, d) if y-guard <= v <= y+guard)
    states = set(); overlap = False; count = 0
    for xx, yy in itertools.product(partition_axis(xs), partition_axis(ys)):
        count += 1
        found = point_colors(xx, yy, source, target, width)
        if found is None: overlap = True
        else: states.add(found)
    nominal = point_colors(x, y, source, target, width)
    return {'classes': sorted({category(*pair) for pair in states}),
            'jointColorStates': [list(pair) for pair in sorted(states)], 'overlapObserved': overlap,
            'cellsEvaluated': count, 'nominalClass': None if nominal is None else category(*nominal),
            'nominalColors': None if nominal is None else list(nominal)}

def self_test():
    require(__debug__, 'Run controls with assertions enabled')
    empty = {'orange': [], 'black': []}
    def fill(state):
        return {'orange': [[-10,-10,20,20]] if state == 1 else [],
                'black': [[-10,-10,20,20]] if state == 2 else []}
    truth = (('neither','target-only','target-only'),
             ('source-only','same-color','opposite-color'),
             ('source-only','opposite-color','same-color'))
    for a, b in itertools.product(range(3), repeat=2):
        got = classify_joint([5,5],1,fill(a),fill(b),10)
        assert got['classes'] == [truth[a][b]] and not got['overlapObserved']
        assert got['jointColorStates'] == [[a,b]] and got['nominalColors'] == [a,b]
    source = {'orange': [[2,0,4,2]], 'black': []}
    assert classify_joint([6,1],0,source,empty,10)['classes'] == ['neither']
    assert classify_joint([8,1],0,source,empty,10)['classes'] == ['source-only']
    assert classify_joint([7,1],1,source,empty,10)['classes'] == ['neither','source-only']
    adjacent = {'orange': [[0,0,1,3],[1,0,3,3]], 'black': []}
    assert classify_joint([1,1],1,empty,adjacent,10)['classes'] == ['target-only']
    gap = {'orange': [[0,0,1,3],[2,0,4,3]], 'black': []}
    assert classify_joint([1,1],1,empty,gap,10)['classes'] == ['neither','target-only']
    overlap = {'orange': [[-10,-10,20,20]], 'black': [[-10,-10,20,20]]}
    assert classify_joint([5,5],1,overlap,empty,10)['overlapObserved']
    assert classify_joint([5,5],1,empty,overlap,10)['overlapObserved']
    assert classify_joint([5,5],0,empty,empty,10)['cellsEvaluated'] == 1
    joint = {'orange': [[0,0,10,1]], 'black': []}
    assert classify_joint([5,1],1,joint,joint,10)['classes'] == ['neither','same-color']
    edge_x = math.nextafter(1.0,math.inf)
    edge_masks = {'orange': [[8,0,9,2]], 'black': [[9,0,10,2]]}
    edge = classify_joint([edge_x,1],0,edge_masks,empty,10)
    assert edge['nominalColors'] == [1,0] and edge['nominalClass'] == 'source-only'
    assert point_colors(edge_x,1,edge_masks,empty,10) == (2,0)
    rejected = 0
    for bad in [float('nan'),float('inf'),True,'1']:
        try: classify_joint([bad,0],1,empty,empty)
        except ValueError: rejected += 1
    assert rejected == 4
    with tempfile.TemporaryDirectory(prefix='key404-g02-path-control-') as name:
        root = Path(name); site = root/'site'; outside = root/'outside'; site.mkdir(); outside.mkdir()
        corpus = site/'public/research'; corpus.mkdir(parents=True)
        (root/'alias').symlink_to(site, target_is_directory=True)
        (site/'escape').symlink_to(outside, target_is_directory=True)
        for path in [site/'new',root/'public/new',root/'alias/escape/new']:
            try: output_directory(path,corpus)
            except ValueError: pass
            else: raise AssertionError('Unsafe output path accepted')
        assert output_directory(outside/'new',corpus) == (outside/'new').resolve()
    return {'passed':True,'truthTableCases':9,'endpointUnionOverlapEmptyAndCouplingControls':9,
            'sameClassDifferentNominalColorsControl':True,
            'unsafeOutputPathControlsRejected':3,'safePrivatePathControlAccepted':True,
            'invalidCoordinatesRejected':rejected,'targetInputsRead':False,
            'newCipherOutputs':0,'keyChecks':0,'networkRequests':0}

def output_directory(value, corpus):
    raw = value.expanduser()
    if not raw.is_absolute(): raw = Path.cwd()/raw
    normalized = Path(os.path.abspath(raw)); resolved = raw.resolve()
    site = corpus.parent.parent.resolve()
    candidates = [raw,normalized,resolved,*[parent.resolve() for parent in raw.parents]]
    require(all(not p.is_relative_to(site) and 'public' not in [x.lower() for x in p.parts] for p in candidates),
            'Output must be outside Site and public routes')
    require(not raw.exists() and not raw.is_symlink(), 'Output must be fresh')
    require(resolved.parent.is_dir(), 'Private parent must already exist')
    resolved.mkdir(mode=0o700)
    return resolved

def save(path, value):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as h:
        json.dump(value,h,indent=2); h.write('\n')

def audit(corpus, protocol_path, registration_commit, out):
    started = utc(); controls = self_test(); protocol = read(protocol_path)
    require(protocol['definition'] == DEFINITION, 'Protocol definition changed')
    require(re.fullmatch('[a-f0-9]{40}',registration_commit) is not None, 'Invalid registration identity')
    require(set(protocol['sourceHashes']) == set(INPUTS) and set(protocol['scriptHashes']) == set(SCRIPTS), 'Wrong pins')
    buffers = {}
    for rel, pin in {**protocol['sourceHashes'],**protocol['scriptHashes']}.items():
        buffers[rel] = (corpus/rel).read_bytes()
        require(hashlib.sha256(buffers[rel]).hexdigest() == pin, 'Source/code identity changed: '+rel)
    require(sha(Path(__file__)) == protocol['scriptHashes'][SCRIPTS[0]], 'Wrong executing code')
    registration = read(protocol_path.parent/'REGISTRATION.json')
    require(registration['registrationCommit'] == registration_commit and registration['protocolSha256'] == sha(protocol_path)
            and registration['remoteHeadMatches'] is True, 'Missing verified public registration')
    helper = SCRIPTS[2]
    g = types.ModuleType('pinned_g02_source_helpers')
    g.__file__ = str(corpus/helper)
    exec(compile(buffers[helper],g.__file__,'exec'),g.__dict__)
    g.ROOT = corpus
    def pinned_json(path):
        rel = Path(path).relative_to(corpus).as_posix()
        require(rel in INPUTS, 'Unregistered source read')
        return json.loads(buffers[rel])
    g.read_json = pinned_json
    rows = pinned_json(corpus/INPUTS[0])['rows']; require(len(rows) == 142, 'Unexpected row population')
    geometry,_ = g.load_geometry(rows)
    require(all(row['geometryStatus'] == 'complete' for row in geometry), 'Incomplete frozen lexical geometry')
    require(sum(len(row['text'].split()) for row in rows) == 1258, 'Unexpected canonical token population')
    require(sum(len(row['words']) for row in geometry) == 1243, 'Unexpected canonical lexical population')
    masks = g.get_masks(pinned_json(corpus/INPUTS[2]),pinned_json(corpus/INPUTS[3]))
    output = output_directory(out,corpus); records=[]; scopes=[]; total_points=0
    for source,target in PAIRS:
        pair_records=[]
        for row in geometry:
            if row['page'] != target: continue
            for ordinal,word in enumerate(row['words'],1):
                center = g.point_rotate(*g.center(word['box']),-row['geometryRotationCCW'])
                guard = max(12,float(word.get('centerUncertaintyPx',12)))
                found = classify_joint(center,guard,masks[source],masks[target])
                total_points += found['cellsEvaluated']
                require(total_points <= DEFINITION['maximumTotalPartitionPoints'], 'Partition point cap exceeded')
                _,au = g.color_at((2544-center[0],center[1]),masks[source],guard)
                _,bu = g.color_at(center,masks[target],guard)
                old_colors = point_colors(*center,masks[source],masks[target],2544)
                old_class = None if old_colors is None else category(*old_colors)
                nominal_mismatch = found['nominalColors'] != (None if old_colors is None else list(old_colors))
                stable_mismatch = not (au or bu) and (found['classes'] != [old_class] or found['overlapObserved'])
                unresolved = found['overlapObserved'] or nominal_mismatch or stable_mismatch
                membership = {selector: 'unresolved' if unresolved else
                              'must' if found['classes'] == [selector] else
                              'optional' if selector in found['classes'] else 'out' for selector in SELECTORS}
                rec={'source':source,'target':target,'rowId':row['id'],'wordId':word['id'],
                     'wordOrdinalInRow':ordinal,'centerUprightFloat':list(center),'guardPxFloat':guard,
                     **found,'oldFloatClass':old_class,'oldFloatColors':None if old_colors is None else list(old_colors),
                     'oldGuardUnknown':au or bu,
                     'nominalFloatCompatibilityDisagreement':nominal_mismatch,
                     'oldStableClassDisagreement':stable_mismatch,'selectorMembership':membership}
                records.append(rec);pair_records.append(rec)
        counts={}
        for selector in SELECTORS:
            states=[r['selectorMembership'][selector] for r in pair_records]
            c={key:states.count(key) for key in ['must','optional','out','unresolved']}
            c['independentAssignmentUpperBound'] = None if c['unresolved'] else str(2**c['optional'])
            counts[selector]=c
        scopes.append({'source':source,'target':target,'wordPositions':len(pair_records),
                       'legacyFlaggedWordOccurrences':sum(r['oldGuardUnknown'] for r in pair_records),
                       'overlapWords':sum(r['overlapObserved'] for r in pair_records),
                       'nominalCompatibilityDisagreements':sum(r['nominalFloatCompatibilityDisagreement'] for r in pair_records),
                       'oldStableClassDisagreements':sum(r['oldStableClassDisagreement'] for r in pair_records),
                       'selectors':counts})
    require(len({r['wordId'] for r in records}) == len(records), 'Duplicate target word IDs')
    require([s['wordPositions'] for s in scopes] == DEFINITION['targetWordPositionsByPair'], 'Target word population changed')
    require([s['legacyFlaggedWordOccurrences'] for s in scopes] == [20,25,23,29], 'Owning saved uncertainty counts changed')
    global_counts={}
    for selector in SELECTORS:
        c={key:sum(s['selectors'][selector][key] for s in scopes) for key in ['must','optional','out','unresolved']}
        c['independentAssignmentUpperBound']=None if c['unresolved'] else str(2**c['optional'])
        global_counts[selector]=c
    inventory={'version':1,'auditId':DEFINITION['id'],'sourceHashes':protocol['sourceHashes'],
               'definition':DEFINITION,'wordRecords':records}
    save(output/'MEMBERSHIP.json',inventory)
    result={'version':1,'testId':DEFINITION['id'],'caseStatus':'unsolved','startedAtUTC':started,
            'completedAtUTC':utc(),'registrationCommit':registration_commit,'protocolSha256':sha(protocol_path),
            'sourceHashes':protocol['sourceHashes'],'scriptHashes':protocol['scriptHashes'],
            'sourceModelComplete':all(not c['unresolved'] for c in global_counts.values()),
            'negativeResultClaimed':False,'newCipherOutputsGenerated':False,
            'counts':{'canonicalRows':142,'canonicalTokens':1258,'canonicalLexicalWords':1243,'directedPairs':4,
                      'targetWordPositions':len(records),'legacyFlaggedWordOccurrences':97,
                      'partitionPointsEvaluated':total_points},'pairs':scopes,'globalSelectors':global_counts,
            'inventory':{'file':'MEMBERSHIP.json','sha256':sha(output/'MEMBERSHIP.json')},
            'controls':controls,'activity':{'newImages':0,'newOCR':0,'newGeometryFit':0,
                'newCipherOutputs':0,'keyChecks':0,'derivations':0,'historyQueries':0,'walletActions':0},
            'limits':['The exact joint enclosure is new arithmetic, not byte-identical old within() execution.',
                'Centers, rectangles and guards remain investigator-defined, uncalibrated assumptions.',
                'Independent per-word assignment counts overapproximate physical correlations; they are not counts of independent hypotheses or measured likelihoods.',
                'Only metadata membership/feasibility was audited. No candidate text, plaintext paths, crypto or puzzle exclusion was generated.']}
    save(output/'RESULT.json',result)
    return {'sourceModelComplete':result['sourceModelComplete'],'counts':result['counts'],
            'pairs':scopes,'globalSelectors':global_counts,'newCipherOutputs':0,'keyChecks':0}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',action='store_true');p.add_argument('--audit',action='store_true')
    p.add_argument('--corpus',type=Path);p.add_argument('--protocol',type=Path)
    p.add_argument('--registration-commit');p.add_argument('--out',type=Path)
    args=p.parse_args()
    if args.self_test:
        require(not args.audit and not any([args.corpus,args.protocol,args.registration_commit,args.out]),'Self-test accepts no target inputs')
        print(json.dumps(self_test()))
    else:
        require(args.audit and all([args.corpus,args.protocol,args.registration_commit,args.out]),'Explicit audit arguments required')
        print(json.dumps(audit(args.corpus.resolve(),args.protocol.resolve(),args.registration_commit,args.out)))
