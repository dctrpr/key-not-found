# Page-76 Two-Hand Selector Audit

Scope: constrained page-76 selector checks from the reflected graph and high-res B1B1B2O3 intersections. No private-key candidates are generated.

## Counts

- page76MediumStrongEdges: 17
- dedupTargetSourceEdges: 8
- strongOnlyEdges: 9
- highresMeaningfulEdges: 4
- dipEdges: 3

## Streams

- `graph_all:source_pages`: `7979797878787979787879797878787979`
- `graph_all:bits_79_is_1`: `11100011001100011`
- `graph_all:bits79_ascii_7`: `qL`
- `graph_all:bits79_ascii_8`: `.1`
- `graph_all:78_first_79_last`: `yyyOOHddllgg$$$ss`
- `graph_all:78_last_79_first`: `GGGmmdHHggllsss$$`
- `graph_dedup_target_source:source_pages`: `7978787978797879`
- `graph_dedup_target_source:78_first_79_last`: `yOHdlg$s`
- `graph_dedup_target_source:78_last_79_first`: `GmdHgls$`
- `graph_strong_only:source_pages`: `797978797878787979`
- `graph_strong_only:78_first_79_last`: `yyHdl$$ss`
- `graph_strong_only:78_last_79_first`: `GGdHgss$$`
- `highres:target_pattern`: `B1B1B2O3`
- `highres:source_page_pattern`: `79797978`
- `highres:source_index_pattern`: `2,3,2,3`
- `highres:target_line_initials`: `GGnH`
- `highres:above_line_initials`: `rrGt`
- `highres:below_line_initials`: `nnsI`
- `highres:target_word_by_source_index_1based`: `be this and them`
- `highres:target_word_by_source_index_0based`: `this way 10 telling`
- `highres:source_word_by_target_index_1based`: `That's all right fiat` hits=['right']
- `highres:source_word_by_target_index_0based`: `right the Bitcoin cuck` hits=['bitcoin', 'right']
- `dip:above_initials`: `ttt`
- `dip:target_initials`: `HHH`
- `dip:below_initials`: `III`
- `dip:source_initials`: `hybh|GbSwFyoalowP|mbb`

## High-Res B1B1B2O3 Records

- B1 p79 src#2 `That's right, Bitcoin will take all the energy.` -> line 6 `Gotta be this way. Forty years of dumb post-1971 fiat money` | srcIdx1 target word=`be`; targetIdx1 source word=`That's`; below=`nonsense (and 10 years of watching Peter Schiff miss buying bitcoin`
- B1 p79 src#3 `all the energy.` -> line 6 `Gotta be this way. Forty years of dumb post-1971 fiat money` | srcIdx1 target word=`this`; targetIdx1 source word=`all`; below=`nonsense (and 10 years of watching Peter Schiff miss buying bitcoin`
- B2 p79 src#2 `That's right, Bitcoin will take all the energy.` -> line 7 `nonsense (and 10 years of watching Peter Schiff miss buying bitcoin` | srcIdx1 target word=`and`; targetIdx1 source word=`right`; below=`since I started honey-badgering him to buy some at $1 back in 2011)`
- O3 p78 src#3 `$2 trillion fiat cuck-bucks.` -> line 22 `He's taunting them, telling them he's “buying the dip.”` | srcIdx1 target word=`them`; targetIdx1 source word=`fiat`; below=`I tweeted President Nayib Bukele when he announced`

## Dip Adjacent-Line Records

- strong p78 `honéy-badgering him` -> above=`trolling the International Monetary Fund (IMF) on Twitter?` target=`He's taunting them, telling them he's “buying the dip.”` below=`I tweeted President Nayib Bukele when he announced`
- medium p79 `Gotta be S way. Forty years of (and loyears of watching Peter` -> above=`trolling the International Monetary Fund (IMF) on Twitter?` target=`He's taunting them, telling them he's “buying the dip.”` below=`I tweeted President Nayib Bukele when he announced`
- strong p79 `miss buying bitcoin` -> above=`trolling the International Monetary Fund (IMF) on Twitter?` target=`He's taunting them, telling them he's “buying the dip.”` below=`I tweeted President Nayib Bukele when he announced`

## Assessment

- The 78/79 source-page pattern does not decode to printable 7-bit or 8-bit text, and first/last two-hand rules do not create instruction-like language.
- Deduping by target/source and using strong edges only reduces repetition but still produces short non-instruction streams.
- The compact high-res `B1B1B2O3` branch gives one phrase-like stream, `That's all right fiat`, when using target box number to select a word from the reflected source phrase. It is weak: it is not an instruction, it does not select page-76 characters, and the fourth word is just inherited fiat-language context.
- Reading above/below the `buying the dip` target produces initials only (`ttt` above, `III` below) and repeats the corridor narrative rather than giving a selector.
- Keep page 76 as the target surface, but do not promote the current 78/79 two-hand or B1B1B2O3 interpretations without a new registration/source clue.
