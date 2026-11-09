# DOCM Hidden Structure Audit

Scope: inspect DOCM package structure for hidden/source instructions. Macros are not executed, and no key candidates are generated.

## BOLD.docm

- Path: `private_inputs/Desktop/BOLD.docm`
- MD5: `1c7939e59f57da61bd449c996918e7d5`
- Parts: `14`
- Creator: `PRIVATE_CONTRIBUTOR PRIVATE_CONTRIBUTOR`
- Created: `2025-01-23T22:16:00Z`
- Modified: `2025-01-24T19:41:00Z`
- VBA parts: `['word/vbaProject.bin', 'word/_rels/vbaProject.bin.rels', 'word/vbaData.xml']`
- Comments/header/footer/custom XML parts: comments `[]`, headers `[]`, footers `[]`, customXml `[]`
- Hidden runs: `0`
- Bookmarks: `0`
- Hyperlinks: `0`
- Field codes: `0`
- Annotation markers: `{'commentRangeStart': 0, 'commentReference': 0, 'ins': 0, 'del': 0}`
- Non-body instruction-hit parts: `0`
- VBA instruction strings: `7`

### VBA Printable Strings
- `private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt'`
- `Open the .txt file and read the words into the collection`
- `BIP39\ot`
- `nd read`
- `Word`
- `line`
- `word`

## Article with Fonts.docm

- Path: `private_inputs/Desktop/Article with Fonts.docm`
- MD5: `f1866ac300c0028c63cd96d42be01e53`
- Parts: `11`
- Creator: `PRIVATE_CONTRIBUTOR PRIVATE_CONTRIBUTOR`
- Created: `2025-01-06T18:26:00Z`
- Modified: `2025-01-07T00:15:00Z`
- VBA parts: `[]`
- Comments/header/footer/custom XML parts: comments `[]`, headers `[]`, footers `[]`, customXml `[]`
- Hidden runs: `0`
- Bookmarks: `0`
- Hyperlinks: `0`
- Field codes: `0`
- Annotation markers: `{'commentRangeStart': 0, 'commentReference': 0, 'ins': 0, 'del': 0}`
- Non-body instruction-hit parts: `0`
- VBA instruction strings: `0`

## Assessment

- `Article with Fonts.docm` does not expose a hidden instruction layer in package structure: no comments, hidden runs, bookmarks, hyperlinks, field codes, custom XML, or macros.
- `BOLD.docm` contains the already-known macro/highlight workflow and `BIP39\otrobip.txt` path, but no hidden Word annotation layer that tells us how to read the puzzle.
- This strengthens the prior split: use `Article with Fonts.docm` as a formatting witness, treat `BOLD.docm` as a generated working artifact, and do not mine DOCM containers for more instructions unless `otrobip.txt` or original source files appear.

## Next Best Move

- Return to external source clues: higher-resolution Canva/original layout evidence, or physical-source registration that changes what lands on page 76.
