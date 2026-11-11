# Page 74 faint heading and page 75 comparison

The pale heading in the reflected page 74 crop resembles the page 75 heading in word spacing, size and upward slope. Fainter rows below remain too weak for a dependable reading. The resemblance is consistent with show-through. The print layer, optical mechanism and physical displacement remain unresolved. A single viewer made this qualitative comparison at 2026-11-11T00:23:32.676Z and recognized no distinct reading instruction.

Both 1180 × 800 exhibits come from the pinned higher-resolution scan. Decode the embedded JPEG to RGB and transpose 180° to get the 2544 × 3264 upright frame. The boxes are half-open XYXY coordinates in that frame. The page 74 exhibit applies an exact horizontal flip after cropping. The page 75 crop uses the corresponding nominal coordinates and clips the far-right end of its heading. [Pinned source](../../../magazine.pdf)

| Printed page | Exhibit | Upright source box | Exhibit orientation | PNG SHA-256 |
| --- | --- | --- | --- | --- |
| 74 | [p74-faint-heading-reflected.png](exhibits/p74-faint-heading-reflected.png) | `[1224, 300, 2404, 1100]` | horizontal-mirror | `0d1bb6246cb5f7f2b68d3c8e74352cc703928768b34f069b87488ac6a7e8167a` |
| 75 | [p75-heading-upright.png](exhibits/p75-heading-upright.png) | `[140, 300, 1320, 1100]` | upright | `65b66b50882267ac52089b7184d840d0227504b2601db0d56d8628d65f19ae3d` |

The operation used exact pixels. Fitted transforms, contrast adjustments and interpolation were all zero. The original review marks and registered assets remain frozen. [Source metadata](SOURCE_CHECK.json) · [Reader triage](UNCLEAR_TRIAGE.json)

Generate the tile packet using the registered protocol, then run this command from the repository root. Set `PRIVATE_PACKET` to the packet directory and `PRIVATE_HEADING_EXHIBITS` to a fresh output directory. The script checks the source tile hashes against the packet manifest. Both saved PNGs reproduced byte for byte. [Tile instructions](PROTOCOL.md) · [Exhibit script](../../../scripts/make_issue24_heading_exhibits.py)

```sh
python3 public/research/scripts/make_issue24_heading_exhibits.py \
  --packet "$PRIVATE_PACKET" --out "$PRIVATE_HEADING_EXHIBITS"
```
