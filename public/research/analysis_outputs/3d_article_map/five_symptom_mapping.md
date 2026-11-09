# Five-Symptom Mapping

Scope: test whether page 80's `5 SYMPTOM RELIEF` label orders/selects the five page-76 reflected-graph target groups. No private-key candidates are generated.

## Streams

- `symptom_initials`: `NHIUS`
- `symptom_last_initials`: `NHISS`
- `symptom_lengths`: `6,9,11,12,9`
- `graph_target_initials`: `GbbI$`
- `graph_target_last_initials`: `Bmdgb`
- `length_selected_chars`: `mcitn`
- `length_selected_words`: `bitcoin the the stun $1`

## Ordered Symptom -> Graph Target Rows

- `NAUSEA` -> G `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` initial=`G` lastInitial=`B` len=6 charModulo=`m` wordModulo=`bitcoin`
- `HEARTBURN` -> b1 `by the rancid catnip of fiat money.` initial=`b` lastInitial=`m` len=9 charModulo=`c` wordModulo=`the`
- `INDIGESTION` -> b2 `“buying the dip.”` initial=`b` lastInitial=`d` len=11 charModulo=`i` wordModulo=`the`
- `UPSET STOMACH` -> I `It’s a stun gun to the genitals.` initial=`I` lastInitial=`g` len=12 charModulo=`t` wordModulo=`stun`
- `SHITCOINS` -> $ `$1 billion` initial=`$` lastInitial=`b` len=9 charModulo=`n` wordModulo=`$1`

## Direct Matches Across All Page-76 Highlights

- `NAUSEA` -> grey_stun_gun hits=['stun'] text=`It’s a stun gun to the genitals.`
- `HEARTBURN` -> orange_open_heart hits=['heart'] text=`Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.`
- `HEARTBURN` -> orange_shitcoiner_heart hits=['heart'] text=`shitcoiner at heart.`
- `UPSET STOMACH` -> grey_stun_gun hits=['genitals'] text=`It’s a stun gun to the genitals.`
- `SHITCOINS` -> orange_shitcoiner_heart hits=['shitcoin', 'shitcoiner'] text=`shitcoiner at heart.`

## Assessment

- The five-symptom count supports the five page-76 target-group model.
- The symptom order does not create readable initials, last initials, or length-indexed text over the five graph targets.
- Direct lexical/semantic matches mostly point HEARTBURN to heart phrases and SHITCOINS to 'shitcoiner at heart'; they do not order the graph targets cleanly.
- Treat p80 as count/theme support, not the final selector.
