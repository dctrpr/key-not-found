# The announcement photos reuse two views

The white-background image in the March 2023 announcement shares the upper scene of a same-day reply: the two people, their pose and the open OVERDOSE spread. A separate reply showing the closed magazine matches a February 2022 photo from the handoff to Bukele. These images help identify the article and the edition. Counting their repetitions as separate evidence would overstate the case for a particular page or reading order. [Announcement](https://x.com/maxkeiser/status/1632068898169450497) · [Open-spread reply](https://x.com/maxkeiser/status/1632069025391075328) · [Cover reply](https://x.com/maxkeiser/status/1632134737639907328) · [February photo post](https://x.com/elsalvador/status/1492002766306357265)

## Measured matches

Visual inspection suggested both matches. The [frozen comparison](PROTOCOL.json) used three foreground crops to choose one uniform scale and translation per pair. The script then measured four held-out crops and compared each with four equally displaced controls. The held-outs did not set the transform or the thresholds.

| Pair | Calibration correlation | Held-out matches | Held-out correlation range among passes |
| --- | ---: | ---: | ---: |
| Announcement image and open-spread reply | 0.957 | 3 of 4 | 0.928–0.985 |
| Cover reply and February 2022 news photograph | 0.965 | 4 of 4 | 0.946–0.984 |

The trousers crop failed in the first pair. The measurement supports shared foreground content in the matched upper regions and one sleeve. The whole image has differences, including the removed background. It cannot date the open-spread exposure on its own. Matching clothing and the room make the February visit a plausible origin. The exact open-spread frame did not appear among the six contemporaneous post photos checked. The cover-reply match spans the room, clothing and foreground under one resize. [Full crop and control scores](MEASUREMENTS.json) · [February coverage](https://dev.diarioelsalvador.com/dedinero/periodista-y-criptoinversor-max-keiser-entrega-al-presidente-nayib-bukele-una-edicion-de-bitcoin-magazine-dedicada-a-el-salvador/190346)

## The reply structure

The current public post metadata confirms seven photos across the announcement and five replies. The first open-spread reply and the cover reply both answer the announcement. The car image answers the open-spread reply. The later two images answer the announcement. The five replies have photo links without additional prose. This is a branched reply structure. A linear chronological image order is a research convention. The older mapping from image subjects to page 76 remains a thematic reading. No reply names a printed row, starting side or operation. [Exact post IDs and parent links](SOURCE_POSTS.json) · [Earlier mapping](../../external_clues/announcement_media_order_selector/announcement_media_order_selector.md)

The car image also borrows from the desert convertible scene in *Fear and Loathing in Las Vegas*. The bucket hat, both floral shirts, the driver’s sunglasses, the front headrests and the upper visor match the scene. The back-seat figure and the colored objects differ. The comparison identifies the source scene by visual details. The reference still shows a different instant, so the exact frame and origin of the added material remain open. The earlier “El Salvador context” label for this image is unsupported. The drug-film reference is compatible with the article’s OVERDOSE motif without selecting a particular page. [Keiser’s car image](https://pbs.twimg.com/media/FqaYnkpaMAEuMC5.jpg) · [Reference frame](https://www.listal.com/viewimage/1958143h) · [Cinematographer’s production account](https://theasc.com/article/fear-and-loathing-in-las-vegas-gonzo/)

## A separate timestamp check

The March Bitcoin Beach interview captions say “play back the tape to minute 17” at 1:24:40, amid a comparison of Bitcoin and gold. At 17:00–17:31 the same upload discusses Bukele and Bitcoin as a mirror. A more direct comparison to gold appears around 9:00. The original player showed Keiser at the microphone at 17:13, 17:31 and 1:24:42. No magazine or printed instruction was visible in those three frames. These are visual spot checks, with the callback wording still based on captions. The intended timestamp and any puzzle connection remain unverified. [Caption review](../bitcoin_beach_interview/RESULT.md) · [Minute 17](https://www.youtube.com/watch?v=h0y-iZaSpCc&t=1020s) · [Callback](https://www.youtube.com/watch?v=h0y-iZaSpCc&t=5080s)

The next retained-source test can use a print control within page 78. The same sentence appears in body type and in the tilted display quote. Compare fixed asymmetric glyphs in the two copies under ordinary and reflected orientations. Use the corresponding printed glyphs across scans to verify that the comparison can distinguish handedness before applying it to the quote. [Repeated sentence and source crop](../sand_terminal_echo/RESULT.md)

## Replay

Run from the repository root. The asset list records the exact public source URLs and byte hashes. All thresholds and bounds were saved before running the pixel comparison. Two runs reproduced the scores byte for byte.

```sh
protocol=public/research/analysis_outputs/continuation_20261111/announcement_photo_lineage/PROTOCOL.json
assets=$(mktemp -d)
jq -r '.assets[] | [.file, .url] | @tsv' "$protocol" |
  while IFS="$(printf '\t')" read -r file url; do
    curl --fail --silent --show-error --location "$url" --output "$assets/$file" || exit
  done
python3 public/research/scripts/check_announcement_photo_lineage.py --assets "$assets" --out lineage.json
```
