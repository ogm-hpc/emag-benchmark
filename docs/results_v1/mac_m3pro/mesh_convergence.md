# 既存ケースのメッシュ収束（B6）

`freefem/pcb/mesh_convergence.py summary` が出力。lc（パラメータ `lc*`）に倍率 s を掛けたメッシュで `mumps/direct`（s < 0.6 は MUMPS のメモリが足りないので `npatch_asm/cocg`、rtol 1e-8。ソルバー v1.0）で解き、最も細かいメッシュの解との相対差（最も細かいメッシュの上で積分、core は UPML を除いた領域）。s = 1 はベンチマークのメッシュ（B1）そのもの。メッシュが入れ子でないので2つの離散化誤差はほぼ無相関で、差は \(d(s)^2 = C^2(s^{2p} + s_{\min}^{2p})\) に従う（滑らかな場の補間で確認、`estimate` の注）。p はこの当てはめによる見かけの次数、err(1) = C は s = 1（ベンチマークのメッシュ）の誤差の推定（h → 0 の極限に対する）、fit は log d の当てはめの残差（rms）。

| set | s | ndof | l2 | curl | hcurl | l2core | curlcore | hcurlcore |
|---|---|---|---|---|---|---|---|---|
| case2A:standard | 1.00 | 92785 | 2.06e-01 | 1.95e-01 | 2.01e-01 | 2.06e-01 | 1.95e-01 | 2.01e-01 |
| case2A:standard | 0.80 | 176597 | 1.70e-01 | 1.61e-01 | 1.66e-01 | 1.70e-01 | 1.61e-01 | 1.66e-01 |
| case2A:standard | 0.63 | 361446 | 1.44e-01 | 1.36e-01 | 1.40e-01 | 1.44e-01 | 1.36e-01 | 1.40e-01 |
| case2A:standard | 0.50 | 695896 | (ref) | (ref) | (ref) | (ref) | (ref) | (ref) |
| case1A:standard | 1.00 | 85598 | 3.49e-01 | 3.16e-01 | 3.33e-01 | 3.62e-01 | 2.88e-01 | 3.28e-01 |
| case1A:standard | 0.80 | 160270 | 2.97e-01 | 2.70e-01 | 2.83e-01 | 3.08e-01 | 2.48e-01 | 2.80e-01 |
| case1A:standard | 0.63 | 333381 | 2.52e-01 | 2.23e-01 | 2.38e-01 | 2.65e-01 | 2.07e-01 | 2.38e-01 |
| case1A:standard | 0.50 | 623072 | (ref) | (ref) | (ref) | (ref) | (ref) | (ref) |
| case2A:off_resonance | 1.00 | 92785 | 7.49e-02 | 6.73e-02 | 7.08e-02 | 7.49e-02 | 6.73e-02 | 7.08e-02 |
| case2A:off_resonance | 0.80 | 176597 | 6.27e-02 | 5.70e-02 | 5.96e-02 | 6.27e-02 | 5.70e-02 | 5.96e-02 |
| case2A:off_resonance | 0.63 | 361446 | 5.29e-02 | 4.83e-02 | 5.04e-02 | 5.29e-02 | 4.83e-02 | 5.04e-02 |
| case2A:off_resonance | 0.50 | 695896 | (ref) | (ref) | (ref) | (ref) | (ref) | (ref) |
| case3A:high_contrast | 1.00 | 98004 | 7.45e-01 | 3.84e-01 | 4.05e-01 | 7.45e-01 | 3.84e-01 | 4.05e-01 |
| case3A:high_contrast | 0.80 | 184891 | 6.91e-01 | 2.30e-01 | 2.65e-01 | 6.91e-01 | 2.30e-01 | 2.65e-01 |
| case3A:high_contrast | 0.63 | 369804 | 6.25e-01 | 1.82e-01 | 2.19e-01 | 6.25e-01 | 1.82e-01 | 2.19e-01 |
| case3A:high_contrast | 0.50 | 723568 | (ref) | (ref) | (ref) | (ref) | (ref) | (ref) |

| set | p (hcurl) | err(1) hcurl | fit | p (hcurlcore) | err(1) hcurlcore | fit | p (l2core) | err(1) l2core | fit |
|---|---|---|---|---|---|---|---|---|---|
| case2A:standard | 1.08 | 1.81e-01 | 0.003 | 1.08 | 1.81e-01 | 0.003 | 1.08 | 1.86e-01 | 0.002 |
| case1A:standard | 1.02 | 3.00e-01 | 0.006 | 0.97 | 2.92e-01 | 0.003 | 0.96 | 3.22e-01 | 0.002 |
| case2A:off_resonance | 1.03 | 6.37e-02 | 0.002 | 1.03 | 6.37e-02 | 0.002 | 1.04 | 6.73e-02 | 0.001 |
| case3A:high_contrast | 1.65 | 3.73e-01 | 0.050 | 1.65 | 3.73e-01 | 0.050 | 0.60 | 6.25e-01 | 0.007 |
