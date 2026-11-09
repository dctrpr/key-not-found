# Source Packet Fold-World OVERDOSE Order Control

- Fold/page order modes checked: `9`.
- Unique active center-slot streams: `DEVO,ODEV,OEVD,OVED,VEDO`.
- Known page/x stream order rows: `5`.
- Fold-only new streams: `DEVO,ODEV,OEVD`.
- Instruction-hit order rows: `0`.
- Layout-hit / thematic-hit order rows: `0` / `8`.
- Source depth/front/back cue hits: `0`.
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
- Selector unlocked: `False`.
- Fingerprint: `orders=9|unique=5|streams=DEVO,ODEV,OEVD,OVED,VEDO|knownOrders=5|new=DEVO,ODEV,OEVD|instructionRows=0|layoutRows=0|themeRows=8|sourceDepthCues=0|sourceR3=0|triggers=0/9|selectors=0`.

Order rows:

- `page_line_top_to_bottom`: targets `O4 B4 G5 O5`, slots `OVED`, state `YKKY`, color `OBBO`, layout `-`, theme `DOVE`, instruction `-`.
- `page_x_left_to_right`: targets `B4 G5 O5 O4`, slots `VEDO`, state `KKYY`, color `BBOO`, layout `-`, theme `DOVE`, instruction `-`.
- `fold_world_x_left_to_right`: targets `B4 G5 O5 O4`, slots `VEDO`, state `KKYY`, color `BBOO`, layout `-`, theme `DOVE`, instruction `-`.
- `fold_world_y_low_to_high`: targets `O5 G5 B4 O4`, slots `DEVO`, state `YKKY`, color `OBBO`, layout `-`, theme `DOVE`, instruction `-`.
- `fold_world_y_high_to_low`: targets `O4 B4 G5 O5`, slots `OVED`, state `YKKY`, color `OBBO`, layout `-`, theme `DOVE`, instruction `-`.
- `fold_depth_z_front_to_back_low_to_high`: targets `O4 O5 G5 B4`, slots `ODEV`, state `YYKK`, color `OOBB`, layout `-`, theme `DOVE`, instruction `-`.
- `fold_depth_z_back_to_front_high_to_low`: targets `B4 G5 O5 O4`, slots `VEDO`, state `KKYY`, color `BBOO`, layout `-`, theme `DOVE`, instruction `-`.
- `distance_from_page76_fold_center_near_to_far`: targets `O4 G5 B4 O5`, slots `OEVD`, state `YKKY`, color `OBBO`, layout `-`, theme `-`, instruction `-`.
- `distance_from_p78_pair_center_near_to_far`: targets `O4 O5 G5 B4`, slots `ODEV`, state `YYKK`, color `OOBB`, layout `-`, theme `DOVE`, instruction `-`.

Decision: fold-world active target order does not reopen OVERDOSE-slot extraction.
