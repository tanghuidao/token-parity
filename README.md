# Token 能量平价指数（Token Energy Parity Index）

把 AI 推理 token 和 PoW 加密货币折算到同一个物理公分母（每千瓦时收入），构造日频指数族，作为"焦耳平价"框架的实证核心与活体演示。

**官方站点 / Official site: https://abundantics.org** （指数大屏、方法论、数据下载；本仓库的 GitHub Pages 页面继续作为数据页保留）

方法论文档：TEPI Index Methodology v0.1（中英双语，见官方站点方法论页）。本指数隶属丰裕学（Abundantics）研究纲领，预印本合订本 v1.6 已存缴 Zenodo：DOI [10.5281/zenodo.21989658](https://doi.org/10.5281/zenodo.21989658)。

## 四条指数

| 指数 | 定义 | 含义 |
|---|---|---|
| R_M | hashprice ÷ 每 PH/s 日耗电 | 挖矿每度电毛收入（$/kWh） |
| R_A | Σ 用量权重 × 模型单价 × (3.6e6 ÷ 单token能耗) | 推理每度电毛收入（$/kWh） |
| Λ | R_A / R_M（发布链式接续序列 Lambda_chained） | 能量套利比（**毛收入口径，非利润**） |
| Ω | ln(ρ*/ρ)，质量调整后 | 平价偏离指数：市场对"防御性耗散"与"生产性耗散"的定价缺口 |

其中 ρ*（焦耳平价汇率）= ε_BTC × 篮子每焦耳标准token产出；ρ（市场隐含汇率）= BTC 价格 ÷ 基准模型 token 单价；ε_BTC（单枚体现能）= 全网日耗能 ÷ 日产出 BTC。标准 token 当量由**外部质量分**折算（见下文"质量分口径"），非价格权重。

序列起点：2026-08-16（篮子 v1）。质量分于同日采纳，Ω 自 2026-08-17（采纳后首个例行运行日）起进入发布序列。

**篮子代表性口径声明**：当前篮子（v1）为**前沿 reasoning 模型篮子**（加权均价约 $11.44/百万 token），Λ 度量的是前沿推理口径的能量套利比，**不代表全 AI 行业平均水平**。产业界常说的"20–25 倍"对应**走量（commodity）模型口径**（均价约 $1/百万 token）。两口径各自自洽，详见 `docs/ji_source.md` 与国外对标 Compute Heat Rate（CHR，Hans Royal 提出）的交叉验证。

## Λ 置信带（jᵢ 三档）

jᵢ（单 token 能耗）是本指数最薄弱的输入（局限 L5）。自 2026-09-01（P0）起，主序列新增四列置信带：`R_A_low / R_A_high / Lambda_low / Lambda_high`。

- **三档取值**：每个篮子模型配低/中/高三档 jᵢ（同 D′ 口径：全栈 ÷ 计费输出 token 含思考），中档 = 主列点值，三档表与逐项出处见 `docs/ji_source.md` §9.3。
- **计算定义**：逐模型把 jᵢ 替换为低/高档（价格、权重一律不变）后重新聚合，**而非对加权均值 j̄ 整体缩放**——jᵢ 低档 → R_A_high / Lambda_high，jᵢ 高档 → R_A_low / Lambda_low。
- **主列零影响**：`R_A / Lambda / Lambda_chained / Omega` 等全部主列恒用中档点值，口径与历史数值不变；置信带仅为附加区间列，历史行留空（自 2026-09-01 起新行有值，不回填）。
- **复现承诺**：与 R_A = Σ contrib_R_A 相同，`basket_detail.csv` 新增 `j_per_token_low/high` 与 `contrib_R_A_low/high` 列，逐行求和即可复现两个边界值，数值哨兵每次写入前自动核验。
- 参考：换篮子（basket_version 递增）后，chained 口径的置信带 = 当日链式系数 × Lambda_low/high。

## 换算链条（全部显式，可逐步核对）

挖矿侧：

```
hashprice ($/PH/day) = 近144块总奖励(BTC) × BTC价格 / 全网算力(PH/s)
1 PH/s 功耗 (W)      = 全网加权能效(J/TH) × 1000
R_M ($/kWh)          = hashprice / (功耗 × 86400 / 3.6e6)
```

自校验：2026-08-10 样本数据算出 hashprice $31.74、R_M $0.066/kWh，与 Hashrate Index 周报的 $31.73 及"多数矿工处于盈亏平衡"的描述吻合（典型矿场电价 $0.04–0.08/kWh）。

推理侧（质量折算用外部基准分，独立于价格）：

```
质量权重 q_i   = 模型i质量分 s_i / 基准模型质量分 s_ref   (s 来自 AA Intelligence Index)
标准token当量  = 原始token × q_i        (质量调整落在数量侧，价格侧不动)
R_A            = Σ w_i × 单价_i × (3.6e6 / J/token_i)
```

> 注：第 0 版曾采用价格型质量权重（q_i = 单价比），后证明该定义使 Ω ≡ ln(Λ) 恒成立、不携带独立信息（退化命题，见方法论 v0.1 第 5.5 节），已于 Patch v2.0 弃用。

## 使用

```
pip install requests matplotlib     # matplotlib 仅 --plot 需要

python parity_index.py              # 在线抓取，计算并追加当日一行
python parity_index.py --offline    # 用 sample_data.json 离线验算
python parity_index.py --plot       # 附带绘制历史四联图
python parity_index.py --config my.json   # 覆盖默认配置
```

日频运行建议挂 cron / 计划任务：

```
10 8 * * * cd /path/to/token_parity && python3 parity_index.py --plot
```

同一天重复运行会覆盖当日行，序列保持干净。

`--dry-run` 参数只计算打印不写 CSV，用于换篮子时的新旧对比：

```
python parity_index.py --dry-run    # 实时抓取计算，只打印不写入
```

## 如何更换篮子（Λ 链式接续）

模型篮子会随 OpenRouter 上下架频繁变化，Λ 的绝对水平对篮子极敏感。为保证正式序列衡量"变动"而非"篮子水平"，参照 CPI 的链式接续法：

1. 仓库根目录维护 `chain_factors.json`，结构 `{"v1": 1.0, "v2": <系数>, ...}`，每个版本对应 `DEFAULT_CONFIG` 里的 `basket_version`。
2. 换篮当天，先把 `basket_version` 递增为 v2（修改篮子 id / weight / j_per_token 后），分别用旧配置和新配置各跑一次 `--dry-run`：

```
# 旧配置（v1）
git stash && python parity_index.py --dry-run    # 记下输出的 Λ_raw(旧)
# 新配置（v2）
git stash pop && python parity_index.py --dry-run    # 记下输出的 Λ_raw(新)
```

3. 计算系数：`chain_factor_v2 = Λ_chained(旧) ÷ Λ_raw(新)`，把该系数写入 `chain_factors.json` 的 `"v2"` 键后再正式提交切换。
4. 切换后 `Lambda_chained = Lambda × chain_factor_v2`，与 v1 序列无缝衔接。
5. 网页图表与一切分析使用 `Lambda_chained` 列，不用原始 `Lambda`。

本机制已搭好，当前 v1 系数为 1.0，两列数值相同属正常。

## 质量分口径（quality_score）

Ω 的质量侧校准使用 Artificial Analysis 的 Intelligence Index 综合分（https://artificialanalysis.ai/models ，当前指数版本 v4.1.1），作为独立于价格的质量度量。口径与维护规则：

- **选档口径**：取该模型"各档位中 AA 已评测的最高 reasoning 档"分数（如 GPT-5.5 xhigh、Claude Sonnet 5 Max Effort、Gemini 3.7 Flash high、DeepSeek V4 Pro Max Effort），因为多数模型只有最高档被 AA 完整评测。
- **记录位置**：分数写在 `parity_index.py` 的 `inference_basket` 每项 `quality_score` 后的行内注释里，含变体全名、指数版本、查询日期、口径。
- **季度复查**：每季度由项目所有者复查一次，确认 AA 是否更新分数或改版。
- **变更登记**：AA 指数改版或任一模型分数更新时，在 `docs/changelog.md` 记一行：日期 + 模型 + 新旧分数（如 `2026-11-15 | GPT-5.5 | 56 -> 58 (AA v4.2)`）。

## 数据源

| 数据 | 来源 | 更新方式 |
|---|---|---|
| BTC 价格 | CoinGecko simple/price | 自动 |
| 全网算力、区块奖励 | mempool.space mining API | 自动 |
| 推理价格（主源） | OpenRouter /api/v1/models | 自动 |
| 推理价格（第二源，交叉验证） | LiteLLM model_prices 表（厂商直连牌价） | 自动 |
| 矿机队列能效 | CBECI / Hashrate Index 机型统计 | **手动，建议每季度** |
| 单token能耗 | 人工设定工作假设，溯源与口径见 `docs/ji_source.md` | **手动** |
| 篮子用量权重 | OpenRouter rankings 页 | **手动，建议每月** |
| 质量分（Ω 用） | Artificial Analysis Intelligence Index | **手动，季度复查** |
| 历史回填（RM 侧，月频至 2010-07） | blockchain.info charts（价格/算力/手续费，日频） | **一次性脚本** `backfill_rm.py`，能效历史表见 `docs/efficiency_history_source.md` |
| 机器间真实成交（agent-to-agent，x402/USDC 协议） | Agentic.Market 等 v1.x 公开 discovery 端点（依赖项见 `x402_archive.py`） | 自动（`raw_x402/YYYY-MM-DD.json.gz`，归档不动数据） |

**`raw_x402/` 归档说明**：自 2026-09-03 起，本仓库开始逐日归档 x402/USDC 协议下的机器间（agent-to-agent）真实成交数据（v1.1，gzip 存储）。这是为未来把 R_A 的校准锚点从"挂牌价"升级为"真实机器间成交价"做准备——挂牌价与智能体真实交付价值之间的脱钩，会随着智能体工作流占比上升而扩大，x402 提供的是这方面目前能拿到的最接近真实经济价值的公开数据。当前处于归档阶段，尚未接入主计算，接入方案见 Agent 任务书④。

hashprice 不直接抓 Luxor（需要 API key），而是用公开链上数据从定义式自行计算，结果与 Luxor 指数一致（见上文自校验）。

## 数据源治理与可复现性

指数编制的行规是把风险写在前面。本节登记数据源的治理风险与本项目的三层应对机制，均自 2026-08-17 起生效。

**风险事件登记：2026-08-16，彭博报道 Stripe 已敲定以超 70 亿美元收购 OpenRouter。** 本指数推理侧的价格主源、篮子用量权重参考、Ω 的市场隐含汇率基准，此前均单一依赖 OpenRouter。收购意味着这些数据的开放政策、披露口径从此属于单一商业主体的经营决策；此外垂直整合可能推动计价从"每 token 单价"走向打包订阅，侵蚀"市场价差即质量评价"这一显示性偏好方法的竞争性定价前提。应对如下：

1. **原始数据逐日归档**（`raw/YYYY-MM-DD.json`）。每次在线抓取都把四个数据源的原始响应存档入库：链上数据原样保存；OpenRouter 全量响应逐模型精简为 id、名称、上架时间、上下文长度与完整 pricing 字典（剔除大段描述文本，控制体量）。归档的是**全市场每日价格截面**而非仅篮子四个模型——享乐回归、跨模型价格研究、事后换篮审计都以此为原料。上游政策变更之日，就是这份存档不可再生成之时。
2. **第二价格源每日交叉验证 + 稳健性对照列**。取 LiteLLM 社区维护的公开价格表中各厂商**官方直连** API 条目（非 Azure/Bedrock 转售渠道），治理上独立于 OpenRouter/Stripe。自 2026-09-01（P1）起在验证列之外升级为稳健性对照：主序列新增 `R_A_alt / Lambda_alt / alt_deviation` 三列——用第二源牌价、同一权重同一 jᵢ（中档）平行计算的 Λ 对照序列，与主列同篮子同权重、直接可比；`alt_deviation`（小数，0.02 即 +2%）监测两源剪刀差，超 ±15% 触发哨兵告警，覆盖不完整（≠4/4）时对照列置空。主列 R_A / Lambda **继续只用 OpenRouter 市场价**，对照列零影响；两源发生系统性背离时可据此判别漂移发生在数据源还是指数本身，主源危机时 `Lambda_alt` 序列可作过渡基准（源切换须人工决策，不自动执行）。结构性差异须知：LiteLLM 为厂商牌价（阶梯粘性，多日不变），OpenRouter 为市场价（日日波动），偏离度本身是牌价-市场价折溢价的观测，并非"谁对谁错"；历史观测区间 ±1.3% 至 +9.8%（2026-08-18 至 08-31）。
3. **成分层明细公开**（`basket_detail.csv`）。每日每模型一行：归一化权重、两源价格、能耗参数、质量分与对 R_A 的贡献。复现关系为 R_A = Σ contrib_R_A，逐行可验，数值哨兵在每次写入前自动核验这条恒等式。主序列中的 `basket_price_usd_per_mtok` 与 `basket_j_per_token` 为**描述性均值，仅供概览**：由于逐模型聚合（先除后加）与均值相除（先加后除）不可交换，`basket_price × 3.6e6 ÷ basket_j ≠ R_A` 是数学必然而非数据错误；R_A 的精确复现一律以明细文件为准。

## 已知局限（写论文时要如实交代）

1. **Λ 是毛收入比不是利润比。** 推理侧成本大头是 GPU 折旧而非电费，均衡应比较全成本利润率。利润版 Λ' 需要矿企/云厂商财报做季度校准。

    **阶段一试算**（2026-09-01，2026 Q2 财报口径）显示：现金口径 Λ′≈420，**全成本口径下矿工侧与推理侧利润率均为负**。这提示两点：其一，方法论 9.1 节"挖矿侧套利已闭合"这一表述需要加一句限定——难度调整摁住的是矿工的**边际现金成本**，而非全成本，矿工目前很可能仍在用硬件折旧的老本运营，全成本意义上的均衡尚未达成；其二，"净口径套利比反而高于毛口径"（420 > 234）本身是个需要专门解读的现象，大概率是矿工现金成本（几乎全是电费）占收入比重远高于推理侧现金成本占比，扣除各自现金成本后挖矿侧收入被压缩得更狠。完整的 α 双侧净 + 多家财报校准尚未展开，详见路线图 O2。
2. **能效参数是最大误差源。** 挖矿侧全网加权能效 η 与推理侧单 token 能耗 jᵢ 是本指数最大的两个不确定性来源：η ±25% 会让 R_M 与 ε_BTC 同比例漂移；jᵢ 的公开估计仍横跨接近一个数量级。**jᵢ 已于 2026-09-01 上线三档置信带**（见「Λ 置信带」小节，逐模型替换低/中/高档后重新聚合）；**η 的三档敏感性尚未实现**，建议按同一处理方式（而非对全网能效整体线性缩放）补上，输出 R_M/ε_BTC 的置信带。
3. **模型 id 会随 OpenRouter 上下架漂移。** 应对机制已落地：篮子变更走 `basket_version` 递增 + chain-linking 流程（见"如何更换篮子"），正式序列使用 `Lambda_chained`；但接续系数本身引入一次性测量误差，且 Ω 在换篮时点的接续行为尚待首次实证检验。
4. **质量分是单一综合分。** Ω 已改用独立于价格的外部基准分（消除了价格权重导致的 Ω ≡ ln Λ 退化），但单一 Intelligence Index 综合分仍压缩了多维能力差异；享乐定价式的细化（分项能力 → 影子价格）是下一步的方法论升级。此外 AA 指数自身的改版会引入口径跳变，需按 changelog 登记并评估接续。

## 部署（GitHub Pages 数据页 + 每日自动更新）

项目已含 `build_site.py`（把 CSV 渲染成 `docs/index.html`）和 `.github/workflows/daily.yml`（GitHub Actions 每天北京时间 08:10 自动抓数、计算、重建页面并提交）。当前架构：

- **本仓库 GitHub Pages**（`https://<用户名>.github.io/token-parity/`）：数据页，展示最新指数与历史图表，随每日 Actions 自动更新。页面对弱网做了两层防御：数据内联在 HTML 里（不依赖二次请求）；Chart.js CDN 加载失败时自动回退显示 matplotlib 生成的 PNG 曲线图。
- **官方站点 abundantics.org**（Astro + Cloudflare Pages，独立仓库）：每日 UTC 00:40 跨仓库只读拉取本仓库的 CSV，渲染指数大屏与方法论页。本仓库是唯一数据与计算源，站点侧不做任何指数计算。

部署/维护要点：

1. Actions 出问题时，到仓库 Actions 页 → daily-parity-index → "Run workflow" 手动补跑一次。
2. 数值哨兵（sanity_check）只在 Actions 日志里发 `::warning::`，不会让任务失败——黄色警告出现时人工检查即可。
3. 上游抓取失败时保留前一日已发布文件，序列不断档、不造数。

## 国外对标

本指数最接近的同赛道对标是 **Compute Heat Rate（CHR）**，由 Hans Royal 提出、2026 年被 PJM 电网白皮书引用：同样把 AI 推理折算到能源口径（美元/kWh），其混合口径 R_w ≈ $12.5/kWh 与 TEPI 的 R_A ≈ $15.4/kWh 同量级（TEPI 为前沿篮子口径），构成独立方法的交叉验证；CHR 隐含的单 token 能耗 1.1–2.8 J/token 亦与 TEPI 篮子 jᵢ（1.0–3.0）独立收敛。TEPI 相对 CHR 的差异化：日频序列 + 完全开源（CHR 历史仅 2 个季度且数据不开放）、链式接续处理模型更替、质量调整项（Ω）。逐维度对比见研究文档《CHR vs TEPI 逐条对比》。

## 升级路线

- [ ] Λ' 利润率版本（季频，财报校准）
- [x] jᵢ（推理侧单 token 能耗）三档敏感性区间，输出置信带（2026-09-01 上线，见「Λ 置信带」小节）
- [ ] η（挖矿侧全网加权能效）三档敏感性区间，输出 R_M / ε_BTC 置信带（与 jᵢ 处理方式对齐，尚未实现）
- [ ] 享乐定价质量调整（分项评测分数 → 影子价格），及 Ω 换篮接续行为的首次实证
- [ ] BTC 计价 hashprice 序列（剥离币价方差，供协整检验用）
- [x] 历史回填·挖矿侧（O1a，2026-09-01）：`backfill_rm.py` + `docs/rm_history.csv`（月频至 2010-07，独立序列不进主序列，能效历史表初稿待溯源定稿见 `docs/efficiency_history_source.md`）；历史回填·推理侧（O1b，"历史前沿篮子"）另立项
- [ ] x402/USDC 交易级数据接入，用真实机器间成交价校准 R_A
- [ ] TEPI 独立 Zenodo 记录（版本化数据集 + 方法论双文档，目标：序列满 30 天时存缴，DOI 回填引用条目）

## 引用

```bibtex
@misc{tang2026tepi,
  title  = {TEPI --- Token Energy Parity Index: Index Methodology v0.1},
  author = {Tang, Huidao},
  year   = {2026},
  url    = {https://abundantics.org/en/index/methodology/},
  note   = {Abundantics Empirical Module 01. Method v0.1, accessed YYYY-MM-DD}
}
```

数据与方法论：CC-BY 4.0 · 代码开源 · 非投资建议
