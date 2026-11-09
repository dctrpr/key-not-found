# O4 Frame Rescue Y/K Filter Control

Scope: control-test the tempting `Y/K` filter inside the `3-up / 1-down` rescue frame. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T01:56:11`
- Full-page signal layer codes: `YBMMMKBMYKMYBKKBMMY`
- Full-page Y/K group count: `8`
- Full-page Y/K layer codes: `YKYKYKKY`
- Full-page Y/K non-active groups: `4`
- Frame signal layer codes: `YBKKBMMY`
- Frame Y/K layer codes: `YKKY`
- Frame Y/K active target coverage: `4/4`
- Frame Y/K non-active groups: `0`
- Hard instruction hits: `[]`
- Sheet: `analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control_sheet.jpg`

## Frame Y/K Groups

| group | code | active target | hard hits | text |
|---:|---|---|---|---|
| `12` | `Y` | `buying_dip` | `-` | "buying the dip." |
| `14` | `K` | `one_billion` | `-` | $1 billion |
| `15` | `K` | `volcano_bonds` | `-` | “Volcano Bonds” |
| `19` | `Y` | `shitcoiner_heart` | `-` | shitcoiner at heart. |

## Full-Page Y/K Control

| group | code | target | active? | text |
|---:|---|---|---|---|
| `1` | `Y` | `open_heart` | `False` | Get some toxicity. Get some bitcoin. Open your heart toBitcoin. |
| `6` | `K` | `calibration_black` | `False` | Gotta be this way. Forty years of dumb post-1971 fiat moneynonsense |
| `9` | `Y` | `rancid_catnip` | `False` | by the rancid catnip of fiat money. |
| `10` | `K` | `stun_gun` | `False` | It's a stun gun to the genitals. |
| `12` | `Y` | `buying_dip` | `True` | "buying the dip." |
| `14` | `K` | `one_billion` | `True` | $1 billion |
| `15` | `K` | `volcano_bonds` | `True` | “Volcano Bonds” |
| `19` | `Y` | `shitcoiner_heart` | `True` | shitcoiner at heart. |

## Decision

- `Y/K` inside the rescue frame isolates the four active targets.
- This is not enough to unlock extraction because full-page `Y/K` has four non-active controls: `Get some toxicity...`, `Gotta be this way...`, `by the rancid catnip...`, and `It's a stun gun...`.
- The `Y/K + frame` intersection has no hard instruction hits and no source-backed permission.
- Treat it as a source-validation benchmark only, not current-scan key material.
