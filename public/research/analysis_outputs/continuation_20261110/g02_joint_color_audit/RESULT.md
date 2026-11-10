# The two-sided stencil: joint color memberships mapped

**The declared geometry model is complete; the puzzle remains unsolved.** Two implementations matched all 962 ordered word positions across four directed pairs and 12,560 partition points. The 97 legacy boundary flags were reproduced. All 97 positions can still change a selector; none is silently assigned a fixed color. No unresolved both-color overlap, nominal-color discrepancy or old stable-class disagreement was observed in this finite model.

The [original G02 run](../batch20/G02/RESULT.json) retained zero complete readings. It discarded every selector/order scope containing any uncertain word. The later first/last-word envelopes considered one reflected color and at most one edge word per row. This audit completes a distinct source preparation step for G02's joint colors and all-word selection.

| Global selector | Required words | Optional positions | Independent assignment bound |
| --- | ---: | ---: | ---: |
| same-color | 0 | 27 | 134,217,728 |
| opposite-color | 0 | 3 | 8 |
| source-only | 78 | 59 | 576,460,752,303,423,488 |
| target-only | 139 | 39 | 549,755,813,888 |

Each bound assumes independent include/omit choices across positions. Shared geometry can correlate them, so the bound is not a count of physically attainable readings, distinct strings or theories. Same-color and opposite-color have no required word. Opposite-color has at most three words across its eight modeled assignments. The largest global bound, source-only, is `2^59`. Enumerating every complete reading would be impractical.

The [public registration](https://github.com/dctrpr/key-not-found/commit/ec3bb322cb1b8baa35ee128143dd8864cb6ab451) preceded target classification. The [protocol](PROTOCOL.md) fixes the source files, exact joint enclosure, reflected endpoints, controls and stop rules. The [ID-only membership inventory](MEMBERSHIP.json) preserves the joint color pairs and word membership options without word strings. The [primary result](RESULT.json) finished at 2026-11-10T22:20:31.145Z; the [independent reconstruction](INDEPENDENT_VERIFICATION.json) finished at 2026-11-10T22:21:09.121Z. It compared every ordered metadata field and the aggregate counts. [Registration receipt](REGISTRATION.json), [preflight](PREFLIGHT.json).

**No reading, key check, image measurement, new OCR, derivation, history query or wallet action ran.** The word-center and rectangle assumptions remain heuristic. Complete metadata coverage does not certify original glyph contours, prove intent, or exclude G02 as a cipher. The next useful test is an exact analysis of the registered literal-format candidates over these fixed selections, using a compact choice graph where enumeration is too large. Its text projection, caps, controls and acceptance criteria need their own registration. The eight opposite-color assignments are also small enough for a complete language review under a fixed scope.

## Reproduce the source audit

From the repository root, use a fresh absolute private output parent outside the checkout. The scripts use the receipt in this folder and verify the pinned source and code. Run with Python 3.9 or later.

```sh
G02_PRIVATE_PARENT="$(mktemp -d)"
G02_PROTOCOL=public/research/analysis_outputs/continuation_20261110/g02_joint_color_audit/PROTOCOL.json
G02_REGISTRATION=ec3bb322cb1b8baa35ee128143dd8864cb6ab451
python3 public/research/scripts/g02_joint_source_audit.py --self-test
python3 public/research/scripts/verify_g02_joint_source_audit.py --self-test
python3 public/research/scripts/g02_joint_source_audit.py --audit --corpus public/research --protocol "$G02_PROTOCOL" --registration-commit "$G02_REGISTRATION" --out "$G02_PRIVATE_PARENT/primary"
python3 public/research/scripts/verify_g02_joint_source_audit.py --verify --corpus public/research --protocol "$G02_PROTOCOL" --registration-commit "$G02_REGISTRATION" --primary-inventory "$G02_PRIVATE_PARENT/primary/MEMBERSHIP.json" --primary-result "$G02_PRIVATE_PARENT/primary/RESULT.json" --out "$G02_PRIVATE_PARENT/independent"
```

Run timestamps and whole result-file hashes change on replay. Ordered memberships and deterministic counts remain comparable. Keep unreviewed outputs in the private directory.
