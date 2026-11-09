# DOCM Layer Selector Audit

Scope: test short selector-like streams from `Article with Fonts.docm` font layers. No private-key candidates are generated.

## Streams

- `cyan_letters`: `MNBILLION`
- `cyan_run_initials`: `MNB`
- `cyan_pages`: `75,75,78`
- `typeka_mix_run_initials`: `aTctooaTVGGbrcnEMNIJRBSPFSt5SsisTTlmhIodlgmoSH`
- `typeka_mix_run_last_initials`: `KaphNstMBMCbrbnSMNgMVBWMFSt5wBessoitwdctpgieyy`
- `typeka_mix_run_lengths`: `8,26,15,12,14,22,42,23,14,24,13,5,6,14,9,10,4,9,23,11,8,5,7,14,4,1,3,2,24,34,38,9,42,12,16,17,10,9,0,20,46,12,4,26,12,39,24`
- `typeka_mix_instruction_hits`: `bitcoin,first`

## Cyan Records

- run 2 p75 text=`M` letters=`M` context=`OVERDOSE with [M] ax Keiser BITCOIN IS TOXIC AF`
- run 42 p75 text=`N` letters=`N` context=`In fact, all the chaos you see around you these days is caused by Bitcoin. And nothing could be better. [N] ocoiners and shitcoiners, and even some Bitcoiners, consider this view toxic.`
- run 263 p78 text=`BILLION` letters=`BILLION` context=`America left $85 [BILLION] worth of hate toys in Afghanistan, for example, for a war`

## Typeka Mix By Page

### p75
- `runInitials`: `aTctooaTVG`
- `runLastInitials`: `KaphNstMBM`
- `runLengths`: `8,26,15,12,14,22,42,23,14,24`
- `letters`: `axKeiserTheydiscountstuffinadvancecollectivepanictheblackholeoftheCosmicNowocoinersandshitcoinersandevensomeBitcoinersconsiderthisviewtoxicToxicBitcoinMaximalistsVitalikButerinGoBitcoinToxicMaximalist`
- `text`: `ax KeiserThey discount stuff in advance.collective panicthe black hole of the Cosmic Nowocoiners and shitcoiners,and even some Bitcoiners, consider this view toxic.Toxic Bitcoin MaximalistsVitalik ButerinGo Bitcoin Toxic Maximalist,`
- `instructionHits`: `['bitcoin']`
### p76
- `runInitials`: `GbrcnEMNI`
- `runLastInitials`: `CbrbnSMNg`
- `runLengths`: `13,5,6,14,9,10,4,9,23`
- `letters`: `GeorgeClintonbeingrippedcentralbankersnocoinersElSalvadorMikeNovogratzIdontreallytrustthatguy`
- `text`: `George Clintonbeing ripped central bankersnocoiners'El SalvadorMike NovogratzI don't really trust that guy.`
- `instructionHits`: `[]`
### p77
- `runInitials`: `JRBSPFSt5Ssis`
- `runLastInitials`: `MVBWMFSt5wBes`
- `runLengths`: `11,8,5,7,14,4,1,3,2,24,34,38,9`
- `letters`: `JackMallersRogerVerBlockSizeWarPeterMcCormackFullStop51ShitcoinsfiatandgoldwillstarvetodeathastheresultofBitcoinsinsatiableconquestofallavailableenergyshitcoins`
- `text`: `Jack Mallers'Roger VerBlock Size War Peter McCormack)Full Stop.51%Shitcoins, fiat and gold willstarve to death as the result of Bitcoin'sinsatiable conquest of all available energy.shitcoins`
- `instructionHits`: `[]`
### p78
- `runInitials`: `TTlmh`
- `runLastInitials`: `soitw`
- `runLengths`: `42,12,16,17,10`
- `letters`: `ThewarmongerswillstartminingbitcoinforsureTheeconomyofloveisinfinitelymoreefficientthanhateandwar`
- `text`: `The warmongers will start mining bitcoin for sure. The economy oflove is infinitelymore efficient thanhate and war.`
- `instructionHits`: `['bitcoin']`
### p79
- `runInitials`: `IodlgmoSH`
- `runLastInitials`: `dctpgieyy`
- `runLengths`: `9,0,20,46,12,4,26,12,39,24`
- `letters`: `InsodoingourenergyconsumptiondropstonearzerobecauseournaturaltendencytowardloveandpeacegetsmonetizedforthefirsttimeinourexistenceStacyandIhavebeenlivinginherefor10yearsHappytoshareitallwithyou`
- `text`: `In so doing, our energy consumption drops to near zero because our natural tendency toward love and peace gets monetized for the first time in our existence.Stacy and I have been living in here for 10 years. Happy to share it all with you`
- `instructionHits`: `['first']`

## Assessment

- Cyan stream is MNBILLION and appears on p75/p75/p78. It is an anomaly but not an instruction.
- The cyan BILLION sits inside the p78 '$85 BILLION' yellow phrase, creating a semantic bridge to the p76 '$1 billion' target.
- Typeka Mix initials/last-initials/lengths do not form readable instruction text.
- Typeka Mix remains the best available alternate-font/partial-bold witness, but it needs a separate selector before it can be used for extraction.
