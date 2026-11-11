# Test the boundary of the archived first-word example

The retained archived George Sand page marks the first words of eight lines in its nine-line question. Test whether the ninth line has the same textual identity as the previous letter's first line, apart from trailing ellipsis characters, and whether it is unmarked. Confirm the two-line reply marks both first words. Use both pinned archived captures and verify the previously recorded markup digests. This recovers the role of the excluded line and distinguishes it from an arbitrary fixed-length rule. [Previous archive report](../sand_archive_context/RESULT.md)

## Issue 24 source screen

Use the frozen 151-unit print model. Compare each unit with earlier units after NFC normalization, whitespace collapse, case folding and removal of trailing spaces, periods and ellipses. Record any exact earlier-line echo. In the 142-row body model, inspect contiguous runs with the same page, section and paragraph, and report all nine-row runs and their actual color-marked row positions. Keep historical bold annotations separate. Check the known page 78 pull quote separately by comparing its four display lines with the final sentence spanning the two body rows p78r04–05. An editorial quotation with different wrapping has a distinct source role. No arbitrary omission, new reading rule or new extraction applies to Issue 24 in this screen. [Printed-unit model](../../../sources/issue24-column151/README.md) · [Parameters](PROTOCOL.json)

## One Issue 26 comparison

The earlier Q2 2022 Censorship column has an independently verified nine-line prose opener on p102, six lines and then three. The STOP callout begins outside that unit. Its ninth row is ordinary prose, with no equivalent terminal echo or exclusion mark established. The matching count motivates a single comparison. It supplies no creator rule and no association with the March 2023 reward claim. [Publisher contents](https://bitcoinmagazine.com/2022-censorship-resistant-issue) · [Page 102 source crop](../../../sources/issue26/firstword-review/p102-01-12.png)

Take the literal, verified printed first-word fields from rows 1–8 and compare them to the complete nine-row opener in printed order. Check whether the exact row choices are in the existing ledger, using its saved metadata and whole-opener baseline. This comparison examines whether removing the ninth token yields a coherent instruction with an explicit action and object. The eight-word spaced form is a word-boundary prefix of the earlier nine-word form. No new format, compact projection, variant, key or network test is run. Two fresh AI contexts review masked, reordered readings and two known controls under the frozen rubric. Qualified negatives are literal language judgments, with no exclusion of encoded instructions.

## Replay

Set `EARLIER_HTML` and `SAME_DAY_HTML` to the raw captures identified in the prior archive report. Hash mismatches stop the replay. Run from the repository root with Python 3.9 or later.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/audit_sand_terminal_echo.py \
  --earlier "$EARLIER_HTML" --same-day "$SAME_DAY_HTML" --out sand-terminal-echo.json
```
