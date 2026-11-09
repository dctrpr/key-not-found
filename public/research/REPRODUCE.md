# Reproduce the released checks

Use Python 3.12 or newer for historical scripts, and a current Node.js release supported by the locked dependencies. Work from the extracted corpus root. No local account, original home directory, or private application connection is required for the current offline checks.

```sh
npm ci
python3 -m venv .venv
.venv/bin/pip install pillow numpy pymupdf
python3 scripts/continue_corrected_duplex.py
.venv/bin/python scripts/continuation_corrected_inverted_masks.py
python3 scripts/continuation_audit_phrase_boxes.py
node analysis_outputs/continuation_20261109/fresh_cryptanalysis/transcript_mirror_probe.js
node analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.js
python3 scripts/continuation_george_sand_highlight_lines.py
python3 scripts/continuation_numeric_inventory.py
```

Use the virtual environment's Python executable for scripts importing Pillow, NumPy or PyMuPDF. Run a single check at a time if it rewrites one of its own result files. Preserve the released snapshot before rerunning; newly produced output will have different check times and may reflect changed external state.

## Read-only address checks

These explicit commands query public address services and never submit transactions:

```sh
node scripts/continue_printed_line_ascii_keys.js --check
node scripts/continue_printed_line_ascii_keys.js --firstword-sha256 --check
node scripts/continuation_george_sand_minikey_check.cjs
node scripts/continuation_numeric_activity.cjs
```

Successful cached address responses may be reused by these historical checkers. A fresh audit should preserve the old result and run against a separate copy so that cached results cannot be mistaken for a new live observation. HTTP failures are not zero balances. The released results retain their recorded timestamps and response scopes.

The 5-address-family derivation was independently checked against public scalar 1 vectors, including independent Bech32/Bech32m and TapTweak calculations. These address encodings still do not prove that an arbitrary source extraction is intentional.

## Historical code and unavailable inputs

The archive includes relevant scripts, candidate streams and reports for review. Some older checks depend on reconstructed Word font annotations, private investigator notes, comparison scans not present in the source set, original PDF byte hashes, or host-specific OCR facilities. Those inputs were not silently replaced with invented evidence. A historical script that names `private_inputs/` requires an unreleased or unavailable input and is not promised to rerun completely from this snapshot.

Original absolute home-directory paths have been converted to corpus-relative paths or explicit `private_inputs/` placeholders. Private home-directory scanning is disabled in released copies. Dependencies, compiled binaries, caches, private screenshots and unreviewed diagnostic raster exports are excluded. Generated geometry pictures can generally be recreated from the published pages and scripts; exact identity-sensitive or unavailable inputs remain unavailable.

Metadata-clean PDFs intentionally have different file hashes and no original OCR wrapper. Their cleaned JPEG streams preserve decoded pixels. The public web-preview JPEGs are recompressed; use the scan PDFs or preserved runtime source aliases for pixel-level work. See `sources/provenance.json`.

## Verify integrity

```sh
sha256sum -c SHA256SUMS
# macOS alternative:
shasum -a 256 -c SHA256SUMS
```

SHA256SUMS covers the payload files and both generated catalogs/manifests. It excludes its own bytes, as a checksum file cannot contain its own fixed hash. `files.json` indexes payload files; `manifest.json` adds the file-catalog hash. Dependency installation is outside that manifest.
