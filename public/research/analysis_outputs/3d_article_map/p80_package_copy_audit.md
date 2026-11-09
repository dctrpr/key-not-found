# Page-80 Package Copy Audit

Scope: manual transcription and low-parameter selector checks for page-80 graphic/package copy. No private-key candidates are generated.

- Source image: `analysis_outputs/3d_article_map/page_80_upright.jpg`

## Manual Transcription

- top_right: `FAKE AD` initials=`FA` lasts=`ED` numbers=[]
- cap_front: `5 SYMPTOM RELIEF` initials=`5SR` lasts=`5MF` numbers=[5]
- product: `Bitcoin FixesThis` initials=`BF` lasts=`ns` numbers=[]
- claim_1: `100% Proof of Work Liquid` initials=`1PoWL` lasts=`0ffkd` numbers=[100]
- claim_2: `Fiat Humiditus Reliever / Anticentralization` initials=`FHRA` lasts=`tsrn` numbers=[]
- bottle_front: `5 SYMPTOM RELIEF` initials=`5SR` lasts=`5MF` numbers=[5]
- symptoms: `NAUSEA HEARTBURN INDIGESTION UPSET STOMACH SHITCOINS` initials=`NHIUSS` lasts=`ANNTHS` numbers=[]
- volume_visible_likely: `16 FL OZ (473 mL)` initials=`1FO4m` lasts=`6LZ3L` numbers=[16, 473]
- volume_crop_recorded: `6 FL OZ (473 mL)` initials=`6FO4m` lasts=`6LZ3L` numbers=[6, 473]
- footer: `TOXIC BTB` initials=`TB` lasts=`CB` numbers=[]
- page_number: `80` initials=`8` lasts=`0` numbers=[80]

## Streams

- `package_all_initials`: `FA5SRBF1PoWLFHRA5SRNHIUSS1FO4m6FO4mTB8`
- `package_all_lasts`: `ED5MFns0ffkdtsrn5MFANNTHS6LZ3L6LZ3LCB0`
- `numbers_joined`: `5100516473647380`
- `numbers_csv`: `5,100,5,16,473,6,473,80`
- `known_page76_group_initials`: `GbbI$`
- `symptom_initials`: `NHIUSS`
- `claims_initials`: `1PoWLFHRA`

## Numeric Checks

- `5` matches known page-76 target group count: `True`
- Known page-76 group initials: `GbbI$`
- `16` as page-76 line: `laundering lobotomy. It’s a stun gun to the genitals.`
- Volume ambiguity: full-page visual and 473 mL imply `16 FL OZ`; crop-only source records `6 FL OZ` because the left edge is clipped.
- 1-based page-76 word checks:
  - `5` -> `some`
  - `16` -> `ghetto`
  - `80` -> `Peter`
  - `100` -> `dulled`
  - `473` -> ``

## Assessment

- The package copy is useful as an unresolved visual layer, but it does not contain a direct instruction.
- The strongest low-parameter link is count-based: '5 SYMPTOM RELIEF' appears twice and the label lists exactly five symptoms: nausea, heartburn, indigestion, upset stomach, and shitcoins. This matches the five page-76 target groups from the reflected graph.
- The volume is visually and semantically likely '16 FL OZ (473 mL)'; an existing crop-only source records '6 FL OZ' because the left edge is clipped. If using p80 numbers, keep this ambiguity registered.
- The number 16 lands on the page-76 line containing 'It's a stun gun to the genitals.', but this is not enough by itself because other package numbers do not produce a coherent index stream.
- Treat p80 as thematic/count support unless a source/physical alignment shows the bottle copy lining up with another page.
