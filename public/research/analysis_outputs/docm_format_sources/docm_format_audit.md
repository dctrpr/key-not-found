# DOCM Formatting Source Audit

Scope: extract run-level bold/font information from the user-provided Word macro documents without executing macros.

## Sources

- `bold`: `private_inputs/Desktop/BOLD.docm`
  - macros present: `True`
  - paragraphs/runs/words/chars: `25` / `140` / `230` / `1417`
  - bold runs/chars: `126` / `1357`
- `article_with_fonts`: `private_inputs/Desktop/Article with Fonts.docm`
  - macros present: `False`
  - paragraphs/runs/words/chars: `149` / `344` / `1281` / `7632`
  - bold runs/chars: `129` / `2586`

- Text equal after whitespace normalization: `False`

## Bold Streams

- `bold` bold letters length `1108`: `ReallyYesglobalunconsciousprotocolYouwouldntbediggingblindlywithyourbarehandsinthemuckofBitcoinsrabbitholeifthiswerenttrueUTXOghettoupinhereshitcoinersPresidentNayibBukeleIMFloanhyperbitcoinizedEVERYSINGLEONEOFTHEBITCOINWANNABESBCHBSVETHXRPADAAND12000OTHERSHITCOINSPLUSFIATMONEYANDGOLDISFACINGTHEIGNOMINIOUSFATEOFDEMONETIZATIONVERSUSBITCOINWeveneverhadaneconomyandamoneythatincentivizeslovebeforeuntilbitcoinLoveopensupthecollectiveunconsciousandourjointinnercosmicbeingTheeconomyofloveisinfinitelymo...`
- `article_with_fonts` bold letters length `2119`: `OVERDOSEMReallyYesTheyarethesumofallourneurosesglobalunconsciousmoneyprintersbankingterroristsstocktraderscentralbankarsonistsLayer1protocolFactItsLayer1foreverygreatthingthatseverbeeninventedordiscoveredMaximalistDontfallforshitcoineryKeepyourdignityLayer1YouwouldntbediggingblindlywithyourbarehandsinthemuckofBitcoinsrabbitholeifthiswerenttrueGetsometoxicityGetsomebitcoinOpenyourhearttoBitcoinUTXOghettoupinhereGottabethiswayFortyyearsofdumbpost1971fiatmoneynonsenseshitcoinersbytherancidcatnipoff...`

## Font Character Counts

### bold
- `Typeka`: 1374
- `Stencil`: 19
### article_with_fonts
- `Typeka`: 6574
- `Typeka Mix`: 883
- `Stencil`: 19
- `LonestarW00-Regular`: 8

## Size Character Counts

### bold
- `(none)`: 1365
- `36`: 19
- `32`: 5
- `28`: 3
- `22`: 1
### article_with_fonts
- `(none)`: 7003
- `20`: 256
- `28`: 160
- `36`: 29
- `22`: 23
- `72`: 8
- `32`: 5

## Small Formatting Streams

### bold
- `fontStreams:Stencil` len=19: `BITCOIN IS TOXIC AF`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; color=000000` len=188: `hyperbitcoinizedEVERY SINGLE OF THE BITCOIN WANNABES - BCH, BSV, ETH, XRP, ADA, AND 12,000 SHITCOINS, PLUS FIAT MONEY AND - IS FACING THE IGNOMINIOUS FATE OF DEMONETIZATION VERSUS BITCOIN.`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; color=000000; highlight=yellow` len=12: `ONEOTHERGOLD`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; highlight=yellow` len=193: `YourabbitholethistrueloannevereconomythatlovebeforeuntilLoveinnereconomylovemoreALLTHISoilperfectRemoveyouremovegaploveintorighttherePovertybecausebecauseexpressseaallconnectrabbitholepeacelove`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=22` len=1: `R`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=28` len=3: `al?`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=32` len=5: `yYes.`
- `signatureStreams:bold=True; underline=True; fontAscii=Typeka; fontHAnsi=Typeka` len=8: `protocol`
- `signatureStreams:fontAscii=Stencil; fontHAnsi=Stencil; sizeHalfPoints=36` len=19: `BITCOIN IS TOXIC AF`
- `signatureStreams:fontAscii=Typeka; fontHAnsi=Typeka` len=7: `. , - -`
### article_with_fonts
- `fontStreams:LonestarW00-Regular` len=8: `OVERDOSE`
- `fontStreams:Stencil` len=19: `BITCOIN IS TOXIC AF`
- `signatureStreams:bold=True; fontAscii=LonestarW00-Regular; fontHAnsi=LonestarW00-Regular; sizeHalfPoints=72` len=8: `OVERDOSE`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; color=000000` len=200: `hyperbitcoinized EVERY SINGLE ONE OFTHE BITCOIN WANNABES - BCH, BSV, ETH, XRP,ADA, AND 12,000 OTHER SHITCOINS, PLUS FIATMONEY AND GOLD - IS FACING THE IGNOMINIOUSFATE OF DEMONETIZATION VERSUS BITCOIN.`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; color=000000; highlight=yellow` len=77: `Toxic Bitcoin Maximalists within six months.who harass old women and children`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; color=FFFFFF; highlight=black` len=472: `money printers, banking terrorists, stock traders, central bank arsonists,Don't fall for shitcoinery.Gotta be this way. Forty years of dumb post-1971 fiat moneynonsenseIt's a stun gun to the genitals.$1 billion“Volcano Bonds”(Sorry Bhutan, you fell for that snake oil salesmen over at XRP. Get ready to experience shitcoin hell.Faketoshishitcoiners, useless Royals,It does this by monetizing,gargantuanly wastefulmoney printingwars to keep it goingwar and violence economy`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; highlight=cyan` len=1: `M`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=20` len=256: `BITCOIN FIXES ALL THIS by replacing oil-dripping, corpse-ridden, poppy-harvesting fiat money with perfect bitcoin. Remove the war incentive, and you remove the hate incentive. Bitcoin fills in the gap with love; our most natural tendency if given a chance.`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=22` len=23: `RIt's a fact baked into`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=28` len=5: `al? ,`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=28; highlight=yellow` len=55: `shitcoiner at heart.the game-theorized Bitcoin protocol`
- `signatureStreams:bold=True; fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=32` len=5: `yYes.`
- `signatureStreams:bold=True; underline=True; fontAscii=Typeka; fontHAnsi=Typeka` len=8: `protocol`
- `signatureStreams:fontAscii=Stencil; fontHAnsi=Stencil; sizeHalfPoints=36` len=19: `BITCOIN IS TOXIC AF`
- `signatureStreams:fontAscii=Typeka Mix; fontHAnsi=Typeka Mix; color=000000` len=180: `Jack Mallers'Roger VerBlock Size War Peter McCormack)51%Shitcoins, fiat and gold willstarve to death as the result of Bitcoin'sinsatiable conquest of all available energy.shitcoins`
- `signatureStreams:fontAscii=Typeka Mix; fontHAnsi=Typeka Mix; sizeHalfPoints=28` len=78: `Go Bitcoin Toxic Maximalist,The warmongers will start mining bitcoin for sure.`
- `signatureStreams:fontAscii=Typeka Mix; fontHAnsi=Typeka Mix; sizeHalfPoints=36; color=000000` len=10: `Full Stop.`
- `signatureStreams:fontAscii=Typeka; fontHAnsi=Typeka; highlight=cyan` len=8: `NBILLION`
- `signatureStreams:fontAscii=Typeka; fontHAnsi=Typeka; sizeHalfPoints=28` len=20: `Maybe because he's a`
- `signatureStreams:strike=True; fontAscii=Typeka; fontHAnsi=Typeka` len=58: `(and 10 years of watching Peter Schiff miss buying bitcoin`
- `signatureStreams:underline=True; fontAscii=Typeka Mix; fontHAnsi=Typeka Mix` len=31: `They discount stuff in advance.`

## Assessment

- These files are new formatting witnesses. They should be compared against the high-res article model before using them as selectors.
- Macro presence is noted, but macro code was not executed.
- If a font or bold stream is short and non-body-like, it is a candidate selector. Huge body-font streams should be treated as transcription support, not key material.
