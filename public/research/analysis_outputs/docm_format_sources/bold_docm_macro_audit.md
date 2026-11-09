# BOLD.docm Macro Provenance Audit

Scope: inspect macro-enabled Word-package metadata and embedded VBA strings without executing macros.

## Sources

- `BOLD.docm`: `private_inputs/Desktop/BOLD.docm`
  - MD5: `1c7939e59f57da61bd449c996918e7d5`
  - embedded VBA project: `True`
  - embedded VBA data: `True`
  - created by: `PRIVATE_CONTRIBUTOR PRIVATE_CONTRIBUTOR`
  - created: `2025-01-23T22:16:00Z`
  - modified: `2025-01-24T19:41:00Z`
- `Article with Fonts.docm`: `private_inputs/Desktop/Article with Fonts.docm`
  - MD5: `f1866ac300c0028c63cd96d42be01e53`
  - embedded VBA project: `False`
  - embedded VBA data: `False`
  - created by: `PRIVATE_CONTRIBUTOR PRIVATE_CONTRIBUTOR`

## Macro Evidence

- `word/vbaData.xml` references `HighlightWordsFromTextFile`: `True`
- Relevant printable strings from `word/vbaProject.bin`:
  - `Set the path to the .txt file containing the words`
  - `private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt'`
  - `Initialize the collection to store words`
  - `Open the .txt file and read the words into the collection`
  - `Reference the current document`
  - `Loop through the words in the collection`
  - `Highlighting complete!`
  - `Error reading file. Please check the file path.`
  - `tWordsF`
  - `.txt`
  - `BIP39\ot`
  - `HighlightWordsFromTextFile`
  - `wordsList`
  - `HighlightColorIndex`

## Referenced Word List Search

- Macro-referenced path: `private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt`
- Search roots checked: `private_inputs/Desktop, .`
- Local `otrobip.txt` matches found: `0`

## Assessment

- `BOLD.docm` is probably not an original article-format source. It appears to be a generated/highlighted working document made by a macro that reads a separate text file of words.
- The folder name `BIP39` and file name `otrobip.txt` suggest this document may highlight BIP39-like words, but the actual word list file was not recovered locally.
- Do not use `BOLD.docm` as proof that the puzzle's original bolding is BIP39-based.
- Use `Article with Fonts.docm` as the stronger Word-level formatting witness because it has no embedded VBA project and preserves font/highlight layers directly.
