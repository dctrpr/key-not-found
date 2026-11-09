# Lower Page 76 Mark Pointers

Scope: retest the lower page-76 visual marks as a standalone pointer/order system. This separates highlighted text boxes from true non-text brush/X marks and uses high-res page geometry only.

- Source marks: `analysis_outputs/source_audit/page76_nontext_marks.json`
- Overlay: `analysis_outputs/source_audit/lower_page76_mark_pointers_overlay.jpg`

## Classification

- M1: false positive, $1 billion grey highlighted text box; detector caught text/highlight, not a separate mark.
- M2: false positive, Volcano Bonds grey highlighted text box; detector caught text/highlight, not a separate mark.
- M3: standalone mark, box=[2172, 2619, 2544, 2884], center=[2358.0, 2751.5], PCA angle=173.75 deg, rows crossed=L28 `loan and get rid of those leeches. I tagged Mike`; L29 `Novogratz in the tweet, figuring he could sell a`; L30 `bunch to his Wall Street crony pals, but so far he`; L31 `hasn't moved on it. I don't really trust that guy.` [bold: I don't really trust that guy]
- M4: standalone mark, box=[1827, 3003, 2120, 3182], center=[1973.5, 3092.5], PCA angle=-168.84 deg, rows crossed=none

## Pointer Reads

### M3

- Horizontal left-row candidates:
  - row 31 / L30: `bunch to his Wall Street crony pals, but so far he`; nearest-left words `he far so but pals, crony Street Wall his to bunch`
  - row 30 / L29: `Novogratz in the tweet, figuring he could sell a`; nearest-left words `sella could he figuring tweet, the in Novogratz`
  - row 32 / L31: `hasn't moved on it. I don't really trust that guy.` [bold: I don't really trust that guy]; nearest-left words `guy that trust really don't I it. on moved hasn't`
  - row 29 / L28: `loan and get rid of those leeches. I tagged Mike`; nearest-left words `Mike tagged I leeches. those of rid get and loan`
- PCA-axis left/down read: `guy that trust really a he's because Maybe`
- PCA-axis opposite read: `-`

### M4

- Horizontal left-row candidates:
  - row 33 / L32: `Maybe because he's a shitcoiner at heart.` [orange: shitcoiner at heart]; nearest-left words `siukbeodmensertslveaarty a he's because Maybe`
  - row 32 / L31: `hasn't moved on it. I don't really trust that guy.` [bold: I don't really trust that guy]; nearest-left words `guy that trust really don't I it. on moved hasn't`
  - row 31 / L30: `bunch to his Wall Street crony pals, but so far he`; nearest-left words `he far so but pals, crony Street Wall his to bunch`
  - row 30 / L29: `Novogratz in the tweet, figuring he could sell a`; nearest-left words `sella could he figuring tweet, the in Novogratz`
- PCA-axis left/down read: `siukbeodmensertslveaarty a I it. on moved hasn't bunch`
- PCA-axis opposite read: `-`

## Assessment

- M1 and M2 are not standalone symbols; they are the detected black/grey highlighted text around `$1 billion` and `Volcano Bonds`.
- The true marks, M3 and M4, sit at the right/lower edge of the same El Salvador / Novogratz / shitcoiner corridor, so they reinforce the region selection.
- They do not provide a clean independent order: horizontal reads return ordinary adjacent prose, and the principal-axis rays either hit no text or clipped normal words.
- This closes the lower page-76 mark-as-pointer branch for now. Keep page 76 as the target surface, but the missing selector is still outside these lower brush/X marks.
