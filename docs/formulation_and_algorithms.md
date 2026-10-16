# 定式化とアルゴリズム：高周波電磁界 FEM・COCG / GMRES(m)・前処理

本ベンチマーク（`freefem/`）で使っている定式化と反復法・前処理を、自前実装の参考になるように数式で整理する。記号と既定値は実装に合わせてあり、各節の末尾に対応するファイルを示す。

- 時間因子は $e^{+i\omega t}$（工学系の規約。$j$ の代わりに $i$ と書く）
- ベクトルの2つの積を区別する
  - 双一次形式（**共役を取らない**）：$u^{\mathsf T} v = \sum_k u_k v_k$
  - エルミート内積：$u^{\mathsf H} v = \sum_k \bar u_k v_k$、ノルム $\|u\| = \sqrt{u^{\mathsf H} u}$

---

## 1. 支配方程式と弱形式

### 1.1 時間調和 Maxwell 方程式（電界の2階形式）

$e^{+i\omega t}$ のもとで $\nabla\times E = -i\omega\mu H$、$\nabla\times H = i\omega\varepsilon E + J$ から $H$ を消去すると、

$$
\nabla\times\left(\mu_r^{-1}\,\nabla\times E\right) - k_0^2\,\varepsilon_r\,E = f,
\qquad f = -i\omega\mu_0 J,
\qquad k_0 = \omega\sqrt{\varepsilon_0\mu_0} = \frac{2\pi}{\lambda_0}.
$$

- 損失材料：$\varepsilon_r = \varepsilon'\,(1 - i\tan\delta)$。この規約では、受動的な媒質は $\operatorname{Im}\varepsilon_r \le 0$ になる。
- 本ベンチマークでは $\mu_r = 1$ とし、励振 $f$ はガウス分布の x 偏波体積源とする。

$$
f(x) = e_x \exp\!\left(-\frac{|x - x_s|^2}{w^2}\right).
$$

### 1.2 境界条件

- **PEC**（完全導体）：$n\times E = 0$
- **Silver–Müller 吸収境界**（1次）：外向きの平面波 $E = E_0 e^{-ik_0 n\cdot x}$ では $\nabla\times E = -ik_0\,n\times E$ なので、

$$
n\times(\nabla\times E) = i k_0\,E_t,\qquad E_t := (n\times E)\times n .
$$

### 1.3 異方性 UPML（座標伸長型の完全整合層）

計算領域の芯を直方体 $[x_-,x_+]\times[y_-,y_+]\times[z_-,z_+]$ とし、その外側を厚さ $t$ の PML で囲む。

**伸長関数**：各座標方向 $q\in\{x,y,z\}$ について、芯の外側への侵入深さを

$$
d_q = \max(q - q_+, 0) + \max(q_- - q, 0)
$$

とし、微分を $\partial_q \to s_q^{-1}\partial_q$ と置き換える。

$$
s_q = 1 - i\,\frac{\sigma_q}{k_0},\qquad
\sigma_q = \sigma_{\max}\left(\frac{d_q}{t}\right)^{m},\qquad
\sigma_{\max} = \frac{(m+1)\ln(1/R_0)}{2t}.
$$

（本実装では $m=2$、$R_0 = 10^{-4}$）

**減衰と反射**：伸長座標 $\tilde q = \int s_q\,dq$ では、外向き波 $e^{-ik_0\tilde q}$ が次のように指数的に減衰する。

$$
e^{-ik_0\tilde q} = e^{-ik_0 q}\,e^{-\int\sigma_q\,dq}.
$$

外面を PEC で打ち切ると、法線入射の往復減衰は $R = \exp\!\left(-2\int_0^t\sigma\,dq\right) = \exp\!\left(-\frac{2\sigma_{\max}t}{m+1}\right) = R_0$ となり、上の $\sigma_{\max}$ はここから決まる。

> 符号に注意：$e^{+i\omega t}$ では $s = 1 - i\sigma/k_0$ でなければならない。旧実装の「$\varepsilon$ に $+i\sigma/k_0$ を足す等方層」は、この規約では**利得**になる。

**等価な異方性媒質**：伸長は、次の対角テンソルを持つ媒質と等価である。

$$
\tilde\varepsilon = \varepsilon_r\Lambda,\quad \tilde\mu = \mu_r\Lambda,\qquad
\Lambda = \operatorname{diag}\!\left(\frac{s_y s_z}{s_x},\ \frac{s_x s_z}{s_y},\ \frac{s_x s_y}{s_z}\right).
$$

- 芯の中では $s_q = 1$ なので $\Lambda = I$。
- 辺や角の PML 領域では、関係する方向の伸長の積が自動的に入る。

### 1.4 弱形式

$\Gamma_{\mathrm{PEC}}$ で接線成分が0になる $H(\mathrm{curl})$ の関数空間を $V$ とする。$E\in V$ を、すべての $v\in V$ に対して $a(E, v) = \ell(v)$ を満たすように求める。

$$
a(E,v) = \int_\Omega \left(\Lambda^{-1}\mu_r^{-1}\,\nabla\times E\right)\cdot(\nabla\times v)\,dx
\;-\;k_0^2\int_\Omega \varepsilon_r\,(\Lambda E)\cdot v\,dx
\;+\;i k_0\int_{\Gamma_{\mathrm{SM}}} E_t\cdot v_t\,ds,
\qquad
\ell(v) = \int_\Omega f\cdot v\,dx .
$$

**導出**：恒等式 $\int_\Omega(\nabla\times A)\cdot v = \int_\Omega A\cdot(\nabla\times v) + \int_{\partial\Omega}(n\times A)\cdot v$ に $A = \mu^{-1}\nabla\times E$ を代入し、境界項に 1.2 の条件を入れる。

- PEC 面では $v_t = 0$ なので境界項は消える。
- Silver–Müller 面では $+ik_0\int E_t\cdot v_t$ が残る。
- PML の外面は PEC で打ち切る。

**離散化**：Nédélec 1次（Whitney 辺要素）の基底関数は、辺 $e = (a, b)$ について

$$
w_e = \lambda_a\nabla\lambda_b - \lambda_b\nabla\lambda_a \qquad (\lambda:\text{重心座標})
$$

であり、自由度は辺ごとの接線循環 $\int_e E\cdot t\,ds$ である。離散系 $A x = b$ の成分は

$$
A_{ij} = a(w_j, w_i),\qquad b_i = \ell(w_i).
$$

PEC 辺の自由度は消去する（FreeFEM の `on()`）。

### 1.5 係数行列の性質（反復法の選択に関係するもの）

**複素対称・非エルミート**：$a(\cdot,\cdot)$ は共役を含まない双一次形式なので $A^{\mathsf T} = A$ であるが、$A^{\mathsf H}\ne A$ である。

**不定値と勾配核**：分解 $A = K - k_0^2 M_\varepsilon + i k_0 B_\Gamma$ において、

- $K$（curl-curl 項）は半正定値で、$\nabla\times\nabla\phi = 0$ により勾配場全体が核になる。
- 離散勾配 $G$（辺×節点、各行に $\pm1$ が1組）について $KG = 0$ が成り立つ。したがって、勾配部分空間（次元は内部節点数）上では $A$ は $-k_0^2 M_\varepsilon$ として振る舞い、実部が負になる。
- 一方、発散のない部分空間では $K$ の固有値 $\lambda$ が $k_0^2$ をまたぐので、符号が不定になる。

**共振近傍**：閉空洞で $k_0^2$ が離散固有値 $\lambda_j$（$K u = \lambda M u$）に近いと、$A$ はほぼ特異になる。`resonance_check.py` はこの距離を $|k_j - k_0|/k_0$ で測っている。

**損失と PML**：損失や PML は係数を複素にし、固有値を実軸から離す。

> 実装：`freefem/maxwell_common.idp`（`epsC`：P0 関数の $\varepsilon_r$、`lamX..Z` / `ilamX..Z`：P1 関数の $\Lambda$ / $\Lambda^{-1}$、双一次形式 `aMaxwell`）、`run_freefem_batch.py`（`PML_R0`、`source_for`）

---

## 2. 複素対称系 $Ax=b$ の反復法

以下、前処理行列を $M\approx A$ とし、その適用 $z = M^{-1}r$ を `precon(r)` と書く。収束判定は、どちらの方法も真の残差で

$$
\frac{\|b - Ax_k\|}{\|b\|} \le \mathrm{rtol}\quad(\mathrm{rtol} = 10^{-8},\ x_0 = 0)
$$

とする。

### 2.1 COCG 法（Conjugate Orthogonal Conjugate Gradient）

**考え方**：CG 法の内積 $u^{\mathsf H}v$ を、双一次形式 $u^{\mathsf T}v$ に置き換えたものである（van der Vorst & Melissen, 1990）。

- $A^{\mathsf T}=A$ に対する Lanczos 過程から導かれ、短い3項漸化式で済む。反復あたりのメモリと演算量は $O(n)$ で、restart は不要。
- 残差は「共役直交」する：$r_i^{\mathsf T} M^{-1} r_j = 0\ (i\ne j)$。
- 何かを最小化する方法ではないので、残差ノルムは単調には減らず、振動する。

**前処理の条件**：$M$ も**複素対称**（$M^{\mathsf T} = M$）でなければならない。

- 満たすもの：$LDL^{\mathsf T}$ 型の IC(0)（加速係数付きを含む）、SSOR、$P^{\mathsf T}$ を使う Galerkin 型 AMG
- 満たさないもの：前進 Gauss–Seidel（本ベンチマークで測定した非対称性は $\approx 4\times10^{-3}$）
- $M$ は反復中に変わってはならない。内側を反復法で近似的に解く CSLP・HX 系は COCG には使えない。

**アルゴリズム**（`cocg_precon.idp`）

$$
\begin{aligned}
& r_0 = b - Ax_0,\quad z_0 = M^{-1}r_0,\quad p_0 = z_0,\quad \rho_0 = r_0^{\mathsf T}z_0\\
& \textbf{for } k = 0,1,2,\dots\\
&\qquad q_k = A p_k\\
&\qquad \pi_k = p_k^{\mathsf T} q_k \qquad\text{（破綻判定：}|\pi_k| < \epsilon\,\|p_k\|\,\|q_k\|\text{）}\\
&\qquad \alpha_k = \rho_k / \pi_k\\
&\qquad x_{k+1} = x_k + \alpha_k p_k,\qquad r_{k+1} = r_k - \alpha_k q_k\\
&\qquad \textbf{if } \|r_{k+1}\|/\|b\| \le \mathrm{rtol}\ \textbf{ stop}\\
&\qquad z_{k+1} = M^{-1} r_{k+1}\\
&\qquad \rho_{k+1} = r_{k+1}^{\mathsf T} z_{k+1} \qquad\text{（破綻判定：}|\rho_{k+1}| < \epsilon\,\|r_{k+1}\|\,\|z_{k+1}\|\text{）}\\
&\qquad \beta_k = \rho_{k+1}/\rho_k,\qquad p_{k+1} = z_{k+1} + \beta_k p_k
\end{aligned}
$$

**実装上の要点**（本プロジェクトで実際に問題になった点）

1. **破綻判定は正規化した相対判定にする**（$\epsilon = 10^{-14}$）。
   - 非零の複素ベクトルでも $u^{\mathsf T}u = 0$ はあり得る（真の破綻）。しかし、$|p^{\mathsf T}Ap|$ の絶対値が小さいだけでは破綻ではない。
   - 絶対値の閾値 $10^{-13}$ にすると、$\|b\|$ が小さい問題では健全な反復を止めてしまう（旧実装では46件中41件）。
2. **エルミート正定値の CG 向けの判定を流用しない**。
   - PETSc 3.22 の `KSPCG`（`-ksp_cg_type symmetric`）は、$\operatorname{Re}\pi_k$ の符号が前反復から変わると `DIVERGED_INDEFINITE_MAT` で止める。
   - 不定値の複素対称系では、この符号変化は普通に起きる。
3. **漸化式の残差 $r_k$ は、丸め誤差で真の残差からずれることがある**。終了時に $\|b - Ax\|$ を計算して確認する。
4. 反復あたりのコストは、行列ベクトル積1回、前処理1回、双一次形式2回（＋ノルム）。

### 2.2 右前処理・可変前処理対応の GMRES(m)（FGMRES）

**考え方**：Krylov 部分空間の中で真の残差ノルム $\|b - Ax\|$ を最小化する（Saad & Schultz, 1986）。

- 対称性は使わないので、内積はエルミート内積 $u^{\mathsf H}v$ を使う。
- 右前処理 $A M^{-1}y = b$、$x = M^{-1}y$ を使うと、監視している残差が真の残差になる。
- 前処理後のベクトル $z_j$ を保存しておけば、$M_j$ が反復ごとに変わってもよい（Flexible GMRES、Saad 1993）。CSLP・HX の内側を反復法で解く場合に必要である。

**アルゴリズム**（`gmres_precon.idp`、restart $m = 300$、修正 Gram–Schmidt、複素 Givens 回転）

$$
\begin{aligned}
& \textbf{repeat}\ (\text{restart})\\
&\quad r = b - Ax,\quad \beta = \|r\|,\quad v_1 = r/\beta,\quad g = (\beta, 0, \dots, 0)^{\mathsf T}\in\mathbb C^{m+1}\\
&\quad \textbf{for } j = 1,\dots,m\\
&\qquad z_j = M_j^{-1} v_j,\qquad w = A z_j\\
&\qquad \textbf{for } i = 1,\dots,j:\quad h_{ij} = v_i^{\mathsf H} w,\quad w \leftarrow w - h_{ij}v_i\\
&\qquad h_{j+1,j} = \|w\|,\qquad v_{j+1} = w / h_{j+1,j}\\
&\qquad \text{過去の回転を第 } j \text{ 列に適用：}\ \begin{pmatrix}h_{ij}\\ h_{i+1,j}\end{pmatrix} \leftarrow
\begin{pmatrix} c_i & s_i\\ -\bar s_i & c_i\end{pmatrix}\begin{pmatrix}h_{ij}\\ h_{i+1,j}\end{pmatrix}\quad (i<j)\\
&\qquad \text{新しい回転：}\ a = h_{jj},\ b = h_{j+1,j},\ D = \sqrt{|a|^2 + |b|^2},\quad
c_j = \frac{|a|}{D},\quad s_j = \frac{a}{|a|}\frac{\bar b}{D}\\
&\qquad h_{jj} \leftarrow c_j a + s_j b,\quad h_{j+1,j}\leftarrow 0,\quad
g_{j+1} = -\bar s_j g_j,\quad g_j \leftarrow c_j g_j\\
&\qquad \textbf{if } |g_{j+1}|/\|b\| \le \mathrm{rtol}\ \textbf{ break}\qquad(|g_{j+1}| = \|b - Ax_j\|)\\
&\quad H_{1:j,1:j}\,y = g_{1:j}\ \text{を後退代入で解く},\qquad x \leftarrow x + \sum_{k=1}^{j} y_k z_k
\end{aligned}
$$

回転行列は、$-\bar s_j a + c_j b = 0$ となるように選んでいる（$a = 0$ のときは $c_j = 0$、$s_j = 1$）。

**実装上の要点**

- 反復 $j$ での直交化は $j$ 回の内積と AXPY で、restart 周期内の合計は $O(m^2 n)$ になる。**内積は組み込みのベクトル演算で計算すること**（要素ごとのスクリプトループだと約40倍遅い）。
- 必要なメモリは $V, Z$ で $2(m+1)n$ 個の複素数。$m = 300$ では1自由度あたり約 9.6 KB で、本実装のピークメモリの大半を占める。
- restart は Krylov 部分空間（近似固有空間）を捨てるので、不定値系では停滞しやすい。$m = 30$ で停滞していたケースが、$m = 300$ で収束するようになった例がある。
- 固定の $M$ なら、PETSc の `-ksp_type gmres -ksp_pc_side right` と数学的に同じである。

### 2.3 COCG と GMRES(m) の比較

| | COCG | GMRES(m) |
|---|---|---|
| 使う性質 | $A^{\mathsf T}=A$、$M^{\mathsf T}=M$ | なし（一般の正則行列） |
| 最適性 | なし（残差は振動する） | 残差ノルムが restart 周期内で単調減少 |
| 反復あたりのコスト・メモリ | $O(n)$ | $O(jn)$ / $O((m+1)n)$ |
| 可変前処理 | 不可 | 可（FGMRES） |
| 失敗の仕方 | 破綻（$\pi_k$ または $\rho_k$ がほぼ0） | restart による停滞 |

### 2.4 可変前処理と COCG（flexible COCG は使わない理由）

**SPD 系の flexible PCG**：前処理 $M_k$ が反復ごとに変わる場合（内側を反復法で近似的に解く場合）、SPD 系の CG では β を Polak–Ribière 型にした flexible PCG が知られている（Golub & Ye 1999、Notay 2000）。

$$
\beta_k^{\mathrm{PR}} = \frac{z_{k+1}^{\mathsf H}(r_{k+1} - r_k)}{z_k^{\mathsf H} r_k},\qquad z_k = M_k^{-1}r_k .
$$

Notay の FCG(m) では、さらに新しい探索方向を直前の $m$ 本に対して明示的に $A$-共役化する。

**COCG への形式的な移植**：内積を双一次形式に置き換えると、次の形になる。

$$
\beta_k = \frac{z_{k+1}^{\mathsf T}(r_{k+1} - r_k)}{z_k^{\mathsf T} r_k},\qquad
p_{k+1} = z_{k+1} - \sum_{j=k-m+1}^{k}\frac{p_j^{\mathsf T}Az_{k+1}}{p_j^{\mathsf T}Ap_j}\,p_j \ \ (\text{FCG}(m)\text{ 型}).
$$

- 前処理が固定なら、共役直交性 $r_{k+1}^{\mathsf T}M^{-1}r_k = 0$ から $z_{k+1}^{\mathsf T}r_k = 0$ となる。したがって、この β は 2.1節の COCG の β（Fletcher–Reeves 型）と一致し、前処理が変わるときだけ補正が効く。

**ただし、理論的な保証は引き継がれない**

- SPD 系の flexible CG が前処理の変動に強いのは、$\|e\|_A$ を探索方向に沿って局所的に最小化する性質（局所最適性：最急降下法より悪くならない）があるためである。
- 複素対称・不定値の系では $u^{\mathsf T}Au$ はノルムではないので、最小化の性質も局所最適性もない。COCG 固有の破綻もそのまま残る。
- 「flexible COCG」を主題とした確立した文献は見つけられなかった（2026-09 時点の調査）。

**本ベンチマークの方針**：可変前処理（内側を GMRES で解く CSLP・HX・CSLP+HX）は FGMRES だけで使う。COCG と組み合わせるときは、内側を**固定の線形演算子**にする（3.5節）。

---

## 3. 前処理

### 3.1 AMG（平滑化集約型、PETSc GAMG）

**セットアップ**（レベル $\ell$ ごと、$A_0 = A$）

1. **強結合グラフ**：$|a_{ij}| \ge \theta\sqrt{|a_{ii}a_{jj}|}$ を満たす辺を残す。
2. **集約**：最大独立集合で節点をまとめ、集約 $\mathcal A_1,\dots,\mathcal A_{n_c}$ を作る。
3. **仮の補間 $\hat P$**：近零空間ベクトル（既定では定数）を各集約に制限して並べ、直交化する。
4. **補間の平滑化**：

$$
P = \left(I - \omega D^{-1}A_\ell\right)\hat P,\qquad \omega = \frac{4}{3\,\lambda_{\max}(D^{-1}A_\ell)}.
$$

5. **粗い演算子**：$A_{\ell+1} = P^{\mathsf T} A_\ell P$。$P^{\mathsf T}$（共役を取らない転置）を使うので、複素対称性が保たれる。
6. **スムーザ**：Chebyshev（Jacobi スケーリング付き）。$D^{-1}A$ のスペクトル区間を固有値推定で決める。
7. **最粗レベル**：直接法。

**適用**：$M^{-1}r$ は V-cycle 1回である。前後のスムーザが対称な多項式で、制限に $P^{\mathsf T}$ を使うので $M^{\mathsf T}=M$ となり、COCG にも使える。

$$
\begin{aligned}
&\text{前平滑化：}\ x \leftarrow x + p(D^{-1}A_\ell)\,D^{-1}(r - A_\ell x)\\
&\text{粗格子補正：}\ x \leftarrow x + P\,\mathrm{Vcycle}_{\ell+1}\!\left(P^{\mathsf T}(r - A_\ell x)\right)\\
&\text{後平滑化：}\ \text{前平滑化と同じ}
\end{aligned}
$$

**この問題での限界**

- 辺要素の curl-curl 系の近零空間は勾配場 $\operatorname{range}(G)$ で、定数ベクトルでは表せない。
- $A$ は不定値で、Chebyshev スムーザの前提（スペクトルが右半平面にある）を満たさない。
- このため、単独では共振近傍・PML の問題で効きにくい。

> 実装：`-pc_type gamg`（PETSc の既定設定）。GMRES では PC として、COCG では `-ksp_type preonly` で1回適用。

### 3.2 CSLP（複素シフト Laplace 型前処理）

$A = K - k_0^2 M_\varepsilon + ik_0B_\Gamma$ の質量項だけに複素シフトを掛けた行列を前処理に使う（Erlangga, Vuik & Oosterlee, 2004）。

$$
M_\beta = K - (\beta_1 - i\beta_2)\,k_0^2 M_\varepsilon + ik_0B_\Gamma,\qquad (\beta_1,\beta_2) = (1,\ 0.5).
$$

PML・損失・PEC の扱いは $A$ とまったく同じにする（`aMaxwellShift`）。

**スペクトル**：$K, M_\varepsilon$ が実対称で、$B_\Gamma = 0$ の単純な場合を考える。$K u = \lambda M_\varepsilon u$（$\lambda \ge 0$）の固有ベクトルに対し、$M_\beta^{-1}A$ の固有値は、$a = \lambda - k_0^2$ として

$$
\mu = \frac{\lambda - k_0^2}{\lambda - k_0^2 + i\beta_2k_0^2} = \frac{a}{a + i\beta_2k_0^2},
\qquad
\left|\mu - \tfrac12\right| = \frac{1}{2}\left|\frac{a - i\beta_2k_0^2}{a + i\beta_2k_0^2}\right| = \frac12
$$

となる（$\beta_1 = 1$ の場合）。つまり、スペクトルは中心 $1/2$・半径 $1/2$ の円上に乗る（van Gijzen, Erlangga & Vuik, 2007）。

- 原点に近づくのは $a\to0$、すなわち**共振近傍**の場合だけである。共振近傍で難しくなるのはこのためである。
- 勾配場（$\lambda = 0$）は $\mu = 1/(1 - i\beta_2)$ となり、原点から離れている。

**適用**：$z = M_\beta^{-1}r$ は、内側の GMRES＋GAMG で近似的に解く（`-ksp_type gmres -pc_type gamg -ksp_rtol 1e-2 -ksp_max_it 20`）。

- 近似の度合いが反復ごとに変わるので、外側は FGMRES（2.2節）にする。COCG は使えない。
- $\beta_2$ を大きくすると $M_\beta$ は解きやすくなるが、前処理としての近さは下がる。

### 3.3 HX（Hiptmair–Xu 型補助空間前処理）

**考え方**：$H(\mathrm{curl})$ の関数を、次の3つに分解する（Hiptmair & Xu, 2007）。

$$
H(\mathrm{curl}) = \underbrace{\nabla H^1}_{\text{勾配}} + \underbrace{\Pi\,(H^1)^3}_{\text{滑らかなベクトル場}} + \text{高周波成分}.
$$

それぞれに対応する補正を足し合わせた加法型の前処理にする。

$$
B_{\mathrm{HX}} = \underbrace{\omega D_A^{-1}}_{\text{スムーザ}} + \underbrace{G\,(G^{\mathsf T}AG)^{-1}G^{\mathsf T}}_{\text{勾配補正}} + \underbrace{\Pi\,(\Pi^{\mathsf T}A\Pi)^{-1}\Pi^{\mathsf T}}_{\text{ベクトル補正}}.
$$

**各演算子の定義**

- **離散勾配** $G\in\{0,\pm1\}^{N_e\times N_v}$：辺 $e = (a\to b)$ について $G_{e,b} = +1$、$G_{e,a} = -1$。Whitney 要素は $\nabla(P1)$ を厳密に表せるので $\nabla\phi_h = \sum_e (G\phi)_e w_e$。
- **勾配空間の補助問題**：$\nabla\times\nabla\phi = 0$ なので curl-curl 項が消え、次の形になる。

$$
(G^{\mathsf T}AG)_{ab} = -k_0^2\int_\Omega \varepsilon_r\,(\Lambda\nabla\phi_b)\cdot\nabla\phi_a\,dx + ik_0\int_{\Gamma_{\mathrm{SM}}}\nabla_\Gamma\phi_b\cdot\nabla_\Gamma\phi_a\,ds .
$$

  スカラー P1 の（符号が負の）Laplace 型問題で、PEC 節点は Dirichlet 条件で消去する。本実装ではこの形式を直接組み立てる（`hxVMgrad`）。
- **ベクトル補間** $\Pi: (P1)^3\to$ 辺要素：辺 $e = (a\to b)$ について

$$
(\Pi u)_e = \int_e u\cdot t\,ds = (x_b - x_a)\cdot\frac{u(x_a) + u(x_b)}{2}\qquad(\text{P1 では台形則で厳密}).
$$

**本実装の形**（2項版）

$$
B_{\mathrm{HX}} = \omega D_A^{-1} + G\,\widetilde{(G^{\mathsf T}AG)}^{-1}G^{\mathsf T},\qquad \omega = 1 .
$$

- $\widetilde{(\cdot)}^{-1}$ は内側の GMRES＋GAMG（rtol $10^{-2}$、最大20反復）による近似逆である。
- 第3項（$\Pi$ と $\Pi^{\mathsf T}A\Pi$）は実装済みだが、GMRES が完全に停滞する未解決の不具合があるため無効にしている（`IFMACRO(HXVECTERM)` で有効化できる）。
- HX 理論は正定値の $H(\mathrm{curl})$ 問題（$\nabla\times\nabla\times + \alpha I$、$\alpha>0$）に対するものである。不定値の問題では、勾配空間の補正は「$-k_0^2$ の負の固有値を持つ部分空間」を直接解く役割になる。

**適用**：GMRES（FGMRES）の前処理として毎反復1回適用する。

### 3.4 CSLP＋HX（加法結合）

CSLP を HX のスムーザ項の代わりに置き、勾配補正と足し合わせる。

$$
B = \widetilde{M_\beta}^{-1} + G\,\widetilde{(G^{\mathsf T}AG)}^{-1}G^{\mathsf T}.
$$

- CSLP は符号の不定性（$-k_0^2$ 項）に対処し、勾配補正は curl の核（$KG = 0$）に対処する。両者は別々の難しさに対応する。
- 2つの内側ソルブ（$M_\beta$、$G^{\mathsf T}AG$）は、どちらも GMRES＋GAMG（rtol $10^{-2}$、最大20反復）である。
- 外側は FGMRES。3項版（$\Pi$ を含むもの）は HX と同じ理由で無効にしている。

### 3.5 内側を固定の線形演算子にした CSLP / CSLP+HX（COCG 対応版）

**考え方**：3.2〜3.4節の前処理は、補助問題の逆（$M_\beta^{-1}$、$(G^{\mathsf T}AG)^{-1}$）を内側の GMRES で近似的に解くので、反復ごとに変わる非線形な作用になる。これを固定の線形演算子 $\mathcal B\approx M_\beta^{-1}$ に置き換えれば、前処理全体が固定の線形演算子になり、通常の COCG（2.1節）と、非 flexible の GMRES が使える。

| プリセット | 前処理 $B$ | 内側 |
|---|---|---|
| `cslp_mg` | $B = \mathcal V(M_\beta)$ | $M_\beta$ に GAMG の V-cycle を1回 |
| `cslp_hx_mg` | $B = \mathcal V(M_\beta) + G\,\mathcal V(G^{\mathsf T}AG)\,G^{\mathsf T}$ | 両方の補助問題に V-cycle を1回ずつ |

ここで $\mathcal V(\cdot)$ は、PETSc の `-ksp_type preonly -pc_type gamg` による V-cycle 1回の作用を表す。これは、CSLP の文献で標準的な「シフト演算子にマルチグリッドを1サイクル」の使い方である。

**複素対称性**（COCG の前提 $B^{\mathsf T}=B$）

1. **V-cycle**：スムーザが $D^{-1}C$ の多項式 $s(D^{-1}C)D^{-1}$（Chebyshev/Jacobi）で前後に同じもの、制限が $P^{\mathsf T}$（共役なしの転置）、最粗レベルが対称な直接法なら、各レベルの $C$ が対称である限り $\mathcal V(C)^{\mathsf T} = \mathcal V(C)$ となる。粗い演算子 $P^{\mathsf T}CP$ も対称なので、再帰的に成り立つ。
2. **補助問題**：$M_\beta^{\mathsf T} = M_\beta$ であり（$K, M_\varepsilon, B_\Gamma$ はすべて対称）、$G^{\mathsf T}AG$ も対称。
3. **和と合成**：$\left(G\,\mathcal V\,G^{\mathsf T}\right)^{\mathsf T} = G\,\mathcal V^{\mathsf T}G^{\mathsf T} = G\,\mathcal V\,G^{\mathsf T}$ であり、対称な演算子の和は対称。
4. **固定回数の定常反復も対称**：対称な $B_0$ による Richardson 法を $x_0 = 0$ から固定回数 $\nu$ 回行う作用は、多項式 $\sum_{k=0}^{\nu-1}(I - B_0C)^kB_0$ になる。$(B_0C)^kB_0 = B_0(CB_0)^k$ の転置は $(B_0C)^kB_0$ なので、この作用も対称である。一方、内側を GMRES にすると右辺に依存する非線形な作用になり、対称でも固定でもない。

**数値確認**（`freefem/symmetry_check.edp`）：ランダムな複素ベクトル $x, y$ で $|x^{\mathsf T}By - y^{\mathsf T}Bx|/(\|x\|\|By\|)$ を測ると、`cslp_mg`・`cslp_hx_mg` ともに $10^{-17}$〜$10^{-16}$ だった（case2F plex7、case2A standard、case1A thin_pml）。同じ $y$ に2回適用した結果は完全に一致した（固定の演算子であることの確認）。

**トレードオフ**：V-cycle 1回は、内側 GMRES（最大20反復）より $M_\beta^{-1}$ の近似が粗い。その代わり、前処理1回あたりのコストが小さく、短い漸化式の COCG と restart のない外側反復が使える。

**試行結果**（2026-09-28、代表10セット、600秒、`results/benchmark_mg_trial/`）

| セット | CSLP（内側GMRES）+GMRES | CSLP-MG+GMRES | CSLP-MG+COCG | CSLP+HX-MG+GMRES | CSLP+HX-MG+COCG | 加速IC(0)+COCG |
|---|---|---|---|---|---|---|
| 2A standard | 4e-8 | 4e-4 | 破綻 | 9e-4 | 破綻 | ✓84 s |
| 2A off_resonance | ✓109 s | ✓258 s | 破綻 | ✓92 s | 破綻 | ✓25 s |
| 1A standard（PML） | 3e-1 | 4e-1 | 6e-1 | 4e-1 | 破綻 | ✓195 s |
| 2B medium_iris | ✓157 s | ✓240 s | 破綻 | ✓403 s | 破綻 | ✓19 s |
| 3E medium_loss | 8e-4 | ✓552 s | 破綻 | ✓503 s | 破綻 | ✓72 s |

（数値は600秒時点で到達した相対残差、✓は収束までの時間。1B・2D・3A・3C・3F も同じ傾向）

- **COCG との組み合わせは10セットすべてで失敗**した。前処理は複素対称かつ固定であることを確認済みなので、実装の問題ではない。
  - CSLP-MG+COCG は1300〜5600反復で破綻し、残差は最大 $10^{11}$ 倍に発散した。
  - CSLP+HX-MG+COCG は30反復以内に破綻した。
  - 解釈：CSLP で前処理した演算子のスペクトルは原点を通る円上に乗る（3.2節）。COCG は残差を最小化しない Galerkin 型（FOM 類似）の方法なので、原点近くに固有値があると反復解が不安定になる。CSLP の文献で外側に GMRES や Bi-CGSTAB が使われるのと整合する。
- **GMRES との組み合わせ**では、固定版（V-cycle 1回）は内側 GMRES 版と同程度か弱く、改善は一部のセットに限られた。
- **結論**：CSLP 系は FGMRES で使い、COCG は加速IC(0)・SSOR（AMG）と組み合わせる。固定版のプリセット（`cslp_mg`、`cslp_hx_mg`）は残すが、本評価の組み合わせには加えない。

---

## 付録 A　実装との対応と既定値

| 項目 | 値・式 | ファイル |
|---|---|---|
| 材料 $\varepsilon_r$ | 領域ごとの P0 関数 `epsC` $=\varepsilon'(1-i\tan\delta)$ | `maxwell_common.idp` |
| UPML | $s_q = 1-i\sigma_q/k_0$、$m=2$、$R_0 = 10^{-4}$、$\Lambda$・$\Lambda^{-1}$ は P1 関数 | `maxwell_common.idp`、`run_freefem_batch.py` |
| 双一次形式 | `aMaxwell`（$A$）、`aMaxwellShift`（$M_\beta$） | `maxwell_common.idp` |
| COCG | $\epsilon = 10^{-14}$ の正規化破綻判定、終了時に真の残差を出力 | `cocg_precon.idp` |
| GMRES(m) | $m = 300$、MGS、複素 Givens、右前処理・可変前処理 | `gmres_precon.idp` |
| PETSc PC + COCG | PC を `-ksp_type preonly` で1回適用 | `maxwell_edge03d_solver.edp`（`pc_cocg`） |
| CSLP | $(\beta_1,\beta_2) = (1, 0.5)$、内側 GMRES+GAMG（rtol $10^{-2}$、最大20反復） | `maxwell_edge03d_solver.edp` |
| HX / CSLP+HX | 2項版、$\omega = 1$、$G$ は `MatrixEdgeP1` | `hx_precon.idp`、`cslp_hx_precon.idp` |
| CSLP / CSLP+HX（固定線形版） | 内側は GAMG の V-cycle 1回（`-ksp_type preonly -pc_type gamg`）、外側は GMRES または COCG | プリセット `cslp_mg` / `cslp_hx_mg`、ソルバーの `runOuter` |
| 対称性の確認 | $\lvert x^{\mathsf T}By - y^{\mathsf T}Bx\rvert/(\lVert x\rVert\lVert By\rVert)$ | `symmetry_check.edp` |
| 収束判定 | $\|b-Ax\|/\|b\| \le 10^{-8}$、1ソルブ600秒（セットアップ込み） | `run_benchmark.py` |

## 付録 B　参考文献

- J.-C. Nédélec, "Mixed finite elements in R³," *Numer. Math.* 35 (1980) 315–341.
- P. Monk, *Finite Element Methods for Maxwell's Equations*, Oxford Univ. Press, 2003.
- Z. S. Sacks, D. M. Kingsland, R. Lee, J.-F. Lee, "A perfectly matched anisotropic absorber for use as an absorbing boundary condition," *IEEE Trans. Antennas Propag.* 43 (1995) 1460–1463.
- S. D. Gedney, "An anisotropic perfectly matched layer-absorbing medium for the truncation of FDTD lattices," *IEEE Trans. Antennas Propag.* 44 (1996) 1630–1639.
- H. A. van der Vorst, J. B. M. Melissen, "A Petrov–Galerkin type method for solving Ax=b, where A is symmetric complex," *IEEE Trans. Magn.* 26 (1990) 706–708.
- Y. Saad, M. H. Schultz, "GMRES: A generalized minimal residual algorithm for solving nonsymmetric linear systems," *SIAM J. Sci. Stat. Comput.* 7 (1986) 856–869.
- Y. Saad, "A flexible inner-outer preconditioned GMRES algorithm," *SIAM J. Sci. Comput.* 14 (1993) 461–469.
- G. H. Golub, Q. Ye, "Inexact preconditioned conjugate gradient method with inner-outer iteration," *SIAM J. Sci. Comput.* 21 (1999) 1305–1320.
- Y. Notay, "Flexible conjugate gradients," *SIAM J. Sci. Comput.* 22 (2000) 1444–1460.
- V. Simoncini, D. B. Szyld, "Flexible inner-outer Krylov subspace methods," *SIAM J. Numer. Anal.* 40 (2003) 2219–2239.
- Y. A. Erlangga, C. Vuik, C. W. Oosterlee, "On a class of preconditioners for solving the Helmholtz equation," *Appl. Numer. Math.* 50 (2004) 409–425.
- M. B. van Gijzen, Y. A. Erlangga, C. Vuik, "Spectral analysis of the discrete Helmholtz operator preconditioned with a shifted Laplacian," *SIAM J. Sci. Comput.* 29 (2007) 1942–1958.
- R. Hiptmair, J. Xu, "Nodal auxiliary space preconditioning in H(curl) and H(div) spaces," *SIAM J. Numer. Anal.* 45 (2007) 2483–2509.
- T. V. Kolev, P. S. Vassilevski, "Parallel auxiliary space AMG for H(curl) problems," *J. Comput. Math.* 27 (2009) 604–623.
- P. Vaněk, J. Mandel, M. Brezina, "Algebraic multigrid by smoothed aggregation for second and fourth order elliptic problems," *Computing* 56 (1996) 179–196.
- K. Fujiwara, T. Nakata, H. Fusayasu, "Acceleration of convergence characteristic of the ICCG method," *IEEE Trans. Magn.* 29(2) (1993).
- S. Balay et al., *PETSc/TAO Users Manual*, ANL-21/39 Rev. 3.22, 2024.
