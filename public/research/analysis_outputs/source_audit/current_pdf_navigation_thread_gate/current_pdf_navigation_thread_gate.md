# Current PDF Navigation / Article Thread Gate

Scope: inspected the current PDFs for navigation and article-thread carriers: outlines/bookmarks, page labels, named destinations, open actions, page modes, article threads, page beads, and page-level navigation keys. No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T20:44:06`
- PDFs / pages: `3` / `24`
- TOC entries / outline xrefs / page labels / named destinations: `0` / `0` / `0` / `0`
- Catalog navigation signal PDFs / page signal rows / page bead rows: `2` / `0` / `0`
- Links / embedded-file names: `0` / `0`
- Raw structural token mentions: `6`
- Strict navigation hits / context hits: `0` / `0`
- Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`
- Fingerprint: `pdfs=3|pages=24|toc=0|outlines=0|labels=0|dests=0|catalogSignalPdfs=2|pageSignals=0|beads=0|links=0|rawTokens=6|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | pages | TOC | labels | named dests | catalog signals | page signal rows | beads | links | strict hits |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| `magazine.pdf` | `8` | `0` | `0` | `0` | `-` | `0` | `0` | `0` | `-` |
| `keyser bitcoin .pdf` | `8` | `0` | `0` | `0` | `Names` | `0` | `0` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `8` | `0` | `0` | `0` | `Names` | `0` | `0` | `0` | `-` |

## Raw Structural Mentions

| PDF | raw token counts |
|---|---|
| `magazine.pdf` | `{}` |
| `keyser bitcoin .pdf` | `{"/Dests": 1, "/Names": 2}` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `{"/Dests": 1, "/Names": 2}` |

## Decision

- `current_pdf_navigation_thread_no_source_order_carrier`.
- The current PDFs expose no bookmarks/outlines, page labels, named destinations, article threads, page beads, open actions, page modes, or non-empty navigation order structures that could supply a read order.
- The few raw `/Names`/`/Dests` mentions belong to the already-known empty derivative name tree; they do not contain strict instruction/context text.
- Do not reopen current-PDF navigation or article-thread metadata as original-layout instruction evidence.

## Next Move

- Highest-value direction remains a distinct physical/original-layout/source asset or raw clue wording that explicitly supplies unit, order, and transform.
