# Duplicate paragraph: exact wrap comparison

Printed p80, center column. Both copies have 27 lexical tokens (28 if 12-step is split into numeric 12 and word step). The source differs in physical wrapping and the terminal Shitcoiners hyphen. The duplicate is not byte-for-byte identical.

| Fragment | Copy1 row | Copy1 text | Copy2 row | Copy2 text |
|---|---|---|---|---|
|1|35|Those who shitcoin need a 12-step|40|Those who shitcoin need a|
|2|36|recovery program. Shitcoiners-|41|12-step recovery program. Shitcoiners|
|3|37|Anonymous meetings are needed to|42|Anonymous meetings are needed to|
|4|38|help them recover from their disease.|43|help them recover from their disease.|
|5|39|Brock Pierce and Novogratz should|44|Brock Pierce and Novogratz should|
|6|40|start one.|45|start one.|

Copy2 starts inside physical row 40; copy-fragment first words are therefore distinct from genuine whole-line first words. Both are saved, with no choosing between them.

## Results

- Token equality after punctuation/linebreak normalization: True
- Line-end token positions, copy1: [6, 9, 14, 20, 25, 27]
- Line-end token positions, copy2: [5, 9, 14, 20, 25, 27]
- Word crossed by moved line boundary: 12-step
- Copy1 fragment first words: Those recovery Anonymous help Brock start
- Copy2 fragment first words: Those 12-step Anonymous help Brock start
- Copy1 fragment last words: 12-step Shitcoiners to disease should one
- Copy2 fragment last words: a Shitcoiners to disease should one
- Firstword change: recovery -> 12-step
- Lastword change: 12-step -> a
- Declared streams: 103; literal key hits: 0.

The rewrap moves exactly the already printed term 12-step between the first two fragments. Reading changed first words supplies recovery and 12-step, which only reconstruct the article’s existing recovery-program phrase. Odd/even fragment readings, their initials, reversed orders, true physical-line leaders and endings, and the nearby recursion-paragraph line edges produce no independently readable new instruction or standard key. No plaintext was hashed into a secret; no wordlist filtering or arbitrary deletion was performed. This is a negative result for the bounded rewrap hypothesis, not proof that the column contains no key.

## All declared streams

### copy1:all:forward:first_words

```text
Those recovery Anonymous help Brock start
```

### copy1:all:forward:first_initials

```text
TrAhBs
```

### copy1:all:forward:first_terminals

```text
eyspkt
```

### copy1:all:forward:last_words

```text
12-step Shitcoiners to disease should one
```

### copy1:all:forward:last_initials

```text
1Stdso
```

### copy1:all:forward:last_terminals

```text
psoede
```

### copy1:all:forward:whole_fragments

```text
Those who shitcoin need a 12-step
recovery program. Shitcoiners-
Anonymous meetings are needed to
help them recover from their disease.
Brock Pierce and Novogratz should
start one.
```

### copy1:all:reverse:first_words

```text
start Brock help Anonymous recovery Those
```

### copy1:all:reverse:first_initials

```text
sBhArT
```

### copy1:all:reverse:first_terminals

```text
tkpsye
```

### copy1:all:reverse:last_words

```text
one should disease to Shitcoiners 12-step
```

### copy1:all:reverse:last_initials

```text
osdtS1
```

### copy1:all:reverse:last_terminals

```text
edeosp
```

### copy1:all:reverse:whole_fragments

```text
start one.
Brock Pierce and Novogratz should
help them recover from their disease.
Anonymous meetings are needed to
recovery program. Shitcoiners-
Those who shitcoin need a 12-step
```

### copy1:odd:forward:first_words

```text
Those Anonymous Brock
```

### copy1:odd:forward:first_initials

```text
TAB
```

### copy1:odd:forward:first_terminals

```text
esk
```

### copy1:odd:forward:last_words

```text
12-step to should
```

### copy1:odd:forward:last_initials

```text
1ts
```

### copy1:odd:forward:last_terminals

```text
pod
```

### copy1:odd:forward:whole_fragments

```text
Those who shitcoin need a 12-step
Anonymous meetings are needed to
Brock Pierce and Novogratz should
```

### copy1:odd:reverse:first_words

```text
Brock Anonymous Those
```

### copy1:odd:reverse:first_initials

```text
BAT
```

### copy1:odd:reverse:first_terminals

```text
kse
```

### copy1:odd:reverse:last_words

```text
should to 12-step
```

### copy1:odd:reverse:last_initials

```text
st1
```

### copy1:odd:reverse:last_terminals

```text
dop
```

### copy1:odd:reverse:whole_fragments

```text
Brock Pierce and Novogratz should
Anonymous meetings are needed to
Those who shitcoin need a 12-step
```

### copy1:even:forward:first_words

```text
recovery help start
```

### copy1:even:forward:first_initials

```text
rhs
```

### copy1:even:forward:first_terminals

```text
ypt
```

### copy1:even:forward:last_words

```text
Shitcoiners disease one
```

### copy1:even:forward:last_initials

```text
Sdo
```

### copy1:even:forward:last_terminals

```text
see
```

### copy1:even:forward:whole_fragments

```text
recovery program. Shitcoiners-
help them recover from their disease.
start one.
```

### copy1:even:reverse:first_words

```text
start help recovery
```

### copy1:even:reverse:first_initials

```text
shr
```

### copy1:even:reverse:first_terminals

```text
tpy
```

### copy1:even:reverse:last_words

```text
one disease Shitcoiners
```

### copy1:even:reverse:last_initials

```text
odS
```

### copy1:even:reverse:last_terminals

```text
ees
```

### copy1:even:reverse:whole_fragments

```text
start one.
help them recover from their disease.
recovery program. Shitcoiners-
```

### copy2:all:forward:first_words

```text
Those 12-step Anonymous help Brock start
```

### copy2:all:forward:first_initials

```text
T1AhBs
```

### copy2:all:forward:first_terminals

```text
epspkt
```

### copy2:all:forward:last_words

```text
a Shitcoiners to disease should one
```

### copy2:all:forward:last_initials

```text
aStdso
```

### copy2:all:forward:last_terminals

```text
asoede
```

### copy2:all:forward:whole_fragments

```text
Those who shitcoin need a
12-step recovery program. Shitcoiners
Anonymous meetings are needed to
help them recover from their disease.
Brock Pierce and Novogratz should
start one.
```

### copy2:all:reverse:first_words

```text
start Brock help Anonymous 12-step Those
```

### copy2:all:reverse:first_initials

```text
sBhA1T
```

### copy2:all:reverse:first_terminals

```text
tkpspe
```

### copy2:all:reverse:last_words

```text
one should disease to Shitcoiners a
```

### copy2:all:reverse:last_initials

```text
osdtSa
```

### copy2:all:reverse:last_terminals

```text
edeosa
```

### copy2:all:reverse:whole_fragments

```text
start one.
Brock Pierce and Novogratz should
help them recover from their disease.
Anonymous meetings are needed to
12-step recovery program. Shitcoiners
Those who shitcoin need a
```

### copy2:odd:forward:first_words

```text
Those Anonymous Brock
```

### copy2:odd:forward:first_initials

```text
TAB
```

### copy2:odd:forward:first_terminals

```text
esk
```

### copy2:odd:forward:last_words

```text
a to should
```

### copy2:odd:forward:last_initials

```text
ats
```

### copy2:odd:forward:last_terminals

```text
aod
```

### copy2:odd:forward:whole_fragments

```text
Those who shitcoin need a
Anonymous meetings are needed to
Brock Pierce and Novogratz should
```

### copy2:odd:reverse:first_words

```text
Brock Anonymous Those
```

### copy2:odd:reverse:first_initials

```text
BAT
```

### copy2:odd:reverse:first_terminals

```text
kse
```

### copy2:odd:reverse:last_words

```text
should to a
```

### copy2:odd:reverse:last_initials

```text
sta
```

### copy2:odd:reverse:last_terminals

```text
doa
```

### copy2:odd:reverse:whole_fragments

```text
Brock Pierce and Novogratz should
Anonymous meetings are needed to
Those who shitcoin need a
```

### copy2:even:forward:first_words

```text
12-step help start
```

### copy2:even:forward:first_initials

```text
1hs
```

### copy2:even:forward:first_terminals

```text
ppt
```

### copy2:even:forward:last_words

```text
Shitcoiners disease one
```

### copy2:even:forward:last_initials

```text
Sdo
```

### copy2:even:forward:last_terminals

```text
see
```

### copy2:even:forward:whole_fragments

```text
12-step recovery program. Shitcoiners
help them recover from their disease.
start one.
```

### copy2:even:reverse:first_words

```text
start help 12-step
```

### copy2:even:reverse:first_initials

```text
sh1
```

### copy2:even:reverse:first_terminals

```text
tpp
```

### copy2:even:reverse:last_words

```text
one disease Shitcoiners
```

### copy2:even:reverse:last_initials

```text
odS
```

### copy2:even:reverse:last_terminals

```text
ees
```

### copy2:even:reverse:whole_fragments

```text
start one.
help them recover from their disease.
12-step recovery program. Shitcoiners
```

### physical_span1:first_words

```text
Those recovery Anonymous help Brock start
```

### physical_span1:first_initials

```text
TrAhBs
```

### physical_span1:last_words

```text
12-step Shitcoiners to disease should a
```

### physical_span1:last_initials

```text
1Stdsa
```

### physical_span2:first_words

```text
start 12-step Anonymous help Brock start
```

### physical_span2:first_initials

```text
s1AhBs
```

### physical_span2:last_words

```text
a Shitcoiners to disease should one
```

### physical_span2:last_initials

```text
aStdso
```

### first_changed_pairs

```text
recovery -> 12-step
```

### first_changed_copy1_words

```text
recovery
```

### first_changed_copy2_words

```text
12-step
```

### last_changed_pairs

```text
12-step -> a
```

### last_changed_copy1_words

```text
12-step
```

### last_changed_copy2_words

```text
a
```

### rewrap_displaced_tokens

```text
12-step
```

### recursion_paragraph:first_words

```text
succumb this a It's playing So
```

### recursion_paragraph:first_initials

```text
staIpS
```

### recursion_paragraph:last_words

```text
made It's code 8-track over off
```

### recursion_paragraph:last_initials

```text
mIc8oo
```

