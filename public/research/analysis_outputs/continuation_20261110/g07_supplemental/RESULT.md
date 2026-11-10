# G07 saved-output compatibility result

The registered supplemental replay completed on the **same 1,038 saved G07 spectral-OCR records: 833 unique texts and 1,464 exact/Unicode-whitespace-compacted forms**. It found **zero valid records in the five added gates**. Six distinct address-shaped strings failed validation; both distinct 26-character minikey shapes failed the eight-bit question-mark checksum. The other added families produced no shapes.

| Added gate | Shape occurrences | Unique shapes / checks | Valid records |
|---|---:|---:|---:|
| Extended private record | 0 | 0 | 0 |
| BIP38 encrypted record | 0 | 0 | 0 |
| Literal Bitcoin address | 6 | 6 | 0 |
| SEC public key | 0 | 0 | 0 |
| Embedded 26-character minikey | 2 | 2 | 0 |

This closes the declared compatibility gap on these saved outputs. It supplements the existing G07 method; it does not add an extraction method or independent theory. The frozen OCR population, original 112 detector views, record order and text remain unchanged. No OCR rerun, selector regeneration, repair, additional join or transform was performed beyond the existing exact/whitespace-only form policy.

The [independent verifier](INDEPENDENT_VERIFICATION.json) reported **PASS**, comparing all original record objects, order and UTF-8 strings, the complete form set, raw validation records, and safe counts/scope. The primary reuses its frozen form/format/window core; the verifier reuses its separately frozen form/window core. Both adapters compile hash-verified source directly and deliberately share the unchanged four-format engine. Their agreement therefore does **not** establish independent mathematics for those four validators. The 26-character enumeration and form reconstruction use the separately frozen independent core.

The [registered machine protocol](PROTOCOL.json), SHA256 `9d14337811a1679014ee06193511fe196861bf3a8f8e1adb0ce69d09fb8ed161`, fixes eight source-witness entries and five script entries: 13 distinct files including the protocol because the common engine appears in both pin maps. The [saved registration receipt](REGISTRATION.json) records matching local HEAD and remote main at commit **`a1051636de65a62d896da9fa1d9d5235484e1c61`** before execution. Prior remote publication is the operator's recorded verification; both execution adapters separately enforce the local Git commit object and exact current/registered bytes before target parsing.

All times below are UTC on 10 November 2026:

| Receipt | Recorded UTC |
|---|---|
| Registration verification | 19:04:34.126661 |
| Primary start → completion | 19:04:34.167 → 19:04:34.397 |
| Independent verification completion | 19:04:44.020430 |

The source artifact is unchanged, SHA256 `e934e778c07cba19c00c6e4fb7cb8f858042f904d320f0d919a59fa1e4c3e7da`. The primary technical result SHA256 is `9c343ca3f1045cf073c122ae8f7bee51fa409284c1f500b46488f9d3c3d9a937`; the independent verification receipt SHA256 is `467547ec5b16ae2fb3f588ed3c581d25b88f4f8d6629970aa3921cfe1299d084`. Raw forms and validation values remain private; public receipts expose counts and whole-artifact integrity only. The [post-run metadata review](POST_RUN_REVIEW.json) also matched all pins, counts, timestamps and private permissions.

To reproduce the registered command sequence, use Python 3.9+ standard library from `public/research` in a local Git checkout containing the registration commit. This is the protocol's command sequence with its registration placeholder filled:

```sh
task_private="$(mktemp -d /tmp/key404-g07.XXXXXX)"
python3 -B scripts/g07_supplemental_formats.py --self-test
python3 -B scripts/verify_g07_supplemental.py --self-test
python3 -B scripts/g07_supplemental_formats.py --run \
  --protocol analysis_outputs/continuation_20261110/g07_supplemental/PROTOCOL.json \
  --registration-commit a1051636de65a62d896da9fa1d9d5235484e1c61 --out "$task_private/primary"
python3 -B scripts/verify_g07_supplemental.py --verify \
  --protocol analysis_outputs/continuation_20261110/g07_supplemental/PROTOCOL.json \
  --registration-commit a1051636de65a62d896da9fa1d9d5235484e1c61 \
  --result "$task_private/primary/RESULT.json" \
  --forms "$task_private/primary/FORMS.private.json" \
  --validation "$task_private/primary/VALIDATION.private.json" \
  --out "$task_private/independent"
```

The output parent and fresh directories must be 0700, outside the entire site checkout; raw files are 0600. Guard failure is inconclusive.

OCR misses, unusual or damaged source text, other readings and the original view model remain outside this result. Within the replay and independent verification, no semantic recognition, geometry conclusion, scalar/key/address/seed derivation, wallet action, candidate-history query or outbound network request occurred. This is no whole-puzzle exclusion or prize/funding authentication. **The puzzle remains unsolved.**
