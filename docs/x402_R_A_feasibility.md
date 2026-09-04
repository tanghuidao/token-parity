# x402 数据接入 R_A 校准可行性报告 —— 2026-09-04

> 任务书④ 探勘输出。本报告**只评估现有归档**是否够用；不修改主管线任何文件。
> 配套分析脚本：`docs/work_x402_feasibility_probe.py`（不入 commit，作为探勘工具保留）。

---

## 一、数据规模与覆盖

| 维度 | 实测值 | 评价 |
|---|---|---|
| 时间窗 | 2026-08-21 → 2026-09-04，共 **15 天** | 刚够开始看趋势，远不到稳态 |
| 总 endpoint 行数 | **440,993** | 充足 |
| 日均 endpoint | 27,811–30,675 | 稳定，单调上升（9-04 突破 30k） |
| 日均 service 数 | 2,190–2,389 | 同样稳定上升 |
| 报价完整度 | **97.5%**（30,006 / 30,675 最新日） | 略高于均值，可接受 |
| 数据源 | **100% Agentic.Market**（单源） | 与"零依赖单源"既定事实一致，无新增风险 |
| fetch 状态 | 100% ok | 无失败日 |
| 存档格式 | v1.1 JSON gzip（每天 ~340 KB） | 与 README §数据源声明一致 |

**结论**：体量、时间窗、完整性均已达到**最低准入门槛**，可以开始建序列。

---

## 二、关键发现：Inference 类的代表性危机

### 2.1 类目分布严重不均

| Category | endpoint 数 | 占比 |
|---|---|---|
| (uncategorized) | 409,047 | **92.7%** |
| Data | 13,577 | 3.1% |
| Infra | 5,865 | 1.3% |
| **Inference** | **4,319** | **1.0%** |
| Media | 4,065 | 0.9% |
| Travel | 1,884 | 0.4% |
| Social | 1,725 | 0.4% |
| Search | 346 | 0.1% |
| Storage | 90 | <0.1% |
| Other / Trading | 75 | <0.1% |

⚠️ **92.7% 服务未分类**——Agentic.Market 上线新服务时未填 category，导致大量 service 进入"无主清单"。

### 2.2 Inference 类高度集中在一家

9 个 Inference 类 service 中，**blockrun-ai 占 3,569/4,319 = 82.6%**。这是 x402 上"任意模型按次计费"的代理层，单一服务聚合了多家上游 LLM。

| Inference service | endpoint | w/price |
|---|---|---|
| blockrun-ai | **3,569** | 3,494 |
| venice-ai | 285 | 270 |
| platform-openai-com | 135 | 75 |
| docs-anthropic-com | 90 | 30 |
| ai-google-dev | 75 | 45 |
| deepseek-com | 60 | 30 |
| groq-com | 60 | 30 |
| api-questflow-ai | 30 | **0**（全无价） |
| hyperbolic-xyz | 15 | 15 |

### 2.3 这种集中度对校准的直接影响

- 如果直接拿 x402 Inference endpoint 均价对照 OpenRouter 主篮子价，**结果主要由 blockrun-ai 一家决定**——本质是"它的挂牌价与 OpenRouter 同模型牌价的偏差"，不具备"agent-to-agent 真实成交价"的代表性。
- 要做"真实成交"校准，需要接入**实际发生过的二级市场 trades 数据**（例如 CDP Bazaar 的 orderbook 历史），但 CDP 全量 15k+ listing 抓不全（已记录在 2026-08-21 评估结论中），单独抓 trades 没有公开端点。

---

## 三、价格口径：按次 USDC，不按 token

### 3.1 报价分布（Inference 类）

```
min=0.001000, p10=0.001000, p50=0.005000, p90=0.008500, max=5.000000, mean=0.024232
（每次调用的 USDC 价格，3989 条有价样本）
```

- 中位数 0.005 USDC（约 $0.005 / 次）
- 长尾到 5 USDC/次（极贵，可能是付费版搜索/数据 API）
- max / median 比 = 1000x——典型按次定价的小额微付费形状

### 3.2 不能直接折算到 $/token

x402 listings **全部按次定价**（准确地说，"upto"上限 + "exact"定额两种 price_scheme），**没有披露每次调用的 token 数量**。

要把 x402 数据折算到 R_A（$/kWh）体系，必须先确定每个 endpoint 的平均 token 用量——这不在 x402 listings 字段内。理论上可以从以下来源反推：
- 上游 OpenRouter / 厂商直接 API 的 token 计费记录
- 每个服务的 documentation / 自行 benchmark

**现实**：这是个**新引入的未知参数**（"每调用 token 数"），把这个参数叠在 jᵢ 之上，会让原本就要驯服的"以 x402 数据取代 x402 listings"流程叠加更多不确定性。

### 3.3 "upto" 价格分布

price_scheme 分布：

| scheme | 行数 |
|---|---|
| exact | 434,114 |
| upto | 6,825 |
| batch-settlement | 39 |
| nvm:erc4337 | 15 |

`upto` 上限报价占 1.5%，意味着**约 1.5% 的 endpoint 不能给出确定成交价**，要做对照序列需对 `upto` 行特殊处理（用 max_amount 或保守取 min_amount）。

---

## 四、可行的接入路线（不自动决策，交由项目所有者拍板）

### 路线 A：纯 listings 对照列（最稳健）

**思路**：把 x402 listings 的"每次调用 USDC 价格"作为**新的稳健性对照列**，与现有 LiteLLM 对照列平行存在；不折算 token、不进主序列。

**实现要点**：
- 在 `parity_series.csv` 新增 `R_A_x402_listings` 与 `alt_x402_deviation` 两列
- 用 Inference 类的简单日均（中位数优于均值，避免 blockrun-ai 长尾）作为对照口径
- 标注 `inference_service_count=N, top1_concentration=X%`，把代表性危机写进数据
- 主列 R_A / Lambda / Lambda_chained / Omega 零影响，历史行不回填

**优势**：完全不动主计算逻辑、保留"按次 vs 按 token"的元数据差异作为方法论注释
**劣势**：因为是 listings 而非真实成交，对真实 agent-to-agent 经济的代表性打折

### 路线 B：折算到 $/token 的对照列（中等成本，需引入新参数）

**思路**：在路线 A 基础上，从 OpenRouter 上对应 service 的 token 计费结构反推"每调用 token 数"假设，给出 `R_A_x402_token_implied` 列。

**前置依赖**：
- 建立 x402 inference service → OpenRouter model 的映射（人工对账，9 个 service 可控）
- 假设每调用平均 X token，需要逐服务 benchmark（这是新参数，与 jᵢ 类比会引入第二个误差源）

**优势**：与 R_A 真正可比（同维度）
**劣势**：引入新参数 `tokens_per_call`，叠在 jᵢ 上变成"两层不确定性"，把"用 x402 真实成交校准"的初衷复杂化

### 路线 C：等到真正二级市场 trades 数据可用（不行动）

**思路**：当前 listings 数据不能代表"真实成交价值"。等到 CDP / 402nodes / 其他二级市场公开 trades 历史后再启动。

**优势**：避免在 listings 上做科学上不严谨的对照
**劣势**：可能需要等很久（目前没有公开 trades 历史端点）

### 路线 D：智能体经济变体 RA_agent（替换路线而非主 R_A 校准）

**任务书暂停确认点**："是否要因为 x402 数据的出现，重新讨论'智能体经济变体 RA_agent'该走 x402 真实成交路线还是之前讨论的 benchmark（如 SWE-bench Pro）代理路线"。

**我的建议**：把 RA_agent 作为**独立的新指数族**，与 R_A（OpenRouter 主篮子）并列发布，走 x402 路线（路线 A 或 B 作为独立序列），不冲击现有 R_A。这样：
- R_A 仍然是 OpenRouter + jᵢ 的现有体系；
- RA_agent_agent 走 x402 listings 或 future trades；
- 两个指数服务于不同问题：R_A 回答"前沿模型 API 经济学"，RA_agent 回答"agent-to-agent 完成一次调用花多少"。

---

## 五、本报告结论与下一步建议

### 5.1 数据**够用程度**判断

| 维度 | 状态 |
|---|---|
| 体量与时间窗 | ✅ 够建对照列 |
| 报价完整度 | ✅ 97.5% |
| 类目代表性 | ❌ 92.7% 未分类；Inference 类过度集中 |
| 价格口径适配 R_A | ❌ 按次不按 token，需引入新参数 |
| 真实 agent-to-agent 成交覆盖 | ❌ 100% 是 listings，非 trades |
| 单源风险 | ⚠️ 与现有数据治理纪律一致，未新增风险 |

### 5.2 给项目所有者的明确建议

1. **短期内不上 R_A 校准**。真实 agent-to-agent 成交数据当前无可信公开端点，强行把 x402 listings 折算到 $/token 会引入"每调用 token 数"这一新假设层，违背"用真实成交校准"的初衷。
2. **可以启动路线 A 作为新稳健性对照列**（`R_A_x402_listings` + `alt_x402_deviation`），但**必须**在 CSV 中标注：
   - `x402_inference_service_count`（天级别）
   - `x402_top1_concentration`（blockrun-ai 占比，天级别）
   - `x402_listings_not_trades`（哨兵，恒为 true 直至 trades 数据接入）
3. **路线 D（独立 RA_agent 指数族）是优选策略**。把 listings 数据 + 未来 trades 数据统一到一个与 R_A 并列的新指数族，作为"agent 经济口径"的独立发布；不冲击主 R_A 也不抢 token 篮子席位。
4. **建议数据积累到至少 30 天再考虑接入**（目前 15 天）。30 天是 README 中"序列稳定"隐含的下限，也与 O4 DOI 存缴时点对齐。

### 5.3 不动 x402 任何东西

- 归档脚本 x402_archive.py 不改
- 主序列（parity_index.py / build_site.py / Lambda_chained 等）不动
- 本报告留仓作为决策依据，本身不入主 commit（作为 docs/ 文件存在即可）
- 探勘脚本 `docs/work_x402_feasibility_probe.py` 作为分析工具保留（不入 commit，写明"work_"前缀）

---

## 六、配套文件

- **本报告**：`docs/x402_R_A_feasibility.md`
- **探勘脚本**：`docs/work_x402_feasibility_probe.py`（不入 commit，前缀 `work_` 表明是临时工具）
- **任务书④**：`Downloads/TEPI_Agent任务书_20260904.md`（已读，结论落本报告）
