# Annotated Color Span Analysis

Scope: parse the user-supplied natural-language annotations for orange and grey/black highlight spans, then match those phrases back to the canonical Markdown character model.

## Summary
- orange: matched-spans=13, anyBoldLen=340, partialBoldLen=0, page76AnyBoldLen=108, page76PartialBoldLen=0
- grey: matched-spans=11, anyBoldLen=0, partialBoldLen=0, page76AnyBoldLen=0, page76PartialBoldLen=0
- unmatched color annotations: 8

## Matched Spans
- p1 orange matched: phrase=`They are the sum of all our neuroses` partial=`` anyBold=`Theyarethesumofallourneuroses` indexes=[54, 55, 56, 57, 58, 59, 60, 61]
- p1 grey matched: phrase=`money printers, banking terrorists, stock traders, central bank arsonists` partial=`` anyBold=`` indexes=[86, 87, 88, 89, 90, 91, 92, 93, 94]
- p1 orange matched: phrase=`Layer 1` partial=`` anyBold=`Layer` indexes=[163, 164]
- p1 orange unmatched: phrase=`Fact: It's Layer 1 for every great thing that's ever been invented or discovered` partial=`` anyBold=`` indexes=[]
- p1 orange matched: phrase=`Maximalist` partial=`` anyBold=`Maximalist` indexes=[210]
- p1 grey unmatched: phrase=`Don't fall for shitcoinery` partial=`` anyBold=`` indexes=[]
- p1 orange matched: phrase=`Keep your dignity` partial=`` anyBold=`Keepyourdignity` indexes=[226, 227, 228]
- p1 orange matched: phrase=`Layer 1` partial=`` anyBold=`Layer` indexes=[163, 164]
- p2 orange matched: phrase=`Get some toxicity. Get some bitcoin. Open your heart to Bitcoin` partial=`` anyBold=`GetsometoxicityGetsomebitcoinOpenyourhearttoBitcoin` indexes=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- p2 grey matched: phrase=`Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` partial=`` anyBold=`` indexes=[61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
- p2 orange matched: phrase=`by the rancid catnip of fiat money` partial=`` anyBold=`bytherancidcatnipoffiatmoney` indexes=[127, 128, 129, 130, 131, 132, 133]
- p2 grey unmatched: phrase=`It's a stun gun to the genitals` partial=`` anyBold=`` indexes=[]
- p2 orange matched: phrase=`buying the dip` partial=`` anyBold=`buyingthedip` indexes=[187, 188, 189]
- p2 grey matched: phrase=`$1 billion` partial=`` anyBold=`` indexes=[208, 209]
- p2 grey matched: phrase=`Volcano Bonds` partial=`` anyBold=`` indexes=[223, 224]
- p2 orange matched: phrase=`shitcoiner at heart` partial=`` anyBold=`shitcoineratheart` indexes=[274, 275, 276]
- p3 orange matched: phrase=`Toxic Bitcoin Maximalists within six months` partial=`` anyBold=`ToxicBitcoinMaximalistswithinsixmonths` indexes=[47, 48, 49, 50, 51, 52]
- p3 grey unmatched: phrase=`Sorry Bhutan, you fell for that snake oil salesman over at XRP. Get ready to experience shitcoin hell` partial=`` anyBold=`` indexes=[]
- p3 grey matched: phrase=`Faketoshi` partial=`` anyBold=`` indexes=[101]
- p3 orange matched: phrase=`harass old women and children` partial=`` anyBold=`harassoldwomenandchildren` indexes=[112, 113, 114, 115, 116]
- p3 grey matched: phrase=`shitcoiners, useless Royals` partial=`` anyBold=`` indexes=[135, 136, 137]
- p3 grey matched: phrase=`it does this by monetizing` partial=`` anyBold=`` indexes=[251, 252, 253, 254, 255]
- p4 orange unmatched: phrase=`The number don't lie` partial=`` anyBold=`` indexes=[]
- p4 grey matched: phrase=`gargantuanly wasteful` partial=`` anyBold=`` indexes=[73, 74]
- p4 grey matched: phrase=`money printing` partial=`` anyBold=`` indexes=[77, 78]
- p4 grey matched: phrase=`wars to keep it going` partial=`` anyBold=`` indexes=[80, 81, 82, 83, 84]
- p4 orange unmatched: phrase=`America left $85 BILLION worth of hate toy in Afghanistan` partial=`` anyBold=`` indexes=[]
- p4 orange matched: phrase=`$2 trillion fiat cuck-bucks` partial=`` anyBold=`trillionfiatcuckbucks` indexes=[127, 128, 129, 130, 131]
- p5 grey matched: phrase=`war and violence economy` partial=`` anyBold=`` indexes=[9, 10, 11, 12]
- p5 orange unmatched: phrase=`infinitely more efficient to transact and store wealth in than fiat, shitcoin or gold` partial=`` anyBold=`` indexes=[]
- p5 orange unmatched: phrase=`That's right, Bitcoin will take all the energy` partial=`` anyBold=`` indexes=[]
- p5 orange matched: phrase=`Everyone will live their own experience in the rabbit hole. We are getting our souls back and our minds` partial=`` anyBold=`EveryonewilllivetheirownexperienceintherabbitholeWearegettingoursoulsbackandourminds` indexes=[169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187]

## Color Streams
### orange
- first letters: `TatsoaonL1MKydL1GstGsbOyhtBbtrcofmbtdsahTBMwsmhowac$tfcbEwltoeitrhWagosbaom`
- last letters: `yeemflrsr1tpryr1teytennrtonyedpftygeprttcnsnxssdndn2ntkselerneneteeegrskdrs`
- any bold: `TheyarethesumofallourneurosesLayerMaximalistKeepyourdignityLayerGetsometoxicityGetsomebitcoinOpenyourhearttoBitcoinbytherancidcatnipoffiatmoneybuyingthedipshitcoineratheartToxicBitcoinMaximalistswithinsixmonthsharassoldwomenandchildrentrillionfiatcuckbucksEveryonewilllivetheirownexperienceintherabbitholeWearegettingoursoulsbackandourminds`
- partial bold: ``
- page76 any bold: `GetsometoxicityGetsomebitcoinOpenyourhearttoBitcoinbytherancidcatnipoffiatmoneybuyingthedipshitcoineratheart`
- page76 partial bold: ``
### grey
- first letters: `mpbtstcbaGbtwFyodp1fmn$bVBFsuRIdtbmgwmpwtkigwave`
- last letters: `ysgskslksaesyysfbt1tye1nosissstssygylygsoptgrdey`
- any bold: ``
- partial bold: ``
- page76 any bold: ``
- page76 partial bold: ``

## Assessment
- Color matching gives a stricter selector than bold alone, but the page-76 color intersections are still phrase-like rather than key-shaped.
- Grey/black on page 76 isolates the struck Peter Schiff line plus grey-highlighted money/volcano phrases; orange isolates the public “heart/Bitcoin/buying dip/shitcoiner” phrases.
- Next useful test is geometric: compare these color spans against reflected orange/black mask boxes to see which highlighted phrases are touched by the mirror, instead of hashing the color text directly.
