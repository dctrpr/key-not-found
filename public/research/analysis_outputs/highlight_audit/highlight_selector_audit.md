# Highlight Selector Audit

Scope: exact high-res highlighted spans plus Markdown bold markup. This checks simple human-readable selector streams only; it does not derive or test private keys.

## Summary

- Spans checked: 34
- Contiguous matches: 33
- Subsequence matches: 0
- Partial matches: 0
- Selector-word transform hits: 3

## Primary Streams

- `all_phrase_initials`: `TLFMKLGbbsThTAttiTESmDGIbVSFsIgmww`
- `orange_phrase_initials`: `TLFMKLGbbsThTAttiTES`
- `grey_phrase_initials`: `mDGIbVSFsIgmww`
- `page76_phrase_initials`: `GbbsGIbV`
- `page76_bold_letters`: `GetsometoxicityGetsomebitcoinOpenyourhearttoBitcoinbytherancidcatnipoffiatmoneybuyingthedipshitcoineratheart`
- `page76_partial_bold_letters`: ``
- `all_lengths_mod26`: `DCCCBCCHEDCECEEEEDDHBJJDDGECDHCDGDDEBGBCFFBDEFCCJBEEGKFCFFCECHCGDCGDGEBDDBKHDDECDIGHJDIBHCEFBDDIBDEEGDDCCFHDDECJBCFDBCGCEDCCEEHGJEGGDIDDCKEBDCEEBDDDEHCADCBCHGGEEFCDCDECHDBCCEBJHDIKGFBDDBJLHEHDBDBECCHG`

## Per Page

- p75: phraseInitials=`TLFMKLmD` bold=`TheyarethesumofallourneurosesLayerFactItsLayerforeverygreatthingthatseverbeeninventedordiscoveredMaximalistKeepyourdignityLayer` partialBold=``
- p76: phraseInitials=`GbbsGIbV` bold=`GetsometoxicityGetsomebitcoinOpenyourhearttoBitcoinbytherancidcatnipoffiatmoneybuyingthedipshitcoineratheart` partialBold=``
- p77: phraseInitials=`ThSFsI` bold=`ToxicBitcoinMaximalistswithinsixmonthsharassoldwomenandchildren` partialBold=``
- p78: phraseInitials=`TAttgmw` bold=`ThenumbersdontlieAmericaleftBILLIONworthofhatetoysinAfghanistantrillionfiatcuckbucksgametheorizedBitcoinprotocol` partialBold=``
- p79: phraseInitials=`iTEw` bold=`infinitelymoreefficienttotransactandstorewealthinthanfiatshitcoinsorgoldThatsrightBitcoinwilltakealltheenergyEveryonewilllivetheirownexperienceintherabbitholeWearegettingoursoulsbackandourminds` partialBold=``
- p80: phraseInitials=`S` bold=`` partialBold=``

## Selector Word Hits

- `all_bold_letters` hits TAKE, LEFT, RIGHT, LAYER, ONE, DIP, BUY, EL, BITCOIN, TOXIC: `THEYARETHESUMOFALLOURNEUROSESLAYERFACTITSLAYERFOREVERYGREATTHINGTHATSEVERBEENINVENTEDORDISCOVEREDMAXIMALISTKEEPYOURDIGNITYLAYERGETSOMETOXICITYGETSOMEBITCOINOPEN`
- `all_bold_letters:reverse` hits GREY, USE, EL: `SDNIMRUODNAKCABSLUOSRUOGNITTEGERAEWELOHTIBBAREHTNIECNEIREPXENWORIEHTEVILLLIWENOYREVEYGRENEEHTLLAEKATLLIWNIOCTIBTHGIRSTAHTDLOGROSNIOCTIHSTAIFNAHTNIHTLAEWEROTSDNA`
- `page76_bold_letters` hits ONE, DIP, BUY, BITCOIN, TOXIC: `GETSOMETOXICITYGETSOMEBITCOINOPENYOURHEARTTOBITCOINBYTHERANCIDCATNIPOFFIATMONEYBUYINGTHEDIPSHITCOINERATHEART`

## Rows

- orange p75 `They are the sum of all our neuroses.` -> mode=contiguous initials=`Tatsoaon` lasts=`yeemflrs` bold=`Theyarethesumofallourneuroses` partial=``
- orange p75 `Layer 1` -> mode=contiguous initials=`L` lasts=`r` bold=`Layer` partial=``
- orange p75 `Fact: It’s Layer 1 for every great thing that’s ever been invented or discovered.` -> mode=contiguous initials=`FILfegttebiod` lasts=`tsrrytgsrndrd` bold=`FactItsLayerforeverygreatthingthatseverbeeninventedordiscovered` partial=``
- orange p75 `“Maximalist”` -> mode=contiguous initials=`M` lasts=`t` bold=`Maximalist` partial=``
- orange p75 `Keep your dignity.` -> mode=contiguous initials=`Kyd` lasts=`pry` bold=`Keepyourdignity` partial=``
- orange p75 `Layer 1` -> mode=contiguous initials=`L` lasts=`r` bold=`Layer` partial=``
- orange p76 `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` -> mode=contiguous initials=`GstGsbOyhtB` lasts=`teytennrton` bold=`GetsometoxicityGetsomebitcoinOpenyourhearttoBitcoin` partial=``
- orange p76 `by the rancid catnip of fiat money.` -> mode=contiguous initials=`btrcofm` lasts=`yedpfty` bold=`bytherancidcatnipoffiatmoney` partial=``
- orange p76 `“buying the dip.”` -> mode=contiguous initials=`btd` lasts=`gep` bold=`buyingthedip` partial=``
- orange p76 `shitcoiner at heart.` -> mode=contiguous initials=`sah` lasts=`rtt` bold=`shitcoineratheart` partial=``
- orange p77 `Toxic Bitcoin Maximalists within six months.` -> mode=contiguous initials=`TBMwsm` lasts=`cnsnxs` bold=`ToxicBitcoinMaximalistswithinsixmonths` partial=``
- orange p77 `harass old women and children` -> mode=contiguous initials=`howac` lasts=`sdndn` bold=`harassoldwomenandchildren` partial=``
- orange p78 `The numbers don’t lie.` -> mode=contiguous initials=`Tndl` lasts=`este` bold=`Thenumbersdontlie` partial=``
- orange p78 `America left $85 BILLION worth of hate toys in Afghanistan,` -> mode=contiguous initials=`AlBwohtiA` lasts=`atNhfesnn` bold=`AmericaleftBILLIONworthofhatetoysinAfghanistan` partial=``
- orange p78 `$2 trillion fiat cuck-bucks.` -> mode=contiguous initials=`tfcb` lasts=`ntks` bold=`trillionfiatcuckbucks` partial=``
- orange p78 `the game-theorized Bitcoin protocol,` -> mode=contiguous initials=`tgtBp` lasts=`eednl` bold=`gametheorizedBitcoinprotocol` partial=``
- orange p79 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold` -> mode=contiguous initials=`imettaswitfsog` lasts=`yetotdehnntsrd` bold=`infinitelymoreefficienttotransactandstorewealthinthanfiatshitcoinsorgold` partial=``
- orange p79 `That’s right, Bitcoin will take all the energy.` -> mode=contiguous initials=`TrBwtate` lasts=`stnleley` bold=`ThatsrightBitcoinwilltakealltheenergy` partial=``
- orange p79 `Everyone will live their own experience in the rabbit hole. We are getting our souls back and our minds.` -> mode=contiguous initials=`EwltoeitrhWagosbaom` lasts=`elerneneteeegrskdrs` bold=`EveryonewilllivetheirownexperienceintherabbitholeWearegettingoursoulsbackandourminds` partial=``
- orange p80 `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS; 6 FL OZ (473 mL)` -> mode=missing_page initials=`` lasts=`` bold=`` partial=``
- grey_black p75 `money printers, banking terrorists, stock traders, central bank arsonists,` -> mode=contiguous initials=`mpbtstcba` lasts=`ysgskslks` bold=`` partial=``
- grey_black p75 `Don’t fall for shitcoinery.` -> mode=contiguous initials=`Dffs` lasts=`tlry` bold=`` partial=``
- grey_black p76 `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` -> mode=contiguous initials=`GbtwFyodpfmn` lasts=`aesyysfbttye` bold=`` partial=``
- grey_black p76 `It’s a stun gun to the genitals.` -> mode=contiguous initials=`Iasgttg` lasts=`sannoes` bold=`` partial=``
- grey_black p76 `$1 billion` -> mode=contiguous initials=`b` lasts=`n` bold=`` partial=``
- grey_black p76 `“Volcano Bonds”` -> mode=contiguous initials=`VB` lasts=`os` bold=`` partial=``
- grey_black p77 `(Sorry Bhutan, you fell for that snake oil salesmen over at XRP. Get ready to experience shitcoin hell.` -> mode=contiguous initials=`SByfftsosoaXGrtesh` lasts=`ynulrtelnrtPtyoenl` bold=`` partial=``
- grey_black p77 `Faketoshi` -> mode=contiguous initials=`F` lasts=`i` bold=`` partial=``
- grey_black p77 `shitcoiners, useless Royals,` -> mode=contiguous initials=`suR` lasts=`sss` bold=`` partial=``
- grey_black p77 `It does this by monetizing,` -> mode=contiguous initials=`Idtbm` lasts=`tssyg` bold=`` partial=``
- grey_black p78 `gargantuanly wasteful` -> mode=contiguous initials=`gw` lasts=`yl` bold=`` partial=``
- grey_black p78 `money printing` -> mode=contiguous initials=`mp` lasts=`yg` bold=`` partial=``
- grey_black p78 `wars to keep it going` -> mode=contiguous initials=`wtkig` lasts=`soptg` bold=`` partial=``
- grey_black p79 `war and violence economy` -> mode=contiguous initials=`wave` lasts=`rdey` bold=`` partial=``

## Assessment

- The highlight/bold intersection is structured but mostly reproduces already-visible emphasized words and known partial-bold fragments.
- Page 76 remains semantically strong, but the exact highlighted spans do not provide a plain instruction through initials, endings, lengths, or bold-only extraction.
- The next best move is source comparison or a manual selector hypothesis tied to the public mirror-writing clue, rather than more stream transforms.
