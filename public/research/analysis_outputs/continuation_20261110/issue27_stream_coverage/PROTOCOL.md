# Issue 27 saved-reading coverage audit

This protocol is to be published **before any target scan**. The target population is the already saved Orange Party column readings, not a newly chosen cipher or a new transcript. The [machine protocol](PROTOCOL.json) fixes seven source hashes, two implementation hashes, exact format rules and completion limits.

## Why this test

The historical Issue 27 checker tested WIF and literal 64-hex records. It did not implement embedded minikey checks or BIP39 validation for this corpus. The later minikey-window audit used a different Issue 24 corpus and cannot supply this missing coverage. This is a validation gap, not evidence of a hidden key.

The [restored source packet](../../comparison_articles/overdose_style_uniqueness/issue27/SOURCE_REGISTER.md) contains unchanged retained scans of the title and printed pages 79–81. The matching publisher contents describe a Fall 2022 column, relevant to the broad December 2022 plural-key post. This does not authenticate it as the March 2023 Issue 24 / 20-BTC target. The legacy Issue 27 identifier and exact publication day retain the bibliographic limits in that register.

## Fixed population and operation

Read the exact pinned `printed_lines_and_streams.json`: 356 source rows, 14 regions and 1,940 labelled streams. Preserve every saved scope, parity, typography selection, row order, fragment and OCR uncertainty. In sorted-label order submit each exact string and its already used character reversal, for **3,880 labelled records**. No re-OCR, spelling repair, dictionary-word filtering, extra page order, deletion of the repeated paragraph or new source selection is included.

The unchanged shared scanner deduplicates exact and whitespace-only-compacted forms. There can be at most **7,760 distinct forms**; the actual count remains unknown before execution. The submitted-text cap is 2,000,000 code points and the form cap is 4,000,000. The source JSON and committed blobs also have fixed byte limits.

Check four literal formats:

- Embedded 51/52-character mainnet WIF, including checksum, compression marker and scalar range.
- Embedded 22/30-character minikey, including windows inside a longer Base58 run and its one-byte check.
- Exactly 64 hexadecimal characters bounded by non-hex characters, with valid scalar range. This format has no checksum.
- Contiguous unfiltered English BIP39 windows of 12/15/18/21/24 lexical tokens, including their entropy checksum. Unknown, numeric and apostrophe-containing words remain barriers; the explicit missing-group marker is a hard boundary. Do not remove unwanted words to manufacture a phrase.

No prose-to-secret hashing, arbitrary ASCII scalar, seed derivation, passphrase guess, address/history request, wallet import, signing or transaction follows from this test.

## Gates and interpretation

Run published/synthetic controls before parsing target text. Verify the actual protocol and every pinned file against the exact bytes in the supplied local Git registration commit. The coordinating researcher must separately verify that commit is public on GitHub before execution. The [independent control review](CONTROL_REVIEW.json) and [extra guards](EXTRA_CONTROLS.json) opened no target text and made no target checks.

Save raw replay records only in a fresh private directory, with private file modes. Public results may expose aggregate counts, named formats, approved validation metadata and domain-separated fingerprints. Never publish the raw candidate, seed, private scalar, source locator that reveals a lead, or SHA256(minikey), which is its private scalar. No per-stream ordinary SHA-256 is computed, including for short strings.

A source/code/registration drift, incomplete population, cap violation, control failure or unsupported result is **inconclusive**, never a negative. A complete zero excludes only these four literal formats under the exact frozen readings and whitespace conventions. It does not validate OCR completeness or rule out the whole article or puzzle. A valid-format record is a private review lead; an eight-bit minikey pass or checksum-free hex value especially needs independent evidence.

## Reproduce

From the research root in a checkout containing the registration commit:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue27_stream_coverage.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue27_stream_coverage.py --run --protocol analysis_outputs/continuation_20261110/issue27_stream_coverage/PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out /tmp/key404-private/issue27-rerun
```

Replace the commit with the first published registration, create the private parent directory first, and use a new output directory. No target result is claimed in this protocol.

## Independent replay audit

A [separate checker](../../../scripts/verify_issue27_saved.py), [pinned before target execution](INDEPENDENT_CHECKER_PIN.json), imports no shared scanner and passed a [separate code/control review](INDEPENDENT_CODE_REVIEW.json). Its [controls](INDEPENDENT_CONTROLS.json) cover actual positive validation and canonical fingerprints in all four formats. After the registered run it must independently compare all 3,880 saved records against the frozen primary strings, reconstruct all forms and reproduce every evaluation field. This audit does not add readings, derive keys or query addresses.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_issue27_saved.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_issue27_saved.py --verify --result /tmp/key404-private/issue27-rerun/RESULT.json --readings /tmp/key404-private/issue27-rerun/READINGS.private.jsonl --primary analysis_outputs/continuation_20261109/george_sand_issue27/printed_lines_and_streams.json --out /tmp/key404-private/issue27-independent
```

Keep both output directories private and fresh. The independent checker reports only aggregate evidence and approved fingerprints.
