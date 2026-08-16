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
    # j_per_token   该模型输出 token 的全栈能耗估计（焦耳/输出 token，含数据中心 PUE）
    #               来源：Epoch AI、厂商披露、学术测量。粗模型的量级在 0.5–5 J/token。
    # quality_ref   是否作为质量基准模型（恰好一个为 true）
    "inference_basket": [
        {"id": "anthropic/claude-sonnet-5",       "weight": 0.30, "j_per_token": 3.0,
         "quality_ref": True},
        {"id": "openai/gpt-5.5",                  "weight": 0.25, "j_per_token": 3.0},
        {"id": "google/gemini-3.7-flash",         "weight": 0.25, "j_per_token": 1.0},
        {"id": "deepseek/deepseek-v4-pro",        "weight": 0.20, "j_per_token": 1.5},
    ],
    # 篮子里某个模型在 OpenRouter 下架时的策略："skip"（剔除并重新归一化）或 "fail"
    "missing_model_policy": "skip",

    # ---------------- 输出 ----------------
    "csv_path": "parity_series.csv",
    "plot_path": "parity_index.png",

    # 数据源 URL（一般不用改）
    "urls": {
        "btc_price": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        "hashrate": "https://mempool.space/api/v1/mining/hashrate/3d",
        "reward_stats": "https://mempool.space/api/v1/mining/reward-stats/144",
        "openrouter_models": "https://openrouter.ai/api/v1/models",
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
    source: str = "live"
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


def _get_json(url: str, timeout: int):
    resp = requests.get(url, timeout=timeout,
                        headers={"User-Agent": "token-parity-index/0.1"})
    resp.raise_for_status()
    return resp.json()


def fetch_live(cfg: dict) -> RawData:
    if requests is None:
        sys.exit("需要 requests 库才能在线抓取：pip install requests")
    urls, t = cfg["urls"], cfg["http_timeout_seconds"]

    # 1) 比特币价格
    price = float(_get_json(urls["btc_price"], t)["bitcoin"]["usd"])

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

    return RawData(
        btc_price_usd=price,
        network_hashrate_hps=hashrate_hps,
        daily_block_reward_btc=daily_reward_btc,
        model_prices_usd_per_token=basket_prices,
    )


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
    basket_detail: list
    # 四条指数
    R_M: float                           # 美元/kWh
    R_A: float                           # 美元/kWh
    Lambda: float                        # R_A / R_M
    rho_parity_tok_per_btc: float        # 焦耳平价汇率
    rho_market_tok_per_btc: float        # 市场隐含汇率
    Omega: float                         # ln(rho_parity / rho_market)
    source: str


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

    # 质量折算（升贴水法）：以基准模型价格为 1，其他模型的质量权重 = 其价格/基准价。
    # 一个"标准token当量"= 原始token × 质量权重。于是：
    #   标准token的单价 对所有模型都等于基准价（构造使然），
    #   但每个模型"每焦耳产出的标准token数"不同——质量调整落在数量侧，不在价格侧。
    ref = next((b for b in priced if b.get("quality_ref")), priced[0])
    ref_price = ref["usd_per_token"]
    for b in priced:
        b["quality_weight"] = b["usd_per_token"] / ref_price
        # 每焦耳标准token产出 = 质量权重 / 单token能耗
        b["std_tok_per_j"] = b["quality_weight"] / b["j_per_token"]
        # 该模型每千瓦时毛收入（美元/kWh）= 单价(美元/tok) × 产量(tok/kWh)
        b["usd_per_kwh"] = b["usd_per_token"] * (J_PER_KWH / b["j_per_token"])

    # 篮子 R_A：按用量权重加权的每千瓦时收入
    R_A = sum(b["weight_norm"] * b["usd_per_kwh"] for b in priced)
    basket_price_mtok = sum(b["weight_norm"] * b["usd_per_token"] for b in priced) * 1e6
    basket_j_per_tok = sum(b["weight_norm"] * b["j_per_token"] for b in priced)
    # 篮子的每焦耳标准token产出（用于平价汇率）
    basket_std_tok_per_j = sum(b["weight_norm"] * b["std_tok_per_j"] for b in priced)

    # ---------- 跨市场汇率 ----------
    Lambda = R_A / R_M
    # 焦耳平价汇率：一枚BTC的体现能全部用于推理，可产出多少"标准token"
    rho_parity = epsilon_btc * basket_std_tok_per_j
    # 市场隐含汇率：币价 / 标准token市价（= 基准模型单价）
    rho_market = raw.btc_price_usd / ref_price
    Omega = math.log(rho_parity / rho_market)

    detail = [{k: b[k] for k in
               ("id", "weight_norm", "usd_per_token", "j_per_token",
                "quality_weight", "usd_per_kwh")} for b in priced]

    return Snapshot(
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        btc_price_usd=raw.btc_price_usd,
        hashprice_usd_per_ph_day=hashprice,
        fleet_efficiency_j_per_th=eff,
        kwh_per_ph_day=kwh_per_ph_day,
        epsilon_btc_j=epsilon_btc,
        basket_price_usd_per_mtok=basket_price_mtok,
        basket_j_per_token=basket_j_per_tok,
        basket_detail=detail,
        R_M=R_M, R_A=R_A, Lambda=Lambda,
        rho_parity_tok_per_btc=rho_parity,
        rho_market_tok_per_btc=rho_market,
        Omega=Omega,
        source=raw.source,
    )


# --------------------------------------------------------------------------
# 输出层
# --------------------------------------------------------------------------
CSV_FIELDS = ["date", "btc_price_usd", "hashprice_usd_per_ph_day",
              "fleet_efficiency_j_per_th", "epsilon_btc_gwh",
              "basket_price_usd_per_mtok", "basket_j_per_token",
              "R_M", "R_A", "Lambda", "Omega",
              "rho_parity_tok_per_btc", "rho_market_tok_per_btc", "source"]


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
        "R_M": f"{snap.R_M:.6f}",
        "R_A": f"{snap.R_A:.4f}",
        "Lambda": f"{snap.Lambda:.2f}",
        "Omega": f"{snap.Omega:.4f}",
        "rho_parity_tok_per_btc": f"{snap.rho_parity_tok_per_btc:.4e}",
        "rho_market_tok_per_btc": f"{snap.rho_market_tok_per_btc:.4e}",
        "source": snap.source,
    })
    rows.sort(key=lambda r: r["date"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
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
    print(f"  篮子均能耗（配置）      {snap.basket_j_per_token:>14.2f}  J/token")
    for b in snap.basket_detail:
        print(f"    - {b['id']:<34} w={b['weight_norm']:.2f}  "
              f"${b['usd_per_token']*1e6:>8.3f}/M  q={b['quality_weight']:.2f}  "
              f"{b['usd_per_kwh']:.2f} $/kWh")
    print("【四条指数】")
    print(f"  R_M   挖矿每度电毛收入   {snap.R_M:>12.4f}  美元/kWh")
    print(f"  R_A   推理每度电毛收入   {snap.R_A:>12.2f}  美元/kWh")
    print(f"  Λ     能量套利比        {snap.Lambda:>12.1f}  （毛收入口径，非利润）")
    print(f"  ρ*    焦耳平价汇率      {snap.rho_parity_tok_per_btc:>12.3e}  标准token/BTC")
    print(f"  ρ     市场隐含汇率      {snap.rho_market_tok_per_btc:>12.3e}  标准token/BTC")
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
    series = {k: [float(r[k]) for r in rows] for k in ("R_M", "R_A", "Lambda", "Omega")}

    labels = {
        "R_M": ("挖矿每度电毛收入 R_M ($/kWh)" if zh else "Mining revenue R_M ($/kWh)"),
        "R_A": ("推理每度电毛收入 R_A ($/kWh)" if zh else "Inference revenue R_A ($/kWh)"),
        "Lambda": ("能量套利比 Λ" if zh else "Energy arbitrage ratio Λ"),
        "Omega": ("平价偏离指数 Ω" if zh else "Parity deviation Ω"),
    }
    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
    for ax, key in zip(axes, ("R_M", "R_A", "Lambda", "Omega")):
        ax.plot(dates, series[key], marker="o", linewidth=1.5)
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
def main():
    ap = argparse.ArgumentParser(description="Token 能量平价指数")
    ap.add_argument("--offline", action="store_true",
                    help="使用 sample_data.json 离线验算，不联网")
    ap.add_argument("--sample", default="sample_data.json",
                    help="离线模式的数据文件路径")
    ap.add_argument("--config", default=None, help="自定义配置 JSON（覆盖默认值）")
    ap.add_argument("--plot", action="store_true", help="计算后绘制历史序列")
    ap.add_argument("--no-csv", action="store_true", help="只打印，不写入 CSV")
    args = ap.parse_args()

    cfg = dict(DEFAULT_CONFIG)
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg.update(json.load(f))

    raw = fetch_offline(args.sample) if args.offline else fetch_live(cfg)
    snap = compute(raw, cfg)
    print_report(snap)

    if not args.no_csv:
        append_csv(snap, cfg["csv_path"])
        print(f"已写入序列：{cfg['csv_path']}")
    if args.plot:
        plot_series(cfg["csv_path"], cfg["plot_path"])


if __name__ == "__main__":
    main()
