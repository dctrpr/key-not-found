# Source Alignment Audit

Purpose: validate the Canva concern that mixed PDF/image sources, rotation, and browser OCR can change what lines up.

## Source Files
- page 75: magazine_pdf_image=(2544, 3264), ocr_pdf_image=(2040, 2805)
- page 76: magazine_pdf_image=(2544, 3264), ocr_pdf_image=(2040, 2805)
- page 77: magazine_pdf_image=(2544, 3264), ocr_pdf_image=(2040, 2805)
- page 78: magazine_pdf_image=(2544, 3264), ocr_pdf_image=(2040, 2805)
- page 79: magazine_pdf_image=(2544, 3264), ocr_pdf_image=(2040, 2805)
- page 80: magazine_pdf_image=(2544, 3264), ocr_pdf_image=(2040, 2805)

## OCR Probe
The Canva note says browser/OCR viewing missed a “#0”. These exact OCR-PDF text probes show what the local OCR layer does preserve:
- 10years: missing
- 20,000: present
- 100,000: present
- 12,000: present
- shitcoin: present
- SHITCOINS: present

## Orange Highlight Registration
- page 75: highres_size=(2544, 3264), ocr_size=(2040, 2805), highres_orange_boxes=8, mapped_boxes=8
  01 highres=(1572, 984, 2076, 1032) center=(1824.0,1008.0) ocr_mapped=(1219, 784, 1619, 820) center=(1419.0,802.0)
  02 highres=(368, 1050, 812, 1099) center=(590.0,1074.5) ocr_mapped=(260, 840, 614, 877) center=(437.0,858.5)
  03 highres=(870, 1833, 1076, 1880) center=(973.0,1856.5) ocr_mapped=(666, 1462, 830, 1498) center=(748.0,1480.0)
  04 highres=(455, 1904, 1689, 1956) center=(1072.0,1930.0) ocr_mapped=(337, 1518, 1319, 1557) center=(828.0,1537.5)
  05 highres=(455, 1977, 1715, 2029) center=(1085.0,2003.0) ocr_mapped=(337, 1576, 1341, 1615) center=(839.0,1595.5)
  06 highres=(1271, 2200, 1608, 2248) center=(1439.5,2224.0) ocr_mapped=(989, 1753, 1257, 1789) center=(1123.0,1771.0)
  07 highres=(452, 2415, 925, 2464) center=(688.5,2439.5) ocr_mapped=(338, 1925, 714, 1962) center=(526.0,1943.5)
  08 highres=(544, 2553, 735, 2600) center=(639.5,2576.5) ocr_mapped=(412, 2035, 563, 2071) center=(487.5,2053.0)
- page 76: highres_size=(2544, 3264), ocr_size=(2040, 2805), highres_orange_boxes=5, mapped_boxes=5
  01 highres=(808, 373, 2215, 425) center=(1511.5,399.0) ocr_mapped=(638, 280, 1759, 320) center=(1198.5,300.0)
  02 highres=(813, 451, 1020, 498) center=(916.5,474.5) ocr_mapped=(642, 342, 806, 379) center=(724.0,360.5)
  03 highres=(429, 1351, 1306, 1400) center=(867.5,1375.5) ocr_mapped=(352, 1056, 1045, 1093) center=(698.5,1074.5)
  04 highres=(1334, 2177, 1801, 2225) center=(1567.5,2201.0) ocr_mapped=(1069, 1716, 1440, 1753) center=(1254.5,1734.5)
  05 highres=(1040, 2932, 1661, 2982) center=(1350.5,2957.0) ocr_mapped=(835, 2316, 1329, 2353) center=(1082.0,2334.5)
- page 77: highres_size=(2544, 3264), ocr_size=(2040, 2805), highres_orange_boxes=2, mapped_boxes=2
  01 highres=(768, 663, 1962, 710) center=(1365.0,686.5) ocr_mapped=(586, 521, 1536, 581) center=(1061.0,551.0)
  02 highres=(1440, 1225, 2232, 1273) center=(1836.0,1249.0) ocr_mapped=(1112, 983, 1742, 1034) center=(1427.0,1008.5)
- page 78: highres_size=(2544, 3264), ocr_size=(2040, 2805), highres_orange_boxes=4, mapped_boxes=4
  01 highres=(1137, 956, 1690, 1006) center=(1413.5,981.0) ocr_mapped=(861, 751, 1301, 789) center=(1081.0,770.0)
  02 highres=(1678, 1244, 2169, 1294) center=(1923.5,1269.0) ocr_mapped=(1290, 986, 1680, 1024) center=(1485.0,1005.0)
  03 highres=(431, 1321, 1808, 1445) center=(1119.5,1383.0) ocr_mapped=(297, 1037, 1392, 1138) center=(844.5,1087.5)
  04 highres=(1000, 1997, 2202, 2052) center=(1601.0,2024.5) ocr_mapped=(746, 1583, 1702, 1624) center=(1224.0,1603.5)
- page 79: highres_size=(2544, 3264), ocr_size=(2040, 2805), highres_orange_boxes=10, mapped_boxes=10
  01 highres=(579, 552, 1920, 716) center=(1249.5,634.0) ocr_mapped=(374, 442, 1439, 586) center=(906.5,514.0)
  02 highres=(1097, 830, 1904, 915) center=(1500.5,872.5) ocr_mapped=(791, 669, 1433, 715) center=(1112.0,692.0)
  03 highres=(592, 873, 979, 939) center=(785.5,906.0) ocr_mapped=(384, 717, 693, 755) center=(538.5,736.0)
  04 highres=(632, 2030, 2041, 2079) center=(1336.5,2054.5) ocr_mapped=(512, 1591, 1633, 1650) center=(1072.5,1620.5)
  05 highres=(632, 2104, 1660, 2152) center=(1146.0,2128.0) ocr_mapped=(512, 1650, 1633, 1714) center=(1072.5,1682.0)
  06 highres=(146, 2370, 196, 2446) center=(171.0,2408.0) ocr_mapped=(129, 1897, 167, 1952) center=(148.0,1924.5)
  07 highres=(387, 2429, 456, 2480) center=(421.5,2454.5) ocr_mapped=(324, 1939, 377, 1977) center=(350.5,1958.0)
  08 highres=(577, 2576, 635, 2641) center=(606.0,2608.5) ocr_mapped=(478, 2053, 522, 2102) center=(500.0,2077.5)
  09 highres=(408, 2746, 466, 2815) center=(437.0,2780.5) ocr_mapped=(347, 2191, 390, 2243) center=(368.5,2217.0)
  10 highres=(161, 2935, 206, 3001) center=(183.5,2968.0) ocr_mapped=(155, 2345, 182, 2394) center=(168.5,2369.5)
- page 80: highres_size=(2544, 3264), ocr_size=(2040, 2805), highres_orange_boxes=2, mapped_boxes=2
  01 highres=(1328, 1713, 1656, 2098) center=(1492.0,1905.5) ocr_mapped=(1151, 291, 1591, 686) center=(1371.0,488.5)
  02 highres=(917, 1939, 1200, 2099) center=(1058.5,2019.0) ocr_mapped=(650, 1317, 1344, 1759) center=(997.0,1538.0)

## Canva Anchor Candidates
Small orange components on page 79 are likely the pill marks mentioned in the Canva note.
- page 79 orange box 06: box=(146, 2370, 196, 2446) center=(171.0,2408.0) hflip_center=(2373.0,2408.0)
- page 79 orange box 07: box=(387, 2429, 456, 2480) center=(421.5,2454.5) hflip_center=(2122.5,2454.5)
- page 79 orange box 08: box=(577, 2576, 635, 2641) center=(606.0,2608.5) hflip_center=(1938.0,2608.5)
- page 79 orange box 09: box=(408, 2746, 466, 2815) center=(437.0,2780.5) hflip_center=(2107.0,2780.5)
- page 79 orange box 10: box=(161, 2935, 206, 3001) center=(183.5,2968.0) hflip_center=(2360.5,2968.0)

## Targeted Reflection Text
- 79 -> 75: truth. Bitcoin was not a reaction Financial Crisis of 2008. It caused it. Yes. / sensed Bitcoin was coming and started to / Markets are / It's only the language of the shameless opportunists trying / only the language of the shameless opportunists trying cash in by riding Bitcoins coattails that give it a bad name.
- 78 -> 76: honéy-badgering him / Our imaginations / ¥ortunately, bitcoin end to the paper chase Manhattan Bank money / Have you seen the president of El Salvador
- 76 -> 78: We've never had an economy and a money / any for gnample: for a war
- 79 -> 76: but George Clinton and James Brown clones. It's Martin Luther nailing the Vatican with ultimatums. It's the sound of skin being ripped off live central bankers tied to a burning stake. / Gotta be S way. Forty years of (and loyears of watching Peter / miss buying bitcoin / Have you seen the president of El Salvador / trolling the International Monetary Fund (IMF) on Twitter? taunting them, telling them he's ByiiREeraipy"

## Output Images
- highres_overlay_75_79_hflip.png
- highres_diff_75_79_hflip.png
- highres_overlay_76_78_hflip.png
- highres_diff_76_78_hflip.png
- highres_overlay_76_79_hflip.png
- highres_diff_76_79_hflip.png
- highres_overlay_75_78_hflip.png
- highres_diff_75_78_hflip.png

