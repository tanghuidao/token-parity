# Changelog

质量分（quality_score）与指数口径变更登记。规则见 README「质量分口径」。

| 日期 | 项目 | 变更 |
|---|---|---|
| 2026-08-16 | quality_score 首次录入 | Claude Sonnet 5=55, GPT-5.5=56, Gemini 3.7 Flash=56, DeepSeek V4 Pro=53（AA Intelligence Index v4.1.1，各模型最高已评档，查询日期 2026-08-16） |
| 2026-08-17 | 数据源治理三层机制上线 | 背景：Stripe 收购 OpenRouter（彭博 2026-08-16）。新增：raw/ 原始响应逐日归档；basket_detail.csv 成分层明细（R_A=Σcontrib 可复现）；LiteLLM 厂商牌价第二源交叉验证列。主序列加列 basket_price_alt_usd_per_mtok、alt_coverage，旧行补空值，口径无断点 |
