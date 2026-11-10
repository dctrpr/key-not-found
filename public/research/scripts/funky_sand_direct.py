#!/usr/bin/env python3
"""Three fixed literal Sand readings; offline source generation, stdlib only.

--definition and --self-test never open target sources. --run requires exact
protocol/source/code bytes in a full Git registration commit. Generated text
stays in a fresh private directory. No semantic, key-format, checksum, address,
wallet or network implementation is included. SHA-256 is output/file integrity.
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
import tempfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
PRIMARY = 'sources/funky-upheaval/physical-lines.json'
REGISTER = 'sources/funky-upheaval/SOURCE_REGISTER.json'
AUTHORITY = 'analysis_outputs/continuation_20261109/george_sand_research.md'
IMAGES = tuple(f'sources/funky-upheaval/pages/{p}.jpg' for p in (108,109,110,111))
INPUTS = (PRIMARY, REGISTER) + IMAGES + (AUTHORITY,)
SCRIPTS = ('scripts/funky_sand_direct.py', 'scripts/verify_funky_sand_direct.py')
PROTOCOL = 'analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.json'
TEST_ID = 'funky-sand-direct'
BATCH_ID = 'keiser-funky-sand-direct-20261110'
READING_IDS = ('SAND-FW-ALL', 'SAND-ODD-LINES', 'SAND-EVEN-CONTROL')
ROW_KEYS = ('id','ordinal','printedPage','role','block','lineInBlock','printedText')
MAX_INPUT_BYTES = 2_000_000
MAX_PROTOCOL_BYTES = 1_000_000
MAX_ROW_CODEPOINTS = 2000
MAX_SOURCE_CODEPOINTS = 100_000
MAX_OUTPUT_CODEPOINTS = 200_000

EXPECTED_METADATA = {'version': 1,
 'modelId': 'funky-upheaval-physical-lines-v1',
 'status': 'frozen-declared-transcription-model',
 'frozenAtUTC': '2026-11-10T12:56:33.732Z',
 'title': 'Bitcoin and the Funky Upheaval',
 'publication': 'Bitcoin Magazine',
 'issueNumber': None,
 'publicationDate': None,
 'eligibility': {'status': 'unverified-conditional',
                 'decemberClaimURL': 'https://x.com/maxkeiser/status/1607378060172460032',
                 'decemberStatementDoesNotIdentifyThisArticle': True,
                 'marchMirrorApplied': False,
                 'march20BTCClaimAssigned': False,
                 'prizeOrFundingAuthenticated': False},
 'scope': {'printedTextPages': [108, 109, 110, 111],
           'allPhysicalContentRowsIncluded': True,
           'titleRowsIncluded': True,
           'articlePageBoundaries': [107, 108, 109, 110, 111, 112],
           'outsideThisModel': ['Printed107illustrated opener and printed112related full-page art.',
                                'Running headers, vertical margin labels, page numbers and tiny footer '
                                'signatures.',
                                'Decorative coin labels and the separately retained adjacent '
                                'advertisements.'],
           'wholeColumnCipherExclusion': False},
 'order': 'Preserve the stored row order: printed page ascending, then visual top-to-bottom '
          'block/physical-line order. This conventional order is not an authenticated creator cipher '
          'instruction.',
 'encoding': {'version': 'literal-printedText-v1',
              'characterEncoding': 'UTF-8',
              'normalization': 'none',
              'printedTextPolicy': 'Every printedText string is byte-identical in UTF-8 to the reviewed '
                                   'draft. Literal case, punctuation, visible physical wraps and stored word '
                                   'spacing are frozen as this declared transcription model.',
              'wordSpacing': 'One U+0020 between visible word chunks; no leading/trailing or repeated '
                             'U+0020, tabs, CR or LF inside a row. Raster spacing widths are not '
                             'represented.',
              'apostrophes': 'Retain existing U+0027 ASCII apostrophe bytes. Apostrophe presence was '
                             'visually reviewed; original typesetting codepoints are not recovered from '
                             'raster ink.',
              'longDashes': 'Retain existing U+2014 em dash bytes, including the printed110 row-final Nobel '
                            'Prize dash.',
              'bookTitleQuotationMarks': 'Retain existing U+201C/U+201D double quotation marks in the '
                                         'printed111 work list, including the period before the final '
                                         'closing quote. Other stored quote bytes remain unchanged.',
              'case': 'Retain all literal case, including FiAT CUCkS. No case folding or style-based case '
                      'repair.',
              'physicalRows': 'One JSON record per reviewed physical content row; no hard-wrap joining or '
                              'fragment expansion.',
              'originalTypesettingUnicodeRecovered': False,
              'glyphPerfectOriginalByteStringClaimed': False},
 'sourceImages': [{'printedPage': 108,
                   'path': 'sources/funky-upheaval/pages/108.jpg',
                   'bytes': 1118342,
                   'sha256': '1557e2974d4f04579aea3015b6f885f35b2b966f06ac5944d39c70439ee8fb6c',
                   'width': 2040,
                   'height': 2805},
                  {'printedPage': 109,
                   'path': 'sources/funky-upheaval/pages/109.jpg',
                   'bytes': 1200108,
                   'sha256': 'bc12df605c993055ef761f27b413d9c8bc781d70c83533a7d9ae119034554814',
                   'width': 2040,
                   'height': 2805},
                  {'printedPage': 110,
                   'path': 'sources/funky-upheaval/pages/110.jpg',
                   'bytes': 1184970,
                   'sha256': '2f5cbca356f01887acf84cabcf6d5d8b5a5ec56547ae88329fd7de923a84601f',
                   'width': 2040,
                   'height': 2805},
                  {'printedPage': 111,
                   'path': 'sources/funky-upheaval/pages/111.jpg',
                   'bytes': 1016588,
                   'sha256': '40092c66f44296988a7f397563915e30f3926a6e265c512aa61b01057e970f50',
                   'width': 2040,
                   'height': 2805}],
 'sourceRegister': {'path': 'sources/funky-upheaval/SOURCE_REGISTER.json',
                    'sha256': 'fb756e12d376af208c619b6e46ea17366df9d90214992e53673cc10fda106b2f',
                    'role': 'Existing image/source identity register, left unchanged.'},
 'counts': {'physicalRows': 115,
            'titleRows': 4,
            'nonTitleRows': 111,
            'byPrintedPage': {'108': 11, '109': 41, '110': 29, '111': 34},
            'nonTitleByPrintedPage': {'108': 7, '109': 41, '110': 29, '111': 34},
            'byRole': {'title': 4,
                       'deck': 7,
                       'lead': 12,
                       'body': 53,
                       'display-emphasis': 10,
                       'attributed-quotation': 10,
                       'facts-display': 5,
                       'name-list': 3,
                       'section-introduction': 3,
                       'work-list': 5,
                       'closing-display': 3}},
 'review': {'reviewerType': 'Two AI visual passes; second pass unblinded to the draft.',
            'physicalRowsCompared': 115,
            'lexicalOrWrapCorrectionsProposedBySecondPass': 0,
            'roleOrOrderChangesProposedBySecondPass': 0,
            'unreadableLexicalRowsRecognized': 0,
            'reviewedDraftSHA256': 'c1cb621770524770f0edcd86dcd6b7e5562cff2255ec993ca48891b811570119',
            'independentRowReviewSHA256': 'd15e34055f2ef762adb75a845a85b17f5dae12ce7f76d750c757c6e087ed0a0b',
            'firstReviewCompletedAtUTC': '2026-11-10T12:42:23.642Z',
            'secondReviewCompletedAtUTC': '2026-11-10T12:47:59.198738+00:00',
            'limitations': ['AI visual agreement is fallible and does not authenticate the issue/date or '
                            'creator intent.',
                            'This freeze declares an encoding model, not original typesetting Unicode or '
                            'bytes.',
                            'Small furniture/decorative lettering outside the content-row population is not '
                            'exhaustively transcribed.']},
 'preparationOnly': {'projectedFirstWordOutputs': False,
                     'projectedAlternateLineOutputs': False,
                     'cryptographicTestsPerformed': False,
                     'networkRequestsPerformed': False,
                     'resultClaim': 'This is a source model, not an experiment or solution.'}}
ROW_LAYOUT = (('p108-title01', 1, 108, 'title', 'title', 1),
 ('p108-title02', 2, 108, 'title', 'title', 2),
 ('p108-title03', 3, 108, 'title', 'title', 3),
 ('p108-title04', 4, 108, 'title', 'title', 4),
 ('p108-deck01', 5, 108, 'deck', 'deck', 1),
 ('p108-deck02', 6, 108, 'deck', 'deck', 2),
 ('p108-deck03', 7, 108, 'deck', 'deck', 3),
 ('p108-deck04', 8, 108, 'deck', 'deck', 4),
 ('p108-deck05', 9, 108, 'deck', 'deck', 5),
 ('p108-deck06', 10, 108, 'deck', 'deck', 6),
 ('p108-deck07', 11, 108, 'deck', 'deck', 7),
 ('p109-r001', 12, 109, 'lead', 'lead', 1),
 ('p109-r002', 13, 109, 'lead', 'lead', 2),
 ('p109-r003', 14, 109, 'lead', 'lead', 3),
 ('p109-r004', 15, 109, 'lead', 'lead', 4),
 ('p109-r005', 16, 109, 'lead', 'lead', 5),
 ('p109-r006', 17, 109, 'lead', 'lead', 6),
 ('p109-r007', 18, 109, 'lead', 'lead', 7),
 ('p109-r008', 19, 109, 'body', 'historians', 1),
 ('p109-r009', 20, 109, 'body', 'historians', 2),
 ('p109-r010', 21, 109, 'body', 'historians', 3),
 ('p109-r011', 22, 109, 'body', 'historians', 4),
 ('p109-r012', 23, 109, 'body', 'invisible', 1),
 ('p109-r013', 24, 109, 'body', 'invisible', 2),
 ('p109-r014', 25, 109, 'body', 'essentially', 1),
 ('p109-r015', 26, 109, 'body', 'essentially', 2),
 ('p109-r016', 27, 109, 'body', 'essentially', 3),
 ('p109-r017', 28, 109, 'body', 'opposite', 1),
 ('p109-r018', 29, 109, 'body', 'opposite', 2),
 ('p109-r019', 30, 109, 'body', 'opposite', 3),
 ('p109-r020', 31, 109, 'display-emphasis', 'satoshi-display', 1),
 ('p109-r021', 32, 109, 'display-emphasis', 'satoshi-display', 2),
 ('p109-r022', 33, 109, 'display-emphasis', 'satoshi-display', 3),
 ('p109-r023', 34, 109, 'display-emphasis', 'satoshi-display', 4),
 ('p109-r024', 35, 109, 'display-emphasis', 'satoshi-display', 5),
 ('p109-r025', 36, 109, 'body', 'gold', 1),
 ('p109-r026', 37, 109, 'body', 'gold', 2),
 ('p109-r027', 38, 109, 'body', 'gold', 3),
 ('p109-r028', 39, 109, 'body', 'gold', 4),
 ('p109-r029', 40, 109, 'body', 'gold', 5),
 ('p109-r030', 41, 109, 'body', 'gold', 6),
 ('p109-r031', 42, 109, 'body', 'nocoiners', 1),
 ('p109-r032', 43, 109, 'body', 'nocoiners', 2),
 ('p109-r033', 44, 109, 'body', 'nocoiners', 3),
 ('p109-r034', 45, 109, 'body', 'humans', 1),
 ('p109-r035', 46, 109, 'body', 'humans', 2),
 ('p109-r036', 47, 109, 'body', 'humans', 3),
 ('p109-r037', 48, 109, 'body', 'humans', 4),
 ('p109-r038', 49, 109, 'body', 'humans', 5),
 ('p109-r039', 50, 109, 'body', 'humans', 6),
 ('p109-r040', 51, 109, 'body', 'humans', 7),
 ('p109-r041', 52, 109, 'display-emphasis', 'bitcoin-fixes-this', 1),
 ('p110-r001', 53, 110, 'body', 'early-adopters', 1),
 ('p110-r002', 54, 110, 'body', 'early-adopters', 2),
 ('p110-r003', 55, 110, 'body', 'early-adopters', 3),
 ('p110-r004', 56, 110, 'body', 'early-adopters', 4),
 ('p110-r005', 57, 110, 'body', 'early-adopters', 5),
 ('p110-r006', 58, 110, 'body', 'early-adopters', 6),
 ('p110-r007', 59, 110, 'body', 'early-adopters', 7),
 ('p110-r008', 60, 110, 'body', 'early-adopters', 8),
 ('p110-r009', 61, 110, 'attributed-quotation', 'hayek', 1),
 ('p110-r010', 62, 110, 'attributed-quotation', 'hayek', 2),
 ('p110-r011', 63, 110, 'attributed-quotation', 'hayek', 3),
 ('p110-r012', 64, 110, 'attributed-quotation', 'hayek', 4),
 ('p110-r013', 65, 110, 'attributed-quotation', 'hayek', 5),
 ('p110-r014', 66, 110, 'attributed-quotation', 'hayek', 6),
 ('p110-r015', 67, 110, 'attributed-quotation', 'hayek', 7),
 ('p110-r016', 68, 110, 'attributed-quotation', 'hayek', 8),
 ('p110-r017', 69, 110, 'attributed-quotation', 'hayek', 9),
 ('p110-r018', 70, 110, 'attributed-quotation', 'hayek', 10),
 ('p110-r019', 71, 110, 'body', 'sly-roundabout', 1),
 ('p110-r020', 72, 110, 'body', 'sly-roundabout', 2),
 ('p110-r021', 73, 110, 'body', 'sly-roundabout', 3),
 ('p110-r022', 74, 110, 'body', 'sly-roundabout', 4),
 ('p110-r023', 75, 110, 'body', 'sly-roundabout', 5),
 ('p110-r024', 76, 110, 'body', 'sly-roundabout', 6),
 ('p110-r025', 77, 110, 'facts-display', 'facts', 1),
 ('p110-r026', 78, 110, 'facts-display', 'facts', 2),
 ('p110-r027', 79, 110, 'facts-display', 'facts', 3),
 ('p110-r028', 80, 110, 'facts-display', 'facts', 4),
 ('p110-r029', 81, 110, 'facts-display', 'facts', 5),
 ('p111-r001', 82, 111, 'lead', 'economists-intro', 1),
 ('p111-r002', 83, 111, 'lead', 'economists-intro', 2),
 ('p111-r003', 84, 111, 'lead', 'economists-intro', 3),
 ('p111-r004', 85, 111, 'lead', 'economists-intro', 4),
 ('p111-r005', 86, 111, 'lead', 'economists-intro', 5),
 ('p111-r006', 87, 111, 'name-list', 'economists', 1),
 ('p111-r007', 88, 111, 'name-list', 'economists', 2),
 ('p111-r008', 89, 111, 'name-list', 'economists', 3),
 ('p111-r009', 90, 111, 'section-introduction', 'new-generation-intro', 1),
 ('p111-r010', 91, 111, 'section-introduction', 'new-generation-intro', 2),
 ('p111-r011', 92, 111, 'section-introduction', 'new-generation-intro', 3),
 ('p111-r012', 93, 111, 'work-list', 'new-generation-works', 1),
 ('p111-r013', 94, 111, 'work-list', 'new-generation-works', 2),
 ('p111-r014', 95, 111, 'work-list', 'new-generation-works', 3),
 ('p111-r015', 96, 111, 'work-list', 'new-generation-works', 4),
 ('p111-r016', 97, 111, 'work-list', 'new-generation-works', 5),
 ('p111-r017', 98, 111, 'body', 'antonopoulos', 1),
 ('p111-r018', 99, 111, 'body', 'antonopoulos', 2),
 ('p111-r019', 100, 111, 'body', 'antonopoulos', 3),
 ('p111-r020', 101, 111, 'body', 'antonopoulos', 4),
 ('p111-r021', 102, 111, 'body', 'antonopoulos', 5),
 ('p111-r022', 103, 111, 'body', 'antonopoulos', 6),
 ('p111-r023', 104, 111, 'display-emphasis', 'singularity', 1),
 ('p111-r024', 105, 111, 'display-emphasis', 'singularity', 2),
 ('p111-r025', 106, 111, 'display-emphasis', 'singularity', 3),
 ('p111-r026', 107, 111, 'display-emphasis', 'singularity', 4),
 ('p111-r027', 108, 111, 'body', 'future-past', 1),
 ('p111-r028', 109, 111, 'body', 'future-past', 2),
 ('p111-r029', 110, 111, 'body', 'future-past', 3),
 ('p111-r030', 111, 111, 'body', 'future-past', 4),
 ('p111-r031', 112, 111, 'body', 'future-past', 5),
 ('p111-r032', 113, 111, 'closing-display', 'genesis', 1),
 ('p111-r033', 114, 111, 'closing-display', 'genesis', 2),
 ('p111-r034', 115, 111, 'closing-display', 'genesis', 3))

DEFINITION = {
 'id': TEST_ID, 'title': 'Three literal Sand readings of the frozen Funky Upheaval source',
 'family': 'fixed-literal-source-reading', 'branchId': 'text-lines',
 'inputPaths': list(INPUTS), 'implementationPaths': list(SCRIPTS),
 'protocolPath': PROTOCOL,
 'sourceModel': {'id': EXPECTED_METADATA['modelId'], 'physicalRows':115,
   'titleRowsExcluded':4, 'contentRows':111,
   'contentRowsByPrintedPage':{'108':7,'109':41,'110':29,'111':34},
   'rolePopulation':EXPECTED_METADATA['counts']['byRole'],
   'encoding':EXPECTED_METADATA['encoding'],
   'ordering':'Stored source order; remove only title rows, then one global content-row index.',
   'issueAndDateAuthenticated':False},
 'readings': [
   {'id':READING_IDS[0], 'selectedRowCount':111,
    'rule':'First nonempty U+0020-delimited chunk of each retained row, preserving every glyph; join with one U+0020. Stop if a first chunk contains no ASCII letter/digit.'},
   {'id':READING_IDS[1], 'selectedRowCount':56,
    'rule':'Whole retained rows numbered 1,3,...,111 globally after title exclusion; join with LF.'},
   {'id':READING_IDS[2], 'selectedRowCount':55,
    'rule':'Whole retained rows numbered 2,4,...,110 globally after title exclusion; join with LF; predeclared parity control.'}],
 'boundaries': {'pageOrBlockResets':False,'roleSelectionsBeyondTitleExclusion':False,
   'caseOrUnicodeNormalization':False,'punctuationRemoval':False,'wrapJoining':False,
   'reversals':False,'initialsOrFinals':False,'selectedSubstrings':False,
   'keyFormatOrChecksumChecks':False,'wordlistFiltering':False,
   'proseToKeyHashing':False,'seedOrAddressDerivation':False,'networkQueries':0},
 'caps':{'maximumInputOrRegisteredBlobBytes':MAX_INPUT_BYTES,
   'maximumProtocolBytes':MAX_PROTOCOL_BYTES,'maximumRowCodepoints':MAX_ROW_CODEPOINTS,
   'maximumSourceCodepoints':MAX_SOURCE_CODEPOINTS,'maximumOutputCodepoints':MAX_OUTPUT_CODEPOINTS,
   'maximumReadings':3},
 'outputPolicy':{'privateArtifacts':['READINGS.private.json','READINGS.private.txt'],
   'rawOutputOutsidePublicCheckoutRequired':True,
   'safeReceipt':'RESULT.json: fixed technical fields, aggregate counts and output-integrity hashes only; no raw strings or row locators.',
   'hashMeaning':'SHA-256 of UTF-8 output bytes is an integrity identifier only, never a scalar/key derivation.',
   'semanticOutcome':'No semantic verdict is computed. Independent full-reading reviews follow separately.'},
 'authorityEvidence':{'path':AUTHORITY,
   'role':'Provenance only; no text from this file is used by the reading generator.',
   'caveat':'The creator-linked blog demonstrates first-word and alternate-whole-line readings; its current presentation includes later corrections, including one dated December 28, 2022, after the creator December 26 post.'},
 'limitations':[
   'Exact issue/date and applicability to the December 2022 plural-key claim remain unverified.',
   'The March 2023 mirror clue and 20-BTC claim are not assigned to this column.',
   'This is one frozen transcription/encoding model, not recovered original typesetting bytes.',
   'The population excludes title rows, running furniture, decorative text, opener/art and adjacent ads as declared.',
   'Three related source readings are not independent theories or statistical trials.',
   'Successful generation is neither semantic recognition nor a claim that a message, key or cipher is absent.']}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')


def digest(data):
    """File and UTF-8 output-integrity identifiers, never candidate/key hashes."""
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=True, allow_nan=False)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field')
        result[key] = value
    return result


def load_json(raw):
    def no_constant(value):
        raise ValueError('Nonfinite JSON constant')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object, parse_constant=no_constant)


def code_definition():
    return deepcopy(DEFINITION)


def capped_read(path, limit):
    require(path.is_file() and path.stat().st_size <= limit, 'File byte cap exceeded')
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, 'File grew beyond byte cap')
    return raw


def content_rows(rows):
    return [row for row in rows if row['role'] != 'title']


def validate_source(data):
    require(isinstance(data,dict) and set(data)==set(EXPECTED_METADATA)|{'rows'}, 'Source schema changed')
    metadata={k:data[k] for k in EXPECTED_METADATA}
    require(canonical(metadata)==canonical(EXPECTED_METADATA), 'Source metadata changed')
    rows=data['rows']
    require(isinstance(rows,list) and len(rows)==115, 'Source population changed')
    total=0
    for row, expected in zip(rows,ROW_LAYOUT):
        require(isinstance(row,dict) and set(row)==set(ROW_KEYS), 'Row schema changed')
        require(all(type(row[k]) is int for k in ('ordinal','printedPage','lineInBlock')), 'Row ordinal type changed')
        require(all(isinstance(row[k],str) for k in ('id','role','block')), 'Row identity type changed')
        actual=tuple(row[k] for k in ROW_KEYS[:-1])
        require(actual==expected, 'Row order, identity or role changed')
        text=row['printedText']
        require(isinstance(text,str) and 0<len(text)<=MAX_ROW_CODEPOINTS, 'Row text length invalid')
        require(text==text.strip(' ') and '  ' not in text, 'Row spacing invalid')
        require(all(ch==' ' or (ch.isprintable() and not ch.isspace()) for ch in text), 'Nonliteral row whitespace/control')
        require(re.search(r'[A-Za-z0-9]',text.split(' ',1)[0]) is not None, 'Punctuation-only first chunk')
        total+=len(text)
    require(total<=MAX_SOURCE_CODEPOINTS, 'Source codepoint cap exceeded')
    kept=content_rows(rows)
    require(len(kept)==111 and len(rows)-len(kept)==4, 'Title exclusion changed')
    require(dict(Counter(str(r['printedPage']) for r in rows))==EXPECTED_METADATA['counts']['byPrintedPage'], 'Page population changed')
    require(dict(Counter(str(r['printedPage']) for r in kept))==EXPECTED_METADATA['counts']['nonTitleByPrintedPage'], 'Content page population changed')
    require(dict(Counter(r['role'] for r in rows))==EXPECTED_METADATA['counts']['byRole'], 'Role population changed')
    return kept


def literal_readings(kept):
    # All selection is global after title exclusion; no role/page reset.
    texts=[row['printedText'] for row in kept]
    return [
      {'id':READING_IDS[0],'selectedRowCount':len(texts),'text':' '.join(text.split(' ',1)[0] for text in texts)},
      {'id':READING_IDS[1],'selectedRowCount':len(texts[0::2]),'text':'\n'.join(texts[0::2])},
      {'id':READING_IDS[2],'selectedRowCount':len(texts[1::2]),'text':'\n'.join(texts[1::2])}]


def reading_descriptors(readings):
    return [{'id':r['id'],'selectedRowCount':r['selectedRowCount'],
      'codepoints':len(r['text']),'utf8Bytes':len(r['text'].encode('utf-8')),
      'sha256':digest(r['text'].encode('utf-8'))} for r in readings]


def text_export(readings, source_sha):
    header='KEY404 / three fixed literal readings\nSource SHA-256: '+source_sha+'\n'
    return header+'\n\n'.join('['+r['id']+']\nSelected rows: '+str(r['selectedRowCount'])+'\n'+r['text'] for r in readings)+'\n'


def validate_protocol_header(protocol, registration):
    require(isinstance(registration,str) and re.fullmatch(r'[0-9a-f]{40}',registration) is not None, 'Full registration commit required')
    require(isinstance(protocol,dict) and {'version','batchId','test','sourceHashes','scriptHashes'}<=set(protocol), 'Protocol schema changed')
    if 'registeredAtUTC' in protocol:
        stamp=protocol['registeredAtUTC']
        require(isinstance(stamp,str), 'Invalid registration metadata')
        parsed=datetime.fromisoformat(stamp.replace('Z','+00:00'))
        require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds()==0, 'Registration metadata must be UTC')
    require(type(protocol['version']) is int and protocol['version']==1 and protocol['batchId']==BATCH_ID, 'Protocol identity changed')
    require(canonical(protocol['test'])==canonical(code_definition()), 'Protocol definition changed')
    for field,paths in (('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)):
        require(isinstance(protocol[field],dict) and set(protocol[field])==set(paths), 'Protocol pin population changed')
        require(all(isinstance(h,str) and re.fullmatch(r'[0-9a-f]{64}',h) for h in protocol[field].values()), 'Invalid file pin')
    for image in EXPECTED_METADATA['sourceImages']:
        require(protocol['sourceHashes'][image['path']]==image['sha256'], 'Image pin differs from source model')
    require(protocol['sourceHashes'][REGISTER]==EXPECTED_METADATA['sourceRegister']['sha256'], 'Register pin differs from source model')


def registered_blob(registration, relative):
    require(relative in INPUTS+SCRIPTS+(PROTOCOL,), 'Unregistered blob path')
    obj=registration+':public/research/'+relative
    size=subprocess.run(['git','cat-file','-s',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(size.returncode==0 and len(size.stdout)<=20 and re.fullmatch(rb'[0-9]+\n',size.stdout), 'Registration blob missing')
    n=int(size.stdout)
    require(n<=MAX_INPUT_BYTES, 'Registered blob cap exceeded')
    data=subprocess.run(['git','cat-file','blob',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(data.returncode==0 and len(data.stdout)==n, 'Registration blob unavailable')
    return data.stdout


def verify_payloads(protocol, protocol_bytes, registration, current_reader, blob_reader):
    # Registration of the protocol itself is checked before target file opens.
    require(blob_reader(registration,PROTOCOL)==protocol_bytes, 'Protocol registration bytes differ')
    contents={}
    for field,paths in (('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)):
        for relative in paths:
            registered=blob_reader(registration,relative)
            require(len(registered)<=MAX_INPUT_BYTES, 'Registered content cap exceeded')
            require(digest(registered)==protocol[field][relative], 'Registered file pin differs')
            current=current_reader(relative)
            require(current==registered, 'Current and registered bytes differ')
            contents[relative]=current
    return contents


def validate_protocol(path, registration):
    expected=(ROOT/PROTOCOL).resolve()
    protocol_path=Path(path).expanduser().resolve(strict=True)
    require(protocol_path==expected and protocol_path.is_relative_to(ROOT), 'Fixed public protocol required')
    raw=capped_read(protocol_path,MAX_PROTOCOL_BYTES)
    protocol=load_json(raw)
    validate_protocol_header(protocol,registration)
    def current(relative):
        require(relative in INPUTS+SCRIPTS, 'Unregistered research file')
        file=(ROOT/relative).resolve(strict=True)
        require(file.is_relative_to(ROOT), 'Research file escapes root')
        return capped_read(file,MAX_INPUT_BYTES)
    contents=verify_payloads(protocol,raw,registration,current,registered_blob)
    require(contents[SCRIPTS[0]]==Path(__file__).read_bytes(), 'Executing implementation differs')
    return protocol,raw,contents


def private_output(value):
    raw=Path(value).expanduser()
    require(not raw.exists() and not raw.is_symlink(), 'Fresh private output required')
    out=raw.resolve()
    require(not any(part.lower()=='public' for part in out.parts) and
            not out.is_relative_to(ROOT.parent.parent), 'Output outside the public checkout required')
    require(out.parent.is_dir() and not out.exists(), 'Fresh private output parent required')
    return out


def private_write(path, raw):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as handle:
        handle.write(raw)


def json_bytes(value):
    return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')


def safe_result(protocol, protocol_bytes, registration, readings, started, completed, artifacts):
    descriptors=reading_descriptors(readings)
    return {'version':1,'testId':TEST_ID,'batchId':BATCH_ID,
      'status':'readings-generated-awaiting-review','startedAtUTC':started,'completedAtUTC':completed,
      'registrationCommit':registration,'protocolSha256':digest(protocol_bytes),
      'sourceHashes':deepcopy(protocol['sourceHashes']),'scriptHashes':deepcopy(protocol['scriptHashes']),
      'sourceModel':{'id':EXPECTED_METADATA['modelId'],'physicalRows':115,'titleRowsExcluded':4,
        'contentRows':111,'contentRowsByPrintedPage':{'108':7,'109':41,'110':29,'111':34},
        'issueNumber':None,'publicationDate':None,'eligibility':'unverified-conditional',
        'originalTypesettingBytesRecovered':False},
      'scopeComplete':True,'readingsGenerated':True,'semanticReviewComplete':False,
      'counts':{'readings':3,'selectedRows':[111,56,55],'submittedCodepoints':sum(d['codepoints'] for d in descriptors)},
      'readingDescriptors':descriptors,'privateArtifactIntegrity':artifacts,
      'activity':{'variantsBeyondRegisteredReadings':0,'keyFormatChecks':0,'checksumChecks':0,
        'wordlistFilters':0,'proseToKeyHashes':0,'seedDerivations':0,'addressDerivations':0,
        'semanticScoring':0,'networkQueries':0,'transactions':0},
      'limitations':deepcopy(DEFINITION['limitations'])}


def run(protocol_path, registration, out_value):
    started=utc()
    out=private_output(out_value)
    protocol,pbytes,files=validate_protocol(protocol_path,registration)
    kept=validate_source(load_json(files[PRIMARY]))
    readings=literal_readings(kept)
    require(len(readings)==3 and [r['selectedRowCount'] for r in readings]==[111,56,55], 'Reading population changed')
    require(sum(len(r['text']) for r in readings)<=MAX_OUTPUT_CODEPOINTS, 'Output codepoint cap exceeded')
    raw={'schemaVersion':1,'testId':TEST_ID,'sourceSha256':protocol['sourceHashes'][PRIMARY],'readings':readings}
    raw_json=json_bytes(raw)
    raw_text=text_export(readings,protocol['sourceHashes'][PRIMARY]).encode('utf-8')
    out.mkdir(mode=0o700)
    try:
        private_write(out/'READINGS.private.json',raw_json)
        private_write(out/'READINGS.private.txt',raw_text)
        artifacts={'readingsJsonSha256':digest(raw_json),'readingsTextSha256':digest(raw_text)}
        result=safe_result(protocol,pbytes,registration,readings,started,utc(),artifacts)
        private_write(out/'RESULT.json',json_bytes(result))
    except Exception:
        try:private_write(out/'FAILURE.json',json_bytes({'version':1,'testId':TEST_ID,'status':'inconclusive','scopeComplete':False,'readingsGenerated':False,'reason':'Private output write failed; no semantic conclusion.'}))
        except Exception:pass
        raise
    return result


def synthetic_source():
    source=deepcopy(EXPECTED_METADATA)
    source['rows']=[dict(zip(ROW_KEYS,layout+(f'Literal{i:03d}, Wrap-{i}',))) for i,layout in enumerate(ROW_LAYOUT,1)]
    return source


def self_test():
    checks=0
    def rejects(call):
        nonlocal checks
        try:call()
        except (ValueError,UnicodeError):checks+=1
        else:raise AssertionError('Expected rejection')
    # Hand-written oracle spans page and role changes; title exclusion is global.
    toy=[{'role':'title','printedText':'DO NOT SELECT'},
      {'role':'deck','printedPage':108,'printedText':'READ, this'},
      {'role':'body','printedPage':108,'printedText':"don't merge-"},
      {'role':'title','printedText':'ALSO EXCLUDED'},
      {'role':'attributed-quotation','printedPage':109,'printedText':'THE “Case”'},
      {'role':'facts-display','printedPage':110,'printedText':'FiAT CUCkS'},
      {'role':'name-list','printedPage':110,'printedText':'BLUE. map'},
      {'role':'work-list','printedPage':111,'printedText':'continuation— literal'},
      {'role':'closing-display','printedPage':111,'printedText':'PAGE111 now'}]
    oracle=[
      {'id':READING_IDS[0],'selectedRowCount':7,'text':"READ, don't THE FiAT BLUE. continuation— PAGE111"},
      {'id':READING_IDS[1],'selectedRowCount':4,'text':'READ, this\nTHE “Case”\nBLUE. map\nPAGE111 now'},
      {'id':READING_IDS[2],'selectedRowCount':3,'text':"don't merge-\nFiAT CUCkS\ncontinuation— literal"}]
    assert literal_readings(content_rows(toy))==oracle;checks+=1
    src=synthetic_source();kept=validate_source(src)
    assert len(kept)==111 and [len(kept[::2]),len(kept[1::2])]==[56,55];checks+=1
    assert [kept[i]['printedPage'] for i in (6,7,47,48,76,77)]==[108,109,109,110,110,111];checks+=1
    # All source roles survive except title; no source file was opened to make fixture.
    assert set(r['role'] for r in kept)==set(EXPECTED_METADATA['counts']['byRole'])-{'title'};checks+=1
    for text in ('', ' leading', 'trailing ', 'two  spaces','tab\tword','line\nword','carriage\rword','non\u00a0breaking','zero\u200bwidth','! punctuation','\u2028separator'):
        bad=deepcopy(src);bad['rows'][4]['printedText']=text;rejects(lambda b=bad:validate_source(b))
    for field,value in (('id','unexpected'),('ordinal',True),('printedPage',109),('role','title'),('block','unexpected'),('lineInBlock',0)):
        bad=deepcopy(src);bad['rows'][4][field]=value;rejects(lambda b=bad:validate_source(b))
    bad=deepcopy(src);bad['rows'].pop();rejects(lambda:validate_source(bad))
    bad=deepcopy(src);bad['rows'][4]['extra']='x';rejects(lambda:validate_source(bad))
    bad=deepcopy(src);bad['issueNumber']=25;rejects(lambda:validate_source(bad))
    bad=deepcopy(src);bad['counts']['nonTitleRows']=110;rejects(lambda:validate_source(bad))
    bad=deepcopy(src);bad['encoding']['normalization']='NFC';rejects(lambda:validate_source(bad))
    bad=deepcopy(src);bad['rows'][4]['printedText']='x'*(MAX_ROW_CODEPOINTS+1);rejects(lambda:validate_source(bad))
    rejects(lambda:load_json(b'{"a":1,"a":2}'));rejects(lambda:load_json(b'{"a":NaN}'))
    protocol={'version':1,'batchId':BATCH_ID,'test':code_definition(),
      'sourceHashes':{p:'0'*64 for p in INPUTS},'scriptHashes':{p:'1'*64 for p in SCRIPTS}}
    for image in EXPECTED_METADATA['sourceImages']:protocol['sourceHashes'][image['path']]=image['sha256']
    protocol['sourceHashes'][REGISTER]=EXPECTED_METADATA['sourceRegister']['sha256']
    registration='a'*40;validate_protocol_header(protocol,registration);checks+=1
    for field in ('sourceHashes','scriptHashes'):
        bad=deepcopy(protocol);bad[field].pop(next(iter(bad[field])));rejects(lambda b=bad:validate_protocol_header(b,registration))
        bad=deepcopy(protocol);bad[field][next(iter(bad[field]))]='invalid';rejects(lambda b=bad:validate_protocol_header(b,registration))
    rejects(lambda:validate_protocol_header(protocol,'short'))
    bad=deepcopy(protocol);bad['test']['readings'][1]['selectedRowCount']=55;rejects(lambda:validate_protocol_header(bad,registration))
    current={p:('synthetic file '+p).encode() for p in INPUTS+SCRIPTS}
    mock=deepcopy(protocol)
    for field,paths in (('sourceHashes',INPUTS),('scriptHashes',SCRIPTS)):
        for p in paths:mock[field][p]=digest(current[p])
    pbytes=b'synthetic protocol bytes';blobs={**current,PROTOCOL:pbytes};calls=[]
    def read_blob(commit,path):calls.append(path);return blobs[path]
    assert verify_payloads(mock,pbytes,registration,current.__getitem__,read_blob)==current
    assert calls[0]==PROTOCOL and len(calls)==10;checks+=1
    rejects(lambda:verify_payloads(mock,b'wrong protocol',registration,current.__getitem__,read_blob))
    damaged=dict(current);damaged[PRIMARY]=b'changed source'
    rejects(lambda:verify_payloads(mock,pbytes,registration,damaged.__getitem__,read_blob))
    readings=literal_readings(kept)
    safe=safe_result(protocol,b'protocol',registration,readings,'control-start','control-end',{'readingsJsonSha256':'2'*64,'readingsTextSha256':'3'*64})
    assert all(r['text'] not in json.dumps(safe) for r in readings)
    assert 'printedText' not in json.dumps(safe) and 'negative' not in json.dumps(safe).lower()
    assert safe['semanticReviewComplete'] is False and safe['scopeComplete'] is True;checks+=1
    with tempfile.TemporaryDirectory(prefix='key404-sand-control-') as temp:
        path=Path(temp)/'private-output';assert private_output(path)==path.resolve()
        path.mkdir(mode=0o700);private_write(path/'control.txt',b'literal control\n')
        assert (path.stat().st_mode&0o777)==0o700 and ((path/'control.txt').stat().st_mode&0o777)==0o600;checks+=1
        rejects(lambda:private_output(path))
        public=Path(temp)/'public';public.mkdir();rejects(lambda:private_output(public/'new'))
        rejects(lambda:private_output(ROOT.parent.parent/'synthetic-private-control-output'))
        link=Path(temp)/'link';link.symlink_to(path,target_is_directory=True);rejects(lambda:private_output(link))
        try:private_write(path/'control.txt',b'replace')
        except FileExistsError:checks+=1
        else:raise AssertionError('Existing private artifact overwritten')
    return {'version':1,'testId':TEST_ID,'passed':True,'checks':checks,
      'controls':'synthetic only; hand-written parity/punctuation oracle,115-row metadata fixture,source/protocol/registration/privacy/output guards',
      'targetSourceOpened':False,'targetReadingsGenerated':False,'keyFormatChecks':0,
      'addressDerivations':0,'networkQueries':0}


class QuietParser(argparse.ArgumentParser):
    def error(self,message):
        raise ValueError('Invalid command arguments')


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    known=('--definition','--self-test','--run','--protocol','--registration-commit','--out')
    require(all(argv.count(flag)<=1 for flag in known), 'Duplicate command argument')
    parser=QuietParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--definition',action='store_true');action.add_argument('--self-test',action='store_true');action.add_argument('--run',action='store_true')
    parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out')
    args=parser.parse_args(argv)
    extras=(args.protocol,args.registration_commit,args.out)
    if not args.run:require(not any(extras), 'Run-only arguments require run')
    if args.definition:return code_definition()
    if args.self_test:return self_test()
    require(all(extras), 'Protocol, registration and private output required')
    return run(args.protocol,args.registration_commit,args.out)


if __name__=='__main__':
    os.umask(0o077)
    try:
        result=main()
        print(json.dumps(result,ensure_ascii=False,allow_nan=False))
    except Exception:
        print(json.dumps({'version':1,'testId':TEST_ID,'status':'inconclusive','scopeComplete':False,
          'readingsGenerated':False,'error':'Validation or execution failed; no semantic conclusion.'}),file=sys.stderr)
        raise SystemExit(1)
