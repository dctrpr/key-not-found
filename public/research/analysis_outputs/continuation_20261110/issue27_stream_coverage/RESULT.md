# Issue 27 replay: one weak checksum lead

Completed **2026-11-10T09:13:14.337Z**. **The puzzle remains unsolved.**

The exact 1,940 saved Orange Party readings and their pre-existing character reversals produced 3,880 labelled records and 3,709 distinct exact/whitespace-compacted forms. No text, OCR, source scope or selection rule was repaired for this replay.

| Format | Shaped occurrences | Distinct shaped strings | Valid records |
| --- | ---: | ---: | ---: |
| Mainnet WIF | 57 | 15 | 0 |
| 22/30-character minikey | 1,016 | 205 | 1 |
| Bounded 64-hex scalar | 0 | 0 | 0 |
| Unfiltered English BIP39 | 0 | 0 | 0 |

The sole pass is a **22-character minikey**, identified publicly only by its domain-separated fingerprint: `d0ad21f0839baa35c7789a8a1de80408bd9eba6e8a0102a2a055bf4af8100203`. Its format check is only eight bits. One pass among 205 distinct shaped strings is compatible with chance; neither a key's intended use nor the prize claim has been authenticated. The result does not reprint the selected value, private scalar or revealing source locators. Raw lead files stay outside the public archive. The underlying saved readings are public and reproducible; this is not a secrecy guarantee for a value extracted from them.

The [separately implemented replay audit](INDEPENDENT_CHECK.json) verified every saved record against the frozen primary source and reproduced the complete evaluation, including the positive fingerprint. It imports no shared scanner. [Controls and code review](INDEPENDENT_CODE_REVIEW.json) preceded target execution.

## Scope and next check

This is a completed validator-coverage replay with a private-review lead, **not a complete negative or a solution**. It closes the historical omission of embedded minikey and BIP39 checks for these saved readings. WIF failed in all 15 shaped strings; the other two formats had no shaped records under the fixed tokenizer and boundary rules.

The unchanged OCR model has uncertain interiors and line ends. This does not exhaust the column, every George Sand interpretation or any whole cipher family. The retained Fall 2022 Orange Party column is relevant to the broad December plural-key post; it is not authenticated as the March 2023 Issue 24 / 20-BTC target.

A separately registered follow-up will check only this frozen lead through five standard mainnet address constructions, with independent Python/Node agreement and two providers. No address construction or history query was part of this extraction. No wallet import, signing or transaction occurred.

## Registration and reproduction

The protocol, pinned inputs and implementations were public before execution in commit [`070f8b712d9fd5b6b6fa3f5355d612fcbaa7f192`](https://github.com/dctrpr/key-not-found/commit/070f8b712d9fd5b6b6fa3f5355d612fcbaa7f192). See the [protocol and exact reproduction commands](PROTOCOL.md), [machine result](RESULT.json), [independent audit](INDEPENDENT_CHECK.json) and [source scans/register](../../comparison_articles/overdose_style_uniqueness/issue27/SOURCE_REGISTER.md). Keep rerun reading files and any raw lead private. Numbers count correlated readings and format checks, not independent puzzle theories.
