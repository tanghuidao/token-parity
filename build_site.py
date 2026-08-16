#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py —— 把 parity_series.csv 渲染成静态页 docs/index.html

设计：坐标纸底色 + 学术宋体标题 + 等宽数据字体。
页首签名元素"一度电的两种命运"：R_M 与 R_A 在同一条对数刻度上的位置对比。
图表用 Chart.js（cdnjs CDN），数据内联在页面里；JS 加载失败时回退显示
matplotlib 生成的 parity_index.png，保证国内无 CDN 环境也能看到曲线。

用法：python build_site.py            # 读 parity_series.csv，写 docs/
"""

import csv
import json
import math
import os
import shutil

CSV_PATH = "parity_series.csv"
OUT_DIR = "docs"

# 设计令牌（与 README 的设计说明保持一致）
C = {
    "paper":  "#F2F4F1",   # 坐标纸
    "grid":   "rgba(31,42,38,0.07)",
    "ink":    "#1F2A26",   # 墨
    "faint":  "#5C6B64",
    "copper": "#B4642D",   # 矿（R_M）
    "cobalt": "#2456A6",   # 推理（R_A）
    "graphite": "#4A4F4C", # Λ
    "oxblood": "#8C2F39",  # Ω
    "card":   "#FBFCFA",
}


def load_series():
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f"找不到 {CSV_PATH}，请先运行 parity_index.py 生成序列")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("序列为空")
    return rows


def logpos(value, lo=-2.0, hi=1.0):
    """把美元/kWh 数值映射到对数刻度条上的百分比位置（10^lo 到 10^hi）。"""
    x = (math.log10(max(value, 1e-9)) - lo) / (hi - lo)
    return max(2.0, min(98.0, x * 100))


def _sf(v):
    """安全转浮点：空字符串 / None / 缺失键返回 None。"""
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def build(rows):
    latest = rows[-1]
    dates = [r["date"] for r in rows]

    rm, ra = float(latest["R_M"]), float(latest["R_A"])
    # Λ 展示用链式接续列 Lambda_chained；缺失时退回原始 Lambda
    lam = _sf(latest.get("Lambda_chained")) or _sf(latest.get("Lambda")) or 0.0
    om = _sf(latest.get("Omega"))          # 可能为 None（待质量基准数据上线）
    omega_pending = (om is None)

    # 历史序列：Λ 用链式接续列，Ω 容空
    s = {
        "R_M":    [_sf(r["R_M"]) for r in rows],
        "R_A":    [_sf(r["R_A"]) for r in rows],
        "Lambda": [_sf(r.get("Lambda_chained")) or _sf(r.get("Lambda")) for r in rows],
        "Omega":  [_sf(r.get("Omega")) for r in rows],
    }
    payload = json.dumps({"dates": dates, "series": s}, ensure_ascii=False)

    SPARSE_MIN = 5
    n_pts = {k: sum(v is not None for v in s[k]) for k in s}

    def _fmt(key, val):
        if val is None:
            return "—"
        if key == "R_M":
            return f"{val:.4f}"
        if key == "R_A":
            return f"{val:.2f}"
        if key == "Lambda":
            return f"{val:.1f}"
        return f"{val:.3f}"

    def chartbox(key, title, color, cur_val):
        """稀疏(<5点)显示"序列积累中"大字；Ω待基准时不渲染该图块。"""
        cnt = n_pts[key]
        if key == "Omega" and omega_pending:
            return ""
        if cnt < SPARSE_MIN:
            return (f'<div class="chartbox"><h3 style="color:{color}">{title}</h3>'
                    f'<div class="collecting">序列积累中（当前 {cnt} 天）'
                    f'· Collecting data (day {cnt}）<br>'
                    f'<span class="bigval" style="color:{color}">{_fmt(key, cur_val)}</span>'
                    f'</div></div>')
        cid = {"R_M": "c_rm", "R_A": "c_ra", "Lambda": "c_l", "Omega": "c_o"}[key]
        return (f'<div class="chartbox"><h3 style="color:{color}">{title}</h3>'
                f'<canvas id="{cid}"></canvas></div>')

    box_rm = chartbox("R_M", "R_M（$/kWh）", "var(--copper)", rm)
    box_ra = chartbox("R_A", "R_A（$/kWh）", "var(--cobalt)", ra)
    box_l = chartbox("Lambda", "Λ 能量套利比", "var(--graphite)", lam)
    box_o = chartbox("Omega", "Ω 平价偏离指数", "var(--oxblood)", om)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Token 能量平价指数 · 丰裕学</title>
<meta name="description" content="把 AI 推理 token 与 PoW 加密货币折算到同一物理公分母（每千瓦时收入）的日频指数族。丰裕学框架的第一个活体演示。">
<style>
:root {{
  --paper: {C['paper']}; --ink: {C['ink']}; --faint: {C['faint']};
  --copper: {C['copper']}; --cobalt: {C['cobalt']};
  --graphite: {C['graphite']}; --oxblood: {C['oxblood']}; --card: {C['card']};
  --mono: "IBM Plex Mono", "SF Mono", "Cascadia Mono", Consolas, "Courier New", monospace;
  --serif: "Songti SC", "STSong", SimSun, "Noto Serif SC", serif;
  --sans: -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; }}
body {{
  background: var(--paper) ;
  background-image:
    linear-gradient({C['grid']} 1px, transparent 1px),
    linear-gradient(90deg, {C['grid']} 1px, transparent 1px);
  background-size: 28px 28px;
  color: var(--ink); font-family: var(--sans); line-height: 1.65;
}}
.wrap {{ max-width: 980px; margin: 0 auto; padding: 40px 20px 80px; }}
.eyebrow {{ font-family: var(--mono); font-size: 12px; letter-spacing: .18em;
  color: var(--faint); text-transform: uppercase; }}
h1 {{ font-family: var(--serif); font-weight: 700; font-size: clamp(30px, 5vw, 44px);
  letter-spacing: .02em; margin: 6px 0 2px; }}
.sub {{ color: var(--faint); font-size: 15px; max-width: 640px; }}
.stamp {{ font-family: var(--mono); font-size: 12px; color: var(--faint); margin-top: 10px; }}

/* 签名元素：一度电的两种命运（对数刻度条） */
.kwh {{ margin: 44px 0 8px; padding: 26px 22px 34px; background: var(--card);
  border: 1px solid rgba(31,42,38,.14); }}
.kwh h2 {{ font-family: var(--serif); font-size: 20px; margin-bottom: 4px; }}
.kwh .note {{ font-size: 13px; color: var(--faint); margin-bottom: 22px; }}
.scale {{ position: relative; height: 4px; background:
  linear-gradient(90deg, rgba(31,42,38,.25), rgba(31,42,38,.25)); margin: 46px 8px 30px; }}
.tick {{ position: absolute; top: -5px; width: 1px; height: 14px; background: rgba(31,42,38,.4); }}
.tick span {{ position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
  font-family: var(--mono); font-size: 11px; color: var(--faint); white-space: nowrap; }}
.pin {{ position: absolute; top: 50%; transform: translate(-50%, -50%);
  width: 14px; height: 14px; border-radius: 50%; border: 3px solid var(--paper); }}
.pin.mine {{ background: var(--copper); }}
.pin.infer {{ background: var(--cobalt); }}
.pin b {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  font-family: var(--mono); font-size: 13px; font-weight: 600; white-space: nowrap; }}
.pin.mine b {{ color: var(--copper); }}
.pin.infer b {{ color: var(--cobalt); }}
.kwh .verdict {{ font-size: 14px; }}
.kwh .verdict strong {{ font-family: var(--mono); }}

/* 指标卡 */
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px; margin: 26px 0 10px; }}
.card {{ background: var(--card); border: 1px solid rgba(31,42,38,.14); padding: 16px 18px; }}
.card .k {{ font-family: var(--mono); font-size: 12px; color: var(--faint); }}
.card .v {{ font-family: var(--mono); font-size: 27px; font-weight: 600; margin: 4px 0 2px; }}
.card .d {{ font-size: 12.5px; color: var(--faint); }}
.v.copper {{ color: var(--copper); }} .v.cobalt {{ color: var(--cobalt); }}
.v.graphite {{ color: var(--graphite); }} .v.oxblood {{ color: var(--oxblood); }}

/* 图表 */
section.charts {{ margin-top: 36px; }}
.chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
@media (max-width: 760px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
.chartbox {{ background: var(--card); border: 1px solid rgba(31,42,38,.14); padding: 14px; }}
.chartbox h3 {{ font-family: var(--mono); font-size: 13px; font-weight: 600; margin-bottom: 8px; }}
.fallback img {{ width: 100%; border: 1px solid rgba(31,42,38,.14); }}
.collecting {{ font-family: var(--mono); font-size: 13px; color: var(--faint);
  text-align: center; padding: 34px 10px; }}
.collecting .bigval {{ display: block; font-size: 26px; font-weight: 600; margin-top: 12px; }}

/* 方法论 */
details {{ margin-top: 36px; background: var(--card);
  border: 1px solid rgba(31,42,38,.14); padding: 18px 20px; }}
summary {{ font-family: var(--serif); font-size: 18px; cursor: pointer; }}
details p, details li {{ font-size: 14px; }}
details ul {{ padding-left: 20px; margin: 8px 0; }}
code {{ font-family: var(--mono); font-size: 13px; background: rgba(31,42,38,.06);
  padding: 1px 5px; }}
footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid rgba(31,42,38,.18);
  font-size: 12.5px; color: var(--faint); }}
footer a {{ color: var(--faint); }}
@media (prefers-reduced-motion: no-preference) {{
  .pin {{ transition: left .8s cubic-bezier(.2,.8,.2,1); }}
}}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="eyebrow">Abundantics · 丰裕学 / 实证模块 01</div>
  <h1>Token 能量平价指数</h1>
  <p class="sub">同一焦耳，两种耗散：AI 推理 token 与 PoW 加密货币折算到同一物理公分母（每千瓦时收入）后的日频指数族。</p>
  <div class="stamp">最近更新 {latest['date']} · 数据源 CoinGecko / mempool.space / OpenRouter · 自动更新</div>
</header>

<div class="kwh">
  <h2>一度电的两种命运</h2>
  <div class="note">对数刻度：同一 kWh 电能，投入比特币挖矿与投入 AI 推理的毛收入（美元）。</div>
  <div class="scale">
    <div class="tick" style="left:{logpos(0.01):.1f}%"><span>$0.01</span></div>
    <div class="tick" style="left:{logpos(0.1):.1f}%"><span>$0.10</span></div>
    <div class="tick" style="left:{logpos(1.0):.1f}%"><span>$1</span></div>
    <div class="tick" style="left:{logpos(10.0):.1f}%"><span>$10</span></div>
    <div class="pin mine" style="left:{logpos(rm):.1f}%"><b>挖矿 ${rm:.3f}</b></div>
    <div class="pin infer" style="left:{logpos(ra):.1f}%"><b>推理 ${ra:.2f}</b></div>
  </div>
  <div class="verdict">当前能量套利比 <strong>Λ = {lam:.1f}</strong>：一度电喂给推理的毛收入是喂给挖矿的 {lam:.0f} 倍（毛收入口径，未扣 GPU 折旧等非电成本）。</div>
</div>

<div class="cards">
  <div class="card"><div class="k">R_M · 挖矿每度电毛收入</div>
    <div class="v copper">${rm:.4f}</div><div class="d">美元/kWh，由链上数据自算 hashprice ÷ 全网加权能耗</div></div>
  <div class="card"><div class="k">R_A · 推理每度电毛收入</div>
    <div class="v cobalt">${ra:.2f}</div><div class="d">美元/kWh，用量加权模型篮子，标准 token 当量</div></div>
  <div class="card"><div class="k">Λ · 能量套利比</div>
    <div class="v graphite">{lam:.1f}</div><div class="d">R_A / R_M，毛收入口径 · 链式接续序列 · chain-linked</div></div>
  <div class="card"><div class="k">Ω · 平价偏离指数</div>
    {'<div class="v oxblood">待质量基准数据上线</div><div class="d">Pending quality benchmark · 待外部评测分（quality_score）上线后自动恢复</div>' if omega_pending else f'<div class="v oxblood">{om:.3f}</div><div class="d">ln(焦耳平价汇率 / 市场隐含汇率)，防御性 vs 生产性耗散的定价缺口</div>'}</div>
</div>

<section class="charts">
  <div class="chart-grid" id="jscharts">
    {box_rm}
    {box_ra}
    {box_l}
    {box_o}
  </div>
  <noscript><div class="fallback"><img src="parity_index.png" alt="指数历史曲线"></div></noscript>
  <div class="fallback" id="pngfallback" style="display:none"><img src="parity_index.png" alt="指数历史曲线"></div>
</section>

<details>
  <summary>方法论与口径</summary>
  <p style="margin-top:10px">挖矿侧：<code>hashprice = 近144块总奖励(BTC) × BTC价格 ÷ 全网算力(PH/s)</code>，再除以每 PH/s 的日耗电（全网加权能效 × 24h）得 R_M。单枚 BTC 体现能 ε = 全网日耗能 ÷ 日产出。</p>
  <p>推理侧：模型篮子按用量加权；质量折算采用"升贴水法"——以基准模型的 <code>quality_score</code>（来自价格以外的独立评测源，如 Artificial Analysis Intelligence Index）为 1，其他模型质量权重 = 其 quality_score ÷ 基准分。当篮子模型尚未提供 quality_score 时，质量权重一律置 1，Ω 与 ρ* 暂不计算（页面显示"待质量基准数据上线"）。</p>
  <p>Ω 的含义：比特币的能量用于"设防"（不可伪造的耗费），AI token 的能量用于"生产"。Ω 度量市场为这两种耗散支付的每焦耳价格之差，其<b>时间变化</b>比水平值更可信。</p>
  <ul>
    <li><b>全网加权能耗（fleet-weighted energy efficiency）</b>：全网矿机按算力加权的平均能效，单位 J/TH，数据来源 CBECI / Hashrate Index，季度手动更新；</li>
    <li>全网加权能效与单 token 能耗为手动参数（参考 CBECI / Epoch AI），是主要误差源；</li>
    <li>Λ 为毛收入口径，非利润口径——推理侧成本大头是 GPU 折旧而非电费；</li>
    <li>篮子成分变更采用链式接续（chain-linking），系数记录于仓库根目录 <code>chain_factors.json</code>，换基日期记录于提交历史。</li>
  </ul>
</details>

<footer>
  丰裕学（Abundantics）研究项目 · 指数定义与代码开源，非投资建议 ·
  <a href="parity_series.csv">下载完整序列 CSV</a>
  <div style="margin-top:6px">TEPI — Token Energy Parity Index. Daily revenue per kWh of Bitcoin mining (R_M) vs AI inference (R_A). Open data &amp; code · <a href="parity_series.csv">Download CSV</a></div>
</footer>
</div>

<script>window.__PARITY__ = {payload};</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"
        onerror="document.getElementById('jscharts').style.display='none';document.getElementById('pngfallback').style.display='block';"></script>
<script>
(function () {{
  if (!window.Chart) return;
  var D = window.__PARITY__;
  var base = {{
    type: "line",
    options: {{
      responsive: true, animation: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ maxTicksLimit: 8, font: {{ family: "monospace", size: 10 }} }},
             grid: {{ color: "rgba(31,42,38,0.07)" }} }},
        y: {{ ticks: {{ font: {{ family: "monospace", size: 10 }} }},
             grid: {{ color: "rgba(31,42,38,0.07)" }} }}
      }}
    }}
  }};
  function draw(id, key, color) {{
    var el = document.getElementById(id);
    if (!el) return;  // 稀疏模式或 Ω 待基准时该 canvas 不存在，跳过
    var cfg = JSON.parse(JSON.stringify(base));
    cfg.data = {{ labels: D.dates, datasets: [{{
      data: D.series[key], borderColor: color, backgroundColor: color,
      borderWidth: 1.8, pointRadius: D.dates.length > 60 ? 0 : 2.5, tension: 0.15 }}] }};
    // 稀疏序列（<5 点）关闭自动缩放到孤点的折线：spanGaps + 固定小 padding
    new Chart(el, cfg);
  }}
  draw("c_rm", "R_M", "{C['copper']}");
  draw("c_ra", "R_A", "{C['cobalt']}");
  draw("c_l", "Lambda", "{C['graphite']}");
  draw("c_o", "Omega", "{C['oxblood']}");
}})();
</script>
</body>
</html>
"""
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    # 供无 JS / 无 CDN 环境回退显示的曲线图，以及可下载的原始序列
    for src in ("parity_index.png", "parity_series.csv"):
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT_DIR, src))
    print(f"已生成 {OUT_DIR}/index.html（{len(rows)} 个数据点，最近 {rows[-1]['date']}）")


if __name__ == "__main__":
    build(load_series())
