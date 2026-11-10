#!/usr/bin/env python3
"""Fixed Issue27 body-model stride12 experiment; offline, stdlib only.

Import, --list and --self-test never open target source rows. --run requires
published registration bytes and a fresh private output folder. Raw tokens and
readings remain private. No seed/address derivation or network implementation.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent if (SCRIPT_DIR / 'batch20_common.py').is_file() else Path(__file__).resolve().parents[3] / 'site/public/research'
sys.path.insert(0, str(ROOT / 'scripts'))
BODY = 'analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json'
PRIMARY = 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json'
PRIMARY_SHA256 = 'f5f441345ebe411ee769cdcb624c0717a2b4f790b7eadc50d10dc12d37da07bb'
BODY_SHA256 = '783cc6676edf9b135d1eeff04d8bf8636088c1334f9e983f0d9f07dc579bff27'
POLICY_SHA256 = '5c6d4a7b406f99515b1bb16c7f7874df6444c64c3be2e6a32c0798ac08e0d1e5'
IMAGE_DIR = 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/'
INPUT_PINS = {
 BODY: BODY_SHA256, PRIMARY: PRIMARY_SHA256,
 IMAGE_DIR+'page_01.jpg':'d4cca9f4326ba21a959551e8537596846bccdea42efe37f463506cd2d423fb8c',
 IMAGE_DIR+'page_02.jpg':'e18e02e521444c9ea760c6e1d80a39bbee08d65a7839e970629ab81b4fd83610',
 IMAGE_DIR+'page_03.jpg':'b7f120860b1a76aa6ba97c836bb56388477ee8878665d75414098f9b8a38a1b5',
 IMAGE_DIR+'page_04.jpg':'60da7f7ed64764e8c9bb347bce163eb2f8dc4c4ad20abbd00182bced3ad3343a',
 'scripts/batch20_support/english.txt':'2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda',
 'scripts/batch20_support/controls.json':'d37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b',
 'analysis_outputs/continuation_20261110/issue27_stride12/POLICY_PROPOSAL.json':POLICY_SHA256}
INPUTS = tuple(INPUT_PINS)
SCRIPTS = ('scripts/issue27_stride12.py','scripts/batch20_common.py','scripts/verify_issue27_stride12.py','scripts/verify_issue27_saved.py')
FORMATS = ('wif','minikey','hex64','bip39')
PROJECTIONS = ('words','initials','finals')
DIRECTIONS = ('forward','reverse')
BATCH_ID = 'keiser-issue27-body-stride12-20261110'
WRAPPERS = '!"\'(),.:;?[]{}‘’“”'
UNCERTAIN = {'p4:col1_top:2':('l',8),'p4:col1_top:3':('e',7),'p4:col1_top:4':('s',4)}
FINGERPRINT_RULE = {'algorithm':'SHA-256','domainText':'KEY404/batch20/record-fingerprint/v1',
 'separatorHex':'00','rule':'SHA256(domain || 0x00 || ASCII(format) || 0x00 || canonical record bytes)'}


DEFINITION = {'id': 'issue27-body-stride12',
 'title': 'Issue27 repaired body model: every twelfth literal chunk',
 'family': 'fixed-stride-source-model',
 'branchId': 'text-lines',
 'inputPaths': ['analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json',
                'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json',
                'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_01.jpg',
                'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_02.jpg',
                'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_03.jpg',
                'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_04.jpg',
                'scripts/batch20_support/english.txt',
                'scripts/batch20_support/controls.json',
                'analysis_outputs/continuation_20261110/issue27_stride12/POLICY_PROPOSAL.json'],
 'implementationPaths': ['scripts/issue27_stride12.py',
                         'scripts/batch20_common.py',
                         'scripts/verify_issue27_stride12.py',
                         'scripts/verify_issue27_saved.py'],
 'policySha256': '5c6d4a7b406f99515b1bb16c7f7874df6444c64c3be2e6a32c0798ac08e0d1e5',
 'policy': {'modelId': 'issue27-physical-chunks-stride12-v1',
            'tokenization': {'rowTraversal': 'Existing conventional source order, page then frozen '
                                             'region then physical row; no row, region, page or '
                                             'paragraph reset.',
                             'splitRegex': '[ \\t\\r\\n\\f\\v]+',
                             'keepChunkPredicate': 'Contains at least one ASCII A-Z, a-z or 0-9, tested '
                                                   'before wrapper stripping.',
                             'outerWrapperCharacters': ['!',
                                                        '"',
                                                        "'",
                                                        '(',
                                                        ')',
                                                        ',',
                                                        '.',
                                                        ':',
                                                        ';',
                                                        '?',
                                                        '[',
                                                        ']',
                                                        '{',
                                                        '}',
                                                        '‘',
                                                        '’',
                                                        '“',
                                                        '”'],
                             'outerWrapperCodepoints': ['U+0021',
                                                        'U+0022',
                                                        'U+0027',
                                                        'U+0028',
                                                        'U+0029',
                                                        'U+002C',
                                                        'U+002E',
                                                        'U+003A',
                                                        'U+003B',
                                                        'U+003F',
                                                        'U+005B',
                                                        'U+005D',
                                                        'U+007B',
                                                        'U+007D',
                                                        'U+2018',
                                                        'U+2019',
                                                        'U+201C',
                                                        'U+201D'],
                             'stripRule': 'Repeatedly remove only members of outerWrapperCharacters '
                                          'from the beginning and end. Do not remove any interior '
                                          'character. Retain the remaining chunk exactly.',
                             'literalRetentions': ['Internal periods and apostrophes',
                                                   'All hyphens, including physical row-ending hyphens',
                                                   'All censor asterisks',
                                                   'All slash characters, including a row-ending slash',
                                                   'Currency symbols, including a leading dollar sign'],
                             'forbidden': ['Hard-wrap joining',
                                           'Unicode normalization',
                                           'Case conversion',
                                           'BIP39 word filtering',
                                           'Letter-only filtering',
                                           'Punctuation deletion beyond the registered outer-wrapper '
                                           'rule',
                                           'Reversing characters inside tokens',
                                           'Guessed letters or wildcard expansion']},
            'selection': {'directions': ['forward', 'reverse-token-order'],
                          'phasesZeroBased': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                          'stride': 12,
                          'rule': 'For the direction-specific token sequence T, select T[p], T[p+12], '
                                  'T[p+24], ... while in range. Reverse means reverse the entire token '
                                  'sequence before applying this rule. No other reset or reversal.'},
            'projections': {'words': 'Join selected cleaned chunks in order with exactly one U+0020 '
                                     'ASCII space.',
                            'initials': 'Concatenate the first remaining Unicode character of every '
                                        'selected cleaned chunk.',
                            'finals': 'Concatenate the last remaining Unicode character of every '
                                      'selected cleaned chunk.'},
            'projectionTerminology': 'Initials/finals are literal first/last core glyphs, not inferred '
                                     'linguistic word letters. Thus final hyphens, censor stars and '
                                     'slash characters remain possible. This is one declared model, not '
                                     'a test of all linguistic letter policies.',
            'sourceUncertainty': {'executionModel': 'Execute the single frozen repaired-OCR model, '
                                                    'retaining the unchanged prior strings in the three '
                                                    'uncertain leading-word spans. No branch over '
                                                    'alternative spellings.',
                                  'uncertainTokens': [{'sourcePage': 4,
                                                       'printedPage': 81,
                                                       'region': 'col1_top',
                                                       'line': 2,
                                                       'physicalChunk': 'First chunk containing ASCII '
                                                                        'alphanumeric characters in '
                                                                        'that row',
                                                       'uncertainty': 'Leading glyph/prefix not '
                                                                      'source-certified; word '
                                                                      'boundary/count and terminal '
                                                                      'glyph are source-certified by '
                                                                      'the independent third review.',
                                                       'unknownForProjections': ['words', 'initials'],
                                                       'knownForProjections': ['finals']},
                                                      {'sourcePage': 4,
                                                       'printedPage': 81,
                                                       'region': 'col1_top',
                                                       'line': 3,
                                                       'physicalChunk': 'First chunk containing ASCII '
                                                                        'alphanumeric characters in '
                                                                        'that row',
                                                       'uncertainty': 'Leading glyph/prefix not '
                                                                      'source-certified; word '
                                                                      'boundary/count and terminal '
                                                                      'glyph are source-certified by '
                                                                      'the independent third review.',
                                                       'unknownForProjections': ['words', 'initials'],
                                                       'knownForProjections': ['finals']},
                                                      {'sourcePage': 4,
                                                       'printedPage': 81,
                                                       'region': 'col1_top',
                                                       'line': 4,
                                                       'physicalChunk': 'First chunk containing ASCII '
                                                                        'alphanumeric characters in '
                                                                        'that row',
                                                       'uncertainty': 'Leading glyph/prefix not '
                                                                      'source-certified; word '
                                                                      'boundary/count and terminal '
                                                                      'glyph are source-certified by '
                                                                      'the independent third review.',
                                                       'unknownForProjections': ['words', 'initials'],
                                                       'knownForProjections': ['finals']}],
                                  'perReadingMetadata': ['executionModelComplete',
                                                         'selectedUncertainTokenCount',
                                                         'physicalSourceComplete',
                                                         'sourceUncertaintyAffected'],
                                  'executionModelComplete': 'True after all finite declared readings '
                                                            'are evaluated against the pinned model, '
                                                            'regardless of source uncertainty.',
                                  'physicalSourceComplete': 'For words and initials, true only if '
                                                            'selected token positions avoid all three '
                                                            'uncertain-prefix tokens. For finals, true '
                                                            'because all relevant final glyphs, '
                                                            'including l/e/s for these three tokens, '
                                                            'are source-certified. Record the '
                                                            'projection-specific rule without guessing '
                                                            'the unknown prefixes.',
                                  'negativeLanguage': 'No strict-format lead in the 72 readings of this '
                                                      'frozen repaired-OCR model. Separately report how '
                                                      'many readings used no uncertain token; '
                                                      'source-affected readings cannot exclude the '
                                                      'corresponding physical-source reading.',
                                  'hitLanguage': 'Any words/initials lead involving an uncertain-prefix '
                                                 'token depends on the provisional OCR spelling and '
                                                 'needs source confirmation before significance is '
                                                 'assigned. A finals reading uses only source-certified '
                                                 'terminal glyphs; this certifies its input glyphs, not '
                                                 'the cryptographic hypothesis.',
                                  'punctuationOnlyUncertainty': 'The p79 leading elision quote before '
                                                                'til is removed regardless of its curly '
                                                                'orientation because both U+2018 and '
                                                                'U+2019 are in the fixed wrapper set. A '
                                                                'standalone en/em dash after day has no '
                                                                'ASCII alphanumeric and is not a '
                                                                'counted token in this declared model. '
                                                                'Neither requires a model branch.',
                                  'finalGlyphEvidence': 'Root reports an independent blinded third '
                                                        'source review visibly certifying the final '
                                                        'glyphs l/e/s of the three affected words. This '
                                                        'proposal accepts that explicit source receipt; '
                                                        'the earlier page81 review conservatively left '
                                                        'row3 final-glyph evidence unresolved.'}},
 'parameters': {'expectedBodyRows': 312,
                'expectedUncertainTokens': 3,
                'maximumTokens': 5000,
                'expectedSubmittedRecords': 72,
                'maximumSubmittedRecords': 72,
                'maximumUniqueForms': 144,
                'maximumInputBytes': 2000000,
                'maximumRegisteredBlobBytes': 2000000,
                'maximumSubmittedCodePoints': 250000,
                'maximumUniqueFormCodePoints': 250000,
                'maximumSourceCodePoints': 250000,
                'stride': 12,
                'directions': ['forward', 'reverse'],
                'phaseLabelsOneBased': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                'phaseMeaning': 'Offset phase-1 into the direction-specific full token array, then '
                                'every twelfth token. Reverse means reverse all tokens before '
                                'selection.',
                'projections': ['words', 'initials', 'finals'],
                'forms': ['exact', 'whitespace-only-compacted'],
                'formats': ['wif', 'minikey', 'hex64', 'bip39'],
                'strictKnownSubset': 'Filter whole readings whose selected tokens are source-complete '
                                     'for their projection; never omit selected tokens or join across '
                                     'omitted tokens.',
                'uncertainty': 'Only first kept chunk in p4:col1_top:2/3/4 is uncertain for words and '
                               'initials; its finals l/e/s are source-certified.',
                'rawArtifacts': ['TOKENS.private.json', 'READINGS.private.jsonl'],
                'perStreamHashes': False,
                'networkQueries': 0,
                'deriveSeeds': False,
                'deriveAddresses': False,
                'transactions': 0},
 'fingerprintRule': {'algorithm': 'SHA-256',
                     'domainText': 'KEY404/batch20/record-fingerprint/v1',
                     'separatorHex': '00',
                     'rule': 'SHA256(domain || 0x00 || ASCII(format) || 0x00 || canonical record '
                             'bytes)'},
 'controls': ['shared-format-controls',
              'literal-wrappers-censor-hyphen-slash-currency-internal-apostrophes',
              'all-directions-phases-projections-no-resets',
              'every-twelfth-published-minikey-and-BIP39',
              'whole-reading-projection-uncertainty-filter',
              'source-alignment-schema-and-uncertainty-guards',
              'nominal-72-empty-and-duplicate-records',
              'safe-evaluation-allowlist',
              'protocol-and-registration-byte-drift-rejections'],
 'negativeCriterion': 'A complete zero result excludes only four literal formats in the 72 declared '
                      'readings of the single frozen repaired-OCR model. Separately report the '
                      'whole-reading subset with source-complete projection inputs. Never call the '
                      'whole physical-source hypothesis negative.',
 'limitations': ['Stride12 is exploratory, motivated by the duplicated printed 12-step passage; no '
                 'creator instruction is authenticated.',
                 'Conventional body-row order, whitespace chunks and the exact wrapper set are declared '
                 'model assumptions.',
                 'Three unchanged low-confidence leading words remain provisional for words and '
                 'initials; no alternative spelling is tried. Finals use source-certified terminal '
                 'glyphs.',
                 'No hard-wrap joins, linguistic letter policy, case variants, page resets, other '
                 'populations, arbitrary encodings or downstream key use are tested.',
                 'Minikey checksum evidence is weak and hex64 scalar range has no checksum. Any '
                 'positive is private review only.']}


def code_definition():
    return deepcopy(DEFINITION)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def sha_bytes(data):
    # Whole-file provenance/registration bytes only. Never called on target
    # streams or target candidate records.
    return hashlib.sha256(data).hexdigest()


def private_json(path, value):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                   'w', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=True)
        handle.write('\n')


def capped_read(file, limit):
    require(file.stat().st_size <= limit, 'File byte cap exceeded')
    with file.open('rb') as handle:
        content = handle.read(limit + 1)
    require(len(content) <= limit, 'File grew beyond byte cap')
    return content


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field')
        result[key] = value
    return result


def private_output(value):
    out = Path(value).expanduser().resolve()
    require(not any(part.lower() == 'public' for part in out.parts), 'Private output required')
    require(not out.exists() and not out.is_symlink(), 'Fresh output required')
    require(out.parent.is_dir(), 'Existing private output parent required')
    return out



def research_file(relative):
    require(relative in INPUTS + SCRIPTS, 'Unregistered file path')
    file = (ROOT / relative).resolve(strict=True)
    require(file.is_file() and file.is_relative_to(ROOT), 'Research file escapes root')
    return file

def literal_chunks(text):
    require(isinstance(text, str), 'Invalid source text')
    return [chunk.strip(WRAPPERS) for chunk in re.split(r'[ \t\r\n\f\v]+', text)
            if re.search(r'[A-Za-z0-9]', chunk)]

def validate_source(manifest, parent, expectations, source_hashes):
    require(isinstance(manifest, dict) and set(manifest) == {'schemaVersion','source','images','population','normalizationPolicy','reviewSummary','rows','preparedAtUTC'}, 'Body schema changed')
    require(type(manifest['schemaVersion']) is int and manifest['schemaVersion'] == 1, 'Body schema version changed')
    require(manifest['source'] == {'path':PRIMARY,'sha256':PRIMARY_SHA256,'bytes':946620}, 'Body parent metadata changed')
    require(isinstance(parent, dict) and isinstance(parent.get('rows'), list) and len(parent['rows']) == 356, 'Parent rows changed')
    require(isinstance(manifest['images'], list) and len(manifest['images']) == 4, 'Image evidence metadata changed')
    for index, image in enumerate(manifest['images'], 1):
        relative = IMAGE_DIR + 'page_' + str(index).zfill(2) + '.jpg'
        require(isinstance(image, dict) and set(image) == {'path','printedPage','sha256','bytes','width','height'}, 'Image evidence fields changed')
        require(image['path'] == relative and image['sha256'] == source_hashes[relative] and image['printedPage'] == index + 77 and image['width'] == 2040 and image['height'] == 2805, 'Image evidence identity changed')
        require(type(image['bytes']) is int and 0 < image['bytes'] <= DEFINITION['parameters']['maximumInputBytes'], 'Image byte metadata changed')
    require(manifest['population']['rows'] == 312 and manifest['population']['pages'] == [79,80,81] and manifest['population']['creatorDefinitionAuthenticated'] is False, 'Body population metadata changed')
    require(manifest['reviewSummary']['fullPhysicalSourceCertified'] is False and manifest['reviewSummary']['lexicallyUncertainFirstTokens'] == 3, 'Source uncertainty metadata changed')
    for key, expected in {'casePreserved':True,'hardWrapsJoined':False,'duplicatesDeleted':False,'sourceRowsReordered':False,'newWordsGuessed':False}.items():
        require(manifest['normalizationPolicy'].get(key) is expected, 'Source normalization policy changed')
    rows = manifest['rows']
    selected = [(index + 1, row) for index, row in enumerate(parent['rows']) if row.get('kind') == 'body']
    require(isinstance(rows, list) and len(rows) == len(selected) == expectations['bodyRows'] == 312, 'Body row population changed')
    core = {'rowId','sourceRowOrdinal','sourcePage','printedPage','region','line','rawLine','kind','originalText','printedText','modelText','sourceReviewStatus','uncertainForProjections','uncertainTokenIndices','sourceNormalizedBoxXYXY','notes'}
    seen = set()
    for row, (ordinal, old) in zip(rows, selected):
        require(isinstance(row, dict) and set(row) in (core,core|{'firstTokenFinalGlyphEvidence'}), 'Body row fields changed')
        require(type(row['sourceRowOrdinal']) is int and row['sourceRowOrdinal'] == ordinal, 'Body order changed')
        require(row['sourcePage'] == old['page'] and row['printedPage'] == {2:79,3:80,4:81}[old['page']] and row['region'] == old['region'] and row['line'] == old['line'] and row['rawLine'] == old['rawLine'], 'Body row identity changed')
        expected_id = 'p' + str(old['page']) + ':' + old['region'] + ':' + str(old['line'])
        require(row['rowId'] == expected_id and expected_id not in seen and row['kind'] == 'body', 'Body row ID changed')
        seen.add(expected_id)
        require(isinstance(row['originalText'], str) and row['originalText'] == old['text'] and isinstance(row['modelText'], str), 'Parent text linkage changed')
        require(row['printedText'] is None or isinstance(row['printedText'], str) and row['printedText'] == row['modelText'], 'Printed/model policy changed')
        uncertain = expected_id in UNCERTAIN
        require(row['uncertainTokenIndices'] == ([0] if uncertain else []) and row['uncertainForProjections'] == (['words','initials'] if uncertain else []), 'Projection uncertainty changed')
        require(('firstTokenFinalGlyphEvidence' in row) is uncertain, 'Final glyph evidence changed')
        if uncertain:
            glyph, count = UNCERTAIN[expected_id]
            require(row['sourceReviewStatus'] == 'lexical-prefix-uncertain' and row['printedText'] is None, 'Uncertain source status changed')
            require(row['firstTokenFinalGlyphEvidence']['glyph'] == glyph and row['firstTokenFinalGlyphEvidence']['sourceRowWordCount'] == count, 'Known final/count evidence changed')
    require(set(UNCERTAIN).issubset(seen) and sum(len(row['modelText']) for row in rows) <= DEFINITION['parameters']['maximumSourceCodePoints'], 'Body source cap failed')
    return rows

def make_tokens(rows):
    tokens = []
    for row in rows:
        chunks = literal_chunks(row['modelText'])
        unknown = row['uncertainTokenIndices']
        require(all(type(index) is int and 0 <= index < len(chunks) for index in unknown), 'Uncertain token index invalid')
        if row['rowId'] in UNCERTAIN:
            glyph, count = UNCERTAIN[row['rowId']]
            original = literal_chunks(row['originalText'])
            require(len(chunks) == count and chunks[0] == original[0] and chunks[0][-1] == glyph, 'Uncertain token/count/final changed')
        for within, text in enumerate(chunks):
            require(text and re.search(r'[A-Za-z0-9]', text), 'Empty retained token')
            tokens.append({'tokenIndex0':len(tokens),'rowId':row['rowId'],'withinRowIndex0':within,
                           'text':text,'uncertainForProjections':list(row['uncertainForProjections']) if within in unknown else []})
            require(len(tokens) <= DEFINITION['parameters']['maximumTokens'], 'Token cap exceeded')
    return tokens

def make_readings(tokens):
    readings = []
    for direction in DIRECTIONS:
        ordered = tokens if direction == 'forward' else list(reversed(tokens))
        for phase in range(1,13):
            selected = ordered[phase-1::12]
            for projection in PROJECTIONS:
                if projection == 'words':
                    text = ' '.join(token['text'] for token in selected)
                elif projection == 'initials':
                    text = ''.join(token['text'][0] for token in selected)
                else:
                    text = ''.join(token['text'][-1] for token in selected)
                affected = sum(projection in token['uncertainForProjections'] for token in selected)
                readings.append({'id':direction+':phase'+str(phase).zfill(2)+':'+projection,
                    'direction':direction,'phase':phase,'projection':projection,
                    'selectedTokenCount':len(selected),'sourceCompleteForProjection':affected == 0,
                    'uncertainSelectedTokens':affected,'text':text})
    require(len(readings) == 72 and len({row['id'] for row in readings}) == 72, 'Reading population changed')
    return readings

def evaluate(readings):
    p = DEFINITION['parameters']
    require(isinstance(readings,list) and len(readings) <= p['maximumSubmittedRecords'], 'Reading cap exceeded')
    require(sum(len(row['text']) for row in readings) <= p['maximumSubmittedCodePoints'], 'Reading character cap exceeded')
    forms = {row['text'] for row in readings}
    forms |= {re.sub(r'\s','',text) for text in tuple(forms)}
    require(len(forms) <= p['maximumUniqueForms'] and sum(map(len,forms)) <= p['maximumUniqueFormCodePoints'], 'Evaluation form cap exceeded')
    from batch20_common import DEFAULT_FORMATS, scan_streams
    require(DEFAULT_FORMATS == FORMATS, 'Shared default formats changed')
    checked = safe_evaluation(scan_streams(readings, FORMATS))
    require(checked['streamCount'] == len(readings) and checked['uniqueFormCount'] == len(forms), 'Evaluation coverage differs')
    return checked


def registered_blob(registration, relative):
    object_name = registration + ':public/research/' + relative
    size = subprocess.run(['git', 'cat-file', '-s', object_name], cwd=ROOT,
                          capture_output=True, timeout=30, check=False)
    require(size.returncode == 0 and len(size.stdout) <= 20 and
            re.fullmatch(rb'[0-9]+\n', size.stdout), 'Missing registration size')
    expected_size = int(size.stdout)
    require(expected_size <= DEFINITION['parameters']['maximumRegisteredBlobBytes'], 'Registered blob cap exceeded')
    result = subprocess.run(['git', 'cat-file', 'blob', object_name],
                            cwd=ROOT, capture_output=True, timeout=30, check=False)
    require(result.returncode == 0 and len(result.stdout) == expected_size, 'Missing registration bytes')
    return result.stdout


def verify_registered_bytes(registration, files, reader):
    # Pure equality helper; controls supply synthetic bytes and a mock reader.
    for relative, content in files.items():
        require(reader(registration, relative) == content, 'Registration bytes differ')


def safe_evaluation(evaluation):
    expected_keys = {'streamCount', 'uniqueStreamCount', 'uniqueFormCount', 'formats', 'shapeCounts',
                     'uniqueShapeCounts', 'executionCount', 'validCounts', 'hits', 'privateReviewRequired',
                     'fingerprintRule', 'networkQueries', 'rawAsciiScalarInterpretations'}
    require(isinstance(evaluation, dict) and set(evaluation) == expected_keys, 'Unexpected evaluator schema')
    require(evaluation['formats'] == list(FORMATS) and evaluation['fingerprintRule'] == FINGERPRINT_RULE, 'Evaluator scope differs')
    for key in ('streamCount', 'uniqueStreamCount', 'uniqueFormCount', 'executionCount', 'networkQueries', 'rawAsciiScalarInterpretations'):
        require(type(evaluation[key]) is int and evaluation[key] >= 0, 'Invalid evaluator count')
    for key in ('shapeCounts', 'uniqueShapeCounts', 'validCounts'):
        require(isinstance(evaluation[key], dict) and set(evaluation[key]) == set(FORMATS), 'Invalid evaluator count fields')
        require(all(type(value) is int and value >= 0 for value in evaluation[key].values()), 'Invalid evaluator counts')
    require(evaluation['networkQueries'] == 0 and evaluation['rawAsciiScalarInterpretations'] == 0, 'Forbidden evaluator action')
    require(isinstance(evaluation['hits'], list), 'Invalid evaluator hits')
    counts = Counter()
    for hit in evaluation['hits']:
        require(isinstance(hit, dict) and hit.get('format') in FORMATS, 'Unexpected hit format')
        kind = hit['format']
        fields = {'format', 'fingerprint', 'checkBits', 'private'}
        fields |= {'compressed'} if kind == 'wif' else {'length'} if kind == 'minikey' else {'wordCount'} if kind == 'bip39' else set()
        require(set(hit) == fields and hit['private'] is True, 'Unsafe hit metadata')
        require(isinstance(hit['fingerprint'], str) and re.fullmatch(r'[0-9a-f]{64}', hit['fingerprint']), 'Invalid record fingerprint')
        require(type(hit['checkBits']) is int, 'Invalid checksum metadata')
        if kind == 'wif':
            require(type(hit['compressed']) is bool and hit['checkBits'] == 32, 'Invalid WIF metadata')
        elif kind == 'minikey':
            require(type(hit['length']) is int and hit['length'] in (22, 30) and hit['checkBits'] == 8, 'Invalid minikey metadata')
        elif kind == 'hex64':
            require(hit['checkBits'] == 0, 'Invalid hex metadata')
        else:
            require(type(hit['wordCount']) is int and hit['wordCount'] in (12, 15, 18, 21, 24) and hit['checkBits'] == hit['wordCount'] // 3, 'Invalid mnemonic metadata')
        counts[kind] += 1
    require(all(counts[kind] == evaluation['validCounts'][kind] for kind in FORMATS), 'Hit counts disagree')
    require(len({(hit['format'], hit['fingerprint']) for hit in evaluation['hits']}) == len(evaluation['hits']), 'Duplicate safe record')
    require(evaluation['executionCount'] == sum(evaluation['uniqueShapeCounts'].values()), 'Validation execution counts differ')
    require(all(evaluation['shapeCounts'][kind] >= evaluation['uniqueShapeCounts'][kind] >= evaluation['validCounts'][kind]
                for kind in FORMATS), 'Validation count bounds differ')
    require(evaluation['uniqueStreamCount'] <= evaluation['streamCount'] and
            evaluation['uniqueStreamCount'] <= evaluation['uniqueFormCount'] <= 2 * evaluation['uniqueStreamCount'], 'Evaluator form bounds differ')
    require(type(evaluation['privateReviewRequired']) is bool and evaluation['privateReviewRequired'] == bool(evaluation['hits']), 'Lead classification differs')
    return deepcopy(evaluation)



def validate_protocol_header(protocol, registration):
    require(re.fullmatch(r'[0-9a-f]{40}', registration or '') is not None, 'Full registration commit required')
    require(isinstance(protocol,dict) and set(protocol) == {'version','batchId','test','sourceHashes','scriptHashes','sourceExpectations'}, 'Protocol schema changed')
    require(type(protocol['version']) is int and protocol['version'] == 1 and protocol['batchId'] == BATCH_ID and protocol['test'] == code_definition(), 'Protocol differs from code definition')
    require(protocol['sourceHashes'] == INPUT_PINS, 'Source pin population or bytes differ')
    require(isinstance(protocol['scriptHashes'],dict) and set(protocol['scriptHashes']) == set(SCRIPTS) and all(isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) for value in protocol['scriptHashes'].values()), 'Script pin population differs')
    expected = protocol['sourceExpectations']
    require(isinstance(expected,dict) and set(expected) == {'bodyRows','bodyTokenCount','uncertainTokens'}, 'Source expectations schema changed')
    require(all(type(value) is int for value in expected.values()) and expected['bodyRows'] == 312 and expected['uncertainTokens'] == 3 and 0 < expected['bodyTokenCount'] <= DEFINITION['parameters']['maximumTokens'], 'Source expectations changed')

def validate_protocol(protocol_path, registration, blob_reader=None):
    file = Path(protocol_path).resolve(strict=True)
    require(file.is_file() and file.is_relative_to(ROOT), 'Public protocol required')
    content = capped_read(file,1000000)
    protocol = json.loads(content,object_pairs_hook=unique_json_object)
    validate_protocol_header(protocol,registration)
    files = {}
    for key,paths in (('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)):
        for relative in paths:
            raw = capped_read(research_file(relative),DEFINITION['parameters']['maximumRegisteredBlobBytes'])
            require(sha_bytes(raw) == protocol[key][relative], 'Pinned bytes changed')
            files[relative] = raw
    require(len(files[BODY]) == 218304 and len(files[PRIMARY]) == 946620, 'Frozen source byte lengths changed')
    relative = file.relative_to(ROOT).as_posix()
    require(relative not in files, 'Protocol replaces a pin')
    files[relative] = content
    verify_registered_bytes(registration,files,blob_reader or registered_blob)
    return protocol,sha_bytes(content),files

def self_test():
    from batch20_common import self_test as shared_test
    shared = shared_test()
    require(shared.get('passed') is True, 'Shared controls failed')
    require(len(WRAPPERS) == len(set(WRAPPERS)) == 18, 'Wrapper set changed')
    def toy(texts, unknown=None):
        rows = [{'rowId':'toy:'+str(i),'modelText':text,'originalText':text,
                 'uncertainTokenIndices':([0] if unknown == i else []),
                 'uncertainForProjections':(['words','initials'] if unknown == i else [])}
                for i,text in enumerate(texts)]
        return make_tokens(rows)
    literal = toy(['“c****.” U.S. exponen-','tial. and/','or $400 can’t','day — ‘til 12-step'])
    require([row['text'] for row in literal] == ['c****','U.S','exponen-','tial','and/','or','$400','can’t','day','til','12-step'], 'Literal boundaries changed')
    require(''.join(t['text'][0] for t in literal) == 'cUetao$cdt1' and ''.join(t['text'][-1] for t in literal) == '*S-l/r0tylp', 'Literal glyph projections changed')
    require(literal_chunks("'til ‘til ’til “til”") == ['til']*4 and literal_chunks('— / *** !') == [], 'Quote/punctuation policy changed')
    require(literal_chunks('aa\u2003bb') == ['aa\u2003bb'], 'Non-ASCII whitespace incorrectly split')
    sequence = ['a'+str(i).zfill(2) for i in range(24)]
    tokens = toy([' '.join(sequence)])
    readings = make_readings(tokens)
    partition = toy([' '.join(sequence[:5]),' '.join(sequence[5:17]),' '.join(sequence[17:])])
    require(make_readings(partition) == readings, 'Unexpected row reset')
    for reading in readings:
        ordered = sequence if reading['direction'] == 'forward' else sequence[::-1]
        selected = [value for index,value in enumerate(ordered) if index % 12 == reading['phase']-1]
        projection = reading['projection']
        expected = ' '.join(selected) if projection == 'words' else ''.join(value[0 if projection == 'initials' else -1] for value in selected)
        require(reading['text'] == expected and reading['selectedTokenCount'] == 2, 'Direction/phase/projection control failed')
    by_id = {row['id']:row for row in readings}
    require(by_id['forward:phase06:words']['text'] == 'a05 a17' and by_id['reverse:phase06:words']['text'] == 'a18 a06', 'Phase indexing changed')
    tokens[5]['uncertainForProjections'] = ['words','initials']
    uncertainty = make_readings(tokens)
    affected = [r for r in uncertainty if not r['sourceCompleteForProjection']]
    require(len(affected) == 4 and all(r['projection'] != 'finals' and r['uncertainSelectedTokens'] == 1 for r in affected), 'Projection uncertainty changed')
    require(all(r['sourceCompleteForProjection'] for r in uncertainty if r['projection'] == 'finals'), 'Known finals incorrectly excluded')
    strict = [r for r in uncertainty if r['sourceCompleteForProjection']]
    require(len(strict) == 68 and all(r['selectedTokenCount'] == 2 for r in strict), 'Strict subset dropped individual words')
    short = make_readings(toy(['a a']))
    require(len(short) == 72 and len({r['text'] for r in short}) < 72, 'Nominal empty/duplicate records lost')
    empty = evaluate(make_readings([]))
    require(empty['streamCount'] == 72 and empty['uniqueStreamCount'] == 1, 'Empty reading records lost')
    sample = 'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'
    slots = ['q']*(12*len(sample))
    for index,glyph in enumerate(sample):slots[index*12+4] = glyph
    mini = make_readings(toy([' '.join(slots)]))
    require(next(r['text'] for r in mini if r['id'] == 'forward:phase05:initials') == sample, 'Stride minikey placement changed')
    mini_result = evaluate(mini)
    require(mini_result['validCounts']['minikey'] >= 1, 'Stride minikey control not detected')
    controls = json.loads((ROOT/'scripts/batch20_support/controls.json').read_text())
    phrase = controls['bip39_valid'].split(' ')
    slots = ['unknownword']*(12*len(phrase))
    for index,word in enumerate(phrase):slots[index*12+2] = word
    bip = make_readings(toy([' '.join(slots)]))
    require(next(r['text'] for r in bip if r['id'] == 'forward:phase03:words') == ' '.join(phrase), 'Stride BIP39 placement changed')
    bip_result = evaluate(bip)
    require(bip_result['validCounts']['bip39'] >= 1, 'Stride BIP39 control not detected')
    unsafe = deepcopy(mini_result);unsafe['hits'][0]['value'] = sample
    try:safe_evaluation(unsafe)
    except ValueError:pass
    else:raise ValueError('Unsafe hit field accepted')
    require(sample not in json.dumps(mini_result) and hashlib.sha256(sample.encode('ascii')).hexdigest() not in json.dumps(mini_result), 'Raw/scalar control leaked')
    protocol = {'version':1,'batchId':BATCH_ID,'test':code_definition(),'sourceHashes':dict(INPUT_PINS),
                'scriptHashes':{relative:'2'*64 for relative in SCRIPTS},'sourceExpectations':{'bodyRows':312,'bodyTokenCount':24,'uncertainTokens':3}}
    validate_protocol_header(protocol,'1'*40)
    invalid=[]
    for key,value in [('sourceHashes',{}),('scriptHashes',{}),('sourceExpectations',{'bodyRows':312,'bodyTokenCount':5001,'uncertainTokens':3}),('version',True)]:
        changed=deepcopy(protocol);changed[key]=value;invalid.append(changed)
    changed=deepcopy(protocol);changed['test']['parameters']['stride']=13;invalid.append(changed)
    for changed in invalid:
        try:validate_protocol_header(changed,'1'*40)
        except ValueError:pass
        else:raise ValueError('Unregistered protocol accepted')
    synthetic={'protocol':b'synthetic protocol','script':b'synthetic code'}
    verify_registered_bytes('1'*40,synthetic,lambda commit,relative:synthetic[relative])
    try:verify_registered_bytes('1'*40,synthetic,lambda commit,relative:synthetic[relative]+b' ')
    except ValueError:pass
    else:raise ValueError('Registration byte drift accepted')
    source_rows=[];parent_rows=[]
    for page,count in ((2,109),(3,116),(4,87)):
        for line in range(1,count+1):
            region='col1_top' if page==4 else 'col1'
            row_id='p'+str(page)+':'+region+':'+str(line)
            text='control'
            if row_id in UNCERTAIN:
                final,count_words=UNCERTAIN[row_id]
                text='a'+final+' '+' '.join(['control']*(count_words-1))
            old={'kind':'body','page':page,'region':region,'line':line,'rawLine':line,'text':text}
            parent_rows.append(old)
            row={'rowId':row_id,'sourceRowOrdinal':len(parent_rows),'sourcePage':page,'printedPage':page+77,
                 'region':region,'line':line,'rawLine':line,'kind':'body','originalText':text,'printedText':text,
                 'modelText':text,'sourceReviewStatus':'confirmed','uncertainForProjections':[],
                 'uncertainTokenIndices':[],'sourceNormalizedBoxXYXY':[0,0,1,1],'notes':[]}
            if row_id in UNCERTAIN:
                final,count_words=UNCERTAIN[row_id]
                row.update(printedText=None,sourceReviewStatus='lexical-prefix-uncertain',
                           uncertainForProjections=['words','initials'],uncertainTokenIndices=[0],
                           firstTokenFinalGlyphEvidence={'glyph':final,'sourceRowWordCount':count_words})
            source_rows.append(row)
    parent_fixture={'rows':parent_rows+[{'kind':'intro'} for _ in range(44)]}
    manifest={'schemaVersion':1,'source':{'path':PRIMARY,'sha256':PRIMARY_SHA256,'bytes':946620},
        'images':[{'path':IMAGE_DIR+'page_'+str(i).zfill(2)+'.jpg','printedPage':i+77,
                   'sha256':INPUT_PINS[IMAGE_DIR+'page_'+str(i).zfill(2)+'.jpg'],'bytes':1,'width':2040,'height':2805} for i in range(1,5)],
        'population':{'rows':312,'pages':[79,80,81],'creatorDefinitionAuthenticated':False},
        'normalizationPolicy':{'casePreserved':True,'hardWrapsJoined':False,'duplicatesDeleted':False,'sourceRowsReordered':False,'newWordsGuessed':False},
        'reviewSummary':{'fullPhysicalSourceCertified':False,'lexicallyUncertainFirstTokens':3},
        'rows':source_rows,'preparedAtUTC':'2000-01-01T00:00:00.000Z'}
    validated=validate_source(manifest,parent_fixture,{'bodyRows':312,'bodyTokenCount':328,'uncertainTokens':3},INPUT_PINS)
    require(len(make_tokens(validated))==328, 'Synthetic full-source token population changed')
    mutations=[]
    mutations.append(lambda m:m['rows'].reverse())
    mutations.append(lambda m:m['rows'].pop())
    mutations.append(lambda m:m['rows'][0].update(rowId='different'))
    mutations.append(lambda m:m['rows'][0].update(sourceRowOrdinal=2))
    mutations.append(lambda m:m['rows'][0].update(originalText='different'))
    mutations.append(lambda m:m['rows'][0].update(modelText='different'))
    mutations.append(lambda m:m['normalizationPolicy'].update(casePreserved=False))
    mutations.append(lambda m:m['images'][0].update(sha256='0'*64))
    for field,value in [('uncertainForProjections',['words','initials','finals']),('uncertainTokenIndices',[1]),('sourceReviewStatus','confirmed')]:
        mutations.append(lambda m,field=field,value=value:next(r for r in m['rows'] if r['rowId']=='p4:col1_top:2').update({field:value}))
    mutations.append(lambda m:next(r for r in m['rows'] if r['rowId']=='p4:col1_top:2')['firstTokenFinalGlyphEvidence'].update(glyph='x'))
    for mutate in mutations:
        changed=deepcopy(manifest);mutate(changed)
        try:validate_source(changed,parent_fixture,{'bodyRows':312,'bodyTokenCount':328,'uncertainTokens':3},INPUT_PINS)
        except ValueError:pass
        else:raise ValueError('Source/schema uncertainty drift accepted')
    try:make_tokens([{'rowId':'toy-cap','modelText':'a '*5001,'originalText':'a '*5001,'uncertainTokenIndices':[],'uncertainForProjections':[]}])
    except ValueError:pass
    else:raise ValueError('Token cap ignored')
    return {'passed':True,'controls':DEFINITION['controls'],'shared':shared,'syntheticNominalReadings':72,
            'syntheticSelectionComparisons':72,'syntheticUncertaintyAffected':4,'syntheticStrictKnownReadings':68,
            'syntheticPositiveFormatControls':['published-minikey30-every12','BIP39-every12'],
            'syntheticProtocolRejections':len(invalid)+1,'syntheticSourceGuardRejections':len(mutations),'syntheticSourceBodyRows':312,'syntheticTokenCapRejections':1,'targetInputsRead':False,'targetTokenizations':0,
            'targetStrideSelections':0,'targetRecordChecks':0,'networkQueries':0,'transactions':0}

def run(args):
    require(re.fullmatch(r'[0-9a-f]{40}',args.registration_commit or '') is not None, 'Full registration commit required')
    out=private_output(args.out);out.mkdir(mode=0o700)
    require(out.stat().st_mode & 0o077 == 0, 'Private output mode required')
    result={'schemaVersion':1,'batchId':BATCH_ID,'testId':DEFINITION['id'],'startedAtUTC':utc(),
            'registrationCommit':args.registration_commit,'policySha256':POLICY_SHA256,
            'scopeComplete':False,'computationalModelComplete':False,'physicalSourceComplete':False,
            'completeNegative':False,'completeModelNegative':False,'strictKnownSubsetComplete':False,
            'strictKnownSubsetNegative':False,'completePhysicalHypothesisNegative':False,
            'privateReviewRequired':False,'networkQueries':0,'transactions':0}
    try:
        controls=self_test()
        protocol,protocol_hash,files=validate_protocol(args.protocol,args.registration_commit)
        # Only now parse article text: controls and all actual Git byte gates passed.
        manifest=json.loads(files[BODY],object_pairs_hook=unique_json_object)
        parent=json.loads(files[PRIMARY],object_pairs_hook=unique_json_object)
        rows=validate_source(manifest,parent,protocol['sourceExpectations'],protocol['sourceHashes'])
        tokens=make_tokens(rows)
        require(len(tokens) == protocol['sourceExpectations']['bodyTokenCount'], 'Frozen token population differs')
        require(sum(bool(t['uncertainForProjections']) for t in tokens) == protocol['sourceExpectations']['uncertainTokens'], 'Uncertain token population differs')
        readings=make_readings(tokens)
        strict=[r for r in readings if r['sourceCompleteForProjection']]
        evaluation_all=evaluate(readings)
        evaluation_strict=evaluate(strict)
        require({(h['format'],h['fingerprint']) for h in evaluation_strict['hits']}.issubset({(h['format'],h['fingerprint']) for h in evaluation_all['hits']}), 'Strict subset hit inclusion failed')
        private_json(out/'TOKENS.private.json',{'schemaVersion':1,'tokens':tokens})
        with os.fdopen(os.open(out/'READINGS.private.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',encoding='utf-8') as handle:
            for reading in readings:handle.write(json.dumps(reading,ensure_ascii=True)+'\n')
        lead=evaluation_all['privateReviewRequired']
        result.update(protocolSha256=protocol_hash,sourceHashes=protocol['sourceHashes'],scriptHashes=protocol['scriptHashes'],
            sourceExpectations=protocol['sourceExpectations'],parameters=DEFINITION['parameters'],controls=controls,
            scopeComplete=True,computationalModelComplete=True,physicalSourceComplete=False,
            completeModelNegative=not lead,strictKnownSubsetComplete=True,
            strictKnownSubsetNegative=not evaluation_strict['privateReviewRequired'],privateReviewRequired=lead,
            evaluationAll=evaluation_all,evaluationStrictKnown=evaluation_strict,
            procedureCounts={'bodyRows':len(rows),'bodyTokens':len(tokens),'uncertainTokens':3,'nominalReadings':len(readings),
              'strictKnownReadings':len(strict),'sourceAffectedReadings':len(readings)-len(strict),
              'readingsByProjection':{p:sum(r['projection']==p for r in readings) for p in PROJECTIONS},
              'strictKnownReadingsByProjection':{p:sum(r['projection']==p for r in strict) for p in PROJECTIONS},
              'submittedCodePoints':sum(len(r['text']) for r in readings),'perStreamHashes':False},
            outcome='finding-private-review-required' if lead else 'no-valid-record-in-fixed-model',
            negativeCriterion=DEFINITION['negativeCriterion'],limitations=DEFINITION['limitations'],
            privateArtifacts=['TOKENS.private.json','READINGS.private.jsonl'])
    except Exception as error:
        private_json(out/'ERROR.private.json',{'errorClass':type(error).__name__,'error':'Registered execution failed; no negative claim.'})
        result.update(outcome='inconclusive-control-pin-source-or-execution',errorClass=type(error).__name__,
                      error='Controls, registration bytes, source alignment, bounds or evaluation failed. No negative claim.')
    result['completedAtUTC']=utc();private_json(out/'RESULT.json',result)
    print(json.dumps({key:result[key] for key in ('testId','outcome','computationalModelComplete','physicalSourceComplete','completeModelNegative','strictKnownSubsetNegative','privateReviewRequired','networkQueries')}))
    return result


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('Invalid arguments')



def main(argv=None):
    parser=SafeParser(description=__doc__,allow_abbrev=False)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list',action='store_true');group.add_argument('--self-test',action='store_true');group.add_argument('--run',action='store_true')
    parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out')
    arguments=list(sys.argv[1:] if argv is None else argv)
    for option in ('--list','--self-test','--run','--protocol','--registration-commit','--out'):
        require(sum(value==option or value.startswith(option+'=') for value in arguments)<=1,'Duplicate argument')
    args=parser.parse_args(arguments)
    if args.list or args.self_test:
        require(not any((args.protocol,args.registration_commit,args.out)),'Mixed action arguments')
        print(json.dumps(code_definition() if args.list else self_test(),indent=2));return 0
    require(args.protocol and args.registration_commit and args.out,'Run requires protocol, registration commit and fresh private output')
    return 0 if run(args)['computationalModelComplete'] else 1

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        print(json.dumps({'outcome':'inconclusive-before-execution','computationalModelComplete':False,'physicalSourceComplete':False,'completeModelNegative':False,'strictKnownSubsetNegative':False,'networkQueries':0}),file=sys.stderr)
        sys.exit(1)
