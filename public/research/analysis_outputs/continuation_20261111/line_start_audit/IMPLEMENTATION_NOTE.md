# Reader note representation

Both locked readers supplied the final `notes` field as an array of strings. The registered comparison required a single string there. Its initial replay stopped at that metadata type check before comparing rows.

The [replay adapter](../../../scripts/replay_issue24_line_start_audit.py) joins only those note strings in memory before invoking the original validator. It reuses the registered matching, uncertainty and edge-comparison functions. The original receipt bytes and receipt-lock hashes remain intact. The adapter does not edit any row, coordinate, cue, edge chunk, exposure declaration or timestamp.

To reproduce the recorded comparison, use the commands in the [protocol](PROTOCOL.md) with `replay_issue24_line_start_audit.py` as the comparison executable. Use an absolute fresh private output path. The resulting `RECONCILIATION.json` retains the raw receipt hashes. Execution timestamps change on replay.

An independent metadata replay checked the unique complete low-reader pairing and every forced canonical pair with a separate length-only dynamic program. Excluding any reported canonical pair reduced the maximum matching by one. [Matching replay](MATCHING_REPLAY.json)
