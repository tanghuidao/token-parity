# Artificial Analysis Intelligence Index 调查记录

> **查询日期**: 2026-08-16
> **Intelligence Index 版本**: v4.1.1（含 9 项评估：GDPval-AA v2、τ³-Banking、Terminal-Bench v2.1、SciCode、HLE、GPQA Diamond、CritPt、AA-Omniscience、AA-LCR）
> **数据来源**: artificialanalysis.ai 官方模型页面（直接抓取）
> **用途**: 供项目所有者核对后填入 parity_index.py 的 inference_basket quality_score 字段

---

## 一、四个模型各档位分数汇总

### 1. Claude Sonnet 5（Anthropic）

| 完整显示名 | 档位 | 分数 | 排名 | AA 页面 | 状态 |
|---|---|---|---|---|---|
| Claude Sonnet 5 (Adaptive Reasoning, Max Effort) | Max | **55** | #20/188 | /models/claude-sonnet-5 | ✅ 已评分 |
| Claude Sonnet 5 (Adaptive Reasoning, Medium Effort) | Medium | **N/A** | — | /models/claude-sonnet-5-medium | ⚠️ 页面存在但尚未评分 |

- Anthropic 使用"自适应推理"（Adaptive Reasoning），有 5 个 effort 档位
- **标准档（Medium）页面已建但分数为 N/A**——AA 尚未完成该档位评测
- 目前仅有 Max Effort 档有分数

### 2. GPT-5.5（OpenAI）

| 完整显示名 | 档位 | 分数 | 排名 | AA 页面 | 状态 |
|---|---|---|---|---|---|
| GPT-5.5 (xhigh) | xhigh | **56** | #16/188 | /models/gpt-5-5 | ✅ 已评分（极端档） |
| GPT-5.5 (high) | high | **55** | #22/188 | /models/gpt-5-5-high | ✅ 已评分 |
| GPT-5.5 (medium) | medium | **51** | #27/185 | /models/gpt-5-5-medium | ✅ 已评分 |
| GPT-5.5 (Non-reasoning) | 无推理 | 35.4 | — | 镜像站数据 | ✅ 已评分 |

- OpenAI 有 5 个 effort 档位：xhigh / high / medium / low / non-reasoning
- **OpenRouter 默认端点对应 medium 档**（OpenAI API 默认 reasoning effort = medium）
- 标准档分数 = **51**

### 3. Gemini 3.7 Flash（Google）

| 完整显示名 | 档位 | 分数 | 排名 | AA 页面 | 状态 |
|---|---|---|---|---|---|
| Gemini 3.7 Flash (high) | high | **56** | #17/188 | /models/gemini-3-7-flash | ✅ 已评分 |
| Gemini 3.7 Flash (medium) | medium | **53** | #23/188 | /models/gemini-3-7-flash-medium | ✅ 已评分 |

- Google 有 3 个 reasoning 档位：Low / Medium / High（无 max/xhigh）
- "high" 是 Gemini Flash 的最高档（等同其他家的 max）
- 模型发布日期：2026-08-13（仅 3 天前）
- **需项目所有者确认 OpenRouter 默认调用的是 high 还是 medium**

### 4. DeepSeek V4 Pro（DeepSeek）

| 完整显示名 | 档位 | 分数 | 排名 | AA 页面 | 状态 |
|---|---|---|---|---|---|
| DeepSeek V4 Pro 0813 (Reasoning, Max Effort) | Max | **53** | #17 全榜 / #3/106 开源 | /models/deepseek-v4-pro | ✅ 已评分 |
| DeepSeek V4 Pro 0813 (Reasoning, High Effort) | High | — | — | /models/deepseek-v4-pro-high | ❌ 404 页面不存在 |

- "0813" 是 2026-08-13 正式发布的 GA 版本（非 4 月预览版）
- 4 月预览版 max 档仅 45 分，0813 版升至 53 分（+8 分）
- **High 档页面尚不存在**——AA 目前只为 Max Effort 档评了分
- 目前仅有 Max Effort 档有分数

---

## 二、标准档分数可用性总结

| 模型 | 标准档（对应 OR 默认） | 分数 | 可用？ |
|---|---|---|---|
| Claude Sonnet 5 | Medium | N/A | ❌ AA 未评测 |
| GPT-5.5 | Medium | **51** | ✅ |
| Gemini 3.7 Flash | Medium 或 High（需确认） | **53** 或 **56** | ✅ |
| DeepSeek V4 Pro 0813 | High（页不存在）或 Max | — 或 **53** | ⚠️ High 未评测 |

---

## 三、需要项目所有者决策的问题

1. **Claude Sonnet 5**：标准档（Medium）在 AA 上尚未评分（N/A）。是否暂用 Max 档分数 55？还是等 AA 评测完再填？

2. **Gemini 3.7 Flash**：OpenRouter 默认调用的是 high 还是 medium？（Google API 默认通常是 high，但项目所有者需确认）如果 high 是默认，分数 = 56；如果 medium 是默认，分数 = 53。

3. **DeepSeek V4 Pro 0813**：High 档在 AA 上不存在（404）。是否暂用 Max 档分数 53？还是等 AA 评测完再填？

4. **GPT-5.5**：标准档（Medium）分数 = 51，可直接使用。无歧义。

---

## 四、补充说明

- 所有分数均来自 Intelligence Index **v4.1.1**，查询于 2026-08-16
- AA 的 Intelligence Index 是滚动基准（rolling benchmark），分数会随版本更新而变化
- DeepSeek V4 Pro 的 "0813" 后缀表示 8 月 13 日发布的正式版，与项目 config 中的 `deepseek/deepseek-v4-pro` 对应（OpenRouter 会自动指向最新版本）
- 全程未注册任何账号、未输入任何 API key、未遇付费墙
