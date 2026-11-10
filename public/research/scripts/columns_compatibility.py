#!/usr/bin/env python3
"""One four-cohort recorded-output compatibility replay; Python3.9+ stdlib.

Public-input reconstruction occurs only after fixed public Git-byte gates.
Every original raw artifact identity must pass before any candidate validation.
Raw output stays outside the whole site checkout, in fresh0700/0600 storage.
--self-test uses only synthetic/published controls, never target source data.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
import gzip,hashlib,io,json,os,re,stat,subprocess,sys,tempfile,types
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve()
ROOT=(HERE.parent.parent if (HERE.parent/'batch20_common.py').is_file() else HERE.parents[3]/'site/public/research').resolve()
COMMON='scripts/batch20_common.py'
CORE='scripts/batch20_supplemental_formats.py'
ENGLISH='scripts/batch20_support/english.txt'
CONTROLS='scripts/batch20_support/controls.json'
FORMATS4=('extended_private','bip38','address','sec_public')
FORMATS8=('wif','minikey','hex64','bip39')+FORMATS4
DEFINITION={'id': 'columns-fixed-output-compatibility', 'title': 'One fixed four-cohort column-output compatibility matrix', 'family': 'fixed-artifact-format-compatibility', 'branchId': 'text-lines', 'inputPaths': ['analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.json', 'analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.md', 'analysis_outputs/continuation_20261110/funky_sand_direct/RESULT.json', 'analysis_outputs/continuation_20261110/funky_sand_direct/RESULT.md', 'analysis_outputs/continuation_20261110/funky_sand_direct/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/funky_sand_direct/EXECUTION.json', 'scripts/funky_sand_direct.py', 'scripts/verify_funky_sand_direct.py', 'sources/funky-upheaval/physical-lines.json', 'sources/funky-upheaval/SOURCE_REGISTER.json', 'sources/funky-upheaval/pages/108.jpg', 'sources/funky-upheaval/pages/109.jpg', 'sources/funky-upheaval/pages/110.jpg', 'sources/funky-upheaval/pages/111.jpg', 'analysis_outputs/continuation_20261109/george_sand_research.md', 'analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.json', 'analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.md', 'analysis_outputs/continuation_20261110/issue26_firstwords/RESULT.json', 'analysis_outputs/continuation_20261110/issue26_firstwords/RESULT.md', 'analysis_outputs/continuation_20261110/issue26_firstwords/INDEPENDENT_CHECK.json', 'scripts/batch20_common.py', 'scripts/batch20_geometry.py', 'scripts/issue26_firstword_probe.py', 'scripts/verify_firstword_readings.py', 'sources/issue26/issue26-source.json', 'sources/issue26/page_03.jpg', 'sources/issue26/page_04.jpg', 'sources/issue26/page_05.jpg', 'scripts/batch20_support/english.txt', 'scripts/batch20_support/controls.json', 'analysis_outputs/continuation_20261110/issue26_firstwords/READINGS.jsonl.gz', 'analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.json', 'analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.md', 'analysis_outputs/continuation_20261110/issue27_stride12/RESULT.json', 'analysis_outputs/continuation_20261110/issue27_stride12/RESULT.md', 'analysis_outputs/continuation_20261110/issue27_stride12/INDEPENDENT_CHECK.json', 'scripts/issue27_stride12.py', 'scripts/verify_issue27_saved.py', 'scripts/verify_issue27_stride12.py', 'analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json', 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_01.jpg', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_02.jpg', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_03.jpg', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_04.jpg', 'analysis_outputs/continuation_20261110/issue27_stride12/POLICY_PROPOSAL.json', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/PROTOCOL.json', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/PROTOCOL.md', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/RESULT.json', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/RESULT.md', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/INDEPENDENT_CHECK.json', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/INDEPENDENT_CHECKER_PIN.json', 'scripts/issue27_stream_coverage.py', 'analysis_outputs/continuation_20261109/george_sand_issue27/analyze_printed_lines.py', 'analysis_outputs/continuation_20261109/george_sand_issue27/REPORT.md', 'analysis_outputs/continuation_20261109/george_sand_issue27/regions.json', 'analysis_outputs/continuation_20261109/george_sand_issue27/vision_raw.json'], 'implementationPaths': ['scripts/columns_compatibility.py', 'scripts/verify_columns_compatibility.py', 'scripts/batch20_supplemental_formats.py', 'scripts/verify_batch20_supplemental.py', 'scripts/batch20_common.py'], 'protocolPath': 'analysis_outputs/continuation_20261110/columns_compatibility/PROTOCOL.json', 'auditMetadataSha256': '3403f13aa4e1503f8754fe7bcbf3ae2d7b89ab85f4f0e98f8ae75ef2e2d6ea68', 'contractSha256': '6f23a8e475e27ab902e15401b85ed866d5fbacff31d501d6bb59ef5a46c5635f', 'sourceExpectations': [{'id': 'funky-sand-direct', 'readingFile': 'FUNKY_READINGS.private.json', 'rawBytes': 8272, 'rawSha256': '033513555f835cdec0193732751118a6ca0a09b9558537edf323c46658d15c61', 'rawSchema': 'funky-json', 'recordKeys': ['id', 'selectedRowCount', 'text'], 'recordCount': 3, 'uniqueTextCount': 3, 'emptyTexts': 0, 'minimumTextCodepoints': 703, 'maximumTextCodepoints': 3541, 'totalTextCodepoints': 7689, 'expectedForms': None, 'maximumForms': 6, 'commonFormats': ['wif', 'minikey', 'hex64', 'bip39', 'extended_private', 'bip38', 'address', 'sec_public'], 'minikey26': True, 'originalReadingReconstruction': True, 'artifactPinAuthority': 'prior-public-execution', 'strictKnown': None}, {'id': 'issue26-first-words', 'readingFile': 'ISSUE26_READINGS.private.jsonl', 'rawBytes': 25477680, 'rawSha256': '53e24a093652064a7965b57a9c2195e88f555b6e13f2d83b9f02d96958edf054', 'rawSchema': 'jsonl', 'recordKeys': ['STOPPolicy', 'characterOrder', 'id', 'parityOrigin', 'phase', 'population', 'projection', 'rowOrder', 'selectedRowIds', 'surface', 'text', 'tokenSourceIds', 'unit'], 'recordCount': 39744, 'uniqueTextCount': 1746, 'emptyTexts': 10752, 'minimumTextCodepoints': 0, 'maximumTextCodepoints': 765, 'totalTextCodepoints': 934320, 'expectedForms': 1746, 'maximumForms': 1746, 'commonFormats': [], 'minikey26': True, 'originalReadingReconstruction': False, 'artifactPinAuthority': 'public-gzip-plus-registered-decompressed-identity', 'strictKnown': None}, {'id': 'issue27-body-stride12', 'readingFile': 'STRIDE_READINGS.private.jsonl', 'rawBytes': 46984, 'rawSha256': 'b2b33f3eb8440cdf3fa949355b59f443e8aa545b8809500b45d406b364a93225', 'rawSchema': 'jsonl', 'recordKeys': ['direction', 'id', 'phase', 'projection', 'selectedTokenCount', 'sourceCompleteForProjection', 'text', 'uncertainSelectedTokens'], 'recordCount': 72, 'uniqueTextCount': 72, 'emptyTexts': 0, 'minimumTextCodepoints': 168, 'maximumTextCodepoints': 1027, 'totalTextCodepoints': 32038, 'expectedForms': 96, 'maximumForms': 96, 'commonFormats': ['extended_private', 'bip38', 'address', 'sec_public'], 'minikey26': True, 'originalReadingReconstruction': True, 'artifactPinAuthority': 'newly-registered-original-artifact-identity', 'strictKnown': {'recordCount': 60, 'formCount': 78, 'sourceAffectedRecords': 12, 'projectionCounts': {'words': 18, 'initials': 18, 'finals': 24}, 'nestedInNominal': True, 'physicalSourceComplete': False}}, {'id': 'issue27-frozen-stream-coverage', 'readingFile': 'FROZEN_READINGS.private.jsonl', 'rawBytes': 2044672, 'rawSha256': 'f397d4932969dd6282dd8b2f1562ec0cbec7165a19a7038aecf131b4a3789030', 'rawSchema': 'jsonl', 'recordKeys': ['characterOrder', 'id', 'sourceLabel', 'text'], 'recordCount': 3880, 'uniqueTextCount': 2133, 'emptyTexts': 0, 'minimumTextCodepoints': 1, 'maximumTextCodepoints': 13698, 'totalTextCodepoints': 1329528, 'expectedForms': 3709, 'maximumForms': 3709, 'commonFormats': ['extended_private', 'bip38', 'address', 'sec_public'], 'minikey26': True, 'originalReadingReconstruction': True, 'artifactPinAuthority': 'newly-registered-original-artifact-identity', 'strictKnown': None}], 'fixedSourceHashes': {'analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.json': '26a681bc40ddb6a1d9d471cf7e70f7f7c3c0c6a588b2f3400a4c083a1e59f15e', 'analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.md': '824bd796a124ee94e49c3feb50daa370c0c8b42d2bfc62dab5015ba00ccfde86', 'analysis_outputs/continuation_20261110/funky_sand_direct/RESULT.json': 'c260981ee58f2575951fbf1c51c197e78b25c4009ff79f1be38eac9e59ed3c89', 'analysis_outputs/continuation_20261110/funky_sand_direct/RESULT.md': 'b101fef0e977bc5ca0a4afc6c077e3be17d021544b1b55af668fdee4e639a4d3', 'analysis_outputs/continuation_20261110/funky_sand_direct/INDEPENDENT_CHECK.json': 'a30f75596e51e3b5635f1ce879da986f13f1eef00e0e91d4a7d6ef9688ce8a7b', 'analysis_outputs/continuation_20261110/funky_sand_direct/EXECUTION.json': 'dcc173a36d0e49bf01cfa2ced4497b726822296e93e004e19d8e0c0f7c3afa0f', 'scripts/funky_sand_direct.py': '4eec6a4ce0ab8466875ddfc8568e1a38debf767a8d619eb5d8d1809ddaf7c8b1', 'scripts/verify_funky_sand_direct.py': '7e7c5c9c2234b4934665b287848d6383d787949935ff99248c11f2f2083163d5', 'sources/funky-upheaval/physical-lines.json': '12ef2d85578b89a164a109c7f5045e9fd28b88fd7ce5c58e30632e242a60eb11', 'sources/funky-upheaval/SOURCE_REGISTER.json': 'fb756e12d376af208c619b6e46ea17366df9d90214992e53673cc10fda106b2f', 'sources/funky-upheaval/pages/108.jpg': '1557e2974d4f04579aea3015b6f885f35b2b966f06ac5944d39c70439ee8fb6c', 'sources/funky-upheaval/pages/109.jpg': 'bc12df605c993055ef761f27b413d9c8bc781d70c83533a7d9ae119034554814', 'sources/funky-upheaval/pages/110.jpg': '2f5cbca356f01887acf84cabcf6d5d8b5a5ec56547ae88329fd7de923a84601f', 'sources/funky-upheaval/pages/111.jpg': '40092c66f44296988a7f397563915e30f3926a6e265c512aa61b01057e970f50', 'analysis_outputs/continuation_20261109/george_sand_research.md': '8a619cf8c6ab246fc4dc1c2086648e5d245bfa1ca751011febcbf74be42dd1ff', 'analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.json': '8ec335eae647d695f14f0024027d281975265d02ba11eb3811ad8480f2255d3d', 'analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.md': 'cce61a4e76206c0e488922bc188e2ffbc82c6df115210457fae26b4924dae6ac', 'analysis_outputs/continuation_20261110/issue26_firstwords/RESULT.json': '11d77df1a463382011ca6c17b6ecc670f5e1639e833313b0e09d9166038590a0', 'analysis_outputs/continuation_20261110/issue26_firstwords/RESULT.md': 'f8238669dc2f6d89a34849663dcf62bc2722fbf42880755f76d4c05f63232105', 'analysis_outputs/continuation_20261110/issue26_firstwords/INDEPENDENT_CHECK.json': 'c7c3dbfe083c49b8db87c40fa8dd90913c5fbad6f8393db4e929f68ffbaea3ea', 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d', 'scripts/batch20_geometry.py': 'e7786acc472fa3f7a294fe6391e74bd6f8840017e30d9f54941544019dbafb9a', 'scripts/issue26_firstword_probe.py': '79b3a93d38760208ffc728e1e9ada6dcefd430f1ae155ca467aa5d34e8c04b56', 'scripts/verify_firstword_readings.py': '30dc5a126c666e65a7b4379155742d807b1b061142ff938c59b66cfc1ef46170', 'sources/issue26/issue26-source.json': '1ff7a0a26c1e91fb2bfef9817693419979fdf39381d4124c2c9e5e7739f73c67', 'sources/issue26/page_03.jpg': 'bd88ecc69fe5215aaf370a97520cb7668d9b67c43395f4d36544cd3b5a6081f7', 'sources/issue26/page_04.jpg': 'f7eaedb88bf75249c45a61e5abd9bfa7cc5c59c472d63c84aa30bad7334c75da', 'sources/issue26/page_05.jpg': 'de13717ccc0d51fa6442ab1f6c8591162d1b3db2a910e36c2cdfedeedb89250d', 'scripts/batch20_support/english.txt': '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda', 'scripts/batch20_support/controls.json': 'd37bf54e78d408453939259dc7ef1a60f54e32bedadd0cd5de903f8d41fb334b', 'analysis_outputs/continuation_20261110/issue26_firstwords/READINGS.jsonl.gz': '83fe1bbf4fbe7e4f93a82b136445d314225816943e41e6c027ded89939e7e98a', 'analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.json': '6e5a4bf93303c29e4447c0e18c22f3e844509c30b9c6e3ee4202df2aa6c3ca69', 'analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.md': 'da0312f8741893ff18aa043012e4b0a7f9fb590b4d658e0c7a267ebf235dbc23', 'analysis_outputs/continuation_20261110/issue27_stride12/RESULT.json': '102d1f0459b371292250080cb72692db187a40bae204937673c0be18b0e286d1', 'analysis_outputs/continuation_20261110/issue27_stride12/RESULT.md': '615f088b8c4c6cb40d89e35d2cabf24aecf6ee59e15bd7c4c426f745fab56659', 'analysis_outputs/continuation_20261110/issue27_stride12/INDEPENDENT_CHECK.json': '43870042280d9cecf78fc48e6e9fe8e7a816e937e0fe7f695478d38119e00347', 'scripts/issue27_stride12.py': '84a061444a73fbedc14f8068f8d3cce1fb7ef990b4bef65181e78f234dcbfd01', 'scripts/verify_issue27_saved.py': '97cace8ee5f9b2707cc1344c08e46e068db327edc504a8625fb825481261422b', 'scripts/verify_issue27_stride12.py': '1f482648945fe1508a211628ba7ec826c23cdbeed317bbf05426595b5be1ebae', 'analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json': '783cc6676edf9b135d1eeff04d8bf8636088c1334f9e983f0d9f07dc579bff27', 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json': 'f5f441345ebe411ee769cdcb624c0717a2b4f790b7eadc50d10dc12d37da07bb', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_01.jpg': 'd4cca9f4326ba21a959551e8537596846bccdea42efe37f463506cd2d423fb8c', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_02.jpg': 'e18e02e521444c9ea760c6e1d80a39bbee08d65a7839e970629ab81b4fd83610', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_03.jpg': 'b7f120860b1a76aa6ba97c836bb56388477ee8878665d75414098f9b8a38a1b5', 'analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_04.jpg': '60da7f7ed64764e8c9bb347bce163eb2f8dc4c4ad20abbd00182bced3ad3343a', 'analysis_outputs/continuation_20261110/issue27_stride12/POLICY_PROPOSAL.json': '5c6d4a7b406f99515b1bb16c7f7874df6444c64c3be2e6a32c0798ac08e0d1e5', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/PROTOCOL.json': '0f4699ac1bddbc661c7b583fc638f0adbcfc98e7372d604bfed81b770a9a0343', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/PROTOCOL.md': 'c91e8bf8660a430da344ae5371e2fc122cc423f836f0c321dc646059fcc56d45', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/RESULT.json': '6cbe0570fc7e03e05eb1369ed98e5456d193c2c8527b7c47fbf83fbf69b059ba', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/RESULT.md': 'a3493bff6d92f2c872bd9bfe3f1d8303f08c5f95ee461a2b32fd5fa040a4ec2a', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/INDEPENDENT_CHECK.json': '5fc0254fa4b750472b264690f2aa302f1796d05adea8ab324c9ed7a4e526689b', 'analysis_outputs/continuation_20261110/issue27_stream_coverage/INDEPENDENT_CHECKER_PIN.json': '229f243de559dd6d55d2ae4bdfd398d2a88710cea4055375e48717f202e7ab8d', 'scripts/issue27_stream_coverage.py': '7e045510592b19bc1399ca896cd19d601f3a9fc6fee8e8306a1d4115cf812e61', 'analysis_outputs/continuation_20261109/george_sand_issue27/analyze_printed_lines.py': '78108c23acf33596985b674cc89a033efe19ba7599b8fde521f7ea5efe837184', 'analysis_outputs/continuation_20261109/george_sand_issue27/REPORT.md': '76c23544624cd5e81d18deadf83113135c9ce425c181fd43e60d11a677abb74f', 'analysis_outputs/continuation_20261109/george_sand_issue27/regions.json': 'faabd124ade630330beee9ed99c376af65512172f0a3eeed551f865d769efce9', 'analysis_outputs/continuation_20261109/george_sand_issue27/vision_raw.json': 'c6cdf7de5fa6c34e33c0eba25b6727057a32f953ae55d428d3b77292265c0df3'}, 'fixedDependencyHashes': {'scripts/batch20_supplemental_formats.py': '385524773ef0c20a2af1858bbf1d1f15cb45fd47fdf08627b0b97d2dda2754ac', 'scripts/verify_batch20_supplemental.py': 'a4bf930523eb29c0da942439eb6005514fc60d0dfb4f6deede2171380bd4389c', 'scripts/batch20_common.py': '48328a24ae0f2b136a1aa18f273c1a507efaf90153277a6b3ab1bc8ff97e590d'}, 'publicMaterialization': {'funkySource': 'sources/funky-upheaval/physical-lines.json', 'funkyProducer': 'scripts/funky_sand_direct.py', 'strideBody': 'analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json', 'parent': 'analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json', 'strideProtocol': 'analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.json', 'strideProducer': 'scripts/issue27_stride12.py', 'frozenProducer': 'scripts/issue27_stream_coverage.py', 'issue26Gzip': 'analysis_outputs/continuation_20261110/issue26_firstwords/READINGS.jsonl.gz', 'issue26CompressedBytes': 654565, 'issue26CompressedSha256': '83fe1bbf4fbe7e4f93a82b136445d314225816943e41e6c027ded89939e7e98a', 'FunkySerializer': 'Exact old envelope insertion order schemaVersion,testId,sourceSha256,readings; producer.json_bytes indent2/ensure_asciiFalse/allow_nanFalse +LF UTF8.', 'JSONLSerializer': 'Original record dict insertion order, json.dumps(record,ensure_ascii=True) +LF, binary UTF8.', 'validationBarrier': 'All four materialized/decompressed artifacts must pass exact raw byte count and registered SHA before ANY candidate/form validator; counts/schema then forms and gates.', 'oldProducerCallsAllowed': ['Funky validate_source/literal_readings/json_bytes', 'stride validate_source/make_tokens/make_readings', 'frozen validate_source/submitted_readings'], 'forbiddenOldCalls': ['run', 'evaluate', 'self_test', 'legacy whole CLI or loader'], 'directCompileVerifiedSource': True}, 'formsPolicy': 'Per cohort sorted unique exact texts union Unicode-whitespace-only compaction; empty retained. Funky surface newly registered <=6 forms; others old fixed conventions. Issue26 MUST prove exact set equals exact+compact union directly after registration, both cardinality1746. No global union.', 'caps': {'registeredBlobBytes': 20000000, 'sourceJsonBytes': 2000000, 'protocolBytes': 1000000, 'gzipCompressedBytes': 1000000, 'decompressedBytes': 26000000, 'jsonlLineBytes': 131072, 'rawArtifactBytes': 30000000, 'privateArtifactBytes': 64000000, 'totalPrivateOutputBytes': 128000000, 'maximumRecordCount': 39744, 'maximumTextCodepoints': 15000, 'totalTextCodepoints': 2400000, 'totalFormCodepoints': 6000000, 'shapeOccurrencesPerCohort': 1000000, 'uniqueShapesPerCohort': 500000}, 'outputPolicy': {'rawArtifacts': ['FUNKY_READINGS.private.json', 'ISSUE26_READINGS.private.jsonl', 'STRIDE_READINGS.private.jsonl', 'FROZEN_READINGS.private.jsonl', 'FORMS.private.json', 'VALIDATION.private.json'], 'rawOutsideEntireSiteCheckout': True, 'directoryMode': '0700', 'fileMode': '0600', 'publicReceipt': 'Per-cohort aggregate counts/declared scope and whole-artifact integrity only; no raw values, fingerprints or candidate/source associations.', 'semanticConclusionComputed': False}, 'registrationGate': 'Fixed public paths, full40hex actual localGitcommit; all source/code/protocol currentbytes must equal registeredblobs before any targetparse or original-reading reconstruction. All4 exact rawartifact byte identities must pass before any candidatevalidation. Operator separately verifies prior remote publication.', 'activityBoundary': {'originalReadingReconstructionCohorts': 3, 'gzipArtifactsDecompressed': 1, 'newSelectors': 0, 'newReversalVariants': 0, 'ocrReruns': 0, 'sourceRepairs': 0, 'bareMinikeyScalarHashes': 0, 'proseToKeyHashes': 0, 'scalarDerivations': 0, 'seedDerivations': 0, 'addressDerivations': 0, 'childKeyDerivations': 0, 'networkQueries': 0, 'historyQueries': 0, 'transactions': 0, 'legacyValidatorsOutsideFunky': 0}, 'limitations': ['One compatibility matrix over four correlated recorded-output cohorts, not four new theories or a global independent-trial count.', 'Funky first8shared-format coverage and26gate includes a newly registered <=6 exact/whitespace-only form surface; issue/date and December eligibility remain unverified.', 'Issue26 only26 gate; addedfour not repeated. Direct exact/compact set equality is checked after registration. Firstword proof does not repair23 blurred lineendings or recover its missingPDF.', 'Stride60source-known records/78forms are nested within72/96, preserving three uncertain prefixes; no complete physical-source exclusion.', 'Historical3880wrapper reproduces existing1940exact/reversed rules on old79–81OCRmodel; it adds no opener/source repairs and does not claim priorpublic rawEXEC pins.', 'Funky rawJSON identity has a priorpublic executionpin; stride/frozen rawJSONL identities are newly registered for this replay.', 'Four-format validators are shared and reused; separate frozen form/26 implementations do not establish independent mathematics for sharedvalidators.', 'No semantic recognition, scalar/seed/address derivation, funding/historyquery, wallet activity or whole-puzzle exclusion is computed; puzzle remains unsolved.'], 'nestedSubsetPolicy': 'Stride60whole-record/78form subset uses only shape enumeration and cached nominal validation/positive membership. No repeated validator/checksum/fingerprint; actual validationCalls/checksumCalls0, explicitly derived status/proof. Nested, not independent observations.'}
TEST_ID=DEFINITION['id']
BATCH_ID='keiser-columns-fixed-output-compatibility-20261110'
PROTOCOL=DEFINITION['protocolPath']
SOURCE_PINS=DEFINITION['fixedSourceHashes']
INPUTS=tuple(SOURCE_PINS)
SCRIPTS=tuple(DEFINITION['implementationPaths'])
FIXED_CODE_PINS=DEFINITION['fixedDependencyHashes']
CAPS=DEFINITION['caps']
COHORTS=tuple(DEFINITION['sourceExpectations'])
MATERIAL=DEFINITION['publicMaterialization']
READING_FILES=tuple(c['readingFile'] for c in COHORTS)
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

def json_bytes(value):
    return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')

def capped_read(path, limit):
    require(path.is_file() and path.stat().st_size <= limit, 'File byte cap exceeded')
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, 'File grew beyond byte cap')
    return raw

def private_output(value):
    raw=Path(value).expanduser();require(not raw.exists() and not raw.is_symlink(),'Fresh private output required')
    out=raw.resolve();require(not any(p.casefold()=='public' for p in out.parts) and not out.is_relative_to(ROOT.parent.parent),'Output outside entire site checkout required')
    require(out.parent.is_dir() and stat.S_IMODE(out.parent.stat().st_mode)==0o700,'Private0700 output parent required')
    return out

def private_write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.fchmod(fd,0o600)
    with os.fdopen(fd,'wb') as handle:handle.write(raw)

def code_definition():return deepcopy(DEFINITION)

def registered_blob(registration,relative):
    require(relative in set(INPUTS+SCRIPTS+(PROTOCOL,)),'Unregistered blob path')
    obj=registration+':public/research/'+relative
    size=subprocess.run(['git','cat-file','-s',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(size.returncode==0 and re.fullmatch(rb'[0-9]+\n',size.stdout) and len(size.stdout)<=20,'Registered blob missing')
    count=int(size.stdout);require(count<=CAPS['registeredBlobBytes'],'Registered blob cap exceeded')
    data=subprocess.run(['git','cat-file','blob',obj],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(data.returncode==0 and len(data.stdout)==count,'Registered blob unavailable')
    return data.stdout

def require_commit(registration,runner=None):
    runner=subprocess.run if runner is None else runner
    kind=runner(['git','cat-file','-t',registration],cwd=ROOT,capture_output=True,check=False,timeout=30)
    require(kind.returncode==0 and kind.stdout==b'commit\n','Actual Git commit object required')

def verify_payloads(protocol,pbytes,registration,current_reader,blob_reader):
    # Protocol byte proof comes before any target file opens.
    require(blob_reader(registration,PROTOCOL)==pbytes,'Protocol registered bytes differ')
    files={};pins={**protocol['sourceHashes'],**protocol['scriptHashes']}
    for relative in dict.fromkeys(INPUTS+SCRIPTS):
        registered=blob_reader(registration,relative)
        require(len(registered)<=CAPS['registeredBlobBytes'] and digest(registered)==pins[relative],'Registered content pin differs')
        current=current_reader(relative);require(current==registered,'Current bytes differ from registration')
        files[relative]=current
    return files

def validate_protocol(path,registration):
    require(HERE==(ROOT/SCRIPTS[0]).resolve(),'Actual run requires fixed public script')
    path=Path(path).expanduser().resolve(strict=True)
    require(path==(ROOT/PROTOCOL).resolve() and path.is_relative_to(ROOT),'Fixed public protocol required')
    pbytes=capped_read(path,CAPS['protocolBytes']);protocol=load_json(pbytes);validate_protocol_header(protocol,registration)
    require_commit(registration)
    def current(relative):
        file=(ROOT/relative).resolve(strict=True);require(file.is_relative_to(ROOT),'Research path escape')
        return capped_read(file,CAPS['sourceJsonBytes'] if relative in INPUTS else CAPS['registeredBlobBytes'])
    files=verify_payloads(protocol,pbytes,registration,current,registered_blob)
    require(files[SCRIPTS[0]]==HERE.read_bytes(),'Executing bytes differ')
    return protocol,pbytes,files

def validate_protocol_header(protocol,registration):
    require(isinstance(registration,str) and re.fullmatch('[0-9a-f]{40}',registration),'Full40hex registration required')
    require(isinstance(protocol,dict) and {'version','batchId','test','sourceHashes','scriptHashes'}<=set(protocol),'Protocol schema changed')
    require(type(protocol['version']) is int and protocol['version']==1 and protocol['batchId']==BATCH_ID,'Protocol identity changed')
    require(canonical(protocol['test'])==canonical(DEFINITION),'Protocol definition changed')
    require(protocol['sourceHashes']==SOURCE_PINS,'Exact public witness population required')
    require(isinstance(protocol['scriptHashes'],dict) and set(protocol['scriptHashes'])==set(SCRIPTS),'Five script pins required')
    require(all(isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) for h in protocol['scriptHashes'].values()),'Invalid script pin')
    require(all(protocol['scriptHashes'][p]==h for p,h in FIXED_CODE_PINS.items()),'Frozen dependency pin changed')
    if 'registeredAtUTC' in protocol:
        stamp=datetime.fromisoformat(protocol['registeredAtUTC'].replace('Z','+00:00'))
        require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds()==0,'Registration metadata must be UTC')


def contained_file(relative,root=ROOT):
    require(isinstance(relative,str) and not Path(relative).is_absolute() and '..' not in Path(relative).parts,'Relative research path required')
    path=(root/relative).resolve(strict=True)
    require(path.is_relative_to(root.resolve()) and path.is_file(),'Pinned file path escape')
    return path


def compiled_module(relative,files=None,common=None):
    pin=SOURCE_PINS.get(relative,FIXED_CODE_PINS.get(relative))
    require(pin is not None,'Unpinned module')
    path=contained_file(relative);raw=files[relative] if files is not None else capped_read(path,CAPS['registeredBlobBytes'])
    require(digest(raw)==pin,'Module byte pin changed')
    module=types.ModuleType('columns_frozen_'+Path(relative).stem);module.__file__=str(path)
    previous_path=list(sys.path);previous_common=sys.modules.get('batch20_common')
    if common is not None:sys.modules['batch20_common']=common
    try:exec(compile(raw,str(path),'exec'),module.__dict__)
    finally:
        sys.path[:]=previous_path
        if common is not None:
            if previous_common is None:sys.modules.pop('batch20_common',None)
            else:sys.modules['batch20_common']=previous_common
    return module


def load_engines(files=None):
    for relative in (ENGLISH,CONTROLS):
        path=contained_file(relative)
        raw=files[relative] if files is not None else capped_read(path,CAPS['sourceJsonBytes'])
        require(digest(raw)==SOURCE_PINS[relative],'Support byte pin changed')
    common=compiled_module(COMMON,files)
    core=compiled_module(CORE,files,common)
    require(tuple(common.ALL_FORMATS)==FORMATS8 and tuple(core.FORMATS)==FORMATS4,'Frozen format list changed')
    return core,common


def private_stream(path,chunks,limit):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.fchmod(fd,0o600)
    count=0;mark=hashlib.sha256()
    with os.fdopen(fd,'wb') as handle:
        for chunk in chunks:
            require(isinstance(chunk,bytes),'Binary artifact chunk required');count+=len(chunk)
            require(count<=limit,'Artifact byte cap exceeded')
            handle.write(chunk);mark.update(chunk)
    return count,mark.hexdigest()


def jsonl_chunks(records):
    for record in records:
        raw=(json.dumps(record,ensure_ascii=True)+'\n').encode('utf-8')
        require(len(raw)<=CAPS['jsonlLineBytes'],'JSONL line cap exceeded')
        yield raw


def bounded_gzip_chunks(compressed):
    require(len(compressed)<=CAPS['gzipCompressedBytes'],'Compressed byte cap exceeded')
    total=0
    with gzip.GzipFile(fileobj=io.BytesIO(compressed),mode='rb') as handle:
        while True:
            raw=handle.read(65536)
            if not raw:break
            total+=len(raw);require(total<=CAPS['decompressedBytes'],'Decompressed byte cap exceeded')
            yield raw


def verify_original_identities(identities,cohorts=COHORTS):
    require(set(identities)=={c['readingFile'] for c in cohorts},'Original artifact population changed')
    for cohort in cohorts:
        require(identities[cohort['readingFile']]==(cohort['rawBytes'],cohort['rawSha256']),'Original artifact byte identity changed')


def reconstruct_originals(files,out,common):
    # These are only frozen source-to-record functions, never old run/evaluate/self_test.
    parent=load_json(files[MATERIAL['parent']])
    funky=compiled_module(MATERIAL['funkyProducer'],files,common)
    kept=funky.validate_source(load_json(files[MATERIAL['funkySource']]))
    readings=funky.literal_readings(kept)
    envelope={'schemaVersion':1,'testId':funky.TEST_ID,'sourceSha256':SOURCE_PINS[MATERIAL['funkySource']],'readings':readings}
    raw=funky.json_bytes(envelope)
    identities={COHORTS[0]['readingFile']:private_stream(out/COHORTS[0]['readingFile'],[raw],CAPS['rawArtifactBytes'])}
    compressed=files[MATERIAL['issue26Gzip']]
    require(len(compressed)==MATERIAL['issue26CompressedBytes'] and digest(compressed)==MATERIAL['issue26CompressedSha256'],'Issue26 compressed identity changed')
    identities[COHORTS[1]['readingFile']]=private_stream(out/COHORTS[1]['readingFile'],bounded_gzip_chunks(compressed),CAPS['rawArtifactBytes'])
    stride=compiled_module(MATERIAL['strideProducer'],files,common)
    old_protocol=load_json(files[MATERIAL['strideProtocol']])
    rows=stride.validate_source(load_json(files[MATERIAL['strideBody']]),parent,old_protocol['sourceExpectations'],old_protocol['sourceHashes'])
    tokens=stride.make_tokens(rows);require(len(tokens)==2018,'Frozen stride token population changed')
    readings=stride.make_readings(tokens)
    identities[COHORTS[2]['readingFile']]=private_stream(out/COHORTS[2]['readingFile'],jsonl_chunks(readings),CAPS['rawArtifactBytes'])
    frozen=compiled_module(MATERIAL['frozenProducer'],files,common)
    streams=frozen.validate_source(parent)
    identities[COHORTS[3]['readingFile']]=private_stream(out/COHORTS[3]['readingFile'],jsonl_chunks(frozen.submitted_readings(streams)),CAPS['rawArtifactBytes'])
    # Global barrier: no target form or candidate validator before all4 exact identities.
    verify_original_identities(identities)
    return identities


def reading_records(path,cohort):
    if cohort['rawSchema']=='funky-json':
        data=load_json(capped_read(path,CAPS['rawArtifactBytes']))
        require(isinstance(data,dict) and set(data)=={'schemaVersion','testId','sourceSha256','readings'} and type(data['schemaVersion']) is int and data['schemaVersion']==1,'Funky original envelope changed')
        require(data['testId']=='funky-sand-direct' and data['sourceSha256']==SOURCE_PINS[MATERIAL['funkySource']] and isinstance(data['readings'],list),'Funky original identity changed')
        yield from data['readings']
    else:
        with path.open('rb') as handle:
            while True:
                raw=handle.readline(CAPS['jsonlLineBytes']+1)
                if not raw:break
                require(len(raw)<=CAPS['jsonlLineBytes'] and raw.endswith(b'\n'),'JSONL line cap/ending changed')
                yield load_json(raw)


def analyze_records(records,cohort):
    count=empty=total=0;minimum=None;maximum=0;texts=set();ids=set();known_count=0;known_texts=set();known_projections=Counter();orders=Counter()
    for record in records:
        count+=1;require(count<=CAPS['maximumRecordCount'],'Record cap exceeded')
        require(isinstance(record,dict) and set(record)==set(cohort['recordKeys']) and isinstance(record.get('id'),str) and isinstance(record.get('text'),str),'Original record schema changed')
        require(record['id'] not in ids,'Duplicate reading ID');ids.add(record['id'])
        text=record['text'];text.encode('utf-8');length=len(text)
        require(length<=CAPS['maximumTextCodepoints'],'Text codepoint cap exceeded')
        total+=length;require(total<=CAPS['totalTextCodepoints'],'Text population cap exceeded')
        empty+=int(length==0);minimum=length if minimum is None else min(minimum,length);maximum=max(maximum,length);texts.add(text)
        if cohort['strictKnown'] is not None:
            flag=record['sourceCompleteForProjection'];affected=record['uncertainSelectedTokens']
            require(type(flag) is bool and type(affected) is int and affected>=0 and flag==(affected==0),'Strict source flag changed')
            require(record['projection'] in ('words','initials','finals'),'Projection changed')
            if flag:known_count+=1;known_texts.add(text);known_projections[record['projection']]+=1
        if cohort['id']=='issue27-frozen-stream-coverage':orders[record['characterOrder']]+=1
    actual={'recordCount':count,'uniqueTextCount':len(texts),'emptyTexts':empty,'minimumTextCodepoints':minimum,'maximumTextCodepoints':maximum,'totalTextCodepoints':total}
    require(actual=={k:cohort[k] for k in actual},'Original reading population changed')
    if cohort['strictKnown'] is not None:
        known=cohort['strictKnown'];require(known_count==known['recordCount'] and dict(known_projections)==known['projectionCounts'] and count-known_count==known['sourceAffectedRecords'],'Strict source subset changed')
    if cohort['id']=='issue27-frozen-stream-coverage':require(dict(orders)=={'exact':1940,'reversed-codepoints':1940},'Original character-order population changed')
    return actual,texts,known_texts


def cohort_forms(texts,cohort,core):
    forms=core.make_forms([{'text':text} for text in texts])
    require(len(forms)<=cohort['maximumForms'] and (cohort['expectedForms'] is None or len(forms)==cohort['expectedForms']),'Registered form population changed')
    if cohort['id']=='issue26-first-words':
        # Direct equality proof, stronger than the older hash-index cardinality inference.
        require(set(forms)==texts and len(forms)==1746,'Issue26 exact/compact set equality failed')
    return forms


def evaluate_shared(forms,formats,common,core):
    formats=tuple(formats)
    if formats==FORMATS4:return core.evaluate_common4(forms,common)
    require(formats in (FORMATS8,()),'Gate matrix changed')
    if 'bip39' in formats:contained_file(ENGLISH)
    indexes=common.wordlist()[1] if 'bip39' in formats else None
    counts=dict.fromkeys(formats,0);shapes={f:set() for f in formats}
    for text in forms:
        for kind in formats:
            for value in common.shape_values(kind,text,indexes):
                counts[kind]+=1;shapes[kind].add(value)
                require(sum(counts.values())<=CAPS['shapeOccurrencesPerCohort'] and sum(map(len,shapes.values()))<=CAPS['uniqueShapesPerCohort'],'Shared shape cap exceeded')
    rawshapes={f:sorted(shapes[f]) for f in formats};positives=[];valid={f:set() for f in formats}
    for kind in formats:
        for value in rawshapes[kind]:
            checked=common.validate_record(kind,value,indexes)
            if checked is not None:
                canonical_bytes,metadata=checked;fp=common.fingerprint(kind,canonical_bytes);valid[kind].add(fp)
                positives.append({'format':kind,'value':value,'fingerprint':fp,'metadata':metadata})
    summary={'formats':list(formats),'shapeCounts':counts,'uniqueShapeCounts':{f:len(shapes[f]) for f in formats},'validationCalls':sum(map(len,shapes.values())),
      'validCounts':{f:len(valid[f]) for f in formats},'privateReviewRequired':bool(positives),'fingerprintRule':deepcopy(common.FINGERPRINT_RULE)}
    return summary,rawshapes,positives


def evaluate_forms(forms,formats,core,common):
    shared,shapes,positives=evaluate_shared(forms,formats,common,core)
    mini,mshapes,mpositives=core.scan_minikey26_forms(forms,common)
    return {'common':shared,'rawShapeValues':shapes,'rawPositives':positives,'minikey26':mini,'minikey26Shapes':mshapes,'minikey26Positives':mpositives}


def safe_evaluation(evaluation):
    common=evaluation['common'];mini=evaluation['minikey26']
    return {k:deepcopy(common[k]) for k in ('formats','shapeCounts','uniqueShapeCounts','validationCalls','validCounts')},{k:mini[k] for k in ('status','enumerated','shapeOccurrences','uniqueShapeCount','checksumCalls','validCount')}


def valid_count(evaluation):return sum(evaluation['common']['validCounts'].values())+evaluation['minikey26']['validCount']


def safe_result(protocol,pbytes,registration,cohort_data,started,integrity):
    cohorts=[]
    for cohort,stats,forms,validation,known_forms in cohort_data:
        common,mini=safe_evaluation(validation['evaluationAll']);strict=None
        if cohort['strictKnown'] is not None:
            c,m=safe_evaluation(validation['evaluationStrictKnown']);strict={'recordCount':60,'formCount':len(known_forms),'nestedInNominal':True,'physicalSourceComplete':False,'common':c,'minikey26':m,'privateReviewRequired':bool(valid_count(validation['evaluationStrictKnown']))}
        cohorts.append({'id':cohort['id'],'recordCount':stats['recordCount'],'uniqueTextCount':stats['uniqueTextCount'],'formCount':len(forms),'rawReadingBytes':cohort['rawBytes'],'rawReadingSha256':cohort['rawSha256'],
          'artifactPinAuthority':cohort['artifactPinAuthority'],'originalReadingReconstruction':cohort['originalReadingReconstruction'],'common':common,'minikey26':mini,'strictKnown':strict,'privateReviewRequired':bool(valid_count(validation['evaluationAll']))})
    return {'version':1,'testId':TEST_ID,'batchId':BATCH_ID,'status':'four-cohort-fixed-output-compatibility-scope-complete','startedAtUTC':started,'completedAtUTC':utc(),
      'registrationCommit':registration,'protocolSha256':digest(pbytes),'sourceHashes':deepcopy(protocol['sourceHashes']),'scriptHashes':deepcopy(protocol['scriptHashes']),
      'scopeComplete':True,'compatibilityGatesComplete':True,'allOriginalArtifactIdentitiesVerified':True,'originalReadingReconstruction':{c['id']:c['originalReadingReconstruction'] for c in COHORTS},
      'newSelectorIntroduced':False,'ocrRerun':False,'sourceRepairs':False,'semanticReviewPerformed':False,'privateReviewRequired':any(c['privateReviewRequired'] for c in cohorts),
      'cohorts':cohorts,'counts':{'cohorts':len(cohorts),'labeledRecords':sum(s['recordCount'] for _,s,_,_,_ in cohort_data),'textCodepoints':sum(s['totalTextCodepoints'] for _,s,_,_,_ in cohort_data),
      'sumPerCohortForms':sum(c['formCount'] for c in cohorts),'globalUnionComputed':False,'strictKnownIsNested':True,'sumNominalValidRecords':sum(valid_count(v['evaluationAll']) for _,_,_,v,_ in cohort_data)},
      'privateArtifactIntegrity':integrity,'activity':deepcopy(DEFINITION['activityBoundary']),'limitations':deepcopy(DEFINITION['limitations'])}


def run(protocol_path,registration,out_value):
    started=utc();out=private_output(out_value);protocol,pbytes,files=validate_protocol(protocol_path,registration)
    out.mkdir(mode=0o700);os.chmod(out,0o700)
    try:
        core,common=load_engines(files)
        identities=reconstruct_originals(files,out,common)
        populations=[];form_records=[]
        # Validate every schema/population/form surface before any candidate validation.
        for cohort in COHORTS:
            stats,texts,known=analyze_records(reading_records(out/cohort['readingFile'],cohort),cohort)
            forms=cohort_forms(texts,cohort,core);known_forms=None
            if cohort['strictKnown'] is not None:
                known_forms=core.make_forms([{'text':text} for text in known]);require(len(known_forms)==78 and set(known_forms)<=set(forms),'Strict form subset changed')
            populations.append((cohort,stats,forms,known_forms))
            form_records.append({'id':cohort['id'],'forms':forms,'strictKnownForms':known_forms})
        require(sum(s['recordCount'] for _,s,_,_ in populations)==43699 and sum(s['totalTextCodepoints'] for _,s,_,_ in populations)==2303575,'Combined population changed')
        require(sum(sum(map(len,f))+(sum(map(len,k)) if k else 0) for _,_,f,k in populations)<=CAPS['totalFormCodepoints'],'Combined form cap exceeded')
        validations=[];cohort_data=[]
        for cohort,stats,forms,known_forms in populations:
            all_evaluation=evaluate_forms(forms,cohort['commonFormats'],core,common)
            strict=derive_strict_evaluation(known_forms,cohort['commonFormats'],all_evaluation,common) if known_forms is not None else None
            validation={'id':cohort['id'],'evaluationAll':all_evaluation,'evaluationStrictKnown':strict}
            validations.append(validation);cohort_data.append((cohort,stats,forms,validation,known_forms))
        payloads={'FORMS.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,'cohorts':form_records}),'VALIDATION.private.json':json_bytes({'schemaVersion':1,'testId':TEST_ID,'cohorts':validations})}
        require(all(len(raw)<=CAPS['privateArtifactBytes'] for raw in payloads.values()),'Private artifact byte cap exceeded')
        require(sum(n for n,_ in identities.values())+sum(map(len,payloads.values()))<=CAPS['totalPrivateOutputBytes'],'Total private output cap exceeded')
        integrity={name:mark for name,(_,mark) in identities.items()};integrity.update({name:digest(raw) for name,raw in payloads.items()})
        result=safe_result(protocol,pbytes,registration,cohort_data,started,integrity)
        for name,raw in payloads.items():private_write(out/name,raw)
        private_write(out/'RESULT.json',json_bytes(result))
        return result
    except Exception:
        try:private_write(out/'FAILURE.json',json_bytes({'version':1,'testId':TEST_ID,'status':'inconclusive','scopeComplete':False,'error':'Registered compatibility scope did not complete.'}))
        except Exception:pass
        raise
def derive_strict_evaluation(forms,formats,nominal,common):
    # Subset shapes may be counted again; all actual validation/checksum work is reused.
    formats=tuple(formats);require(formats==FORMATS4,'Strict source subset gate matrix changed')
    counts=dict.fromkeys(formats,0);shapes={f:set() for f in formats}
    for text in forms:
        for kind in formats:
            for value in common.shape_values(kind,text):
                counts[kind]+=1;shapes[kind].add(value)
                require(sum(counts.values())<=CAPS['shapeOccurrencesPerCohort'],'Strict shape cap exceeded')
    for kind in formats:require(shapes[kind]<=set(nominal['rawShapeValues'][kind]),'Strict shape not in nominal validation')
    positives=[deepcopy(p) for p in nominal['rawPositives'] if p['value'] in shapes[p['format']]]
    valid={kind:{p['fingerprint'] for p in positives if p['format']==kind} for kind in formats}
    shared={'formats':list(formats),'shapeCounts':counts,'uniqueShapeCounts':{f:len(shapes[f]) for f in formats},'validationCalls':0,'validCounts':{f:len(valid[f]) for f in formats},
      'privateReviewRequired':bool(positives),'fingerprintRule':deepcopy(common.FINGERPRINT_RULE)}
    mset=set();occurrences=0;pattern=re.compile(r'(?=(S[1-9A-HJ-NP-Za-km-z]{25}))')
    for text in forms:
        for match in pattern.finditer(text):occurrences+=1;mset.add(match.group(1));require(occurrences<=CAPS['shapeOccurrencesPerCohort'],'Strict mini shape cap exceeded')
    require(mset<=set(nominal['minikey26Shapes']),'Strict mini shape not in nominal validation')
    mpositives=[deepcopy(p) for p in nominal['minikey26Positives'] if p['value'] in mset]
    mini={'status':'derived-from-nominal-validation','enumerated':True,'length':26,'shapeOccurrences':occurrences,'uniqueShapeCount':len(mset),'checksumCalls':0,'validCount':len(mpositives),
      'privateReviewRequired':bool(mpositives),'fingerprintRule':deepcopy(common.FINGERPRINT_RULE),'proof':{'nominalValidationReused':True,'nestedSubset':True}}
    return {'common':shared,'rawShapeValues':{f:sorted(shapes[f]) for f in formats},'rawPositives':positives,'minikey26':mini,'minikey26Shapes':sorted(mset),'minikey26Positives':mpositives}
def self_test():
    checks=0
    def reject(call):
        nonlocal checks
        try:call()
        except (ValueError,UnicodeError,OSError,EOFError):checks+=1
        else:raise AssertionError('Expected source-free rejection')
    core,common=load_engines();controls=load_json(capped_read(ROOT/CONTROLS,CAPS['sourceJsonBytes']))
    assert core.make_forms([{'text':' A\tB\nC\u00a0D '},{'text':''}])==['',' A\tB\nC\u00a0D ','ABCD'];checks+=1
    funky=compiled_module(MATERIAL['funkyProducer'],common=common);stride=compiled_module(MATERIAL['strideProducer'],common=common);frozen=compiled_module(MATERIAL['frozenProducer'],common=common)
    old_functions={}
    forbidden={'wholeProducerCalls':0,'bareMinikeyHashes':0,'legacyValidatorsOutsideFunky':0}
    def forbidden_whole(*args,**kwargs):forbidden['wholeProducerCalls']+=1;raise AssertionError('Whole producer/old evaluator forbidden')
    for module in (funky,stride,frozen,core,common):
        for name in ('run','evaluate','self_test','load_evaluator'):
            if hasattr(module,name):old_functions[(module,name)]=getattr(module,name);setattr(module,name,forbidden_whole)
    # Frozen source-only APIs on synthetic fixtures, with independent literal expected surfaces.
    toyrows=[{'printedText':'Alpha first'},{'printedText':'Beta second'},{'printedText':'Gamma third'}]
    records=funky.literal_readings(toyrows)
    assert records==[{'id':'SAND-FW-ALL','selectedRowCount':3,'text':'Alpha Beta Gamma'},{'id':'SAND-ODD-LINES','selectedRowCount':2,'text':'Alpha first\nGamma third'},{'id':'SAND-EVEN-CONTROL','selectedRowCount':1,'text':'Beta second'}];checks+=1
    envelope={'schemaVersion':1,'testId':funky.TEST_ID,'sourceSha256':'0'*64,'readings':records}
    assert funky.json_bytes(envelope)==(json.dumps(envelope,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();checks+=1
    tiny=[{'rowId':'control-row','modelText':' '.join('word'+str(i) for i in range(36)),'originalText':'control','uncertainTokenIndices':[0,1,2],'uncertainForProjections':['words','initials']}]
    tokens=stride.make_tokens(tiny);r=stride.make_readings(tokens)
    assert len(tokens)==36 and len(r)==72 and sum(x['sourceCompleteForProjection'] for x in r)==60 and all(x['sourceCompleteForProjection'] for x in r if x['projection']=='finals');checks+=1
    wrapped=list(frozen.submitted_readings({'b':'second line','a':'A ♥'}))
    assert [x['id'] for x in wrapped]==['a:exact','a:reversed-codepoints','b:exact','b:reversed-codepoints'] and wrapped[1]['text']=='♥ A';checks+=1
    line=list(jsonl_chunks([{'id':'test','text':'♥\nA'}]))
    assert line==[b'{"id": "test", "text": "\\u2665\\nA"}\n'];checks+=1
    reject(lambda:stride.validate_source({}, {}, {}, {}));reject(lambda:frozen.validate_source({}));reject(lambda:funky.validate_source({}))
    old_hash=hashlib.sha256;old_shape=common.shape_values;old_validate=common.validate_record;old_fp=common.fingerprint
    scope={'funky':False}
    def guarded_hash(data=b'',*args,**kwargs):
        raw=bytes(data)
        if len(raw) in (22,26,30) and raw.startswith(b'S') and all(chr(c) in core.B58 for c in raw):forbidden['bareMinikeyHashes']+=1;raise AssertionError('Bare minikey hash forbidden')
        return old_hash(data,*args,**kwargs)
    def guarded_shape(kind,*args,**kwargs):
        if kind=='minikey' and not scope['funky']:forbidden['legacyValidatorsOutsideFunky']+=1;raise AssertionError('Legacy minikey outside Funky')
        return old_shape(kind,*args,**kwargs)
    def guarded_validate(kind,*args,**kwargs):
        if kind=='minikey' and not scope['funky']:forbidden['legacyValidatorsOutsideFunky']+=1;raise AssertionError('Legacy minikey outside Funky')
        return old_validate(kind,*args,**kwargs)
    hashlib.sha256=guarded_hash;common.shape_values=guarded_shape;common.validate_record=guarded_validate
    try:
        mini=None
        for counter in range(65536):
            n=counter;suffix=''
            while n:n,rem=divmod(n,58);suffix=core.B58[rem]+suffix
            value='S'+'2'*21+(suffix or '1').rjust(4,'1')
            if core.minikey26_valid(value):mini=value;break
        assert mini is not None;checks+=1
        payload=b'\x80'+bytes(31)+b'\x01\x01';wif=common.b58encode(payload+hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4])
        fixture=[wif,'0'*63+'1',controls['bip39_valid'],controls['bip32_extended_private'],controls['bip38_encrypted_private'],controls['legacy_address'],controls['segwit_v0'],controls['segwit_v1'],controls['sec_compressed_generator'],controls['sec_uncompressed_generator'],'SzavMBLoXU6kDrqtUVmffv','S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy',mini]
        scope['funky']=True;ev=evaluate_forms(sorted(set(fixture)),FORMATS8,core,common);scope['funky']=False
        assert all(ev['common']['validCounts'][f]>=1 for f in FORMATS8) and ev['minikey26']['validCount']==1;checks+=1
        assert ev['common']['validCounts']['sec_public']==1 and len([p for p in ev['rawPositives'] if p['format']=='sec_public'])==2;checks+=1
        ev4=evaluate_forms(sorted(set(fixture)),FORMATS4,core,common)
        ev26=evaluate_forms([mini],(),core,common)
        assert ev26['common']['formats']==[] and ev26['common']['validationCalls']==0 and ev26['minikey26']['validCount']==1;checks+=1
        for text in ['S'*22,'S'*25,mini[:25],'s'+mini[1:],'Ｓ'+mini[1:],mini[:4]+'0'+mini[5:]]:
            assert core.scan_minikey26_forms([text],common)[0]['checksumCalls']==0;checks+=1
        overlap=core.scan_minikey26_forms(['S'*27],common)[0]
        assert overlap['shapeOccurrences']==2 and overlap['uniqueShapeCount']==overlap['checksumCalls']==1;checks+=1
        def no_validation(*args,**kwargs):raise AssertionError('Strict subset must reuse nominal validation')
        common.validate_record=no_validation;common.fingerprint=no_validation;hashlib.sha256=no_validation
        try:
            derived=derive_strict_evaluation([mini,controls['sec_compressed_generator']],FORMATS4,ev4,common)
            assert derived['common']['validationCalls']==0 and derived['minikey26']['checksumCalls']==0 and derived['minikey26']['status']=='derived-from-nominal-validation' and derived['minikey26']['validCount']==1 and derived['common']['validCounts']['sec_public']==1;checks+=1
        finally:common.validate_record=guarded_validate;common.fingerprint=old_fp;hashlib.sha256=guarded_hash
        toy={'id':'control','recordKeys':['id','text'],'recordCount':3,'uniqueTextCount':2,'emptyTexts':1,'minimumTextCodepoints':0,'maximumTextCodepoints':2,'totalTextCodepoints':4,'strictKnown':None}
        stats,texts,known=analyze_records([{'id':'a','text':''},{'id':'b','text':'ab'},{'id':'c','text':'ab'}],toy)
        assert texts=={'','ab'} and known==set() and stats['recordCount']==3;checks+=1
        reject(lambda:analyze_records([{'id':'a','text':1}],toy));reject(lambda:analyze_records([{'id':'a','text':''},{'id':'a','text':'ab'}],toy))
        exact={f'control{i:04d}' for i in range(1746)}
        assert len(cohort_forms(exact,COHORTS[1],core))==1746;checks+=1
        changed=set(exact);changed.remove('control0000');changed.add('control 0000');reject(lambda:cohort_forms(changed,COHORTS[1],core))
        # A positive-containing safe receipt excludes every raw record and fingerprint.
        dummy=[]
        for cohort in COHORTS:
            e=ev if cohort['id']=='funky-sand-direct' else ev26 if cohort['id']=='issue26-first-words' else ev4
            validation={'id':cohort['id'],'evaluationAll':e,'evaluationStrictKnown':derived if cohort['strictKnown'] else None}
            s={'recordCount':cohort['recordCount'],'uniqueTextCount':cohort['uniqueTextCount'],'totalTextCodepoints':cohort['totalTextCodepoints']}
            dummy.append((cohort,s,fixture,validation,fixture if cohort['strictKnown'] else None))
        proto={'version':1,'batchId':BATCH_ID,'test':code_definition(),'sourceHashes':deepcopy(SOURCE_PINS),'scriptHashes':{p:FIXED_CODE_PINS.get(p,'0'*64) for p in SCRIPTS}}
        safe=safe_result(proto,b'control protocol','0'*40,dummy,'control',{})
        rendered=json_bytes(safe)
        assert safe['privateReviewRequired'] and b'fingerprint' not in rendered and b'rawPositives' not in rendered;checks+=1
        assert all(value.encode() not in rendered for value in fixture);checks+=1
    finally:
        hashlib.sha256=old_hash;common.shape_values=old_shape;common.validate_record=old_validate;common.fingerprint=old_fp
        for (module,name),function in old_functions.items():setattr(module,name,function)
    with tempfile.TemporaryDirectory(prefix='columns-compatibility-control-') as tmp:
        parent=Path(tmp);os.chmod(parent,0o700);out=private_output(parent/'fresh');out.mkdir(mode=0o700)
        sandbox=parent/'root';sandbox.mkdir(mode=0o700);(sandbox/'inside').write_bytes(b'control');(parent/'outside').write_bytes(b'control');(sandbox/'escape').symlink_to(parent/'outside')
        assert contained_file('inside',sandbox)==(sandbox/'inside').resolve();checks+=1
        reject(lambda:contained_file('escape',sandbox));reject(lambda:contained_file('../outside',sandbox));reject(lambda:contained_file(str(parent/'outside'),sandbox))
        original=b'{"id":"a","text":"control"}\n';compressed=gzip.compress(original)
        info=private_stream(out/'control.jsonl',bounded_gzip_chunks(compressed),1000)
        assert info==(len(original),digest(original)) and (out/'control.jsonl').read_bytes()==original;checks+=1
        verify_original_identities({'x':info},[{'readingFile':'x','rawBytes':len(original),'rawSha256':digest(original)}]);checks+=1
        reject(lambda:verify_original_identities({'x':info},[{'readingFile':'x','rawBytes':len(original),'rawSha256':'0'*64}]))
        reject(lambda:list(bounded_gzip_chunks(compressed[:-5])))
        old_cap=CAPS['decompressedBytes'];CAPS['decompressedBytes']=1
        try:reject(lambda:list(bounded_gzip_chunks(compressed)))
        finally:CAPS['decompressedBytes']=old_cap
        assert stat.S_IMODE(out.stat().st_mode)==0o700 and stat.S_IMODE((out/'control.jsonl').stat().st_mode)==0o600;checks+=1
        reject(lambda:private_output(out));reject(lambda:private_output(ROOT.parent.parent/'dist'/'raw-control'));reject(lambda:private_output(parent/'public'/'raw-control'))
        reject(lambda:private_stream(out/'too-small',iter([b'abcdef']),2))
        os.chmod(parent,0o755);reject(lambda:private_output(parent/'other'));os.chmod(parent,0o700)
    validate_protocol_header(proto,'0'*40);checks+=1
    for field in ('sourceHashes','scriptHashes'):
        bad=deepcopy(proto);bad[field].pop(next(iter(bad[field])));reject(lambda b=bad:validate_protocol_header(b,'0'*40))
    bad=deepcopy(proto);bad['test']['formsPolicy']='other';reject(lambda:validate_protocol_header(bad,'0'*40))
    for registration in ['main','a'*39,'A'*40]:reject(lambda r=registration:validate_protocol_header(proto,r))
    for code,kind in [(0,b'tree\n'),(0,b'tag\n'),(1,b'commit\n'),(0,b'')]:
        reject(lambda c=code,k=kind:require_commit('0'*40,lambda *a,**kw:types.SimpleNamespace(returncode=c,stdout=k)))
    require_commit('0'*40,lambda *a,**kw:types.SimpleNamespace(returncode=0,stdout=b'commit\n'));checks+=1
    rawfiles={p:('source-free-control:'+p).encode() for p in dict.fromkeys(INPUTS+SCRIPTS)}
    fake={'sourceHashes':{p:digest(rawfiles[p]) for p in INPUTS},'scriptHashes':{p:digest(rawfiles[p]) for p in SCRIPTS}};pbytes=b'control protocol';rawfiles[PROTOCOL]=pbytes;reads=[]
    def blob(reg,path):return rawfiles[path]
    def current(path):reads.append(path);return rawfiles[path]
    assert set(verify_payloads(fake,pbytes,'0'*40,current,blob))==set(INPUTS+SCRIPTS);checks+=1
    reads.clear();reject(lambda:verify_payloads(fake,b'changed','0'*40,current,blob));assert reads==[];checks+=1
    reject(lambda:verify_payloads(fake,pbytes,'0'*40,lambda p:rawfiles[p]+b'changed',blob))
    assert forbidden=={'wholeProducerCalls':0,'bareMinikeyHashes':0,'legacyValidatorsOutsideFunky':0};checks+=1
    return {'version':1,'testId':TEST_ID,'status':'PASS','selfTestChecks':checks,'targetSourcesOpened':False,'targetReadingsReconstructed':False,'targetFormsConstructed':False,'targetChecks':0,'wholeProducerCalls':0,'bareMinikeyHashes':0,'legacyValidatorsOutsideFunky':0,'strictSubsetValidatorCalls':0,'strictSubsetChecksumCalls':0,'strictSubsetFingerprintCalls':0,'ocrReruns':0,'networkQueries':0}


class QuietParser(argparse.ArgumentParser):
    def error(self,message):raise ValueError('Invalid command arguments')


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    flags=('--definition','--self-test','--run','--protocol','--registration-commit','--out')
    require(all(argv.count(f)<=1 for f in flags),'Duplicate argument')
    parser=QuietParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--definition',action='store_true');action.add_argument('--self-test',action='store_true');action.add_argument('--run',action='store_true')
    parser.add_argument('--protocol');parser.add_argument('--registration-commit');parser.add_argument('--out');args=parser.parse_args(argv)
    extra=(args.protocol,args.registration_commit,args.out)
    if not args.run:require(not any(extra),'Run-only arguments require run')
    if args.definition:return code_definition()
    if args.self_test:return self_test()
    require(all(extra),'Protocol registration and private output required')
    return run(args.protocol,args.registration_commit,args.out)


if __name__=='__main__':
    os.umask(0o077)
    try:print(json.dumps(main(),ensure_ascii=False,allow_nan=False))
    except Exception:
        print(json.dumps({'version':1,'testId':TEST_ID,'status':'inconclusive','scopeComplete':False,'error':'Validation or execution failed; no compatibility conclusion.'}),file=sys.stderr)
        raise SystemExit(1)
