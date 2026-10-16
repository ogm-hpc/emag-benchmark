# PCBベンチマーク 結果サマリー（mac_m3pro、WSLの結果とは比べない）

- 元データ: `results/pcb_v1/runs/`（1344件。標準 1344件、変種 0件）
- 予算: 43200 秒（setupを含む）。PCB_SOLVER_VERSION: 1.0
- 反復回数の上限 K_max: gs/gmres 10000, ssor/gmres 10000, ssor/cocg 50000, amg_gamg/gmres 10000, amg_gamg/cocg 50000, accel_ic/gmres 10000, accel_ic/cocg 50000, cslp/gmres 3000, hx/gmres 10000, cslp_hx/gmres 1000, npatch_asm/cocg 50000
- 生成: `python3 freefem/pcb/summarize_pcb_benchmark.py`。時間の定義・\|dS\| はスクリプト冒頭の説明を参照

## 標準の結果（ケース×組合せ）

収束は「総時間 s（反復数）」、それ以外は状態と最終相対残差。

| case | gs/gmres | ssor/gmres | ssor/cocg | amg_gamg/gmres | amg_gamg/cocg | accel_ic/gmres | accel_ic/cocg | cslp/gmres | hx/gmres | cslp_hx/gmres | npatch_asm/cocg | mumps/direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01-1 | max_it 2.2e-03 | max_it 5.4e-04 | 71 s (10538) | max_it 5.6e-04 | 113 s (10270) | max_it 7.9e-04 | 69 s (12031) | 85 s (423) | 13 s (61) | 14 s (49) | 8.6 s (319) | 5.6 s (1) |
| P01-2 | max_it 3.2e-06 | 132 s (8260) | 43 s (4947) | max_it 1.4e-08 | 102 s (7456) | 304 s (9447) | 42 s (5673) | 59 s (228) | 36 s (271) | 34 s (117) | 16 s (816) | 6.8 s (1) |
| P01-3 | max_it 2.4e-03 | max_it 4.9e-04 | 173 s (26833) | max_it 5.6e-04 | 262 s (24154) | max_it 7.3e-04 | 190 s (33890) | 313 s (1626) | 15 s (61) | 11 s (28) | 8.5 s (317) | 5.5 s (1) |
| P01-1_coarse | max_it 3.8e-04 | max_it 9.0e-06 | 7.3 s (3905) | max_it 1.1e-05 | 12 s (4345) | max_it 5.0e-05 | 6.8 s (4301) | 8.9 s (181) | 5.2 s (156) | 2.8 s (32) | 1.9 s (199) | 1.3 s (1) |
| P01-1_fine | max_it 8.8e-03 | max_it 2.7e-03 | 772 s (21950) | max_it 4.8e-03 | 1735 s (28686) | max_it 3.2e-03 | 825 s (26475) | 1299 s (1175) | 66 s (39) | 81 s (49) | 61 s (572) | 37 s (1) |
| P01-1_sibc | max_it 2.2e-03 | max_it 5.4e-04 | 65 s (9523) | max_it 5.9e-04 | 101 s (9090) | max_it 7.7e-04 | 69 s (11797) | 102 s (513) | 9.6 s (29) | 15 s (50) | 9.0 s (318) | 5.5 s (1) |
| P01-2_sibc | max_it 3.1e-06 | 132 s (8235) | 45 s (5114) | max_it 1.7e-08 | 98 s (7124) | 303 s (9421) | 42 s (5560) | 59 s (227) | 70 s (597) | 34 s (118) | 18 s (855) | 6.7 s (1) |
| P01-a_f0.5 | max_it 3.3e-03 | max_it 1.0e-03 | 89 s (13267) | max_it 1.0e-03 | 153 s (13959) | max_it 1.3e-03 | 94 s (16262) | 118 s (592) | 14 s (60) | 11 s (29) | 8.3 s (306) | 5.5 s (1) |
| P01-a_f2 | max_it 1.5e-03 | max_it 1.7e-04 | 51 s (7342) | max_it 2.0e-04 | 89 s (7997) | max_it 3.5e-04 | 59 s (10067) | 50 s (240) | 12 s (64) | 15 s (51) | 8.6 s (331) | 5.5 s (1) |
| P01-a_f5 | max_it 1.5e-04 | max_it 8.8e-07 | 41 s (5681) | max_it 2.7e-06 | 78 s (6794) | max_it 5.1e-06 | 44 s (7034) | 45 s (208) | 13 s (85) | 19 s (71) | 9.8 s (408) | 5.6 s (1) |
| P01-a_f20 | 252 s (6728) | 153 s (3721) | 83 s (3740) | 518 s (9716) | 652 s (19259) | 341 s (4261) | 86 s (4508) | 214 s (329) | max_it 1.5e-05 | 196 s (289) | 97 s (2561) | 18 s (1) |
| P01-b_L16.4 | 75 s (9944) | 42 s (5197) | 15 s (3380) | 61 s (5726) | 33 s (4681) | 100 s (6008) | 16 s (3942) | 20 s (153) | 11 s (154) | 11 s (67) | 5.9 s (412) | 3.2 s (1) |
| P01-b_L32.9 | max_it 1.0e-06 | 108 s (7875) | 34 s (4402) | 162 s (8924) | 83 s (7034) | 254 s (9202) | 36 s (5524) | 47 s (212) | 27 s (239) | 26 s (105) | 13 s (703) | 5.7 s (1) |
| P01-b_L65.7 | max_it 5.4e-05 | max_it 3.7e-08 | 85 s (6362) | max_it 1.8e-06 | 232 s (10908) | max_it 2.2e-07 | 89 s (7693) | 132 s (332) | 247 s (1444) | 73 s (169) | 34 s (1275) | 11 s (1) |
| P01-b_L131.4 | max_it 8.6e-04 | max_it 8.2e-06 | 247 s (10032) | max_it 4.4e-04 | 778 s (19090) | max_it 3.1e-05 | 257 s (12038) | 525 s (700) | 893 s (2696) | 248 s (305) | 109 s (2457) | 21 s (1) |
| P01-1_td0 | max_it 2.2e-03 | max_it 5.4e-04 | 68 s (10054) | max_it 5.7e-04 | 113 s (10205) | max_it 7.9e-04 | 70 s (12274) | 84 s (422) | 13 s (61) | 15 s (49) | 8.4 s (319) | 5.6 s (1) |
| P01-1_td0.02 | max_it 2.0e-03 | max_it 5.2e-04 | 69 s (10206) | max_it 5.5e-04 | 108 s (9731) | max_it 7.6e-04 | 66 s (11471) | 86 s (429) | 13 s (61) | 14 s (49) | 8.5 s (319) | 5.5 s (1) |
| P01-2_td0 | max_it 3.5e-06 | 133 s (8304) | 44 s (5009) | max_it 1.5e-08 | 102 s (7447) | 307 s (9530) | 43 s (5758) | 59 s (228) | 36 s (271) | 34 s (117) | 17 s (843) | 6.8 s (1) |
| P01-2_td0.02 | max_it 1.8e-06 | 127 s (7912) | 43 s (4934) | 212 s (9986) | 98 s (7065) | 294 s (9132) | 43 s (5621) | 58 s (225) | 36 s (270) | 33 s (116) | 16 s (778) | 6.7 s (1) |
| P01-2_N20 | 293 s (7833) | 177 s (4351) | 70 s (3055) | 366 s (6804) | 176 s (4936) | 397 s (4981) | 73 s (3713) | 106 s (156) | 176 s (622) | 72 s (94) | 42 s (836) | 18 s (1) |
| P01-1_t | max_it 2.0e-02 | max_it 1.3e-02 | max_it 3.7e-02 | max_it 1.2e-02 | max_it 4.1e-02 | max_it 1.3e-02 | max_it 2.7e-01 | max_it 3.7e-05 | 63 s (44) | 135 s (104) | 49 s (434) | 30 s (1) |
| P01-2_t | max_it 3.3e-02 | max_it 1.8e-02 | max_it 5.0e-04 | max_it 1.9e-02 | max_it 1.4e-03 | max_it 1.6e-02 | max_it 1.1e-03 | max_it 3.7e-05 | 172 s (267) | 272 s (219) | 90 s (1171) | 31 s (1) |
| P02-a_h0.2 | max_it 1.6e-03 | max_it 4.7e-06 | 29 s (4719) | max_it 3.2e-04 | 84 s (9070) | max_it 3.5e-05 | 29 s (5540) | 42 s (245) | 25 s (265) | 20 s (102) | 10 s (630) | 4.5 s (1) |
| P02-a_h0.05 | max_it 1.9e-02 | max_it 1.2e-03 | 59 s (10374) | max_it 6.6e-03 | 157 s (17437) | max_it 2.4e-03 | 56 s (11337) | 107 s (669) | 25 s (272) | 23 s (122) | 9.8 s (579) | 4.5 s (1) |
| P02-b_h0.2 | max_it 6.4e-02 | max_it 5.3e-02 | max_it 1.8e-02 | max_it 5.3e-02 | max_it 6.2e-01 | max_it 4.6e-02 | max_it 4.2e-01 | max_it 2.8e-03 | 441 s (476) | max_it 1.5e-03 | 172 s (2352) | 35 s (1) |
| P02-sr_h1.6 | max_it 3.3e-02 | max_it 1.5e-02 | 165 s (29845) | max_it 1.1e-02 | 270 s (30228) | max_it 1.1e-02 | 128 s (27405) | 236 s (1481) | 12 s (61) | 14 s (65) | 7.5 s (352) | 4.8 s (1) |
| P03-1 | max_it 4.9e-02 | max_it 3.2e-02 | max_it 4.2e-05 | max_it 2.6e-02 | max_it 2.2e-05 | max_it 2.7e-02 | max_it 4.8e-05 | max_it 8.0e-05 | 430 s (903) | 236 s (272) | 82 s (1521) | 26 s (1) |
| P03-2 | max_it 5.0e-02 | max_it 3.1e-02 | max_it 3.6e-05 | max_it 2.6e-02 | max_it 5.9e-05 | max_it 2.7e-02 | max_it 7.0e-05 | max_it 6.5e-05 | 415 s (955) | 234 s (270) | 84 s (1562) | 27 s (1) |
| P03-3 | max_it 5.3e-02 | max_it 3.6e-02 | max_it 6.2e-05 | max_it 3.0e-02 | max_it 1.0e-04 | max_it 3.2e-02 | max_it 2.7e-03 | max_it 1.6e-04 | 604 s (1470) | 222 s (277) | 85 s (1709) | 24 s (1) |
| P03-r1 | max_it 5.1e-02 | max_it 3.3e-02 | max_it 5.1e-05 | max_it 2.8e-02 | max_it 4.9e-05 | max_it 2.8e-02 | max_it 2.0e-03 | max_it 8.4e-05 | 486 s (1214) | 227 s (277) | 82 s (1590) | 25 s (1) |
| P03-r2 | max_it 4.8e-02 | max_it 3.3e-02 | max_it 9.0e-06 | max_it 2.8e-02 | max_it 3.1e-04 | max_it 2.8e-02 | max_it 1.6e-02 | max_it 7.8e-05 | 498 s (1173) | 229 s (273) | 81 s (1595) | 25 s (1) |
| P03-r8 | max_it 4.9e-02 | max_it 3.3e-02 | max_it 5.3e-05 | max_it 2.7e-02 | max_it 6.3e-05 | max_it 2.8e-02 | max_it 5.0e-02 | max_it 8.7e-05 | 449 s (961) | 255 s (271) | 88 s (1526) | 29 s (1) |
| P03-d0.7 | max_it 5.0e-02 | max_it 3.4e-02 | max_it 3.1e-03 | max_it 2.9e-02 | max_it 5.6e-06 | max_it 2.8e-02 | max_it 6.1e-03 | max_it 9.2e-05 | 537 s (1279) | 232 s (274) | 83 s (1579) | 26 s (1) |
| P03-d2 | max_it 4.9e-02 | max_it 3.0e-02 | max_it 3.4e-06 | max_it 2.5e-02 | max_it 2.4e-06 | max_it 2.7e-02 | max_it 2.6e-05 | max_it 6.9e-05 | 397 s (864) | 255 s (274) | 92 s (1556) | 29 s (1) |
| P03-d5 | max_it 5.4e-02 | max_it 3.6e-02 | max_it 2.5e-05 | max_it 3.0e-02 | max_it 8.3e-05 | max_it 3.2e-02 | max_it 1.8e-02 | max_it 1.4e-04 | 561 s (1179) | 271 s (279) | 93 s (1568) | 28 s (1) |
| P03-v0.2 | max_it 4.9e-02 | max_it 3.2e-02 | max_it 1.4e-05 | max_it 2.7e-02 | max_it 2.5e-04 | max_it 2.8e-02 | max_it 1.4e-04 | max_it 1.1e-04 | 444 s (907) | 278 s (288) | 92 s (1547) | 29 s (1) |
| P03-v0.5 | max_it 4.9e-02 | max_it 3.2e-02 | max_it 7.2e-05 | max_it 2.8e-02 | max_it 1.3e-05 | max_it 2.7e-02 | max_it 2.2e-04 | max_it 9.0e-05 | 417 s (1050) | 222 s (268) | 79 s (1518) | 25 s (1) |
| P03-a0.6 | max_it 5.0e-02 | max_it 3.2e-02 | max_it 3.3e-05 | max_it 2.6e-02 | max_it 5.0e-06 | max_it 2.7e-02 | max_it 2.6e-03 | max_it 9.6e-05 | 471 s (1087) | 237 s (271) | 85 s (1519) | 27 s (1) |
| P03-a1.2 | max_it 4.9e-02 | max_it 3.1e-02 | max_it 5.6e-06 | max_it 2.6e-02 | max_it 1.5e-05 | max_it 2.7e-02 | max_it 1.8e-04 | max_it 5.9e-05 | 412 s (957) | 232 s (267) | 83 s (1507) | 27 s (1) |
| P04-1 | max_it 2.6e-02 | max_it 1.3e-02 | 1504 s (42790) | max_it 1.2e-02 | 2892 s (47576) | max_it 1.2e-02 | 1476 s (48204) | max_it 2.8e-05 | 80 s (63) | 203 s (161) | 74 s (779) | 38 s (1) |
| P04-2 | max_it 3.7e-02 | max_it 1.6e-02 | 1447 s (40777) | max_it 1.5e-02 | 2876 s (47239) | max_it 1.4e-02 | 1491 s (48694) | max_it 7.2e-06 | 83 s (68) | 197 s (155) | 73 s (762) | 38 s (1) |
| P04-3 | max_it 4.4e-02 | max_it 1.6e-02 | 1482 s (40983) | max_it 1.5e-02 | 2951 s (47888) | max_it 1.6e-02 | max_it 3.0e-06 | max_it 1.9e-06 | 95 s (82) | 198 s (151) | 76 s (787) | 39 s (1) |
| P04-4 | max_it 3.4e-02 | max_it 1.8e-02 | 2097 s (40039) | max_it 1.6e-02 | 3970 s (43811) | max_it 1.6e-02 | 2140 s (46894) | max_it 5.5e-08 | 805 s (705) | 345 s (177) | 381 s (3848) | 58 s (1) |
| P05-1 | max_it 4.9e-05 | max_it 1.0e-06 | 16 s (4070) | max_it 1.7e-08 | 23 s (4043) | max_it 7.1e-06 | 17 s (5242) | 22 s (215) | 6.3 s (33) | 5.2 s (20) | 4.7 s (366) | 3.0 s (1) |
| P05-2 | max_it 1.9e-02 | max_it 2.3e-04 | 14 s (3492) | max_it 2.0e-06 | 21 s (3617) | max_it 3.6e-03 | 16 s (4647) | 19 s (181) | 7.2 s (44) | 5.8 s (28) | 5.0 s (429) | 2.9 s (1) |
| P05-3 | max_it 2.0e-02 | max_it 2.2e-04 | 14 s (3619) | max_it 1.8e-06 | 20 s (3440) | max_it 4.1e-03 | 15 s (4381) | 19 s (179) | 7.2 s (44) | 5.8 s (28) | 5.0 s (429) | 2.9 s (1) |
| P05-2_sibc | max_it 7.5e-03 | max_it 2.4e-04 | 16 s (4091) | max_it 8.9e-06 | 20 s (3539) | max_it 1.0e-03 | 16 s (4879) | 25 s (248) | 4.2 s (30) | 5.9 s (30) | 5.7 s (434) | 2.9 s (1) |
| P05-g0.1 | max_it 1.7e-02 | max_it 5.5e-05 | 20 s (5373) | max_it 7.0e-06 | 22 s (3817) | max_it 6.1e-03 | 19 s (5880) | 23 s (231) | 7.3 s (45) | 5.6 s (26) | 5.0 s (432) | 2.9 s (1) |
| P05-g1.0 | max_it 9.4e-03 | max_it 2.8e-04 | 16 s (4099) | max_it 2.8e-05 | 23 s (4019) | max_it 4.3e-04 | 16 s (5113) | 24 s (239) | 7.6 s (48) | 6.0 s (31) | 5.0 s (448) | 2.9 s (1) |
| P05-fc | max_it 6.8e-05 | max_it 5.0e-06 | 13 s (3308) | max_it 2.3e-08 | 18 s (3005) | max_it 4.3e-05 | 13 s (3937) | 18 s (175) | 7.2 s (44) | 5.9 s (29) | 4.8 s (390) | 2.9 s (1) |
| P05-fe | max_it 5.0e-03 | max_it 2.1e-04 | 16 s (4036) | max_it 9.4e-06 | 20 s (3526) | max_it 5.2e-04 | 17 s (5185) | 19 s (187) | 7.1 s (43) | 5.7 s (28) | 4.9 s (426) | 2.9 s (1) |
| P05-n1 | 4.9 s (866) | 2.5 s (244) | 2.2 s (270) | 2.7 s (226) | 2.5 s (251) | 4.3 s (305) | 2.3 s (347) | 3.3 s (26) | max_it nan | 3.5 s (26) | 2.8 s (443) | 1.9 s (1) |
| P05-n4 | max_it 1.9e-02 | max_it 7.6e-03 | 43 s (6345) | max_it 7.3e-04 | 63 s (5940) | max_it 5.1e-03 | 46 s (7988) | 75 s (413) | 12 s (43) | 12 s (37) | 9.2 s (400) | 5.2 s (1) |
| P05-td1e-4 | max_it 1.9e-02 | max_it 2.2e-04 | 15 s (3731) | max_it 1.8e-06 | 20 s (3347) | max_it 4.0e-03 | 15 s (4423) | 18 s (178) | 7.2 s (44) | 5.8 s (28) | 5.0 s (429) | 3.0 s (1) |
| P05-td1e-2 | max_it 5.9e-03 | max_it 1.1e-04 | 16 s (4016) | max_it 4.5e-06 | 22 s (3883) | max_it 9.3e-04 | 16 s (4711) | 19 s (189) | 7.2 s (44) | 5.8 s (28) | 5.0 s (429) | 2.9 s (1) |
| P05-lc1.25 | max_it 1.8e-02 | max_it 7.9e-03 | 59 s (4270) | max_it 3.6e-03 | 76 s (3559) | max_it 9.2e-03 | 59 s (4944) | 70 s (183) | 26 s (43) | 22 s (33) | 23 s (823) | 10 s (1) |
| P05-lc0.625 | max_it 1.1e-02 | max_it 1.0e-02 | 243 s (4559) | max_it 8.0e-03 | 335 s (3864) | max_it 8.2e-03 | 251 s (5357) | 272 s (169) | 132 s (64) | 123 s (57) | 141 s (1600) | 42 s (1) |
| P06-L0 | max_it 2.0e-02 | max_it 5.5e-03 | 540 s (18324) | max_it 1.0e-02 | 1176 s (23581) | max_it 7.2e-03 | 571 s (21879) | 1029 s (1130) | 86 s (137) | 143 s (135) | 64 s (882) | 30 s (1) |
| P06-L10 | max_it 1.9e-02 | max_it 2.4e-03 | 564 s (17353) | max_it 1.1e-02 | 1627 s (29718) | max_it 4.2e-03 | 606 s (21215) | 1888 s (1894) | 1212 s (2725) | 337 s (304) | 137 s (2187) | 33 s (1) |
| P06-L30 | max_it 2.7e-02 | max_it 8.0e-03 | 874 s (22609) | max_it 1.4e-02 | 2189 s (32975) | max_it 1.1e-02 | 981 s (28954) | 1688 s (1379) | 127 s (154) | 235 s (169) | 99 s (1107) | 39 s (1) |
| P06-L30_s2 | max_it 2.2e-02 | max_it 6.5e-03 | 811 s (20943) | max_it 1.1e-02 | 1855 s (27767) | max_it 7.8e-03 | 889 s (25771) | 1447 s (1175) | 122 s (147) | 227 s (161) | 93 s (1019) | 40 s (1) |
| P07-1 | max_it 2.5e-02 | max_it 1.8e-02 | max_it 6.6e-02 | max_it 1.6e-02 | max_it 1.8e+02 | max_it 1.7e-02 | max_it 4.6e-01 | max_it 1.2e-03 | 922 s (902) | 248 s (173) | 122 s (1331) | 43 s (1) |
| P07-4 | max_it 4.8e-02 | max_it 3.4e-02 | max_it 7.7e-03 | max_it 2.8e-02 | max_it 1.0e-02 | max_it 2.8e-02 | max_it 4.0e-02 | max_it 1.7e-04 | 1485 s (2063) | max_it 1.3e-06 | 201 s (2646) | 44 s (1) |
| P08-N2_s1 | max_it 5.7e-05 | max_it 4.1e-07 | 78 s (6280) | max_it 1.5e-06 | 145 s (7235) | max_it 1.8e-06 | 79 s (7286) | 90 s (241) | 29 s (113) | 45 s (107) | 21 s (623) | 10 s (1) |
| P08-N4_s1 | max_it 6.2e-05 | max_it 5.9e-07 | 177 s (8277) | max_it 3.5e-06 | 379 s (10782) | max_it 2.1e-06 | 194 s (10369) | 254 s (391) | 72 s (175) | 128 s (182) | 50 s (1027) | 19 s (1) |
| P08-N8_s1 | max_it 7.4e-05 | max_it 1.1e-06 | 392 s (9824) | max_it 3.7e-06 | 817 s (12026) | max_it 2.5e-06 | 405 s (11379) | 548 s (432) | 194 s (255) | 310 s (226) | 130 s (1647) | 40 s (1) |
| case1A:standard | max_it 1.1e-03 | max_it 6.6e-04 | 153 s (16749) | max_it 4.4e-01 | max_it 8.9e-01 | max_it 8.2e-06 | 90 s (10858) | max_it 1.5e-01 | 272 s (2387) | max_it 2.1e-01 | 24 s (1028) | 10 s (1) |
| case1A:high_freq | max_it 3.7e-03 | max_it 3.1e-03 | 325 s (23811) | max_it 4.9e-01 | max_it 1.4e+00 | max_it 8.1e-05 | 171 s (13871) | max_it 2.4e-01 | 463 s (2734) | max_it 2.6e-01 | 39 s (1136) | 16 s (1) |
| case1A:thick_pml | max_it 6.0e-05 | max_it 4.5e-04 | 292 s (20624) | max_it 5.3e-01 | max_it 1.1e+01 | 537 s (9593) | 101 s (7497) | max_it 4.6e-01 | 348 s (1896) | max_it 4.1e-01 | 36 s (955) | 17 s (1) |
| case1A:thin_pml | max_it 5.6e-03 | max_it 1.4e-03 | 96 s (17258) | max_it 2.5e-03 | 189 s (20725) | max_it 2.2e-03 | 89 s (18194) | 307 s (1889) | max_it 2.1e-01 | 116 s (644) | 14 s (896) | 5.9 s (1) |
| case1B:mie_low_eps | max_it 2.8e-02 | max_it 3.4e-02 | 103 s (15592) | max_it 4.5e-01 | max_it 7.1e-01 | max_it 3.1e-03 | 61 s (10196) | max_it 5.7e-02 | 255 s (3250) | max_it 3.8e-02 | 27 s (2002) | 7.0 s (1) |
| case1B:mie_mid_eps | max_it 1.4e-01 | max_it 1.4e-01 | 261 s (34740) | max_it 4.6e-01 | max_it 6.0e+00 | max_it 8.5e-02 | 152 s (22832) | max_it 1.4e-01 | 352 s (3836) | max_it 1.0e-01 | 82 s (6231) | 8.2 s (1) |
| case1B:mie_high_eps | max_it 1.6e-01 | max_it 1.6e-01 | max_it 2.4e-07 | max_it 4.2e-01 | max_it 1.0e+01 | max_it 1.1e-01 | 258 s (34022) | max_it 2.2e-01 | max_it 3.5e-08 | max_it 2.5e-01 | 94 s (6091) | 9.8 s (1) |
| case1B:mie_ultra_high_eps | max_it 2.0e-01 | max_it 1.9e-01 | max_it 1.2e-03 | max_it 5.4e-01 | max_it 3.8e+00 | max_it 1.5e-01 | max_it 4.2e-07 | max_it 1.9e-01 | max_it 5.2e-02 | max_it 1.6e-01 | 298 s (15604) | 13 s (1) |
| case1C:narrow_aperture | max_it 3.1e-03 | max_it 1.8e-03 | 162 s (18804) | max_it 6.1e-01 | max_it 1.4e+00 | max_it 2.3e-05 | 93 s (11675) | max_it 3.5e-01 | 381 s (3664) | max_it 2.8e-01 | 24 s (1096) | 9.5 s (1) |
| case1C:medium_aperture | max_it 3.6e-03 | max_it 1.8e-03 | 163 s (18742) | max_it 5.9e-01 | max_it 3.1e+00 | max_it 3.3e-05 | 92 s (11564) | max_it 2.0e-01 | 303 s (2904) | max_it 3.7e-01 | 24 s (1096) | 9.6 s (1) |
| case1C:wide_aperture | max_it 6.6e-03 | max_it 6.2e-03 | 166 s (19350) | max_it 6.2e-01 | max_it 2.9e+00 | max_it 1.3e-04 | 89 s (11212) | max_it 1.4e-01 | 369 s (3572) | max_it 2.3e-01 | 23 s (1073) | 9.3 s (1) |
| case2A:standard | max_it 3.9e-07 | 116 s (5904) | 36 s (3194) | max_it 3.4e-05 | 239 s (14412) | 311 s (7999) | 37 s (3751) | 206 s (686) | max_it 8.6e-05 | 251 s (811) | 81 s (4687) | 8.8 s (1) |
| case2A:off_resonance | 42 s (2086) | 21 s (866) | 12 s (729) | 60 s (2123) | 25 s (1223) | 40 s (910) | 12 s (813) | 35 s (101) | 14 s (59) | 25 s (60) | 14 s (373) | 8.9 s (1) |
| case2B:narrow_iris | 61 s (4585) | 33 s (2232) | 16 s (1912) | 116 s (6229) | 90 s (7600) | 84 s (2934) | 17 s (2308) | 94 s (441) | max_it 1.4e-04 | 78 s (343) | 25 s (1920) | 5.5 s (1) |
| case2B:medium_iris | 21 s (1985) | 14 s (1115) | 8.3 s (1084) | 28 s (1866) | 29 s (2979) | 30 s (1300) | 9.0 s (1342) | 56 s (337) | max_it 3.7e-06 | 66 s (389) | 16 s (1545) | 4.0 s (1) |
| case2B:wide_iris | 51 s (5158) | 24 s (2198) | 10 s (1586) | 86 s (6195) | 55 s (6152) | 59 s (2726) | 11 s (1864) | 76 s (484) | max_it 7.4e-06 | 92 s (567) | 25 s (2636) | 4.0 s (1) |
| case2B:off_resonance | 15 s (1228) | 9.5 s (679) | 6.6 s (716) | 20 s (1289) | 17 s (1649) | 19 s (787) | 6.7 s (828) | 20 s (108) | 13 s (186) | 21 s (106) | 10 s (763) | 4.1 s (1) |
| case2C:narrow_slit | 32 s (2724) | 21 s (1625) | 12 s (1602) | 63 s (3974) | 109 s (11207) | 47 s (1944) | 12 s (1872) | 75 s (424) | max_it 1.2e-03 | 78 s (424) | 23 s (2171) | 4.5 s (1) |
| case2C:medium_slit | 34 s (3049) | 23 s (1786) | 12 s (1590) | 65 s (4158) | 54 s (5469) | 51 s (2109) | 12 s (1897) | 77 s (445) | max_it 2.4e-05 | 85 s (476) | 23 s (2284) | 4.4 s (1) |
| case2C:wide_slit | 76 s (6998) | 39 s (3236) | 13 s (1751) | 137 s (8984) | 82 s (8425) | 66 s (2783) | 13 s (2023) | 87 s (492) | max_it 1.2e-05 | 96 s (525) | 25 s (2407) | 4.4 s (1) |
| case2C:off_resonance | 20 s (1663) | 14 s (1069) | 8.4 s (965) | 29 s (1753) | 23 s (2116) | 29 s (1155) | 8.3 s (1106) | 27 s (142) | 15 s (209) | 26 s (131) | 11 s (826) | 4.5 s (1) |
| case2D:few_walls | max_it 4.4e-07 | 194 s (8619) | 38 s (3050) | max_it 3.5e-05 | 245 s (13071) | max_it 1.3e-08 | 40 s (3564) | 464 s (1370) | 661 s (6444) | max_it 4.2e-07 | 69 s (3771) | 8.1 s (1) |
| case2D:many_walls | max_it 5.9e-03 | max_it 5.2e-03 | 190 s (20876) | max_it 4.4e-03 | 304 s (19450) | max_it 4.8e-03 | 204 s (24553) | max_it 8.6e-04 | max_it 3.1e-03 | max_it 2.1e-03 | 118 s (9927) | 6.2 s (1) |
| case2D:off_resonance | 53 s (2316) | 33 s (1291) | 17 s (1080) | 69 s (2136) | 38 s (1712) | 69 s (1452) | 17 s (1217) | 52 s (137) | 36 s (214) | 33 s (74) | 15 s (373) | 8.2 s (1) |
| case2E:sparse_irises | 25 s (6225) | 15 s (3312) | 3.2 s (1033) | 16 s (2846) | 4.9 s (1167) | 35 s (3880) | 3.3 s (1216) | 7.8 s (118) | 5.7 s (239) | 8.9 s (132) | 3.2 s (626) | 1.4 s (1) |
| case2E:dense_irises | 8.1 s (1242) | 5.5 s (752) | 3.7 s (794) | 6.0 s (590) | 5.0 s (772) | 11 s (840) | 3.7 s (883) | 7.5 s (72) | 9.0 s (283) | 8.3 s (79) | 3.3 s (374) | 1.8 s (1) |
| case2F:empty | 0.7 s (810) | 0.5 s (268) | 0.4 s (354) | 0.5 s (236) | 0.5 s (331) | 0.9 s (321) | 0.4 s (413) | 0.6 s (33) | 0.6 s (69) | 0.7 s (35) | 0.4 s (128) | 0.3 s (1) |
| case2F:plex7 | 0.9 s (1035) | 0.5 s (290) | 0.5 s (394) | 0.5 s (249) | 0.5 s (343) | 1.1 s (477) | 0.5 s (443) | 0.7 s (31) | 0.6 s (75) | 0.7 s (34) | 0.4 s (115) | 0.3 s (1) |
| case2F:plex9 | 0.8 s (722) | 0.5 s (274) | 0.5 s (372) | 0.5 s (240) | 0.5 s (338) | 0.9 s (346) | 0.5 s (431) | 0.7 s (31) | 0.6 s (75) | 0.7 s (33) | 0.5 s (117) | 0.3 s (1) |
| case2F:pvc7 | 0.9 s (900) | 0.5 s (289) | 0.5 s (391) | 0.5 s (252) | 0.5 s (345) | 1.4 s (558) | 0.5 s (452) | 0.7 s (32) | 0.6 s (75) | 0.7 s (34) | 0.5 s (116) | 0.3 s (1) |
| case2F:pvc9 | 0.7 s (642) | 0.5 s (267) | 0.4 s (346) | 0.5 s (229) | 0.5 s (312) | 0.9 s (306) | 0.5 s (416) | 0.6 s (29) | 0.6 s (75) | 0.7 s (32) | 0.5 s (111) | 0.3 s (1) |
| case3A:low_contrast | 66 s (3244) | 33 s (1420) | 17 s (1072) | 44 s (1420) | 26 s (1157) | 73 s (1707) | 17 s (1271) | 40 s (110) | 14 s (35) | 21 s (42) | 13 s (267) | 9.6 s (1) |
| case3A:high_contrast | max_it 4.8e-03 | max_it 7.0e-04 | 89 s (8411) | max_it 5.4e-03 | max_it 9.2e-08 | max_it 1.2e-03 | 91 s (9653) | max_it 3.5e-05 | max_it 2.1e-02 | max_it 1.3e-03 | 214 s (12170) | 9.7 s (1) |
| case3B:few_layers | max_it 1.2e-03 | max_it 1.9e-04 | 57 s (6382) | max_it 5.0e-04 | 412 s (28924) | max_it 4.0e-04 | 60 s (7692) | max_it 9.8e-08 | max_it 6.3e-04 | max_it 9.8e-05 | 136 s (9695) | 6.9 s (1) |
| case3B:many_layers | max_it 3.7e-04 | max_it 1.2e-04 | 95 s (6966) | max_it 1.5e-04 | 181 s (7917) | max_it 1.9e-04 | 98 s (8047) | 593 s (1464) | max_it 7.5e-03 | max_it 9.8e-07 | 472 s (21606) | 11 s (1) |
| case3C:coarse_check | max_it 3.8e-02 | max_it 1.7e-03 | 80 s (8113) | max_it 2.4e-02 | 409 s (25525) | max_it 1.3e-02 | 91 s (10371) | 574 s (1999) | max_it 4.5e-07 | max_it 2.3e-07 | 182 s (11085) | 8.4 s (1) |
| case3C:medium_check | max_it 2.8e-03 | max_it 3.5e-04 | 86 s (8591) | max_it 2.7e-04 | 242 s (14990) | max_it 4.4e-04 | 100 s (11630) | 463 s (1634) | 590 s (6161) | max_it 1.2e-07 | 105 s (6208) | 8.1 s (1) |
| case3C:fine_check | max_it 1.8e-02 | max_it 6.3e-04 | 68 s (5374) | max_it 1.6e-03 | 152 s (7400) | max_it 8.7e-04 | 71 s (6288) | 259 s (727) | 643 s (4983) | 267 s (720) | 180 s (8075) | 9.9 s (1) |
| case3D:sparse_array | max_it 1.5e-06 | 51 s (8329) | 12 s (3277) | 38 s (4681) | 18 s (3219) | 71 s (5546) | 12 s (3768) | 23 s (246) | 12 s (253) | 15 s (146) | 14 s (2280) | 2.4 s (1) |
| case3D:dense_array | max_it 3.0e-04 | max_it 2.5e-05 | 93 s (7499) | max_it 5.3e-05 | 170 s (8186) | max_it 2.3e-05 | 92 s (8335) | 389 s (1080) | max_it 4.2e-04 | max_it 8.0e-07 | 443 s (22079) | 10 s (1) |
| case3E:low_loss | max_it 1.2e-05 | max_it 6.0e-08 | 52 s (5434) | max_it 9.3e-05 | max_it 1.2e-05 | max_it 3.1e-07 | 53 s (6295) | 398 s (1456) | 752 s (8471) | max_it 8.1e-07 | 109 s (6802) | 8.9 s (1) |
| case3E:medium_loss | 80 s (4713) | 52 s (2786) | 31 s (2932) | 189 s (7923) | 510 s (33820) | 116 s (3190) | 31 s (3414) | 99 s (347) | 102 s (1091) | 104 s (348) | 50 s (2851) | 9.1 s (1) |
| case3E:high_loss | 83 s (4840) | 54 s (2892) | 29 s (2756) | 190 s (7922) | 210 s (13691) | 117 s (3222) | 31 s (3379) | 65 s (224) | 76 s (677) | 62 s (202) | 46 s (2573) | 9.0 s (1) |
| case3F:low_contrast_no_loss | max_it 1.2e-02 | max_it 3.1e-05 | 28 s (2150) | max_it 2.3e-06 | 42 s (2026) | max_it 4.9e-04 | 30 s (2611) | 49 s (137) | 17 s (73) | 25 s (53) | 17 s (486) | 8.6 s (1) |
| case3F:high_contrast_with_loss | max_it 6.6e-02 | max_it 2.9e-02 | 91 s (8323) | max_it 3.2e-02 | 170 s (9308) | max_it 3.7e-02 | 93 s (9660) | 597 s (1896) | 208 s (1707) | 106 s (298) | 118 s (6171) | 8.7 s (1) |
| case3F:ultra_contrast_high_loss | max_it 4.5e-02 | max_it 1.2e-02 | 160 s (14983) | max_it 1.4e-02 | 366 s (20503) | max_it 1.5e-02 | 175 s (18674) | max_it 1.1e-08 | max_it 2.1e-05 | max_it 9.3e-06 | 334 s (18290) | 8.6 s (1) |

## 標準の結果（詳細）

| case | combination | status | it | final rel.res | true rel.res | setup [s] | solve [s] | total [s] | RSS [GB] | \|dS\| vs MUMPS |
|---|---|---|---|---|---|---|---|---|---|---|
| P01-1 | gs/gmres | max_it | 10000 | 2.2e-03 | - | 3.4 | 119 | 123 | 0.396 | 6.8e-03 |
| P01-1 | ssor/gmres | max_it | 10000 | 5.4e-04 | - | 3.4 | 126 | 130 | 0.396 | 1.6e-03 |
| P01-1 | ssor/cocg | converged | 10538 | 9.1e-09 | - | 3.5 | 67 | 71 | 0.164 | 1.7e-10 |
| P01-1 | amg_gamg/gmres | max_it | 10000 | 5.6e-04 | - | 3.6 | 169 | 173 | 0.431 | 1.4e-03 |
| P01-1 | amg_gamg/cocg | converged | 10270 | 6.9e-09 | - | 3.4 | 110 | 113 | 0.231 | 2.8e-11 |
| P01-1 | accel_ic/gmres | max_it | 10000 | 7.9e-04 | - | 3.4 | 259 | 263 | 0.75 | 2.5e-03 |
| P01-1 | accel_ic/cocg | converged | 12031 | 6.8e-09 | - | 3.4 | 65 | 69 | 0.19 | 4.1e-11 |
| P01-1 | cslp/gmres | converged | 423 | 9.8e-09 | - | 4.7 | 79 | 85 | 0.831 | 8.1e-09 |
| P01-1 | hx/gmres | converged | 61 | 6.5e-09 | - | 5.4 | 6.8 | 13 | 0.996 | 3.8e-10 |
| P01-1 | cslp_hx/gmres | converged | 49 | 6.5e-09 | - | 5.0 | 9.1 | 14 | 0.841 | 1.7e-09 |
| P01-1 | npatch_asm/cocg | converged | 319 | 6.5e-09 | - | 5.0 | 3.2 | 8.6 | 0.536 | 2.9e-11 |
| P01-1 | mumps/direct | converged | 1 | 4.2e-13 | - | 5.1 | 0.1 | 5.6 | 0.765 | - |
| P01-2 | gs/gmres | max_it | 10000 | 3.2e-06 | - | 4.1 | 145 | 149 | 0.483 | 1.1e-05 |
| P01-2 | ssor/gmres | converged | 8260 | 1.0e-08 | - | 4.1 | 127 | 132 | 0.483 | 3.5e-08 |
| P01-2 | ssor/cocg | converged | 4947 | 9.2e-09 | - | 4.1 | 39 | 43 | 0.203 | 5.9e-10 |
| P01-2 | amg_gamg/gmres | max_it | 10000 | 1.4e-08 | - | 4.5 | 207 | 212 | 0.531 | 4.5e-08 |
| P01-2 | amg_gamg/cocg | converged | 7456 | 8.4e-09 | - | 4.1 | 98 | 102 | 0.282 | 2.5e-09 |
| P01-2 | accel_ic/gmres | converged | 9447 | 1.0e-08 | - | 4.1 | 299 | 304 | 0.921 | 5.4e-08 |
| P01-2 | accel_ic/cocg | converged | 5673 | 7.6e-09 | - | 4.1 | 38 | 42 | 0.231 | 1.3e-10 |
| P01-2 | cslp/gmres | converged | 228 | 9.0e-09 | - | 5.7 | 53 | 59 | 1.03 | 1.0e-08 |
| P01-2 | hx/gmres | converged | 271 | 8.3e-09 | - | 6.7 | 29 | 36 | 1.236 | 6.7e-10 |
| P01-2 | cslp_hx/gmres | converged | 117 | 8.2e-09 | - | 6.1 | 27 | 34 | 1.042 | 2.2e-09 |
| P01-2 | npatch_asm/cocg | converged | 816 | 5.6e-09 | - | 6.0 | 10 | 16 | 0.645 | 8.4e-10 |
| P01-2 | mumps/direct | converged | 1 | 7.3e-14 | - | 6.2 | 0.1 | 6.8 | 0.906 | - |
| P01-3 | gs/gmres | max_it | 10000 | 2.4e-03 | - | 3.4 | 118 | 122 | 0.396 | 1.7e-02 |
| P01-3 | ssor/gmres | max_it | 10000 | 4.9e-04 | - | 3.4 | 126 | 130 | 0.396 | 2.0e-03 |
| P01-3 | ssor/cocg | converged | 26833 | 9.4e-09 | - | 3.4 | 170 | 173 | 0.164 | 6.8e-11 |
| P01-3 | amg_gamg/gmres | max_it | 10000 | 5.6e-04 | - | 3.7 | 169 | 173 | 0.431 | 2.7e-03 |
| P01-3 | amg_gamg/cocg | converged | 24154 | 9.8e-09 | - | 3.4 | 258 | 262 | 0.231 | 1.8e-11 |
| P01-3 | accel_ic/gmres | max_it | 10000 | 7.3e-04 | - | 3.5 | 259 | 263 | 0.749 | 4.2e-03 |
| P01-3 | accel_ic/cocg | converged | 33890 | 7.4e-09 | - | 3.4 | 186 | 190 | 0.19 | 6.3e-10 |
| P01-3 | cslp/gmres | converged | 1626 | 9.9e-09 | - | 4.7 | 308 | 313 | 0.831 | 1.4e-08 |
| P01-3 | hx/gmres | converged | 61 | 5.7e-09 | - | 5.4 | 9.2 | 15 | 0.996 | 2.5e-10 |
| P01-3 | cslp_hx/gmres | converged | 28 | 8.8e-09 | - | 5.0 | 5.3 | 11 | 0.841 | 7.4e-10 |
| P01-3 | npatch_asm/cocg | converged | 317 | 9.4e-09 | - | 5.0 | 3.2 | 8.5 | 0.535 | 1.4e-12 |
| P01-3 | mumps/direct | converged | 1 | 4.2e-12 | - | 5.0 | 0.1 | 5.5 | 0.765 | - |
| P01-1_coarse | gs/gmres | max_it | 10000 | 3.8e-04 | - | 0.9 | 29 | 30 | 0.12 | 1.0e-03 |
| P01-1_coarse | ssor/gmres | max_it | 10000 | 9.0e-06 | - | 0.9 | 31 | 32 | 0.12 | 1.8e-05 |
| P01-1_coarse | ssor/cocg | converged | 3905 | 8.1e-09 | - | 0.9 | 6.2 | 7.3 | 0.056 | 4.4e-10 |
| P01-1_coarse | amg_gamg/gmres | max_it | 10000 | 1.1e-05 | - | 1.0 | 40 | 41 | 0.125 | 3.0e-05 |
| P01-1_coarse | amg_gamg/cocg | converged | 4345 | 6.6e-09 | - | 1.0 | 11 | 12 | 0.069 | 8.6e-11 |
| P01-1_coarse | accel_ic/gmres | max_it | 10000 | 5.0e-05 | - | 1.0 | 68 | 70 | 0.212 | 1.7e-04 |
| P01-1_coarse | accel_ic/cocg | converged | 4301 | 9.8e-09 | - | 1.0 | 5.7 | 6.8 | 0.064 | 4.9e-10 |
| P01-1_coarse | cslp/gmres | converged | 181 | 9.7e-09 | - | 1.3 | 7.5 | 8.9 | 0.222 | 5.5e-10 |
| P01-1_coarse | hx/gmres | converged | 156 | 9.2e-09 | - | 1.4 | 3.6 | 5.2 | 0.267 | 3.1e-09 |
| P01-1_coarse | cslp_hx/gmres | converged | 32 | 6.0e-09 | - | 1.4 | 1.3 | 2.8 | 0.226 | 1.4e-09 |
| P01-1_coarse | npatch_asm/cocg | converged | 199 | 9.7e-09 | - | 1.3 | 0.5 | 1.9 | 0.131 | 6.1e-12 |
| P01-1_coarse | mumps/direct | converged | 1 | 2.0e-13 | - | 1.2 | 0.0 | 1.3 | 0.059 | - |
| P01-1_fine | gs/gmres | max_it | 10000 | 8.8e-03 | - | 18 | 620 | 639 | 1.985 | 7.9e-02 |
| P01-1_fine | ssor/gmres | max_it | 10000 | 2.7e-03 | - | 18 | 665 | 684 | 1.985 | 1.7e-02 |
| P01-1_fine | ssor/cocg | converged | 21950 | 7.1e-09 | - | 18 | 753 | 772 | 0.806 | 1.2e-10 |
| P01-1_fine | amg_gamg/gmres | max_it | 10000 | 4.8e-03 | - | 19 | 922 | 943 | 2.182 | 4.4e-02 |
| P01-1_fine | amg_gamg/cocg | converged | 28686 | 9.0e-09 | - | 18 | 1716 | 1735 | 1.145 | 6.3e-12 |
| P01-1_fine | accel_ic/gmres | max_it | 10000 | 3.2e-03 | - | 18 | 1344 | 1364 | 3.845 | 2.9e-02 |
| P01-1_fine | accel_ic/cocg | converged | 26475 | 7.9e-09 | - | 18 | 806 | 825 | 0.927 | 1.1e-10 |
| P01-1_fine | cslp/gmres | converged | 1175 | 9.9e-09 | - | 25 | 1273 | 1299 | 4.288 | 4.3e-08 |
| P01-1_fine | hx/gmres | converged | 39 | 4.6e-09 | - | 33 | 32 | 66 | 5.141 | 1.5e-10 |
| P01-1_fine | cslp_hx/gmres | converged | 49 | 9.5e-09 | - | 28 | 52 | 81 | 4.356 | 3.3e-09 |
| P01-1_fine | npatch_asm/cocg | converged | 572 | 7.3e-09 | - | 28 | 31 | 61 | 2.766 | 1.4e-11 |
| P01-1_fine | mumps/direct | converged | 1 | 1.1e-12 | - | 35 | 0.5 | 37 | 6.211 | - |
| P01-1_sibc | gs/gmres | max_it | 10000 | 2.2e-03 | - | 3.4 | 118 | 122 | 0.396 | 6.6e-03 |
| P01-1_sibc | ssor/gmres | max_it | 10000 | 5.4e-04 | - | 3.4 | 126 | 130 | 0.396 | 1.5e-03 |
| P01-1_sibc | ssor/cocg | converged | 9523 | 8.4e-09 | - | 3.4 | 61 | 65 | 0.164 | 3.1e-10 |
| P01-1_sibc | amg_gamg/gmres | max_it | 10000 | 5.9e-04 | - | 3.7 | 169 | 173 | 0.431 | 1.5e-03 |
| P01-1_sibc | amg_gamg/cocg | converged | 9090 | 6.4e-09 | - | 3.4 | 97 | 101 | 0.231 | 9.2e-11 |
| P01-1_sibc | accel_ic/gmres | max_it | 10000 | 7.7e-04 | - | 3.5 | 259 | 263 | 0.751 | 2.7e-03 |
| P01-1_sibc | accel_ic/cocg | converged | 11797 | 7.4e-09 | - | 3.4 | 65 | 69 | 0.19 | 9.0e-11 |
| P01-1_sibc | cslp/gmres | converged | 513 | 9.7e-09 | - | 4.7 | 97 | 102 | 0.831 | 3.8e-08 |
| P01-1_sibc | hx/gmres | converged | 29 | 5.6e-09 | - | 5.4 | 3.9 | 9.6 | 0.996 | 6.8e-10 |
| P01-1_sibc | cslp_hx/gmres | converged | 50 | 5.4e-09 | - | 5.0 | 9.3 | 15 | 0.841 | 1.9e-09 |
| P01-1_sibc | npatch_asm/cocg | converged | 318 | 7.2e-09 | - | 5.0 | 3.6 | 9.0 | 0.579 | 3.3e-11 |
| P01-1_sibc | mumps/direct | converged | 1 | 4.5e-13 | - | 5.0 | 0.1 | 5.5 | 0.765 | - |
| P01-2_sibc | gs/gmres | max_it | 10000 | 3.1e-06 | - | 4.1 | 144 | 149 | 0.483 | 1.1e-05 |
| P01-2_sibc | ssor/gmres | converged | 8235 | 1.0e-08 | - | 4.1 | 127 | 132 | 0.483 | 3.7e-08 |
| P01-2_sibc | ssor/cocg | converged | 5114 | 9.7e-09 | - | 4.1 | 40 | 45 | 0.203 | 1.4e-10 |
| P01-2_sibc | amg_gamg/gmres | max_it | 10000 | 1.7e-08 | - | 4.5 | 207 | 212 | 0.531 | 6.4e-08 |
| P01-2_sibc | amg_gamg/cocg | converged | 7124 | 9.8e-09 | - | 4.2 | 94 | 98 | 0.283 | 9.4e-10 |
| P01-2_sibc | accel_ic/gmres | converged | 9421 | 1.0e-08 | - | 4.1 | 298 | 303 | 0.921 | 5.4e-08 |
| P01-2_sibc | accel_ic/cocg | converged | 5560 | 8.2e-09 | - | 4.1 | 38 | 42 | 0.231 | 7.1e-10 |
| P01-2_sibc | cslp/gmres | converged | 227 | 9.3e-09 | - | 5.6 | 53 | 59 | 1.03 | 8.6e-09 |
| P01-2_sibc | hx/gmres | converged | 597 | 8.3e-09 | - | 6.6 | 63 | 70 | 1.236 | 1.4e-09 |
| P01-2_sibc | cslp_hx/gmres | converged | 118 | 7.7e-09 | - | 6.0 | 27 | 34 | 1.042 | 2.5e-09 |
| P01-2_sibc | npatch_asm/cocg | converged | 855 | 9.1e-09 | - | 6.1 | 11 | 18 | 0.733 | 4.1e-10 |
| P01-2_sibc | mumps/direct | converged | 1 | 9.1e-14 | - | 6.2 | 0.1 | 6.7 | 0.951 | - |
| P01-a_f0.5 | gs/gmres | max_it | 10000 | 3.3e-03 | - | 3.4 | 118 | 122 | 0.396 | 1.6e-02 |
| P01-a_f0.5 | ssor/gmres | max_it | 10000 | 1.0e-03 | - | 3.4 | 126 | 130 | 0.396 | 2.9e-03 |
| P01-a_f0.5 | ssor/cocg | converged | 13267 | 9.7e-09 | - | 3.5 | 85 | 89 | 0.164 | 5.3e-09 |
| P01-a_f0.5 | amg_gamg/gmres | max_it | 10000 | 1.0e-03 | - | 3.7 | 169 | 173 | 0.431 | 2.7e-03 |
| P01-a_f0.5 | amg_gamg/cocg | converged | 13959 | 9.8e-09 | - | 3.4 | 149 | 153 | 0.231 | 3.1e-11 |
| P01-a_f0.5 | accel_ic/gmres | max_it | 10000 | 1.3e-03 | - | 3.4 | 259 | 263 | 0.749 | 4.8e-03 |
| P01-a_f0.5 | accel_ic/cocg | converged | 16262 | 8.2e-09 | - | 3.4 | 90 | 94 | 0.19 | 3.1e-10 |
| P01-a_f0.5 | cslp/gmres | converged | 592 | 9.8e-09 | - | 4.7 | 113 | 118 | 0.831 | 7.6e-09 |
| P01-a_f0.5 | hx/gmres | converged | 60 | 6.6e-09 | - | 5.4 | 7.8 | 14 | 0.996 | 2.9e-10 |
| P01-a_f0.5 | cslp_hx/gmres | converged | 29 | 5.4e-09 | - | 4.9 | 5.5 | 11 | 0.841 | 9.4e-10 |
| P01-a_f0.5 | npatch_asm/cocg | converged | 306 | 9.8e-09 | - | 4.9 | 3.0 | 8.3 | 0.536 | 7.2e-11 |
| P01-a_f0.5 | mumps/direct | converged | 1 | 8.5e-13 | - | 5.0 | 0.1 | 5.5 | 0.765 | - |
| P01-a_f2 | gs/gmres | max_it | 10000 | 1.5e-03 | - | 3.4 | 118 | 122 | 0.396 | 2.3e-03 |
| P01-a_f2 | ssor/gmres | max_it | 10000 | 1.7e-04 | - | 3.4 | 126 | 130 | 0.396 | 3.5e-04 |
| P01-a_f2 | ssor/cocg | converged | 7342 | 9.0e-09 | - | 3.4 | 47 | 51 | 0.164 | 2.6e-09 |
| P01-a_f2 | amg_gamg/gmres | max_it | 10000 | 2.0e-04 | - | 3.7 | 169 | 173 | 0.431 | 5.0e-04 |
| P01-a_f2 | amg_gamg/cocg | converged | 7997 | 5.7e-09 | - | 3.4 | 85 | 89 | 0.231 | 2.2e-10 |
| P01-a_f2 | accel_ic/gmres | max_it | 10000 | 3.5e-04 | - | 3.4 | 259 | 263 | 0.749 | 1.0e-03 |
| P01-a_f2 | accel_ic/cocg | converged | 10067 | 5.6e-09 | - | 3.5 | 55 | 59 | 0.19 | 1.8e-10 |
| P01-a_f2 | cslp/gmres | converged | 240 | 9.5e-09 | - | 4.7 | 45 | 50 | 0.831 | 1.5e-09 |
| P01-a_f2 | hx/gmres | converged | 64 | 6.0e-09 | - | 5.5 | 6.2 | 12 | 0.996 | 2.6e-10 |
| P01-a_f2 | cslp_hx/gmres | converged | 51 | 7.0e-09 | - | 5.0 | 9.4 | 15 | 0.841 | 4.3e-09 |
| P01-a_f2 | npatch_asm/cocg | converged | 331 | 5.4e-09 | - | 5.0 | 3.3 | 8.6 | 0.536 | 1.7e-11 |
| P01-a_f2 | mumps/direct | converged | 1 | 2.1e-13 | - | 5.0 | 0.1 | 5.5 | 0.765 | - |
| P01-a_f5 | gs/gmres | max_it | 10000 | 1.5e-04 | - | 3.4 | 119 | 123 | 0.399 | 5.9e-04 |
| P01-a_f5 | ssor/gmres | max_it | 10000 | 8.8e-07 | - | 3.5 | 128 | 131 | 0.399 | 3.5e-06 |
| P01-a_f5 | ssor/cocg | converged | 5681 | 7.4e-09 | - | 3.4 | 37 | 41 | 0.167 | 1.9e-09 |
| P01-a_f5 | amg_gamg/gmres | max_it | 10000 | 2.7e-06 | - | 3.7 | 171 | 175 | 0.439 | 1.2e-05 |
| P01-a_f5 | amg_gamg/cocg | converged | 6794 | 9.1e-09 | - | 3.5 | 74 | 78 | 0.237 | 6.1e-10 |
| P01-a_f5 | accel_ic/gmres | max_it | 10000 | 5.1e-06 | - | 3.5 | 264 | 268 | 0.77 | 2.7e-05 |
| P01-a_f5 | accel_ic/cocg | converged | 7034 | 7.4e-09 | - | 3.5 | 40 | 44 | 0.191 | 3.0e-09 |
| P01-a_f5 | cslp/gmres | converged | 208 | 9.4e-09 | - | 4.8 | 39 | 45 | 0.857 | 5.3e-09 |
| P01-a_f5 | hx/gmres | converged | 85 | 9.2e-09 | - | 5.6 | 7.1 | 13 | 1.038 | 4.9e-10 |
| P01-a_f5 | cslp_hx/gmres | converged | 71 | 9.6e-09 | - | 5.1 | 13 | 19 | 0.87 | 5.1e-09 |
| P01-a_f5 | npatch_asm/cocg | converged | 408 | 8.9e-09 | - | 5.0 | 4.4 | 9.8 | 0.537 | 4.2e-11 |
| P01-a_f5 | mumps/direct | converged | 1 | 8.3e-14 | - | 5.1 | 0.1 | 5.6 | 0.785 | - |
| P01-a_f20 | gs/gmres | converged | 6728 | 1.0e-08 | - | 10 | 241 | 252 | 1.155 | 1.2e-08 |
| P01-a_f20 | ssor/gmres | converged | 3721 | 1.0e-08 | - | 10 | 142 | 153 | 1.155 | 1.5e-08 |
| P01-a_f20 | ssor/cocg | converged | 3740 | 1.0e-08 | - | 10.0 | 73 | 83 | 0.466 | 1.2e-09 |
| P01-a_f20 | amg_gamg/gmres | converged | 9716 | 1.0e-08 | - | 11 | 507 | 518 | 1.262 | 9.3e-09 |
| P01-a_f20 | amg_gamg/cocg | converged | 19259 | 7.6e-09 | - | 10 | 641 | 652 | 0.662 | 3.6e-09 |
| P01-a_f20 | accel_ic/gmres | converged | 4261 | 1.0e-08 | - | 10 | 330 | 341 | 2.24 | 2.0e-08 |
| P01-a_f20 | accel_ic/cocg | converged | 4508 | 7.1e-09 | - | 10 | 75 | 86 | 0.537 | 8.5e-10 |
| P01-a_f20 | cslp/gmres | converged | 329 | 9.5e-09 | - | 14 | 199 | 214 | 2.478 | 2.3e-08 |
| P01-a_f20 | hx/gmres | max_it | 10000 | 1.5e-05 | - | 17 | 2777 | 2795 | 3.047 | 3.7e-07 |
| P01-a_f20 | cslp_hx/gmres | converged | 289 | 9.6e-09 | - | 15 | 180 | 196 | 2.524 | 2.7e-08 |
| P01-a_f20 | npatch_asm/cocg | converged | 2561 | 1.0e-08 | - | 15 | 81 | 97 | 1.588 | 2.2e-09 |
| P01-a_f20 | mumps/direct | converged | 1 | 9.5e-14 | - | 17 | 0.2 | 18 | 2.817 | - |
| P01-b_L16.4 | gs/gmres | converged | 9944 | 1.0e-08 | - | 2.1 | 72 | 75 | 0.251 | 3.1e-09 |
| P01-b_L16.4 | ssor/gmres | converged | 5197 | 1.0e-08 | - | 2.2 | 40 | 42 | 0.251 | 1.7e-08 |
| P01-b_L16.4 | ssor/cocg | converged | 3380 | 8.4e-09 | - | 2.1 | 13 | 15 | 0.106 | 8.5e-10 |
| P01-b_L16.4 | amg_gamg/gmres | converged | 5726 | 1.0e-08 | - | 2.3 | 59 | 61 | 0.273 | 1.2e-08 |
| P01-b_L16.4 | amg_gamg/cocg | converged | 4681 | 6.9e-09 | - | 2.1 | 30 | 33 | 0.145 | 4.6e-10 |
| P01-b_L16.4 | accel_ic/gmres | converged | 6008 | 1.0e-08 | - | 2.1 | 97 | 100 | 0.468 | 9.8e-09 |
| P01-b_L16.4 | accel_ic/cocg | converged | 3942 | 7.6e-09 | - | 2.1 | 13 | 16 | 0.12 | 4.6e-10 |
| P01-b_L16.4 | cslp/gmres | converged | 153 | 9.9e-09 | - | 2.9 | 17 | 20 | 0.518 | 7.4e-09 |
| P01-b_L16.4 | hx/gmres | converged | 154 | 8.5e-09 | - | 3.3 | 7.4 | 11 | 0.623 | 4.3e-10 |
| P01-b_L16.4 | cslp_hx/gmres | converged | 67 | 9.3e-09 | - | 3.1 | 7.4 | 11 | 0.528 | 3.6e-09 |
| P01-b_L16.4 | npatch_asm/cocg | converged | 412 | 8.7e-09 | - | 3.0 | 2.7 | 5.9 | 0.334 | 8.7e-10 |
| P01-b_L16.4 | mumps/direct | converged | 1 | 5.9e-14 | - | 3.0 | 0.0 | 3.2 | 0.437 | - |
| P01-b_L32.9 | gs/gmres | max_it | 10000 | 1.0e-06 | - | 3.5 | 124 | 127 | 0.417 | 2.9e-06 |
| P01-b_L32.9 | ssor/gmres | converged | 7875 | 1.0e-08 | - | 3.5 | 104 | 108 | 0.417 | 2.8e-08 |
| P01-b_L32.9 | ssor/cocg | converged | 4402 | 7.3e-09 | - | 3.6 | 30 | 34 | 0.175 | 1.5e-09 |
| P01-b_L32.9 | amg_gamg/gmres | converged | 8924 | 1.0e-08 | - | 3.8 | 158 | 162 | 0.455 | 3.5e-08 |
| P01-b_L32.9 | amg_gamg/cocg | converged | 7034 | 6.8e-09 | - | 3.6 | 79 | 83 | 0.246 | 9.6e-10 |
| P01-b_L32.9 | accel_ic/gmres | converged | 9202 | 1.0e-08 | - | 3.6 | 251 | 254 | 0.796 | 3.1e-08 |
| P01-b_L32.9 | accel_ic/cocg | converged | 5524 | 8.2e-09 | - | 3.6 | 32 | 36 | 0.2 | 1.3e-09 |
| P01-b_L32.9 | cslp/gmres | converged | 212 | 9.6e-09 | - | 4.9 | 41 | 47 | 0.895 | 9.8e-09 |
| P01-b_L32.9 | hx/gmres | converged | 239 | 8.5e-09 | - | 5.7 | 21 | 27 | 1.063 | 5.7e-10 |
| P01-b_L32.9 | cslp_hx/gmres | converged | 105 | 8.4e-09 | - | 5.3 | 21 | 26 | 0.905 | 3.6e-09 |
| P01-b_L32.9 | npatch_asm/cocg | converged | 703 | 8.7e-09 | - | 5.2 | 7.3 | 13 | 0.56 | 6.2e-10 |
| P01-b_L32.9 | mumps/direct | converged | 1 | 1.3e-13 | - | 5.2 | 0.1 | 5.7 | 0.768 | - |
| P01-b_L65.7 | gs/gmres | max_it | 10000 | 5.4e-05 | - | 6.3 | 225 | 232 | 0.735 | 2.6e-04 |
| P01-b_L65.7 | ssor/gmres | max_it | 10000 | 3.7e-08 | - | 6.4 | 241 | 248 | 0.736 | 1.9e-07 |
| P01-b_L65.7 | ssor/cocg | converged | 6362 | 7.1e-09 | - | 6.5 | 78 | 85 | 0.307 | 9.4e-10 |
| P01-b_L65.7 | amg_gamg/gmres | max_it | 10000 | 1.8e-06 | - | 6.9 | 324 | 331 | 0.811 | 9.3e-06 |
| P01-b_L65.7 | amg_gamg/cocg | converged | 10908 | 9.6e-09 | - | 6.3 | 225 | 232 | 0.429 | 2.1e-10 |
| P01-b_L65.7 | accel_ic/gmres | max_it | 10000 | 2.2e-07 | - | 6.4 | 489 | 496 | 1.427 | 1.7e-06 |
| P01-b_L65.7 | accel_ic/cocg | converged | 7693 | 4.0e-09 | - | 6.4 | 82 | 89 | 0.351 | 3.0e-10 |
| P01-b_L65.7 | cslp/gmres | converged | 332 | 1.0e-08 | - | 8.9 | 122 | 132 | 1.583 | 4.0e-08 |
| P01-b_L65.7 | hx/gmres | converged | 1444 | 1.0e-08 | - | 10 | 236 | 247 | 1.899 | 3.8e-09 |
| P01-b_L65.7 | cslp_hx/gmres | converged | 169 | 1.0e-08 | - | 9.4 | 62 | 73 | 1.606 | 3.9e-09 |
| P01-b_L65.7 | npatch_asm/cocg | converged | 1275 | 8.4e-09 | - | 9.4 | 24 | 34 | 0.986 | 2.3e-10 |
| P01-b_L65.7 | mumps/direct | converged | 1 | 2.0e-13 | - | 9.7 | 0.1 | 11 | 1.571 | - |
| P01-b_L131.4 | gs/gmres | max_it | 10000 | 8.6e-04 | - | 12 | 429 | 442 | 1.377 | 4.6e-03 |
| P01-b_L131.4 | ssor/gmres | max_it | 10000 | 8.2e-06 | - | 12 | 459 | 472 | 1.378 | 7.4e-05 |
| P01-b_L131.4 | ssor/cocg | converged | 10032 | 9.1e-09 | - | 12 | 234 | 247 | 0.56 | 1.6e-09 |
| P01-b_L131.4 | amg_gamg/gmres | max_it | 10000 | 4.4e-04 | - | 13 | 628 | 643 | 1.511 | 2.2e-03 |
| P01-b_L131.4 | amg_gamg/cocg | converged | 19090 | 9.7e-09 | - | 12 | 765 | 778 | 0.796 | 4.1e-09 |
| P01-b_L131.4 | accel_ic/gmres | max_it | 10000 | 3.1e-05 | - | 12 | 927 | 940 | 2.667 | 2.1e-04 |
| P01-b_L131.4 | accel_ic/cocg | converged | 12038 | 5.4e-09 | - | 12 | 243 | 257 | 0.642 | 1.1e-09 |
| P01-b_L131.4 | cslp/gmres | converged | 700 | 9.9e-09 | - | 17 | 507 | 525 | 2.972 | 6.7e-08 |
| P01-b_L131.4 | hx/gmres | converged | 2696 | 1.0e-08 | - | 20 | 871 | 893 | 3.622 | 8.7e-10 |
| P01-b_L131.4 | cslp_hx/gmres | converged | 305 | 9.8e-09 | - | 18 | 229 | 248 | 3.029 | 3.9e-09 |
| P01-b_L131.4 | npatch_asm/cocg | converged | 2457 | 4.5e-09 | - | 18 | 89 | 109 | 1.905 | 1.0e-09 |
| P01-b_L131.4 | mumps/direct | converged | 1 | 1.7e-13 | - | 19 | 0.2 | 21 | 2.753 | - |
| P01-1_td0 | gs/gmres | max_it | 10000 | 2.2e-03 | - | 3.4 | 118 | 122 | 0.396 | 6.8e-03 |
| P01-1_td0 | ssor/gmres | max_it | 10000 | 5.4e-04 | - | 3.4 | 126 | 130 | 0.396 | 1.5e-03 |
| P01-1_td0 | ssor/cocg | converged | 10054 | 7.1e-09 | - | 3.4 | 64 | 68 | 0.164 | 2.9e-10 |
| P01-1_td0 | amg_gamg/gmres | max_it | 10000 | 5.7e-04 | - | 3.6 | 169 | 173 | 0.431 | 1.4e-03 |
| P01-1_td0 | amg_gamg/cocg | converged | 10205 | 5.2e-09 | - | 3.4 | 109 | 113 | 0.231 | 1.0e-11 |
| P01-1_td0 | accel_ic/gmres | max_it | 10000 | 7.9e-04 | - | 3.4 | 259 | 263 | 0.752 | 2.6e-03 |
| P01-1_td0 | accel_ic/cocg | converged | 12274 | 8.3e-09 | - | 3.4 | 67 | 70 | 0.19 | 4.9e-11 |
| P01-1_td0 | cslp/gmres | converged | 422 | 9.7e-09 | - | 4.7 | 79 | 84 | 0.831 | 9.7e-09 |
| P01-1_td0 | hx/gmres | converged | 61 | 6.6e-09 | - | 5.4 | 6.8 | 13 | 0.996 | 3.8e-10 |
| P01-1_td0 | cslp_hx/gmres | converged | 49 | 6.5e-09 | - | 5.1 | 9.1 | 15 | 0.841 | 1.7e-09 |
| P01-1_td0 | npatch_asm/cocg | converged | 319 | 6.7e-09 | - | 4.9 | 3.2 | 8.4 | 0.536 | 3.0e-11 |
| P01-1_td0 | mumps/direct | converged | 1 | 3.9e-13 | - | 5.1 | 0.1 | 5.6 | 0.765 | - |
| P01-1_td0.02 | gs/gmres | max_it | 10000 | 2.0e-03 | - | 3.4 | 118 | 122 | 0.396 | 6.7e-03 |
| P01-1_td0.02 | ssor/gmres | max_it | 10000 | 5.2e-04 | - | 3.4 | 126 | 130 | 0.396 | 1.6e-03 |
| P01-1_td0.02 | ssor/cocg | converged | 10206 | 4.2e-09 | - | 3.4 | 65 | 69 | 0.164 | 1.1e-10 |
| P01-1_td0.02 | amg_gamg/gmres | max_it | 10000 | 5.5e-04 | - | 3.7 | 169 | 173 | 0.431 | 1.4e-03 |
| P01-1_td0.02 | amg_gamg/cocg | converged | 9731 | 7.1e-09 | - | 3.4 | 104 | 108 | 0.231 | 2.1e-11 |
| P01-1_td0.02 | accel_ic/gmres | max_it | 10000 | 7.6e-04 | - | 3.4 | 259 | 263 | 0.749 | 2.3e-03 |
| P01-1_td0.02 | accel_ic/cocg | converged | 11471 | 9.8e-09 | - | 3.4 | 62 | 66 | 0.19 | 1.5e-10 |
| P01-1_td0.02 | cslp/gmres | converged | 429 | 9.6e-09 | - | 4.7 | 81 | 86 | 0.831 | 2.2e-08 |
| P01-1_td0.02 | hx/gmres | converged | 61 | 6.5e-09 | - | 5.4 | 6.8 | 13 | 0.996 | 3.7e-10 |
| P01-1_td0.02 | cslp_hx/gmres | converged | 49 | 6.5e-09 | - | 5.0 | 9.1 | 14 | 0.841 | 1.7e-09 |
| P01-1_td0.02 | npatch_asm/cocg | converged | 319 | 6.9e-09 | - | 4.9 | 3.2 | 8.5 | 0.536 | 2.9e-11 |
| P01-1_td0.02 | mumps/direct | converged | 1 | 4.1e-13 | - | 5.0 | 0.1 | 5.5 | 0.765 | - |
| P01-2_td0 | gs/gmres | max_it | 10000 | 3.5e-06 | - | 4.1 | 144 | 149 | 0.483 | 1.2e-05 |
| P01-2_td0 | ssor/gmres | converged | 8304 | 1.0e-08 | - | 4.1 | 128 | 133 | 0.483 | 3.9e-08 |
| P01-2_td0 | ssor/cocg | converged | 5009 | 1.0e-08 | - | 4.1 | 39 | 44 | 0.203 | 6.6e-10 |
| P01-2_td0 | amg_gamg/gmres | max_it | 10000 | 1.5e-08 | - | 4.5 | 207 | 212 | 0.531 | 4.8e-08 |
| P01-2_td0 | amg_gamg/cocg | converged | 7447 | 8.7e-09 | - | 4.1 | 98 | 102 | 0.282 | 9.3e-10 |
| P01-2_td0 | accel_ic/gmres | converged | 9530 | 1.0e-08 | - | 4.2 | 302 | 307 | 0.925 | 4.9e-08 |
| P01-2_td0 | accel_ic/cocg | converged | 5758 | 8.2e-09 | - | 4.2 | 39 | 43 | 0.231 | 2.3e-10 |
| P01-2_td0 | cslp/gmres | converged | 228 | 9.5e-09 | - | 5.7 | 53 | 59 | 1.03 | 1.1e-08 |
| P01-2_td0 | hx/gmres | converged | 271 | 8.5e-09 | - | 6.7 | 29 | 36 | 1.236 | 6.9e-10 |
| P01-2_td0 | cslp_hx/gmres | converged | 117 | 8.3e-09 | - | 6.1 | 27 | 34 | 1.042 | 2.4e-09 |
| P01-2_td0 | npatch_asm/cocg | converged | 843 | 7.7e-09 | - | 6.1 | 11 | 17 | 0.645 | 2.2e-09 |
| P01-2_td0 | mumps/direct | converged | 1 | 9.8e-14 | - | 6.2 | 0.1 | 6.8 | 0.907 | - |
| P01-2_td0.02 | gs/gmres | max_it | 10000 | 1.8e-06 | - | 4.1 | 144 | 149 | 0.483 | 6.2e-06 |
| P01-2_td0.02 | ssor/gmres | converged | 7912 | 1.0e-08 | - | 4.1 | 122 | 127 | 0.483 | 3.7e-08 |
| P01-2_td0.02 | ssor/cocg | converged | 4934 | 9.3e-09 | - | 4.1 | 38 | 43 | 0.203 | 3.7e-10 |
| P01-2_td0.02 | amg_gamg/gmres | converged | 9986 | 1.0e-08 | - | 4.5 | 207 | 212 | 0.531 | 3.8e-08 |
| P01-2_td0.02 | amg_gamg/cocg | converged | 7065 | 1.0e-08 | - | 4.2 | 93 | 98 | 0.282 | 1.7e-09 |
| P01-2_td0.02 | accel_ic/gmres | converged | 9132 | 1.0e-08 | - | 4.2 | 289 | 294 | 0.921 | 3.8e-08 |
| P01-2_td0.02 | accel_ic/cocg | converged | 5621 | 9.7e-09 | - | 4.1 | 38 | 43 | 0.231 | 1.2e-09 |
| P01-2_td0.02 | cslp/gmres | converged | 225 | 9.7e-09 | - | 5.8 | 52 | 58 | 1.03 | 8.5e-09 |
| P01-2_td0.02 | hx/gmres | converged | 270 | 9.2e-09 | - | 6.7 | 28 | 36 | 1.236 | 6.4e-10 |
| P01-2_td0.02 | cslp_hx/gmres | converged | 116 | 9.7e-09 | - | 6.1 | 27 | 33 | 1.042 | 3.3e-09 |
| P01-2_td0.02 | npatch_asm/cocg | converged | 778 | 5.4e-09 | - | 6.0 | 9.4 | 16 | 0.645 | 1.6e-09 |
| P01-2_td0.02 | mumps/direct | converged | 1 | 5.7e-14 | - | 6.1 | 0.1 | 6.7 | 0.949 | - |
| P01-2_N20 | gs/gmres | converged | 7833 | 1.0e-08 | - | 10.0 | 282 | 293 | 1.155 | 3.8e-08 |
| P01-2_N20 | ssor/gmres | converged | 4351 | 1.0e-08 | - | 10 | 166 | 177 | 1.155 | 5.5e-08 |
| P01-2_N20 | ssor/cocg | converged | 3055 | 8.5e-09 | - | 10 | 59 | 70 | 0.465 | 1.8e-09 |
| P01-2_N20 | amg_gamg/gmres | converged | 6804 | 1.0e-08 | - | 11 | 354 | 366 | 1.262 | 6.1e-08 |
| P01-2_N20 | amg_gamg/cocg | converged | 4936 | 7.2e-09 | - | 10 | 165 | 176 | 0.662 | 1.0e-09 |
| P01-2_N20 | accel_ic/gmres | converged | 4981 | 1.0e-08 | - | 10 | 386 | 397 | 2.24 | 7.3e-08 |
| P01-2_N20 | accel_ic/cocg | converged | 3713 | 9.2e-09 | - | 10 | 62 | 73 | 0.537 | 2.8e-10 |
| P01-2_N20 | cslp/gmres | converged | 156 | 9.8e-09 | - | 14 | 91 | 106 | 2.478 | 1.5e-08 |
| P01-2_N20 | hx/gmres | converged | 622 | 9.8e-09 | - | 17 | 158 | 176 | 3.047 | 1.4e-09 |
| P01-2_N20 | cslp_hx/gmres | converged | 94 | 9.3e-09 | - | 15 | 56 | 72 | 2.523 | 7.4e-09 |
| P01-2_N20 | npatch_asm/cocg | converged | 836 | 6.0e-09 | - | 15 | 26 | 42 | 1.589 | 5.9e-10 |
| P01-2_N20 | mumps/direct | converged | 1 | 5.8e-14 | - | 17 | 0.2 | 18 | 2.817 | - |
| P01-1_t | gs/gmres | max_it | 10000 | 2.0e-02 | - | 17 | 600 | 620 | 1.922 | 2.4e-01 |
| P01-1_t | ssor/gmres | max_it | 10000 | 1.3e-02 | - | 17 | 642 | 661 | 1.922 | 1.4e-01 |
| P01-1_t | ssor/cocg | max_it | 50000 | 3.7e-02 | - | 17 | 1632 | 1652 | 0.783 | 3.2e-05 |
| P01-1_t | amg_gamg/gmres | max_it | 10000 | 1.2e-02 | - | 18 | 891 | 912 | 2.092 | 1.5e-01 |
| P01-1_t | amg_gamg/cocg | max_it | 50000 | 4.1e-02 | - | 17 | 2845 | 2864 | 1.102 | 2.2e-05 |
| P01-1_t | accel_ic/gmres | max_it | 10000 | 1.3e-02 | - | 17 | 1299 | 1318 | 3.734 | 1.8e-01 |
| P01-1_t | accel_ic/cocg | max_it | 50000 | 2.7e-01 | - | 17 | 1424 | 1443 | 0.897 | 1.5e-05 |
| P01-1_t | cslp/gmres | max_it | 3000 | 3.7e-05 | - | 24 | 3133 | 3159 | 4.12 | 7.4e-05 |
| P01-1_t | hx/gmres | converged | 44 | 9.0e-09 | - | 29 | 31 | 63 | 5.051 | 2.3e-10 |
| P01-1_t | cslp_hx/gmres | converged | 104 | 9.7e-09 | - | 25 | 107 | 135 | 4.18 | 1.7e-09 |
| P01-1_t | npatch_asm/cocg | converged | 434 | 9.9e-09 | - | 25 | 22 | 49 | 2.6 | 5.1e-12 |
| P01-1_t | mumps/direct | converged | 1 | 3.2e-12 | - | 27 | 0.3 | 30 | 3.844 | - |
| P01-2_t | gs/gmres | max_it | 10000 | 3.3e-02 | - | 18 | 627 | 647 | 2.006 | 2.1e-01 |
| P01-2_t | ssor/gmres | max_it | 10000 | 1.8e-02 | - | 18 | 672 | 692 | 2.006 | 5.9e-02 |
| P01-2_t | ssor/cocg | max_it | 50000 | 5.0e-04 | - | 18 | 1704 | 1724 | 0.822 | 8.6e-07 |
| P01-2_t | amg_gamg/gmres | max_it | 10000 | 1.9e-02 | - | 19 | 934 | 956 | 2.189 | 1.1e-01 |
| P01-2_t | amg_gamg/cocg | max_it | 50000 | 1.4e-03 | - | 17 | 2984 | 3004 | 1.155 | 5.8e-05 |
| P01-2_t | accel_ic/gmres | max_it | 10000 | 1.6e-02 | - | 18 | 1357 | 1378 | 3.896 | 1.1e-01 |
| P01-2_t | accel_ic/cocg | max_it | 50000 | 1.1e-03 | - | 18 | 1489 | 1509 | 0.94 | 5.5e-07 |
| P01-2_t | cslp/gmres | max_it | 3000 | 3.7e-05 | - | 25 | 3296 | 3324 | 4.301 | 1.5e-04 |
| P01-2_t | hx/gmres | converged | 267 | 7.8e-09 | - | 30 | 139 | 172 | 5.164 | 3.8e-10 |
| P01-2_t | cslp_hx/gmres | converged | 219 | 9.5e-09 | - | 27 | 243 | 272 | 4.353 | 2.3e-09 |
| P01-2_t | npatch_asm/cocg | converged | 1171 | 7.3e-09 | - | 26 | 61 | 90 | 2.716 | 1.9e-10 |
| P01-2_t | mumps/direct | converged | 1 | 3.0e-13 | - | 28 | 0.4 | 31 | 3.901 | - |
| P02-a_h0.2 | gs/gmres | max_it | 10000 | 1.6e-03 | - | 2.9 | 100 | 103 | 0.345 | 3.1e-03 |
| P02-a_h0.2 | ssor/gmres | max_it | 10000 | 4.7e-06 | - | 2.9 | 107 | 110 | 0.345 | 7.8e-06 |
| P02-a_h0.2 | ssor/cocg | converged | 4719 | 9.3e-09 | - | 2.9 | 26 | 29 | 0.144 | 9.7e-11 |
| P02-a_h0.2 | amg_gamg/gmres | max_it | 10000 | 3.2e-04 | - | 3.1 | 141 | 145 | 0.374 | 5.5e-04 |
| P02-a_h0.2 | amg_gamg/cocg | converged | 9070 | 8.6e-09 | - | 3.0 | 81 | 84 | 0.2 | 6.8e-11 |
| P02-a_h0.2 | accel_ic/gmres | max_it | 10000 | 3.5e-05 | - | 3.0 | 223 | 227 | 0.652 | 8.1e-05 |
| P02-a_h0.2 | accel_ic/cocg | converged | 5540 | 8.9e-09 | - | 3.0 | 26 | 29 | 0.166 | 7.3e-11 |
| P02-a_h0.2 | cslp/gmres | converged | 245 | 9.8e-09 | - | 4.1 | 38 | 42 | 0.72 | 1.1e-09 |
| P02-a_h0.2 | hx/gmres | converged | 265 | 9.9e-09 | - | 4.6 | 20 | 25 | 0.864 | 1.3e-10 |
| P02-a_h0.2 | cslp_hx/gmres | converged | 102 | 8.3e-09 | - | 4.3 | 16 | 20 | 0.733 | 4.0e-10 |
| P02-a_h0.2 | npatch_asm/cocg | converged | 630 | 8.7e-09 | - | 4.2 | 5.8 | 10 | 0.462 | 1.6e-10 |
| P02-a_h0.2 | mumps/direct | converged | 1 | 6.3e-14 | - | 4.1 | 0.1 | 4.5 | 0.573 | - |
| P02-a_h0.05 | gs/gmres | max_it | 10000 | 1.9e-02 | - | 2.9 | 99 | 102 | 0.341 | 1.3e-02 |
| P02-a_h0.05 | ssor/gmres | max_it | 10000 | 1.2e-03 | - | 2.9 | 106 | 109 | 0.341 | 7.0e-04 |
| P02-a_h0.05 | ssor/cocg | converged | 10374 | 9.3e-09 | - | 2.9 | 56 | 59 | 0.143 | 2.0e-11 |
| P02-a_h0.05 | amg_gamg/gmres | max_it | 10000 | 6.6e-03 | - | 3.1 | 140 | 143 | 0.371 | 5.0e-03 |
| P02-a_h0.05 | amg_gamg/cocg | converged | 17437 | 1.0e-08 | - | 2.9 | 153 | 157 | 0.199 | 8.7e-11 |
| P02-a_h0.05 | accel_ic/gmres | max_it | 10000 | 2.4e-03 | - | 2.9 | 221 | 224 | 0.651 | 1.9e-03 |
| P02-a_h0.05 | accel_ic/cocg | converged | 11337 | 9.2e-09 | - | 2.9 | 52 | 56 | 0.164 | 1.3e-11 |
| P02-a_h0.05 | cslp/gmres | converged | 669 | 9.9e-09 | - | 4.0 | 103 | 107 | 0.72 | 4.2e-09 |
| P02-a_h0.05 | hx/gmres | converged | 272 | 9.4e-09 | - | 4.6 | 20 | 25 | 0.878 | 7.9e-11 |
| P02-a_h0.05 | cslp_hx/gmres | converged | 122 | 9.9e-09 | - | 4.3 | 19 | 23 | 0.734 | 1.2e-10 |
| P02-a_h0.05 | npatch_asm/cocg | converged | 579 | 7.0e-09 | - | 4.2 | 5.3 | 9.8 | 0.457 | 3.4e-11 |
| P02-a_h0.05 | mumps/direct | converged | 1 | 2.6e-13 | - | 4.1 | 0.1 | 4.5 | 0.652 | - |
| P02-b_h0.2 | gs/gmres | max_it | 10000 | 6.4e-02 | - | 19 | 668 | 688 | 2.161 | 9.8e-01 |
| P02-b_h0.2 | ssor/gmres | max_it | 10000 | 5.3e-02 | - | 19 | 714 | 735 | 2.161 | 9.9e-01 |
| P02-b_h0.2 | ssor/cocg | max_it | 50000 | 1.8e-02 | - | 19 | 1843 | 1865 | 0.877 | 1.4e-04 |
| P02-b_h0.2 | amg_gamg/gmres | max_it | 10000 | 5.3e-02 | - | 21 | 976 | 999 | 2.38 | 9.8e-01 |
| P02-b_h0.2 | amg_gamg/cocg | max_it | 50000 | 6.2e-01 | - | 19 | 3150 | 3171 | 1.25 | 3.1e-02 |
| P02-b_h0.2 | accel_ic/gmres | max_it | 10000 | 4.6e-02 | - | 20 | 1456 | 1478 | 4.191 | 9.8e-01 |
| P02-b_h0.2 | accel_ic/cocg | max_it | 50000 | 4.2e-01 | - | 19 | 1589 | 1610 | 1.008 | 5.4e-04 |
| P02-b_h0.2 | cslp/gmres | max_it | 3000 | 2.8e-03 | - | 27 | 3399 | 3428 | 4.676 | 4.6e-02 |
| P02-b_h0.2 | hx/gmres | converged | 476 | 9.7e-09 | - | 32 | 407 | 441 | 5.608 | 5.4e-09 |
| P02-b_h0.2 | cslp_hx/gmres | max_it | 1000 | 1.5e-03 | - | 29 | 1155 | 1186 | 4.753 | 4.1e-02 |
| P02-b_h0.2 | npatch_asm/cocg | converged | 2352 | 8.3e-09 | - | 29 | 141 | 172 | 2.901 | 7.8e-10 |
| P02-b_h0.2 | mumps/direct | converged | 1 | 6.0e-13 | - | 32 | 0.4 | 35 | 4.719 | - |
| P02-sr_h1.6 | gs/gmres | max_it | 10000 | 3.3e-02 | - | 2.9 | 99 | 102 | 0.341 | 1.7e-01 |
| P02-sr_h1.6 | ssor/gmres | max_it | 10000 | 1.5e-02 | - | 2.9 | 106 | 109 | 0.341 | 7.1e-02 |
| P02-sr_h1.6 | ssor/cocg | converged | 29845 | 9.7e-09 | - | 2.9 | 161 | 165 | 0.142 | 1.4e-09 |
| P02-sr_h1.6 | amg_gamg/gmres | max_it | 10000 | 1.1e-02 | - | 3.1 | 140 | 144 | 0.37 | 5.4e-02 |
| P02-sr_h1.6 | amg_gamg/cocg | converged | 30228 | 9.3e-09 | - | 2.9 | 267 | 270 | 0.199 | 3.1e-11 |
| P02-sr_h1.6 | accel_ic/gmres | max_it | 10000 | 1.1e-02 | - | 3.0 | 220 | 224 | 0.643 | 7.7e-02 |
| P02-sr_h1.6 | accel_ic/cocg | converged | 27405 | 9.0e-09 | - | 2.9 | 125 | 128 | 0.164 | 7.8e-10 |
| P02-sr_h1.6 | cslp/gmres | converged | 1481 | 1.0e-08 | - | 4.0 | 231 | 236 | 0.712 | 2.1e-08 |
| P02-sr_h1.6 | hx/gmres | converged | 61 | 7.1e-09 | - | 4.6 | 7.5 | 12 | 0.862 | 2.3e-10 |
| P02-sr_h1.6 | cslp_hx/gmres | converged | 65 | 6.8e-09 | - | 4.3 | 9.9 | 14 | 0.727 | 3.1e-09 |
| P02-sr_h1.6 | npatch_asm/cocg | converged | 352 | 6.2e-09 | - | 4.2 | 3.1 | 7.5 | 0.459 | 2.4e-11 |
| P02-sr_h1.6 | mumps/direct | converged | 1 | 2.3e-12 | - | 4.4 | 0.1 | 4.8 | 0.556 | - |
| P03-1 | gs/gmres | max_it | 10000 | 4.9e-02 | - | 13 | 456 | 470 | 1.455 | 6.7e-01 |
| P03-1 | ssor/gmres | max_it | 10000 | 3.2e-02 | - | 13 | 486 | 501 | 1.455 | 3.7e-01 |
| P03-1 | ssor/cocg | max_it | 50000 | 4.2e-05 | - | 13 | 1258 | 1273 | 0.594 | 3.7e-08 |
| P03-1 | amg_gamg/gmres | max_it | 10000 | 2.6e-02 | - | 14 | 665 | 681 | 1.625 | 3.4e-01 |
| P03-1 | amg_gamg/cocg | max_it | 50000 | 2.2e-05 | - | 13 | 2150 | 2165 | 0.854 | 2.2e-07 |
| P03-1 | accel_ic/gmres | max_it | 10000 | 2.7e-02 | - | 14 | 977 | 992 | 2.847 | 3.7e-01 |
| P03-1 | accel_ic/cocg | max_it | 50000 | 4.8e-05 | - | 14 | 1079 | 1094 | 0.713 | 5.5e-07 |
| P03-1 | cslp/gmres | max_it | 3000 | 8.0e-05 | - | 19 | 2312 | 2333 | 3.143 | 6.1e-04 |
| P03-1 | hx/gmres | converged | 903 | 9.8e-09 | - | 22 | 406 | 430 | 3.809 | 5.4e-09 |
| P03-1 | cslp_hx/gmres | converged | 272 | 9.6e-09 | - | 20 | 215 | 236 | 3.2 | 3.2e-09 |
| P03-1 | npatch_asm/cocg | converged | 1521 | 3.5e-09 | - | 20 | 61 | 82 | 2.081 | 1.2e-10 |
| P03-1 | mumps/direct | converged | 1 | 5.1e-13 | - | 24 | 0.3 | 26 | 4.067 | - |
| P03-2 | gs/gmres | max_it | 10000 | 5.0e-02 | - | 13 | 455 | 470 | 1.45 | 7.1e-01 |
| P03-2 | ssor/gmres | max_it | 10000 | 3.1e-02 | - | 13 | 484 | 499 | 1.45 | 3.2e-01 |
| P03-2 | ssor/cocg | max_it | 50000 | 3.6e-05 | - | 13 | 1254 | 1269 | 0.591 | 4.2e-08 |
| P03-2 | amg_gamg/gmres | max_it | 10000 | 2.6e-02 | - | 14 | 662 | 678 | 1.619 | 2.8e-01 |
| P03-2 | amg_gamg/cocg | max_it | 50000 | 5.9e-05 | - | 13 | 2140 | 2155 | 0.85 | 5.8e-08 |
| P03-2 | accel_ic/gmres | max_it | 10000 | 2.7e-02 | - | 13 | 974 | 989 | 2.835 | 3.2e-01 |
| P03-2 | accel_ic/cocg | max_it | 50000 | 7.0e-05 | - | 13 | 1060 | 1075 | 0.71 | 8.4e-07 |
| P03-2 | cslp/gmres | max_it | 3000 | 6.5e-05 | - | 19 | 2309 | 2330 | 3.13 | 5.4e-04 |
| P03-2 | hx/gmres | converged | 955 | 9.9e-09 | - | 22 | 391 | 415 | 3.794 | 3.7e-09 |
| P03-2 | cslp_hx/gmres | converged | 270 | 7.5e-09 | - | 20 | 213 | 234 | 3.187 | 9.7e-10 |
| P03-2 | npatch_asm/cocg | converged | 1562 | 5.2e-09 | - | 20 | 63 | 84 | 2.075 | 9.0e-12 |
| P03-2 | mumps/direct | converged | 1 | 5.1e-13 | - | 24 | 0.4 | 27 | 4.174 | - |
| P03-3 | gs/gmres | max_it | 10000 | 5.3e-02 | - | 12 | 418 | 432 | 1.348 | 5.6e-01 |
| P03-3 | ssor/gmres | max_it | 10000 | 3.6e-02 | - | 12 | 446 | 460 | 1.348 | 5.4e-01 |
| P03-3 | ssor/cocg | max_it | 50000 | 6.2e-05 | - | 12 | 1164 | 1178 | 0.547 | 1.2e-07 |
| P03-3 | amg_gamg/gmres | max_it | 10000 | 3.0e-02 | - | 13 | 610 | 624 | 1.501 | 5.3e-01 |
| P03-3 | amg_gamg/cocg | max_it | 50000 | 1.0e-04 | - | 12 | 1981 | 1994 | 0.787 | 1.5e-06 |
| P03-3 | accel_ic/gmres | max_it | 10000 | 3.2e-02 | - | 12 | 904 | 918 | 2.636 | 4.7e-01 |
| P03-3 | accel_ic/cocg | max_it | 50000 | 2.7e-03 | - | 12 | 1002 | 1015 | 0.657 | 4.4e-06 |
| P03-3 | cslp/gmres | max_it | 3000 | 1.6e-04 | - | 17 | 2126 | 2145 | 2.925 | 1.8e-03 |
| P03-3 | hx/gmres | converged | 1470 | 9.6e-09 | - | 20 | 582 | 604 | 3.584 | 2.8e-08 |
| P03-3 | cslp_hx/gmres | converged | 277 | 8.1e-09 | - | 18 | 202 | 222 | 2.965 | 3.5e-09 |
| P03-3 | npatch_asm/cocg | converged | 1709 | 4.1e-09 | - | 18 | 65 | 85 | 1.931 | 1.0e-10 |
| P03-3 | mumps/direct | converged | 1 | 5.6e-13 | - | 22 | 0.3 | 24 | 3.8 | - |
| P03-r1 | gs/gmres | max_it | 10000 | 5.1e-02 | - | 13 | 429 | 444 | 1.374 | 7.1e-01 |
| P03-r1 | ssor/gmres | max_it | 10000 | 3.3e-02 | - | 13 | 458 | 472 | 1.374 | 4.1e-01 |
| P03-r1 | ssor/cocg | max_it | 50000 | 5.1e-05 | - | 13 | 1186 | 1200 | 0.557 | 3.9e-07 |
| P03-r1 | amg_gamg/gmres | max_it | 10000 | 2.8e-02 | - | 14 | 625 | 641 | 1.528 | 4.0e-01 |
| P03-r1 | amg_gamg/cocg | max_it | 50000 | 4.9e-05 | - | 13 | 2020 | 2034 | 0.803 | 4.2e-07 |
| P03-r1 | accel_ic/gmres | max_it | 10000 | 2.8e-02 | - | 13 | 922 | 936 | 2.685 | 4.1e-01 |
| P03-r1 | accel_ic/cocg | max_it | 50000 | 2.0e-03 | - | 13 | 1003 | 1017 | 0.669 | 1.0e-06 |
| P03-r1 | cslp/gmres | max_it | 3000 | 8.4e-05 | - | 18 | 2174 | 2193 | 2.978 | 7.7e-04 |
| P03-r1 | hx/gmres | converged | 1214 | 9.9e-09 | - | 21 | 463 | 486 | 3.615 | 2.0e-08 |
| P03-r1 | cslp_hx/gmres | converged | 277 | 8.4e-09 | - | 19 | 207 | 227 | 3.018 | 5.1e-10 |
| P03-r1 | npatch_asm/cocg | converged | 1590 | 9.2e-09 | - | 19 | 62 | 82 | 1.964 | 4.8e-11 |
| P03-r1 | mumps/direct | converged | 1 | 5.2e-13 | - | 23 | 0.3 | 25 | 3.895 | - |
| P03-r2 | gs/gmres | max_it | 10000 | 4.8e-02 | - | 13 | 436 | 450 | 1.401 | 6.3e-01 |
| P03-r2 | ssor/gmres | max_it | 10000 | 3.3e-02 | - | 13 | 465 | 480 | 1.401 | 4.0e-01 |
| P03-r2 | ssor/cocg | max_it | 50000 | 9.0e-06 | - | 13 | 1210 | 1225 | 0.571 | 9.0e-08 |
| P03-r2 | amg_gamg/gmres | max_it | 10000 | 2.8e-02 | - | 14 | 636 | 652 | 1.563 | 3.8e-01 |
| P03-r2 | amg_gamg/cocg | max_it | 50000 | 3.1e-04 | - | 13 | 2067 | 2081 | 0.822 | 3.3e-07 |
| P03-r2 | accel_ic/gmres | max_it | 10000 | 2.8e-02 | - | 13 | 940 | 954 | 2.738 | 4.0e-01 |
| P03-r2 | accel_ic/cocg | max_it | 50000 | 1.6e-02 | - | 13 | 1040 | 1054 | 0.686 | 3.3e-06 |
| P03-r2 | cslp/gmres | max_it | 3000 | 7.8e-05 | - | 18 | 2224 | 2243 | 3.045 | 5.9e-04 |
| P03-r2 | hx/gmres | converged | 1173 | 9.9e-09 | - | 21 | 476 | 498 | 3.667 | 3.3e-08 |
| P03-r2 | cslp_hx/gmres | converged | 273 | 8.8e-09 | - | 19 | 208 | 229 | 3.087 | 1.8e-09 |
| P03-r2 | npatch_asm/cocg | converged | 1595 | 9.8e-09 | - | 19 | 61 | 81 | 2.006 | 1.9e-11 |
| P03-r2 | mumps/direct | converged | 1 | 5.1e-13 | - | 23 | 0.3 | 25 | 3.826 | - |
| P03-r8 | gs/gmres | max_it | 10000 | 4.9e-02 | - | 14 | 487 | 503 | 1.564 | 7.1e-01 |
| P03-r8 | ssor/gmres | max_it | 10000 | 3.3e-02 | - | 14 | 520 | 537 | 1.564 | 4.4e-01 |
| P03-r8 | ssor/cocg | max_it | 50000 | 5.3e-05 | - | 14 | 1356 | 1372 | 0.637 | 5.4e-07 |
| P03-r8 | amg_gamg/gmres | max_it | 10000 | 2.7e-02 | - | 16 | 716 | 733 | 1.745 | 3.9e-01 |
| P03-r8 | amg_gamg/cocg | max_it | 50000 | 6.3e-05 | - | 14 | 2328 | 2345 | 0.916 | 8.7e-08 |
| P03-r8 | accel_ic/gmres | max_it | 10000 | 2.8e-02 | - | 14 | 1054 | 1070 | 3.064 | 4.3e-01 |
| P03-r8 | accel_ic/cocg | max_it | 50000 | 5.0e-02 | - | 14 | 1152 | 1169 | 0.766 | 1.7e-06 |
| P03-r8 | cslp/gmres | max_it | 3000 | 8.7e-05 | - | 20 | 2512 | 2534 | 3.382 | 7.0e-04 |
| P03-r8 | hx/gmres | converged | 961 | 9.9e-09 | - | 24 | 424 | 449 | 4.103 | 6.0e-09 |
| P03-r8 | cslp_hx/gmres | converged | 271 | 7.7e-09 | - | 22 | 232 | 255 | 3.44 | 3.1e-09 |
| P03-r8 | npatch_asm/cocg | converged | 1526 | 7.1e-09 | - | 21 | 66 | 88 | 2.243 | 2.1e-11 |
| P03-r8 | mumps/direct | converged | 1 | 5.2e-13 | - | 27 | 0.4 | 29 | 4.594 | - |
| P03-d0.7 | gs/gmres | max_it | 10000 | 5.0e-02 | - | 13 | 441 | 455 | 1.417 | 6.3e-01 |
| P03-d0.7 | ssor/gmres | max_it | 10000 | 3.4e-02 | - | 13 | 471 | 485 | 1.417 | 4.7e-01 |
| P03-d0.7 | ssor/cocg | max_it | 50000 | 3.1e-03 | - | 13 | 1223 | 1237 | 0.578 | 1.6e-06 |
| P03-d0.7 | amg_gamg/gmres | max_it | 10000 | 2.9e-02 | - | 14 | 644 | 660 | 1.58 | 4.4e-01 |
| P03-d0.7 | amg_gamg/cocg | max_it | 50000 | 5.6e-06 | - | 13 | 2091 | 2105 | 0.831 | 5.7e-09 |
| P03-d0.7 | accel_ic/gmres | max_it | 10000 | 2.8e-02 | - | 13 | 952 | 967 | 2.773 | 4.7e-01 |
| P03-d0.7 | accel_ic/cocg | max_it | 50000 | 6.1e-03 | - | 13 | 1054 | 1068 | 0.694 | 1.1e-06 |
| P03-d0.7 | cslp/gmres | max_it | 3000 | 9.2e-05 | - | 18 | 2239 | 2259 | 3.074 | 6.4e-04 |
| P03-d0.7 | hx/gmres | converged | 1279 | 1.0e-08 | - | 21 | 514 | 537 | 3.744 | 4.1e-08 |
| P03-d0.7 | cslp_hx/gmres | converged | 274 | 8.9e-09 | - | 19 | 211 | 232 | 3.117 | 1.2e-09 |
| P03-d0.7 | npatch_asm/cocg | converged | 1579 | 8.6e-09 | - | 19 | 62 | 83 | 2.027 | 4.2e-11 |
| P03-d0.7 | mumps/direct | converged | 1 | 5.2e-13 | - | 24 | 0.3 | 26 | 3.927 | - |
| P03-d2 | gs/gmres | max_it | 10000 | 4.9e-02 | - | 15 | 478 | 495 | 1.539 | 7.2e-01 |
| P03-d2 | ssor/gmres | max_it | 10000 | 3.0e-02 | - | 15 | 511 | 527 | 1.539 | 3.4e-01 |
| P03-d2 | ssor/cocg | max_it | 50000 | 3.4e-06 | - | 15 | 1331 | 1348 | 0.623 | 2.2e-08 |
| P03-d2 | amg_gamg/gmres | max_it | 10000 | 2.5e-02 | - | 16 | 701 | 719 | 1.713 | 3.0e-01 |
| P03-d2 | amg_gamg/cocg | max_it | 50000 | 2.4e-06 | - | 15 | 2283 | 2300 | 0.897 | 5.9e-08 |
| P03-d2 | accel_ic/gmres | max_it | 10000 | 2.7e-02 | - | 15 | 1035 | 1052 | 3.01 | 3.5e-01 |
| P03-d2 | accel_ic/cocg | max_it | 50000 | 2.6e-05 | - | 15 | 1128 | 1145 | 0.749 | 8.6e-07 |
| P03-d2 | cslp/gmres | max_it | 3000 | 6.9e-05 | - | 21 | 2449 | 2471 | 3.327 | 5.0e-04 |
| P03-d2 | hx/gmres | converged | 864 | 9.9e-09 | - | 24 | 371 | 397 | 4.05 | 1.7e-09 |
| P03-d2 | cslp_hx/gmres | converged | 274 | 8.5e-09 | - | 22 | 231 | 255 | 3.38 | 6.1e-10 |
| P03-d2 | npatch_asm/cocg | converged | 1556 | 9.1e-09 | - | 21 | 69 | 92 | 2.202 | 2.5e-11 |
| P03-d2 | mumps/direct | converged | 1 | 5.2e-13 | - | 26 | 0.4 | 29 | 4.393 | - |
| P03-d5 | gs/gmres | max_it | 10000 | 5.4e-02 | - | 15 | 504 | 521 | 1.618 | 6.1e-01 |
| P03-d5 | ssor/gmres | max_it | 10000 | 3.6e-02 | - | 15 | 538 | 554 | 1.617 | 5.0e-01 |
| P03-d5 | ssor/cocg | max_it | 50000 | 2.5e-05 | - | 15 | 1398 | 1414 | 0.66 | 4.7e-07 |
| P03-d5 | amg_gamg/gmres | max_it | 10000 | 3.0e-02 | - | 16 | 737 | 755 | 1.804 | 5.1e-01 |
| P03-d5 | amg_gamg/cocg | max_it | 50000 | 8.3e-05 | - | 15 | 2395 | 2412 | 0.949 | 5.1e-08 |
| P03-d5 | accel_ic/gmres | max_it | 10000 | 3.2e-02 | - | 15 | 1087 | 1104 | 3.165 | 4.6e-01 |
| P03-d5 | accel_ic/cocg | max_it | 50000 | 1.8e-02 | - | 15 | 1207 | 1224 | 0.793 | 7.3e-07 |
| P03-d5 | cslp/gmres | max_it | 3000 | 1.4e-04 | - | 21 | 2577 | 2600 | 3.495 | 1.5e-03 |
| P03-d5 | hx/gmres | converged | 1179 | 9.8e-09 | - | 24 | 535 | 561 | 4.269 | 1.9e-08 |
| P03-d5 | cslp_hx/gmres | converged | 279 | 8.0e-09 | - | 22 | 247 | 271 | 3.55 | 3.8e-09 |
| P03-d5 | npatch_asm/cocg | converged | 1568 | 6.9e-09 | - | 22 | 69 | 93 | 2.302 | 2.1e-11 |
| P03-d5 | mumps/direct | converged | 1 | 5.4e-13 | - | 26 | 0.4 | 28 | 4.239 | - |
| P03-v0.2 | gs/gmres | max_it | 10000 | 4.9e-02 | - | 15 | 499 | 516 | 1.604 | 7.1e-01 |
| P03-v0.2 | ssor/gmres | max_it | 10000 | 3.2e-02 | - | 15 | 533 | 549 | 1.604 | 3.4e-01 |
| P03-v0.2 | ssor/cocg | max_it | 50000 | 1.4e-05 | - | 15 | 1387 | 1403 | 0.654 | 2.0e-07 |
| P03-v0.2 | amg_gamg/gmres | max_it | 10000 | 2.7e-02 | - | 16 | 733 | 751 | 1.789 | 3.3e-01 |
| P03-v0.2 | amg_gamg/cocg | max_it | 50000 | 2.5e-04 | - | 15 | 2377 | 2394 | 0.94 | 3.1e-07 |
| P03-v0.2 | accel_ic/gmres | max_it | 10000 | 2.8e-02 | - | 15 | 1080 | 1097 | 3.139 | 3.4e-01 |
| P03-v0.2 | accel_ic/cocg | max_it | 50000 | 1.4e-04 | - | 15 | 1187 | 1203 | 0.785 | 1.9e-07 |
| P03-v0.2 | cslp/gmres | max_it | 3000 | 1.1e-04 | - | 21 | 2570 | 2592 | 3.477 | 9.7e-04 |
| P03-v0.2 | hx/gmres | converged | 907 | 9.9e-09 | - | 24 | 418 | 444 | 4.198 | 2.4e-09 |
| P03-v0.2 | cslp_hx/gmres | converged | 288 | 8.7e-09 | - | 22 | 255 | 278 | 3.522 | 1.7e-09 |
| P03-v0.2 | npatch_asm/cocg | converged | 1547 | 6.5e-09 | - | 22 | 69 | 92 | 2.285 | 7.0e-11 |
| P03-v0.2 | mumps/direct | converged | 1 | 5.2e-13 | - | 27 | 0.4 | 29 | 4.423 | - |
| P03-v0.5 | gs/gmres | max_it | 10000 | 4.9e-02 | - | 13 | 429 | 443 | 1.384 | 6.1e-01 |
| P03-v0.5 | ssor/gmres | max_it | 10000 | 3.2e-02 | - | 12 | 458 | 472 | 1.383 | 4.3e-01 |
| P03-v0.5 | ssor/cocg | max_it | 50000 | 7.2e-05 | - | 13 | 1193 | 1207 | 0.565 | 1.3e-07 |
| P03-v0.5 | amg_gamg/gmres | max_it | 10000 | 2.8e-02 | - | 14 | 627 | 642 | 1.544 | 4.1e-01 |
| P03-v0.5 | amg_gamg/cocg | max_it | 50000 | 1.3e-05 | - | 13 | 2035 | 2049 | 0.811 | 6.4e-09 |
| P03-v0.5 | accel_ic/gmres | max_it | 10000 | 2.7e-02 | - | 13 | 927 | 941 | 2.703 | 4.6e-01 |
| P03-v0.5 | accel_ic/cocg | max_it | 50000 | 2.2e-04 | - | 13 | 1026 | 1041 | 0.678 | 6.9e-07 |
| P03-v0.5 | cslp/gmres | max_it | 3000 | 9.0e-05 | - | 18 | 2184 | 2203 | 3.005 | 6.3e-04 |
| P03-v0.5 | hx/gmres | converged | 1050 | 9.9e-09 | - | 21 | 395 | 417 | 3.674 | 1.6e-08 |
| P03-v0.5 | cslp_hx/gmres | converged | 268 | 9.6e-09 | - | 19 | 201 | 222 | 3.049 | 2.9e-09 |
| P03-v0.5 | npatch_asm/cocg | converged | 1518 | 9.7e-09 | - | 19 | 59 | 79 | 1.977 | 1.9e-11 |
| P03-v0.5 | mumps/direct | converged | 1 | 5.2e-13 | - | 23 | 0.3 | 25 | 3.914 | - |
| P03-a0.6 | gs/gmres | max_it | 10000 | 5.0e-02 | - | 13 | 452 | 467 | 1.453 | 6.7e-01 |
| P03-a0.6 | ssor/gmres | max_it | 10000 | 3.2e-02 | - | 13 | 483 | 498 | 1.453 | 4.1e-01 |
| P03-a0.6 | ssor/cocg | max_it | 50000 | 3.3e-05 | - | 13 | 1252 | 1267 | 0.589 | 6.9e-08 |
| P03-a0.6 | amg_gamg/gmres | max_it | 10000 | 2.6e-02 | - | 15 | 662 | 678 | 1.619 | 3.9e-01 |
| P03-a0.6 | amg_gamg/cocg | max_it | 50000 | 5.0e-06 | - | 13 | 2147 | 2162 | 0.849 | 8.4e-08 |
| P03-a0.6 | accel_ic/gmres | max_it | 10000 | 2.7e-02 | - | 13 | 976 | 991 | 2.842 | 4.2e-01 |
| P03-a0.6 | accel_ic/cocg | max_it | 50000 | 2.6e-03 | - | 13 | 1066 | 1081 | 0.708 | 1.4e-06 |
| P03-a0.6 | cslp/gmres | max_it | 3000 | 9.6e-05 | - | 19 | 2309 | 2329 | 3.155 | 8.0e-04 |
| P03-a0.6 | hx/gmres | converged | 1087 | 9.9e-09 | - | 24 | 446 | 471 | 3.808 | 3.1e-08 |
| P03-a0.6 | cslp_hx/gmres | converged | 271 | 9.2e-09 | - | 21 | 214 | 237 | 3.2 | 2.0e-09 |
| P03-a0.6 | npatch_asm/cocg | converged | 1519 | 7.8e-09 | - | 21 | 62 | 85 | 2.071 | 7.3e-11 |
| P03-a0.6 | mumps/direct | converged | 1 | 5.3e-13 | - | 24 | 0.3 | 27 | 4.052 | - |
| P03-a1.2 | gs/gmres | max_it | 10000 | 4.9e-02 | - | 13 | 451 | 466 | 1.452 | 6.8e-01 |
| P03-a1.2 | ssor/gmres | max_it | 10000 | 3.1e-02 | - | 13 | 482 | 496 | 1.452 | 3.5e-01 |
| P03-a1.2 | ssor/cocg | max_it | 50000 | 5.6e-06 | - | 13 | 1253 | 1268 | 0.589 | 9.4e-08 |
| P03-a1.2 | amg_gamg/gmres | max_it | 10000 | 2.6e-02 | - | 15 | 659 | 675 | 1.622 | 2.9e-01 |
| P03-a1.2 | amg_gamg/cocg | max_it | 50000 | 1.5e-05 | - | 13 | 2144 | 2159 | 0.852 | 1.8e-07 |
| P03-a1.2 | accel_ic/gmres | max_it | 10000 | 2.7e-02 | - | 13 | 976 | 991 | 2.842 | 3.5e-01 |
| P03-a1.2 | accel_ic/cocg | max_it | 50000 | 1.8e-04 | - | 13 | 1078 | 1093 | 0.708 | 4.9e-07 |
| P03-a1.2 | cslp/gmres | max_it | 3000 | 5.9e-05 | - | 19 | 2302 | 2322 | 3.168 | 4.8e-04 |
| P03-a1.2 | hx/gmres | converged | 957 | 1.0e-08 | - | 22 | 389 | 412 | 3.822 | 5.8e-09 |
| P03-a1.2 | cslp_hx/gmres | converged | 267 | 7.8e-09 | - | 20 | 210 | 232 | 3.208 | 9.2e-10 |
| P03-a1.2 | npatch_asm/cocg | converged | 1507 | 9.6e-09 | - | 19 | 62 | 83 | 2.075 | 4.2e-11 |
| P03-a1.2 | mumps/direct | converged | 1 | 5.1e-13 | - | 24 | 0.3 | 27 | 4.026 | - |
| P04-1 | gs/gmres | max_it | 10000 | 2.6e-02 | - | 18 | 629 | 648 | 2.007 | 7.2e-01 |
| P04-1 | ssor/gmres | max_it | 10000 | 1.3e-02 | - | 18 | 673 | 692 | 2.007 | 3.4e-01 |
| P04-1 | ssor/cocg | converged | 42790 | 9.6e-09 | - | 18 | 1485 | 1504 | 0.81 | 1.1e-09 |
| P04-1 | amg_gamg/gmres | max_it | 10000 | 1.2e-02 | - | 19 | 932 | 952 | 2.231 | 3.5e-01 |
| P04-1 | amg_gamg/cocg | converged | 47576 | 6.5e-09 | - | 18 | 2873 | 2892 | 1.163 | 2.0e-09 |
| P04-1 | accel_ic/gmres | max_it | 10000 | 1.2e-02 | - | 18 | 1356 | 1376 | 3.928 | 3.3e-01 |
| P04-1 | accel_ic/cocg | converged | 48204 | 9.1e-09 | - | 18 | 1457 | 1476 | 0.973 | 7.8e-10 |
| P04-1 | cslp/gmres | max_it | 3000 | 2.8e-05 | - | 25 | 3274 | 3300 | 4.356 | 6.4e-04 |
| P04-1 | hx/gmres | converged | 63 | 7.1e-09 | - | 31 | 48 | 80 | 5.113 | 1.2e-09 |
| P04-1 | cslp_hx/gmres | converged | 161 | 9.8e-09 | - | 27 | 175 | 203 | 4.408 | 1.6e-08 |
| P04-1 | npatch_asm/cocg | converged | 779 | 6.9e-09 | - | 27 | 45 | 74 | 3.063 | 1.7e-10 |
| P04-1 | mumps/direct | converged | 1 | 2.7e-13 | - | 36 | 0.6 | 38 | 6.749 | - |
| P04-2 | gs/gmres | max_it | 10000 | 3.7e-02 | - | 18 | 628 | 647 | 2.021 | 1.1e+00 |
| P04-2 | ssor/gmres | max_it | 10000 | 1.6e-02 | - | 18 | 672 | 691 | 2.021 | 4.9e-01 |
| P04-2 | ssor/cocg | converged | 40777 | 9.3e-09 | - | 18 | 1428 | 1447 | 0.816 | 2.7e-09 |
| P04-2 | amg_gamg/gmres | max_it | 10000 | 1.5e-02 | - | 20 | 934 | 955 | 2.247 | 4.9e-01 |
| P04-2 | amg_gamg/cocg | converged | 47239 | 8.0e-09 | - | 18 | 2857 | 2876 | 1.173 | 1.8e-10 |
| P04-2 | accel_ic/gmres | max_it | 10000 | 1.4e-02 | - | 18 | 1365 | 1384 | 3.953 | 5.3e-01 |
| P04-2 | accel_ic/cocg | converged | 48694 | 6.9e-09 | - | 18 | 1472 | 1491 | 0.98 | 4.3e-10 |
| P04-2 | cslp/gmres | max_it | 3000 | 7.2e-06 | - | 26 | 3295 | 3322 | 4.386 | 2.9e-04 |
| P04-2 | hx/gmres | converged | 68 | 7.1e-09 | - | 30 | 51 | 83 | 5.148 | 7.2e-10 |
| P04-2 | cslp_hx/gmres | converged | 155 | 9.7e-09 | - | 27 | 169 | 197 | 4.441 | 4.8e-09 |
| P04-2 | npatch_asm/cocg | converged | 762 | 6.4e-09 | - | 27 | 44 | 73 | 3.084 | 4.7e-10 |
| P04-2 | mumps/direct | converged | 1 | 3.9e-13 | - | 36 | 0.6 | 38 | 6.519 | - |
| P04-3 | gs/gmres | max_it | 10000 | 4.4e-02 | - | 18 | 641 | 661 | 2.061 | 1.0e+00 |
| P04-3 | ssor/gmres | max_it | 10000 | 1.6e-02 | - | 18 | 685 | 705 | 2.06 | 3.8e-01 |
| P04-3 | ssor/cocg | converged | 40983 | 7.1e-09 | - | 19 | 1462 | 1482 | 0.836 | 5.1e-10 |
| P04-3 | amg_gamg/gmres | max_it | 10000 | 1.5e-02 | - | 20 | 951 | 972 | 2.295 | 4.1e-01 |
| P04-3 | amg_gamg/cocg | converged | 47888 | 5.1e-09 | - | 18 | 2932 | 2951 | 1.194 | 7.1e-10 |
| P04-3 | accel_ic/gmres | max_it | 10000 | 1.6e-02 | - | 19 | 1395 | 1414 | 4.032 | 5.5e-01 |
| P04-3 | accel_ic/cocg | max_it | 50000 | 3.0e-06 | - | 18 | 1555 | 1575 | 1.003 | 3.0e-09 |
| P04-3 | cslp/gmres | max_it | 3000 | 1.9e-06 | - | 26 | 3355 | 3382 | 4.467 | 6.7e-05 |
| P04-3 | hx/gmres | converged | 82 | 7.3e-09 | - | 31 | 63 | 95 | 5.293 | 1.9e-09 |
| P04-3 | cslp_hx/gmres | converged | 151 | 8.4e-09 | - | 27 | 169 | 198 | 4.524 | 9.1e-09 |
| P04-3 | npatch_asm/cocg | converged | 787 | 7.4e-09 | - | 28 | 47 | 76 | 3.149 | 4.1e-10 |
| P04-3 | mumps/direct | converged | 1 | 3.5e-13 | - | 37 | 0.6 | 39 | 6.472 | - |
| P04-4 | gs/gmres | max_it | 10000 | 3.4e-02 | - | 27 | 934 | 962 | 2.973 | 1.0e+00 |
| P04-4 | ssor/gmres | max_it | 10000 | 1.8e-02 | - | 27 | 997 | 1025 | 2.973 | 3.2e-01 |
| P04-4 | ssor/cocg | converged | 40039 | 9.3e-09 | - | 27 | 2069 | 2097 | 1.196 | 2.4e-09 |
| P04-4 | amg_gamg/gmres | max_it | 10000 | 1.6e-02 | - | 29 | 1391 | 1422 | 3.304 | 2.9e-01 |
| P04-4 | amg_gamg/cocg | converged | 43811 | 8.4e-09 | - | 27 | 3942 | 3970 | 1.792 | 2.2e-09 |
| P04-4 | accel_ic/gmres | max_it | 10000 | 1.6e-02 | - | 27 | 2023 | 2052 | 5.832 | 3.9e-01 |
| P04-4 | accel_ic/cocg | converged | 46894 | 8.9e-09 | - | 27 | 2112 | 2140 | 1.437 | 3.4e-09 |
| P04-4 | cslp/gmres | max_it | 3000 | 5.5e-08 | - | 38 | 4958 | 4998 | 6.497 | 7.8e-07 |
| P04-4 | hx/gmres | converged | 705 | 9.9e-09 | - | 46 | 757 | 805 | 7.618 | 8.1e-10 |
| P04-4 | cslp_hx/gmres | converged | 177 | 8.3e-09 | - | 40 | 304 | 345 | 6.573 | 7.1e-09 |
| P04-4 | npatch_asm/cocg | converged | 3848 | 9.2e-09 | - | 41 | 338 | 381 | 4.088 | 2.2e-09 |
| P04-4 | mumps/direct | converged | 1 | 5.0e-13 | - | 55 | 1.4 | 58 | 9.349 | - |
| P05-1 | gs/gmres | max_it | 10000 | 4.9e-05 | - | 1.8 | 64 | 66 | 0.224 | 1.4e-05 |
| P05-1 | ssor/gmres | max_it | 10000 | 1.0e-06 | - | 1.8 | 68 | 70 | 0.224 | 1.4e-07 |
| P05-1 | ssor/cocg | converged | 4070 | 8.3e-09 | - | 1.8 | 13 | 16 | 0.093 | 1.3e-11 |
| P05-1 | amg_gamg/gmres | max_it | 10000 | 1.7e-08 | - | 1.9 | 86 | 89 | 0.235 | 3.1e-09 |
| P05-1 | amg_gamg/cocg | converged | 4043 | 5.6e-09 | - | 1.8 | 21 | 23 | 0.125 | 1.3e-10 |
| P05-1 | accel_ic/gmres | max_it | 10000 | 7.1e-06 | - | 1.8 | 144 | 147 | 0.426 | 8.9e-07 |
| P05-1 | accel_ic/cocg | converged | 5242 | 3.8e-09 | - | 1.8 | 15 | 17 | 0.104 | 2.1e-11 |
| P05-1 | cslp/gmres | converged | 215 | 9.7e-09 | - | 2.5 | 19 | 22 | 0.454 | 1.5e-11 |
| P05-1 | hx/gmres | converged | 33 | 7.1e-09 | - | 2.9 | 2.8 | 6.3 | 0.555 | 6.0e-11 |
| P05-1 | cslp_hx/gmres | converged | 20 | 2.1e-09 | - | 2.7 | 1.8 | 5.2 | 0.464 | 1.1e-10 |
| P05-1 | npatch_asm/cocg | converged | 366 | 9.5e-09 | - | 2.5 | 1.5 | 4.7 | 0.216 | 2.3e-12 |
| P05-1 | mumps/direct | converged | 1 | 9.3e-14 | - | 2.2 | 0.0 | 3.0 | 0.127 | - |
| P05-2 | gs/gmres | max_it | 10000 | 1.9e-02 | - | 1.8 | 63 | 66 | 0.224 | 2.0e-01 |
| P05-2 | ssor/gmres | max_it | 10000 | 2.3e-04 | - | 1.8 | 68 | 70 | 0.224 | 1.2e-03 |
| P05-2 | ssor/cocg | converged | 3492 | 6.5e-09 | - | 1.8 | 11 | 14 | 0.093 | 1.3e-10 |
| P05-2 | amg_gamg/gmres | max_it | 10000 | 2.0e-06 | - | 1.9 | 86 | 89 | 0.236 | 6.1e-06 |
| P05-2 | amg_gamg/cocg | converged | 3617 | 7.6e-09 | - | 1.8 | 18 | 21 | 0.125 | 5.7e-10 |
| P05-2 | accel_ic/gmres | max_it | 10000 | 3.6e-03 | - | 1.8 | 144 | 147 | 0.426 | 2.1e-02 |
| P05-2 | accel_ic/cocg | converged | 4647 | 6.5e-09 | - | 1.8 | 13 | 16 | 0.104 | 7.0e-11 |
| P05-2 | cslp/gmres | converged | 181 | 9.2e-09 | - | 2.4 | 16 | 19 | 0.454 | 7.9e-10 |
| P05-2 | hx/gmres | converged | 44 | 8.0e-09 | - | 2.9 | 3.6 | 7.2 | 0.555 | 6.5e-10 |
| P05-2 | cslp_hx/gmres | converged | 28 | 8.5e-09 | - | 2.6 | 2.4 | 5.8 | 0.464 | 2.1e-09 |
| P05-2 | npatch_asm/cocg | converged | 429 | 8.5e-09 | - | 2.5 | 1.8 | 5.0 | 0.219 | 2.2e-12 |
| P05-2 | mumps/direct | converged | 1 | 5.6e-13 | - | 2.2 | 0.0 | 2.9 | 0.135 | - |
| P05-3 | gs/gmres | max_it | 10000 | 2.0e-02 | - | 1.8 | 63 | 66 | 0.224 | 2.3e-01 |
| P05-3 | ssor/gmres | max_it | 10000 | 2.2e-04 | - | 1.8 | 68 | 70 | 0.225 | 1.7e-03 |
| P05-3 | ssor/cocg | converged | 3619 | 9.1e-09 | - | 1.8 | 12 | 14 | 0.093 | 6.4e-11 |
| P05-3 | amg_gamg/gmres | max_it | 10000 | 1.8e-06 | - | 1.9 | 86 | 89 | 0.236 | 6.0e-06 |
| P05-3 | amg_gamg/cocg | converged | 3440 | 9.0e-09 | - | 1.8 | 18 | 20 | 0.125 | 1.1e-10 |
| P05-3 | accel_ic/gmres | max_it | 10000 | 4.1e-03 | - | 1.8 | 144 | 147 | 0.426 | 5.8e-02 |
| P05-3 | accel_ic/cocg | converged | 4381 | 8.4e-09 | - | 1.8 | 12 | 15 | 0.104 | 1.5e-11 |
| P05-3 | cslp/gmres | converged | 179 | 1.0e-08 | - | 2.5 | 15 | 19 | 0.454 | 7.9e-10 |
| P05-3 | hx/gmres | converged | 44 | 8.1e-09 | - | 2.9 | 3.6 | 7.2 | 0.555 | 6.6e-10 |
| P05-3 | cslp_hx/gmres | converged | 28 | 8.6e-09 | - | 2.6 | 2.4 | 5.8 | 0.464 | 1.9e-09 |
| P05-3 | npatch_asm/cocg | converged | 429 | 8.6e-09 | - | 2.5 | 1.8 | 5.0 | 0.216 | 2.2e-12 |
| P05-3 | mumps/direct | converged | 1 | 5.2e-13 | - | 2.2 | 0.0 | 2.9 | 0.135 | - |
| P05-2_sibc | gs/gmres | max_it | 10000 | 7.5e-03 | - | 1.8 | 64 | 66 | 0.224 | 6.3e-02 |
| P05-2_sibc | ssor/gmres | max_it | 10000 | 2.4e-04 | - | 1.8 | 68 | 70 | 0.224 | 1.4e-03 |
| P05-2_sibc | ssor/cocg | converged | 4091 | 9.2e-09 | - | 1.8 | 13 | 16 | 0.094 | 1.3e-10 |
| P05-2_sibc | amg_gamg/gmres | max_it | 10000 | 8.9e-06 | - | 1.9 | 86 | 88 | 0.236 | 2.9e-05 |
| P05-2_sibc | amg_gamg/cocg | converged | 3539 | 9.9e-09 | - | 1.8 | 18 | 20 | 0.125 | 2.2e-09 |
| P05-2_sibc | accel_ic/gmres | max_it | 10000 | 1.0e-03 | - | 1.8 | 144 | 147 | 0.426 | 9.2e-03 |
| P05-2_sibc | accel_ic/cocg | converged | 4879 | 8.2e-09 | - | 1.8 | 14 | 16 | 0.104 | 9.4e-11 |
| P05-2_sibc | cslp/gmres | converged | 248 | 9.5e-09 | - | 2.4 | 22 | 25 | 0.454 | 9.4e-11 |
| P05-2_sibc | hx/gmres | converged | 30 | 5.6e-09 | - | 2.8 | 0.7 | 4.2 | 0.555 | 5.5e-10 |
| P05-2_sibc | cslp_hx/gmres | converged | 30 | 4.2e-09 | - | 2.7 | 2.6 | 5.9 | 0.464 | 2.1e-09 |
| P05-2_sibc | npatch_asm/cocg | converged | 434 | 8.8e-09 | - | 2.6 | 2.4 | 5.7 | 0.293 | 0.0e+00 |
| P05-2_sibc | mumps/direct | converged | 1 | 6.0e-13 | - | 2.1 | 0.0 | 2.9 | 0.144 | - |
| P05-g0.1 | gs/gmres | max_it | 10000 | 1.7e-02 | - | 1.8 | 63 | 66 | 0.224 | 4.7e-02 |
| P05-g0.1 | ssor/gmres | max_it | 10000 | 5.5e-05 | - | 1.8 | 68 | 70 | 0.224 | 5.9e-05 |
| P05-g0.1 | ssor/cocg | converged | 5373 | 4.9e-09 | - | 1.8 | 18 | 20 | 0.094 | 2.3e-12 |
| P05-g0.1 | amg_gamg/gmres | max_it | 10000 | 7.0e-06 | - | 1.9 | 86 | 89 | 0.236 | 5.0e-06 |
| P05-g0.1 | amg_gamg/cocg | converged | 3817 | 8.7e-09 | - | 1.8 | 19 | 22 | 0.125 | 2.7e-11 |
| P05-g0.1 | accel_ic/gmres | max_it | 10000 | 6.1e-03 | - | 1.8 | 144 | 146 | 0.426 | 2.2e-02 |
| P05-g0.1 | accel_ic/cocg | converged | 5880 | 8.0e-09 | - | 1.8 | 17 | 19 | 0.104 | 1.0e-12 |
| P05-g0.1 | cslp/gmres | converged | 231 | 9.5e-09 | - | 2.4 | 20 | 23 | 0.454 | 8.1e-11 |
| P05-g0.1 | hx/gmres | converged | 45 | 6.4e-09 | - | 2.9 | 3.7 | 7.3 | 0.554 | 5.6e-11 |
| P05-g0.1 | cslp_hx/gmres | converged | 26 | 2.4e-09 | - | 2.7 | 2.2 | 5.6 | 0.464 | 8.5e-11 |
| P05-g0.1 | npatch_asm/cocg | converged | 432 | 8.1e-09 | - | 2.5 | 1.9 | 5.0 | 0.216 | 1.5e-12 |
| P05-g0.1 | mumps/direct | converged | 1 | 5.6e-13 | - | 2.2 | 0.0 | 2.9 | 0.141 | - |
| P05-g1.0 | gs/gmres | max_it | 10000 | 9.4e-03 | - | 1.8 | 63 | 66 | 0.224 | 2.1e-01 |
| P05-g1.0 | ssor/gmres | max_it | 10000 | 2.8e-04 | - | 1.8 | 68 | 70 | 0.224 | 1.6e-03 |
| P05-g1.0 | ssor/cocg | converged | 4099 | 9.4e-09 | - | 1.8 | 13 | 16 | 0.093 | 5.7e-10 |
| P05-g1.0 | amg_gamg/gmres | max_it | 10000 | 2.8e-05 | - | 1.9 | 86 | 89 | 0.236 | 3.3e-04 |
| P05-g1.0 | amg_gamg/cocg | converged | 4019 | 6.2e-09 | - | 1.8 | 21 | 23 | 0.125 | 3.7e-11 |
| P05-g1.0 | accel_ic/gmres | max_it | 10000 | 4.3e-04 | - | 1.8 | 144 | 147 | 0.426 | 5.0e-03 |
| P05-g1.0 | accel_ic/cocg | converged | 5113 | 8.9e-09 | - | 1.8 | 14 | 16 | 0.104 | 4.3e-11 |
| P05-g1.0 | cslp/gmres | converged | 239 | 9.3e-09 | - | 2.5 | 21 | 24 | 0.454 | 3.2e-09 |
| P05-g1.0 | hx/gmres | converged | 48 | 8.7e-09 | - | 2.9 | 4.0 | 7.6 | 0.555 | 2.1e-09 |
| P05-g1.0 | cslp_hx/gmres | converged | 31 | 8.1e-09 | - | 2.6 | 2.7 | 6.0 | 0.464 | 9.3e-09 |
| P05-g1.0 | npatch_asm/cocg | converged | 448 | 8.4e-09 | - | 2.5 | 1.9 | 5.0 | 0.216 | 2.2e-12 |
| P05-g1.0 | mumps/direct | converged | 1 | 5.5e-13 | - | 2.2 | 0.0 | 2.9 | 0.135 | - |
| P05-fc | gs/gmres | max_it | 10000 | 6.8e-05 | - | 1.8 | 64 | 66 | 0.224 | 6.7e-06 |
| P05-fc | ssor/gmres | max_it | 10000 | 5.0e-06 | - | 1.8 | 68 | 70 | 0.224 | 4.9e-07 |
| P05-fc | ssor/cocg | converged | 3308 | 8.1e-09 | - | 1.8 | 11 | 13 | 0.093 | 1.1e-12 |
| P05-fc | amg_gamg/gmres | max_it | 10000 | 2.3e-08 | - | 1.9 | 86 | 89 | 0.236 | 2.1e-09 |
| P05-fc | amg_gamg/cocg | converged | 3005 | 5.1e-09 | - | 1.8 | 15 | 18 | 0.129 | 4.0e-11 |
| P05-fc | accel_ic/gmres | max_it | 10000 | 4.3e-05 | - | 1.8 | 144 | 147 | 0.426 | 4.9e-06 |
| P05-fc | accel_ic/cocg | converged | 3937 | 5.8e-09 | - | 1.8 | 11 | 13 | 0.105 | 5.0e-12 |
| P05-fc | cslp/gmres | converged | 175 | 9.7e-09 | - | 2.5 | 15 | 18 | 0.454 | 1.0e-10 |
| P05-fc | hx/gmres | converged | 44 | 4.9e-09 | - | 2.9 | 3.6 | 7.2 | 0.555 | 2.7e-11 |
| P05-fc | cslp_hx/gmres | converged | 29 | 7.9e-09 | - | 2.7 | 2.5 | 5.9 | 0.464 | 1.9e-10 |
| P05-fc | npatch_asm/cocg | converged | 390 | 8.4e-09 | - | 2.5 | 1.6 | 4.8 | 0.216 | 1.2e-10 |
| P05-fc | mumps/direct | converged | 1 | 3.3e-14 | - | 2.2 | 0.0 | 2.9 | 0.134 | - |
| P05-fe | gs/gmres | max_it | 10000 | 5.0e-03 | - | 1.7 | 63 | 66 | 0.223 | 3.5e-02 |
| P05-fe | ssor/gmres | max_it | 10000 | 2.1e-04 | - | 1.8 | 67 | 70 | 0.223 | 8.2e-04 |
| P05-fe | ssor/cocg | converged | 4036 | 7.2e-09 | - | 1.7 | 13 | 16 | 0.093 | 2.0e-10 |
| P05-fe | amg_gamg/gmres | max_it | 10000 | 9.4e-06 | - | 1.9 | 86 | 88 | 0.232 | 2.3e-05 |
| P05-fe | amg_gamg/cocg | converged | 3526 | 8.6e-09 | - | 1.7 | 18 | 20 | 0.123 | 6.5e-11 |
| P05-fe | accel_ic/gmres | max_it | 10000 | 5.2e-04 | - | 1.8 | 143 | 145 | 0.417 | 3.4e-03 |
| P05-fe | accel_ic/cocg | converged | 5185 | 9.0e-09 | - | 1.8 | 14 | 17 | 0.104 | 8.0e-11 |
| P05-fe | cslp/gmres | converged | 187 | 9.8e-09 | - | 2.5 | 16 | 19 | 0.443 | 6.0e-10 |
| P05-fe | hx/gmres | converged | 43 | 9.6e-09 | - | 2.8 | 3.6 | 7.1 | 0.546 | 6.0e-10 |
| P05-fe | cslp_hx/gmres | converged | 28 | 6.0e-09 | - | 2.6 | 2.4 | 5.7 | 0.452 | 2.9e-09 |
| P05-fe | npatch_asm/cocg | converged | 426 | 9.3e-09 | - | 2.5 | 1.8 | 4.9 | 0.218 | 1.0e-12 |
| P05-fe | mumps/direct | converged | 1 | 4.9e-13 | - | 2.1 | 0.0 | 2.9 | 0.155 | - |
| P05-n1 | gs/gmres | converged | 866 | 9.2e-09 | - | 1.0 | 3.2 | 4.9 | 0.143 | 3.9e-08 |
| P05-n1 | ssor/gmres | converged | 244 | 9.5e-09 | - | 1.0 | 0.8 | 2.5 | 0.128 | 1.5e-10 |
| P05-n1 | ssor/cocg | converged | 270 | 9.2e-09 | - | 1.0 | 0.5 | 2.2 | 0.062 | 6.3e-12 |
| P05-n1 | amg_gamg/gmres | converged | 226 | 8.3e-09 | - | 1.1 | 0.9 | 2.7 | 0.125 | 7.6e-10 |
| P05-n1 | amg_gamg/cocg | converged | 251 | 8.7e-09 | - | 1.0 | 0.8 | 2.5 | 0.075 | 3.2e-12 |
| P05-n1 | accel_ic/gmres | converged | 305 | 9.9e-09 | - | 1.0 | 2.6 | 4.3 | 0.257 | 1.1e-09 |
| P05-n1 | accel_ic/cocg | converged | 347 | 6.6e-09 | - | 1.0 | 0.6 | 2.3 | 0.066 | 2.2e-12 |
| P05-n1 | cslp/gmres | converged | 26 | 7.2e-09 | - | 1.4 | 1.2 | 3.3 | 0.274 | 1.5e-10 |
| P05-n1 | hx/gmres | max_it | 10000 | nan | - | 1.8 | 178 | 181 | 0.341 | nan |
| P05-n1 | cslp_hx/gmres | converged | 26 | 7.2e-09 | - | 1.6 | 1.2 | 3.5 | 0.279 | 1.5e-10 |
| P05-n1 | npatch_asm/cocg | converged | 443 | 1.0e-08 | - | 1.4 | 0.7 | 2.8 | 0.093 | 4.1e-12 |
| P05-n1 | mumps/direct | converged | 1 | 5.4e-13 | - | 1.2 | 0.0 | 1.9 | 0.052 | - |
| P05-n4 | gs/gmres | max_it | 10000 | 1.9e-02 | - | 3.3 | 116 | 120 | 0.398 | 2.1e-01 |
| P05-n4 | ssor/gmres | max_it | 10000 | 7.6e-03 | - | 3.3 | 124 | 128 | 0.398 | 7.0e-02 |
| P05-n4 | ssor/cocg | converged | 6345 | 9.3e-09 | - | 3.3 | 39 | 43 | 0.167 | 1.3e-10 |
| P05-n4 | amg_gamg/gmres | max_it | 10000 | 7.3e-04 | - | 3.5 | 160 | 165 | 0.424 | 5.3e-03 |
| P05-n4 | amg_gamg/cocg | converged | 5940 | 7.2e-09 | - | 3.3 | 59 | 63 | 0.23 | 1.8e-10 |
| P05-n4 | accel_ic/gmres | max_it | 10000 | 5.1e-03 | - | 3.3 | 260 | 264 | 0.769 | 7.0e-02 |
| P05-n4 | accel_ic/cocg | converged | 7988 | 5.9e-09 | - | 3.3 | 42 | 46 | 0.191 | 7.6e-12 |
| P05-n4 | cslp/gmres | converged | 413 | 9.8e-09 | - | 4.5 | 70 | 75 | 0.854 | 6.8e-09 |
| P05-n4 | hx/gmres | converged | 43 | 8.6e-09 | - | 5.3 | 6.3 | 12 | 1.025 | 6.9e-11 |
| P05-n4 | cslp_hx/gmres | converged | 37 | 9.7e-09 | - | 4.9 | 6.1 | 12 | 0.87 | 1.7e-08 |
| P05-n4 | npatch_asm/cocg | converged | 400 | 6.6e-09 | - | 4.8 | 3.7 | 9.2 | 0.489 | 1.3e-10 |
| P05-n4 | mumps/direct | converged | 1 | 5.8e-13 | - | 4.4 | 0.0 | 5.2 | 0.518 | - |
| P05-td1e-4 | gs/gmres | max_it | 10000 | 1.9e-02 | - | 1.8 | 63 | 66 | 0.224 | 2.2e-01 |
| P05-td1e-4 | ssor/gmres | max_it | 10000 | 2.2e-04 | - | 1.8 | 68 | 70 | 0.224 | 1.8e-03 |
| P05-td1e-4 | ssor/cocg | converged | 3731 | 6.0e-09 | - | 1.8 | 12 | 15 | 0.094 | 1.7e-11 |
| P05-td1e-4 | amg_gamg/gmres | max_it | 10000 | 1.8e-06 | - | 1.9 | 86 | 89 | 0.236 | 6.0e-06 |
| P05-td1e-4 | amg_gamg/cocg | converged | 3347 | 8.2e-09 | - | 1.8 | 17 | 20 | 0.125 | 6.7e-10 |
| P05-td1e-4 | accel_ic/gmres | max_it | 10000 | 4.0e-03 | - | 1.8 | 144 | 146 | 0.426 | 5.6e-02 |
| P05-td1e-4 | accel_ic/cocg | converged | 4423 | 9.2e-09 | - | 1.8 | 12 | 15 | 0.104 | 4.4e-11 |
| P05-td1e-4 | cslp/gmres | converged | 178 | 9.8e-09 | - | 2.5 | 15 | 18 | 0.453 | 5.4e-10 |
| P05-td1e-4 | hx/gmres | converged | 44 | 8.0e-09 | - | 2.9 | 3.6 | 7.2 | 0.555 | 6.5e-10 |
| P05-td1e-4 | cslp_hx/gmres | converged | 28 | 7.4e-09 | - | 2.6 | 2.4 | 5.8 | 0.464 | 1.2e-09 |
| P05-td1e-4 | npatch_asm/cocg | converged | 429 | 8.6e-09 | - | 2.5 | 1.9 | 5.0 | 0.216 | 1.0e-12 |
| P05-td1e-4 | mumps/direct | converged | 1 | 5.6e-13 | - | 2.2 | 0.0 | 3.0 | 0.123 | - |
| P05-td1e-2 | gs/gmres | max_it | 10000 | 5.9e-03 | - | 1.8 | 63 | 66 | 0.224 | 3.9e-02 |
| P05-td1e-2 | ssor/gmres | max_it | 10000 | 1.1e-04 | - | 1.8 | 68 | 70 | 0.224 | 4.2e-04 |
| P05-td1e-2 | ssor/cocg | converged | 4016 | 9.0e-09 | - | 1.8 | 13 | 16 | 0.097 | 5.8e-11 |
| P05-td1e-2 | amg_gamg/gmres | max_it | 10000 | 4.5e-06 | - | 1.9 | 86 | 89 | 0.236 | 1.2e-05 |
| P05-td1e-2 | amg_gamg/cocg | converged | 3883 | 6.4e-09 | - | 1.8 | 20 | 22 | 0.125 | 2.2e-12 |
| P05-td1e-2 | accel_ic/gmres | max_it | 10000 | 9.3e-04 | - | 1.8 | 144 | 147 | 0.426 | 7.8e-03 |
| P05-td1e-2 | accel_ic/cocg | converged | 4711 | 5.5e-09 | - | 1.8 | 13 | 16 | 0.104 | 2.7e-11 |
| P05-td1e-2 | cslp/gmres | converged | 189 | 9.7e-09 | - | 2.5 | 16 | 19 | 0.454 | 5.4e-10 |
| P05-td1e-2 | hx/gmres | converged | 44 | 7.4e-09 | - | 2.9 | 3.6 | 7.2 | 0.555 | 5.1e-10 |
| P05-td1e-2 | cslp_hx/gmres | converged | 28 | 8.6e-09 | - | 2.7 | 2.4 | 5.8 | 0.464 | 1.5e-09 |
| P05-td1e-2 | npatch_asm/cocg | converged | 429 | 7.8e-09 | - | 2.5 | 1.8 | 5.0 | 0.216 | 1.4e-12 |
| P05-td1e-2 | mumps/direct | converged | 1 | 5.2e-13 | - | 2.2 | 0.0 | 2.9 | 0.141 | - |
| P05-lc1.25 | gs/gmres | max_it | 10000 | 1.8e-02 | - | 6.0 | 228 | 237 | 0.74 | 1.9e-01 |
| P05-lc1.25 | ssor/gmres | max_it | 10000 | 7.9e-03 | - | 6.0 | 244 | 252 | 0.74 | 1.5e-01 |
| P05-lc1.25 | ssor/cocg | converged | 4270 | 7.5e-09 | - | 6.0 | 50 | 59 | 0.273 | 1.7e-10 |
| P05-lc1.25 | amg_gamg/gmres | max_it | 10000 | 3.6e-03 | - | 6.5 | 314 | 323 | 0.788 | 8.9e-02 |
| P05-lc1.25 | amg_gamg/cocg | converged | 3559 | 8.7e-09 | - | 6.0 | 67 | 76 | 0.388 | 1.7e-11 |
| P05-lc1.25 | accel_ic/gmres | max_it | 10000 | 9.2e-03 | - | 6.1 | 502 | 511 | 1.447 | 2.0e-01 |
| P05-lc1.25 | accel_ic/cocg | converged | 4944 | 6.1e-09 | - | 6.1 | 50 | 59 | 0.329 | 1.1e-10 |
| P05-lc1.25 | cslp/gmres | converged | 183 | 9.6e-09 | - | 8.5 | 59 | 70 | 1.583 | 2.5e-10 |
| P05-lc1.25 | hx/gmres | converged | 43 | 5.3e-09 | - | 10 | 13 | 26 | 1.898 | 6.7e-10 |
| P05-lc1.25 | cslp_hx/gmres | converged | 33 | 7.2e-09 | - | 9.3 | 11 | 22 | 1.605 | 2.1e-09 |
| P05-lc1.25 | npatch_asm/cocg | converged | 823 | 9.8e-09 | - | 8.7 | 12 | 23 | 0.744 | 1.0e-12 |
| P05-lc1.25 | mumps/direct | converged | 1 | 1.1e-12 | - | 7.7 | 0.1 | 10 | 0.791 | - |
| P05-lc0.625 | gs/gmres | max_it | 10000 | 1.1e-02 | - | 24 | 889 | 922 | 2.827 | 4.6e-01 |
| P05-lc0.625 | ssor/gmres | max_it | 10000 | 1.0e-02 | - | 23 | 949 | 982 | 2.827 | 4.7e-01 |
| P05-lc0.625 | ssor/cocg | converged | 4559 | 2.6e-09 | - | 24 | 209 | 243 | 1.023 | 4.8e-09 |
| P05-lc0.625 | amg_gamg/gmres | max_it | 10000 | 8.0e-03 | - | 25 | 1268 | 1303 | 2.986 | 4.3e-01 |
| P05-lc0.625 | amg_gamg/cocg | converged | 3864 | 9.0e-09 | - | 23 | 302 | 335 | 1.468 | 3.0e-10 |
| P05-lc0.625 | accel_ic/gmres | max_it | 10000 | 8.2e-03 | - | 24 | 1952 | 1985 | 5.567 | 4.9e-01 |
| P05-lc0.625 | accel_ic/cocg | converged | 5357 | 9.9e-09 | - | 23 | 217 | 251 | 1.236 | 1.2e-10 |
| P05-lc0.625 | cslp/gmres | converged | 169 | 8.8e-09 | - | 33 | 228 | 272 | 6.054 | 9.6e-10 |
| P05-lc0.625 | hx/gmres | converged | 64 | 6.9e-09 | - | 41 | 81 | 132 | 7.276 | 1.3e-08 |
| P05-lc0.625 | cslp_hx/gmres | converged | 57 | 5.5e-09 | - | 36 | 77 | 123 | 6.142 | 3.3e-09 |
| P05-lc0.625 | npatch_asm/cocg | converged | 1600 | 8.9e-09 | - | 34 | 97 | 141 | 2.784 | 1.6e-11 |
| P05-lc0.625 | mumps/direct | converged | 1 | 2.3e-12 | - | 31 | 0.3 | 42 | 3.357 | - |
| P06-L0 | gs/gmres | max_it | 10000 | 2.0e-02 | - | 15 | 517 | 533 | 1.644 | 1.2e-01 |
| P06-L0 | ssor/gmres | max_it | 10000 | 5.5e-03 | - | 15 | 553 | 569 | 1.645 | 1.0e-02 |
| P06-L0 | ssor/cocg | converged | 18324 | 6.5e-09 | - | 15 | 524 | 540 | 0.666 | 2.9e-10 |
| P06-L0 | amg_gamg/gmres | max_it | 10000 | 1.0e-02 | - | 17 | 766 | 784 | 1.831 | 8.4e-02 |
| P06-L0 | amg_gamg/cocg | converged | 23581 | 7.0e-09 | - | 15 | 1159 | 1176 | 0.959 | 1.4e-09 |
| P06-L0 | accel_ic/gmres | max_it | 10000 | 7.2e-03 | - | 15 | 1115 | 1132 | 3.218 | 4.5e-02 |
| P06-L0 | accel_ic/cocg | converged | 21879 | 5.4e-09 | - | 15 | 555 | 571 | 0.8 | 7.8e-10 |
| P06-L0 | cslp/gmres | converged | 1130 | 9.9e-09 | - | 21 | 1007 | 1029 | 3.576 | 1.3e-07 |
| P06-L0 | hx/gmres | converged | 137 | 9.3e-09 | - | 25 | 59 | 86 | 4.172 | 4.9e-10 |
| P06-L0 | cslp_hx/gmres | converged | 135 | 9.1e-09 | - | 23 | 119 | 143 | 3.617 | 5.8e-09 |
| P06-L0 | npatch_asm/cocg | converged | 882 | 5.3e-09 | - | 22 | 40 | 64 | 2.295 | 5.1e-11 |
| P06-L0 | mumps/direct | converged | 1 | 4.5e-13 | - | 28 | 0.4 | 30 | 4.811 | - |
| P06-L10 | gs/gmres | max_it | 10000 | 1.9e-02 | - | 17 | 562 | 580 | 1.802 | 7.1e-02 |
| P06-L10 | ssor/gmres | max_it | 10000 | 2.4e-03 | - | 16 | 602 | 620 | 1.802 | 9.4e-03 |
| P06-L10 | ssor/cocg | converged | 17353 | 4.7e-09 | - | 17 | 546 | 564 | 0.734 | 3.4e-09 |
| P06-L10 | amg_gamg/gmres | max_it | 10000 | 1.1e-02 | - | 18 | 841 | 860 | 2.008 | 5.8e-02 |
| P06-L10 | amg_gamg/cocg | converged | 29718 | 9.9e-09 | - | 16 | 1609 | 1627 | 1.047 | 9.2e-09 |
| P06-L10 | accel_ic/gmres | max_it | 10000 | 4.2e-03 | - | 17 | 1225 | 1243 | 3.526 | 3.3e-02 |
| P06-L10 | accel_ic/cocg | converged | 21215 | 7.9e-09 | - | 16 | 588 | 606 | 0.88 | 1.4e-09 |
| P06-L10 | cslp/gmres | converged | 1894 | 1.0e-08 | - | 23 | 1864 | 1888 | 3.891 | 1.0e-07 |
| P06-L10 | hx/gmres | converged | 2725 | 9.9e-09 | - | 28 | 1183 | 1212 | 4.659 | 1.0e-09 |
| P06-L10 | cslp_hx/gmres | converged | 304 | 9.2e-09 | - | 25 | 311 | 337 | 3.941 | 8.0e-09 |
| P06-L10 | npatch_asm/cocg | converged | 2187 | 8.9e-09 | - | 25 | 111 | 137 | 2.523 | 3.4e-10 |
| P06-L10 | mumps/direct | converged | 1 | 1.5e-13 | - | 31 | 0.5 | 33 | 5.342 | - |
| P06-L30 | gs/gmres | max_it | 10000 | 2.7e-02 | - | 20 | 672 | 693 | 2.145 | 2.7e-01 |
| P06-L30 | ssor/gmres | max_it | 10000 | 8.0e-03 | - | 20 | 720 | 741 | 2.145 | 3.2e-02 |
| P06-L30 | ssor/cocg | converged | 22609 | 9.8e-09 | - | 20 | 852 | 874 | 0.866 | 8.4e-10 |
| P06-L30 | amg_gamg/gmres | max_it | 10000 | 1.4e-02 | - | 21 | 1013 | 1036 | 2.384 | 1.1e-01 |
| P06-L30 | amg_gamg/cocg | converged | 32975 | 9.7e-09 | - | 20 | 2168 | 2189 | 1.245 | 2.8e-09 |
| P06-L30 | accel_ic/gmres | max_it | 10000 | 1.1e-02 | - | 20 | 1462 | 1483 | 4.197 | 9.6e-02 |
| P06-L30 | accel_ic/cocg | converged | 28954 | 6.4e-09 | - | 20 | 960 | 981 | 1.042 | 1.1e-09 |
| P06-L30 | cslp/gmres | converged | 1379 | 1.0e-08 | - | 27 | 1659 | 1688 | 4.675 | 1.2e-07 |
| P06-L30 | hx/gmres | converged | 154 | 9.6e-09 | - | 34 | 92 | 127 | 5.466 | 3.4e-10 |
| P06-L30 | cslp_hx/gmres | converged | 169 | 9.7e-09 | - | 29 | 205 | 235 | 4.734 | 2.9e-09 |
| P06-L30 | npatch_asm/cocg | converged | 1107 | 3.4e-09 | - | 29 | 68 | 99 | 3.006 | 1.1e-10 |
| P06-L30 | mumps/direct | converged | 1 | 5.3e-13 | - | 37 | 0.6 | 39 | 6.134 | - |
| P06-L30_s2 | gs/gmres | max_it | 10000 | 2.2e-02 | - | 20 | 678 | 699 | 2.145 | 1.7e-01 |
| P06-L30_s2 | ssor/gmres | max_it | 10000 | 6.5e-03 | - | 20 | 725 | 747 | 2.145 | 3.3e-02 |
| P06-L30_s2 | ssor/cocg | converged | 20943 | 4.7e-09 | - | 20 | 789 | 811 | 0.866 | 1.3e-10 |
| P06-L30_s2 | amg_gamg/gmres | max_it | 10000 | 1.1e-02 | - | 22 | 1019 | 1043 | 2.383 | 9.0e-02 |
| P06-L30_s2 | amg_gamg/cocg | converged | 27767 | 9.8e-09 | - | 20 | 1833 | 1855 | 1.244 | 5.1e-10 |
| P06-L30_s2 | accel_ic/gmres | max_it | 10000 | 7.8e-03 | - | 21 | 1462 | 1485 | 4.197 | 6.0e-02 |
| P06-L30_s2 | accel_ic/cocg | converged | 25771 | 8.4e-09 | - | 20 | 867 | 889 | 1.041 | 2.7e-10 |
| P06-L30_s2 | cslp/gmres | converged | 1175 | 9.9e-09 | - | 28 | 1417 | 1447 | 4.638 | 9.6e-08 |
| P06-L30_s2 | hx/gmres | converged | 147 | 7.8e-09 | - | 34 | 87 | 122 | 5.528 | 5.5e-10 |
| P06-L30_s2 | cslp_hx/gmres | converged | 161 | 9.5e-09 | - | 30 | 195 | 227 | 4.703 | 2.1e-09 |
| P06-L30_s2 | npatch_asm/cocg | converged | 1019 | 1.0e-08 | - | 30 | 62 | 93 | 3.005 | 5.0e-11 |
| P06-L30_s2 | mumps/direct | converged | 1 | 4.6e-13 | - | 38 | 0.6 | 40 | 6.368 | - |
| P07-1 | gs/gmres | max_it | 10000 | 2.5e-02 | - | 21 | 700 | 723 | 2.238 | 6.0e-01 |
| P07-1 | ssor/gmres | max_it | 10000 | 1.8e-02 | - | 21 | 747 | 770 | 2.238 | 4.2e-01 |
| P07-1 | ssor/cocg | max_it | 50000 | 6.6e-02 | - | 21 | 1959 | 1982 | 0.904 | 1.4e-05 |
| P07-1 | amg_gamg/gmres | max_it | 10000 | 1.6e-02 | - | 23 | 1040 | 1065 | 2.489 | 4.2e-01 |
| P07-1 | amg_gamg/cocg | max_it | 50000 | 1.8e+02 | - | 21 | 3374 | 3397 | 1.301 | 7.2e-04 |
| P07-1 | accel_ic/gmres | max_it | 10000 | 1.7e-02 | - | 21 | 1514 | 1537 | 4.38 | 4.8e-01 |
| P07-1 | accel_ic/cocg | max_it | 50000 | 4.6e-01 | - | 21 | 1687 | 1710 | 1.088 | 1.9e-05 |
| P07-1 | cslp/gmres | max_it | 3000 | 1.2e-03 | - | 29 | 3680 | 3711 | 4.84 | 1.1e-02 |
| P07-1 | hx/gmres | converged | 902 | 9.2e-09 | - | 35 | 884 | 922 | 5.921 | 4.0e-09 |
| P07-1 | cslp_hx/gmres | converged | 173 | 6.4e-09 | - | 31 | 215 | 248 | 4.918 | 2.6e-09 |
| P07-1 | npatch_asm/cocg | converged | 1331 | 3.3e-09 | - | 32 | 87 | 122 | 3.189 | 1.3e-11 |
| P07-1 | mumps/direct | converged | 1 | 5.5e-12 | - | 40 | 0.6 | 43 | 6.788 | - |
| P07-4 | gs/gmres | max_it | 10000 | 4.8e-02 | - | 21 | 702 | 725 | 2.234 | 6.0e-01 |
| P07-4 | ssor/gmres | max_it | 10000 | 3.4e-02 | - | 20 | 749 | 772 | 2.234 | 3.8e-01 |
| P07-4 | ssor/cocg | max_it | 50000 | 7.7e-03 | - | 21 | 1956 | 1979 | 0.903 | 2.2e-05 |
| P07-4 | amg_gamg/gmres | max_it | 10000 | 2.8e-02 | - | 23 | 1041 | 1066 | 2.485 | 3.9e-01 |
| P07-4 | amg_gamg/cocg | max_it | 50000 | 1.0e-02 | - | 21 | 3359 | 3382 | 1.299 | 5.2e-05 |
| P07-4 | accel_ic/gmres | max_it | 10000 | 2.8e-02 | - | 21 | 1511 | 1534 | 4.37 | 3.8e-01 |
| P07-4 | accel_ic/cocg | max_it | 50000 | 4.0e-02 | - | 21 | 1687 | 1711 | 1.086 | 1.3e-04 |
| P07-4 | cslp/gmres | max_it | 3000 | 1.7e-04 | - | 29 | 3681 | 3713 | 4.829 | 1.3e-03 |
| P07-4 | hx/gmres | converged | 2063 | 1.0e-08 | - | 35 | 1448 | 1485 | 5.955 | 1.9e-08 |
| P07-4 | cslp_hx/gmres | max_it | 1000 | 1.3e-06 | - | 31 | 1257 | 1291 | 4.907 | 1.6e-05 |
| P07-4 | npatch_asm/cocg | converged | 2646 | 9.3e-09 | - | 31 | 167 | 201 | 3.184 | 1.1e-10 |
| P07-4 | mumps/direct | converged | 1 | 5.2e-13 | - | 40 | 0.6 | 44 | 6.693 | - |
| P08-N2_s1 | gs/gmres | max_it | 10000 | 5.7e-05 | - | 6.0 | 209 | 216 | 0.679 | 1.5e-04 |
| P08-N2_s1 | ssor/gmres | max_it | 10000 | 4.1e-07 | - | 5.9 | 223 | 230 | 0.678 | 8.7e-07 |
| P08-N2_s1 | ssor/cocg | converged | 6280 | 6.7e-09 | - | 6.0 | 71 | 78 | 0.286 | 1.1e-09 |
| P08-N2_s1 | amg_gamg/gmres | max_it | 10000 | 1.5e-06 | - | 6.4 | 300 | 307 | 0.746 | 4.1e-06 |
| P08-N2_s1 | amg_gamg/cocg | converged | 7235 | 1.0e-08 | - | 6.0 | 138 | 145 | 0.401 | 1.6e-09 |
| P08-N2_s1 | accel_ic/gmres | max_it | 10000 | 1.8e-06 | - | 5.9 | 452 | 458 | 1.317 | 5.8e-06 |
| P08-N2_s1 | accel_ic/cocg | converged | 7286 | 4.3e-09 | - | 6.0 | 72 | 79 | 0.325 | 2.0e-10 |
| P08-N2_s1 | cslp/gmres | converged | 241 | 9.7e-09 | - | 8.2 | 81 | 90 | 1.473 | 8.6e-09 |
| P08-N2_s1 | hx/gmres | converged | 113 | 8.6e-09 | - | 9.8 | 18 | 29 | 1.74 | 4.1e-10 |
| P08-N2_s1 | cslp_hx/gmres | converged | 107 | 7.7e-09 | - | 8.7 | 36 | 45 | 1.491 | 2.5e-09 |
| P08-N2_s1 | npatch_asm/cocg | converged | 623 | 7.3e-09 | - | 8.7 | 12 | 21 | 0.923 | 2.7e-10 |
| P08-N2_s1 | mumps/direct | converged | 1 | 8.3e-14 | - | 9.4 | 0.1 | 10 | 1.544 | - |
| P08-N4_s1 | gs/gmres | max_it | 10000 | 6.2e-05 | - | 10 | 365 | 377 | 1.175 | 1.4e-04 |
| P08-N4_s1 | ssor/gmres | max_it | 10000 | 5.9e-07 | - | 10 | 390 | 401 | 1.175 | 1.1e-06 |
| P08-N4_s1 | ssor/cocg | converged | 8277 | 7.5e-09 | - | 10 | 166 | 177 | 0.48 | 2.6e-09 |
| P08-N4_s1 | amg_gamg/gmres | max_it | 10000 | 3.5e-06 | - | 11 | 531 | 543 | 1.291 | 7.3e-06 |
| P08-N4_s1 | amg_gamg/cocg | converged | 10782 | 9.1e-09 | - | 10 | 368 | 379 | 0.695 | 1.3e-09 |
| P08-N4_s1 | accel_ic/gmres | max_it | 10000 | 2.1e-06 | - | 11 | 792 | 804 | 2.274 | 5.2e-06 |
| P08-N4_s1 | accel_ic/cocg | converged | 10369 | 6.5e-09 | - | 10 | 182 | 194 | 0.55 | 6.9e-11 |
| P08-N4_s1 | cslp/gmres | converged | 391 | 9.6e-09 | - | 15 | 238 | 254 | 2.532 | 4.5e-08 |
| P08-N4_s1 | hx/gmres | converged | 175 | 9.3e-09 | - | 17 | 54 | 72 | 3.001 | 1.8e-09 |
| P08-N4_s1 | cslp_hx/gmres | converged | 182 | 9.5e-09 | - | 15 | 112 | 128 | 2.575 | 7.9e-09 |
| P08-N4_s1 | npatch_asm/cocg | converged | 1027 | 6.9e-09 | - | 16 | 33 | 50 | 1.639 | 1.8e-10 |
| P08-N4_s1 | mumps/direct | converged | 1 | 8.6e-14 | - | 18 | 0.2 | 19 | 3.314 | - |
| P08-N8_s1 | gs/gmres | max_it | 10000 | 7.4e-05 | - | 20 | 683 | 705 | 2.175 | 1.5e-04 |
| P08-N8_s1 | ssor/gmres | max_it | 10000 | 1.1e-06 | - | 19 | 731 | 753 | 2.175 | 1.7e-06 |
| P08-N8_s1 | ssor/cocg | converged | 9824 | 9.8e-09 | - | 19 | 370 | 392 | 0.882 | 2.0e-09 |
| P08-N8_s1 | amg_gamg/gmres | max_it | 10000 | 3.7e-06 | - | 21 | 1021 | 1045 | 2.393 | 7.8e-06 |
| P08-N8_s1 | amg_gamg/cocg | converged | 12026 | 8.2e-09 | - | 19 | 795 | 817 | 1.256 | 2.9e-09 |
| P08-N8_s1 | accel_ic/gmres | max_it | 10000 | 2.5e-06 | - | 20 | 1478 | 1500 | 4.214 | 5.5e-06 |
| P08-N8_s1 | accel_ic/cocg | converged | 11379 | 7.6e-09 | - | 20 | 383 | 405 | 1.013 | 6.4e-09 |
| P08-N8_s1 | cslp/gmres | converged | 432 | 9.9e-09 | - | 27 | 518 | 548 | 4.706 | 3.9e-08 |
| P08-N8_s1 | hx/gmres | converged | 255 | 8.5e-09 | - | 33 | 158 | 194 | 5.719 | 7.0e-09 |
| P08-N8_s1 | cslp_hx/gmres | converged | 226 | 9.1e-09 | - | 29 | 279 | 310 | 4.78 | 4.3e-08 |
| P08-N8_s1 | npatch_asm/cocg | converged | 1647 | 9.2e-09 | - | 29 | 98 | 130 | 3.01 | 5.7e-10 |
| P08-N8_s1 | mumps/direct | converged | 1 | 8.3e-14 | - | 36 | 0.6 | 40 | 6.616 | - |
| case1A:standard | gs/gmres | max_it | 10000 | 1.1e-03 | - | 4.9 | 163 | 170 | 0.529 | - |
| case1A:standard | ssor/gmres | max_it | 10000 | 6.6e-04 | - | 4.8 | 174 | 181 | 0.529 | - |
| case1A:standard | ssor/cocg | converged | 16749 | 1.0e-08 | - | 4.9 | 146 | 153 | 0.22 | - |
| case1A:standard | amg_gamg/gmres | max_it | 10000 | 4.4e-01 | - | 5.2 | 234 | 241 | 0.577 | - |
| case1A:standard | amg_gamg/cocg | max_it | 50000 | 8.9e-01 | - | 4.9 | 738 | 745 | 0.305 | - |
| case1A:standard | accel_ic/gmres | max_it | 10000 | 8.2e-06 | - | 4.9 | 353 | 360 | 1.02 | - |
| case1A:standard | accel_ic/cocg | converged | 10858 | 8.5e-09 | - | 4.8 | 82 | 90 | 0.25 | - |
| case1A:standard | cslp/gmres | max_it | 3000 | 1.5e-01 | - | 6.6 | 801 | 810 | 1.13 | - |
| case1A:standard | hx/gmres | converged | 2387 | 1.0e-08 | - | 7.7 | 262 | 272 | 1.359 | - |
| case1A:standard | cslp_hx/gmres | max_it | 1000 | 2.1e-01 | - | 7.0 | 282 | 292 | 1.144 | - |
| case1A:standard | npatch_asm/cocg | converged | 1028 | 8.7e-09 | - | 7.0 | 15 | 24 | 0.714 | - |
| case1A:standard | mumps/direct | converged | 1 | 9.1e-14 | - | 7.7 | 0.1 | 10 | 1.44 | - |
| case1A:high_freq | gs/gmres | max_it | 10000 | 3.7e-03 | - | 7.7 | 244 | 255 | 0.789 | - |
| case1A:high_freq | ssor/gmres | max_it | 10000 | 3.1e-03 | - | 7.6 | 261 | 271 | 0.789 | - |
| case1A:high_freq | ssor/cocg | converged | 23811 | 9.3e-09 | - | 7.5 | 314 | 325 | 0.329 | - |
| case1A:high_freq | amg_gamg/gmres | max_it | 10000 | 4.9e-01 | - | 8.2 | 353 | 365 | 0.868 | - |
| case1A:high_freq | amg_gamg/cocg | max_it | 50000 | 1.4e+00 | - | 7.6 | 1125 | 1136 | 0.461 | - |
| case1A:high_freq | accel_ic/gmres | max_it | 10000 | 8.1e-05 | - | 7.8 | 529 | 540 | 1.53 | - |
| case1A:high_freq | accel_ic/cocg | converged | 13871 | 9.0e-09 | - | 7.6 | 160 | 171 | 0.376 | - |
| case1A:high_freq | cslp/gmres | max_it | 3000 | 2.4e-01 | - | 10 | 1227 | 1240 | 1.683 | - |
| case1A:high_freq | hx/gmres | converged | 2734 | 1.0e-08 | - | 12 | 448 | 463 | 1.986 | - |
| case1A:high_freq | cslp_hx/gmres | max_it | 1000 | 2.6e-01 | - | 11 | 434 | 448 | 1.708 | - |
| case1A:high_freq | npatch_asm/cocg | converged | 1136 | 8.9e-09 | - | 11 | 25 | 39 | 1.082 | - |
| case1A:high_freq | mumps/direct | converged | 1 | 9.6e-14 | - | 13 | 0.2 | 16 | 2.363 | - |
| case1A:thick_pml | gs/gmres | max_it | 10000 | 6.0e-05 | - | 7.6 | 254 | 265 | 0.818 | - |
| case1A:thick_pml | ssor/gmres | max_it | 10000 | 4.5e-04 | - | 7.7 | 270 | 281 | 0.818 | - |
| case1A:thick_pml | ssor/cocg | converged | 20624 | 9.9e-09 | - | 7.5 | 281 | 292 | 0.338 | - |
| case1A:thick_pml | amg_gamg/gmres | max_it | 10000 | 5.3e-01 | - | 8.2 | 367 | 379 | 0.896 | - |
| case1A:thick_pml | amg_gamg/cocg | max_it | 50000 | 1.1e+01 | - | 7.5 | 1168 | 1179 | 0.478 | - |
| case1A:thick_pml | accel_ic/gmres | converged | 9593 | 1.0e-08 | - | 7.6 | 526 | 537 | 1.582 | - |
| case1A:thick_pml | accel_ic/cocg | converged | 7497 | 9.0e-09 | - | 7.6 | 90 | 101 | 0.386 | - |
| case1A:thick_pml | cslp/gmres | max_it | 3000 | 4.6e-01 | - | 10 | 1274 | 1288 | 1.764 | - |
| case1A:thick_pml | hx/gmres | converged | 1896 | 9.9e-09 | - | 12 | 333 | 348 | 2.08 | - |
| case1A:thick_pml | cslp_hx/gmres | max_it | 1000 | 4.1e-01 | - | 11 | 460 | 474 | 1.78 | - |
| case1A:thick_pml | npatch_asm/cocg | converged | 955 | 8.0e-09 | - | 11 | 22 | 36 | 1.126 | - |
| case1A:thick_pml | mumps/direct | converged | 1 | 1.0e-13 | - | 13 | 0.2 | 17 | 2.52 | - |
| case1A:thin_pml | gs/gmres | max_it | 10000 | 5.6e-03 | - | 3.0 | 100 | 104 | 0.34 | - |
| case1A:thin_pml | ssor/gmres | max_it | 10000 | 1.4e-03 | - | 3.0 | 106 | 111 | 0.34 | - |
| case1A:thin_pml | ssor/cocg | converged | 17258 | 9.5e-09 | - | 3.0 | 92 | 96 | 0.142 | - |
| case1A:thin_pml | amg_gamg/gmres | max_it | 10000 | 2.5e-03 | - | 3.2 | 142 | 147 | 0.368 | - |
| case1A:thin_pml | amg_gamg/cocg | converged | 20725 | 9.7e-09 | - | 3.0 | 184 | 189 | 0.198 | - |
| case1A:thin_pml | accel_ic/gmres | max_it | 10000 | 2.2e-03 | - | 3.1 | 220 | 224 | 0.641 | - |
| case1A:thin_pml | accel_ic/cocg | converged | 18194 | 9.7e-09 | - | 3.0 | 85 | 89 | 0.163 | - |
| case1A:thin_pml | cslp/gmres | converged | 1889 | 1.0e-08 | - | 4.1 | 302 | 307 | 0.71 | - |
| case1A:thin_pml | hx/gmres | max_it | 10000 | 2.1e-01 | - | 4.7 | 640 | 646 | 0.858 | - |
| case1A:thin_pml | cslp_hx/gmres | converged | 644 | 9.6e-09 | - | 4.3 | 110 | 116 | 0.725 | - |
| case1A:thin_pml | npatch_asm/cocg | converged | 896 | 1.0e-08 | - | 4.3 | 7.8 | 14 | 0.44 | - |
| case1A:thin_pml | mumps/direct | converged | 1 | 1.1e-13 | - | 4.4 | 0.1 | 5.9 | 0.727 | - |
| case1B:mie_low_eps | gs/gmres | max_it | 10000 | 2.8e-02 | - | 3.5 | 116 | 121 | 0.388 | - |
| case1B:mie_low_eps | ssor/gmres | max_it | 10000 | 3.4e-02 | - | 3.5 | 123 | 128 | 0.388 | - |
| case1B:mie_low_eps | ssor/cocg | converged | 15592 | 9.1e-09 | - | 3.6 | 97 | 103 | 0.158 | - |
| case1B:mie_low_eps | amg_gamg/gmres | max_it | 10000 | 4.5e-01 | - | 3.8 | 166 | 171 | 0.424 | - |
| case1B:mie_low_eps | amg_gamg/cocg | max_it | 50000 | 7.1e-01 | - | 3.5 | 525 | 530 | 0.224 | - |
| case1B:mie_low_eps | accel_ic/gmres | max_it | 10000 | 3.1e-03 | - | 3.6 | 256 | 261 | 0.743 | - |
| case1B:mie_low_eps | accel_ic/cocg | converged | 10196 | 8.4e-09 | - | 3.5 | 56 | 61 | 0.184 | - |
| case1B:mie_low_eps | cslp/gmres | max_it | 3000 | 5.7e-02 | - | 4.8 | 564 | 570 | 0.822 | - |
| case1B:mie_low_eps | hx/gmres | converged | 3250 | 9.9e-09 | - | 5.5 | 248 | 255 | 0.975 | - |
| case1B:mie_low_eps | cslp_hx/gmres | max_it | 1000 | 3.8e-02 | - | 5.1 | 199 | 206 | 0.836 | - |
| case1B:mie_low_eps | npatch_asm/cocg | converged | 2002 | 9.4e-09 | - | 5.1 | 20 | 27 | 0.518 | - |
| case1B:mie_low_eps | mumps/direct | converged | 1 | 7.3e-13 | - | 5.3 | 0.1 | 7.0 | 0.988 | - |
| case1B:mie_mid_eps | gs/gmres | max_it | 10000 | 1.4e-01 | - | 4.2 | 135 | 141 | 0.456 | - |
| case1B:mie_mid_eps | ssor/gmres | max_it | 10000 | 1.4e-01 | - | 4.2 | 144 | 150 | 0.456 | - |
| case1B:mie_mid_eps | ssor/cocg | converged | 34740 | 9.6e-09 | - | 4.1 | 255 | 261 | 0.191 | - |
| case1B:mie_mid_eps | amg_gamg/gmres | max_it | 10000 | 4.6e-01 | - | 4.4 | 195 | 201 | 0.492 | - |
| case1B:mie_mid_eps | amg_gamg/cocg | max_it | 50000 | 6.0e+00 | - | 4.2 | 620 | 626 | 0.267 | - |
| case1B:mie_mid_eps | accel_ic/gmres | max_it | 10000 | 8.5e-02 | - | 4.1 | 298 | 304 | 0.87 | - |
| case1B:mie_mid_eps | accel_ic/cocg | converged | 22832 | 9.8e-09 | - | 4.2 | 146 | 152 | 0.216 | - |
| case1B:mie_mid_eps | cslp/gmres | max_it | 3000 | 1.4e-01 | - | 5.6 | 669 | 676 | 0.966 | - |
| case1B:mie_mid_eps | hx/gmres | converged | 3836 | 1.0e-08 | - | 6.5 | 344 | 352 | 1.152 | - |
| case1B:mie_mid_eps | cslp_hx/gmres | max_it | 1000 | 1.0e-01 | - | 6.0 | 236 | 244 | 0.977 | - |
| case1B:mie_mid_eps | npatch_asm/cocg | converged | 6231 | 9.8e-09 | - | 5.9 | 74 | 82 | 0.617 | - |
| case1B:mie_mid_eps | mumps/direct | converged | 1 | 9.2e-13 | - | 6.2 | 0.1 | 8.2 | 1.038 | - |
| case1B:mie_high_eps | gs/gmres | max_it | 10000 | 1.6e-01 | - | 4.8 | 155 | 162 | 0.516 | - |
| case1B:mie_high_eps | ssor/gmres | max_it | 10000 | 1.6e-01 | - | 4.7 | 166 | 173 | 0.516 | - |
| case1B:mie_high_eps | ssor/cocg | max_it | 50000 | 2.4e-07 | - | 4.7 | 423 | 430 | 0.216 | - |
| case1B:mie_high_eps | amg_gamg/gmres | max_it | 10000 | 4.2e-01 | - | 5.1 | 225 | 232 | 0.563 | - |
| case1B:mie_high_eps | amg_gamg/cocg | max_it | 50000 | 1.0e+01 | - | 4.8 | 714 | 721 | 0.302 | - |
| case1B:mie_high_eps | accel_ic/gmres | max_it | 10000 | 1.1e-01 | - | 4.8 | 340 | 347 | 0.99 | - |
| case1B:mie_high_eps | accel_ic/cocg | converged | 34022 | 9.8e-09 | - | 4.8 | 251 | 258 | 0.248 | - |
| case1B:mie_high_eps | cslp/gmres | max_it | 3000 | 2.2e-01 | - | 6.5 | 770 | 778 | 1.1 | - |
| case1B:mie_high_eps | hx/gmres | max_it | 10000 | 3.5e-08 | - | 7.4 | 1042 | 1052 | 1.295 | - |
| case1B:mie_high_eps | cslp_hx/gmres | max_it | 1000 | 2.5e-01 | - | 6.8 | 273 | 282 | 1.118 | - |
| case1B:mie_high_eps | npatch_asm/cocg | converged | 6091 | 8.7e-09 | - | 6.9 | 85 | 94 | 0.712 | - |
| case1B:mie_high_eps | mumps/direct | converged | 1 | 1.6e-12 | - | 7.4 | 0.1 | 9.8 | 1.333 | - |
| case1B:mie_ultra_high_eps | gs/gmres | max_it | 10000 | 2.0e-01 | - | 6.1 | 201 | 210 | 0.662 | - |
| case1B:mie_ultra_high_eps | ssor/gmres | max_it | 10000 | 1.9e-01 | - | 6.1 | 214 | 223 | 0.662 | - |
| case1B:mie_ultra_high_eps | ssor/cocg | max_it | 50000 | 1.2e-03 | - | 6.2 | 548 | 557 | 0.276 | - |
| case1B:mie_ultra_high_eps | amg_gamg/gmres | max_it | 10000 | 5.4e-01 | - | 6.6 | 291 | 300 | 0.723 | - |
| case1B:mie_ultra_high_eps | amg_gamg/cocg | max_it | 50000 | 3.8e+00 | - | 6.0 | 932 | 941 | 0.388 | - |
| case1B:mie_ultra_high_eps | accel_ic/gmres | max_it | 10000 | 1.5e-01 | - | 6.3 | 438 | 447 | 1.271 | - |
| case1B:mie_ultra_high_eps | accel_ic/cocg | max_it | 50000 | 4.2e-07 | - | 6.1 | 480 | 489 | 0.315 | - |
| case1B:mie_ultra_high_eps | cslp/gmres | max_it | 3000 | 1.9e-01 | - | 8.4 | 1004 | 1015 | 1.423 | - |
| case1B:mie_ultra_high_eps | hx/gmres | max_it | 10000 | 5.2e-02 | - | 9.7 | 1433 | 1445 | 1.664 | - |
| case1B:mie_ultra_high_eps | cslp_hx/gmres | max_it | 1000 | 1.6e-01 | - | 8.9 | 360 | 372 | 1.44 | - |
| case1B:mie_ultra_high_eps | npatch_asm/cocg | converged | 15604 | 9.5e-09 | - | 8.9 | 287 | 298 | 0.892 | - |
| case1B:mie_ultra_high_eps | mumps/direct | converged | 1 | 3.0e-12 | - | 10.0 | 0.1 | 13 | 1.811 | - |
| case1C:narrow_aperture | gs/gmres | max_it | 10000 | 3.1e-03 | - | 4.7 | 157 | 164 | 0.514 | - |
| case1C:narrow_aperture | ssor/gmres | max_it | 10000 | 1.8e-03 | - | 4.7 | 167 | 174 | 0.514 | - |
| case1C:narrow_aperture | ssor/cocg | converged | 18804 | 9.5e-09 | - | 4.7 | 155 | 162 | 0.213 | - |
| case1C:narrow_aperture | amg_gamg/gmres | max_it | 10000 | 6.1e-01 | - | 5.1 | 225 | 233 | 0.56 | - |
| case1C:narrow_aperture | amg_gamg/cocg | max_it | 50000 | 1.4e+00 | - | 4.7 | 712 | 718 | 0.3 | - |
| case1C:narrow_aperture | accel_ic/gmres | max_it | 10000 | 2.3e-05 | - | 4.7 | 342 | 349 | 0.985 | - |
| case1C:narrow_aperture | accel_ic/cocg | converged | 11675 | 9.1e-09 | - | 4.7 | 86 | 93 | 0.244 | - |
| case1C:narrow_aperture | cslp/gmres | max_it | 3000 | 3.5e-01 | - | 6.3 | 772 | 781 | 1.091 | - |
| case1C:narrow_aperture | hx/gmres | converged | 3664 | 1.0e-08 | - | 7.4 | 371 | 381 | 1.305 | - |
| case1C:narrow_aperture | cslp_hx/gmres | max_it | 1000 | 2.8e-01 | - | 6.8 | 272 | 281 | 1.107 | - |
| case1C:narrow_aperture | npatch_asm/cocg | converged | 1096 | 5.7e-09 | - | 6.8 | 15 | 24 | 0.689 | - |
| case1C:narrow_aperture | mumps/direct | converged | 1 | 1.9e-13 | - | 7.2 | 0.1 | 9.5 | 1.14 | - |
| case1C:medium_aperture | gs/gmres | max_it | 10000 | 3.6e-03 | - | 4.7 | 158 | 165 | 0.517 | - |
| case1C:medium_aperture | ssor/gmres | max_it | 10000 | 1.8e-03 | - | 4.7 | 169 | 175 | 0.517 | - |
| case1C:medium_aperture | ssor/cocg | converged | 18742 | 9.8e-09 | - | 4.7 | 156 | 163 | 0.214 | - |
| case1C:medium_aperture | amg_gamg/gmres | max_it | 10000 | 5.9e-01 | - | 5.1 | 228 | 235 | 0.564 | - |
| case1C:medium_aperture | amg_gamg/cocg | max_it | 50000 | 3.1e+00 | - | 4.8 | 716 | 723 | 0.299 | - |
| case1C:medium_aperture | accel_ic/gmres | max_it | 10000 | 3.3e-05 | - | 4.8 | 344 | 351 | 0.999 | - |
| case1C:medium_aperture | accel_ic/cocg | converged | 11564 | 9.9e-09 | - | 4.8 | 85 | 92 | 0.244 | - |
| case1C:medium_aperture | cslp/gmres | max_it | 3000 | 2.0e-01 | - | 6.6 | 778 | 787 | 1.104 | - |
| case1C:medium_aperture | hx/gmres | converged | 2904 | 1.0e-08 | - | 7.5 | 294 | 303 | 1.319 | - |
| case1C:medium_aperture | cslp_hx/gmres | max_it | 1000 | 3.7e-01 | - | 6.8 | 274 | 283 | 1.118 | - |
| case1C:medium_aperture | npatch_asm/cocg | converged | 1096 | 9.1e-09 | - | 6.8 | 15 | 24 | 0.693 | - |
| case1C:medium_aperture | mumps/direct | converged | 1 | 2.0e-13 | - | 7.2 | 0.1 | 9.6 | 1.172 | - |
| case1C:wide_aperture | gs/gmres | max_it | 10000 | 6.6e-03 | - | 4.6 | 155 | 161 | 0.51 | - |
| case1C:wide_aperture | ssor/gmres | max_it | 10000 | 6.2e-03 | - | 4.6 | 165 | 172 | 0.51 | - |
| case1C:wide_aperture | ssor/cocg | converged | 19350 | 9.2e-09 | - | 4.6 | 159 | 166 | 0.211 | - |
| case1C:wide_aperture | amg_gamg/gmres | max_it | 10000 | 6.2e-01 | - | 5.0 | 223 | 231 | 0.556 | - |
| case1C:wide_aperture | amg_gamg/cocg | max_it | 50000 | 2.9e+00 | - | 4.7 | 704 | 711 | 0.298 | - |
| case1C:wide_aperture | accel_ic/gmres | max_it | 10000 | 1.3e-04 | - | 4.7 | 338 | 345 | 0.984 | - |
| case1C:wide_aperture | accel_ic/cocg | converged | 11212 | 8.3e-09 | - | 4.6 | 82 | 89 | 0.242 | - |
| case1C:wide_aperture | cslp/gmres | max_it | 3000 | 1.4e-01 | - | 6.3 | 768 | 776 | 1.089 | - |
| case1C:wide_aperture | hx/gmres | converged | 3572 | 1.0e-08 | - | 7.4 | 360 | 369 | 1.307 | - |
| case1C:wide_aperture | cslp_hx/gmres | max_it | 1000 | 2.3e-01 | - | 6.8 | 269 | 278 | 1.105 | - |
| case1C:wide_aperture | npatch_asm/cocg | converged | 1073 | 8.2e-09 | - | 6.6 | 14 | 23 | 0.683 | - |
| case1C:wide_aperture | mumps/direct | converged | 1 | 1.6e-13 | - | 7.0 | 0.1 | 9.3 | 1.14 | - |
| case2A:standard | gs/gmres | max_it | 10000 | 3.9e-07 | - | 5.3 | 176 | 181 | 0.574 | - |
| case2A:standard | ssor/gmres | converged | 5904 | 1.0e-08 | - | 5.3 | 111 | 116 | 0.574 | - |
| case2A:standard | ssor/cocg | converged | 3194 | 9.9e-09 | - | 5.4 | 30 | 36 | 0.242 | - |
| case2A:standard | amg_gamg/gmres | max_it | 10000 | 3.4e-05 | - | 5.7 | 254 | 260 | 0.629 | - |
| case2A:standard | amg_gamg/cocg | converged | 14412 | 9.7e-09 | - | 5.3 | 233 | 239 | 0.336 | - |
| case2A:standard | accel_ic/gmres | converged | 7999 | 1.0e-08 | - | 5.4 | 305 | 311 | 1.111 | - |
| case2A:standard | accel_ic/cocg | converged | 3751 | 9.7e-09 | - | 5.3 | 31 | 37 | 0.274 | - |
| case2A:standard | cslp/gmres | converged | 686 | 9.8e-09 | - | 7.2 | 199 | 206 | 1.227 | - |
| case2A:standard | hx/gmres | max_it | 10000 | 8.6e-05 | - | 8.5 | 863 | 872 | 1.471 | - |
| case2A:standard | cslp_hx/gmres | converged | 811 | 9.7e-09 | - | 7.7 | 244 | 251 | 1.242 | - |
| case2A:standard | npatch_asm/cocg | converged | 4687 | 6.3e-09 | - | 7.6 | 73 | 81 | 0.777 | - |
| case2A:standard | mumps/direct | converged | 1 | 6.0e-12 | - | 8.7 | 0.1 | 8.8 | 1.298 | - |
| case2A:off_resonance | gs/gmres | converged | 2086 | 9.9e-09 | - | 5.3 | 37 | 42 | 0.574 | - |
| case2A:off_resonance | ssor/gmres | converged | 866 | 9.9e-09 | - | 5.3 | 16 | 21 | 0.574 | - |
| case2A:off_resonance | ssor/cocg | converged | 729 | 8.1e-09 | - | 5.3 | 6.9 | 12 | 0.242 | - |
| case2A:off_resonance | amg_gamg/gmres | converged | 2123 | 9.9e-09 | - | 5.7 | 54 | 60 | 0.629 | - |
| case2A:off_resonance | amg_gamg/cocg | converged | 1223 | 8.2e-09 | - | 5.4 | 20 | 25 | 0.336 | - |
| case2A:off_resonance | accel_ic/gmres | converged | 910 | 9.8e-09 | - | 5.3 | 35 | 40 | 1.111 | - |
| case2A:off_resonance | accel_ic/cocg | converged | 813 | 9.6e-09 | - | 5.4 | 6.7 | 12 | 0.274 | - |
| case2A:off_resonance | cslp/gmres | converged | 101 | 6.7e-09 | - | 7.3 | 28 | 35 | 1.227 | - |
| case2A:off_resonance | hx/gmres | converged | 59 | 7.6e-09 | - | 8.6 | 5.4 | 14 | 1.471 | - |
| case2A:off_resonance | cslp_hx/gmres | converged | 60 | 4.8e-09 | - | 7.7 | 17 | 25 | 1.243 | - |
| case2A:off_resonance | npatch_asm/cocg | converged | 373 | 7.4e-09 | - | 7.7 | 5.9 | 14 | 0.777 | - |
| case2A:off_resonance | mumps/direct | converged | 1 | 2.5e-12 | - | 8.7 | 0.1 | 8.9 | 1.278 | - |
| case2B:narrow_iris | gs/gmres | converged | 4585 | 1.0e-08 | - | 3.8 | 57 | 61 | 0.419 | - |
| case2B:narrow_iris | ssor/gmres | converged | 2232 | 9.9e-09 | - | 3.7 | 29 | 33 | 0.419 | - |
| case2B:narrow_iris | ssor/cocg | converged | 1912 | 9.2e-09 | - | 3.8 | 12 | 16 | 0.177 | - |
| case2B:narrow_iris | amg_gamg/gmres | converged | 6229 | 9.9e-09 | - | 4.1 | 112 | 116 | 0.458 | - |
| case2B:narrow_iris | amg_gamg/cocg | converged | 7600 | 9.4e-09 | - | 3.8 | 86 | 90 | 0.247 | - |
| case2B:narrow_iris | accel_ic/gmres | converged | 2934 | 9.9e-09 | - | 3.8 | 80 | 84 | 0.798 | - |
| case2B:narrow_iris | accel_ic/cocg | converged | 2308 | 9.3e-09 | - | 3.8 | 14 | 17 | 0.2 | - |
| case2B:narrow_iris | cslp/gmres | converged | 441 | 9.8e-09 | - | 5.1 | 89 | 94 | 0.892 | - |
| case2B:narrow_iris | hx/gmres | max_it | 10000 | 1.4e-04 | - | 6.0 | 629 | 635 | 1.076 | - |
| case2B:narrow_iris | cslp_hx/gmres | converged | 343 | 9.6e-09 | - | 5.5 | 72 | 78 | 0.902 | - |
| case2B:narrow_iris | npatch_asm/cocg | converged | 1920 | 5.2e-09 | - | 5.3 | 20 | 25 | 0.544 | - |
| case2B:narrow_iris | mumps/direct | converged | 1 | 3.2e-12 | - | 5.4 | 0.1 | 5.5 | 0.643 | - |
| case2B:medium_iris | gs/gmres | converged | 1985 | 9.9e-09 | - | 2.9 | 19 | 21 | 0.328 | - |
| case2B:medium_iris | ssor/gmres | converged | 1115 | 9.8e-09 | - | 2.9 | 11 | 14 | 0.328 | - |
| case2B:medium_iris | ssor/cocg | converged | 1084 | 9.9e-09 | - | 2.9 | 5.4 | 8.3 | 0.135 | - |
| case2B:medium_iris | amg_gamg/gmres | converged | 1866 | 1.0e-08 | - | 3.1 | 25 | 28 | 0.357 | - |
| case2B:medium_iris | amg_gamg/cocg | converged | 2979 | 9.0e-09 | - | 2.9 | 26 | 29 | 0.187 | - |
| case2B:medium_iris | accel_ic/gmres | converged | 1300 | 9.9e-09 | - | 2.9 | 27 | 30 | 0.623 | - |
| case2B:medium_iris | accel_ic/cocg | converged | 1342 | 9.9e-09 | - | 2.9 | 6.1 | 9.0 | 0.156 | - |
| case2B:medium_iris | cslp/gmres | converged | 337 | 9.9e-09 | - | 4.0 | 52 | 56 | 0.687 | - |
| case2B:medium_iris | hx/gmres | max_it | 10000 | 3.7e-06 | - | 4.6 | 469 | 474 | 0.849 | - |
| case2B:medium_iris | cslp_hx/gmres | converged | 389 | 9.9e-09 | - | 4.3 | 62 | 66 | 0.7 | - |
| case2B:medium_iris | npatch_asm/cocg | converged | 1545 | 8.3e-09 | - | 4.1 | 12 | 16 | 0.402 | - |
| case2B:medium_iris | mumps/direct | converged | 1 | 1.7e-12 | - | 4.0 | 0.0 | 4.0 | 0.518 | - |
| case2B:wide_iris | gs/gmres | converged | 5158 | 1.0e-08 | - | 2.9 | 48 | 51 | 0.319 | - |
| case2B:wide_iris | ssor/gmres | converged | 2198 | 9.9e-09 | - | 2.8 | 22 | 24 | 0.319 | - |
| case2B:wide_iris | ssor/cocg | converged | 1586 | 8.8e-09 | - | 2.8 | 7.6 | 10 | 0.13 | - |
| case2B:wide_iris | amg_gamg/gmres | converged | 6195 | 9.9e-09 | - | 3.0 | 83 | 86 | 0.344 | - |
| case2B:wide_iris | amg_gamg/cocg | converged | 6152 | 9.5e-09 | - | 2.8 | 52 | 55 | 0.179 | - |
| case2B:wide_iris | accel_ic/gmres | converged | 2726 | 9.9e-09 | - | 2.9 | 56 | 59 | 0.599 | - |
| case2B:wide_iris | accel_ic/cocg | converged | 1864 | 9.8e-09 | - | 2.8 | 8.2 | 11 | 0.149 | - |
| case2B:wide_iris | cslp/gmres | converged | 484 | 9.7e-09 | - | 3.9 | 73 | 76 | 0.666 | - |
| case2B:wide_iris | hx/gmres | max_it | 10000 | 7.4e-06 | - | 4.5 | 455 | 460 | 0.798 | - |
| case2B:wide_iris | cslp_hx/gmres | converged | 567 | 9.5e-09 | - | 4.1 | 88 | 92 | 0.681 | - |
| case2B:wide_iris | npatch_asm/cocg | converged | 2636 | 7.9e-09 | - | 4.0 | 21 | 25 | 0.382 | - |
| case2B:wide_iris | mumps/direct | converged | 1 | 1.8e-12 | - | 3.9 | 0.0 | 4.0 | 0.138 | - |
| case2B:off_resonance | gs/gmres | converged | 1228 | 1.0e-08 | - | 2.9 | 12 | 15 | 0.328 | - |
| case2B:off_resonance | ssor/gmres | converged | 679 | 9.9e-09 | - | 2.9 | 6.5 | 9.5 | 0.328 | - |
| case2B:off_resonance | ssor/cocg | converged | 716 | 8.8e-09 | - | 2.9 | 3.7 | 6.6 | 0.135 | - |
| case2B:off_resonance | amg_gamg/gmres | converged | 1289 | 9.7e-09 | - | 3.1 | 17 | 20 | 0.357 | - |
| case2B:off_resonance | amg_gamg/cocg | converged | 1649 | 9.7e-09 | - | 2.9 | 14 | 17 | 0.187 | - |
| case2B:off_resonance | accel_ic/gmres | converged | 787 | 9.8e-09 | - | 2.9 | 16 | 19 | 0.623 | - |
| case2B:off_resonance | accel_ic/cocg | converged | 828 | 9.2e-09 | - | 3.0 | 3.7 | 6.7 | 0.156 | - |
| case2B:off_resonance | cslp/gmres | converged | 108 | 7.8e-09 | - | 3.9 | 16 | 20 | 0.687 | - |
| case2B:off_resonance | hx/gmres | converged | 186 | 9.7e-09 | - | 4.6 | 8.5 | 13 | 0.849 | - |
| case2B:off_resonance | cslp_hx/gmres | converged | 106 | 9.0e-09 | - | 4.2 | 16 | 21 | 0.7 | - |
| case2B:off_resonance | npatch_asm/cocg | converged | 763 | 9.1e-09 | - | 4.1 | 6.0 | 10 | 0.402 | - |
| case2B:off_resonance | mumps/direct | converged | 1 | 1.4e-12 | - | 4.0 | 0.0 | 4.1 | 0.515 | - |
| case2C:narrow_slit | gs/gmres | converged | 2724 | 9.9e-09 | - | 3.2 | 28 | 32 | 0.35 | - |
| case2C:narrow_slit | ssor/gmres | converged | 1625 | 1.0e-08 | - | 3.1 | 18 | 21 | 0.35 | - |
| case2C:narrow_slit | ssor/cocg | converged | 1602 | 9.8e-09 | - | 3.1 | 8.7 | 12 | 0.146 | - |
| case2C:narrow_slit | amg_gamg/gmres | converged | 3974 | 1.0e-08 | - | 3.4 | 59 | 63 | 0.382 | - |
| case2C:narrow_slit | amg_gamg/cocg | converged | 11207 | 9.7e-09 | - | 3.2 | 105 | 109 | 0.201 | - |
| case2C:narrow_slit | accel_ic/gmres | converged | 1944 | 1.0e-08 | - | 3.2 | 44 | 47 | 0.672 | - |
| case2C:narrow_slit | accel_ic/cocg | converged | 1872 | 9.1e-09 | - | 3.2 | 9.2 | 12 | 0.166 | - |
| case2C:narrow_slit | cslp/gmres | converged | 424 | 9.9e-09 | - | 4.3 | 71 | 75 | 0.742 | - |
| case2C:narrow_slit | hx/gmres | max_it | 10000 | 1.2e-03 | - | 5.0 | 507 | 512 | 0.9 | - |
| case2C:narrow_slit | cslp_hx/gmres | converged | 424 | 9.9e-09 | - | 4.5 | 73 | 78 | 0.757 | - |
| case2C:narrow_slit | npatch_asm/cocg | converged | 2171 | 8.7e-09 | - | 4.4 | 18 | 23 | 0.435 | - |
| case2C:narrow_slit | mumps/direct | converged | 1 | 2.3e-12 | - | 4.5 | 0.1 | 4.5 | 0.418 | - |
| case2C:medium_slit | gs/gmres | converged | 3049 | 1.0e-08 | - | 3.1 | 31 | 34 | 0.348 | - |
| case2C:medium_slit | ssor/gmres | converged | 1786 | 9.9e-09 | - | 3.1 | 20 | 23 | 0.348 | - |
| case2C:medium_slit | ssor/cocg | converged | 1590 | 9.7e-09 | - | 3.1 | 8.7 | 12 | 0.147 | - |
| case2C:medium_slit | amg_gamg/gmres | converged | 4158 | 1.0e-08 | - | 3.3 | 61 | 65 | 0.377 | - |
| case2C:medium_slit | amg_gamg/cocg | converged | 5469 | 9.5e-09 | - | 3.1 | 51 | 54 | 0.201 | - |
| case2C:medium_slit | accel_ic/gmres | converged | 2109 | 1.0e-08 | - | 3.1 | 48 | 51 | 0.664 | - |
| case2C:medium_slit | accel_ic/cocg | converged | 1897 | 8.5e-09 | - | 3.1 | 9.1 | 12 | 0.167 | - |
| case2C:medium_slit | cslp/gmres | converged | 445 | 9.7e-09 | - | 4.2 | 73 | 77 | 0.734 | - |
| case2C:medium_slit | hx/gmres | max_it | 10000 | 2.4e-05 | - | 4.9 | 497 | 502 | 0.894 | - |
| case2C:medium_slit | cslp_hx/gmres | converged | 476 | 1.0e-08 | - | 4.5 | 81 | 85 | 0.747 | - |
| case2C:medium_slit | npatch_asm/cocg | converged | 2284 | 9.1e-09 | - | 4.4 | 19 | 23 | 0.414 | - |
| case2C:medium_slit | mumps/direct | converged | 1 | 4.3e-12 | - | 4.3 | 0.0 | 4.4 | 0.469 | - |
| case2C:wide_slit | gs/gmres | converged | 6998 | 1.0e-08 | - | 3.1 | 72 | 76 | 0.349 | - |
| case2C:wide_slit | ssor/gmres | converged | 3236 | 9.9e-09 | - | 3.1 | 36 | 39 | 0.349 | - |
| case2C:wide_slit | ssor/cocg | converged | 1751 | 8.7e-09 | - | 3.1 | 9.4 | 13 | 0.144 | - |
| case2C:wide_slit | amg_gamg/gmres | converged | 8984 | 1.0e-08 | - | 3.3 | 134 | 137 | 0.383 | - |
| case2C:wide_slit | amg_gamg/cocg | converged | 8425 | 9.8e-09 | - | 3.1 | 79 | 82 | 0.2 | - |
| case2C:wide_slit | accel_ic/gmres | converged | 2783 | 1.0e-08 | - | 3.2 | 63 | 66 | 0.662 | - |
| case2C:wide_slit | accel_ic/cocg | converged | 2023 | 9.1e-09 | - | 3.2 | 9.9 | 13 | 0.165 | - |
| case2C:wide_slit | cslp/gmres | converged | 492 | 9.9e-09 | - | 4.3 | 82 | 87 | 0.732 | - |
| case2C:wide_slit | hx/gmres | max_it | 10000 | 1.2e-05 | - | 5.0 | 504 | 509 | 0.893 | - |
| case2C:wide_slit | cslp_hx/gmres | converged | 525 | 9.9e-09 | - | 4.6 | 91 | 96 | 0.749 | - |
| case2C:wide_slit | npatch_asm/cocg | converged | 2407 | 8.5e-09 | - | 4.4 | 20 | 25 | 0.433 | - |
| case2C:wide_slit | mumps/direct | converged | 1 | 2.1e-12 | - | 4.3 | 0.1 | 4.4 | 0.473 | - |
| case2C:off_resonance | gs/gmres | converged | 1663 | 9.9e-09 | - | 3.1 | 17 | 20 | 0.348 | - |
| case2C:off_resonance | ssor/gmres | converged | 1069 | 9.9e-09 | - | 3.1 | 11 | 14 | 0.348 | - |
| case2C:off_resonance | ssor/cocg | converged | 965 | 9.8e-09 | - | 3.1 | 5.3 | 8.4 | 0.145 | - |
| case2C:off_resonance | amg_gamg/gmres | converged | 1753 | 9.9e-09 | - | 3.4 | 26 | 29 | 0.377 | - |
| case2C:off_resonance | amg_gamg/cocg | converged | 2116 | 9.8e-09 | - | 3.1 | 20 | 23 | 0.201 | - |
| case2C:off_resonance | accel_ic/gmres | converged | 1155 | 1.0e-08 | - | 3.1 | 26 | 29 | 0.663 | - |
| case2C:off_resonance | accel_ic/cocg | converged | 1106 | 7.3e-09 | - | 3.1 | 5.3 | 8.3 | 0.167 | - |
| case2C:off_resonance | cslp/gmres | converged | 142 | 9.2e-09 | - | 4.2 | 23 | 27 | 0.734 | - |
| case2C:off_resonance | hx/gmres | converged | 209 | 8.9e-09 | - | 4.9 | 10 | 15 | 0.894 | - |
| case2C:off_resonance | cslp_hx/gmres | converged | 131 | 9.7e-09 | - | 4.5 | 22 | 26 | 0.747 | - |
| case2C:off_resonance | npatch_asm/cocg | converged | 826 | 8.6e-09 | - | 4.4 | 7.1 | 11 | 0.414 | - |
| case2C:off_resonance | mumps/direct | converged | 1 | 1.8e-12 | - | 4.4 | 0.0 | 4.5 | 0.449 | - |
| case2D:few_walls | gs/gmres | max_it | 10000 | 4.4e-07 | - | 6.0 | 205 | 211 | 0.668 | - |
| case2D:few_walls | ssor/gmres | converged | 8619 | 1.0e-08 | - | 5.9 | 188 | 194 | 0.668 | - |
| case2D:few_walls | ssor/cocg | converged | 3050 | 9.7e-09 | - | 5.9 | 32 | 38 | 0.278 | - |
| case2D:few_walls | amg_gamg/gmres | max_it | 10000 | 3.5e-05 | - | 6.4 | 294 | 300 | 0.712 | - |
| case2D:few_walls | amg_gamg/cocg | converged | 13071 | 9.4e-09 | - | 5.9 | 239 | 245 | 0.384 | - |
| case2D:few_walls | accel_ic/gmres | max_it | 10000 | 1.3e-08 | - | 6.0 | 443 | 449 | 1.29 | - |
| case2D:few_walls | accel_ic/cocg | converged | 3564 | 1.0e-08 | - | 5.9 | 34 | 40 | 0.317 | - |
| case2D:few_walls | cslp/gmres | converged | 1370 | 9.9e-09 | - | 8.1 | 456 | 464 | 1.424 | - |
| case2D:few_walls | hx/gmres | converged | 6444 | 1.0e-08 | - | 9.7 | 652 | 661 | 1.72 | - |
| case2D:few_walls | cslp_hx/gmres | max_it | 1000 | 4.2e-07 | - | 8.7 | 344 | 353 | 1.441 | - |
| case2D:few_walls | npatch_asm/cocg | converged | 3771 | 8.1e-09 | - | 8.4 | 61 | 69 | 0.83 | - |
| case2D:few_walls | mumps/direct | converged | 1 | 1.3e-12 | - | 7.9 | 0.1 | 8.1 | 0.879 | - |
| case2D:many_walls | gs/gmres | max_it | 10000 | 5.9e-03 | - | 4.9 | 182 | 187 | 0.588 | - |
| case2D:many_walls | ssor/gmres | max_it | 10000 | 5.2e-03 | - | 4.9 | 193 | 198 | 0.588 | - |
| case2D:many_walls | ssor/cocg | converged | 20876 | 9.9e-09 | - | 5.0 | 185 | 190 | 0.223 | - |
| case2D:many_walls | amg_gamg/gmres | max_it | 10000 | 4.4e-03 | - | 5.3 | 257 | 263 | 0.624 | - |
| case2D:many_walls | amg_gamg/cocg | converged | 19450 | 1.0e-08 | - | 4.9 | 299 | 304 | 0.313 | - |
| case2D:many_walls | accel_ic/gmres | max_it | 10000 | 4.8e-03 | - | 5.0 | 394 | 400 | 1.137 | - |
| case2D:many_walls | accel_ic/cocg | converged | 24553 | 9.4e-09 | - | 4.9 | 199 | 204 | 0.254 | - |
| case2D:many_walls | cslp/gmres | max_it | 3000 | 8.6e-04 | - | 6.8 | 857 | 864 | 1.237 | - |
| case2D:many_walls | hx/gmres | max_it | 10000 | 3.1e-03 | - | 8.3 | 879 | 887 | 1.539 | - |
| case2D:many_walls | cslp_hx/gmres | max_it | 1000 | 2.1e-03 | - | 7.5 | 290 | 298 | 1.254 | - |
| case2D:many_walls | npatch_asm/cocg | converged | 9927 | 6.2e-09 | - | 6.9 | 111 | 118 | 0.508 | - |
| case2D:many_walls | mumps/direct | converged | 1 | 1.3e-12 | - | 6.0 | 0.0 | 6.2 | 0.502 | - |
| case2D:off_resonance | gs/gmres | converged | 2316 | 1.0e-08 | - | 5.9 | 47 | 53 | 0.668 | - |
| case2D:off_resonance | ssor/gmres | converged | 1291 | 1.0e-08 | - | 5.9 | 27 | 33 | 0.668 | - |
| case2D:off_resonance | ssor/cocg | converged | 1080 | 9.0e-09 | - | 5.9 | 11 | 17 | 0.278 | - |
| case2D:off_resonance | amg_gamg/gmres | converged | 2136 | 9.9e-09 | - | 6.5 | 63 | 69 | 0.712 | - |
| case2D:off_resonance | amg_gamg/cocg | converged | 1712 | 8.6e-09 | - | 6.0 | 32 | 38 | 0.384 | - |
| case2D:off_resonance | accel_ic/gmres | converged | 1452 | 9.9e-09 | - | 5.9 | 63 | 69 | 1.29 | - |
| case2D:off_resonance | accel_ic/cocg | converged | 1217 | 9.7e-09 | - | 5.9 | 12 | 17 | 0.317 | - |
| case2D:off_resonance | cslp/gmres | converged | 137 | 9.5e-09 | - | 8.1 | 44 | 52 | 1.424 | - |
| case2D:off_resonance | hx/gmres | converged | 214 | 8.7e-09 | - | 9.8 | 27 | 36 | 1.72 | - |
| case2D:off_resonance | cslp_hx/gmres | converged | 74 | 9.0e-09 | - | 8.7 | 24 | 33 | 1.44 | - |
| case2D:off_resonance | npatch_asm/cocg | converged | 373 | 4.4e-09 | - | 8.6 | 6.1 | 15 | 0.831 | - |
| case2D:off_resonance | mumps/direct | converged | 1 | 5.7e-12 | - | 8.0 | 0.1 | 8.2 | 0.875 | - |
| case2E:sparse_irises | gs/gmres | converged | 6225 | 1.0e-08 | - | 1.2 | 24 | 25 | 0.148 | - |
| case2E:sparse_irises | ssor/gmres | converged | 3312 | 1.0e-08 | - | 1.2 | 13 | 15 | 0.148 | - |
| case2E:sparse_irises | ssor/cocg | converged | 1033 | 9.0e-09 | - | 1.2 | 2.0 | 3.2 | 0.059 | - |
| case2E:sparse_irises | amg_gamg/gmres | converged | 2846 | 1.0e-08 | - | 1.2 | 15 | 16 | 0.152 | - |
| case2E:sparse_irises | amg_gamg/cocg | converged | 1167 | 7.8e-09 | - | 1.2 | 3.7 | 4.9 | 0.078 | - |
| case2E:sparse_irises | accel_ic/gmres | converged | 3880 | 1.0e-08 | - | 1.2 | 34 | 35 | 0.259 | - |
| case2E:sparse_irises | accel_ic/cocg | converged | 1216 | 9.9e-09 | - | 1.2 | 2.1 | 3.3 | 0.065 | - |
| case2E:sparse_irises | cslp/gmres | converged | 118 | 8.8e-09 | - | 1.6 | 6.2 | 7.8 | 0.276 | - |
| case2E:sparse_irises | hx/gmres | converged | 239 | 7.9e-09 | - | 1.8 | 3.9 | 5.7 | 0.339 | - |
| case2E:sparse_irises | cslp_hx/gmres | converged | 132 | 9.2e-09 | - | 1.7 | 7.2 | 8.9 | 0.284 | - |
| case2E:sparse_irises | npatch_asm/cocg | converged | 626 | 6.7e-09 | - | 1.6 | 1.6 | 3.2 | 0.137 | - |
| case2E:sparse_irises | mumps/direct | converged | 1 | 3.0e-13 | - | 1.4 | 0.0 | 1.4 | 0.049 | - |
| case2E:dense_irises | gs/gmres | converged | 1242 | 9.8e-09 | - | 1.5 | 6.6 | 8.1 | 0.192 | - |
| case2E:dense_irises | ssor/gmres | converged | 752 | 1.0e-08 | - | 1.5 | 4.0 | 5.5 | 0.192 | - |
| case2E:dense_irises | ssor/cocg | converged | 794 | 9.9e-09 | - | 1.6 | 2.1 | 3.7 | 0.079 | - |
| case2E:dense_irises | amg_gamg/gmres | converged | 590 | 9.9e-09 | - | 1.7 | 4.4 | 6.0 | 0.198 | - |
| case2E:dense_irises | amg_gamg/cocg | converged | 772 | 9.2e-09 | - | 1.6 | 3.5 | 5.0 | 0.103 | - |
| case2E:dense_irises | accel_ic/gmres | converged | 840 | 9.9e-09 | - | 1.6 | 9.9 | 11 | 0.354 | - |
| case2E:dense_irises | accel_ic/cocg | converged | 883 | 7.4e-09 | - | 1.5 | 2.1 | 3.7 | 0.088 | - |
| case2E:dense_irises | cslp/gmres | converged | 72 | 9.7e-09 | - | 2.1 | 5.3 | 7.5 | 0.384 | - |
| case2E:dense_irises | hx/gmres | converged | 283 | 9.7e-09 | - | 2.5 | 6.5 | 9.0 | 0.478 | - |
| case2E:dense_irises | cslp_hx/gmres | converged | 79 | 9.7e-09 | - | 2.3 | 6.0 | 8.3 | 0.39 | - |
| case2E:dense_irises | npatch_asm/cocg | converged | 374 | 8.5e-09 | - | 2.1 | 1.2 | 3.3 | 0.156 | - |
| case2E:dense_irises | mumps/direct | converged | 1 | 1.3e-13 | - | 1.8 | 0.0 | 1.8 | 0.031 | - |
| case2F:empty | gs/gmres | converged | 810 | 9.7e-09 | - | 0.3 | 0.4 | 0.7 | 0 | - |
| case2F:empty | ssor/gmres | converged | 268 | 9.2e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:empty | ssor/cocg | converged | 354 | 8.4e-09 | - | 0.3 | 0.1 | 0.4 | 0 | - |
| case2F:empty | amg_gamg/gmres | converged | 236 | 6.6e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:empty | amg_gamg/cocg | converged | 331 | 7.3e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:empty | accel_ic/gmres | converged | 321 | 9.7e-09 | - | 0.3 | 0.6 | 0.9 | 0.066 | - |
| case2F:empty | accel_ic/cocg | converged | 413 | 8.1e-09 | - | 0.3 | 0.1 | 0.4 | 0 | - |
| case2F:empty | cslp/gmres | converged | 33 | 1.0e-08 | - | 0.4 | 0.2 | 0.6 | 0 | - |
| case2F:empty | hx/gmres | converged | 69 | 6.6e-09 | - | 0.4 | 0.2 | 0.6 | 0 | - |
| case2F:empty | cslp_hx/gmres | converged | 35 | 7.8e-09 | - | 0.4 | 0.3 | 0.7 | 0 | - |
| case2F:empty | npatch_asm/cocg | converged | 128 | 7.5e-09 | - | 0.4 | 0.1 | 0.4 | 0 | - |
| case2F:empty | mumps/direct | converged | 1 | 2.1e-14 | - | 0.3 | 0.0 | 0.3 | 0 | - |
| case2F:plex7 | gs/gmres | converged | 1035 | 1.0e-08 | - | 0.3 | 0.6 | 0.9 | 0.043 | - |
| case2F:plex7 | ssor/gmres | converged | 290 | 9.1e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:plex7 | ssor/cocg | converged | 394 | 5.6e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:plex7 | amg_gamg/gmres | converged | 249 | 9.6e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:plex7 | amg_gamg/cocg | converged | 343 | 7.6e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:plex7 | accel_ic/gmres | converged | 477 | 9.9e-09 | - | 0.3 | 0.8 | 1.1 | 0.066 | - |
| case2F:plex7 | accel_ic/cocg | converged | 443 | 8.9e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:plex7 | cslp/gmres | converged | 31 | 7.9e-09 | - | 0.4 | 0.2 | 0.7 | 0 | - |
| case2F:plex7 | hx/gmres | converged | 75 | 5.6e-09 | - | 0.4 | 0.2 | 0.6 | 0 | - |
| case2F:plex7 | cslp_hx/gmres | converged | 34 | 4.7e-09 | - | 0.4 | 0.3 | 0.7 | 0 | - |
| case2F:plex7 | npatch_asm/cocg | converged | 115 | 8.8e-09 | - | 0.4 | 0.1 | 0.4 | 0 | - |
| case2F:plex7 | mumps/direct | converged | 1 | 1.2e-14 | - | 0.3 | 0.0 | 0.3 | 0 | - |
| case2F:plex9 | gs/gmres | converged | 722 | 1.0e-08 | - | 0.3 | 0.4 | 0.8 | 0 | - |
| case2F:plex9 | ssor/gmres | converged | 274 | 9.5e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:plex9 | ssor/cocg | converged | 372 | 4.9e-09 | - | 0.3 | 0.1 | 0.5 | 0.001 | - |
| case2F:plex9 | amg_gamg/gmres | converged | 240 | 9.6e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:plex9 | amg_gamg/cocg | converged | 338 | 5.0e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:plex9 | accel_ic/gmres | converged | 346 | 9.8e-09 | - | 0.3 | 0.6 | 0.9 | 0.066 | - |
| case2F:plex9 | accel_ic/cocg | converged | 431 | 8.3e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:plex9 | cslp/gmres | converged | 31 | 5.9e-09 | - | 0.4 | 0.2 | 0.7 | 0 | - |
| case2F:plex9 | hx/gmres | converged | 75 | 6.9e-09 | - | 0.5 | 0.2 | 0.6 | 0 | - |
| case2F:plex9 | cslp_hx/gmres | converged | 33 | 6.6e-09 | - | 0.4 | 0.3 | 0.7 | 0 | - |
| case2F:plex9 | npatch_asm/cocg | converged | 117 | 4.4e-09 | - | 0.4 | 0.1 | 0.5 | 0 | - |
| case2F:plex9 | mumps/direct | converged | 1 | 3.9e-14 | - | 0.3 | 0.0 | 0.3 | 0 | - |
| case2F:pvc7 | gs/gmres | converged | 900 | 9.8e-09 | - | 0.3 | 0.6 | 0.9 | 0.043 | - |
| case2F:pvc7 | ssor/gmres | converged | 289 | 9.6e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:pvc7 | ssor/cocg | converged | 391 | 2.3e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:pvc7 | amg_gamg/gmres | converged | 252 | 7.7e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:pvc7 | amg_gamg/cocg | converged | 345 | 7.3e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:pvc7 | accel_ic/gmres | converged | 558 | 9.5e-09 | - | 0.3 | 1.0 | 1.4 | 0.066 | - |
| case2F:pvc7 | accel_ic/cocg | converged | 452 | 6.4e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:pvc7 | cslp/gmres | converged | 32 | 4.7e-09 | - | 0.4 | 0.2 | 0.7 | 0 | - |
| case2F:pvc7 | hx/gmres | converged | 75 | 8.2e-09 | - | 0.4 | 0.2 | 0.6 | 0 | - |
| case2F:pvc7 | cslp_hx/gmres | converged | 34 | 6.3e-09 | - | 0.4 | 0.3 | 0.7 | 0 | - |
| case2F:pvc7 | npatch_asm/cocg | converged | 116 | 3.3e-09 | - | 0.4 | 0.1 | 0.5 | 0 | - |
| case2F:pvc7 | mumps/direct | converged | 1 | 1.1e-14 | - | 0.3 | 0.0 | 0.3 | 0 | - |
| case2F:pvc9 | gs/gmres | converged | 642 | 9.8e-09 | - | 0.3 | 0.4 | 0.7 | 0 | - |
| case2F:pvc9 | ssor/gmres | converged | 267 | 7.5e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:pvc9 | ssor/cocg | converged | 346 | 5.1e-09 | - | 0.3 | 0.1 | 0.4 | 0 | - |
| case2F:pvc9 | amg_gamg/gmres | converged | 229 | 8.4e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:pvc9 | amg_gamg/cocg | converged | 312 | 4.8e-09 | - | 0.3 | 0.2 | 0.5 | 0 | - |
| case2F:pvc9 | accel_ic/gmres | converged | 306 | 9.7e-09 | - | 0.3 | 0.6 | 0.9 | 0.066 | - |
| case2F:pvc9 | accel_ic/cocg | converged | 416 | 3.7e-09 | - | 0.3 | 0.1 | 0.5 | 0 | - |
| case2F:pvc9 | cslp/gmres | converged | 29 | 8.4e-09 | - | 0.4 | 0.2 | 0.6 | 0 | - |
| case2F:pvc9 | hx/gmres | converged | 75 | 7.2e-09 | - | 0.4 | 0.2 | 0.6 | 0 | - |
| case2F:pvc9 | cslp_hx/gmres | converged | 32 | 6.6e-09 | - | 0.4 | 0.3 | 0.7 | 0 | - |
| case2F:pvc9 | npatch_asm/cocg | converged | 111 | 7.9e-09 | - | 0.4 | 0.1 | 0.5 | 0 | - |
| case2F:pvc9 | mumps/direct | converged | 1 | 1.4e-14 | - | 0.3 | 0.0 | 0.3 | 0 | - |
| case3A:low_contrast | gs/gmres | converged | 3244 | 9.9e-09 | - | 5.7 | 60 | 66 | 0.607 | - |
| case3A:low_contrast | ssor/gmres | converged | 1420 | 9.9e-09 | - | 5.7 | 27 | 33 | 0.607 | - |
| case3A:low_contrast | ssor/cocg | converged | 1072 | 9.1e-09 | - | 5.7 | 11 | 17 | 0.255 | - |
| case3A:low_contrast | amg_gamg/gmres | converged | 1420 | 1.0e-08 | - | 6.2 | 37 | 44 | 0.664 | - |
| case3A:low_contrast | amg_gamg/cocg | converged | 1157 | 9.9e-09 | - | 5.7 | 20 | 26 | 0.356 | - |
| case3A:low_contrast | accel_ic/gmres | converged | 1707 | 1.0e-08 | - | 5.7 | 67 | 73 | 1.172 | - |
| case3A:low_contrast | accel_ic/cocg | converged | 1271 | 8.1e-09 | - | 5.7 | 11 | 17 | 0.289 | - |
| case3A:low_contrast | cslp/gmres | converged | 110 | 8.7e-09 | - | 7.7 | 32 | 40 | 1.305 | - |
| case3A:low_contrast | hx/gmres | converged | 35 | 7.9e-09 | - | 9.1 | 4.6 | 14 | 1.556 | - |
| case3A:low_contrast | cslp_hx/gmres | converged | 42 | 7.0e-09 | - | 8.2 | 13 | 21 | 1.317 | - |
| case3A:low_contrast | npatch_asm/cocg | converged | 267 | 8.3e-09 | - | 8.2 | 4.3 | 13 | 0.854 | - |
| case3A:low_contrast | mumps/direct | converged | 1 | 1.8e-13 | - | 9.4 | 0.1 | 9.6 | 1.778 | - |
| case3A:high_contrast | gs/gmres | max_it | 10000 | 4.8e-03 | - | 5.6 | 186 | 191 | 0.607 | - |
| case3A:high_contrast | ssor/gmres | max_it | 10000 | 7.0e-04 | - | 5.7 | 199 | 204 | 0.607 | - |
| case3A:high_contrast | ssor/cocg | converged | 8411 | 9.9e-09 | - | 5.6 | 83 | 89 | 0.254 | - |
| case3A:high_contrast | amg_gamg/gmres | max_it | 10000 | 5.4e-03 | - | 6.1 | 269 | 275 | 0.665 | - |
| case3A:high_contrast | amg_gamg/cocg | max_it | 50000 | 9.2e-08 | - | 5.7 | 857 | 863 | 0.356 | - |
| case3A:high_contrast | accel_ic/gmres | max_it | 10000 | 1.2e-03 | - | 5.7 | 404 | 409 | 1.172 | - |
| case3A:high_contrast | accel_ic/cocg | converged | 9653 | 9.8e-09 | - | 5.8 | 86 | 91 | 0.289 | - |
| case3A:high_contrast | cslp/gmres | max_it | 3000 | 3.5e-05 | - | 7.7 | 930 | 937 | 1.305 | - |
| case3A:high_contrast | hx/gmres | max_it | 10000 | 2.1e-02 | - | 9.0 | 991 | 1000 | 1.556 | - |
| case3A:high_contrast | cslp_hx/gmres | max_it | 1000 | 1.3e-03 | - | 8.3 | 319 | 327 | 1.317 | - |
| case3A:high_contrast | npatch_asm/cocg | converged | 12170 | 5.1e-09 | - | 8.2 | 205 | 214 | 0.854 | - |
| case3A:high_contrast | mumps/direct | converged | 1 | 1.3e-11 | - | 9.5 | 0.1 | 9.7 | 1.727 | - |
| case3B:few_layers | gs/gmres | max_it | 10000 | 1.2e-03 | - | 4.6 | 154 | 158 | 0.509 | - |
| case3B:few_layers | ssor/gmres | max_it | 10000 | 1.9e-04 | - | 4.7 | 164 | 169 | 0.509 | - |
| case3B:few_layers | ssor/cocg | converged | 6382 | 9.5e-09 | - | 4.7 | 52 | 57 | 0.213 | - |
| case3B:few_layers | amg_gamg/gmres | max_it | 10000 | 5.0e-04 | - | 5.0 | 222 | 227 | 0.557 | - |
| case3B:few_layers | amg_gamg/cocg | converged | 28924 | 9.4e-09 | - | 4.6 | 408 | 412 | 0.297 | - |
| case3B:few_layers | accel_ic/gmres | max_it | 10000 | 4.0e-04 | - | 4.7 | 335 | 339 | 0.977 | - |
| case3B:few_layers | accel_ic/cocg | converged | 7692 | 8.9e-09 | - | 4.7 | 56 | 60 | 0.244 | - |
| case3B:few_layers | cslp/gmres | max_it | 3000 | 9.8e-08 | - | 6.3 | 764 | 770 | 1.087 | - |
| case3B:few_layers | hx/gmres | max_it | 10000 | 6.3e-04 | - | 7.4 | 799 | 807 | 1.277 | - |
| case3B:few_layers | cslp_hx/gmres | max_it | 1000 | 9.8e-05 | - | 6.7 | 261 | 268 | 1.102 | - |
| case3B:few_layers | npatch_asm/cocg | converged | 9695 | 9.6e-09 | - | 6.8 | 129 | 136 | 0.695 | - |
| case3B:few_layers | mumps/direct | converged | 1 | 3.0e-12 | - | 6.8 | 0.1 | 6.9 | 0.697 | - |
| case3B:many_layers | gs/gmres | max_it | 10000 | 3.7e-04 | - | 7.2 | 240 | 247 | 0.776 | - |
| case3B:many_layers | ssor/gmres | max_it | 10000 | 1.2e-04 | - | 7.1 | 255 | 262 | 0.776 | - |
| case3B:many_layers | ssor/cocg | converged | 6966 | 9.3e-09 | - | 7.2 | 88 | 95 | 0.323 | - |
| case3B:many_layers | amg_gamg/gmres | max_it | 10000 | 1.5e-04 | - | 7.8 | 344 | 352 | 0.854 | - |
| case3B:many_layers | amg_gamg/cocg | converged | 7917 | 9.1e-09 | - | 7.1 | 174 | 181 | 0.451 | - |
| case3B:many_layers | accel_ic/gmres | max_it | 10000 | 1.9e-04 | - | 7.2 | 518 | 525 | 1.497 | - |
| case3B:many_layers | accel_ic/cocg | converged | 8047 | 8.9e-09 | - | 7.2 | 91 | 98 | 0.37 | - |
| case3B:many_layers | cslp/gmres | converged | 1464 | 9.9e-09 | - | 9.9 | 583 | 593 | 1.676 | - |
| case3B:many_layers | hx/gmres | max_it | 10000 | 7.5e-03 | - | 11 | 1361 | 1373 | 1.989 | - |
| case3B:many_layers | cslp_hx/gmres | max_it | 1000 | 9.8e-07 | - | 10 | 410 | 420 | 1.693 | - |
| case3B:many_layers | npatch_asm/cocg | converged | 21606 | 8.2e-09 | - | 11 | 462 | 472 | 1.091 | - |
| case3B:many_layers | mumps/direct | converged | 1 | 5.3e-12 | - | 11 | 0.1 | 11 | 1.756 | - |
| case3C:coarse_check | gs/gmres | max_it | 10000 | 3.8e-02 | - | 5.3 | 176 | 181 | 0.584 | - |
| case3C:coarse_check | ssor/gmres | max_it | 10000 | 1.7e-03 | - | 5.3 | 187 | 193 | 0.584 | - |
| case3C:coarse_check | ssor/cocg | converged | 8113 | 9.9e-09 | - | 5.3 | 75 | 80 | 0.244 | - |
| case3C:coarse_check | amg_gamg/gmres | max_it | 10000 | 2.4e-02 | - | 5.8 | 251 | 257 | 0.637 | - |
| case3C:coarse_check | amg_gamg/cocg | converged | 25525 | 9.6e-09 | - | 5.3 | 404 | 409 | 0.34 | - |
| case3C:coarse_check | accel_ic/gmres | max_it | 10000 | 1.3e-02 | - | 5.4 | 386 | 391 | 1.124 | - |
| case3C:coarse_check | accel_ic/cocg | converged | 10371 | 9.2e-09 | - | 5.3 | 85 | 91 | 0.277 | - |
| case3C:coarse_check | cslp/gmres | converged | 1999 | 1.0e-08 | - | 7.2 | 567 | 574 | 1.251 | - |
| case3C:coarse_check | hx/gmres | max_it | 10000 | 4.5e-07 | - | 8.3 | 975 | 983 | 1.509 | - |
| case3C:coarse_check | cslp_hx/gmres | max_it | 1000 | 2.3e-07 | - | 7.7 | 293 | 301 | 1.264 | - |
| case3C:coarse_check | npatch_asm/cocg | converged | 11085 | 9.1e-09 | - | 7.8 | 174 | 182 | 0.831 | - |
| case3C:coarse_check | mumps/direct | converged | 1 | 7.8e-12 | - | 8.2 | 0.1 | 8.4 | 1.454 | - |
| case3C:medium_check | gs/gmres | max_it | 10000 | 2.8e-03 | - | 5.3 | 175 | 181 | 0.584 | - |
| case3C:medium_check | ssor/gmres | max_it | 10000 | 3.5e-04 | - | 5.4 | 187 | 192 | 0.584 | - |
| case3C:medium_check | ssor/cocg | converged | 8591 | 9.5e-09 | - | 5.3 | 80 | 86 | 0.245 | - |
| case3C:medium_check | amg_gamg/gmres | max_it | 10000 | 2.7e-04 | - | 6.4 | 249 | 256 | 0.638 | - |
| case3C:medium_check | amg_gamg/cocg | converged | 14990 | 9.8e-09 | - | 5.3 | 237 | 242 | 0.34 | - |
| case3C:medium_check | accel_ic/gmres | max_it | 10000 | 4.4e-04 | - | 5.4 | 385 | 390 | 1.124 | - |
| case3C:medium_check | accel_ic/cocg | converged | 11630 | 9.9e-09 | - | 5.3 | 95 | 100 | 0.278 | - |
| case3C:medium_check | cslp/gmres | converged | 1634 | 1.0e-08 | - | 7.3 | 456 | 463 | 1.256 | - |
| case3C:medium_check | hx/gmres | converged | 6161 | 1.0e-08 | - | 8.3 | 582 | 590 | 1.501 | - |
| case3C:medium_check | cslp_hx/gmres | max_it | 1000 | 1.2e-07 | - | 7.6 | 288 | 296 | 1.269 | - |
| case3C:medium_check | npatch_asm/cocg | converged | 6208 | 3.3e-09 | - | 7.8 | 97 | 105 | 0.814 | - |
| case3C:medium_check | mumps/direct | converged | 1 | 9.6e-12 | - | 7.9 | 0.1 | 8.1 | 1.351 | - |
| case3C:fine_check | gs/gmres | max_it | 10000 | 1.8e-02 | - | 6.5 | 219 | 226 | 0.726 | - |
| case3C:fine_check | ssor/gmres | max_it | 10000 | 6.3e-04 | - | 6.6 | 233 | 240 | 0.726 | - |
| case3C:fine_check | ssor/cocg | converged | 5374 | 9.4e-09 | - | 6.6 | 61 | 68 | 0.304 | - |
| case3C:fine_check | amg_gamg/gmres | max_it | 10000 | 1.6e-03 | - | 7.0 | 311 | 318 | 0.798 | - |
| case3C:fine_check | amg_gamg/cocg | converged | 7400 | 8.7e-09 | - | 6.6 | 146 | 152 | 0.425 | - |
| case3C:fine_check | accel_ic/gmres | max_it | 10000 | 8.7e-04 | - | 6.6 | 478 | 485 | 1.4 | - |
| case3C:fine_check | accel_ic/cocg | converged | 6288 | 9.4e-09 | - | 6.6 | 64 | 71 | 0.346 | - |
| case3C:fine_check | cslp/gmres | converged | 727 | 9.7e-09 | - | 9.1 | 250 | 259 | 1.559 | - |
| case3C:fine_check | hx/gmres | converged | 4983 | 1.0e-08 | - | 10 | 632 | 643 | 1.881 | - |
| case3C:fine_check | cslp_hx/gmres | converged | 720 | 9.9e-09 | - | 9.5 | 257 | 267 | 1.579 | - |
| case3C:fine_check | npatch_asm/cocg | converged | 8075 | 9.6e-09 | - | 9.7 | 171 | 180 | 1.115 | - |
| case3C:fine_check | mumps/direct | converged | 1 | 1.2e-11 | - | 9.7 | 0.1 | 9.9 | 1.265 | - |
| case3D:sparse_array | gs/gmres | max_it | 10000 | 1.5e-06 | - | 1.8 | 55 | 57 | 0.199 | - |
| case3D:sparse_array | ssor/gmres | converged | 8329 | 1.0e-08 | - | 1.8 | 49 | 51 | 0.199 | - |
| case3D:sparse_array | ssor/cocg | converged | 3277 | 9.4e-09 | - | 1.8 | 9.8 | 12 | 0.087 | - |
| case3D:sparse_array | amg_gamg/gmres | converged | 4681 | 1.0e-08 | - | 1.9 | 36 | 38 | 0.212 | - |
| case3D:sparse_array | amg_gamg/cocg | converged | 3219 | 9.8e-09 | - | 1.8 | 16 | 18 | 0.118 | - |
| case3D:sparse_array | accel_ic/gmres | converged | 5546 | 1.0e-08 | - | 1.8 | 69 | 71 | 0.373 | - |
| case3D:sparse_array | accel_ic/cocg | converged | 3768 | 9.8e-09 | - | 1.8 | 9.8 | 12 | 0.097 | - |
| case3D:sparse_array | cslp/gmres | converged | 246 | 8.2e-09 | - | 2.4 | 21 | 23 | 0.408 | - |
| case3D:sparse_array | hx/gmres | converged | 253 | 6.7e-09 | - | 2.7 | 9.5 | 12 | 0.488 | - |
| case3D:sparse_array | cslp_hx/gmres | converged | 146 | 8.9e-09 | - | 2.6 | 12 | 15 | 0.416 | - |
| case3D:sparse_array | npatch_asm/cocg | converged | 2280 | 6.8e-09 | - | 2.5 | 12 | 14 | 0.265 | - |
| case3D:sparse_array | mumps/direct | converged | 1 | 1.6e-12 | - | 2.4 | 0.0 | 2.4 | 0.12 | - |
| case3D:dense_array | gs/gmres | max_it | 10000 | 3.0e-04 | - | 6.7 | 219 | 226 | 0.725 | - |
| case3D:dense_array | ssor/gmres | max_it | 10000 | 2.5e-05 | - | 6.7 | 233 | 240 | 0.725 | - |
| case3D:dense_array | ssor/cocg | converged | 7499 | 1.0e-08 | - | 6.6 | 87 | 93 | 0.303 | - |
| case3D:dense_array | amg_gamg/gmres | max_it | 10000 | 5.3e-05 | - | 7.2 | 314 | 322 | 0.795 | - |
| case3D:dense_array | amg_gamg/cocg | converged | 8186 | 9.6e-09 | - | 6.6 | 163 | 170 | 0.423 | - |
| case3D:dense_array | accel_ic/gmres | max_it | 10000 | 2.3e-05 | - | 6.8 | 480 | 486 | 1.4 | - |
| case3D:dense_array | accel_ic/cocg | converged | 8335 | 9.6e-09 | - | 6.7 | 85 | 92 | 0.346 | - |
| case3D:dense_array | cslp/gmres | converged | 1080 | 9.9e-09 | - | 9.1 | 380 | 389 | 1.558 | - |
| case3D:dense_array | hx/gmres | max_it | 10000 | 4.2e-04 | - | 11 | 1512 | 1522 | 1.873 | - |
| case3D:dense_array | cslp_hx/gmres | max_it | 1000 | 8.0e-07 | - | 9.7 | 368 | 378 | 1.579 | - |
| case3D:dense_array | npatch_asm/cocg | converged | 22079 | 8.3e-09 | - | 9.9 | 433 | 443 | 1.01 | - |
| case3D:dense_array | mumps/direct | converged | 1 | 2.0e-12 | - | 10.0 | 0.1 | 10 | 1.432 | - |
| case3E:low_loss | gs/gmres | max_it | 10000 | 1.2e-05 | - | 5.0 | 160 | 165 | 0.531 | - |
| case3E:low_loss | ssor/gmres | max_it | 10000 | 6.0e-08 | - | 5.0 | 172 | 177 | 0.531 | - |
| case3E:low_loss | ssor/cocg | converged | 5434 | 9.9e-09 | - | 4.9 | 47 | 52 | 0.221 | - |
| case3E:low_loss | amg_gamg/gmres | max_it | 10000 | 9.3e-05 | - | 5.4 | 233 | 238 | 0.583 | - |
| case3E:low_loss | amg_gamg/cocg | max_it | 50000 | 1.2e-05 | - | 5.0 | 749 | 754 | 0.317 | - |
| case3E:low_loss | accel_ic/gmres | max_it | 10000 | 3.1e-07 | - | 5.0 | 351 | 356 | 1.027 | - |
| case3E:low_loss | accel_ic/cocg | converged | 6295 | 9.3e-09 | - | 5.0 | 48 | 53 | 0.263 | - |
| case3E:low_loss | cslp/gmres | converged | 1456 | 1.0e-08 | - | 6.7 | 392 | 398 | 1.139 | - |
| case3E:low_loss | hx/gmres | converged | 8471 | 1.0e-08 | - | 7.9 | 744 | 752 | 1.306 | - |
| case3E:low_loss | cslp_hx/gmres | max_it | 1000 | 8.1e-07 | - | 7.2 | 279 | 286 | 1.155 | - |
| case3E:low_loss | npatch_asm/cocg | converged | 6802 | 9.3e-09 | - | 7.2 | 102 | 109 | 0.789 | - |
| case3E:low_loss | mumps/direct | converged | 1 | 1.9e-13 | - | 8.7 | 0.1 | 8.9 | 1.751 | - |
| case3E:medium_loss | gs/gmres | converged | 4713 | 1.0e-08 | - | 4.9 | 75 | 80 | 0.531 | - |
| case3E:medium_loss | ssor/gmres | converged | 2786 | 1.0e-08 | - | 4.9 | 47 | 52 | 0.531 | - |
| case3E:medium_loss | ssor/cocg | converged | 2932 | 8.9e-09 | - | 5.0 | 26 | 31 | 0.221 | - |
| case3E:medium_loss | amg_gamg/gmres | converged | 7923 | 1.0e-08 | - | 5.4 | 184 | 189 | 0.583 | - |
| case3E:medium_loss | amg_gamg/cocg | converged | 33820 | 7.6e-09 | - | 4.9 | 505 | 510 | 0.317 | - |
| case3E:medium_loss | accel_ic/gmres | converged | 3190 | 1.0e-08 | - | 5.0 | 110 | 116 | 1.027 | - |
| case3E:medium_loss | accel_ic/cocg | converged | 3414 | 8.0e-09 | - | 5.0 | 26 | 31 | 0.263 | - |
| case3E:medium_loss | cslp/gmres | converged | 347 | 9.8e-09 | - | 6.8 | 93 | 99 | 1.138 | - |
| case3E:medium_loss | hx/gmres | converged | 1091 | 1.0e-08 | - | 7.8 | 94 | 102 | 1.31 | - |
| case3E:medium_loss | cslp_hx/gmres | converged | 348 | 9.8e-09 | - | 7.1 | 97 | 104 | 1.155 | - |
| case3E:medium_loss | npatch_asm/cocg | converged | 2851 | 1.0e-08 | - | 7.2 | 42 | 50 | 0.79 | - |
| case3E:medium_loss | mumps/direct | converged | 1 | 3.8e-14 | - | 8.9 | 0.1 | 9.1 | 1.947 | - |
| case3E:high_loss | gs/gmres | converged | 4840 | 1.0e-08 | - | 5.0 | 78 | 83 | 0.531 | - |
| case3E:high_loss | ssor/gmres | converged | 2892 | 1.0e-08 | - | 5.0 | 49 | 54 | 0.531 | - |
| case3E:high_loss | ssor/cocg | converged | 2756 | 8.9e-09 | - | 5.0 | 24 | 29 | 0.221 | - |
| case3E:high_loss | amg_gamg/gmres | converged | 7922 | 1.0e-08 | - | 5.4 | 184 | 190 | 0.583 | - |
| case3E:high_loss | amg_gamg/cocg | converged | 13691 | 9.5e-09 | - | 4.9 | 206 | 210 | 0.317 | - |
| case3E:high_loss | accel_ic/gmres | converged | 3222 | 1.0e-08 | - | 5.0 | 112 | 117 | 1.028 | - |
| case3E:high_loss | accel_ic/cocg | converged | 3379 | 6.5e-09 | - | 5.0 | 26 | 31 | 0.264 | - |
| case3E:high_loss | cslp/gmres | converged | 224 | 9.4e-09 | - | 6.7 | 59 | 65 | 1.139 | - |
| case3E:high_loss | hx/gmres | converged | 677 | 1.0e-08 | - | 7.8 | 69 | 76 | 1.306 | - |
| case3E:high_loss | cslp_hx/gmres | converged | 202 | 9.5e-09 | - | 7.1 | 55 | 62 | 1.155 | - |
| case3E:high_loss | npatch_asm/cocg | converged | 2573 | 6.1e-09 | - | 7.2 | 39 | 46 | 0.79 | - |
| case3E:high_loss | mumps/direct | converged | 1 | 3.7e-14 | - | 8.8 | 0.1 | 9.0 | 1.752 | - |
| case3F:low_contrast_no_loss | gs/gmres | max_it | 10000 | 1.2e-02 | - | 5.9 | 194 | 199 | 0.638 | - |
| case3F:low_contrast_no_loss | ssor/gmres | max_it | 10000 | 3.1e-05 | - | 5.8 | 206 | 212 | 0.638 | - |
| case3F:low_contrast_no_loss | ssor/cocg | converged | 2150 | 9.6e-09 | - | 5.8 | 22 | 28 | 0.266 | - |
| case3F:low_contrast_no_loss | amg_gamg/gmres | max_it | 10000 | 2.3e-06 | - | 6.4 | 276 | 282 | 0.704 | - |
| case3F:low_contrast_no_loss | amg_gamg/cocg | converged | 2026 | 9.8e-09 | - | 5.9 | 36 | 42 | 0.373 | - |
| case3F:low_contrast_no_loss | accel_ic/gmres | max_it | 10000 | 4.9e-04 | - | 6.0 | 423 | 429 | 1.233 | - |
| case3F:low_contrast_no_loss | accel_ic/cocg | converged | 2611 | 9.3e-09 | - | 5.9 | 24 | 30 | 0.304 | - |
| case3F:low_contrast_no_loss | cslp/gmres | converged | 137 | 8.4e-09 | - | 8.0 | 41 | 49 | 1.374 | - |
| case3F:low_contrast_no_loss | hx/gmres | converged | 73 | 6.5e-09 | - | 9.2 | 8.0 | 17 | 1.661 | - |
| case3F:low_contrast_no_loss | cslp_hx/gmres | converged | 53 | 4.2e-09 | - | 8.4 | 16 | 25 | 1.388 | - |
| case3F:low_contrast_no_loss | npatch_asm/cocg | converged | 486 | 7.4e-09 | - | 8.6 | 8.5 | 17 | 0.882 | - |
| case3F:low_contrast_no_loss | mumps/direct | converged | 1 | 6.8e-12 | - | 8.4 | 0.1 | 8.6 | 1.117 | - |
| case3F:high_contrast_with_loss | gs/gmres | max_it | 10000 | 6.6e-02 | - | 5.8 | 194 | 199 | 0.639 | - |
| case3F:high_contrast_with_loss | ssor/gmres | max_it | 10000 | 2.9e-02 | - | 5.9 | 206 | 212 | 0.638 | - |
| case3F:high_contrast_with_loss | ssor/cocg | converged | 8323 | 8.9e-09 | - | 5.9 | 85 | 91 | 0.266 | - |
| case3F:high_contrast_with_loss | amg_gamg/gmres | max_it | 10000 | 3.2e-02 | - | 6.3 | 276 | 282 | 0.701 | - |
| case3F:high_contrast_with_loss | amg_gamg/cocg | converged | 9308 | 8.5e-09 | - | 5.9 | 164 | 170 | 0.373 | - |
| case3F:high_contrast_with_loss | accel_ic/gmres | max_it | 10000 | 3.7e-02 | - | 5.9 | 423 | 429 | 1.233 | - |
| case3F:high_contrast_with_loss | accel_ic/cocg | converged | 9660 | 9.5e-09 | - | 6.0 | 87 | 93 | 0.304 | - |
| case3F:high_contrast_with_loss | cslp/gmres | converged | 1896 | 1.0e-08 | - | 7.9 | 589 | 597 | 1.374 | - |
| case3F:high_contrast_with_loss | hx/gmres | converged | 1707 | 1.0e-08 | - | 9.2 | 199 | 208 | 1.661 | - |
| case3F:high_contrast_with_loss | cslp_hx/gmres | converged | 298 | 9.1e-09 | - | 8.4 | 97 | 106 | 1.388 | - |
| case3F:high_contrast_with_loss | npatch_asm/cocg | converged | 6171 | 7.4e-09 | - | 8.8 | 109 | 118 | 0.882 | - |
| case3F:high_contrast_with_loss | mumps/direct | converged | 1 | 5.4e-12 | - | 8.5 | 0.1 | 8.7 | 1.108 | - |
| case3F:ultra_contrast_high_loss | gs/gmres | max_it | 10000 | 4.5e-02 | - | 5.9 | 193 | 199 | 0.638 | - |
| case3F:ultra_contrast_high_loss | ssor/gmres | max_it | 10000 | 1.2e-02 | - | 5.8 | 206 | 212 | 0.638 | - |
| case3F:ultra_contrast_high_loss | ssor/cocg | converged | 14983 | 8.4e-09 | - | 5.9 | 154 | 160 | 0.266 | - |
| case3F:ultra_contrast_high_loss | amg_gamg/gmres | max_it | 10000 | 1.4e-02 | - | 6.3 | 276 | 283 | 0.701 | - |
| case3F:ultra_contrast_high_loss | amg_gamg/cocg | converged | 20503 | 9.1e-09 | - | 6.0 | 360 | 366 | 0.373 | - |
| case3F:ultra_contrast_high_loss | accel_ic/gmres | max_it | 10000 | 1.5e-02 | - | 5.9 | 423 | 429 | 1.233 | - |
| case3F:ultra_contrast_high_loss | accel_ic/cocg | converged | 18674 | 1.0e-08 | - | 5.9 | 169 | 175 | 0.304 | - |
| case3F:ultra_contrast_high_loss | cslp/gmres | max_it | 3000 | 1.1e-08 | - | 8.0 | 935 | 943 | 1.374 | - |
| case3F:ultra_contrast_high_loss | hx/gmres | max_it | 10000 | 2.1e-05 | - | 9.1 | 1178 | 1187 | 1.661 | - |
| case3F:ultra_contrast_high_loss | cslp_hx/gmres | max_it | 1000 | 9.3e-06 | - | 8.4 | 324 | 333 | 1.388 | - |
| case3F:ultra_contrast_high_loss | npatch_asm/cocg | converged | 18290 | 9.6e-09 | - | 8.5 | 325 | 334 | 0.882 | - |
| case3F:ultra_contrast_high_loss | mumps/direct | converged | 1 | 2.8e-12 | - | 8.4 | 0.1 | 8.6 | 1.107 | - |

## 上限に達した結果の補足情報

| case | combination | status | it | K_max | r_hat | s | N_est | N_est/K | rho_cyc | 最終更新 | 窓での減少 | 判定 | total [s] | s/it | 推定時間 [s] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01-1 | gs/gmres | max_it | 10000 | 10000 | 2.2e-03 | -8.62e-05 | 7.19e+04 | 7.2 | 0.9445 | 10000 | 0.659 | 停滞 | 123 | 0.0119 | 858 |
| P01-1 | ssor/gmres | max_it | 10000 | 10000 | 5.4e-04 | -1.04e-04 | 5.54e+04 | 5.5 | 0.9328 | 10000 | 0.606 | 停滞 | 130 | 0.0126 | 702 |
| P01-1 | amg_gamg/gmres | max_it | 10000 | 10000 | 5.6e-04 | -9.83e-05 | 5.83e+04 | 5.8 | 0.9357 | 10000 | 0.631 | 停滞 | 173 | 0.0169 | 988 |
| P01-1 | accel_ic/gmres | max_it | 10000 | 10000 | 7.9e-04 | -9.16e-05 | 6.35e+04 | 6.3 | 0.9421 | 10000 | 0.642 | 停滞 | 263 | 0.0259 | 1646 |
| P01-2 | gs/gmres | max_it | 10000 | 10000 | 3.2e-06 | -3.68e-04 | 1.68e+04 | 1.7 | 0.7758 | 10000 | 0.174 | 遅い収束 | 149 | 0.0145 | 247 |
| P01-2 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.4e-08 | -5.76e-04 | 1.03e+04 | 1 | 0.6853 | 10000 | 0.06 | 遅い収束 | 212 | 0.0207 | 217 |
| P01-3 | gs/gmres | max_it | 10000 | 10000 | 2.4e-03 | -3.70e-05 | 1.55e+05 | 16 | 0.9781 | 10000 | 0.836 | 停滞 | 122 | 0.0118 | 1841 |
| P01-3 | ssor/gmres | max_it | 10000 | 10000 | 4.9e-04 | -9.51e-05 | 5.93e+04 | 5.9 | 0.9324 | 10000 | 0.658 | 停滞 | 130 | 0.0126 | 753 |
| P01-3 | amg_gamg/gmres | max_it | 10000 | 10000 | 5.6e-04 | -5.97e-05 | 8.95e+04 | 9 | 0.9626 | 10000 | 0.757 | 停滞 | 173 | 0.0169 | 1515 |
| P01-3 | accel_ic/gmres | max_it | 10000 | 10000 | 7.3e-04 | -5.08e-05 | 1.06e+05 | 11 | 0.9706 | 10000 | 0.792 | 停滞 | 263 | 0.0259 | 2739 |
| P01-1_coarse | gs/gmres | max_it | 10000 | 10000 | 3.8e-04 | -1.35e-04 | 4.39e+04 | 4.4 | 0.9119 | 10000 | 0.52 | 停滞 | 30 | 0.0029 | 129 |
| P01-1_coarse | ssor/gmres | max_it | 10000 | 10000 | 9.0e-06 | -2.57e-04 | 2.15e+04 | 2.1 | 0.8428 | 10000 | 0.289 | 遅い収束 | 32 | 0.0031 | 68 |
| P01-1_coarse | amg_gamg/gmres | max_it | 10000 | 10000 | 1.1e-05 | -2.61e-04 | 2.16e+04 | 2.2 | 0.8376 | 10000 | 0.284 | 遅い収束 | 41 | 0.004 | 88 |
| P01-1_coarse | accel_ic/gmres | max_it | 10000 | 10000 | 5.0e-05 | -1.98e-04 | 2.87e+04 | 2.9 | 0.8715 | 10000 | 0.381 | 遅い収束 | 70 | 0.0068 | 197 |
| P01-1_fine | gs/gmres | max_it | 10000 | 10000 | 8.8e-03 | -4.93e-05 | 1.31e+05 | 13 | 0.9585 | 10000 | 0.776 | 停滞 | 639 | 0.062 | 8120 |
| P01-1_fine | ssor/gmres | max_it | 10000 | 10000 | 2.7e-03 | -8.43e-05 | 7.43e+04 | 7.4 | 0.9423 | 10000 | 0.66 | 停滞 | 684 | 0.0665 | 4960 |
| P01-1_fine | amg_gamg/gmres | max_it | 10000 | 10000 | 4.8e-03 | -7.09e-05 | 9.01e+04 | 9 | 0.9643 | 10000 | 0.722 | 停滞 | 943 | 0.0922 | 8325 |
| P01-1_fine | accel_ic/gmres | max_it | 10000 | 10000 | 3.2e-03 | -7.44e-05 | 8.41e+04 | 8.4 | 0.9458 | 10000 | 0.678 | 停滞 | 1364 | 0.1344 | 11321 |
| P01-1_sibc | gs/gmres | max_it | 10000 | 10000 | 2.2e-03 | -8.62e-05 | 7.19e+04 | 7.2 | 0.9451 | 10000 | 0.659 | 停滞 | 122 | 0.0118 | 854 |
| P01-1_sibc | ssor/gmres | max_it | 10000 | 10000 | 5.4e-04 | -1.05e-04 | 5.5e+04 | 5.5 | 0.932 | 10000 | 0.604 | 停滞 | 130 | 0.0126 | 699 |
| P01-1_sibc | amg_gamg/gmres | max_it | 10000 | 10000 | 5.9e-04 | -1.00e-04 | 5.77e+04 | 5.8 | 0.9323 | 10000 | 0.636 | 停滞 | 173 | 0.0169 | 978 |
| P01-1_sibc | accel_ic/gmres | max_it | 10000 | 10000 | 7.7e-04 | -9.77e-05 | 6e+04 | 6 | 0.9351 | 10000 | 0.627 | 停滞 | 263 | 0.0259 | 1556 |
| P01-2_sibc | gs/gmres | max_it | 10000 | 10000 | 3.1e-06 | -3.68e-04 | 1.68e+04 | 1.7 | 0.7771 | 10000 | 0.174 | 遅い収束 | 149 | 0.0144 | 247 |
| P01-2_sibc | amg_gamg/gmres | max_it | 10000 | 10000 | 1.7e-08 | -6.01e-04 | 1.04e+04 | 1 | 0.6621 | 10000 | 0.061 | 遅い収束 | 212 | 0.0207 | 220 |
| P01-a_f0.5 | gs/gmres | max_it | 10000 | 10000 | 3.3e-03 | -6.74e-05 | 9.19e+04 | 9.2 | 0.9555 | 10000 | 0.725 | 停滞 | 122 | 0.0118 | 1090 |
| P01-a_f0.5 | ssor/gmres | max_it | 10000 | 10000 | 1.0e-03 | -8.00e-05 | 7.27e+04 | 7.3 | 0.95 | 10000 | 0.68 | 停滞 | 130 | 0.0126 | 922 |
| P01-a_f0.5 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.0e-03 | -8.19e-05 | 7.11e+04 | 7.1 | 0.9494 | 10000 | 0.677 | 停滞 | 173 | 0.0169 | 1204 |
| P01-a_f0.5 | accel_ic/gmres | max_it | 10000 | 10000 | 1.3e-03 | -7.45e-05 | 7.88e+04 | 7.9 | 0.9532 | 10000 | 0.697 | 停滞 | 263 | 0.0259 | 2043 |
| P01-a_f2 | gs/gmres | max_it | 10000 | 10000 | 1.5e-03 | -1.00e-04 | 6.15e+04 | 6.2 | 0.9337 | 10000 | 0.598 | 停滞 | 122 | 0.0118 | 730 |
| P01-a_f2 | ssor/gmres | max_it | 10000 | 10000 | 1.7e-04 | -1.59e-04 | 3.65e+04 | 3.7 | 0.8976 | 10000 | 0.469 | 遅い収束 | 130 | 0.0126 | 465 |
| P01-a_f2 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.0e-04 | -1.53e-04 | 3.81e+04 | 3.8 | 0.8999 | 10000 | 0.483 | 遅い収束 | 173 | 0.0169 | 648 |
| P01-a_f2 | accel_ic/gmres | max_it | 10000 | 10000 | 3.5e-04 | -1.28e-04 | 4.56e+04 | 4.6 | 0.9175 | 10000 | 0.547 | 停滞 | 263 | 0.0259 | 1184 |
| P01-a_f5 | gs/gmres | max_it | 10000 | 10000 | 1.5e-04 | -2.27e-04 | 2.85e+04 | 2.8 | 0.8577 | 10000 | 0.326 | 遅い収束 | 123 | 0.0119 | 343 |
| P01-a_f5 | ssor/gmres | max_it | 10000 | 10000 | 8.8e-07 | -4.07e-04 | 1.48e+04 | 1.5 | 0.7623 | 10000 | 0.142 | 遅い収束 | 131 | 0.0128 | 192 |
| P01-a_f5 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.7e-06 | -3.90e-04 | 1.62e+04 | 1.6 | 0.7553 | 10000 | 0.145 | 遅い収束 | 175 | 0.0171 | 282 |
| P01-a_f5 | accel_ic/gmres | max_it | 10000 | 10000 | 5.1e-06 | -3.79e-04 | 1.71e+04 | 1.7 | 0.7768 | 10000 | 0.162 | 遅い収束 | 268 | 0.0264 | 455 |
| P01-a_f20 | hx/gmres | max_it | 10000 | 10000 | 1.5e-05 | -2.80e-04 | 2.14e+04 | 2.1 | 0.8319 | 10000 | 0.251 | 遅い収束 | 2795 | 0.2777 | 5954 |
| P01-b_L32.9 | gs/gmres | max_it | 10000 | 10000 | 1.0e-06 | -4.03e-04 | 1.5e+04 | 1.5 | 0.774 | 10000 | 0.149 | 遅い収束 | 127 | 0.0124 | 189 |
| P01-b_L65.7 | gs/gmres | max_it | 10000 | 10000 | 5.4e-05 | -2.79e-04 | 2.34e+04 | 2.3 | 0.8317 | 10000 | 0.259 | 遅い収束 | 232 | 0.0225 | 532 |
| P01-b_L65.7 | ssor/gmres | max_it | 10000 | 10000 | 3.7e-08 | -5.68e-04 | 1.1e+04 | 1.1 | 0.6656 | 10000 | 0.064 | 遅い収束 | 248 | 0.0241 | 271 |
| P01-b_L65.7 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.8e-06 | -4.47e-04 | 1.5e+04 | 1.5 | 0.7374 | 10000 | 0.111 | 遅い収束 | 331 | 0.0324 | 493 |
| P01-b_L65.7 | accel_ic/gmres | max_it | 10000 | 10000 | 2.2e-07 | -5.18e-04 | 1.26e+04 | 1.3 | 0.7046 | 10000 | 0.084 | 遅い収束 | 496 | 0.0489 | 623 |
| P01-b_L131.4 | gs/gmres | max_it | 10000 | 10000 | 8.6e-04 | -2.81e-04 | 2.75e+04 | 2.8 | 0.7394 | 10000 | 0.256 | 遅い収束 | 442 | 0.0429 | 1193 |
| P01-b_L131.4 | ssor/gmres | max_it | 10000 | 10000 | 8.2e-06 | -3.44e-04 | 1.85e+04 | 1.8 | 0.7872 | 10000 | 0.167 | 遅い収束 | 472 | 0.0459 | 860 |
| P01-b_L131.4 | amg_gamg/gmres | max_it | 10000 | 10000 | 4.4e-04 | -3.83e-04 | 2.21e+04 | 2.2 | 0.8473 | 10000 | 0.178 | 遅い収束 | 643 | 0.0628 | 1404 |
| P01-b_L131.4 | accel_ic/gmres | max_it | 10000 | 10000 | 3.1e-05 | -3.91e-04 | 1.89e+04 | 1.9 | 0.7121 | 10000 | 0.164 | 遅い収束 | 940 | 0.0927 | 1767 |
| P01-1_td0 | gs/gmres | max_it | 10000 | 10000 | 2.2e-03 | -8.61e-05 | 7.2e+04 | 7.2 | 0.9443 | 10000 | 0.657 | 停滞 | 122 | 0.0118 | 854 |
| P01-1_td0 | ssor/gmres | max_it | 10000 | 10000 | 5.4e-04 | -1.04e-04 | 5.54e+04 | 5.5 | 0.9328 | 10000 | 0.606 | 停滞 | 130 | 0.0126 | 703 |
| P01-1_td0 | amg_gamg/gmres | max_it | 10000 | 10000 | 5.7e-04 | -9.80e-05 | 5.85e+04 | 5.9 | 0.9353 | 10000 | 0.633 | 停滞 | 173 | 0.0169 | 992 |
| P01-1_td0 | accel_ic/gmres | max_it | 10000 | 10000 | 7.9e-04 | -9.23e-05 | 6.31e+04 | 6.3 | 0.9414 | 10000 | 0.641 | 停滞 | 263 | 0.0259 | 1635 |
| P01-1_td0.02 | gs/gmres | max_it | 10000 | 10000 | 2.0e-03 | -8.53e-05 | 7.23e+04 | 7.2 | 0.9465 | 10000 | 0.666 | 停滞 | 122 | 0.0118 | 858 |
| P01-1_td0.02 | ssor/gmres | max_it | 10000 | 10000 | 5.2e-04 | -1.05e-04 | 5.5e+04 | 5.5 | 0.9328 | 10000 | 0.605 | 停滞 | 130 | 0.0126 | 696 |
| P01-1_td0.02 | amg_gamg/gmres | max_it | 10000 | 10000 | 5.5e-04 | -9.86e-05 | 5.81e+04 | 5.8 | 0.9364 | 10000 | 0.634 | 停滞 | 173 | 0.0169 | 984 |
| P01-1_td0.02 | accel_ic/gmres | max_it | 10000 | 10000 | 7.6e-04 | -9.07e-05 | 6.38e+04 | 6.4 | 0.9419 | 10000 | 0.644 | 停滞 | 263 | 0.0259 | 1656 |
| P01-2_td0 | gs/gmres | max_it | 10000 | 10000 | 3.5e-06 | -3.72e-04 | 1.68e+04 | 1.7 | 0.7659 | 10000 | 0.172 | 遅い収束 | 149 | 0.0144 | 247 |
| P01-2_td0 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.5e-08 | -5.83e-04 | 1.03e+04 | 1 | 0.6762 | 10000 | 0.06 | 遅い収束 | 212 | 0.0207 | 218 |
| P01-2_td0.02 | gs/gmres | max_it | 10000 | 10000 | 1.8e-06 | -3.88e-04 | 1.58e+04 | 1.6 | 0.7663 | 10000 | 0.153 | 遅い収束 | 149 | 0.0144 | 233 |
| P01-1_t | gs/gmres | max_it | 10000 | 10000 | 2.0e-02 | -2.97e-05 | 2.22e+05 | 22 | 0.9832 | 10000 | 0.871 | 停滞 | 620 | 0.06 | 13339 |
| P01-1_t | ssor/gmres | max_it | 10000 | 10000 | 1.3e-02 | -3.15e-05 | 2.04e+05 | 20 | 0.9778 | 10000 | 0.85 | 停滞 | 661 | 0.0642 | 13127 |
| P01-1_t | ssor/cocg | max_it | 50000 | 50000 | 2.5e-04 | -5.10e-05 | 1.36e+05 | 2.7 | - | 46075 | 0.075 | 遅い収束 | 1652 | 0.0326 | 4464 |
| P01-1_t | amg_gamg/gmres | max_it | 10000 | 10000 | 1.2e-02 | -3.42e-05 | 1.87e+05 | 19 | 0.9808 | 10000 | 0.844 | 停滞 | 912 | 0.0891 | 16705 |
| P01-1_t | amg_gamg/cocg | max_it | 50000 | 50000 | 1.0e-03 | -5.20e-05 | 1.46e+05 | 2.9 | - | 48643 | 0.101 | 遅い収束 | 2864 | 0.0569 | 8345 |
| P01-1_t | accel_ic/gmres | max_it | 10000 | 10000 | 1.3e-02 | -3.07e-05 | 2.09e+05 | 21 | 0.9818 | 10000 | 0.855 | 停滞 | 1318 | 0.1299 | 27216 |
| P01-1_t | accel_ic/cocg | max_it | 50000 | 50000 | 4.7e-04 | -2.93e-05 | 2.09e+05 | 4.2 | - | 49544 | 0.022 | 遅い収束 | 1443 | 0.0285 | 5975 |
| P01-1_t | cslp/gmres | max_it | 3000 | 3000 | 3.7e-05 | -4.46e-04 | 1.1e+04 | 3.7 | 0.7355 | 3000 | 0.539 | 停滞 | 3159 | 1.0444 | 11522 |
| P01-2_t | gs/gmres | max_it | 10000 | 10000 | 3.3e-02 | -5.72e-05 | 1.24e+05 | 12 | 0.9694 | 10000 | 0.779 | 停滞 | 647 | 0.0627 | 7804 |
| P01-2_t | ssor/gmres | max_it | 10000 | 10000 | 1.8e-02 | -4.63e-05 | 1.45e+05 | 14 | 0.9628 | 10000 | 0.803 | 停滞 | 692 | 0.0672 | 9749 |
| P01-2_t | ssor/cocg | max_it | 50000 | 50000 | 1.8e-06 | -1.12e-04 | 7.02e+04 | 1.4 | - | 44428 | 0.004 | 遅い収束 | 1724 | 0.0341 | 2409 |
| P01-2_t | amg_gamg/gmres | max_it | 10000 | 10000 | 1.9e-02 | -5.77e-05 | 1.19e+05 | 12 | 0.9582 | 10000 | 0.768 | 停滞 | 956 | 0.0934 | 11116 |
| P01-2_t | amg_gamg/cocg | max_it | 50000 | 50000 | 1.5e-04 | -5.86e-05 | 1.21e+05 | 2.4 | - | 49684 | 0.047 | 遅い収束 | 3004 | 0.0597 | 7266 |
| P01-2_t | accel_ic/gmres | max_it | 10000 | 10000 | 1.6e-02 | -6.04e-05 | 1.13e+05 | 11 | 0.972 | 10000 | 0.767 | 停滞 | 1378 | 0.1357 | 15324 |
| P01-2_t | accel_ic/cocg | max_it | 50000 | 50000 | 9.1e-06 | -9.91e-05 | 7.99e+04 | 1.6 | - | 47858 | 0.003 | 遅い収束 | 1509 | 0.0298 | 2395 |
| P01-2_t | cslp/gmres | max_it | 3000 | 3000 | 3.7e-05 | -6.65e-04 | 8.36e+03 | 2.8 | 0.5961 | 3000 | 0.378 | 遅い収束 | 3324 | 1.0988 | 9213 |
| P02-a_h0.2 | gs/gmres | max_it | 10000 | 10000 | 1.6e-03 | -1.82e-04 | 3.85e+04 | 3.9 | 0.885 | 10000 | 0.42 | 遅い収束 | 103 | 0.01 | 388 |
| P02-a_h0.2 | ssor/gmres | max_it | 10000 | 10000 | 4.7e-06 | -4.16e-04 | 1.64e+04 | 1.6 | 0.7518 | 10000 | 0.136 | 遅い収束 | 110 | 0.0107 | 178 |
| P02-a_h0.2 | amg_gamg/gmres | max_it | 10000 | 10000 | 3.2e-04 | -2.27e-04 | 2.99e+04 | 3 | 0.8534 | 10000 | 0.334 | 遅い収束 | 145 | 0.0141 | 425 |
| P02-a_h0.2 | accel_ic/gmres | max_it | 10000 | 10000 | 3.5e-05 | -3.18e-04 | 2.11e+04 | 2.1 | 0.8065 | 10000 | 0.214 | 遅い収束 | 227 | 0.0223 | 475 |
| P02-a_h0.05 | gs/gmres | max_it | 10000 | 10000 | 1.9e-02 | -7.97e-05 | 8.86e+04 | 8.9 | 0.9472 | 10000 | 0.681 | 停滞 | 102 | 0.0099 | 879 |
| P02-a_h0.05 | ssor/gmres | max_it | 10000 | 10000 | 1.2e-03 | -1.83e-04 | 3.77e+04 | 3.8 | 0.8798 | 10000 | 0.411 | 遅い収束 | 109 | 0.0106 | 401 |
| P02-a_h0.05 | amg_gamg/gmres | max_it | 10000 | 10000 | 6.6e-03 | -1.15e-04 | 6.08e+04 | 6.1 | 0.9307 | 10000 | 0.573 | 停滞 | 143 | 0.014 | 853 |
| P02-a_h0.05 | accel_ic/gmres | max_it | 10000 | 10000 | 2.4e-03 | -1.50e-04 | 4.57e+04 | 4.6 | 0.9042 | 10000 | 0.483 | 停滞 | 224 | 0.0221 | 1013 |
| P02-b_h0.2 | gs/gmres | max_it | 10000 | 10000 | 6.4e-02 | -5.61e-06 | 1.22e+06 | 1.2e+02 | 0.9966 | 10000 | 0.973 | 停滞 | 688 | 0.0668 | 81701 |
| P02-b_h0.2 | ssor/gmres | max_it | 10000 | 10000 | 5.3e-02 | -6.36e-06 | 1.07e+06 | 1.1e+02 | 0.9959 | 10000 | 0.97 | 停滞 | 735 | 0.0714 | 76240 |
| P02-b_h0.2 | ssor/cocg | max_it | 50000 | 50000 | 1.9e-04 | -1.01e-04 | 9.23e+04 | 1.8 | - | 48688 | 0.003 | 遅い収束 | 1865 | 0.0369 | 3424 |
| P02-b_h0.2 | amg_gamg/gmres | max_it | 10000 | 10000 | 5.3e-02 | -5.94e-06 | 1.14e+06 | 1.1e+02 | 0.9962 | 10000 | 0.971 | 停滞 | 999 | 0.0976 | 111577 |
| P02-b_h0.2 | amg_gamg/cocg | max_it | 50000 | 50000 | 5.5e-02 | 0.00e+00 | ∞ | ∞ | - | 21036 | 1 | 停滞 | 3171 | 0.063 | ∞ |
| P02-b_h0.2 | accel_ic/gmres | max_it | 10000 | 10000 | 4.6e-02 | -5.83e-06 | 1.15e+06 | 1.2e+02 | 0.9962 | 10000 | 0.972 | 停滞 | 1478 | 0.1456 | 167981 |
| P02-b_h0.2 | accel_ic/cocg | max_it | 50000 | 50000 | 8.1e-03 | -5.38e-05 | 1.6e+05 | 3.2 | - | 49334 | 0.07 | 遅い収束 | 1610 | 0.0318 | 5096 |
| P02-b_h0.2 | cslp/gmres | max_it | 3000 | 3000 | 2.8e-03 | -3.45e-04 | 1.88e+04 | 6.3 | 0.774 | 3000 | 0.606 | 停滞 | 3428 | 1.133 | 21311 |
| P02-b_h0.2 | cslp_hx/gmres | max_it | 1000 | 1000 | 1.5e-03 | -1.01e-03 | 6.13e+03（悲観側） | 6.1 | 0.1239 | 1000 | 0.446 | 遅い収束 | 1186 | 1.1555 | 7108 |
| P02-sr_h1.6 | gs/gmres | max_it | 10000 | 10000 | 3.3e-02 | -5.86e-05 | 1.21e+05 | 12 | 0.9625 | 10000 | 0.774 | 停滞 | 102 | 0.0099 | 1204 |
| P02-sr_h1.6 | ssor/gmres | max_it | 10000 | 10000 | 1.5e-02 | -5.48e-05 | 1.23e+05 | 12 | 0.9307 | 10000 | 0.745 | 停滞 | 109 | 0.0106 | 1303 |
| P02-sr_h1.6 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.1e-02 | -7.65e-05 | 8.91e+04 | 8.9 | 0.9698 | 10000 | 0.73 | 停滞 | 144 | 0.014 | 1253 |
| P02-sr_h1.6 | accel_ic/gmres | max_it | 10000 | 10000 | 1.1e-02 | -6.53e-05 | 1.03e+05 | 10 | 0.9674 | 10000 | 0.723 | 停滞 | 224 | 0.022 | 2265 |
| P03-1 | gs/gmres | max_it | 10000 | 10000 | 4.9e-02 | -2.42e-05 | 2.86e+05 | 29 | 0.9842 | 10000 | 0.89 | 停滞 | 470 | 0.0456 | 13057 |
| P03-1 | ssor/gmres | max_it | 10000 | 10000 | 3.2e-02 | -2.92e-05 | 2.32e+05 | 23 | 0.9803 | 10000 | 0.862 | 停滞 | 501 | 0.0486 | 11305 |
| P03-1 | ssor/cocg | max_it | 50000 | 50000 | 5.8e-07 | -1.26e-04 | 6.4e+04 | 1.3 | - | 46722 | 0.001 | 遅い収束 | 1273 | 0.0252 | 1623 |
| P03-1 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.6e-02 | -3.31e-05 | 2.04e+05 | 20 | 0.9723 | 10000 | 0.842 | 停滞 | 681 | 0.0665 | 13548 |
| P03-1 | amg_gamg/cocg | max_it | 50000 | 50000 | 5.7e-07 | -1.40e-04 | 6.25e+04 | 1.3 | - | 45195 | 0.001 | 遅い収束 | 2165 | 0.043 | 2701 |
| P03-1 | accel_ic/gmres | max_it | 10000 | 10000 | 2.7e-02 | -3.48e-05 | 1.95e+05 | 19 | 0.9786 | 10000 | 0.845 | 停滞 | 992 | 0.0977 | 19036 |
| P03-1 | accel_ic/cocg | max_it | 50000 | 50000 | 4.0e-06 | -1.18e-04 | 7.2e+04 | 1.4 | - | 49709 | 0.001 | 遅い収束 | 1094 | 0.0216 | 1567 |
| P03-1 | cslp/gmres | max_it | 3000 | 3000 | 8.0e-05 | -7.88e-04 | 7.95e+03 | 2.7 | 0.6048 | 3000 | 0.353 | 遅い収束 | 2333 | 0.7707 | 6149 |
| P03-2 | gs/gmres | max_it | 10000 | 10000 | 5.0e-02 | -2.06e-05 | 3.36e+05 | 34 | 0.9861 | 10000 | 0.906 | 停滞 | 470 | 0.0455 | 15287 |
| P03-2 | ssor/gmres | max_it | 10000 | 10000 | 3.1e-02 | -3.29e-05 | 2.07e+05 | 21 | 0.9774 | 10000 | 0.845 | 停滞 | 499 | 0.0484 | 10058 |
| P03-2 | ssor/cocg | max_it | 50000 | 50000 | 9.4e-07 | -1.21e-04 | 6.63e+04 | 1.3 | - | 49665 | 0.001 | 遅い収束 | 1269 | 0.0251 | 1676 |
| P03-2 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.6e-02 | -3.71e-05 | 1.83e+05 | 18 | 0.9695 | 10000 | 0.828 | 停滞 | 678 | 0.0662 | 12108 |
| P03-2 | amg_gamg/cocg | max_it | 50000 | 50000 | 6.0e-07 | -1.33e-04 | 6.33e+04 | 1.3 | - | 46861 | 0.001 | 遅い収束 | 2155 | 0.0428 | 2724 |
| P03-2 | accel_ic/gmres | max_it | 10000 | 10000 | 2.7e-02 | -3.89e-05 | 1.75e+05 | 18 | 0.9757 | 10000 | 0.829 | 停滞 | 989 | 0.0974 | 17067 |
| P03-2 | accel_ic/cocg | max_it | 50000 | 50000 | 2.3e-06 | -1.27e-04 | 6.87e+04 | 1.4 | - | 46840 | 0 | 遅い収束 | 1075 | 0.0212 | 1470 |
| P03-2 | cslp/gmres | max_it | 3000 | 3000 | 6.5e-05 | -7.67e-04 | 7.97e+03 | 2.7 | 0.5937 | 3000 | 0.352 | 遅い収束 | 2330 | 0.7697 | 6153 |
| P03-3 | gs/gmres | max_it | 10000 | 10000 | 5.3e-02 | -1.15e-05 | 5.95e+05 | 59 | 0.9929 | 10000 | 0.946 | 停滞 | 432 | 0.0418 | 24902 |
| P03-3 | ssor/gmres | max_it | 10000 | 10000 | 3.6e-02 | -3.88e-05 | 1.79e+05 | 18 | 0.9715 | 10000 | 0.833 | 停滞 | 460 | 0.0446 | 7998 |
| P03-3 | ssor/cocg | max_it | 50000 | 50000 | 4.2e-07 | -1.35e-04 | 6.2e+04 | 1.2 | - | 47690 | 0 | 遅い収束 | 1178 | 0.0233 | 1455 |
| P03-3 | amg_gamg/gmres | max_it | 10000 | 10000 | 3.0e-02 | -4.25e-05 | 1.63e+05 | 16 | 0.9734 | 10000 | 0.818 | 停滞 | 624 | 0.061 | 9928 |
| P03-3 | amg_gamg/cocg | max_it | 50000 | 50000 | 4.3e-07 | -1.37e-04 | 6.19e+04 | 1.2 | - | 46944 | 0 | 遅い収束 | 1994 | 0.0396 | 2463 |
| P03-3 | accel_ic/gmres | max_it | 10000 | 10000 | 3.2e-02 | -2.77e-05 | 2.45e+05 | 25 | 0.9803 | 10000 | 0.872 | 停滞 | 918 | 0.0904 | 22175 |
| P03-3 | accel_ic/cocg | max_it | 50000 | 50000 | 1.2e-05 | -1.17e-04 | 7.61e+04 | 1.5 | - | 48549 | 0.001 | 遅い収束 | 1015 | 0.02 | 1537 |
| P03-3 | cslp/gmres | max_it | 3000 | 3000 | 1.6e-04 | -5.75e-04 | 1.03e+04 | 3.4 | 0.6399 | 3000 | 0.429 | 遅い収束 | 2145 | 0.7088 | 7330 |
| P03-r1 | gs/gmres | max_it | 10000 | 10000 | 5.1e-02 | -1.67e-05 | 4.12e+05 | 41 | 0.9885 | 10000 | 0.923 | 停滞 | 444 | 0.0429 | 17722 |
| P03-r1 | ssor/gmres | max_it | 10000 | 10000 | 3.3e-02 | -3.29e-05 | 2.08e+05 | 21 | 0.9774 | 10000 | 0.853 | 停滞 | 472 | 0.0458 | 9529 |
| P03-r1 | ssor/cocg | max_it | 50000 | 50000 | 8.8e-07 | -1.30e-04 | 6.5e+04 | 1.3 | - | 48109 | 0.001 | 遅い収束 | 1200 | 0.0237 | 1554 |
| P03-r1 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.8e-02 | -3.29e-05 | 2.06e+05 | 21 | 0.9786 | 10000 | 0.854 | 停滞 | 641 | 0.0625 | 12900 |
| P03-r1 | amg_gamg/cocg | max_it | 50000 | 50000 | 3.3e-07 | -1.29e-04 | 6.18e+04 | 1.2 | - | 48088 | 0 | 遅い収束 | 2034 | 0.0404 | 2508 |
| P03-r1 | accel_ic/gmres | max_it | 10000 | 10000 | 2.8e-02 | -3.44e-05 | 1.97e+05 | 20 | 0.9795 | 10000 | 0.843 | 停滞 | 936 | 0.0922 | 18190 |
| P03-r1 | accel_ic/cocg | max_it | 50000 | 50000 | 8.8e-06 | -1.16e-04 | 7.54e+04 | 1.5 | - | 47464 | 0.001 | 遅い収束 | 1017 | 0.0201 | 1525 |
| P03-r1 | cslp/gmres | max_it | 3000 | 3000 | 8.4e-05 | -7.83e-04 | 8.01e+03 | 2.7 | 0.6059 | 3000 | 0.356 | 遅い収束 | 2193 | 0.7246 | 5823 |
| P03-r2 | gs/gmres | max_it | 10000 | 10000 | 4.8e-02 | -2.28e-05 | 3.03e+05 | 30 | 0.9873 | 10000 | 0.898 | 停滞 | 450 | 0.0436 | 13229 |
| P03-r2 | ssor/gmres | max_it | 10000 | 10000 | 3.3e-02 | -2.77e-05 | 2.45e+05 | 24 | 0.9829 | 10000 | 0.869 | 停滞 | 480 | 0.0465 | 11408 |
| P03-r2 | ssor/cocg | max_it | 50000 | 50000 | 6.1e-07 | -1.35e-04 | 6.32e+04 | 1.3 | - | 46610 | 0.001 | 遅い収束 | 1225 | 0.0242 | 1543 |
| P03-r2 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.8e-02 | -2.84e-05 | 2.37e+05 | 24 | 0.9777 | 10000 | 0.865 | 停滞 | 652 | 0.0636 | 15084 |
| P03-r2 | amg_gamg/cocg | max_it | 50000 | 50000 | 2.4e-06 | -1.19e-04 | 7e+04 | 1.4 | - | 44769 | 0.002 | 遅い収束 | 2081 | 0.0413 | 2906 |
| P03-r2 | accel_ic/gmres | max_it | 10000 | 10000 | 2.8e-02 | -3.45e-05 | 1.97e+05 | 20 | 0.9782 | 10000 | 0.85 | 停滞 | 954 | 0.094 | 18488 |
| P03-r2 | accel_ic/cocg | max_it | 50000 | 50000 | 1.3e-05 | -9.36e-05 | 8.31e+04 | 1.7 | - | 48205 | 0.002 | 遅い収束 | 1054 | 0.0208 | 1741 |
| P03-r2 | cslp/gmres | max_it | 3000 | 3000 | 7.8e-05 | -6.99e-04 | 8.57e+03 | 2.9 | 0.606 | 3000 | 0.364 | 遅い収束 | 2243 | 0.7413 | 6372 |
| P03-r8 | gs/gmres | max_it | 10000 | 10000 | 4.9e-02 | -2.50e-05 | 2.78e+05 | 28 | 0.9813 | 10000 | 0.887 | 停滞 | 503 | 0.0487 | 13556 |
| P03-r8 | ssor/gmres | max_it | 10000 | 10000 | 3.3e-02 | -2.43e-05 | 2.78e+05 | 28 | 0.9836 | 10000 | 0.885 | 停滞 | 537 | 0.052 | 14501 |
| P03-r8 | ssor/cocg | max_it | 50000 | 50000 | 2.3e-06 | -1.23e-04 | 6.92e+04 | 1.4 | - | 49844 | 0.002 | 遅い収束 | 1372 | 0.0271 | 1891 |
| P03-r8 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.7e-02 | -3.28e-05 | 2.06e+05 | 21 | 0.973 | 10000 | 0.845 | 停滞 | 733 | 0.0716 | 14766 |
| P03-r8 | amg_gamg/cocg | max_it | 50000 | 50000 | 1.2e-06 | -1.23e-04 | 6.67e+04 | 1.3 | - | 48665 | 0.002 | 遅い収束 | 2345 | 0.0466 | 3123 |
| P03-r8 | accel_ic/gmres | max_it | 10000 | 10000 | 2.8e-02 | -2.77e-05 | 2.43e+05 | 24 | 0.9833 | 10000 | 0.873 | 停滞 | 1070 | 0.1054 | 25590 |
| P03-r8 | accel_ic/cocg | max_it | 50000 | 50000 | 1.1e-05 | -1.16e-04 | 7.62e+04 | 1.5 | - | 48012 | 0.002 | 遅い収束 | 1169 | 0.023 | 1772 |
| P03-r8 | cslp/gmres | max_it | 3000 | 3000 | 8.7e-05 | -7.32e-04 | 8.38e+03 | 2.8 | 0.6063 | 3000 | 0.366 | 遅い収束 | 2534 | 0.8372 | 7037 |
| P03-d0.7 | gs/gmres | max_it | 10000 | 10000 | 5.0e-02 | -2.49e-05 | 2.79e+05 | 28 | 0.9828 | 10000 | 0.889 | 停滞 | 455 | 0.0441 | 12333 |
| P03-d0.7 | ssor/gmres | max_it | 10000 | 10000 | 3.4e-02 | -2.41e-05 | 2.8e+05 | 28 | 0.9872 | 10000 | 0.884 | 停滞 | 485 | 0.0471 | 13216 |
| P03-d0.7 | ssor/cocg | max_it | 50000 | 50000 | 7.2e-07 | -1.20e-04 | 6.54e+04 | 1.3 | - | 47653 | 0.001 | 遅い収束 | 1237 | 0.0245 | 1613 |
| P03-d0.7 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.9e-02 | -2.37e-05 | 2.82e+05 | 28 | 0.9844 | 10000 | 0.884 | 停滞 | 660 | 0.0644 | 18169 |
| P03-d0.7 | amg_gamg/cocg | max_it | 50000 | 50000 | 3.7e-07 | -1.22e-04 | 6.29e+04 | 1.3 | - | 49605 | 0.001 | 遅い収束 | 2105 | 0.0418 | 2643 |
| P03-d0.7 | accel_ic/gmres | max_it | 10000 | 10000 | 2.8e-02 | -3.42e-05 | 1.99e+05 | 20 | 0.9794 | 10000 | 0.851 | 停滞 | 967 | 0.0952 | 18939 |
| P03-d0.7 | accel_ic/cocg | max_it | 50000 | 50000 | 3.6e-06 | -1.43e-04 | 6.79e+04 | 1.4 | - | 48261 | 0 | 遅い収束 | 1068 | 0.0211 | 1443 |
| P03-d0.7 | cslp/gmres | max_it | 3000 | 3000 | 9.2e-05 | -7.25e-04 | 8.47e+03 | 2.8 | 0.6042 | 3000 | 0.361 | 遅い収束 | 2259 | 0.7464 | 6336 |
| P03-d2 | gs/gmres | max_it | 10000 | 10000 | 4.9e-02 | -2.40e-05 | 2.89e+05 | 29 | 0.9824 | 10000 | 0.891 | 停滞 | 495 | 0.0478 | 13845 |
| P03-d2 | ssor/gmres | max_it | 10000 | 10000 | 3.0e-02 | -3.99e-05 | 1.73e+05 | 17 | 0.9734 | 10000 | 0.824 | 停滞 | 527 | 0.0511 | 8831 |
| P03-d2 | ssor/cocg | max_it | 50000 | 50000 | 3.7e-07 | -1.27e-04 | 6.23e+04 | 1.2 | - | 49662 | 0 | 遅い収束 | 1348 | 0.0266 | 1674 |
| P03-d2 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.5e-02 | -4.38e-05 | 1.56e+05 | 16 | 0.9721 | 10000 | 0.811 | 停滞 | 719 | 0.0701 | 10962 |
| P03-d2 | amg_gamg/cocg | max_it | 50000 | 50000 | 8.5e-08 | -1.52e-04 | 5.61e+04 | 1.1 | - | 48783 | 0 | 遅い収束 | 2300 | 0.0457 | 2577 |
| P03-d2 | accel_ic/gmres | max_it | 10000 | 10000 | 2.7e-02 | -4.10e-05 | 1.67e+05 | 17 | 0.974 | 10000 | 0.823 | 停滞 | 1052 | 0.1035 | 17268 |
| P03-d2 | accel_ic/cocg | max_it | 50000 | 50000 | 3.5e-06 | -9.95e-05 | 7.56e+04 | 1.5 | - | 49299 | 0 | 遅い収束 | 1145 | 0.0226 | 1722 |
| P03-d2 | cslp/gmres | max_it | 3000 | 3000 | 6.9e-05 | -7.68e-04 | 8e+03 | 2.7 | 0.5908 | 3000 | 0.344 | 遅い収束 | 2471 | 0.8162 | 6551 |
| P03-d5 | gs/gmres | max_it | 10000 | 10000 | 5.4e-02 | -9.11e-06 | 7.49e+05 | 75 | 0.9942 | 10000 | 0.956 | 停滞 | 521 | 0.0504 | 37745 |
| P03-d5 | ssor/gmres | max_it | 10000 | 10000 | 3.6e-02 | -4.29e-05 | 1.63e+05 | 16 | 0.9728 | 10000 | 0.816 | 停滞 | 554 | 0.0538 | 8777 |
| P03-d5 | ssor/cocg | max_it | 50000 | 50000 | 4.7e-07 | -1.26e-04 | 6.32e+04 | 1.3 | - | 49679 | 0 | 遅い収束 | 1414 | 0.028 | 1783 |
| P03-d5 | amg_gamg/gmres | max_it | 10000 | 10000 | 3.0e-02 | -4.37e-05 | 1.58e+05 | 16 | 0.973 | 10000 | 0.812 | 停滞 | 755 | 0.0737 | 11679 |
| P03-d5 | amg_gamg/cocg | max_it | 50000 | 50000 | 1.2e-07 | -1.44e-04 | 5.76e+04 | 1.2 | - | 49690 | 0 | 遅い収束 | 2412 | 0.0479 | 2774 |
| P03-d5 | accel_ic/gmres | max_it | 10000 | 10000 | 3.2e-02 | -3.48e-05 | 1.97e+05 | 20 | 0.9723 | 10000 | 0.848 | 停滞 | 1104 | 0.1087 | 21435 |
| P03-d5 | accel_ic/cocg | max_it | 50000 | 50000 | 4.6e-06 | -1.08e-04 | 7.46e+04 | 1.5 | - | 49244 | 0.002 | 遅い収束 | 1224 | 0.0241 | 1817 |
| P03-d5 | cslp/gmres | max_it | 3000 | 3000 | 1.4e-04 | -6.17e-04 | 9.71e+03 | 3.2 | 0.6347 | 3000 | 0.407 | 遅い収束 | 2600 | 0.859 | 8362 |
| P03-v0.2 | gs/gmres | max_it | 10000 | 10000 | 4.9e-02 | -2.70e-05 | 2.58e+05 | 26 | 0.9829 | 10000 | 0.881 | 停滞 | 516 | 0.0499 | 12871 |
| P03-v0.2 | ssor/gmres | max_it | 10000 | 10000 | 3.2e-02 | -3.17e-05 | 2.15e+05 | 22 | 0.9793 | 10000 | 0.855 | 停滞 | 549 | 0.0533 | 11484 |
| P03-v0.2 | ssor/cocg | max_it | 50000 | 50000 | 4.7e-07 | -1.36e-04 | 6.23e+04 | 1.2 | - | 49220 | 0 | 遅い収束 | 1403 | 0.0277 | 1741 |
| P03-v0.2 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.7e-02 | -3.46e-05 | 1.96e+05 | 20 | 0.9765 | 10000 | 0.84 | 停滞 | 751 | 0.0733 | 14366 |
| P03-v0.2 | amg_gamg/cocg | max_it | 50000 | 50000 | 4.5e-07 | -1.43e-04 | 6.15e+04 | 1.2 | - | 45612 | 0.001 | 遅い収束 | 2394 | 0.0475 | 2940 |
| P03-v0.2 | accel_ic/gmres | max_it | 10000 | 10000 | 2.8e-02 | -3.21e-05 | 2.11e+05 | 21 | 0.9791 | 10000 | 0.857 | 停滞 | 1097 | 0.108 | 22780 |
| P03-v0.2 | accel_ic/cocg | max_it | 50000 | 50000 | 3.3e-06 | -1.29e-04 | 6.94e+04 | 1.4 | - | 48200 | 0 | 遅い収束 | 1203 | 0.0237 | 1663 |
| P03-v0.2 | cslp/gmres | max_it | 3000 | 3000 | 1.1e-04 | -6.68e-04 | 9.06e+03 | 3 | 0.6264 | 3000 | 0.394 | 遅い収束 | 2592 | 0.8566 | 7784 |
| P03-v0.5 | gs/gmres | max_it | 10000 | 10000 | 4.9e-02 | -2.55e-05 | 2.73e+05 | 27 | 0.9821 | 10000 | 0.885 | 停滞 | 443 | 0.0429 | 11705 |
| P03-v0.5 | ssor/gmres | max_it | 10000 | 10000 | 3.2e-02 | -2.29e-05 | 2.94e+05 | 29 | 0.9851 | 10000 | 0.889 | 停滞 | 472 | 0.0458 | 13464 |
| P03-v0.5 | ssor/cocg | max_it | 50000 | 50000 | 5.9e-07 | -1.10e-04 | 6.61e+04 | 1.3 | - | 49726 | 0.001 | 遅い収束 | 1207 | 0.0239 | 1588 |
| P03-v0.5 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.8e-02 | -2.49e-05 | 2.69e+05 | 27 | 0.981 | 10000 | 0.88 | 停滞 | 642 | 0.0627 | 16901 |
| P03-v0.5 | amg_gamg/cocg | max_it | 50000 | 50000 | 2.3e-07 | -1.28e-04 | 6.06e+04 | 1.2 | - | 49711 | 0 | 遅い収束 | 2049 | 0.0407 | 2481 |
| P03-v0.5 | accel_ic/gmres | max_it | 10000 | 10000 | 2.7e-02 | -3.43e-05 | 1.98e+05 | 20 | 0.9818 | 10000 | 0.848 | 停滞 | 941 | 0.0927 | 18335 |
| P03-v0.5 | accel_ic/cocg | max_it | 50000 | 50000 | 8.4e-06 | -1.22e-04 | 7.39e+04 | 1.5 | - | 47492 | 0.001 | 遅い収束 | 1041 | 0.0205 | 1530 |
| P03-v0.5 | cslp/gmres | max_it | 3000 | 3000 | 9.0e-05 | -7.78e-04 | 8.08e+03 | 2.7 | 0.5997 | 3000 | 0.343 | 遅い収束 | 2203 | 0.7278 | 5900 |
| P03-a0.6 | gs/gmres | max_it | 10000 | 10000 | 5.0e-02 | -2.22e-05 | 3.12e+05 | 31 | 0.9839 | 10000 | 0.899 | 停滞 | 467 | 0.0452 | 14137 |
| P03-a0.6 | ssor/gmres | max_it | 10000 | 10000 | 3.2e-02 | -2.73e-05 | 2.49e+05 | 25 | 0.9835 | 10000 | 0.873 | 停滞 | 498 | 0.0483 | 12018 |
| P03-a0.6 | ssor/cocg | max_it | 50000 | 50000 | 6.3e-07 | -1.12e-04 | 6.61e+04 | 1.3 | - | 49171 | 0.001 | 遅い収束 | 1267 | 0.025 | 1669 |
| P03-a0.6 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.6e-02 | -2.85e-05 | 2.35e+05 | 24 | 0.9805 | 10000 | 0.863 | 停滞 | 678 | 0.0662 | 15574 |
| P03-a0.6 | amg_gamg/cocg | max_it | 50000 | 50000 | 1.0e-06 | -1.10e-04 | 6.83e+04 | 1.4 | - | 46420 | 0.003 | 遅い収束 | 2162 | 0.0429 | 2946 |
| P03-a0.6 | accel_ic/gmres | max_it | 10000 | 10000 | 2.7e-02 | -3.77e-05 | 1.81e+05 | 18 | 0.9787 | 10000 | 0.832 | 停滞 | 991 | 0.0976 | 17645 |
| P03-a0.6 | accel_ic/cocg | max_it | 50000 | 50000 | 8.4e-06 | -9.63e-05 | 8.03e+04 | 1.6 | - | 49326 | 0.001 | 遅い収束 | 1081 | 0.0213 | 1726 |
| P03-a0.6 | cslp/gmres | max_it | 3000 | 3000 | 9.6e-05 | -6.99e-04 | 8.7e+03 | 2.9 | 0.6057 | 3000 | 0.367 | 遅い収束 | 2329 | 0.7696 | 6714 |
| P03-a1.2 | gs/gmres | max_it | 10000 | 10000 | 4.9e-02 | -2.21e-05 | 3.12e+05 | 31 | 0.9861 | 10000 | 0.899 | 停滞 | 466 | 0.0451 | 14094 |
| P03-a1.2 | ssor/gmres | max_it | 10000 | 10000 | 3.1e-02 | -3.34e-05 | 2.04e+05 | 20 | 0.977 | 10000 | 0.843 | 停滞 | 496 | 0.0482 | 9859 |
| P03-a1.2 | ssor/cocg | max_it | 50000 | 50000 | 1.7e-07 | -1.62e-04 | 5.75e+04 | 1.2 | - | 48086 | 0 | 遅い収束 | 1268 | 0.0251 | 1456 |
| P03-a1.2 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.6e-02 | -4.43e-05 | 1.55e+05 | 15 | 0.961 | 10000 | 0.8 | 停滞 | 675 | 0.0659 | 10211 |
| P03-a1.2 | amg_gamg/cocg | max_it | 50000 | 50000 | 2.6e-07 | -1.41e-04 | 6e+04 | 1.2 | - | 42289 | 0 | 遅い収束 | 2159 | 0.0429 | 2587 |
| P03-a1.2 | accel_ic/gmres | max_it | 10000 | 10000 | 2.7e-02 | -3.43e-05 | 1.98e+05 | 20 | 0.9786 | 10000 | 0.848 | 停滞 | 991 | 0.0976 | 19317 |
| P03-a1.2 | accel_ic/cocg | max_it | 50000 | 50000 | 4.9e-06 | -1.34e-04 | 7.01e+04 | 1.4 | - | 46513 | 0.001 | 遅い収束 | 1093 | 0.0216 | 1526 |
| P03-a1.2 | cslp/gmres | max_it | 3000 | 3000 | 5.9e-05 | -7.40e-04 | 8.1e+03 | 2.7 | 0.5832 | 3000 | 0.334 | 遅い収束 | 2322 | 0.7672 | 6230 |
| P04-1 | gs/gmres | max_it | 10000 | 10000 | 2.6e-02 | -1.75e-05 | 3.78e+05 | 38 | 0.9851 | 10000 | 0.917 | 停滞 | 648 | 0.0629 | 23771 |
| P04-1 | ssor/gmres | max_it | 10000 | 10000 | 1.3e-02 | -5.80e-05 | 1.15e+05 | 12 | 0.9678 | 10000 | 0.766 | 停滞 | 692 | 0.0673 | 7779 |
| P04-1 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.2e-02 | -6.31e-05 | 1.07e+05 | 11 | 0.9592 | 10000 | 0.747 | 停滞 | 952 | 0.0932 | 9955 |
| P04-1 | accel_ic/gmres | max_it | 10000 | 10000 | 1.2e-02 | -4.13e-05 | 1.57e+05 | 16 | 0.9674 | 10000 | 0.809 | 停滞 | 1376 | 0.1356 | 21371 |
| P04-1 | cslp/gmres | max_it | 3000 | 3000 | 2.8e-05 | -9.58e-04 | 6.6e+03 | 2.2 | 0.5279 | 3000 | 0.28 | 遅い収束 | 3300 | 1.0912 | 7223 |
| P04-2 | gs/gmres | max_it | 10000 | 10000 | 3.7e-02 | -1.27e-05 | 5.26e+05 | 53 | 0.9887 | 10000 | 0.938 | 停滞 | 647 | 0.0628 | 33085 |
| P04-2 | ssor/gmres | max_it | 10000 | 10000 | 1.6e-02 | -5.42e-05 | 1.25e+05 | 12 | 0.9683 | 10000 | 0.762 | 停滞 | 691 | 0.0672 | 8399 |
| P04-2 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.5e-02 | -5.11e-05 | 1.3e+05 | 13 | 0.973 | 10000 | 0.776 | 停滞 | 955 | 0.0935 | 12214 |
| P04-2 | accel_ic/gmres | max_it | 10000 | 10000 | 1.4e-02 | -5.70e-05 | 1.18e+05 | 12 | 0.9518 | 10000 | 0.766 | 停滞 | 1384 | 0.1365 | 16103 |
| P04-2 | cslp/gmres | max_it | 3000 | 3000 | 7.2e-06 | -1.18e-03 | 5.43e+03 | 1.8 | 0.457 | 3000 | 0.208 | 遅い収束 | 3322 | 1.0983 | 5986 |
| P04-3 | gs/gmres | max_it | 10000 | 10000 | 4.4e-02 | -1.66e-05 | 4.1e+05 | 41 | 0.9861 | 10000 | 0.922 | 停滞 | 661 | 0.0641 | 26303 |
| P04-3 | ssor/gmres | max_it | 10000 | 10000 | 1.6e-02 | -8.30e-05 | 8.47e+04 | 8.5 | 0.9462 | 10000 | 0.703 | 停滞 | 705 | 0.0685 | 5823 |
| P04-3 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.5e-02 | -7.91e-05 | 8.8e+04 | 8.8 | 0.9525 | 10000 | 0.709 | 停滞 | 972 | 0.0951 | 8396 |
| P04-3 | accel_ic/gmres | max_it | 10000 | 10000 | 1.6e-02 | -5.71e-05 | 1.19e+05 | 12 | 0.9662 | 10000 | 0.749 | 停滞 | 1414 | 0.1395 | 16566 |
| P04-3 | accel_ic/cocg | max_it | 50000 | 50000 | 2.1e-08 | -1.89e-04 | 5.17e+04 | 1 | - | 48236 | 0 | 遅い収束 | 1575 | 0.0311 | 1628 |
| P04-3 | cslp/gmres | max_it | 3000 | 3000 | 1.9e-06 | -1.42e-03 | 4.61e+03 | 1.5 | 0.3784 | 3000 | 0.14 | 遅い収束 | 3382 | 1.1182 | 5176 |
| P04-4 | gs/gmres | max_it | 10000 | 10000 | 3.4e-02 | -1.35e-05 | 4.94e+05 | 49 | 0.9901 | 10000 | 0.936 | 停滞 | 962 | 0.0934 | 46196 |
| P04-4 | ssor/gmres | max_it | 10000 | 10000 | 1.8e-02 | -4.85e-05 | 1.39e+05 | 14 | 0.9763 | 10000 | 0.777 | 停滞 | 1025 | 0.0997 | 13903 |
| P04-4 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.6e-02 | -5.11e-05 | 1.32e+05 | 13 | 0.9712 | 10000 | 0.773 | 停滞 | 1422 | 0.1391 | 18355 |
| P04-4 | accel_ic/gmres | max_it | 10000 | 10000 | 1.6e-02 | -6.15e-05 | 1.11e+05 | 11 | 0.9558 | 10000 | 0.755 | 停滞 | 2052 | 0.2023 | 22444 |
| P04-4 | cslp/gmres | max_it | 3000 | 3000 | 5.5e-08 | -1.90e-03 | 3.39e+03 | 1.1 | 0.275 | 3000 | 0.076 | 遅い収束 | 4998 | 1.6527 | 5641 |
| P05-1 | gs/gmres | max_it | 10000 | 10000 | 4.9e-05 | -5.83e-05 | 7.33e+04 | 7.3 | 0.958 | 10000 | 0.753 | 停滞 | 66 | 0.0064 | 467 |
| P05-1 | ssor/gmres | max_it | 10000 | 10000 | 1.0e-06 | -1.70e-04 | 2.18e+04 | 2.2 | 0.8673 | 10000 | 0.423 | 遅い収束 | 70 | 0.0068 | 149 |
| P05-1 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.7e-08 | -3.25e-04 | 1.07e+04 | 1.1 | 0.8019 | 10000 | 0.208 | 遅い収束 | 89 | 0.0086 | 94 |
| P05-1 | accel_ic/gmres | max_it | 10000 | 10000 | 7.1e-06 | -9.87e-05 | 3.89e+04 | 3.9 | 0.9441 | 10000 | 0.636 | 停滞 | 147 | 0.0144 | 563 |
| P05-2 | gs/gmres | max_it | 10000 | 10000 | 1.9e-02 | -2.32e-05 | 2.8e+05 | 28 | 0.9847 | 10000 | 0.892 | 停滞 | 66 | 0.0063 | 1778 |
| P05-2 | ssor/gmres | max_it | 10000 | 10000 | 2.3e-04 | -1.72e-04 | 3.54e+04 | 3.5 | 0.8915 | 10000 | 0.424 | 遅い収束 | 70 | 0.0068 | 241 |
| P05-2 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.0e-06 | -1.55e-04 | 2.48e+04 | 2.5 | 0.9037 | 10000 | 0.453 | 停滞 | 89 | 0.0086 | 215 |
| P05-2 | accel_ic/gmres | max_it | 10000 | 10000 | 3.6e-03 | -9.03e-05 | 7.15e+04 | 7.1 | 0.9293 | 10000 | 0.65 | 停滞 | 147 | 0.0144 | 1031 |
| P05-3 | gs/gmres | max_it | 10000 | 10000 | 2.0e-02 | -2.85e-05 | 2.31e+05 | 23 | 0.9838 | 10000 | 0.864 | 停滞 | 66 | 0.0063 | 1468 |
| P05-3 | ssor/gmres | max_it | 10000 | 10000 | 2.2e-04 | -1.70e-04 | 3.55e+04 | 3.5 | 0.8949 | 10000 | 0.422 | 遅い収束 | 70 | 0.0068 | 242 |
| P05-3 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.8e-06 | -1.57e-04 | 2.44e+04 | 2.4 | 0.9031 | 10000 | 0.448 | 停滞 | 89 | 0.0086 | 211 |
| P05-3 | accel_ic/gmres | max_it | 10000 | 10000 | 4.1e-03 | -7.27e-05 | 8.72e+04 | 8.7 | 0.9511 | 10000 | 0.711 | 停滞 | 147 | 0.0144 | 1261 |
| P05-2_sibc | gs/gmres | max_it | 10000 | 10000 | 7.5e-03 | -8.59e-05 | 7.84e+04 | 7.8 | 0.9535 | 10000 | 0.667 | 停滞 | 66 | 0.0063 | 500 |
| P05-2_sibc | ssor/gmres | max_it | 10000 | 10000 | 2.4e-04 | -1.56e-04 | 3.81e+04 | 3.8 | 0.907 | 10000 | 0.474 | 停滞 | 70 | 0.0068 | 260 |
| P05-2_sibc | amg_gamg/gmres | max_it | 10000 | 10000 | 8.9e-06 | -1.51e-04 | 2.95e+04 | 2.9 | 0.9008 | 10000 | 0.463 | 停滞 | 88 | 0.0086 | 255 |
| P05-2_sibc | accel_ic/gmres | max_it | 10000 | 10000 | 1.0e-03 | -1.38e-04 | 4.65e+04 | 4.6 | 0.9075 | 10000 | 0.535 | 停滞 | 147 | 0.0144 | 672 |
| P05-g0.1 | gs/gmres | max_it | 10000 | 10000 | 1.7e-02 | -5.14e-05 | 1.31e+05 | 13 | 0.9686 | 10000 | 0.789 | 停滞 | 66 | 0.0063 | 834 |
| P05-g0.1 | ssor/gmres | max_it | 10000 | 10000 | 5.5e-05 | -1.71e-04 | 3.19e+04 | 3.2 | 0.9084 | 10000 | 0.425 | 停滞 | 70 | 0.0068 | 217 |
| P05-g0.1 | amg_gamg/gmres | max_it | 10000 | 10000 | 7.0e-06 | -9.02e-05 | 4.16e+04 | 4.2 | 0.943 | 10000 | 0.631 | 停滞 | 89 | 0.0086 | 359 |
| P05-g0.1 | accel_ic/gmres | max_it | 10000 | 10000 | 6.1e-03 | -8.31e-05 | 7.96e+04 | 8 | 0.9484 | 10000 | 0.674 | 停滞 | 146 | 0.0144 | 1147 |
| P05-g1.0 | gs/gmres | max_it | 10000 | 10000 | 9.4e-03 | -1.02e-04 | 6.88e+04 | 6.9 | 0.9584 | 10000 | 0.589 | 停滞 | 66 | 0.0063 | 438 |
| P05-g1.0 | ssor/gmres | max_it | 10000 | 10000 | 2.8e-04 | -2.29e-04 | 2.95e+04 | 2.9 | 0.7917 | 10000 | 0.319 | 遅い収束 | 70 | 0.0068 | 201 |
| P05-g1.0 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.8e-05 | -1.67e-04 | 3.07e+04 | 3.1 | 0.8953 | 10000 | 0.447 | 遅い収束 | 89 | 0.0086 | 266 |
| P05-g1.0 | accel_ic/gmres | max_it | 10000 | 10000 | 4.3e-04 | -9.29e-05 | 5.99e+04 | 6 | 0.9327 | 10000 | 0.65 | 停滞 | 147 | 0.0144 | 864 |
| P05-fc | gs/gmres | max_it | 10000 | 10000 | 6.8e-05 | -1.02e-05 | 3.87e+05 | 39 | 0.9928 | 10000 | 0.95 | 停滞 | 66 | 0.0064 | 2457 |
| P05-fc | ssor/gmres | max_it | 10000 | 10000 | 5.0e-06 | -1.17e-04 | 3.31e+04 | 3.3 | 0.9241 | 10000 | 0.554 | 停滞 | 70 | 0.0068 | 226 |
| P05-fc | amg_gamg/gmres | max_it | 10000 | 10000 | 2.3e-08 | -3.01e-04 | 1.12e+04 | 1.1 | 0.8127 | 10000 | 0.216 | 遅い収束 | 89 | 0.0086 | 99 |
| P05-fc | accel_ic/gmres | max_it | 10000 | 10000 | 4.3e-05 | -2.66e-05 | 1.47e+05 | 15 | 0.9825 | 10000 | 0.873 | 停滞 | 147 | 0.0144 | 2119 |
| P05-fe | gs/gmres | max_it | 10000 | 10000 | 5.0e-03 | -3.83e-05 | 1.59e+05 | 16 | 0.976 | 10000 | 0.834 | 停滞 | 66 | 0.0063 | 1006 |
| P05-fe | ssor/gmres | max_it | 10000 | 10000 | 2.1e-04 | -5.45e-05 | 8.93e+04 | 8.9 | 0.9571 | 10000 | 0.743 | 停滞 | 70 | 0.0067 | 604 |
| P05-fe | amg_gamg/gmres | max_it | 10000 | 10000 | 9.4e-06 | -1.64e-04 | 2.82e+04 | 2.8 | 0.8938 | 10000 | 0.439 | 遅い収束 | 88 | 0.0086 | 243 |
| P05-fe | accel_ic/gmres | max_it | 10000 | 10000 | 5.2e-04 | -4.02e-05 | 1.27e+05 | 13 | 0.9723 | 10000 | 0.821 | 停滞 | 145 | 0.0143 | 1822 |
| P05-n1 | hx/gmres | max_it | 10000 | 10000 | 1.0e+00 | 0.00e+00 | ∞ | ∞ | 1 | 0 | 1 | 停滞 | 181 | 0.0178 | ∞ |
| P05-n4 | gs/gmres | max_it | 10000 | 10000 | 1.9e-02 | -3.74e-05 | 1.78e+05 | 18 | 0.9776 | 10000 | 0.84 | 停滞 | 120 | 0.0116 | 2070 |
| P05-n4 | ssor/gmres | max_it | 10000 | 10000 | 7.6e-03 | -5.45e-05 | 1.18e+05 | 12 | 0.9653 | 10000 | 0.762 | 停滞 | 128 | 0.0124 | 1465 |
| P05-n4 | amg_gamg/gmres | max_it | 10000 | 10000 | 7.3e-04 | -1.35e-04 | 4.6e+04 | 4.6 | 0.9117 | 10000 | 0.501 | 停滞 | 165 | 0.016 | 741 |
| P05-n4 | accel_ic/gmres | max_it | 10000 | 10000 | 5.1e-03 | -1.23e-04 | 5.64e+04 | 5.6 | 0.9356 | 10000 | 0.581 | 停滞 | 264 | 0.026 | 1469 |
| P05-td1e-4 | gs/gmres | max_it | 10000 | 10000 | 1.9e-02 | -3.51e-05 | 1.89e+05 | 19 | 0.9788 | 10000 | 0.846 | 停滞 | 66 | 0.0063 | 1203 |
| P05-td1e-4 | ssor/gmres | max_it | 10000 | 10000 | 2.2e-04 | -1.72e-04 | 3.53e+04 | 3.5 | 0.8956 | 10000 | 0.431 | 遅い収束 | 70 | 0.0068 | 240 |
| P05-td1e-4 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.8e-06 | -1.57e-04 | 2.44e+04 | 2.4 | 0.9039 | 10000 | 0.449 | 停滞 | 89 | 0.0086 | 211 |
| P05-td1e-4 | accel_ic/gmres | max_it | 10000 | 10000 | 4.0e-03 | -7.12e-05 | 8.87e+04 | 8.9 | 0.9518 | 10000 | 0.713 | 停滞 | 146 | 0.0144 | 1279 |
| P05-td1e-2 | gs/gmres | max_it | 10000 | 10000 | 5.9e-03 | -8.38e-05 | 7.89e+04 | 7.9 | 0.9537 | 10000 | 0.673 | 停滞 | 66 | 0.0063 | 503 |
| P05-td1e-2 | ssor/gmres | max_it | 10000 | 10000 | 1.1e-04 | -1.27e-04 | 4.18e+04 | 4.2 | 0.925 | 10000 | 0.524 | 停滞 | 70 | 0.0068 | 284 |
| P05-td1e-2 | amg_gamg/gmres | max_it | 10000 | 10000 | 4.5e-06 | -1.70e-04 | 2.56e+04 | 2.6 | 0.8898 | 10000 | 0.423 | 遅い収束 | 89 | 0.0086 | 222 |
| P05-td1e-2 | accel_ic/gmres | max_it | 10000 | 10000 | 9.3e-04 | -1.34e-04 | 4.7e+04 | 4.7 | 0.9201 | 10000 | 0.535 | 停滞 | 147 | 0.0144 | 679 |
| P05-lc1.25 | gs/gmres | max_it | 10000 | 10000 | 1.8e-02 | -1.86e-05 | 3.47e+05 | 35 | 0.9796 | 10000 | 0.897 | 停滞 | 237 | 0.0228 | 7915 |
| P05-lc1.25 | ssor/gmres | max_it | 10000 | 10000 | 7.9e-03 | -9.16e-05 | 7.44e+04 | 7.4 | 0.9614 | 10000 | 0.664 | 停滞 | 252 | 0.0244 | 1818 |
| P05-lc1.25 | amg_gamg/gmres | max_it | 10000 | 10000 | 3.6e-03 | -1.11e-04 | 5.98e+04 | 6 | 0.9524 | 10000 | 0.587 | 停滞 | 323 | 0.0314 | 1883 |
| P05-lc1.25 | accel_ic/gmres | max_it | 10000 | 10000 | 9.2e-03 | -8.17e-05 | 8.3e+04 | 8.3 | 0.9472 | 10000 | 0.707 | 停滞 | 511 | 0.0502 | 4176 |
| P05-lc0.625 | gs/gmres | max_it | 10000 | 10000 | 1.1e-02 | -7.01e-06 | 8.74e+05 | 87 | 0.9958 | 10000 | 0.965 | 停滞 | 922 | 0.0889 | 77684 |
| P05-lc0.625 | ssor/gmres | max_it | 10000 | 10000 | 1.0e-02 | -5.05e-06 | 1.2e+06 | 1.2e+02 | 0.9964 | 10000 | 0.975 | 停滞 | 982 | 0.0949 | 114131 |
| P05-lc0.625 | amg_gamg/gmres | max_it | 10000 | 10000 | 8.0e-03 | -1.06e-05 | 5.68e+05 | 57 | 0.9926 | 10000 | 0.95 | 停滞 | 1303 | 0.1268 | 72019 |
| P05-lc0.625 | accel_ic/gmres | max_it | 10000 | 10000 | 8.2e-03 | -6.02e-06 | 9.92e+05 | 99 | 0.9958 | 10000 | 0.97 | 停滞 | 1985 | 0.1952 | 193593 |
| P06-L0 | gs/gmres | max_it | 10000 | 10000 | 2.0e-02 | -4.64e-05 | 1.46e+05 | 15 | 0.9652 | 10000 | 0.781 | 停滞 | 533 | 0.0517 | 7549 |
| P06-L0 | ssor/gmres | max_it | 10000 | 10000 | 5.5e-03 | -1.06e-04 | 6.42e+04 | 6.4 | 0.9324 | 10000 | 0.621 | 停滞 | 569 | 0.0553 | 3569 |
| P06-L0 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.0e-02 | -7.07e-05 | 9.5e+04 | 9.5 | 0.9568 | 10000 | 0.698 | 停滞 | 784 | 0.0766 | 7293 |
| P06-L0 | accel_ic/gmres | max_it | 10000 | 10000 | 7.2e-03 | -7.09e-05 | 9.26e+04 | 9.3 | 0.9549 | 10000 | 0.712 | 停滞 | 1132 | 0.1115 | 10343 |
| P06-L10 | gs/gmres | max_it | 10000 | 10000 | 1.9e-02 | -1.25e-04 | 6.04e+04 | 6 | 0.9257 | 10000 | 0.535 | 停滞 | 580 | 0.0562 | 3411 |
| P06-L10 | ssor/gmres | max_it | 10000 | 10000 | 2.4e-03 | -1.65e-04 | 4.26e+04 | 4.3 | 0.9067 | 10000 | 0.472 | 停滞 | 620 | 0.0602 | 2580 |
| P06-L10 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.1e-02 | -1.02e-04 | 6.93e+04 | 6.9 | 0.9379 | 10000 | 0.583 | 停滞 | 860 | 0.0841 | 5842 |
| P06-L10 | accel_ic/gmres | max_it | 10000 | 10000 | 4.2e-03 | -1.15e-04 | 5.88e+04 | 5.9 | 0.9252 | 10000 | 0.569 | 停滞 | 1243 | 0.1225 | 7215 |
| P06-L30 | gs/gmres | max_it | 10000 | 10000 | 2.7e-02 | -4.93e-05 | 1.41e+05 | 14 | 0.9481 | 10000 | 0.77 | 停滞 | 693 | 0.0672 | 9459 |
| P06-L30 | ssor/gmres | max_it | 10000 | 10000 | 8.0e-03 | -1.13e-04 | 6.24e+04 | 6.2 | 0.9292 | 10000 | 0.614 | 停滞 | 741 | 0.072 | 4510 |
| P06-L30 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.4e-02 | -5.98e-05 | 1.13e+05 | 11 | 0.9642 | 10000 | 0.753 | 停滞 | 1036 | 0.1013 | 11448 |
| P06-L30 | accel_ic/gmres | max_it | 10000 | 10000 | 1.1e-02 | -4.75e-05 | 1.37e+05 | 14 | 0.9733 | 10000 | 0.787 | 停滞 | 1483 | 0.1462 | 20084 |
| P06-L30_s2 | gs/gmres | max_it | 10000 | 10000 | 2.2e-02 | -5.39e-05 | 1.28e+05 | 13 | 0.9693 | 10000 | 0.766 | 停滞 | 699 | 0.0678 | 8673 |
| P06-L30_s2 | ssor/gmres | max_it | 10000 | 10000 | 6.5e-03 | -7.93e-05 | 8.33e+04 | 8.3 | 0.9419 | 10000 | 0.672 | 停滞 | 747 | 0.0725 | 6060 |
| P06-L30_s2 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.1e-02 | -8.23e-05 | 8.33e+04 | 8.3 | 0.9567 | 10000 | 0.675 | 停滞 | 1043 | 0.1019 | 8517 |
| P06-L30_s2 | accel_ic/gmres | max_it | 10000 | 10000 | 7.8e-03 | -6.84e-05 | 9.61e+04 | 9.6 | 0.9556 | 10000 | 0.708 | 停滞 | 1485 | 0.1462 | 14074 |
| P07-1 | gs/gmres | max_it | 10000 | 10000 | 2.5e-02 | -2.14e-05 | 3.09e+05 | 31 | 0.9874 | 10000 | 0.904 | 停滞 | 723 | 0.07 | 21627 |
| P07-1 | ssor/gmres | max_it | 10000 | 10000 | 1.8e-02 | -3.78e-05 | 1.75e+05 | 18 | 0.9751 | 10000 | 0.834 | 停滞 | 770 | 0.0747 | 13121 |
| P07-1 | ssor/cocg | max_it | 50000 | 50000 | 5.3e-04 | -2.98e-05 | 2.08e+05 | 4.2 | - | 49514 | 0.136 | 遅い収束 | 1982 | 0.0392 | 8188 |
| P07-1 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.6e-02 | -3.92e-05 | 1.69e+05 | 17 | 0.9735 | 10000 | 0.827 | 停滞 | 1065 | 0.104 | 17554 |
| P07-1 | amg_gamg/cocg | max_it | 50000 | 50000 | 5.5e-03 | -4.29e-05 | 1.84e+05 | 3.7 | - | 46666 | 0.088 | 遅い収束 | 3397 | 0.0675 | 12424 |
| P07-1 | accel_ic/gmres | max_it | 10000 | 10000 | 1.7e-02 | -2.57e-05 | 2.52e+05 | 25 | 0.9786 | 10000 | 0.879 | 停滞 | 1537 | 0.1514 | 38166 |
| P07-1 | accel_ic/cocg | max_it | 50000 | 50000 | 3.7e-03 | -4.11e-05 | 1.85e+05 | 3.7 | - | 39238 | 0.18 | 遅い収束 | 1710 | 0.0337 | 6279 |
| P07-1 | cslp/gmres | max_it | 3000 | 3000 | 1.2e-03 | -2.49e-04 | 2.35e+04 | 7.8 | 0.8571 | 3000 | 0.726 | 停滞 | 3711 | 1.2265 | 28828 |
| P07-4 | gs/gmres | max_it | 10000 | 10000 | 4.8e-02 | -2.19e-05 | 3.15e+05 | 31 | 0.9849 | 10000 | 0.899 | 停滞 | 725 | 0.0702 | 22089 |
| P07-4 | ssor/gmres | max_it | 10000 | 10000 | 3.4e-02 | -2.26e-05 | 3e+05 | 30 | 0.9838 | 10000 | 0.895 | 停滞 | 772 | 0.0749 | 22456 |
| P07-4 | ssor/cocg | max_it | 50000 | 50000 | 5.2e-05 | -1.01e-04 | 8.69e+04 | 1.7 | - | 49658 | 0.003 | 遅い収束 | 1979 | 0.0391 | 3419 |
| P07-4 | amg_gamg/gmres | max_it | 10000 | 10000 | 2.8e-02 | -2.75e-05 | 2.45e+05 | 24 | 0.9804 | 10000 | 0.876 | 停滞 | 1066 | 0.1041 | 25491 |
| P07-4 | amg_gamg/cocg | max_it | 50000 | 50000 | 7.1e-05 | -1.02e-04 | 8.76e+04 | 1.8 | - | 48395 | 0.004 | 遅い収束 | 3382 | 0.0672 | 5908 |
| P07-4 | accel_ic/gmres | max_it | 10000 | 10000 | 2.8e-02 | -2.46e-05 | 2.73e+05 | 27 | 0.9863 | 10000 | 0.881 | 停滞 | 1534 | 0.1511 | 41209 |
| P07-4 | accel_ic/cocg | max_it | 50000 | 50000 | 2.6e-04 | -1.06e-04 | 9.16e+04 | 1.8 | - | 44211 | 0.005 | 遅い収束 | 1711 | 0.0337 | 3114 |
| P07-4 | cslp/gmres | max_it | 3000 | 3000 | 1.7e-04 | -6.28e-04 | 9.72e+03 | 3.2 | 0.6479 | 3000 | 0.42 | 遅い収束 | 3713 | 1.227 | 11954 |
| P07-4 | cslp_hx/gmres | max_it | 1000 | 1000 | 1.3e-06 | -6.10e-03 | 1.35e+03（悲観側） | 1.3 | 0.0132 | 1000 | 0.028 | 遅い収束 | 1291 | 1.2575 | 1723 |
| P08-N2_s1 | gs/gmres | max_it | 10000 | 10000 | 5.7e-05 | -2.51e-04 | 2.5e+04 | 2.5 | 0.8364 | 10000 | 0.29 | 遅い収束 | 216 | 0.0209 | 528 |
| P08-N2_s1 | ssor/gmres | max_it | 10000 | 10000 | 4.1e-07 | -4.11e-04 | 1.39e+04 | 1.4 | 0.7454 | 10000 | 0.14 | 遅い収束 | 230 | 0.0223 | 317 |
| P08-N2_s1 | amg_gamg/gmres | max_it | 10000 | 10000 | 1.5e-06 | -4.05e-04 | 1.54e+04 | 1.5 | 0.7546 | 10000 | 0.143 | 遅い収束 | 307 | 0.03 | 467 |
| P08-N2_s1 | accel_ic/gmres | max_it | 10000 | 10000 | 1.8e-06 | -3.80e-04 | 1.6e+04 | 1.6 | 0.7749 | 10000 | 0.162 | 遅い収束 | 458 | 0.0452 | 727 |
| P08-N4_s1 | gs/gmres | max_it | 10000 | 10000 | 6.2e-05 | -2.48e-04 | 2.53e+04 | 2.5 | 0.8424 | 10000 | 0.3 | 遅い収束 | 377 | 0.0365 | 933 |
| P08-N4_s1 | ssor/gmres | max_it | 10000 | 10000 | 5.9e-07 | -3.70e-04 | 1.48e+04 | 1.5 | 0.7879 | 10000 | 0.173 | 遅い収束 | 401 | 0.039 | 587 |
| P08-N4_s1 | amg_gamg/gmres | max_it | 10000 | 10000 | 3.5e-06 | -3.33e-04 | 1.76e+04 | 1.8 | 0.8 | 10000 | 0.203 | 遅い収束 | 543 | 0.0531 | 948 |
| P08-N4_s1 | accel_ic/gmres | max_it | 10000 | 10000 | 2.1e-06 | -3.60e-04 | 1.64e+04 | 1.6 | 0.7827 | 10000 | 0.178 | 遅い収束 | 804 | 0.0792 | 1312 |
| P08-N8_s1 | gs/gmres | max_it | 10000 | 10000 | 7.4e-05 | -2.31e-04 | 2.67e+04 | 2.7 | 0.8546 | 10000 | 0.324 | 遅い収束 | 705 | 0.0683 | 1846 |
| P08-N8_s1 | ssor/gmres | max_it | 10000 | 10000 | 1.1e-06 | -3.51e-04 | 1.58e+04 | 1.6 | 0.7819 | 10000 | 0.189 | 遅い収束 | 753 | 0.0731 | 1174 |
| P08-N8_s1 | amg_gamg/gmres | max_it | 10000 | 10000 | 3.7e-06 | -3.44e-04 | 1.75e+04 | 1.7 | 0.7907 | 10000 | 0.188 | 遅い収束 | 1045 | 0.1021 | 1805 |
| P08-N8_s1 | accel_ic/gmres | max_it | 10000 | 10000 | 2.5e-06 | -3.44e-04 | 1.7e+04 | 1.7 | 0.7935 | 10000 | 0.19 | 遅い収束 | 1500 | 0.1478 | 2528 |
| case1A:standard | gs/gmres | max_it | 10000 | 10000 | 1.1e-03 | -1.70e-04 | 3.96e+04 | 4 | 0.9002 | 10000 | 0.437 | 停滞 | 170 | 0.0163 | 650 |
| case1A:standard | ssor/gmres | max_it | 10000 | 10000 | 6.6e-04 | -1.79e-04 | 3.69e+04 | 3.7 | 0.8831 | 10000 | 0.417 | 遅い収束 | 181 | 0.0174 | 645 |
| case1A:standard | amg_gamg/gmres | max_it | 10000 | 10000 | 4.4e-01 | -1.91e-06 | 4.02e+06 | 4e+02 | 0.9988 | 10000 | 0.991 | 停滞 | 241 | 0.0234 | 93873 |
| case1A:standard | amg_gamg/cocg | max_it | 50000 | 50000 | 2.6e-01 | -7.28e-06 | 1.07e+06 | 21 | - | 42818 | 0.748 | 停滞 | 745 | 0.0148 | 15756 |
| case1A:standard | accel_ic/gmres | max_it | 10000 | 10000 | 8.2e-06 | -3.56e-04 | 1.82e+04 | 1.8 | 0.7696 | 10000 | 0.175 | 遅い収束 | 360 | 0.0353 | 647 |
| case1A:standard | cslp/gmres | max_it | 3000 | 3000 | 1.5e-01 | -5.87e-06 | 1.22e+06 | 4.1e+02 | 0.9956 | 3000 | 0.993 | 停滞 | 810 | 0.267 | 326836 |
| case1A:standard | cslp_hx/gmres | max_it | 1000 | 1000 | 2.1e-01 | -1.09e-04 | 6.79e+04（悲観側） | 68 | 0.5904 | 1000 | 0.948 | 停滞 | 292 | 0.2824 | 19173 |
| case1A:high_freq | gs/gmres | max_it | 10000 | 10000 | 3.7e-03 | -1.02e-04 | 6.45e+04 | 6.5 | 0.9306 | 10000 | 0.609 | 停滞 | 255 | 0.0244 | 1584 |
| case1A:high_freq | ssor/gmres | max_it | 10000 | 10000 | 3.1e-03 | -1.07e-04 | 6.11e+04 | 6.1 | 0.9286 | 10000 | 0.597 | 停滞 | 271 | 0.0261 | 1600 |
| case1A:high_freq | amg_gamg/gmres | max_it | 10000 | 10000 | 4.9e-01 | -4.94e-07 | 1.56e+07 | 1.6e+03 | 0.9997 | 10000 | 0.998 | 停滞 | 365 | 0.0353 | 550135 |
| case1A:high_freq | amg_gamg/cocg | max_it | 50000 | 50000 | 5.5e-01 | -6.82e-08 | 1.14e+08 | 2.3e+03 | - | 49847 | 0.963 | 停滞 | 1136 | 0.0225 | 2555052 |
| case1A:high_freq | accel_ic/gmres | max_it | 10000 | 10000 | 8.1e-05 | -2.50e-04 | 2.56e+04 | 2.6 | 0.8334 | 10000 | 0.295 | 遅い収束 | 540 | 0.0529 | 1363 |
| case1A:high_freq | cslp/gmres | max_it | 3000 | 3000 | 2.4e-01 | -8.89e-06 | 8.33e+05 | 2.8e+02 | 0.9931 | 3000 | 0.988 | 停滞 | 1240 | 0.4089 | 340717 |
| case1A:high_freq | cslp_hx/gmres | max_it | 1000 | 1000 | 2.6e-01 | -4.22e-05 | 1.77e+05（悲観側） | 1.8e+02 | 0.6404 | 1000 | 0.978 | 停滞 | 448 | 0.4336 | 76592 |
| case1A:thick_pml | gs/gmres | max_it | 10000 | 10000 | 6.0e-05 | -2.90e-04 | 2.3e+04 | 2.3 | 0.816 | 10000 | 0.236 | 遅い収束 | 265 | 0.0254 | 592 |
| case1A:thick_pml | ssor/gmres | max_it | 10000 | 10000 | 4.5e-04 | -2.02e-04 | 3.3e+04 | 3.3 | 0.875 | 10000 | 0.388 | 遅い収束 | 281 | 0.027 | 899 |
| case1A:thick_pml | amg_gamg/gmres | max_it | 10000 | 10000 | 5.3e-01 | -6.22e-08 | 1.24e+08 | 1.2e+04 | 0.9999 | 10000 | 1 | 停滞 | 379 | 0.0367 | 4557772 |
| case1A:thick_pml | amg_gamg/cocg | max_it | 50000 | 50000 | 1.0e+00 | 0.00e+00 | ∞ | ∞ | - | 0 | 1 | 停滞 | 1179 | 0.0234 | ∞ |
| case1A:thick_pml | cslp/gmres | max_it | 3000 | 3000 | 4.6e-01 | -1.61e-06 | 4.75e+06 | 1.6e+03 | 0.9983 | 3000 | 0.998 | 停滞 | 1288 | 0.4248 | 2017945 |
| case1A:thick_pml | cslp_hx/gmres | max_it | 1000 | 1000 | 4.1e-01 | -1.79e-05 | 4.27e+05（悲観側） | 4.3e+02 | 0.742 | 1000 | 0.99 | 停滞 | 474 | 0.4598 | 196239 |
| case1A:thin_pml | gs/gmres | max_it | 10000 | 10000 | 5.6e-03 | -9.30e-05 | 7.18e+04 | 7.2 | 0.9271 | 10000 | 0.653 | 停滞 | 104 | 0.01 | 720 |
| case1A:thin_pml | ssor/gmres | max_it | 10000 | 10000 | 1.4e-03 | -1.39e-04 | 4.7e+04 | 4.7 | 0.9148 | 10000 | 0.522 | 停滞 | 111 | 0.0106 | 503 |
| case1A:thin_pml | amg_gamg/gmres | max_it | 10000 | 10000 | 2.5e-03 | -1.04e-04 | 6.19e+04 | 6.2 | 0.9397 | 10000 | 0.621 | 停滞 | 147 | 0.0142 | 885 |
| case1A:thin_pml | accel_ic/gmres | max_it | 10000 | 10000 | 2.2e-03 | -1.00e-04 | 6.33e+04 | 6.3 | 0.929 | 10000 | 0.602 | 停滞 | 224 | 0.022 | 1393 |
| case1A:thin_pml | hx/gmres | max_it | 10000 | 10000 | 2.1e-01 | -3.30e-06 | 2.23e+06 | 2.2e+02 | 0.9987 | 10000 | 0.982 | 停滞 | 646 | 0.064 | 142641 |
| case1B:mie_low_eps | gs/gmres | max_it | 10000 | 10000 | 2.8e-02 | -5.12e-05 | 1.36e+05 | 14 | 0.9654 | 10000 | 0.777 | 停滞 | 121 | 0.0116 | 1577 |
| case1B:mie_low_eps | ssor/gmres | max_it | 10000 | 10000 | 3.4e-02 | -4.47e-05 | 1.56e+05 | 16 | 0.97 | 10000 | 0.806 | 停滞 | 128 | 0.0123 | 1928 |
| case1B:mie_low_eps | amg_gamg/gmres | max_it | 10000 | 10000 | 4.5e-01 | -1.20e-07 | 6.37e+07 | 6.4e+03 | 0.9999 | 10000 | 0.999 | 停滞 | 171 | 0.0166 | 1057954 |
| case1B:mie_low_eps | amg_gamg/cocg | max_it | 50000 | 50000 | 2.7e-01 | -7.42e-06 | 1.05e+06 | 21 | - | 46527 | 0.562 | 停滞 | 530 | 0.0105 | 11051 |
| case1B:mie_low_eps | accel_ic/gmres | max_it | 10000 | 10000 | 3.1e-03 | -1.34e-04 | 5.09e+04 | 5.1 | 0.9084 | 10000 | 0.511 | 停滞 | 261 | 0.0256 | 1305 |
| case1B:mie_low_eps | cslp/gmres | max_it | 3000 | 3000 | 5.7e-02 | -5.20e-05 | 1.33e+05 | 44 | 0.962 | 3000 | 0.928 | 停滞 | 570 | 0.1879 | 24992 |
| case1B:mie_low_eps | cslp_hx/gmres | max_it | 1000 | 1000 | 3.8e-02 | -1.01e-03 | 7.54e+03（悲観側） | 7.5 | 0.3391 | 1000 | 0.575 | 停滞 | 206 | 0.1989 | 1506 |
| case1B:mie_mid_eps | gs/gmres | max_it | 10000 | 10000 | 1.4e-01 | -1.21e-06 | 5.91e+06 | 5.9e+02 | 0.9994 | 10000 | 0.994 | 停滞 | 141 | 0.0135 | 79927 |
| case1B:mie_mid_eps | ssor/gmres | max_it | 10000 | 10000 | 1.4e-01 | -1.33e-07 | 5.39e+07 | 5.4e+03 | 0.9999 | 10000 | 0.999 | 停滞 | 150 | 0.0144 | 777434 |
| case1B:mie_mid_eps | amg_gamg/gmres | max_it | 10000 | 10000 | 4.6e-01 | -3.02e-07 | 2.54e+07 | 2.5e+03 | 0.9998 | 10000 | 0.999 | 停滞 | 201 | 0.0195 | 496113 |
| case1B:mie_mid_eps | amg_gamg/cocg | max_it | 50000 | 50000 | 9.8e-01 | 0.00e+00 | ∞ | ∞ | - | 24831 | 1 | 停滞 | 626 | 0.0124 | ∞ |
| case1B:mie_mid_eps | accel_ic/gmres | max_it | 10000 | 10000 | 8.5e-02 | -8.57e-06 | 8.18e+05 | 82 | 0.9937 | 10000 | 0.961 | 停滞 | 304 | 0.0298 | 24368 |
| case1B:mie_mid_eps | cslp/gmres | max_it | 3000 | 3000 | 1.4e-01 | -1.42e-06 | 5.03e+06 | 1.7e+03 | 0.9985 | 3000 | 0.998 | 停滞 | 676 | 0.223 | 1121324 |
| case1B:mie_mid_eps | cslp_hx/gmres | max_it | 1000 | 1000 | 1.0e-01 | -4.53e-04 | 1.65e+04（悲観側） | 16 | 0.4666 | 999 | 0.795 | 停滞 | 244 | 0.2362 | 3892 |
| case1B:mie_high_eps | gs/gmres | max_it | 10000 | 10000 | 1.6e-01 | -2.07e-07 | 3.48e+07 | 3.5e+03 | 0.9999 | 10000 | 0.999 | 停滞 | 162 | 0.0155 | 540703 |
| case1B:mie_high_eps | ssor/gmres | max_it | 10000 | 10000 | 1.6e-01 | -9.81e-07 | 7.34e+06 | 7.3e+02 | 0.9994 | 10000 | 0.995 | 停滞 | 173 | 0.0166 | 121789 |
| case1B:mie_high_eps | ssor/cocg | max_it | 50000 | 50000 | 3.4e-08 | -1.97e-04 | 5.27e+04 | 1.1 | - | 49508 | 0 | 遅い収束 | 430 | 0.0085 | 450 |
| case1B:mie_high_eps | amg_gamg/gmres | max_it | 10000 | 10000 | 4.2e-01 | -1.38e-07 | 5.51e+07 | 5.5e+03 | 0.9999 | 10000 | 0.999 | 停滞 | 232 | 0.0225 | 1239384 |
| case1B:mie_high_eps | amg_gamg/cocg | max_it | 50000 | 50000 | 6.2e-01 | -5.69e-06 | 1.42e+06 | 28 | - | 34028 | 0.701 | 停滞 | 721 | 0.0143 | 20277 |
| case1B:mie_high_eps | accel_ic/gmres | max_it | 10000 | 10000 | 1.1e-01 | -3.09e-06 | 2.28e+06 | 2.3e+02 | 0.9981 | 10000 | 0.985 | 停滞 | 347 | 0.034 | 77684 |
| case1B:mie_high_eps | cslp/gmres | max_it | 3000 | 3000 | 2.2e-01 | -2.22e-05 | 3.33e+05 | 1.1e+02 | 0.9853 | 3000 | 0.974 | 停滞 | 778 | 0.2565 | 85494 |
| case1B:mie_high_eps | hx/gmres | max_it | 10000 | 10000 | 3.5e-08 | -6.25e-04 | 1.09e+04 | 1.1 | 0.6697 | 10000 | 0.053 | 遅い収束 | 1052 | 0.1042 | 1141 |
| case1B:mie_high_eps | cslp_hx/gmres | max_it | 1000 | 1000 | 2.5e-01 | -5.81e-05 | 1.28e+05（悲観側） | 1.3e+02 | 0.6312 | 1000 | 0.969 | 停滞 | 282 | 0.2728 | 35047 |
| case1B:mie_ultra_high_eps | gs/gmres | max_it | 10000 | 10000 | 2.0e-01 | -9.03e-08 | 8.1e+07 | 8.1e+03 | 0.9999 | 10000 | 1 | 停滞 | 210 | 0.0201 | 1627903 |
| case1B:mie_ultra_high_eps | ssor/gmres | max_it | 10000 | 10000 | 1.9e-01 | -2.70e-07 | 2.7e+07 | 2.7e+03 | 0.9999 | 10000 | 0.999 | 停滞 | 223 | 0.0214 | 579518 |
| case1B:mie_ultra_high_eps | ssor/cocg | max_it | 50000 | 50000 | 3.2e-04 | -1.10e-04 | 9.09e+04 | 1.8 | - | 49025 | 0.006 | 遅い収束 | 557 | 0.011 | 1003 |
| case1B:mie_ultra_high_eps | amg_gamg/gmres | max_it | 10000 | 10000 | 5.4e-01 | -5.29e-07 | 1.46e+07 | 1.5e+03 | 0.9997 | 10000 | 0.997 | 停滞 | 300 | 0.0291 | 426234 |
| case1B:mie_ultra_high_eps | amg_gamg/cocg | max_it | 50000 | 50000 | 7.1e-01 | -7.00e-06 | 1.17e+06 | 23 | - | 42094 | 0.746 | 停滞 | 941 | 0.0186 | 21866 |
| case1B:mie_ultra_high_eps | accel_ic/gmres | max_it | 10000 | 10000 | 1.5e-01 | -2.07e-06 | 3.48e+06 | 3.5e+02 | 0.9986 | 10000 | 0.99 | 停滞 | 447 | 0.0438 | 152419 |
| case1B:mie_ultra_high_eps | accel_ic/cocg | max_it | 50000 | 50000 | 1.5e-07 | -1.59e-04 | 5.75e+04 | 1.1 | - | 49562 | 0 | 遅い収束 | 489 | 0.0096 | 558 |
| case1B:mie_ultra_high_eps | cslp/gmres | max_it | 3000 | 3000 | 1.9e-01 | -1.89e-06 | 3.86e+06 | 1.3e+03 | 0.9985 | 3000 | 0.997 | 停滞 | 1015 | 0.3348 | 1291463 |
| case1B:mie_ultra_high_eps | hx/gmres | max_it | 10000 | 10000 | 5.2e-02 | -8.92e-06 | 7.63e+05 | 76 | 0.9983 | 10000 | 0.962 | 停滞 | 1445 | 0.1433 | 109297 |
| case1B:mie_ultra_high_eps | cslp_hx/gmres | max_it | 1000 | 1000 | 1.6e-01 | -2.88e-04 | 2.6e+04（悲観側） | 26 | 0.5427 | 1000 | 0.859 | 停滞 | 372 | 0.3604 | 9392 |
| case1C:narrow_aperture | gs/gmres | max_it | 10000 | 10000 | 3.1e-03 | -1.39e-04 | 4.96e+04 | 5 | 0.9056 | 10000 | 0.503 | 停滞 | 164 | 0.0157 | 782 |
| case1C:narrow_aperture | ssor/gmres | max_it | 10000 | 10000 | 1.8e-03 | -1.68e-04 | 4.14e+04 | 4.1 | 0.8934 | 10000 | 0.449 | 遅い収束 | 174 | 0.0167 | 697 |
| case1C:narrow_aperture | amg_gamg/gmres | max_it | 10000 | 10000 | 6.1e-01 | -2.29e-07 | 3.4e+07 | 3.4e+03 | 0.9999 | 10000 | 0.999 | 停滞 | 233 | 0.0225 | 766242 |
| case1C:narrow_aperture | amg_gamg/cocg | max_it | 50000 | 50000 | 7.4e-01 | -6.57e-06 | 1.25e+06 | 25 | - | 35934 | 0.74 | 停滞 | 718 | 0.0142 | 17750 |
| case1C:narrow_aperture | accel_ic/gmres | max_it | 10000 | 10000 | 2.3e-05 | -3.51e-04 | 1.96e+04 | 2 | 0.7934 | 10000 | 0.184 | 遅い収束 | 349 | 0.0342 | 674 |
| case1C:narrow_aperture | cslp/gmres | max_it | 3000 | 3000 | 3.5e-01 | -3.26e-06 | 2.31e+06 | 7.7e+02 | 0.9953 | 3000 | 0.989 | 停滞 | 781 | 0.2575 | 595786 |
| case1C:narrow_aperture | cslp_hx/gmres | max_it | 1000 | 1000 | 2.8e-01 | -7.73e-05 | 9.75e+04（悲観側） | 97 | 0.6578 | 1000 | 0.961 | 停滞 | 281 | 0.2717 | 26488 |
| case1C:medium_aperture | gs/gmres | max_it | 10000 | 10000 | 3.6e-03 | -1.38e-04 | 5.02e+04 | 5 | 0.9083 | 10000 | 0.511 | 停滞 | 165 | 0.0158 | 798 |
| case1C:medium_aperture | ssor/gmres | max_it | 10000 | 10000 | 1.8e-03 | -1.64e-04 | 4.21e+04 | 4.2 | 0.9022 | 10000 | 0.446 | 停滞 | 175 | 0.0169 | 714 |
| case1C:medium_aperture | amg_gamg/gmres | max_it | 10000 | 10000 | 5.9e-01 | -6.59e-08 | 1.18e+08 | 1.2e+04 | 0.9999 | 10000 | 1 | 停滞 | 235 | 0.0228 | 2686090 |
| case1C:medium_aperture | amg_gamg/cocg | max_it | 50000 | 50000 | 7.4e-01 | -4.59e-06 | 1.76e+06 | 35 | - | 29887 | 0.743 | 停滞 | 723 | 0.0143 | 25294 |
| case1C:medium_aperture | accel_ic/gmres | max_it | 10000 | 10000 | 3.3e-05 | -3.44e-04 | 2.02e+04 | 2 | 0.7949 | 10000 | 0.19 | 遅い収束 | 351 | 0.0344 | 700 |
| case1C:medium_aperture | cslp/gmres | max_it | 3000 | 3000 | 2.0e-01 | -8.24e-05 | 9.15e+04 | 31 | 0.945 | 3000 | 0.89 | 停滞 | 787 | 0.2594 | 23744 |
| case1C:medium_aperture | cslp_hx/gmres | max_it | 1000 | 1000 | 3.7e-01 | -7.12e-05 | 1.07e+05（悲観側） | 1.1e+02 | 0.7169 | 997 | 0.964 | 停滞 | 283 | 0.274 | 29412 |
| case1C:wide_aperture | gs/gmres | max_it | 10000 | 10000 | 6.6e-03 | -9.62e-05 | 7.05e+04 | 7 | 0.9353 | 10000 | 0.63 | 停滞 | 161 | 0.0155 | 1095 |
| case1C:wide_aperture | ssor/gmres | max_it | 10000 | 10000 | 6.2e-03 | -9.15e-05 | 7.33e+04 | 7.3 | 0.9451 | 10000 | 0.642 | 停滞 | 172 | 0.0165 | 1214 |
| case1C:wide_aperture | amg_gamg/gmres | max_it | 10000 | 10000 | 6.2e-01 | -8.58e-08 | 9.08e+07 | 9.1e+03 | 0.9999 | 10000 | 1 | 停滞 | 231 | 0.0223 | 2028617 |
| case1C:wide_aperture | amg_gamg/cocg | max_it | 50000 | 50000 | 7.4e-01 | -4.30e-06 | 1.88e+06 | 38 | - | 32708 | 0.742 | 停滞 | 711 | 0.0141 | 26489 |
| case1C:wide_aperture | accel_ic/gmres | max_it | 10000 | 10000 | 1.3e-04 | -2.51e-04 | 2.64e+04 | 2.6 | 0.8438 | 10000 | 0.301 | 遅い収束 | 345 | 0.0338 | 897 |
| case1C:wide_aperture | cslp/gmres | max_it | 3000 | 3000 | 1.4e-01 | -1.08e-04 | 6.9e+04 | 23 | 0.9265 | 3000 | 0.873 | 停滞 | 776 | 0.2559 | 17658 |
| case1C:wide_aperture | cslp_hx/gmres | max_it | 1000 | 1000 | 2.3e-01 | -2.87e-04 | 2.67e+04（悲観側） | 27 | 0.6168 | 1000 | 0.866 | 停滞 | 278 | 0.2688 | 7189 |
| case2A:standard | gs/gmres | max_it | 10000 | 10000 | 3.9e-07 | -3.59e-04 | 1.44e+04 | 1.4 | 0.7782 | 10000 | 0.187 | 遅い収束 | 181 | 0.0176 | 259 |
| case2A:standard | amg_gamg/gmres | max_it | 10000 | 10000 | 3.4e-05 | -2.15e-04 | 2.64e+04 | 2.6 | 0.8529 | 10000 | 0.332 | 遅い収束 | 260 | 0.0254 | 676 |
| case2A:standard | hx/gmres | max_it | 10000 | 10000 | 8.6e-05 | -4.33e-04 | 1.91e+04 | 1.9 | 0.7803 | 10000 | 0.145 | 遅い収束 | 872 | 0.0863 | 1655 |
| case2B:narrow_iris | hx/gmres | max_it | 10000 | 10000 | 1.4e-04 | -2.57e-04 | 2.62e+04 | 2.6 | 0.9124 | 10000 | 0.365 | 停滞 | 635 | 0.0629 | 1650 |
| case2B:medium_iris | hx/gmres | max_it | 10000 | 10000 | 3.7e-06 | -4.46e-04 | 1.58e+04 | 1.6 | 0.669 | 9999 | 0.094 | 遅い収束 | 474 | 0.0469 | 744 |
| case2B:wide_iris | hx/gmres | max_it | 10000 | 10000 | 7.4e-06 | -4.00e-04 | 1.72e+04 | 1.7 | 0.7983 | 10000 | 0.161 | 遅い収束 | 460 | 0.0455 | 786 |
| case2C:narrow_slit | hx/gmres | max_it | 10000 | 10000 | 1.2e-03 | -2.33e-04 | 3.18e+04 | 3.2 | 0.8519 | 10000 | 0.326 | 遅い収束 | 512 | 0.0507 | 1615 |
| case2C:medium_slit | hx/gmres | max_it | 10000 | 10000 | 2.4e-05 | -3.76e-04 | 1.9e+04 | 1.9 | 0.7973 | 10000 | 0.168 | 遅い収束 | 502 | 0.0497 | 949 |
| case2C:wide_slit | hx/gmres | max_it | 10000 | 10000 | 1.2e-05 | -3.62e-04 | 1.86e+04 | 1.9 | 0.8086 | 10000 | 0.22 | 遅い収束 | 509 | 0.0504 | 941 |
| case2D:few_walls | gs/gmres | max_it | 10000 | 10000 | 4.4e-07 | -5.56e-04 | 1.3e+04 | 1.3 | 0.6391 | 10000 | 0.079 | 遅い収束 | 211 | 0.0205 | 271 |
| case2D:few_walls | amg_gamg/gmres | max_it | 10000 | 10000 | 3.5e-05 | -2.25e-04 | 2.57e+04 | 2.6 | 0.8936 | 10000 | 0.369 | 遅い収束 | 300 | 0.0294 | 763 |
| case2D:few_walls | accel_ic/gmres | max_it | 10000 | 10000 | 1.3e-08 | -5.16e-04 | 1.02e+04 | 1 | 0.7044 | 10000 | 0.087 | 遅い収束 | 449 | 0.0443 | 458 |
| case2D:few_walls | cslp_hx/gmres | max_it | 1000 | 1000 | 4.2e-07 | -3.27e-03 | 1.5e+03（悲観側） | 1.5 | 0.0088 | 1000 | 0.106 | 遅い収束 | 353 | 0.3438 | 523 |
| case2D:many_walls | gs/gmres | max_it | 10000 | 10000 | 5.9e-03 | -7.18e-06 | 8.14e+05 | 81 | 0.9947 | 10000 | 0.966 | 停滞 | 187 | 0.0182 | 14794 |
| case2D:many_walls | ssor/gmres | max_it | 10000 | 10000 | 5.2e-03 | -1.35e-05 | 4.35e+05 | 44 | 0.994 | 10000 | 0.928 | 停滞 | 198 | 0.0193 | 8413 |
| case2D:many_walls | amg_gamg/gmres | max_it | 10000 | 10000 | 4.4e-03 | -1.39e-05 | 4.16e+05 | 42 | 0.9905 | 10000 | 0.937 | 停滞 | 263 | 0.0257 | 10719 |
| case2D:many_walls | accel_ic/gmres | max_it | 10000 | 10000 | 4.8e-03 | -1.07e-05 | 5.43e+05 | 54 | 0.9931 | 10000 | 0.946 | 停滞 | 400 | 0.0394 | 21417 |
| case2D:many_walls | cslp/gmres | max_it | 3000 | 3000 | 8.6e-04 | -5.69e-05 | 8.98e+04 | 30 | 0.9472 | 3000 | 0.902 | 停滞 | 864 | 0.2857 | 25661 |
| case2D:many_walls | hx/gmres | max_it | 10000 | 10000 | 3.1e-03 | -1.42e-04 | 4.87e+04 | 4.9 | 0.8721 | 10000 | 0.538 | 停滞 | 887 | 0.0879 | 4284 |
| case2D:many_walls | cslp_hx/gmres | max_it | 1000 | 1000 | 2.1e-03 | -3.33e-04 | 1.7e+04（悲観側） | 17 | 0.1303 | 1000 | 0.775 | 停滞 | 298 | 0.29 | 4942 |
| case3A:high_contrast | gs/gmres | max_it | 10000 | 10000 | 4.8e-03 | -7.59e-05 | 8.48e+04 | 8.5 | 0.9489 | 10000 | 0.707 | 停滞 | 191 | 0.0186 | 1581 |
| case3A:high_contrast | ssor/gmres | max_it | 10000 | 10000 | 7.0e-04 | -1.38e-04 | 4.5e+04 | 4.5 | 0.9055 | 10000 | 0.509 | 停滞 | 204 | 0.0199 | 901 |
| case3A:high_contrast | amg_gamg/gmres | max_it | 10000 | 10000 | 5.4e-03 | -8.31e-05 | 7.9e+04 | 7.9 | 0.9427 | 10000 | 0.686 | 停滞 | 275 | 0.0269 | 2132 |
| case3A:high_contrast | amg_gamg/cocg | max_it | 50000 | 50000 | 2.2e-08 | -2.27e-04 | 5.15e+04 | 1 | - | 49745 | 0 | 遅い収束 | 863 | 0.0171 | 889 |
| case3A:high_contrast | accel_ic/gmres | max_it | 10000 | 10000 | 1.2e-03 | -1.05e-04 | 5.83e+04 | 5.8 | 0.9304 | 10000 | 0.612 | 停滞 | 409 | 0.0404 | 2358 |
| case3A:high_contrast | cslp/gmres | max_it | 3000 | 3000 | 3.5e-05 | -6.33e-04 | 8.6e+03 | 2.9 | 0.6227 | 3000 | 0.392 | 遅い収束 | 937 | 0.3099 | 2672 |
| case3A:high_contrast | hx/gmres | max_it | 10000 | 10000 | 2.1e-02 | -5.44e-08 | 1.16e+08 | 1.2e+04 | 1 | 9898 | 1 | 停滞 | 1000 | 0.0991 | 11506520 |
| case3A:high_contrast | cslp_hx/gmres | max_it | 1000 | 1000 | 1.3e-03 | -1.18e-03 | 5.31e+03（悲観側） | 5.3 | 0.1146 | 1000 | 0.443 | 遅い収束 | 327 | 0.319 | 1703 |
| case3B:few_layers | gs/gmres | max_it | 10000 | 10000 | 1.2e-03 | -1.08e-04 | 5.72e+04 | 5.7 | 0.9158 | 10000 | 0.57 | 停滞 | 158 | 0.0154 | 884 |
| case3B:few_layers | ssor/gmres | max_it | 10000 | 10000 | 1.9e-04 | -1.47e-04 | 3.9e+04 | 3.9 | 0.9063 | 10000 | 0.493 | 停滞 | 169 | 0.0164 | 645 |
| case3B:few_layers | amg_gamg/gmres | max_it | 10000 | 10000 | 5.0e-04 | -1.35e-04 | 4.48e+04 | 4.5 | 0.9586 | 10000 | 0.516 | 停滞 | 227 | 0.0222 | 999 |
| case3B:few_layers | accel_ic/gmres | max_it | 10000 | 10000 | 4.0e-04 | -1.10e-04 | 5.17e+04 | 5.2 | 0.9296 | 10000 | 0.575 | 停滞 | 339 | 0.0335 | 1736 |
| case3B:few_layers | cslp/gmres | max_it | 3000 | 3000 | 9.8e-08 | -1.45e-03 | 3.69e+03 | 1.2 | 0.3659 | 3000 | 0.134 | 遅い収束 | 770 | 0.2546 | 945 |
| case3B:few_layers | hx/gmres | max_it | 10000 | 10000 | 6.3e-04 | -1.13e-04 | 5.24e+04 | 5.2 | 0.8923 | 10000 | 0.546 | 停滞 | 807 | 0.0799 | 4198 |
| case3B:few_layers | cslp_hx/gmres | max_it | 1000 | 1000 | 9.8e-05 | -1.73e-03 | 3.31e+03（悲観側） | 3.3 | 0.0522 | 1000 | 0.304 | 遅い収束 | 268 | 0.261 | 872 |
| case3B:many_layers | gs/gmres | max_it | 10000 | 10000 | 3.7e-04 | -4.99e-05 | 1.02e+05 | 10 | 0.9632 | 10000 | 0.806 | 停滞 | 247 | 0.024 | 2440 |
| case3B:many_layers | ssor/gmres | max_it | 10000 | 10000 | 1.2e-04 | -9.61e-05 | 5.23e+04 | 5.2 | 0.9379 | 10000 | 0.611 | 停滞 | 262 | 0.0255 | 1340 |
| case3B:many_layers | amg_gamg/gmres | max_it | 10000 | 10000 | 1.5e-04 | -1.07e-04 | 4.89e+04 | 4.9 | 0.9103 | 10000 | 0.614 | 停滞 | 352 | 0.0344 | 1690 |
| case3B:many_layers | accel_ic/gmres | max_it | 10000 | 10000 | 1.9e-04 | -6.47e-05 | 7.6e+04 | 7.6 | 0.9543 | 10000 | 0.718 | 停滞 | 525 | 0.0518 | 3942 |
| case3B:many_layers | hx/gmres | max_it | 10000 | 10000 | 7.5e-03 | -5.87e-05 | 1.1e+05 | 11 | 0.9692 | 10000 | 0.788 | 停滞 | 1373 | 0.1361 | 14992 |
| case3B:many_layers | cslp_hx/gmres | max_it | 1000 | 1000 | 9.8e-07 | -2.64e-03 | 1.75e+03（悲観側） | 1.8 | 0.0121 | 1000 | 0.146 | 遅い収束 | 420 | 0.4101 | 730 |
| case3C:coarse_check | gs/gmres | max_it | 10000 | 10000 | 3.8e-02 | -9.13e-05 | 8.21e+04 | 8.2 | 0.9408 | 10000 | 0.624 | 停滞 | 181 | 0.0176 | 1449 |
| case3C:coarse_check | ssor/gmres | max_it | 10000 | 10000 | 1.7e-03 | -2.61e-04 | 3e+04 | 3 | 0.8285 | 10000 | 0.267 | 遅い収束 | 193 | 0.0187 | 567 |
| case3C:coarse_check | amg_gamg/gmres | max_it | 10000 | 10000 | 2.4e-02 | -9.45e-05 | 7.76e+04 | 7.8 | 0.936 | 10000 | 0.632 | 停滞 | 257 | 0.0251 | 1955 |
| case3C:coarse_check | accel_ic/gmres | max_it | 10000 | 10000 | 1.3e-02 | -1.17e-04 | 6.23e+04 | 6.2 | 0.9215 | 10000 | 0.56 | 停滞 | 391 | 0.0386 | 2409 |
| case3C:coarse_check | hx/gmres | max_it | 10000 | 10000 | 4.5e-07 | -5.15e-04 | 1.32e+04 | 1.3 | 0.6746 | 10000 | 0.076 | 遅い収束 | 983 | 0.0975 | 1296 |
| case3C:coarse_check | cslp_hx/gmres | max_it | 1000 | 1000 | 2.3e-07 | -5.02e-03 | 1.27e+03（悲観側） | 1.3 | 0.008 | 1000 | 0.033 | 遅い収束 | 301 | 0.293 | 380 |
| case3C:medium_check | gs/gmres | max_it | 10000 | 10000 | 2.8e-03 | -1.22e-04 | 5.46e+04 | 5.5 | 0.9233 | 10000 | 0.553 | 停滞 | 181 | 0.0175 | 964 |
| case3C:medium_check | ssor/gmres | max_it | 10000 | 10000 | 3.5e-04 | -7.88e-05 | 6.76e+04 | 6.8 | 0.9459 | 10000 | 0.68 | 停滞 | 192 | 0.0187 | 1269 |
| case3C:medium_check | amg_gamg/gmres | max_it | 10000 | 10000 | 2.7e-04 | -5.24e-05 | 9.46e+04 | 9.5 | 0.9653 | 10000 | 0.775 | 停滞 | 256 | 0.0249 | 2367 |
| case3C:medium_check | accel_ic/gmres | max_it | 10000 | 10000 | 4.4e-04 | -6.69e-05 | 7.94e+04 | 7.9 | 0.9565 | 10000 | 0.728 | 停滞 | 390 | 0.0385 | 3060 |
| case3C:medium_check | cslp_hx/gmres | max_it | 1000 | 1000 | 1.2e-07 | -4.01e-03 | 1.27e+03（悲観側） | 1.3 | 0.0055 | 1000 | 0.053 | 遅い収束 | 296 | 0.2883 | 373 |
| case3C:fine_check | gs/gmres | max_it | 10000 | 10000 | 1.8e-02 | -8.73e-05 | 8.18e+04 | 8.2 | 0.9432 | 10000 | 0.645 | 停滞 | 226 | 0.0219 | 1801 |
| case3C:fine_check | ssor/gmres | max_it | 10000 | 10000 | 6.3e-04 | -1.93e-04 | 3.49e+04 | 3.5 | 0.8765 | 10000 | 0.406 | 遅い収束 | 240 | 0.0233 | 820 |
| case3C:fine_check | amg_gamg/gmres | max_it | 10000 | 10000 | 1.6e-03 | -1.78e-04 | 3.92e+04 | 3.9 | 0.8834 | 10000 | 0.453 | 遅い収束 | 318 | 0.0311 | 1226 |
| case3C:fine_check | accel_ic/gmres | max_it | 10000 | 10000 | 8.7e-04 | -2.25e-04 | 3.19e+04 | 3.2 | 0.8573 | 10000 | 0.37 | 遅い収束 | 485 | 0.0478 | 1533 |
| case3D:sparse_array | gs/gmres | max_it | 10000 | 10000 | 1.5e-06 | -4.77e-04 | 1.46e+04 | 1.5 | 0.8174 | 10000 | 0.091 | 遅い収束 | 57 | 0.0055 | 82 |
| case3D:dense_array | gs/gmres | max_it | 10000 | 10000 | 3.0e-04 | -5.95e-05 | 8.53e+04 | 8.5 | 0.9545 | 10000 | 0.759 | 停滞 | 226 | 0.0219 | 1876 |
| case3D:dense_array | ssor/gmres | max_it | 10000 | 10000 | 2.5e-05 | -3.88e-04 | 1.87e+04 | 1.9 | 0.8976 | 10000 | 0.156 | 遅い収束 | 240 | 0.0233 | 444 |
| case3D:dense_array | amg_gamg/gmres | max_it | 10000 | 10000 | 5.3e-05 | -7.16e-05 | 6.21e+04 | 6.2 | 0.9583 | 10000 | 0.688 | 停滞 | 322 | 0.0314 | 1959 |
| case3D:dense_array | accel_ic/gmres | max_it | 10000 | 10000 | 2.3e-05 | -2.38e-04 | 2.41e+04 | 2.4 | 0.8445 | 10000 | 0.32 | 遅い収束 | 486 | 0.048 | 1163 |
| case3D:dense_array | hx/gmres | max_it | 10000 | 10000 | 4.2e-04 | -2.07e-04 | 3.23e+04 | 3.2 | 0.823 | 10000 | 0.365 | 遅い収束 | 1522 | 0.1512 | 4890 |
| case3D:dense_array | cslp_hx/gmres | max_it | 1000 | 1000 | 8.0e-07 | -4.05e-03 | 1.47e+03（悲観側） | 1.5 | 0.0116 | 1000 | 0.085 | 遅い収束 | 378 | 0.3678 | 550 |
| case3E:low_loss | gs/gmres | max_it | 10000 | 10000 | 1.2e-05 | -2.57e-04 | 2.19e+04 | 2.2 | 0.8347 | 10000 | 0.277 | 遅い収束 | 165 | 0.016 | 357 |
| case3E:low_loss | ssor/gmres | max_it | 10000 | 10000 | 6.0e-08 | -4.58e-04 | 1.17e+04 | 1.2 | 0.7283 | 10000 | 0.109 | 遅い収束 | 177 | 0.0172 | 206 |
| case3E:low_loss | amg_gamg/gmres | max_it | 10000 | 10000 | 9.3e-05 | -1.54e-04 | 3.57e+04 | 3.6 | 0.9093 | 10000 | 0.462 | 停滞 | 238 | 0.0233 | 837 |
| case3E:low_loss | amg_gamg/cocg | max_it | 50000 | 50000 | 1.9e-07 | -1.21e-04 | 6.05e+04 | 1.2 | - | 48626 | 0 | 遅い収束 | 754 | 0.015 | 911 |
| case3E:low_loss | accel_ic/gmres | max_it | 10000 | 10000 | 3.1e-07 | -4.09e-04 | 1.36e+04 | 1.4 | 0.7487 | 10000 | 0.141 | 遅い収束 | 356 | 0.0351 | 483 |
| case3E:low_loss | cslp_hx/gmres | max_it | 1000 | 1000 | 8.1e-07 | -3.27e-03 | 1.59e+03（悲観側） | 1.6 | 0.0117 | 1000 | 0.11 | 遅い収束 | 286 | 0.2786 | 449 |
| case3F:low_contrast_no_loss | gs/gmres | max_it | 10000 | 10000 | 1.2e-02 | -7.07e-05 | 9.61e+04 | 9.6 | 0.9472 | 10000 | 0.697 | 停滞 | 199 | 0.0194 | 1866 |
| case3F:low_contrast_no_loss | ssor/gmres | max_it | 10000 | 10000 | 3.1e-05 | -2.43e-04 | 2.44e+04 | 2.4 | 0.8391 | 10000 | 0.293 | 遅い収束 | 212 | 0.0206 | 508 |
| case3F:low_contrast_no_loss | amg_gamg/gmres | max_it | 10000 | 10000 | 2.3e-06 | -5.60e-04 | 1.42e+04 | 1.4 | 0.708 | 10000 | 0.049 | 遅い収束 | 282 | 0.0276 | 399 |
| case3F:low_contrast_no_loss | accel_ic/gmres | max_it | 10000 | 10000 | 4.9e-04 | -1.53e-04 | 4.06e+04 | 4.1 | 0.893 | 10000 | 0.453 | 遅い収束 | 429 | 0.0423 | 1722 |
| case3F:high_contrast_with_loss | gs/gmres | max_it | 10000 | 10000 | 6.6e-02 | -2.49e-05 | 2.84e+05 | 28 | 0.983 | 10000 | 0.889 | 停滞 | 199 | 0.0194 | 5501 |
| case3F:high_contrast_with_loss | ssor/gmres | max_it | 10000 | 10000 | 2.9e-02 | -6.22e-05 | 1.14e+05 | 11 | 0.9587 | 10000 | 0.737 | 停滞 | 212 | 0.0206 | 2350 |
| case3F:high_contrast_with_loss | amg_gamg/gmres | max_it | 10000 | 10000 | 3.2e-02 | -4.38e-05 | 1.59e+05 | 16 | 0.9703 | 10000 | 0.812 | 停滞 | 282 | 0.0276 | 4385 |
| case3F:high_contrast_with_loss | accel_ic/gmres | max_it | 10000 | 10000 | 3.7e-02 | -3.81e-05 | 1.82e+05 | 18 | 0.9747 | 10000 | 0.833 | 停滞 | 429 | 0.0423 | 7706 |
| case3F:ultra_contrast_high_loss | gs/gmres | max_it | 10000 | 10000 | 4.5e-02 | -5.82e-05 | 1.24e+05 | 12 | 0.9586 | 10000 | 0.755 | 停滞 | 199 | 0.0193 | 2409 |
| case3F:ultra_contrast_high_loss | ssor/gmres | max_it | 10000 | 10000 | 1.2e-02 | -9.01e-05 | 7.74e+04 | 7.7 | 0.9424 | 10000 | 0.643 | 停滞 | 212 | 0.0206 | 1599 |
| case3F:ultra_contrast_high_loss | amg_gamg/gmres | max_it | 10000 | 10000 | 1.4e-02 | -8.79e-05 | 7.98e+04 | 8 | 0.9457 | 10000 | 0.653 | 停滞 | 283 | 0.0276 | 2210 |
| case3F:ultra_contrast_high_loss | accel_ic/gmres | max_it | 10000 | 10000 | 1.5e-02 | -9.36e-05 | 7.6e+04 | 7.6 | 0.9416 | 10000 | 0.634 | 停滞 | 429 | 0.0423 | 3219 |
| case3F:ultra_contrast_high_loss | cslp/gmres | max_it | 3000 | 3000 | 1.1e-08 | -2.29e-03 | 3.01e+03 | 1 | 0.2202 | 3000 | 0.046 | 遅い収束 | 943 | 0.3116 | 947 |
| case3F:ultra_contrast_high_loss | hx/gmres | max_it | 10000 | 10000 | 2.1e-05 | -5.15e-04 | 1.64e+04 | 1.6 | 0.7423 | 10000 | 0.09 | 遅い収束 | 1187 | 0.1178 | 1945 |
| case3F:ultra_contrast_high_loss | cslp_hx/gmres | max_it | 1000 | 1000 | 9.3e-06 | -4.59e-03 | 1.65e+03（悲観側） | 1.6 | 0.027 | 1000 | 0.055 | 遅い収束 | 333 | 0.3241 | 542 |
