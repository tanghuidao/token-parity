#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token 能量平价指数（Token Energy Parity Index）
================================================

把"挖矿侧"和"AI 推理侧"折算到同一个物理公分母（每千瓦时收入），
构造四条日频指数：

  R_M     挖矿每千瓦时毛收入（美元/kWh）
  R_A     推理每千瓦时毛收入（美元/kWh，按用量加权的模型篮子）
  Lambda  能量套利比 = R_A / R_M（同一度电的毛收入之比）
  Lambda_low/high  Λ 的置信带：篮子 jᵢ 取三档（低/中/高，docs/ji_source.md）
          逐模型替换后重新聚合的区间；主列 Λ 恒用中档点值，不受带列影响
  Omega   平价偏离指数 = ln(焦耳平价汇率 / 市场隐含汇率)
          衡量市场对"防御性耗散"(BTC) vs "生产性耗散"(AI token) 的定价缺口

数据源（全部公开、无需密钥）：
  - 比特币价格:      CoinGecko  /api/v3/simple/price
  - 全网算力/区块奖励: mempool.space  /api/v1/mining/*
  - 推理价格:        OpenRouter  /api/v1/models
  - 矿机队列能效:     配置参数（建议参考 CBECI / Hashrate Index 队列估计，手动季度更新）
  - 推理能效:        配置参数（建议参考 Epoch AI / 厂商披露，手动更新）

用法：
  python parity_index.py                 # 在线抓取并计算今天的指数
  python parity_index.py --offline      # 用 sample_data.json 离线验算
  python parity_index.py --plot         # 计算后把历史序列画成四联图
  python parity_index.py --config my.json  # 使用自定义配置

输出：
  - 终端打印当日快照（含全部中间量，便于核对换算链条）
  - 追加一行到 parity_series.csv（日期去重：同一天重复运行会覆盖当日行）
  - 追加当日各模型明细到 basket_detail.csv（R_A 可由此逐行复现：R_A = Σ contrib_R_A）
  - 在线模式下把三个数据源的原始响应归档到 raw/YYYY-MM-DD.json（数据抢救层：
    上游 API 政策一旦变更，历史就再也抓不到了；先存原始值，用途以后再说）
  - --plot 时生成 parity_index.png

设计说明见 README.md。所有单位换算都显式写出，不藏在魔法数字里。
"""

import argparse
import csv
import json
import math
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None  # 离线模式不需要

# --------------------------------------------------------------------------
# 物理常数与单位（全部显式，便于审计）
# --------------------------------------------------------------------------
J_PER_KWH = 3.6e6          # 1 kWh = 3.6e6 焦耳
SECONDS_PER_DAY = 86400
TH_PER_PH = 1e3            # 1 PH/s = 1000 TH/s
BLOCKS_PER_DAY = 144       # 比特币目标出块率：每 10 分钟一块

DEFAULT_CONFIG = {
    # ---------------- 挖矿侧 ----------------
    # 全网矿机队列平均能效，焦耳每太哈希（J/TH）。
    # 这是唯一无法自动抓取的挖矿侧参数。参考来源：
    #   - CBECI (ccaf.io/cbnsi/cbeci) 的 fleet efficiency 估计
    #   - Hashrate Index 的机型统计（S21 约 17.5 J/TH，S19 XP 约 21.5 J/TH）
    # 建议每季度手动更新一次，并把修改记录在 config 的 notes 里。
    "fleet_efficiency_j_per_th": 20.0,

    # ---------------- 推理侧 ----------------
    # 模型篮子：id 必须与 OpenRouter /api/v1/models 返回的 id 一致。
    # weight        用量权重（建议参考 OpenRouter rankings 页面，手动更新，会自动归一化）
    # j_per_token   该模型输出 token 的全栈能耗估计（焦耳/输出 token，含数据中心 PUE）。
    #               中档点值 = 主口径（R_A/Lambda 等全部主列用此值），政策内参数。
    # j_per_token_low / j_per_token_high
    #               jᵢ 的低/高档估计（同口径 D′：全栈 ÷ 计费输出 token 含思考）。
    #               仅用于置信带列（R_A_low/high、Lambda_low/high），不参与主列计算。
    #               三档取值与出处见 docs/ji_source.md §9.3（2026-09-01 落地，P0）。
    # quality_ref   是否作为质量基准模型（恰好一个为 true）
    # quality_score 该模型的外部基准综合分（如 Artificial Analysis Intelligence Index），
    #               必须来自价格以外的独立评测源。全部模型都有分数时 Ω 才会计算。
    #               口径: 各模型最高已评 reasoning 档（AA Index v4.1.1，2026-08-16 查询）。
    #               由项目所有者手动季度复查；分数更新须在 docs/changelog.md 记一行。
    # alt_price_id: 该模型在第二价格源（LiteLLM model_prices 表）中的键名，
    #               取"厂商官方直连 API"条目（非 Azure/Bedrock 等转售渠道），
    #               用于对 OpenRouter 市场价做治理独立的交叉验证。找不到时置 None。
    "inference_basket": [
        {"id": "anthropic/claude-sonnet-5",       "weight": 0.30, "j_per_token": 3.0,
         "j_per_token_low": 1.5, "j_per_token_high": 4.5,   # 三档：ji_source.md §9.3
         "quality_ref": True, "quality_score": 55,  # 变体 Claude Sonnet 5 (Adaptive Reasoning, Max Effort) | AA Intelligence Index v4.1.1 | 2026-08-16 | 口径: 各模型最高已评档
         "alt_price_id": "claude-sonnet-5",
        },
        {"id": "openai/gpt-5.5",                  "weight": 0.25, "j_per_token": 3.0,
         "j_per_token_low": 1.5, "j_per_token_high": 5.0,   # 三档：ji_source.md §9.3
         "quality_score": 56,  # 变体 GPT-5.5 (xhigh) | AA Intelligence Index v4.1.1 | 2026-08-16 | 口径: 各模型最高已评档
         "alt_price_id": "gpt-5.5",
        },
        {"id": "google/gemini-3.7-flash",         "weight": 0.25, "j_per_token": 1.0,
         "j_per_token_low": 0.5, "j_per_token_high": 1.5,   # 三档：ji_source.md §9.3
         "quality_score": 56,  # 变体 Gemini 3.7 Flash (high) | AA Intelligence Index v4.1.1 | 2026-08-16 | 口径: 各模型最高已评档
         "alt_price_id": "gemini-3.7-flash",
        },
        {"id": "deepseek/deepseek-v4-pro",        "weight": 0.20, "j_per_token": 1.5,
         "j_per_token_low": 1.0, "j_per_token_high": 2.5,   # 三档：ji_source.md §9.3
         "quality_score": 53,  # 变体 DeepSeek V4 Pro 0813 (Reasoning, Max Effort) | AA Intelligence Index v4.1.1 | 2026-08-16 | 口径: 各模型最高已评档
         "alt_price_id": "deepseek-v4-pro",
        },
    ],
    # 篮子里某个模型在 OpenRouter 下架时的策略："skip"（剔除并重新归一化）或 "fail"
    "missing_model_policy": "skip",

    # 篮子版本号：每次修改篮子构成/权重/j_per_token 时由项目所有者手动递增
    # 为 v2、v3…。用于 Λ 的链式接续（见 chain_factor_for / README"如何更换篮子"）。
    "basket_version": "v1",

    # ---------------- 输出 ----------------
    "csv_path": "parity_series.csv",
    "detail_csv_path": "basket_detail.csv",   # 每日各模型明细（R_A 的可复现层）
    "raw_archive_dir": "raw",                 # 原始 API 响应归档目录（数据抢救层）
    "plot_path": "parity_index.png",

    # 数据源 URL（一般不用改）
    "urls": {
        "btc_price": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        "hashrate": "https://mempool.space/api/v1/mining/hashrate/3d",
        "reward_stats": "https://mempool.space/api/v1/mining/reward-stats/144",
        "openrouter_models": "https://openrouter.ai/api/v1/models",
        # 第二价格源：LiteLLM 社区维护的模型价格表（公开、无密钥、独立于
        # OpenRouter 的商业决策）。仅作交叉验证列，不参与 R_A 计算。
        "alt_prices": "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json",
    },
    "http_timeout_seconds": 30,
}


# --------------------------------------------------------------------------
# 数据获取层
# --------------------------------------------------------------------------
@dataclass
class RawData:
    """一次快照所需的全部原始观测值。字段单位写死在名字里，防串。"""
    btc_price_usd: float
    network_hashrate_hps: float          # 全网算力，哈希/秒（H/s）
    daily_block_reward_btc: float        # 最近 144 块的总奖励（补贴+手续费），BTC
    model_prices_usd_per_token: dict     # {model_id: 输出token单价（美元/个）}
    alt_prices_usd_per_token: dict = field(default_factory=dict)
                                         # {model_id: 第二源单价}，抓取失败则为空
    raw_payloads: dict = field(default_factory=dict)
                                         # 各数据源原始响应（在线模式），用于归档
    source: str = "live"
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


def _get_json(url: str, timeout: int):
    resp = requests.get(url, timeout=timeout,
                        headers={"User-Agent": "token-parity-index/0.1"})
    resp.raise_for_status()
    return resp.json()


def fetch_alt_prices(cfg: dict) -> dict:
    """第二价格源（LiteLLM 价格表）：返回 {篮子模型id: 厂商牌价（美元/输出token）}。

    仅作交叉验证，不参与 R_A 计算，因此任何失败都只告警、绝不中断主流程。
    条目缺 alt_price_id 或表中查不到时，该模型对应值为 None。
    """
    mapping = {b["id"]: b.get("alt_price_id") for b in cfg["inference_basket"]}
    out = {mid: None for mid in mapping}
    try:
        table = _get_json(cfg["urls"]["alt_prices"], cfg["http_timeout_seconds"])
    except Exception as e:  # noqa: BLE001 —— 交叉验证源失败不应影响指数产出
        print(f"::warning::第二价格源抓取失败（{type(e).__name__}），本日 alt 列为空")
        return out
    for mid, alt_id in mapping.items():
        if not alt_id:
            continue
        entry = table.get(alt_id)
        if entry is None:
            print(f"::warning::第二价格源中找不到键 {alt_id}（模型 {mid}），"
                  f"请检查 alt_price_id 是否已被上游改名")
            continue
        try:
            out[mid] = float(entry["output_cost_per_token"])
        except (KeyError, TypeError, ValueError):
            print(f"::warning::第二价格源键 {alt_id} 缺少可解析的 output_cost_per_token")
    return out


def fetch_live(cfg: dict) -> RawData:
    if requests is None:
        sys.exit("需要 requests 库才能在线抓取：pip install requests")
    urls, t = cfg["urls"], cfg["http_timeout_seconds"]

    # 1) 比特币价格
    price_payload = _get_json(urls["btc_price"], t)
    price = float(price_payload["bitcoin"]["usd"])

    # 2) 全网算力（mempool.space 返回的 currentHashrate 单位是 H/s）
    hr_data = _get_json(urls["hashrate"], t)
    hashrate_hps = float(hr_data["currentHashrate"])

    # 3) 最近 144 块的总奖励（sats -> BTC）。144 块 ≈ 一天，直接就是日奖励流。
    rs = _get_json(urls["reward_stats"], t)
    daily_reward_btc = float(rs["totalReward"]) / 1e8

    # 4) OpenRouter 模型定价。pricing.completion 是字符串，单位：美元/输出token。
    models = _get_json(urls["openrouter_models"], t)["data"]
    price_map = {}
    for m in models:
        pricing = m.get("pricing") or {}
        completion = pricing.get("completion")
        if completion is not None:
            try:
                price_map[m["id"]] = float(completion)
            except (TypeError, ValueError):
                pass

    wanted = {b["id"] for b in cfg["inference_basket"]}
    basket_prices = {mid: p for mid, p in price_map.items() if mid in wanted}

    # 5) 第二价格源（失败不影响主流程）
    alt_prices = fetch_alt_prices(cfg)

    # 6) 组装归档载荷。前三个源体量小，原样保存；OpenRouter 全量响应含大段
    #    模型描述文本（数 MB），归档时逐模型精简为经济学相关字段：id、名称、
    #    上架时间、上下文长度、完整 pricing 字典——未来做享乐回归、跨模型
    #    价格研究需要的是"全市场每天的价格截面"，而不只是篮子里的四个。
    or_trimmed = [{"id": m.get("id"), "name": m.get("name"),
                   "created": m.get("created"),
                   "context_length": m.get("context_length"),
                   "pricing": m.get("pricing")} for m in models]
    raw_payloads = {
        "btc_price": price_payload,
        "hashrate": hr_data,
        "reward_stats": rs,
        "openrouter_models_trimmed": or_trimmed,
        "alt_prices_extracted": alt_prices,
    }

    return RawData(
        btc_price_usd=price,
        network_hashrate_hps=hashrate_hps,
        daily_block_reward_btc=daily_reward_btc,
        model_prices_usd_per_token=basket_prices,
        alt_prices_usd_per_token=alt_prices,
        raw_payloads=raw_payloads,
    )


def write_raw_archive(raw: RawData, cfg: dict) -> str:
    """把当日原始 API 响应写入 raw/YYYY-MM-DD.json（同日重跑覆盖，与 CSV 同规则）。

    这是数据抢救层：上游（尤其 OpenRouter，2026-08 已被 Stripe 收购）的
    API 政策一旦变更，历史价格截面就永远抓不到了。先原样存档，用途以后再说。
    """
    if not raw.raw_payloads:
        return ""
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(cfg["raw_archive_dir"], exist_ok=True)
    path = os.path.join(cfg["raw_archive_dir"], f"{day}.json")
    doc = {"date": day, "fetched_at": raw.fetched_at, "source": raw.source,
           "payloads": raw.raw_payloads}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    return path


def fetch_offline(sample_path: str) -> RawData:
    with open(sample_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    return RawData(
        btc_price_usd=d["btc_price_usd"],
        network_hashrate_hps=d["network_hashrate_hps"],
        daily_block_reward_btc=d["daily_block_reward_btc"],
        model_prices_usd_per_token=d["model_prices_usd_per_token"],
        source="offline:" + os.path.basename(sample_path),
    )


# --------------------------------------------------------------------------
# 计算层：换算链条逐步显式
# --------------------------------------------------------------------------
@dataclass
class Snapshot:
    date: str
    # 中间量（全部保留，方便核对）
    btc_price_usd: float
    hashprice_usd_per_ph_day: float
    fleet_efficiency_j_per_th: float
    kwh_per_ph_day: float
    epsilon_btc_j: float                 # 一枚 BTC 的体现能（焦耳）
    basket_price_usd_per_mtok: float     # 篮子加权平均：美元/百万标准token
    basket_j_per_token: float            # 篮子加权平均能耗：焦耳/token
    basket_price_alt_usd_per_mtok: float # 第二源（厂商牌价）加权均价；无覆盖时 None
    alt_coverage: str                    # 第二源覆盖度，如 "4/4"
    basket_detail: list
    # 四条指数
    R_M: float                           # 美元/kWh
    R_A: float                           # 美元/kWh
    Lambda: float                        # R_A / R_M
    rho_parity_tok_per_btc: float        # 焦耳平价汇率（无 quality_score 时为 None）
    rho_market_tok_per_btc: float        # 市场隐含汇率
    Omega: float                         # ln(rho_parity / rho_market)（无 quality_score 时为 None）
    source: str
    basket_version: str = "v1"           # 篮子版本号，用于 Λ 链式接续
    Lambda_chained: float = 0.0          # Λ × 链式系数，网页与分析用此列
    # 置信带（jᵢ 三档口径，P0 2026-09-01 起）。任一篮子模型缺三档配置时为 None。
    # 注意与 jᵢ 的反向关系：jᵢ 低档 → R_A_high/Lambda_high；jᵢ 高档 → R_A_low/Lambda_low。
    R_A_low: float = None                # jᵢ 全取高档后的 R_A（$/kWh）
    R_A_high: float = None               # jᵢ 全取低档后的 R_A（$/kWh）
    Lambda_low: float = None             # R_A_low / R_M
    Lambda_high: float = None            # R_A_high / R_M


def chain_factor_for(version, path="chain_factors.json"):
    """读取 Λ 链式接续系数。

    仓库根目录维护 chain_factors.json，结构 {"v1": 1.0, "v2": <系数>, ...}。
    换篮子时由项目所有者手动写入新版本系数，定义：
        系数 = 换篮当天 旧篮 Λ_chained ÷ 新篮 Λ_raw
    （详见 README "如何更换篮子"小节。）

    文件缺失、JSON 损坏或版本未登记时返回 1.0（首版 v1 即为 1.0），
    并打印 ::warning:: 提示，便于在 Actions 日志中发现。
    """
    try:
        with open(path, encoding="utf-8") as f:
            factors = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 1.0
    if version not in factors:
        print(f"::warning::chain_factors.json 中未登记 basket_version={version}，暂用系数 1.0")
    try:
        return float(factors.get(version, 1.0))
    except (TypeError, ValueError):
        return 1.0


def compute(raw: RawData, cfg: dict) -> Snapshot:
    eff = float(cfg["fleet_efficiency_j_per_th"])

    # ---------- 挖矿侧 ----------
    # hashprice（美元/PH/s/天）= 日总奖励(BTC) × 币价 / 全网算力(PH/s)
    hashrate_phps = raw.network_hashrate_hps / 1e15
    hashprice = raw.daily_block_reward_btc * raw.btc_price_usd / hashrate_phps

    # 1 PH/s 的功耗 = eff(J/TH) × 1000(TH/PH) 瓦特；一天电量换成 kWh：
    watts_per_ph = eff * TH_PER_PH
    kwh_per_ph_day = watts_per_ph * SECONDS_PER_DAY / J_PER_KWH
    R_M = hashprice / kwh_per_ph_day

    # 一枚 BTC 的体现能：全网日耗能 / 日产出 BTC
    network_watts = hashrate_phps * watts_per_ph
    daily_energy_j = network_watts * SECONDS_PER_DAY
    epsilon_btc = daily_energy_j / raw.daily_block_reward_btc

    # ---------- 推理侧 ----------
    basket = [dict(b) for b in cfg["inference_basket"]]
    priced = []
    for b in basket:
        p = raw.model_prices_usd_per_token.get(b["id"])
        if p is None:
            if cfg["missing_model_policy"] == "fail":
                sys.exit(f"篮子模型 {b['id']} 在数据源中缺失（missing_model_policy=fail）")
            continue
        b["usd_per_token"] = p
        priced.append(b)
    if not priced:
        sys.exit("篮子中没有任何模型拿到报价，无法计算 R_A")

    wsum = sum(b["weight"] for b in priced)
    for b in priced:
        b["weight_norm"] = b["weight"] / wsum

    # ── 质量折算（升贴水法）─────────────────────────────────────────
    # 弃用说明：旧版用"价格÷基准价"作 quality_weight，代入 ρ_parity/ρ_market
    # 后价格项完全相消，导致 Ω ≡ ln(Λ) 恒成立，Ω 不携带独立信息。
    # 现改用来自价格以外的独立评测分（quality_score）作质量权重。
    ref = next((b for b in priced if b.get("quality_ref")), priced[0])
    ref_price = ref["usd_per_token"]

    # 只有当篮子中所有入选模型都提供了 quality_score 时才计算质量权重；
    # 否则一律置 1，且 Ω、ρ_parity 输出空值（待质量基准数据上线）。
    has_scores = all(b.get("quality_score") is not None for b in priced)
    if has_scores:
        ref_score = float(ref["quality_score"])
        for b in priced:
            b["quality_weight"] = float(b["quality_score"]) / ref_score
    else:
        for b in priced:
            b["quality_weight"] = 1.0

    for b in priced:
        # 每焦耳标准token产出 = 质量权重 / 单token能耗
        b["std_tok_per_j"] = b["quality_weight"] / b["j_per_token"]
        # 该模型每千瓦时毛收入（美元/kWh）= 单价(美元/tok) × 产量(tok/kWh)
        b["usd_per_kwh"] = b["usd_per_token"] * (J_PER_KWH / b["j_per_token"])
        # 该模型对 R_A 的贡献（美元/kWh）。恒等式 R_A = Σ contrib_R_A 即
        # 明细文件对主序列的复现关系，见 basket_detail.csv。
        b["contrib_R_A"] = b["weight_norm"] * b["usd_per_kwh"]
        # 置信带贡献（jᵢ 三档）：价格、权重不变，只替换 jᵢ。反向关系：
        # jᵢ 低档 → contrib_R_A_high（每度电收入更高）；jᵢ 高档 → contrib_R_A_low。
        # 模型缺三档配置时置 None，整条带随后统一放弃（见下方 has_tiers）。
        j_lo, j_hi = b.get("j_per_token_low"), b.get("j_per_token_high")
        b["contrib_R_A_high"] = (None if j_lo is None else
                                 b["weight_norm"] * b["usd_per_token"]
                                 * (J_PER_KWH / j_lo))
        b["contrib_R_A_low"] = (None if j_hi is None else
                                b["weight_norm"] * b["usd_per_token"]
                                * (J_PER_KWH / j_hi))
        # 第二源（厂商牌价）单价，仅作交叉验证列
        b["alt_usd_per_token"] = raw.alt_prices_usd_per_token.get(b["id"])

    # 篮子 R_A：按用量权重加权的每千瓦时收入（与 quality_weight 无关，恒可算）
    R_A = sum(b["contrib_R_A"] for b in priced)

    # ── 置信带（jᵢ 三档，docs/ji_source.md §9.3，P0 2026-09-01 起）─────────
    # 定义：逐模型把 jᵢ 替换为低/高档（价格、权重一律不变）后重新聚合，
    # 而非对加权均值 j̄ 整体缩放——三档表是逐模型的，逐模型替换才是其精确含义。
    # 只有全部入选模型都配置了三档时才发布置信带（与 quality_score 的处理一致）；
    # 主列 R_A / Lambda / Omega 与本节完全无关，缺三档时仅带列置空。
    has_tiers = all(b.get("j_per_token_low") is not None
                    and b.get("j_per_token_high") is not None for b in priced)
    if has_tiers:
        R_A_high = sum(b["contrib_R_A_high"] for b in priced)   # jᵢ 全取低档
        R_A_low = sum(b["contrib_R_A_low"] for b in priced)     # jᵢ 全取高档
        Lambda_low = R_A_low / R_M
        Lambda_high = R_A_high / R_M
    else:
        R_A_low = R_A_high = Lambda_low = Lambda_high = None
    # 注意：以下两个是"描述性均值"，仅供概览。由于逐模型聚合（先除后加）与
    # 均值相除（先加后除）不可交换，basket_price × 3.6e6 / basket_j ≠ R_A
    # 属于数学必然而非错误；R_A 的精确复现请用 basket_detail.csv 逐行求和。
    basket_price_mtok = sum(b["weight_norm"] * b["usd_per_token"] for b in priced) * 1e6
    basket_j_per_tok = sum(b["weight_norm"] * b["j_per_token"] for b in priced)

    # 第二源加权均价：只在有覆盖的模型上按同一权重归一化聚合
    alt_covered = [b for b in priced if b["alt_usd_per_token"] is not None]
    alt_coverage = f"{len(alt_covered)}/{len(priced)}"
    if alt_covered:
        aw = sum(b["weight_norm"] for b in alt_covered)
        basket_price_alt_mtok = sum(
            b["weight_norm"] / aw * b["alt_usd_per_token"] for b in alt_covered) * 1e6
    else:
        basket_price_alt_mtok = None
    # 篮子的每焦耳标准token产出（用于平价汇率）
    basket_std_tok_per_j = sum(b["weight_norm"] * b["std_tok_per_j"] for b in priced)

    # ---------- 跨市场汇率 ----------
    Lambda = R_A / R_M
    # 市场隐含汇率：币价 / 标准token市价（= 基准模型单价）——与质量分无关，始终可算
    rho_market = raw.btc_price_usd / ref_price
    if has_scores:
        # 焦耳平价汇率：一枚BTC的体现能全部用于推理，可产出多少"标准token"
        rho_parity = epsilon_btc * basket_std_tok_per_j
        Omega = math.log(rho_parity / rho_market)
    else:
        # 缺少 quality_score：Ω、ρ_parity 暂不可计算（输出空值）
        rho_parity = None
        Omega = None

    # Λ 链式接续：把不同篮子版本的 Λ 折算到统一基期，使序列衡量"变动"而非"篮子水平"
    version = cfg.get("basket_version", "v1")
    Lambda_chained = Lambda * chain_factor_for(version)

    detail = [{k: b.get(k) for k in
               ("id", "weight_norm", "usd_per_token", "alt_usd_per_token",
                "alt_price_id", "j_per_token", "j_per_token_low",
                "j_per_token_high", "quality_score", "quality_weight",
                "usd_per_kwh", "contrib_R_A", "contrib_R_A_low",
                "contrib_R_A_high")} for b in priced]

    return Snapshot(
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        btc_price_usd=raw.btc_price_usd,
        hashprice_usd_per_ph_day=hashprice,
        fleet_efficiency_j_per_th=eff,
        kwh_per_ph_day=kwh_per_ph_day,
        epsilon_btc_j=epsilon_btc,
        basket_price_usd_per_mtok=basket_price_mtok,
        basket_j_per_token=basket_j_per_tok,
        basket_price_alt_usd_per_mtok=basket_price_alt_mtok,
        alt_coverage=alt_coverage,
        basket_detail=detail,
        R_M=R_M, R_A=R_A, Lambda=Lambda,
        rho_parity_tok_per_btc=rho_parity,
        rho_market_tok_per_btc=rho_market,
        Omega=Omega,
        source=raw.source,
        basket_version=version,
        Lambda_chained=Lambda_chained,
        R_A_low=R_A_low, R_A_high=R_A_high,
        Lambda_low=Lambda_low, Lambda_high=Lambda_high,
    )


# --------------------------------------------------------------------------
# 输出层
# --------------------------------------------------------------------------
CSV_FIELDS = ["date", "btc_price_usd", "hashprice_usd_per_ph_day",
              "fleet_efficiency_j_per_th", "epsilon_btc_gwh",
              "basket_price_usd_per_mtok", "basket_j_per_token",
              "basket_price_alt_usd_per_mtok", "alt_coverage",
              "R_M", "R_A", "Lambda", "Omega",
              "rho_parity_tok_per_btc", "rho_market_tok_per_btc", "source",
              "basket_version", "Lambda_chained",
              # 置信带四列（P0，2026-09-01 起）：jᵢ 三档口径的 Λ 区间。
              # 老序列行由 restval="" 自动补空；自 2026-09-01（含）起新行有值。
              "R_A_low", "R_A_high", "Lambda_low", "Lambda_high"]

# 明细文件字段（basket_detail.csv）：每天每个入选模型一行。
# 复现关系：当日 R_A = 该日全部行 contrib_R_A 之和（数值哨兵会自动核验）；
# 同理 R_A_low/high = Σ contrib_R_A_low/high（数值哨兵一并核验）。
DETAIL_FIELDS = ["date", "model_id", "weight_norm",
                 "usd_per_mtok", "usd_per_mtok_alt", "alt_price_id",
                 "j_per_token", "j_per_token_low", "j_per_token_high",
                 "quality_score", "quality_weight",
                 "usd_per_kwh", "contrib_R_A", "contrib_R_A_low",
                 "contrib_R_A_high", "basket_version", "source"]


def append_csv(snap: Snapshot, path: str):
    """按日期去重追加：同一天重复运行覆盖当日行，保证日频序列干净。"""
    rows = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["date"] != snap.date]
    rows.append({
        "date": snap.date,
        "btc_price_usd": f"{snap.btc_price_usd:.2f}",
        "hashprice_usd_per_ph_day": f"{snap.hashprice_usd_per_ph_day:.4f}",
        "fleet_efficiency_j_per_th": f"{snap.fleet_efficiency_j_per_th:.1f}",
        "epsilon_btc_gwh": f"{snap.epsilon_btc_j / 3.6e12:.4f}",
        "basket_price_usd_per_mtok": f"{snap.basket_price_usd_per_mtok:.4f}",
        "basket_j_per_token": f"{snap.basket_j_per_token:.3f}",
        "basket_price_alt_usd_per_mtok":
            "" if snap.basket_price_alt_usd_per_mtok is None
            else f"{snap.basket_price_alt_usd_per_mtok:.4f}",
        "alt_coverage": snap.alt_coverage,
        "R_M": f"{snap.R_M:.6f}",
        "R_A": f"{snap.R_A:.4f}",
        "Lambda": f"{snap.Lambda:.2f}",
        "Omega": "" if snap.Omega is None else f"{snap.Omega:.4f}",
        "rho_parity_tok_per_btc": "" if snap.rho_parity_tok_per_btc is None
                                   else f"{snap.rho_parity_tok_per_btc:.4e}",
        "rho_market_tok_per_btc": f"{snap.rho_market_tok_per_btc:.4e}",
        "source": snap.source,
        "basket_version": snap.basket_version,
        "Lambda_chained": f"{snap.Lambda_chained:.2f}",
        "R_A_low": "" if snap.R_A_low is None else f"{snap.R_A_low:.4f}",
        "R_A_high": "" if snap.R_A_high is None else f"{snap.R_A_high:.4f}",
        "Lambda_low": "" if snap.Lambda_low is None else f"{snap.Lambda_low:.2f}",
        "Lambda_high": "" if snap.Lambda_high is None else f"{snap.Lambda_high:.2f}",
    })
    rows.sort(key=lambda r: r["date"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        # restval=""：老序列的行没有新增列（如第二源两列），补空值而不是报错，
        # 保证加列后向后兼容——这是 CPI 式"换口径不断序列"的最小实现。
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, restval="", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def append_detail_csv(snap: Snapshot, path: str):
    """把当日各模型明细追加到 basket_detail.csv（同日重跑覆盖当日全部行）。

    这是 R_A 的可复现层：任何人拿这个文件按行求和 contrib_R_A 即可精确
    重算主序列的 R_A，不必信任 basket_price / basket_j 两个描述性均值。
    同时它逐日留存了篮子成分、权重、质量分与两个价格源的截面——享乐回归、
    敏感性分析、换篮审计都以此为原料。
    """
    rows = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["date"] != snap.date]
    for b in snap.basket_detail:
        rows.append({
            "date": snap.date,
            "model_id": b["id"],
            "weight_norm": f"{b['weight_norm']:.4f}",
            "usd_per_mtok": f"{b['usd_per_token'] * 1e6:.4f}",
            "usd_per_mtok_alt":
                "" if b.get("alt_usd_per_token") is None
                else f"{b['alt_usd_per_token'] * 1e6:.4f}",
            "alt_price_id": b.get("alt_price_id") or "",
            "j_per_token": f"{b['j_per_token']:.3f}",
            "j_per_token_low":
                "" if b.get("j_per_token_low") is None
                else f"{b['j_per_token_low']:.3f}",
            "j_per_token_high":
                "" if b.get("j_per_token_high") is None
                else f"{b['j_per_token_high']:.3f}",
            "quality_score":
                "" if b.get("quality_score") is None else f"{b['quality_score']}",
            "quality_weight": f"{b['quality_weight']:.4f}",
            "usd_per_kwh": f"{b['usd_per_kwh']:.4f}",
            "contrib_R_A": f"{b['contrib_R_A']:.6f}",
            "contrib_R_A_low":
                "" if b.get("contrib_R_A_low") is None
                else f"{b['contrib_R_A_low']:.6f}",
            "contrib_R_A_high":
                "" if b.get("contrib_R_A_high") is None
                else f"{b['contrib_R_A_high']:.6f}",
            "basket_version": snap.basket_version,
            "source": snap.source,
        })
    rows.sort(key=lambda r: (r["date"], r["model_id"]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=DETAIL_FIELDS, restval="", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def print_report(snap: Snapshot):
    line = "─" * 62
    print(line)
    print(f"Token 能量平价指数  {snap.date}   (source: {snap.source})")
    print(line)
    print("【挖矿侧】")
    print(f"  BTC 价格               {snap.btc_price_usd:>14,.0f}  美元")
    print(f"  hashprice              {snap.hashprice_usd_per_ph_day:>14.2f}  美元/PH/s/天")
    print(f"  队列能效（配置）        {snap.fleet_efficiency_j_per_th:>14.1f}  J/TH")
    print(f"  1 PH/s 日耗电          {snap.kwh_per_ph_day:>14.1f}  kWh")
    print(f"  ε_BTC 单枚体现能        {snap.epsilon_btc_j/3.6e12:>14.3f}  GWh/枚")
    print("【推理侧】（篮子构成见下）")
    print(f"  篮子均价               {snap.basket_price_usd_per_mtok:>14.3f}  美元/百万token")
    if snap.basket_price_alt_usd_per_mtok is not None:
        print(f"  篮子均价·第二源牌价    {snap.basket_price_alt_usd_per_mtok:>14.3f}"
              f"  美元/百万token（覆盖 {snap.alt_coverage}，仅交叉验证）")
    print(f"  篮子均能耗（配置）      {snap.basket_j_per_token:>14.2f}  J/token")
    for b in snap.basket_detail:
        alt = b.get("alt_usd_per_token")
        alt_str = "  alt=--" if alt is None else f"  alt=${alt*1e6:.2f}/M"
        print(f"    - {b['id']:<34} w={b['weight_norm']:.2f}  "
              f"${b['usd_per_token']*1e6:>8.3f}/M{alt_str}  q={b['quality_weight']:.2f}  "
              f"{b['usd_per_kwh']:.2f} $/kWh")
    print("【四条指数】")
    print(f"  R_M   挖矿每度电毛收入   {snap.R_M:>12.4f}  美元/kWh")
    print(f"  R_A   推理每度电毛收入   {snap.R_A:>12.2f}  美元/kWh")
    print(f"  Λ     能量套利比        {snap.Lambda:>12.1f}  （毛收入口径，非利润；链式 {snap.basket_version} 系数×Λ={snap.Lambda_chained:.1f}）")
    if snap.Lambda_low is not None:
        print(f"  Λ 带  jᵢ三档置信带     [{snap.Lambda_low:>6.1f}, {snap.Lambda_high:.1f}]"
              f"  （R_A ∈ [{snap.R_A_low:.2f}, {snap.R_A_high:.2f}] $/kWh；"
              f"jᵢ 低/高档逐模型替换，主列不受影响）")
    if snap.rho_parity_tok_per_btc is None:
        print("  ρ*    焦耳平价汇率        (待质量基准数据上线)")
    else:
        print(f"  ρ*    焦耳平价汇率      {snap.rho_parity_tok_per_btc:>12.3e}  标准token/BTC")
    print(f"  ρ     市场隐含汇率      {snap.rho_market_tok_per_btc:>12.3e}  标准token/BTC")
    if snap.Omega is None:
        print("  Ω     平价偏离指数        (待质量基准数据上线)")
    else:
        print(f"  Ω     平价偏离指数      {snap.Omega:>12.3f}  = ln(ρ*/ρ)")
    print(line)


def plot_series(csv_path: str, png_path: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    # 尽力找一个中文字体并真正启用它；找不到就退回英文标签
    zh = False
    preferred = ("Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans CJK JP",
                 "WenQuanYi Zen Hei", "PingFang SC", "SimHei")
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            plt.rcParams["font.family"] = [name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            zh = True
            break

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 1:
        print("序列为空，跳过绘图")
        return
    dates = [r["date"] for r in rows]
    # Omega / rho_parity 可能为空（缺少 quality_score 时），用 None 容错形成断点
    def _f(v):
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
    series = {k: [_f(r.get(k, "")) for r in rows]
              for k in ("R_M", "R_A", "Lambda", "Omega")}

    labels = {
        "R_M": ("挖矿每度电毛收入 R_M ($/kWh)" if zh else "Mining revenue R_M ($/kWh)"),
        "R_A": ("推理每度电毛收入 R_A ($/kWh)" if zh else "Inference revenue R_A ($/kWh)"),
        "Lambda": ("能量套利比 Λ（链式接续）" if zh else "Energy arbitrage ratio Λ (chain-linked)"),
        "Omega": ("平价偏离指数 Ω" if zh else "Parity deviation Ω"),
    }
    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
    for ax, key in zip(axes, ("R_M", "R_A", "Lambda", "Omega")):
        vals = series[key]
        # 全空（如 Ω 待质量基准）则只画标题不画线，避免空图报错
        if any(v is not None for v in vals):
            ax.plot(dates, vals, marker="o", linewidth=1.5)
        else:
            ax.text(0.5, 0.5, "待质量基准数据" if zh else "Pending quality benchmark",
                    ha="center", va="center", transform=ax.transAxes,
                    color="#999", fontsize=11)
        ax.set_title(labels[key], fontsize=11)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("date")
    step = max(1, len(dates) // 12)
    axes[-1].set_xticks(dates[::step])
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(png_path, dpi=150)
    print(f"图已保存：{png_path}")


# --------------------------------------------------------------------------
def sanity_check(snap: Snapshot, csv_path: str):
    """数值哨兵：越界只打印 ::warning::（GitHub Actions 会高亮成黄色），
    绝不抛错、绝不中断任务。返回 (warnings, skip_write)。

    skip_write=True 表示日期与 CSV 末行重复，应跳过本次写入。
    """
    warns = []
    skip_write = False

    if not (0.005 <= snap.R_M <= 0.5):
        warns.append(f"R_M={snap.R_M:.4f} 超出合理区间 [0.005, 0.5] $/kWh")
    if not (0.5 <= snap.R_A <= 200):
        warns.append(f"R_A={snap.R_A:.2f} 超出合理区间 [0.5, 200] $/kWh")

    # 复现性自检：明细贡献求和必须等于 R_A（浮点容差 1e-9 相对误差）。
    # 这是 basket_detail.csv 对主序列的复现承诺，写入前先自己验一遍。
    # 置信带两列同样核验（Σ contrib_R_A_low/high = R_A_low/high）。
    contrib_sum = sum(b["contrib_R_A"] for b in snap.basket_detail)
    if snap.R_A > 0 and abs(contrib_sum - snap.R_A) / snap.R_A > 1e-9:
        warns.append(f"复现性自检失败：Σcontrib={contrib_sum:.6f} ≠ R_A={snap.R_A:.6f}")
    if snap.R_A_low is not None:
        for col, target in (("contrib_R_A_low", snap.R_A_low),
                            ("contrib_R_A_high", snap.R_A_high)):
            csum = sum(b[col] for b in snap.basket_detail
                       if b.get(col) is not None)
            if target > 0 and abs(csum - target) / target > 1e-9:
                warns.append(f"置信带复现性自检失败：Σ{col}={csum:.6f} ≠ "
                             f"{target:.6f}")

    # 置信带哨兵：中档点值必须落在区间内。数学上必然成立（逐模型单调），
    # 违反即说明三档 jᵢ 配置写反了档位，须在写入前发现。
    if snap.Lambda_low is not None:
        if not (snap.Lambda_low <= snap.Lambda <= snap.Lambda_high):
            warns.append(f"置信带哨兵失败：Λ={snap.Lambda:.1f} 不在 "
                         f"[{snap.Lambda_low:.1f}, {snap.Lambda_high:.1f}] 内，"
                         f"请检查三档 jᵢ 配置（低档应 < 中档 < 高档）")

    # 读取 CSV 末行，用于日期去重与 Λ 变动检查
    last_date, last_lambda = None, None
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if rows:
            last_date = rows[-1].get("date")
            lam_str = rows[-1].get("Lambda")
            if lam_str:
                try:
                    last_lambda = float(lam_str)
                except ValueError:
                    last_lambda = None

    if last_date == snap.date:
        warns.append(f"日期 {snap.date} 与 CSV 末行重复，跳过写入")
        skip_write = True
    if last_lambda and last_lambda > 0:
        change = abs(snap.Lambda - last_lambda) / last_lambda
        if change > 0.5:
            warns.append(f"Λ={snap.Lambda:.1f} 相对上一行 {last_lambda:.1f} "
                         f"变动 {change*100:.0f}%，超 ±50%")

    for w in warns:
        print(f"::warning::{w}")
    return warns, skip_write


def main():
    ap = argparse.ArgumentParser(description="Token 能量平价指数")
    ap.add_argument("--offline", action="store_true",
                    help="使用 sample_data.json 离线验算，不联网")
    ap.add_argument("--sample", default="sample_data.json",
                    help="离线模式的数据文件路径")
    ap.add_argument("--config", default=None, help="自定义配置 JSON（覆盖默认值）")
    ap.add_argument("--plot", action="store_true", help="计算后绘制历史序列")
    ap.add_argument("--no-csv", action="store_true", help="只打印，不写入 CSV")
    ap.add_argument("--dry-run", action="store_true",
                    help="只计算打印不写 CSV（换篮子时新旧对比用）")
    args = ap.parse_args()

    cfg = dict(DEFAULT_CONFIG)
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg.update(json.load(f))

    raw = fetch_offline(args.sample) if args.offline else fetch_live(cfg)
    snap = compute(raw, cfg)
    print_report(snap)

    # 原始数据归档：只要在线抓到了就存（含 --dry-run），归档的是观测不是计算，
    # 与"是否写序列"是两回事。同日重跑覆盖同名文件。
    archive_path = write_raw_archive(raw, cfg)
    if archive_path:
        print(f"原始响应已归档：{archive_path}")

    # 数值哨兵：在写 CSV 前运行（--dry-run 也运行，仅作告警提示）
    _, skip_write = sanity_check(snap, cfg["csv_path"])

    if not args.no_csv and not args.dry_run and not skip_write:
        append_csv(snap, cfg["csv_path"])
        append_detail_csv(snap, cfg["detail_csv_path"])
        print(f"已写入序列：{cfg['csv_path']}；明细：{cfg['detail_csv_path']}")
    elif skip_write:
        print(f"因日期重复，未写入 {cfg['csv_path']}")
    if args.plot:
        plot_series(cfg["csv_path"], cfg["plot_path"])


if __name__ == "__main__":
    main()
