# The second-scan alignment lacks landmark support

Page 75’s ordinary print transfers closely between the two scans. Page 74’s independently fitted geometry fails the held-out checks, and neither heading half has enough landmark coverage. The registered experiment stopped before opening the faint target for scoring. The earlier pixel match remains local to the sharper scan.

| Same-face map | Calibration points | Held-out points | Forward RMS | Largest forward error | Largest inverse error |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page 74 | 8 | 4 | 8.15 low px | 15.02 low px | 18.88 high px |
| Page 75 | 11 | 11 | 0.64 low px | 1.04 low px | 1.31 high px |
| Registered limit | | | 7 low px | 12 low px | 16 high px |

The largest page 74 error is at the diffuse hill-path hook. The manual survey allows wider placement uncertainty there than at the sharp print features. The error may include landmark placement noise as well as page distortion. All points kept their registered roles. [Page 74 survey](P74_LANDMARK_SURVEY.json) · [Page 75 refinement](P75_LANDMARK_REFINEMENT.json)

The geometric support mask also fails for the previously positive regions. Neither heading half retains any sample that is within both calibration hulls, near held-out landmarks on both faces, and mirrored within the shared mask. Of the four body regions that passed in the sharper scan, the best retains 36.2% of its samples, below the 75% cutoff. Only the fifth body region has enough coverage. That region failed the original sharper-scan pixel test, and page 74’s failed validation makes it ineligible here. [Full coordinates, residuals and coverage](MEASUREMENTS.json)

The page 74 survey marks 12 candidate points on nine printed objects. The orange label supplies two nearby points above the band. The faint photograph boundary gives a visible edge without a reliable shared endpoint for a point correspondence. Both upper corners of the full sharper-scan comparison crop extend beyond even the optimistic hull built from the manual candidate boxes. [Main landmark crops](LANDMARK_CONTEXTS.png) · [Additional landmarks and edge crops](LANDMARK_EXTRA_CONTEXTS.png) · [Visual log](https://keynotfound.com/#visual-issue24-heading-scan-transfer)

The [registration commit](https://github.com/dctrpr/key-not-found/commit/7de8bffa935b0f8bb54c0a1e975167d04f8b0a84) fixes the source, landmarks, point roles, transforms and thresholds. The [registered output](REGISTERED_MEASUREMENTS.json) reproduced byte for byte but the local NumPy build emitted warnings during affine matrix application. The implementation now applies the same affine coefficients component by component and loads the image library only if a window qualifies. Two warning-free replays were byte-identical. All numeric outputs agree with the registered run to 10⁻⁹, and all gates, fractions and counts match. [Protocol and replay commands](PROTOCOL.md) · [Replay receipt](RESULT.json)

These scans do not yet give an independently validated prediction for the faint region. The failed transfer leaves physical show-through and the source layer unresolved. An independently captured pair with repeatable fiducials around the upper artwork could reopen this branch. On the existing corpus, the separate first-word boundary question still has a directly inspectable unresolved initial on page 77. [Earlier pixel match](../heading_pixel_match/RESULT.md) · [First-word boundary audit](../line_start_audit/RESULT.md)
