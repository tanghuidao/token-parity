#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RM（挖矿侧）历史回填脚本 —— O1a
================================

把 R_M（挖矿每千瓦时毛收入）回填到 2010-07（GPU 时代）起，月频，输出独立
序列 docs/rm_history.csv。对应路线图 O1a（历史回填·挖矿侧）；RA 侧的
"历史前沿篮子"（O1b）另立项，不在本脚本范围。

数据源（全部公开、无需密钥，均为日频）：
  - BTC 市场价:   blockchain.info /charts/market-price    （2009-01 起）
  - 全网算力:     blockchain.info /charts/hash-rate        （TH/s，2009 起）
  - 日手续费:     blockchain.info /charts/transaction-fees （BTC）
缓解单源依赖：与主序列（CoinGecko/mempool.space）在重叠期 2026-08-16 起做
交叉验证，偏差阈值 5%（见脚本末尾验证报告）。

计算公式与 parity_index.py 完全一致：
  日奖励(BTC)   = 144 块 × 当时补贴 + 日手续费(BTC)      （区块数按 144/天近似）
  日收入(USD)   = 日奖励 × BTC 价格
  日耗电(kWh)   = 算力(TH/s) × 队列能效(J/TH) × 86400 / 3.6e6
  R_M($/kWh)    = 日收入 ÷ 日耗电
  ε_BTC(GWh/枚) = 月耗电(GWh) ÷ 月产币量(BTC)

队列能效（J/TH）是政策内参数：分时期人工设定（EFFICIENCY_HISTORY），
初稿取值依据见 docs/efficiency_history_source.md（草稿，待溯源定稿）。
能效变更只进 changelog、不改版本号；已发布行永不回溯。

用法：
  python backfill_rm.py            # 抓取全历史并重建 docs/rm_history.csv
  python backfill_rm.py --no-csv   # 只打印验证报告，不写文件

治理（与 docs/lambda_prime_series.csv 同规格）：
  - 独立序列，不进入 parity_series.csv、不进大屏、不改 parity_index.py
  - source 列 = backfill_v1；能效表修订时递增为 backfill_v2 并登记 changelog
"""

import argparse
import csv
import json
import os
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    import sys
    sys.exit("需要 requests 库：pip install requests")

# --------------------------------------------------------------------------
# 常数与政策参数（全部显式，便于审计）
# --------------------------------------------------------------------------
J_PER_KWH = 3.6e6
SECONDS_PER_DAY = 86400
BLOCKS_PER_DAY = 144          # 比特币目标出块率（与主序列同口径的近似）

START_DATE = "2010-07-01"     # 回填起点：GPU 时代（有可靠交易所价格）

BASE_URL = "https://api.blockchain.info/charts/{chart}"
CHARTS = {
    "market_price": "market-price",        # USD，日频
    "hashrate": "hash-rate",               # TH/s，日频
    "fees_btc": "transaction-fees",        # BTC，日频
}
HTTP_TIMEOUT = 120

# 区块补贴时间表（减半历史，UTC 日期）
HALVINGS = [
    ("2009-01-03", 50.0),
    ("2012-11-28", 25.0),
    ("2016-07-09", 12.5),
    ("2020-05-11", 6.25),
    ("2024-04-19", 3.125),
    # 下一次减半预计 2028-04；届时须在此追加并登记 changelog
]

# 队列能效历史（J/TH）——政策内参数，初稿 v0.1。
# 逐段生效（段起始日起适用）；段内代表机型与取值依据见
# docs/efficiency_history_source.md。**全表为"全网队列平均"估计，
# 滞后于当年最新机型 1–3 年；GPU/FPGA 时代（2010–2012）不确定度达数量级。**
EFFICIENCY_HISTORY = [
    # (段起始日, J/TH, 代表机型注记)
    ("2010-07-01", 1_000_000, "GPU：ATI 5870 ≈ 200W/0.25GH/s（~800k J/TH），队列含大量更旧显卡"),
    ("2011-01-01",   700_000, "GPU：5870/5970 主力（新机型 ~430k J/TH），队列均值更高"),
    ("2012-01-01",   200_000, "GPU→FPGA→初代 ASIC 过渡年，队列构成剧变，不确定度大"),
    ("2013-01-01",    30_000, "ASIC 元年·Q1：Avalon batch1/ASICMiner（~10k J/TH 新机）"),
    ("2013-04-01",     8_000, "ASIC 元年·Q2：Bitfury/ASICMiner 阵列铺开"),
    ("2013-07-01",     2_500, "ASIC 元年·Q3：28nm 量产"),
    ("2013-10-01",       900, "ASIC 元年·Q4：Antminer S1（~400 J/TH 新机）上市"),
    ("2014-01-01",       800, "S2/S3 一代（S3 新机 ~750 J/TH）"),
    ("2015-01-01",       500, "S5（新机 ~510 J/TH）/S7（~265 J/TH）换代"),
    ("2016-01-01",       200, "S9（16nm，新机 ~100 J/TH）导入，队列仍多 S7"),
    ("2017-01-01",       100, "S9 大规模部署成为主力"),
    ("2018-01-01",        70, "S9 存量主力 + S11/T15 导入"),
    ("2019-01-01",        50, "S17（新机 ~40 J/TH）导入"),
    ("2020-01-01",        40, "S19（新机 ~34 J/TH）导入"),
    ("2021-01-01",        30, "S19 存量主力"),
    ("2022-01-01",        25, "S19 XP（新机 ~21.5 J/TH）导入"),
    ("2023-01-01",        22, "S19 XP 存量扩大"),
    ("2024-01-01",        21, "S21（新机 ~17.5 J/TH）导入"),
    ("2025-01-01",        20, "队列收敛"),
    ("2026-01-01",        20, "与主序列现行假设一致（无缝衔接）"),
]

OUTPUT_CSV = os.path.join("docs", "rm_history.csv")
RAW_ARCHIVE_DIR = "raw_backfill"

# 主序列（CoinGecko/mempool.space 口径）重叠期 R_M 均值，用于交叉验证。
# 主序列自 2026-08-16 日起日更；该值取 2026-08-16..31 的 R_M 均值。
MAIN_SERIES_OVERLAP = {
    "start": "2026-08-16", "end": "2026-08-31",
    "expected_rm_mean": None,   # 运行时从 docs/parity_series.csv 读取
}


# --------------------------------------------------------------------------
# 工具函数
# --------------------------------------------------------------------------
def fetch_chart(chart: str) -> list:
    """抓取 blockchain.info 单个 chart 的全历史日频序列。

    返回 [(date_str 'YYYY-MM-DD', value float), ...]，按日期升序。
    sampled=false 取全量（不抽样），单 chart 全历史约 6000 点。
    """
    url = BASE_URL.format(chart=chart)
    resp = requests.get(url, params={"format": "json", "sampled": "false",
                                     "timespan": "all"},
                        timeout=HTTP_TIMEOUT,
                        headers={"User-Agent": "token-parity-backfill/0.1"})
    resp.raise_for_status()
    data = resp.json()
    out = []
    for p in data.get("values", []):
        day = datetime.fromtimestamp(p["x"], tz=timezone.utc).strftime("%Y-%m-%d")
        out.append((day, float(p["y"])))
    out.sort(key=lambda t: t[0])
    return out, resp.json()


def subsidy_on(day: str) -> float:
    """某日适用的区块补贴（BTC/块），按减半时间表。"""
    s = HALVINGS[0][1]
    for d, v in HALVINGS:
        if day >= d:
            s = v
    return s


def efficiency_on(day: str) -> float:
    """某日适用的队列能效（J/TH），按 EFFICIENCY_HISTORY 分段表。"""
    val, best = None, None
    for d, v, _note in EFFICIENCY_HISTORY:
        if day >= d:
            val = v
    if val is None:
        val = EFFICIENCY_HISTORY[0][1]
    return val


# 数据质量分层（诚实披露，随行输出）：
#   low      2010-07..2012-12：GPU/FPGA 时代三重不确定（价格仅 Mt.Gox 早期、
#            算力为估计值、能效不确定度达数量级），仅作量级参考
#   medium   2013-01 起：ASIC 时代，价格/算力可靠；能效为初稿政策参数
#            （溯源定稿前不确定度约 ±30–50%）
#   partial  末月为不完整月（数据源截至 2026-08-30，主序列重叠期已交叉验证）
def quality_on(month: str) -> str:
    if month <= "2012-12":
        return "low"
    return "medium"


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="RM 历史回填（O1a）")
    ap.add_argument("--no-csv", action="store_true", help="只打印验证报告，不写文件")
    args = ap.parse_args()

    print("抓取 blockchain.info 全历史日频序列（3 个 chart）……")
    series = {}
    raw_payloads = {}
    for name, chart in CHARTS.items():
        pts, payload = fetch_chart(chart)
        series[name] = dict(pts)
        raw_payloads[name] = payload
        print(f"  {name:<14} {len(pts):>5} 天  ({pts[0][0]} → {pts[-1][0]})")

    # 归档原始响应（数据抢救层，与主序列 raw/ 同哲学）
    os.makedirs(RAW_ARCHIVE_DIR, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_path = os.path.join(RAW_ARCHIVE_DIR, f"{today}.json")
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "charts": list(CHARTS.values()),
                   "payloads": raw_payloads}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"原始响应已归档：{archive_path}")

    # 三序列取交集日期，按天合成
    common_days = sorted(set(series["market_price"]) &
                         set(series["hashrate"]) & set(series["fees_btc"]))
    common_days = [d for d in common_days if d >= START_DATE]
    print(f"有效回填区间：{common_days[0]} → {common_days[-1]}（{len(common_days)} 天）")

    daily = []  # 逐日中间量（全部显式保留，便于核对）
    for d in common_days:
        price = series["market_price"][d]
        hashrate_th = series["hashrate"][d]          # TH/s
        fees_btc = series["fees_btc"][d]
        eff = efficiency_on(d)
        reward_btc = BLOCKS_PER_DAY * subsidy_on(d) + fees_btc
        revenue_usd = reward_btc * price
        # 全网功率(W) = 算力(TH/s) × J/TH（1 J/TH = 1 W/(TH/s)）
        network_watts = hashrate_th * eff
        energy_kwh = network_watts * SECONDS_PER_DAY / J_PER_KWH
        r_m = revenue_usd / energy_kwh if energy_kwh > 0 else 0.0
        daily.append({"date": d, "price": price, "hashrate_th": hashrate_th,
                      "eff": eff, "fees_btc": fees_btc, "reward_btc": reward_btc,
                      "revenue_usd": revenue_usd, "energy_kwh": energy_kwh,
                      "r_m": r_m})

    # ---- 月度聚合：Σ收入 / Σ耗电（比值口径，非均值口径）----
    months = {}
    for row in daily:
        m = row["date"][:7]                     # YYYY-MM
        months.setdefault(m, []).append(row)

    out_rows = []
    for m in sorted(months):
        rows = months[m]
        n = len(rows)
        tot_rev = sum(r["revenue_usd"] for r in rows)
        tot_energy = sum(r["energy_kwh"] for r in rows)
        tot_reward = sum(r["reward_btc"] for r in rows)
        tot_hash_seconds = sum(r["hashrate_th"] for r in rows) * SECONDS_PER_DAY
        out_rows.append({
            "date": m,
            "days": n,
            "btc_price_usd_avg": f"{sum(r['price'] for r in rows)/n:.2f}",
            "hashrate_th_s_avg": f"{sum(r['hashrate_th'] for r in rows)/n:.1f}",
            # 有效能效 = 月耗电(J) ÷ 月总算力·秒(TH)——段界跨越月自动加权
            "fleet_efficiency_j_per_th": f"{tot_energy*J_PER_KWH/tot_hash_seconds:.1f}",
            "reward_btc_per_day_avg": f"{tot_reward/n:.2f}",
            "fees_share_pct": f"{sum(r['fees_btc'] for r in rows)/tot_reward*100:.2f}",
            "R_M_usd_per_kwh": f"{tot_rev/tot_energy:.6f}",
            "epsilon_btc_gwh": f"{tot_energy/1e6/tot_reward:.4f}",
            "quality": quality_on(m),
            "source": "backfill_v1",
        })

    # 末月为不完整月（数据源截止日所致）：在 quality 上追加标记
    if out_rows and out_rows[-1]["days"] < 28:
        out_rows[-1]["quality"] += "_partial"

    # ---- 交叉验证：重叠期日频 R_M vs 主序列 ----
    print("\n" + "─" * 62)
    print("交叉验证（重叠期 vs 主序列 CoinGecko/mempool.space 口径）")
    print("─" * 62)
    overlap = [r for r in daily
               if MAIN_SERIES_OVERLAP["start"] <= r["date"] <= MAIN_SERIES_OVERLAP["end"]]
    backfill_mean = sum(r["r_m"] for r in overlap) / len(overlap)
    main_mean, main_n = None, 0
    main_csv = os.path.join("docs", "parity_series.csv")
    if os.path.exists(main_csv):
        with open(main_csv, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if (MAIN_SERIES_OVERLAP["start"] <= r["date"] <= MAIN_SERIES_OVERLAP["end"]
                        and r.get("R_M")):
                    main_mean = (main_mean or 0) + float(r["R_M"])
                    main_n += 1
        if main_n:
            main_mean /= main_n
    print(f"  回填日频 R_M 均值   {backfill_mean:.6f} $/kWh（{len(overlap)} 天）")
    if main_mean:
        dev = (backfill_mean / main_mean - 1) * 100
        verdict = "✅ 通过" if abs(dev) < 5 else "❌ 超阈值，须排查"
        print(f"  主序列 R_M 均值     {main_mean:.6f} $/kWh（{main_n} 天）")
        print(f"  偏差               {dev:+.2f}%（阈值 ±5% → {verdict}）")

    # ---- 概览打印 ----
    print("\n" + "─" * 62)
    print("RM 历史概览（每 12 个月抽 1 行）")
    print("─" * 62)
    print(f"{'月份':<9}{'BTC均价':>10}{'算力TH/s':>14}{'能效J/TH':>12}{'R_M $/kWh':>11}")
    for i, r in enumerate(out_rows):
        if i % 12 == 0 or i == len(out_rows) - 1:
            print(f"{r['date']:<9}{r['btc_price_usd_avg']:>10}"
                  f"{r['hashrate_th_s_avg']:>14}{r['fleet_efficiency_j_per_th']:>12}"
                  f"{r['R_M_usd_per_kwh']:>11}")

    if not args.no_csv:
        os.makedirs("docs", exist_ok=True)
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
            w.writeheader()
            w.writerows(out_rows)
        print(f"\n已写入 {OUTPUT_CSV}（{len(out_rows)} 个月度行，"
              f"{out_rows[0]['date']} → {out_rows[-1]['date']}）")


if __name__ == "__main__":
    main()
