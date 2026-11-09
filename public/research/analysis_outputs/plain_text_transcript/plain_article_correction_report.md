# Plain Article Text Correction Report

Scope: integrate the latest user-supplied plain text and correct it against the stronger `Article with Fonts.docm` witness. This is a text-source cleanup pass only; no key derivation was run.

## Outputs

- raw user plain text: `analysis_outputs/plain_text_transcript/user_plain_article_latest.txt`
- fixed body text: `analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt`
- fixed body plus visual signature: `analysis_outputs/plain_text_transcript/canonical_plain_article_with_signature.txt`
- JSON report: `analysis_outputs/plain_text_transcript/plain_article_correction_report.json`

## Corrections Applied / Registered

- `Bitcoin is toxic af` -> `BITCOIN IS TOXIC AF` (found): Article title is uppercase in the scan and DOCM witness.
- `Really? Yes` -> `Really? Yes.` (found): DOCM witness includes the period after Yes.
- `hands I\nn the muck` -> `hands in the muck` (found): The raw plain text split the word `in` across lines incorrectly.
- `puts and end` -> `puts an end` (found): DOCM/Markdown witness agree on `an end`.
- `"buying the dip".` -> `"buying the dip."` (found): DOCM witness places the period inside the quote.
- `collateralized to pay off the IMF` -> `collateralized “Volcano Bonds” to pay off the IMF` (found): The raw plain text omitted the highlighted `Volcano Bonds` phrase.
- `At this rate the whole` -> `At this rate, the whole` (found): DOCM witness includes the comma.
- `big blockers` -> `Big blockers` (found): DOCM witness capitalizes the sentence start.
- `Full stop.` -> `Full Stop.` (found): DOCM witness capitalizes both words.
- `Every single one of the bitcoin wannabes- ...` -> `EVERY SINGLE ONE OF THE BITCOIN WANNABES - ...` (registered): This block is all uppercase in the scan and DOCM witness.
- `It's guaranteed, mathematical certainty.` -> `It's a guaranteed, mathematical certainty.` (found): DOCM witness includes `a`.
- `bitcoin was designed` -> `Bitcoin was designed` (found): DOCM witness capitalizes Bitcoin at this sentence position.
- `gargantually wasteful` -> `gargantuanly wasteful` (found): DOCM witness has `gargantuanly`.
- `requires printing and wars` -> `requires money printing and wars` (found): The raw plain text omitted `money`.
- `cost 2 trillion fiat cuck bucks` -> `cost $2 trillion fiat cuck-bucks` (found): DOCM witness includes the dollar sign and hyphenated `cuck-bucks`.
- `Bitcoin fixes all this` -> `BITCOIN FIXES ALL THIS` (found): This lead phrase is all uppercase in the scan and DOCM witness.
- `Remove the war incentive and you remove` -> `Remove the war incentive, and you remove` (found): DOCM witness includes the comma.
- `It's fact baked` -> `It's a fact baked` (found): DOCM witness includes `a`.
- `In so doing our energy consumption` -> `In so doing, our energy consumption` (found): DOCM witness includes the comma.
- `gets monetized and for the first time in our existence` -> `gets monetized for the first time in our existence` (registered): The raw plain text inserted an extra `and`.
- `smile- virtually nothing` -> `smile - virtually nothing` (found): DOCM witness uses spaced hyphen.

## Assessment

- The fixed text should replace the latest raw plain copy for exact text, word-count, and line-level selector work.
- The highest-impact raw-copy omissions were `Volcano Bonds`, `money`, the `$` in `$2 trillion`, and the extra `and` in `gets monetized for the first time`.
- Keep both fixed variants: body-only for DOCM-derived text experiments, and with-signature when testing scan-visible text including the page-79 `MAX KEISER` signature.
- This pass does not change the current conclusion: the missing step is still a selector/registration rule, not another broad hashing branch.

## Diff Preview

`--- `
`+++ `
`@@ -1,6 +1,10 @@`
`-Bitcoin`
`-is`
`-toxic`
`-af`
`+OVERDOSE`
`+with`
`+Max`
`+Keiser`
`+BITCOIN`
`+IS`
`+TOXIC`
`+AF`
` Here's`
` the`
`@@ -28,4 +32,5 @@`
` ?`
` Yes`
`+.`
` The`
` markets`
`@@ -290,6 +295,5 @@`
` bare`
` hands`
`-I`
`-n`
`+in`
` the`
` muck`
`@@ -488,5 +492,5 @@`
` bitcoin`
` puts`
`-and`
`+an`
` end`
` to`
`@@ -550,6 +554,6 @@`
` the`
` dip`
`+.`
` "`
`-.`
` I`
` tweeted`
`@@ -586,4 +590,8 @@`
` earnings`
` collateralized`
`+“`
`+Volcano`
`+Bonds`
`+”`
` to`
` pay`
`@@ -696,4 +704,5 @@`
` this`
` rate`
`+,`
` the`
` whole`
`@@ -708,4 +717,5 @@`
` months`
` .`
`+(`
` Sorry`
` Bhutan`
`@@ -737,5 +747,5 @@`
` lately`
` ?`
`-big`
`+Big`
` blockers`
` got`
`@@ -817,13 +827,13 @@`
` .`
` Full`
`-stop`
`-.`
`-Every`
