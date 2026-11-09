# Open-Heart Capsule Rule Audit

Scope: test the proposed O-K-K-O `open your heart` capsule rule as a source-backed R3 candidate. No key derivation, hashing, WIF, seed/address checks, BIP39, or brute force were run.

- Created: `2026-06-09T23:04:54`
- Proposal: `r3_candidate_rules.md`
- Sheet: `analysis_outputs/source_audit/open_heart_capsule_rule/open_heart_capsule_rule_sheet.jpg`
- Fingerprint: `visualQuartets=34|obbo=3|issue24Obbo=3|indObbo=0|activeBridgeWords=13|maxNonactiveObboBridgeWords=0|maxAdjacentKkBridgeWords=2|uniqueBridge=1|sourceR3=0|triggers=0/9|selector=0`

## Visual Control Counts

- Total visual quartet windows checked from body-highlighter grammar: `34`.
- O-K-K-O / OBBO windows: `3`.
- Issue 24 OBBO windows: `3`.
- Independent-control OBBO windows: `0`.
- Existing broader Y/K controls: `70` full-page combinations, `11` YKKY combinations, `1` contiguous sliding YKKY window.
- Caveat: the proposal's referenced `715-quartet` control set was not located as a named artifact; this pass uses the existing visual/body-highlighter and Y/K quartet controls.

## OBBO Bridge Rows

| page | index | active-like | bridge words | source R3 | content hits | bridge text |
|---:|---:|---|---:|---|---|---|
| `76` | `7` | `yes` | `13` | `no` | `collateralized, sell, bitcoin, sell` | `in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized` |
| `75` | `2` | `no` | `0` | `no` | `-` | `-` |
| `76` | `2` | `no` | `0` | `no` | `-` | `-` |

## Adjacent K-K Controls

| label | page | bridge words | source R3 | content/action hits | unit hits | bridge text |
|---|---:|---:|---|---|---|---|
| `p75_split_black` | `75` | `0` | `no` | `-` | `-` | `-` |
| `p76_upper_split_black` | `76` | `0` | `no` | `-` | `-` | `-` |
| `p76_active_bridge` | `76` | `13` | `no` | `collateralized, sell` | `-` | `in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized` |
| `p78_kk_1` | `78` | `2` | `no` | `-` | `-` | `and requires` |
| `p78_kk_2` | `78` | `1` | `no` | `-` | `-` | `and` |

## Decision

- Result: `partial_unique_selector_no_downstream_r3`.
- Active bridge uniquely substantive: `True`.
- Source-backed R3 / selector unlocked: `False` / `False`.
- Max non-active OBBO bridge words / adjacent K-K control bridge words: `0` / `2`.
- Reason: The proposed capsule operation is a useful partial selector: among the checked OBBO windows, the lower page-76 active window is the only one with a substantive black-to-black bridge, and that bridge contains the pre-registered `should sell` convergence. It still does not supply a source-backed extraction unit/order such as word, letter, line, edge, first/last, or a hard read/take/extract instruction, so it cannot unlock key material by itself.

## Next Move

If pursuing this branch, test whether the selected bridge's `should sell` phrase is named by an external/source clue as a unit/order operation. Without that, keep the capsule rule as a target selector only.
