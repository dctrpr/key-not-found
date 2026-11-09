# Cyan `MNBILLION` Scan Visibility Audit

Scope: check whether the cyan-highlighted `MNBILLION` layer from `Article with Fonts.docm` is actually visible in the high-resolution magazine scan. No key derivation was run.

## DOCM Cyan Runs

- run 2 p75 para 1: `M` font=`Typeka` bold=True
- run 42 p75 para 21: `N` font=`Typeka` bold=False
- run 263 p78 para 123: `BILLION` font=`Typeka` bold=False

- Combined cyan letters: `MNBILLION`

## Scan Cyan Counts

- p75: loose=0 strict=0 of 8303616 pixels
- p76: loose=0 strict=0 of 8303616 pixels
- p77: loose=0 strict=0 of 8303616 pixels
- p78: loose=5 strict=0 of 8303616 pixels
- p79: loose=0 strict=0 of 8303616 pixels
- p80: loose=0 strict=0 of 8303616 pixels

## Target Region Checks

- p75 visible word box: Nocoiners: loose=0 strict=0 pixels in box `[1348, 1607, 1548, 1652]`
- p76 grey target: $1 billion: loose=0 strict=0 pixels in box `[412, 2769, 814, 2838]`
- p78 orange crop: America left $85: loose=0 strict=0 of 119890 pixels
- p78 orange crop: BILLION / $2 trillion: loose=0 strict=0 of 400488 pixels

## Assessment

- The DOCM cyan stream is real as document formatting: `MNBILLION`.
- It is not scan-visible. Under a generous cyan-highlighter threshold, pages 75, 76, 77, 79, and 80 contain zero cyan-like pixels; page 78 has only five loose-threshold pixels and zero strict-threshold pixels.
- The relevant text regions checked directly (`Nocoiners`, p76 `$1 billion`, and p78 `$85/BILLION` orange crops) contain zero cyan pixels.
- Conclusion: do not use cyan as a printed highlight/geometry selector. Keep it as a low-priority DOCM anomaly only if the Word formatting file is later proven to be an original puzzle source.
- Next best move: stay on scan-visible evidence: orange/grey highlights, Typeka variants, page-76 corridor, and improved physical/high-res registration.
