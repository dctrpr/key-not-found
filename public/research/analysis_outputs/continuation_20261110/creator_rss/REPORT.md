# An archived feed; an unresolved recording date

The [June 5, 2023 RSS capture](https://web.archive.org/web/20230605141627id_/https://feeds.buzzsprout.com/1263314.rss) was recovered by one ordinary HTTP 200 GET on November 10, 2026: 342,832 bytes and 165 items. Its SHA-256 is `0e497db47f546759778ee26c249785de25bed82746f954cf31aed6ee0f9c7b06`. The [complete bibliographic table](ITEM_DATES.json) retains every title, GUID and raw/UTC publication date, with no owner/contact or media fields.

OP65 is **Orange Pill [OP65] — A Quantum Entanglement with a Bag of Stones**, GUID `Buzzsprout-12498799`. Feed publication is March 23, 2023 at 04:00 UTC. Its description/content fields are empty. That supplies no recording date or original video; publication cannot exclude an earlier conversation. The RSS self-attribution is not an authenticated creator-to-feed link.

## The feed is not the creator's calendar

| Fixed UTC publication window | Entries in this capture |
| --- | ---: |
|December 12, 2022–January 9, 2023|0|
|February 18–March 19, 2023|1: OP64|

Known original [December 23](https://www.youtube.com/watch?v=e_1yQ3z85pQ) and [December 28](https://www.youtube.com/watch?v=Lh4-rf8uT68) recordings are not identified by their title markers in this feed. Its empty December window cannot clear the creator window. OP64 demonstrates the date distinction: its [original premiere](https://www.youtube.com/watch?v=j71FUmllHBg) displays March 9, the publisher description dates March 8, and the feed publishes March 15. Date-only watch displays have no recovered timezone. The [OP66 original](https://www.youtube.com/watch?v=87f8qbFcjGU) displays March 30 and its description March 29, outside the fixed March window.

## What the additional checks established

The fixed [metadata screen](METADATA_SCREEN.json) covers 165 items and five fields using nine declared literals. Four items match; eight field occurrences duplicate description/content text. Their contexts are ordinary magazine news, a mirror metaphor and general private-key rhetoric, not a newly established puzzle instruction. OP65 is the only empty description/content pair; iTunes summary/subtitle fields are absent throughout this capture. No audio or creator-history exclusion follows.

[Retrieval records](RETRIEVAL.json) show the observed audio URL returning 301→404. Both observed iVoox routes forward to that same failed URL; duplicate destination requests were stopped. Two bounded exact-URL archive indexes returned empty lists. No audio was recovered, decoded or transcribed; this does not establish global unavailability.

The [current public-link pass](PROFILE_LINKS.json) verifies Max Keiser's profile linking the podcast profile. It did not establish an outward link to this particular historical audio feed. The creator website link led to a book page; one native episode query returned no results, without an exhaustive-search claim.

## Reproduce and limits

[SOURCE.json](SOURCE.json) binds the capture, publication inventory, known original-source comparisons and public exports. [PORT_CHECK.json](PORT_CHECK.json) verifies byte-identical inventory reproduction and content-identical metadata-screen results. The source and copyright remain with their owners. Raw XML/headers and unselected metadata/context are not bundled; obtain the stated public capture privately and verify its hash before running the offline tools. No original article, key/cipher family, recording window or prize is ruled out.

Python 3.9+ standard library; from this directory, use fresh private outputs outside the checkout:

```sh
python3 build_inventory.py --rss CACHED_XML --expected-sha256 0e497db47f546759778ee26c249785de25bed82746f954cf31aed6ee0f9c7b06 --source-url https://web.archive.org/web/20230605141627id_/https://feeds.buzzsprout.com/1263314.rss --out PRIVATE_NEW_JSON
python3 screen_metadata.py --self-test
python3 screen_metadata.py --run --source CACHED_XML --out EXISTING_PRIVATE_DIRECTORY
```

The inventory output's parent must be private (0700); the screen writes its detailed contexts privately. Neither script fetches data, submits transactions or derives keys. The immediate source question remains OP65's original context; current failed routes do not justify a guessed date or URL.
