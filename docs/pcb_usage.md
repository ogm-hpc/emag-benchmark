# PCBベンチマークスイートの使い方

プリント基板向け高周波電磁界解析の線形ソルバーベンチマーク（設定書 [pcb_problem_benchmark_settings.md](../pcb_problem_benchmark_settings.md)）を、メッシュ生成から集計まで流す手順。問題の定義と結果の解釈は設定書、作業の経緯は pcb_handoff.md にある。

## 1. スイートの構成

設定書15章の4区分。各パラメータセットの区分は `freefem/pcb/pcb_case_parameters.json` の `"suite"` にある。

| 区分 | ケース | 内容 | 合否・記録（設定書17章） |
|---|---|---|---|
| Core | 9 | P01・P03・P05の各3ケース（最小リリースセット） | 少なくとも1つの組合せが収束 |
| Extended | 52 | P01〜P08の系列（周波数、電気長、損失、ビア形状、プレーン間隔、材料コントラスト、スロット、配線本数など） | 収束した組合せの数 |
| Challenge | 5 | どの組合せも600秒で収束しないケース（v1.0 より前は P02-b_h0.05 を含めて6） | 到達残差 |
| Multi-RHS | 3 | P07-1（4ポート）、P08-N4_s1（8ポート）、P08-N8_s1（16ポート）の全S行列 | 再利用手法の独立に対する比（1/2以下で合格） |

**既存のセット（case1A〜3F、46セット）も同じランナーで流せる**（docs/paper_plan.md A2、2026-10-05）。区分は `gmsh_templates/case_parameters.json` の `"suite"`: Core 4（case1A:standard、case2A:standard、case2A:off_resonance、case3A:high_contrast）、Extended 42。`run --suite core` は PCB の Core 9 と既存の Core 4 を流す。既存のセットは `--sets case2A:standard` の形で指定し、`--problems case2A` でも選べる（`--roles` だけでは選ばれない）。長さは \(\lambda_0\) で正規化（PCB は mm）、励振はガウス体積源（PCB は集中ポート）で、換算しない（結果JSONの `pcb.length_unit`・`pcb.excitation`、サマリーの列 `lengthUnit`・`excitation`）。PCB の標準（PETSc の GMRES の MGS、HX・CSLP+HX のマスク、hx のベクトル項＋対称GS、\(K_{\max}\)）をそのまま使う。メッシュは `generated_meshes/mesh/`（`python3 gmsh_templates/generate_all_meshes.py -o generated_meshes`、`--existing-mesh-dir` で変更可）。`--port`・`--freq`・`--mrhs`・`--excitation E1` は使えない。結果名は `run_benchmark.py` と同じ `<case>_<set>__<preset>_<krylov>`、サマリーでは `case2A:standard` の形で PCB の結果と1つの CSV にまとまる。

**P02-b_h0.05 は v1.0 のスイートから外した**（`"suite": "excluded"`、もとは Challenge。`excludedReason`: M3 Pro のメモリ予算を超える）。`--sets P02-b_h0.05` では流せる。

各ケースは、標準11組合せ（gs/gmres、ssor/gmres、ssor/cocg、amg_gamg/gmres、amg_gamg/cocg、accel_ic/gmres、accel_ic/cocg、cslp/gmres、hx/gmres、cslp_hx/gmres、npatch_asm/cocg）で解く。npatch_asm/cocg（節点パッチ前処理、2026-10-05 追加）はPCB専用のプリセットで、既存の `run_benchmark.py` の10組合せには入っていない（`run_pcb_benchmark.PCB_DEFAULT_COMBOS`）。条件は、1ジョブ1プロセス・1スレッド、右前処理の真の相対残差 \(10^{-8}\)。止める規則は、v1.0 では組合せごとの反復回数の上限 \(K_{\max}\)（2026-10-05 から `run` の既定。4.3節）、v1.0 より前（`docs/pcb_results/` の記録、`chains/suite.sh`）は600秒（セットアップを含む）の時間の予算。参照は、MUMPS（`mumps/direct`）で解いたSパラメータ。

## 2. 必要な環境

| 項目 | 基準の計算機（WSL） | 副の計算機（Mac） |
|---|---|---|
| OS・CPU・メモリ | Windows 11 + WSL（Ubuntu）、Intel Core Ultra 7 255H（16コア）、31 GB | Apple M1（16 GB）、Apple M3 Pro（18 GB） |
| FreeFEM | 4.15（`/usr/local/bin/FreeFem++-mpi`）、複素数版PETSc 3.22.2、MUMPSあり、HYPREなし | 4.15（`/Applications/FreeFem++.app`）、PETSc 3.24.1（M1）・3.23.1（M3 Pro） |
| Gmsh | Pythonのvenv `~/.venvs/pcbmesh` に gmsh 4.15.2（`pip install gmsh==4.15.2`） | 同じ（Homebrewの Python 3.12 で作る） |
| Python | システムの Python 3（ランナー・集計） | 同じ |

- **v1.0 の記録は M3 Pro の結果だけで、`docs/results_v1/mac_m3pro/` に置く**（作業A4、2026-10-05。`--dest docs/results_v1/mac_m3pro`。他の計算機・他の版の結果は拒否される）。以下は v1.0 より前の記録（整備の経緯として残す）の規則: 記録（`docs/pcb_results/`）はWSLの結果だけ。Macの結果は `docs/pcb_results/<host>/` に置き、WSLとは比べない。OS・CPUが違うと、同じGmshでもメッシュがわずかに変わり（辺の数で約1%以内）、時間も比べられないため。
- FreeFEMを流す前に `export HWLOC_COMPONENTS=-gl` を付ける（WSLgのXサーバーが応答しないと、Open MPIの起動が止まる）。チェーンのスクリプトは自分で付ける。

## 3. まとめて流す

```bash
cd <リポジトリ> && git pull
LIST=1 bash freefem/pcb/chains/suite.sh mumps core extended challenge single multirhs   # ジョブの確認（計算しない）
bash freefem/pcb/chains/suite.sh                                                        # 全段階
bash freefem/pcb/chains/suite.sh core summary                                           # 一部の段階だけ
```

`freefem/pcb/chains/suite.sh` の段階は次のとおり（順に流す）。どの段階も、止まったら同じコマンドで再開できる（結果のあるジョブは飛ばす）。

| 段階 | 内容 | WSLでの目安 |
|---|---|---|
| `mesh` | Core・Extended・Challengeの67セットのメッシュ生成と検査（`--suite core,extended,challenge`） | 十数分（L-6の21セットは、メッシュ生成だけで約1分） |
| `regress` | 回帰確認。全件PASSでなければ止まる | 約10分 |
| `mumps` | MUMPS参照。P03は2ポートを1ジョブで（`--mrhs shared`）。P02-b_h0.05（16 GB）は単独 | 約30分（直列の合計は約1.7時間） |
| `core` | Coreの標準11組合せ（5並列） | 約2時間 |
| `extended` | Extendedの標準11組合せ（5並列。P05-lc0.625は3並列） | 約12時間 |
| `challenge` | Challengeの標準11組合せ（5並列。P02-b_h0.05は2並列） | 約2時間 |
| `single` | 下の26セットのcslp_hx/gmresを単独で（1ワーカー） | 約3.5時間 |
| `multirhs` | Multi-RHSの3件。MUMPSのshared、cslp_hxの独立（`--port all --tag u1`）・shared・block・gcro。すべて1ワーカー | 約12時間 |
| `summary` | 集計（`DEST`、既定 `docs/pcb_results`） | 1分 |

- 合計で約32時間。AC電源につなぎ、スリープしない設定で流す（バッテリー駆動ではCPUのクロックが下がり、同じ計算が約2倍遅くなる。スリープすると実行中のジョブが記録されずに止まる）。
- 単独実行のセット（`SINGLE`）: P03（13件）、P04-1〜4、P06-L10・L30・L30_s2、P07-1・P07-4、P08-N8_s1、P01-2_t・P01-a_f20・P01-b_L131.4。辺が20万を超えるこれらのケースでは、5並列ではcslp_hxの1反復が約1.5倍遅くなり、600秒に届かない。そのため、cslp_hxは他のジョブを重ねずに流す（設定書15.4節）。標準の段階では、これらのセットのcslp_hxを除いた9組合せを流す。
- `suite.sh` は v1.0 より前の規則（600秒・5並列）のチェーンで、`--k-max none` を付けて流す（2026-10-05 から。`KMAX=standard` で上限の規則を試せるが、v1.0 の記録（単独実行、docs/paper_plan.md B3）はこのチェーンでは取らない）。
- Macで流すとき: `WORKERS=<性能コアの数> DEST=docs/pcb_results/<host> bash freefem/pcb/chains/suite.sh core summary` のようにする。ランナーは、WSLの記録から各ジョブのメモリを見積もり、物理メモリの75%を超えるジョブを外す（`--mem-budget`）。M1・M3 Proでは P02-b_h0.05 の5ジョブが外れる。

## 4. 手順の詳細

### 4.1 メッシュ

```bash
~/.venvs/pcbmesh/bin/python gmsh_templates/pcb/generate_pcb_meshes.py --suite core          # 区分で選ぶ
~/.venvs/pcbmesh/bin/python gmsh_templates/pcb/generate_pcb_meshes.py --sets P01-1,P05-2     # セットで選ぶ
python3 gmsh_templates/pcb/generate_pcb_meshes.py --list --suite extended                    # 一覧（gmsh不要）
```

- 出力: `generated_meshes/pcb/mesh/<セット>.msh`（MSH 2.2）と `generated_meshes/pcb/mesh_report.json`（物理グループの検査結果、辺の数、最小二面角、二面角5°・10°未満の四面体数、Gmshの版）。検査に失敗すると `[FAIL]` を出し、終了コード1を返す。
- 全94セットのメッシュは約0.8 GB。`generated_meshes/` はgitで管理しない。

### 4.2 回帰確認

```bash
python3 freefem/pcb/run_pcb_benchmark.py regress
```

既存ベンチマークの2ケース（case1A、case2A）を、既存のソルバーとPCB用のソルバーで同じ条件で解き（8組合せ×2、50反復）、残差履歴と解が一致することを確かめる（設定書7.5節）。旧ソルバーにない組合せ（npatch_asm/cocg、case1A・case2A）は、保存した参照（`freefem/pcb/regress_reference.json`、残差履歴と解のノルム、相対許容差1e-8）と比べる。参照は機種ごと（キーの末尾 `@<host>`。メッシュが機種で変わるため）で、メッシュの MD5 も持つ。新しい機種では、まず `regress --update-reference` で参照を取る。取り直すのは、ほかに前処理を意図して変えたときとメッシュを作り直したときだけ。節点パッチのトイ試験（`test_npatch_toy.edp`: パッチごとの直接適用との差、複素対称性、COCGの収束）も流す。`freefem/pcb/` を変えたら必ず流し、全件（11件）PASSを確かめる。既存ケースのメッシュ（`generated_meshes/`）が要る。

### 4.3 ジョブの実行（`run`）

```bash
R="python3 freefem/pcb/run_pcb_benchmark.py run"
$R --suite core --list                              # ジョブの一覧（FreeFEMを使わない）
$R --suite core --combos mumps/direct --workers 5   # MUMPS参照
$R --suite core --workers 1 --out results/pcb_v1    # 標準11組合せ、K_max の規則（v1.0 は単独実行）
$R --suite core --workers 5 --k-max none            # v1.0 より前の規則（600秒の予算、上限なし）
$R --sets P03-1 --combos cslp_hx/gmres --workers 1  # 単独実行
$R --show-config P01-1:hx/gmres                     # 1ジョブの生成設定を表示
```

| オプション | 意味 |
|---|---|
| `--suite core,extended,challenge,multi_rhs` | 区分で選ぶ（`--sets` が優先、`--roles` より優先） |
| `--sets A,B` | パラメータセットで選ぶ |
| `--release-dir DIR` | 公開データ（Zenodo・J-Stage Data）を展開したフォルダのメッシュ `DIR/<セット>/mesh.msh` を使う（既存のセットは `case2A_standard` のように `:` を `_` に）。`--mesh-dir`・`--existing-mesh-dir` より優先。メッシュのパスが変わるだけで、解く条件は変わらない（2026-10-16、C6）。`ritz` にもある |
| `--combos P/K,...` | 組合せ（既定は標準11組合せ）。参照は `mumps/direct`。節点パッチ前処理の変種は `npatch_sms`（`gmres`・`cocg`）、`npatch_ras`（`gmres` のみ）、`npatch_asm/gmres`（引継ぎメモ 作業P） |
| `--workers N` | 並列ジョブ数（WSLの標準は5） |
| `--k-max standard\|none\|N` | 反復回数の上限（docs/paper_plan.md 4.1節）。`standard`（既定）: 組合せごと（`K_MAX_STANDARD`: gs・ssor・amg_gamg・accel_ic の GMRES と hx 10,000、COCG 系と npatch_asm/cocg 50,000、cslp 3,000、cslp_hx 1,000。ほかの組合せは GMRES 10,000・COCG 50,000）。`none`: 上限なし（時間の予算で止める、v1.0 より前の規則。`--mrhs` では `none` のみ）。数字: 全組合せに同じ上限（`--tag` が必要） |
| `--budget S` | 1ソルブの時間の上限（セットアップを含む）。既定は `--k-max standard` で12時間（安全用。起きたら原因を調べる）、`--k-max none` で600秒。`--mrhs` では全右辺の合計 |
| `--port all` | ポートごとに1ジョブ（結果名 `<セット>@<ポート>`） |
| `--mrhs shared\|block\|gcro` | 全ポートを1プロセスで解く（結果名 `<セット>@mrhs-<方法>`、全S行列） |
| `--tag T` | 変種の名前（結果名 `<セット>@T`）。restart長・加速係数・PETScのオプションを変えるときは必須 |
| `--freq f1,f2,...` | セットのメッシュのまま周波数だけを変える（結果名 `<セット>@f<GHz>`） |
| `--save-solutions`、`--ref-solutions DIR` | 解の保存と、MUMPSの解に対するL2・curl誤差の評価（標準でオフ、設定書9.2節） |
| `--force` | 結果があっても流し直す |

- 結果: `results/pcb_benchmark/runs/<問題>_<セット>[@変種]__<preset>_<krylov>.json`（状態、反復数、残差履歴、時間、ピークメモリ、Sパラメータ）、ログは `results/pcb_benchmark/logs/`。`results/` はgitで管理しない（全結果で約0.3 GB）。
- 実行環境（OS、CPU、メモリ、FreeFEM・PETScの版、gitのコミット、コマンドライン）は、`run` ごとに `results/pcb_benchmark/meta.json` に書かれ、`meta_history.jsonl` に追記される。
- 停止の理由は結果JSONの `status`: `converged`、`max_it`（上限 \(K_{\max}\) に達した）、`breakdown`、`timeout`（時間の上限）。`stop_rule`（`k_max`、`time_limit`）に規則を、`history` に全反復の残差履歴（`history_full: true`。v1.0 より前は約1,500点に間引き）を記録する。
- 同じ `--out` に別の規則の結果があると、`run` は止まる（規則を混ぜないため）。v1.0 の測定は新しい `--out`（例 `results/pcb_v1`）に流す。
- v1.0 より前の規則では、600秒で打ち切られたジョブは `timeout` として記録される（到達残差つき）。予算を延ばして解き直すことはしない（設定書15.8節）。

### 4.4 Multi-RHS

1右辺あたりの予算は `pcb_case_parameters.json` の `multiRhsBudgetPerPort`（P07-1・P08-N4_s1は600秒、P08-N8_s1は900秒）。多数右辺の1ジョブの予算は、これにポート数を掛けた値（2,400・4,800・14,400秒）。比べるために、すべて1ワーカーの単独実行で流す。

```bash
S=P08-N4_s1; P=600; B=4800
$R --sets $S --combos mumps/direct --mrhs shared --workers 1 --budget $B
$R --sets $S --combos cslp_hx/gmres --port all --tag u1 --workers 1 --budget $P   # 独立（基準）
for m in shared block gcro; do $R --sets $S --combos cslp_hx/gmres --mrhs $m --workers 1 --budget $B; done
```

独立の総時間は、`@u1` の各ポートの総時間の合計（ポート1は `<セット>@u1`）。

### 4.5 集計

```bash
python3 freefem/pcb/summarize_pcb_benchmark.py --dest docs/results_v1/mac_m3pro   # v1.0 の記録（M3 Pro）
python3 freefem/pcb/summarize_pcb_benchmark.py --dest docs/pcb_results       # v1.0 より前: WSL（Macは docs/pcb_results/<host>）
python3 freefem/pcb/assemble_s_matrix.py --problems P03                      # S行列の組立て（相反性・受動性の確認）
python3 freefem/pcb/check_p01_sparams.py --help                              # 物理の確認（check_p04_contrast.py、check_p05_resonance.py、check_p06_slot.py も）
python3 freefem/pcb/summarize_matrix_features.py --host mac_m3pro \
    --from-csv docs/pcb_results/mac_m3pro/matrix_features.csv --out docs/pcb_results/mac_m3pro   # 特徴量の表の反復数
```

- `pcb_summary.csv`（標準の結果）、`pcb_summary_variants.csv`（名前に `@` を含む変種）、`pcb_summary.md`（ケース×組合せの表と詳細）。`max_it`（と v1.0 より前の `timeout`）の結果には、残差履歴の傾向の補足情報を列 `trend*`（窓の長さ、傾き \(s\)、\(\rho\)、\(N_{\mathrm{est}}\)、\(\rho^{\mathrm{cyc}}\)、包絡線の最終更新、窓での減少）と `timePerIteration`・`trendTimeToConverge` に出し、`pcb_summary.md` の「上限に達した結果の補足情報」に表にする（`convergence_trend.supplement`。窓は GMRES 系 \(w=0.2\)、COCG 系 \(w=0.5\)。cslp_hx の \(N_{\mathrm{est}}\) は悲観側、docs/paper_plan.md 4.3〜4.4節）。\(\lvert\Delta S\rvert\) は同じセットのMUMPS参照との差。
- 記録として残すのは `docs/pcb_results/` のサマリーと確認結果だけ。push前に `git pull --rebase`（WSL・M1・M3 Proの3台から同じ `main` にpushするため）。

### 4.6 Ritz値（前処理後の演算子の特徴量）

求解の代わりに、前処理後の演算子 \(AM^{-1}\) で Arnoldi を K ステップ回し、Hessenberg 行列から Ritz 値と特徴量を求める（matrix_features.md 8章）。

```bash
python3 freefem/pcb/run_pcb_benchmark.py ritz --list                                  # Core 9セット×8前処理
python3 freefem/pcb/run_pcb_benchmark.py ritz --suite core --workers 4                # K=300、開始ベクトルは右辺
python3 freefem/pcb/run_pcb_benchmark.py ritz --sets P05-1 --precs hx --inner vcycle  # 内側をVサイクル1回に
python3 freefem/pcb/ritz_features.py summarize --out docs/pcb_results/<host>          # 表（同じ計算機の反復数と並べる）
python3 freefem/pcb/ritz_features.py show results/pcb_ritz/<host>/hessenberg/P05_P05-1__hx.txt
```

- 前処理は gs、ssor、amg_gamg、accel_ic、cslp、hx、cslp_hx。演算子はKrylov法によらないので、GMRESとCOCGで共通。
- cslp・hx・cslp_hx は、標準では内側の解法がGMRES（rtol \(10^{-2}\)）で、前処理が反復ごとに変わる。プローブでは内側を固定する（既定 `--inner lu`: MUMPSで厳密に解く。標準の組合せが近似している演算子）。
- 結果は `results/pcb_ritz/<host>/`（`runs/*.json`、`hessenberg/*.txt`、`logs/`）。
- 既存ベンチマークのセット（`case2A:standard` など）も `run` と同じ選び方（`--sets`、`--suite`）で入る（2026-10-12）。メッシュは `--existing-mesh-dir`（既定 `generated_meshes/mesh`）。結果の `set` は `case2A:standard` の形。
- v1.0 の記録（B5、M3 Pro）は `freefem/pcb/chains/b5.sh` でまとめて流す（特徴量 `matrix_features.py --backend mumps` → Ritz プローブ 112セット×8前処理、単独。済みのものは飛ばすので、止まったら同じコマンドで再開）。結果は `results/pcb_features_v1/`・`results/pcb_ritz_v1/`、表は `docs/results_v1/mac_m3pro/{matrix_features,ritz_features}.{md,csv}`（反復数は `--iters docs/results_v1/mac_m3pro/pcb_summary.csv`）。
  ```bash
  caffeinate -i nohup bash freefem/pcb/chains/b5.sh > ~/b5.log 2>&1 &
  ```

### 4.7 メッシュ収束（既存ケース、B6）

既存の Core 4セット（case1A:standard、case2A:standard・off_resonance、case3A:high_contrast）で、lc（パラメータ `lc*`）に倍率 1、0.8、0.63、0.5 を掛けたメッシュで解き、最も細かい解との差を求める（`freefem/pcb/mesh_convergence.py`、比較は `pcb_mesh_convergence.edp`）。倍率 1 は B1 のメッシュそのもの（MD5 で確認）。0.5 は MUMPS のメモリが足りないので `npatch_asm/cocg`（rtol \(10^{-8}\)）で解く。

```bash
python3 freefem/pcb/mesh_convergence.py mesh      # generated_meshes/convergence/h<倍率>/
python3 freefem/pcb/mesh_convergence.py run       # results/pcb_meshconv/（単独、解を保存）
python3 freefem/pcb/mesh_convergence.py compare   # 最も細かいメッシュの上で差を積分
python3 freefem/pcb/mesh_convergence.py summary --out docs/results_v1/mac_m3pro
```

## 5. 困ったとき

| 症状 | 対処 |
|---|---|
| FreeFEMが何も出力せずに止まる（WSL） | `export HWLOC_COMPONENTS=-gl` を付ける |
| 同じジョブが急に遅くなった | 電源（バッテリー駆動）と他の負荷を確かめる。5並列の時間の揺らぎは約10% |
| `run` が `parameter set ... not selected` を出す | `--show-config` などでは、既定の `--roles minimal_set` 以外のセットに `--roles ''` か `--suite` を付ける |
| `summarize` がMacの結果の書き込みを拒否する | Macでは `--dest docs/pcb_results/<host>` を指定する。v1.0 の記録は M3 Pro で `--dest docs/results_v1/mac_m3pro`（版が 1.0 でない結果も拒否される） |
| Macで大きいジョブが外される | 仕様（メモリの見積もりが75%を超える）。`--mem-budget 0` で無効にできるが、メモリが足りなくなる |
