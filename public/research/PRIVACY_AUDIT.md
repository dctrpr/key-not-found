# Public-release privacy audit

This is a deliberately curated derivative, not a filesystem dump. The original private workspace was not modified.

## Included and transformed

- 1495 relevant text/code/result files were retained at their portable relative paths.
- 189 historical files required textual redaction or portable-path replacement. The list in `release-build-summary.json` contains public relative filenames only.
- Two scan PDFs were rebuilt without original Info/XMP, OCR wrappers, annotations, attachments, document history or original filenames embedded in metadata.
- JPEG EXIF/private APP/comment segments were stripped. The decoder output before/after was compared byte-for-byte for the PDF/runtime source scans. Website preview JPEGs are separately recompressed and clearly labeled.
- Public creator identities, article subjects and printed artwork credits remain. Private contributor labels and local/account context were generalized.

## Excluded

- Unrelated puzzle trees, package dependencies, virtual environments, compiled OCR executables, caches, Git state, shell/run logs and environment files.
- Private community summaries/screenshots, private annotation boards, private app consultation records and local migration/filesystem inventories.
- All raw third-party tracking HTML, session-bearing pages and unreviewed diagnostic raster screenshots/exports. Relevant text/JSON results remain where safe; reproducible visuals can be regenerated from public inputs.
- Reconstructed Word inputs and other unavailable/private external inputs. Reports disclose their source limits; no replacement evidence was fabricated.

Exact exclusion categories/counts are in `release-build-summary.json`. Counts there include dependencies and duplicates and are not experiment counts.

## Machine checks

The release was scanned for configured private identity/account strings, personal home-directory references, private discussion/annotation service URLs, contact addresses, common access-token formats and forbidden input classes. Structured JSON was parsed and recursively sanitized. All released PDF document metadata and released source-image metadata were inspected.

The machine-readable audit records counts without reproducing the private names/pattern values. Successful matches were resolved before the final file manifest was created. No filesystem ownership, original file timestamps, extended attributes, local repository history or private publication account is part of the case data.

A public Git repository and hosting account can have separate account-level identity surfaces. This audit covers these corpus bytes; publishing configuration must be reviewed separately. No claim of mathematical anonymity or third-party source authenticity is made.

## Historical redactions

Historical scripts/logs are preserved as **redacted public copies**. A replacement such as `private_inputs/` identifies a missing or withheld input, not an invitation to scan a reader's home directory. Assertions in older logs may be obsolete; the curated catalog and latest reports identify known errors.

[DATA_LICENSE.md](DATA_LICENSE.md) separates contributor-owned code from third-party article/artwork rights.
