# December 2023 “El Salvador” statement

**Authentic wording and date; puzzle context remains unverified.**

X's public oEmbed and syndication endpoints both return [Max Keiser’s post](https://x.com/maxkeiser/status/1741134493769965603):

> Obviously, “El Salvador” is a clue.

Syndication gives **December 30, 2023, 16:29:46 UTC**, author handle `maxkeiser`, user ID `20374262`, post ID `1741134493769965603`, and `isEdited=false`.

The oEmbed includes shortlink `OrIU5MWnib`. Its preserved redirect chain points to [@realPRIVATE_CONTRIBUTOR post 1741133781321523668](https://x.com/realPRIVATE_CONTRIBUTOR/status/1741133781321523668). X syndication returns a `TweetTombstone` explicitly saying that the post author deleted that post. This does **not** establish deletion of the account.

Neither surviving response exposes an `in_reply_to_status_id` or a conversation/quoted-parent object. The shortlink establishes the linked antecedent's handle and ID, but its original text is unavailable. Describing this as a verified reply about the 20-BTC puzzle would overstate the evidence.

Exact-URL Wayback CDX checks for both Twitter and X returned empty capture lists. A public FX cache returned 404. Bounded web searches for the ID, shortlink, exact wording, and antecedent handle found no recoverable context.

Therefore:

- Max really called “El Salvador” a clue.
- Its relationship to Issue #24, hidden keys, the 20-BTC announcement, or a different topic is unresolved.
- The post supplies no extraction unit, ordering rule, key format, or target wallet.
- Treat a puzzle-specific interpretation as conditional until the linked post or independent context is recovered.

## Preserved evidence

| File | Contents |
|---|---|
| `oembed.json` | Raw primary oEmbed response |
| `syndication.json` | Raw primary post metadata/text |
| `shortlink_redirect_chain.json` | Shortlink → Twitter antecedent → X antecedent |
| `quoted_syndication.json` | Primary deletion tombstone |
| `quoted_post_fetch_outcomes.json` | Antecedent endpoint outcomes |
| `archive_context_fetches.json` | Bounded archival/cache checks |
| `context_fetches.json` | Additional endpoint outcomes |

No posting, outreach, authenticated account actions, or transactions were performed.
