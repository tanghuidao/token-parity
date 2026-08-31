# Changelog

质量分（quality_score）与指数口径变更登记。规则见 README「质量分口径」。

| 日期 | 项目 | 变更 |
|---|---|---|
| 2026-08-16 | quality_score 首次录入 | Claude Sonnet 5=55, GPT-5.5=56, Gemini 3.7 Flash=56, DeepSeek V4 Pro=53（AA Intelligence Index v4.1.1，各模型最高已评档，查询日期 2026-08-16） |
| 2026-08-17 | 数据源治理三层机制上线 | 背景：Stripe 收购 OpenRouter（彭博 2026-08-16）。新增：raw/ 原始响应逐日归档；basket_detail.csv 成分层明细（R_A=Σcontrib 可复现）；LiteLLM 厂商牌价第二源交叉验证列。主序列加列 basket_price_alt_usd_per_mtok、alt_coverage，旧行补空值，口径无断点 |
| 2026-09-01 | jᵢ 溯源附录发布 | 新增 `docs/ji_source.md`（定稿 v1.0）：V1 核验确认 reasoning token 按输出 token 计价计费（四家厂商官方文档 + OpenRouter API 实测），jᵢ 口径订正为"全栈 ÷ 计费输出 token（含思考）"（D′）；V2 核验 Gemini 3.7 Flash 默认思考档为 medium，质量分维持统一最高已评档口径不变；V3/V4/V5 核验结论并入。**纯文档变更，不改动任何计算逻辑与已发布序列** |
| 2026-09-01 | 篮子代表性口径声明 | README 新增"篮子代表性口径声明"与"国外对标"小节：明确 TEPI 当前为前沿 reasoning 模型篮子口径（Λ 不代表全 AI 行业平均水平，产业界 20–25 倍为走量模型口径）；CHR（Hans Royal）列为正式对标。jᵢ 维持现状点值（j̄=2.2 J/token）不变，暂不实施三档区间。**口径声明类变更，不影响数值** |
| 2026-09-01 | P0 置信带上线（jᵢ 三档） | `parity_index.py` 为每个篮子模型新增 jᵢ 低/高档配置（取值 = ji_source.md §9.3 三档建议表，中档 = 现行点值不变）。主序列新增 4 列：R_A_low / R_A_high / Lambda_low / Lambda_high（定义：逐模型替换 jᵢ 为低/高档后重新聚合，非 j̄ 整体缩放）；basket_detail.csv 同步新增 j_per_token_low/high 与 contrib_R_A_low/high 4 列保持复现承诺；数值哨兵新增置信带区间自检。**主列（R_A/Lambda/Lambda_chained/Omega 等）口径与数值零影响；历史行带列留空不回填；basket_version 不递增**（未构成换篮） |
| 2026-09-01 | O2（Λ′ 净利率变体）阶段一试算 | 新增 `docs/lambda_prime.md`（试算稿 v1.0）+ `docs/lambda_prime_series.csv`（季频独立序列，首行 2026Q2，source=manual_v1）。定义：α 双侧净，Λ′=(m_A/m_M)·Λ，现金/全成本双口径。2026 Q2 校准（CoreWeave/Riot 等六家财报）：现金口径 Λ′≈420（m_A=59%＞m_M=30.4%），全成本口径双侧皆负不可定义。**纯文档+独立 CSV，不进日频主序列、不进大屏、不改 parity_index.py** |
