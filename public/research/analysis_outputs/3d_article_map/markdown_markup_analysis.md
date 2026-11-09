# Markdown Markup Analysis

Scope: parse the user-supplied Markdown transcript as a markup source. `**...**` is bold; `~~...~~` is black/grey highlight.

## Counts
- Page 1: bold=59, partial=45, whole=2, phrase=12, strike=0, partial_stream_len=70
- Page 2: bold=35, partial=23, whole=5, phrase=7, strike=1, partial_stream_len=31
- Page 3: bold=46, partial=39, whole=2, phrase=5, strike=0, partial_stream_len=57
- Page 4: bold=28, partial=10, whole=2, phrase=16, strike=0, partial_stream_len=12
- Page 5: bold=64, partial=55, whole=0, phrase=9, strike=0, partial_stream_len=78

- all partial-bold letters: 248
- all bold letters including full phrases: 1908

## Partial-Bold Streams By Page
### Page 1
- raw: `ThediuuffidvelleivehelefmiNwidhiiedevemeieidehiiTiiiimViliueiGiiTiimli`
- chunks 5: `Thedi uuffi dvell eiveh elefm iNwid hiied eveme ieide hiiTi iiimV iliue iGiiT iimli`
- reverse chunks 5: `ilmii TiiGi euili Vmiii iTiih ediei emeve deiih diwNi mfele hevie llevd iffuu idehT`
- atbash chunks 5: `Gsvwr ffuur wevoo vrevs vovun rMdrw srrvw vevnv rvrwv srrGr rrrnE rorfv rTrrG rrnor`

### Page 2
- raw: `eelibeippedelbeielvdieNvzelluhu`
- chunks 5: `eelib eippe delbe ielvd ieNvz elluh u`
- reverse chunks 5: `uhull ezvNe idvle ieble deppi ebile e`
- atbash chunks 5: `vvory vrkkv wvoyv rvoew rvMea voofs f`

### Page 3
- raw: `lleReVeBleemullSphiifidldvedehheeulfBiiiibleuefllvilbleee`
- chunks 5: `lleRe VeBle emull Sphii fidld vedeh heeul fBiii ibleu efllv ilble ee`
- reverse chunks 5: `eeelb livll feuel biiii Bflue ehhed evdld ifiih pSllu meelB eVeRe ll`
- atbash chunks 5: `oovIv EvYov vnfoo Hksrr urwow evwvs svvfo uYrrr ryovf vuooe royov vv`

### Page 4
- raw: `wmemiibiifue`
- chunks 5: `wmemi ibiif ue`
- reverse chunks 5: `eufii biime mw`
- atbash chunks 5: `dnvnr ryrru fv`

### Page 5
- raw: `diueumpidpezebeueuuledewdlveeeemeizedfhefiimeiuexeedhvebeeliviiheefepphellwihu`
- chunks 5: `diueu mpidp ezebe ueuul edewd lveee emeiz edfhe fiime iuexe edhve beeli viihe efepp hellw ihu`
- reverse chunks 5: `uhiwl lehpp efeeh iivil eebev hdeex euiem iifeh fdezi emeee evldw edelu ueueb ezepd ipmue uid`
- atbash chunks 5: `wrfvf nkrwk vavyv fvffo vwvdw oevvv vnvra vwusv urrnv rfvcv vwsev yvvor errsv vuvkk svood rsf`

## Combined Partial-Bold Stream
- raw: `ThediuuffidvelleivehelefmiNwidhiiedevemeieidehiiTiiiimViliueiGiiTiimlieelibeippedelbeielvdieNvzelluhulleReVeBleemullSphiifidldvedehheeulfBiiiibleuefllvilbleeewmemiibiifuediueumpidpezebeueuuledewdlveeeemeizedfhefiimeiuexeedhvebeeliviiheefepphellwihu`
- chunks 5: `Thedi uuffi dvell eiveh elefm iNwid hiied eveme ieide hiiTi iiimV iliue iGiiT iimli eelib eippe delbe ielvd ieNvz elluh ulleR eVeBl eemul lSphi ifidl dvede hheeu lfBii iible uefll vilbl eeewm emiib iifue diueu mpidp ezebe ueuul edewd lveee emeiz edfhe fiime iuexe edhve beeli viihe efepp hellw ihu`
- chunks 8: `Thediuuf fidvelle ivehelef miNwidhi iedeveme ieidehii TiiiimVi liueiGii Tiimliee libeippe delbeiel vdieNvze lluhulle ReVeBlee mullSphi ifidldve dehheeul fBiiiibl euefllvi lbleeewm emiibiif uediueum pidpezeb eueuuled ewdlveee emeizedf hefiimei uexeedhv ebeelivi iheefepp hellwihu`
- reverse chunks 5: `uhiwl lehpp efeeh iivil eebev hdeex euiem iifeh fdezi emeee evldw edelu ueueb ezepd ipmue uideu fiibi imemw eeelb livll feuel biiii Bflue ehhed evdld ifiih pSllu meelB eVeRe lluhu llezv Neidv leieb ledep piebi leeil miiTi iGieu iliVm iiiiT iihed ieiem evede iihdi wNimf elehe viell evdif fuuid ehT`
- atbash chunks 5: `Gsvwr ffuur wevoo vrevs vovun rMdrw srrvw vevnv rvrwv srrGr rrrnE rorfv rTrrG rrnor vvory vrkkv wvoyv rvoew rvMea voofs foovI vEvYo vvnfo oHksr rurwo wevwv ssvvf ouYrr rryov fvuoo eroyo vvvdn vnrry rrufv wrfvf nkrwk vavyv fvffo vwvdw oevvv vnvra vwusv urrnv rfvcv vwsev yvvor errsv vuvkk svood rsf`

## First Caesar Candidates For Combined Partial Stream
- shift 0: `thedi uuffi dvell eiveh elefm inwid hiied eveme ieide hiiti iiimv iliue igiit iimli eelib eippe delbe ielvd ienvz elluh uller evebl eemul lsphi ifidl dvede hheeu lfbii iible uefll vilbl eeewm emiib iifue diueu mpidp ezebe ueuul edewd lveee emeiz edfhe fiime iuexe edhve beeli viihe efepp hellw ihu`
- shift 1: `uifej vvggj ewfmm fjwfi fmfgn joxje ijjfe fwfnf jfjef ijjuj jjjnw jmjvf jhjju jjnmj ffmjc fjqqf efmcf jfmwe jfowa fmmvi vmmfs fwfcm ffnvm mtqij jgjem ewfef iiffv mgcjj jjcmf vfgmm wjmcm fffxn fnjjc jjgvf ejvfv nqjeq fafcf vfvvm fefxe mwfff fnfja fegif gjjnf jvfyf feiwf cffmj wjjif fgfqq ifmmx jiv`
- shift 2: `vjgfk wwhhk fxgnn gkxgj gngho kpykf jkkgf gxgog kgkfg jkkvk kkkox knkwg kikkv kkonk ggnkd gkrrg fgndg kgnxf kgpxb gnnwj wnngt gxgdn ggown nurjk khkfn fxgfg jjggw nhdkk kkdng wghnn xkndn gggyo gokkd kkhwg fkwgw orkfr gbgdg wgwwn gfgyf nxggg gogkb gfhjg hkkog kwgzg gfjxg dggnk xkkjg ghgrr jgnny kjw`
- shift 3: `wkhgl xxiil gyhoo hlyhk hohip lqzlg kllhg hyhph lhlgh kllwl lllpy lolxh ljllw llpol hhole hlssh ghoeh lhoyg lhqyc hooxk xoohu hyheo hhpxo ovskl lilgo gyhgh kkhhx oiell lleoh xhioo yloeo hhhzp hplle llixh glxhx pslgs hcheh xhxxo hghzg oyhhh hphlc hgikh illph lxhah hgkyh ehhol yllkh hihss khooz lkx`
- shift 13: `gurqv hhssv qiryy rviru ryrsz vajvq uvvrq rirzr vrvqr uvvgv vvvzi vyvhr vtvvg vvzyv rryvo rvccr qryor vryiq vraim ryyhu hyyre riroy rrzhy yfcuv vsvqy qirqr uurrh ysovv vvoyr hrsyy ivyoy rrrjz rzvvo vvshr qvhrh zcvqc rmror hrhhy rqrjq yirrr rzrvm rqsur svvzr vhrkr rquir orryv ivvur rsrcc uryyj vuh`
- shift 23: `qebaf rrccf asbii bfsbe bibcj fktfa effba bsbjb fbfab effqf fffjs fifrb fdffq ffjif bbify bfmmb abiyb fbisa fbksw biire riibo bsbyi bbjri ipmef fcfai asbab eebbr icyff ffyib rbcii sfiyi bbbtj bjffy ffcrb afrbr jmfam bwbyb rbrri babta isbbb bjbfw baceb cffjb frbub baesb ybbif sffeb bcbmm ebiit fer`
- shift 24: `rfcbg ssddg btcjj cgtcf cjcdk glugb fggcb ctckc gcgbc fggrg gggkt gjgsc geggr ggkjg ccjgz cgnnc bcjzc gcjtb gcltx cjjsf sjjcp ctczj ccksj jqnfg gdgbj btcbc ffccs jdzgg ggzjc scdjj tgjzj cccuk ckggz ggdsc bgscs kngbn cxczc scssj cbcub jtccc ckcgx cbdfc dggkc gscvc cbftc zccjg tggfc cdcnn fcjju gfs`
- shift 25: `sgdch tteeh cudkk dhudg dkdel hmvhc ghhdc dudld hdhcd ghhsh hhhlu hkhtd hfhhs hhlkh ddkha dhood cdkad hdkuc hdmuy dkktg tkkdq dudak ddltk krogh hehck cudcd ggddt keahh hhakd tdekk uhkak dddvl dlhha hhetd chtdt lohco dydad tdttk dcdvc kuddd dldhy dcegd ehhld htdwd dcgud addkh uhhgd dedoo gdkkv hgt`

## Highlight/Strike Spans
- Page 2: `(and 10 years of watching Peter Schiff miss buying bitcoin`

## Assessment
- Partial bold fragments form a real, extractable sequence, but raw/reverse/atbash/simple Caesar do not immediately read as prose.
- The sequence should be treated as structured key material or an index stream, not discarded.
- Next best checks: map partial-bold stream positions back onto page geometry, compare with orange/black spans, and test whether per-page lengths or page-order chunks match BIP39/private-key index sizes only after a stronger selector is found.
