# Token 能量平价指数（Token Energy Parity Index）

把 AI 推理 token 和 PoW 加密货币折算到同一个物理公分母（每千瓦时收入），
构造日频指数族，作为"焦耳平价"框架的实证核心与活体演示。

## 四条指数

| 指数 | 定义 | 含义 |
|---|---|---|
| **R_M** | hashprice ÷ 每 PH/s 日耗电 | 挖矿每度电毛收入（$/kWh） |
| **R_A** | Σ 用量权重 × 模型单价 × (3.6MJ ÷ 单token能耗) | 推理每度电毛收入（$/kWh） |
| **Λ** | R_A / R_M | 能量套利比（**毛收入口径，非利润**） |
| **Ω** | ln(ρ*/ρ) | 平价偏离指数：市场对"防御性耗散"与"生产性耗散"的定价缺口 |

其中 ρ*（焦耳平价汇率）= ε_BTC × 篮子每焦耳标准token产出；
ρ（市场隐含汇率）= BTC 价格 ÷ 基准模型 token 单价；
ε_BTC（单枚体现能）= 全网日耗能 ÷ 日产出 BTC。

## 换算链条（全部显式，可逐步核对）

挖矿侧：
```
hashprice ($/PH/day) = 近144块总奖励(BTC) × BTC价格 / 全网算力(PH/s)
1 PH/s 功耗 (W)      = 队列能效(J/TH) × 1000
R_M ($/kWh)          = hashprice / (功耗 × 86400 / 3.6e6)
```
自校验：2026-08-10 样本数据算出 hashprice $31.74、R_M $0.066/kWh，
与 Hashrate Index 周报的 $31.73 及"多数矿工处于盈亏平衡"的描述吻合
（典型矿场电价 $0.04–0.08/kWh）。

推理侧（质量折算用"升贴水法"，仿原油基准分级）：
```
质量权重 q_i   = 模型i单价 / 基准模型单价     （显示性偏好：市场价差即质量评价）
标准token当量  = 原始token × q_i             （质量调整落在数量侧，价格侧不动）
R_A            = Σ w_i × 单价_i × (3.6e6 / J/token_i)
```

## 使用

```bash
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

## 数据源

| 数据 | 来源 | 更新方式 |
|---|---|---|
| BTC 价格 | CoinGecko simple/price | 自动 |
| 全网算力、区块奖励 | mempool.space mining API | 自动 |
| 推理价格 | OpenRouter /api/v1/models | 自动 |
| 矿机队列能效 | CBECI / Hashrate Index 机型统计 | **手动，建议每季度** |
| 单token能耗 | Epoch AI / 厂商披露 | **手动** |
| 篮子用量权重 | OpenRouter rankings 页 | **手动，建议每月** |

hashprice 不直接抓 Luxor（需要 API key），而是用公开链上数据从定义式
自行计算，结果与 Luxor 指数一致（见上文自校验）。

## 已知局限（写论文时要如实交代）

1. **Λ 是毛收入比不是利润比。** 推理侧成本大头是 GPU 折旧而非电费，
   均衡应比较全成本利润率。利润版 Λ' 需要矿企/云厂商财报做季度校准。
2. **能效参数是最大误差源。** 队列能效 ±25% 会让 R_M 和 ε_BTC 同比例漂移；
   单token能耗的公开估计跨度接近一个数量级。建议对这两个参数各设
   高/中/低三档做敏感性区间，而非单点值。
3. **模型 id 会随 OpenRouter 上下架漂移。** 篮子成分变更时应记录换基日期，
   并考虑做环比拼接（chain-linking），否则序列会有断点。
4. **质量权重的内生性。** 用价格做质量权重意味着 Ω 的水平值部分由构造决定；
   跨期变化（ΔΩ）比水平值更可信。享乐回归版（用评测分数回归价格）是
   下一步的方法论升级。

## 部署到 abundantics.cn（静态页 + 每日自动更新）

项目已含 `build_site.py`（把 CSV 渲染成 `docs/index.html`）和
`.github/workflows/daily.yml`（GitHub Actions 每天北京时间 08:10 自动
抓数、计算、重建页面并提交）。部署步骤：

1. **建仓库**：在 GitHub 新建仓库（如 `token-parity`），把本文件夹全部
   内容推上去（注意 `.github` 是隐藏文件夹，不要漏）。
2. **开 Pages**：仓库 Settings → Pages → Source 选 "Deploy from a branch"，
   Branch 选 `main`，目录选 `/docs`，保存。几分钟后页面就在
   `https://<用户名>.github.io/token-parity/` 上线。
3. **首次触发**：仓库 Actions 页 → daily-parity-index → "Run workflow"
   手动跑一次，确认三个接口都通、页面已更新。之后每天自动运行。
4. **绑定域名（可选）**：在 `docs/` 里放一个内容为
   `index.abundantics.cn` 的 `CNAME` 文件；到域名服务商处给
   `index.abundantics.cn` 添加 CNAME 记录指向 `<用户名>.github.io`。

**国内访问的现实提醒**：GitHub Pages 在境内访问时好时坏。三个备选，
按省事程度排序：(a) 前面套一层 Cloudflare（免费，通常显著改善）；
(b) 部署到 Cloudflare Pages / Vercel 而非 GitHub Pages（Actions 照跑，
只换托管端）；(c) 若 abundantics.cn 已有 ICP 备案的国内服务器，在
workflow 末尾加一步 `scp docs/* 服务器:/网站目录/`（需在仓库 Secrets
里配 SSH 私钥），页面就完全落在自己服务器上，访问最稳。
页面本身对弱网做了两层防御：数据内联在 HTML 里（不依赖二次请求）；
Chart.js CDN 加载失败时自动回退显示 matplotlib 生成的 PNG 曲线图。

## 升级路线

- [ ] Λ' 利润率版本（季频，财报校准）
- [ ] 能效参数三档敏感性区间，输出置信带
- [ ] 享乐定价质量调整（评测分数 → 影子价格）
- [ ] BTC 计价 hashprice 序列（剥离币价方差，供协整检验用）
- [ ] 历史回填：CBECI 能耗序列 + 价格存档，把序列推回 2023
- [ ] x402/USDC 交易级数据接入，用真实机器间成交价校准 R_A
- [ ] 部署到 abundantics.cn（静态页 + 每日 GitHub Actions 更新）
