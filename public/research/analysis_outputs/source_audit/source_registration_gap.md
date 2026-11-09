# Source Registration Gap

Scope: compare high-res `magazine.pdf` page images against the OCR PDF page images. This checks geometry risk only; it does not generate key candidates.

- Contact sheet: `analysis_outputs/source_audit/source_registration_gap_contact_sheet.jpg`

## Findings

- p75: highres=(2544, 3264) ocr=(2040, 2805) contentAspect=0.77939->0.72727 contentMap=x0.809845,y0.867884 highlightMap=x0.793824,y0.796122 content-vs-highlight delta mean/max=117.73/209.94 px
- p76: highres=(2544, 3264) ocr=(2040, 2805) contentAspect=0.77053->0.72727 contentMap=x0.811133,y0.859375 highlightMap=x0.795898,y0.795477 content-vs-highlight delta mean/max=125.89/227.67 px
- p77: highres=(2544, 3264) ocr=(2040, 2805) contentAspect=0.77941->0.72727 contentMap=x0.801887,y0.859375 highlightMap=x0.791053,y0.815008 content-vs-highlight delta mean/max=96.04/161.6 px
- p78: highres=(2544, 3264) ocr=(2040, 2805) contentAspect=0.77396->0.72727 contentMap=x0.809524,y0.861486 highlightMap=x0.79513,y0.797685 content-vs-highlight delta mean/max=128.76/222.11 px
- p79: highres=(2544, 3264) ocr=(2040, 2805) contentAspect=0.76961->0.72727 contentMap=x0.812102,y0.859375 highlightMap=x0.788705,y0.7941 content-vs-highlight delta mean/max=116.12/209.82 px
- p80: highres=(2544, 3264) ocr=(2040, 2805) contentAspect=0.77757->0.72727 contentMap=x0.803783,y0.859375 highlightMap=x1.100699,y2.730479 content-vs-highlight delta mean/max=2729.73/4378.13 px

## Assessment

- The high-res and OCR sources are not related by one clean page-size resize. Page rotation, crop, and non-uniform scaling all matter.
- Content-box mapping and orange-highlight mapping differ by hundreds of OCR pixels on several pages, which is too large for letter-level fold/mirror extraction.
- Existing OCR text can still label regions, but final geometry should be done directly on high-res images or a physical scan.
- Next best move: build the mirror-writing selector directly on high-res page-76 corridor geometry, then use OCR only after the target region is identified.
