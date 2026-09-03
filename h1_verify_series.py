#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
h1_verify_series.py —— H1 品类 seriesID 存在性核验（cu.series 权威核验）
=========================================================================

用途：
  把 category_mapping.csv 中「待核实」的 seriesID 逐一与 BLS cu.series 权威清单比对，
  确认存在则翻「已核实」并回填「数据起始年份」，不存在则 fail loud 并在报告中列出。

为什么用 cu.series 而非 BLS API：
  cu.series（download.bls.gov 扁平文件）是全部 CPI 序列的权威目录，含
  series_id / area_code / item_code / seasonal / series_title / begin_year / begin_period ...
  一次下载即可拿到「存在性 + 官方标题 + 起始年月」，且不消耗 BLS API 配额。

环境要求：
  本脚本需在能直连 download.bls.gov 的网络运行（本地开发网络被 Akamai 地域封锁 403，
  无法直连），故实际运行放在 GitHub Action（runner 在美国，可直连）。本地仅可
  `--input <file>` 用已下载的 cu.series 文件做离线核验/回归。

列说明（cu.series，tab 分隔，首行为 header）：
  series_id / area_code / item_code / seasonal / periodicity_code / base_code /
  base_period / series_title / footnote_codes / begin_year / begin_period / end_year / end_period
  其中 series_id 前缀 CUUR0000 = 全国 CPI-U、未季调（本项目的唯一口径）。

行为：
  · 只处理「状态 == 待核实」的行（老「已核实」/「降级」行不动，仅做 sanity check 报告）。
  · 存在 → 状态翻「已核实」，数据起始年份 = cu.series begin_year。
  · 不存在 → 保持「待核实」，写入报告「未通过核验」清单，进程以非零退出（fail loud）。
  · 始终写回 category_mapping.csv（存在的已转正）+ docs/h1_series_verification.md 报告。
  单一信息源：category_mapping.csv 仍是被 fetch/analyze 只读的源头，本脚本只是其核验器。

用法：
  python h1_verify_series.py                  # 在线：下载 cu.series 后核验（GitHub Action 用）
  python h1_verify_series.py --input cu.series.txt   # 离线：读本地 cu.series 文件核验
"""
import argparse
import csv
import os
import sys
from datetime import datetime, timezone

import requests

# --------------------------------------------------------------------------
# 常量
# --------------------------------------------------------------------------
CU_SERIES_URL = "https://download.bls.gov/pub/time.series/cu/cu.series"
MAPPING_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "category_mapping.csv")
REPORT_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "h1_series_verification.md")

PREFIX = "CUUR0000"       # 全国 CPI-U 未季调（本项目的唯一口径）
STATUS_TODO = "待核实"
STATUS_DONE = "已核实"
STATUS_DOWNGRADE = "降级"

TIMEOUT = 180             # cu.series 文件较大（数万行），给足超时
UA = "h1-verify-series/1.0 (series ID audit; see github.com/tanghuidao/token-parity)"

# category_mapping.csv 的列顺序（写回时固定，避免列序漂移）
COLS = ["中文品类名", "BLS_item_title", "series_id", "层级", "状态", "数据起始年份", "备注", "H1分组"]

# cu.series 需要按名定位的列（首行为 header，用名称映射索引，不写死位置）
NEEDED_COLS = ["series_id", "item_code", "seasonal", "series_title", "begin_year", "begin_period"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_cu_series_lines(url: str) -> list:
    """流式下载 cu.series，返回按行切分的字符串列表（首行 header 保留）。"""
    resp = requests.get(url, timeout=TIMEOUT, stream=True, headers={"User-Agent": UA, "Accept": "text/plain"})
    resp.raise_for_status()
    lines = []
    for raw in resp.iter_lines():
        if raw:
            lines.append(raw.decode("utf-8", errors="replace"))
    if not lines:
        raise RuntimeError("cu.series 下载结果为空")
    return lines


def parse_cu_series(lines: list) -> dict:
    """解析 cu.series，返回 {series_id: {item_code, seasonal, series_title, begin_year, begin_period}}，
    仅保留 PREFIX（CUUR0000）前缀的序列。"""
    header = lines[0].split("\t")
    idx = {name: i for i, name in enumerate(header)}
    missing = [n for n in NEEDED_COLS if n not in idx]
    if missing:
        raise RuntimeError(f"cu.series header 缺少列 {missing}；实际列：{header}")

    catalog = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        cols = line.split("\t")
        sid = (cols[idx["series_id"]] if idx["series_id"] < len(cols) else "").strip()
        if not sid.startswith(PREFIX):
            continue
        def col(name):
            i = idx[name]
            return cols[i].strip() if i < len(cols) else ""
        catalog[sid] = {
            "item_code": col("item_code"),
            "seasonal": col("seasonal"),
            "series_title": col("series_title"),
            "begin_year": col("begin_year"),
            "begin_period": col("begin_period"),
        }
    if not catalog:
        raise RuntimeError(f"cu.series 中未找到任何 {PREFIX} 前缀序列，疑似下载/解析异常")
    return catalog


def load_mapping(path: str) -> list:
    if not os.path.exists(path):
        raise FileNotFoundError(f"mapping 文件不存在：{path}")
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("series_id") or "").strip():
                rows.append(r)
    return rows


def write_mapping(rows: list, path: str) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: (r.get(c) or "") for c in COLS})


def write_report(report: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    L = []
    L.append("# H1 品类 seriesID 核验报告\n")
    L.append(f"- 核验时间：{report['verified_at']}")
    L.append(f"- 数据源：BLS cu.series（`{CU_SERIES_URL}`，口径 {PREFIX} 全国 CPI-U 未季调）")
    L.append(f"- 核验对象：category_mapping.csv 中「待核实」的 {report['todo_total']} 个 seriesID")
    L.append(f"- 结论：✅ 通过 {report['found_count']} 项 / ⚠️ 未通过 {report['not_found_count']} 项\n")

    L.append("## 一、未通过核验（需人工复核，seriesID 在 cu.series 中不存在）\n")
    if report["not_found"]:
        L.append("| series_id | item_code | 中文品类名 | H1分组 | 备注 |")
        L.append("|---|---|---|---|---|")
        for it in report["not_found"]:
            L.append(f"| `{it['series_id']}` | `{it['item_code']}` | {it['zh']} | {it['group']} | {it['note']} |")
    else:
        L.append("（无）")
    L.append("")

    L.append("## 二、通过核验（已转正为「已核实」，并回填起始年份）\n")
    if report["found"]:
        L.append("| series_id | 中文品类名 | 官方 series_title | H1分组 | 起始年份 |")
        L.append("|---|---|---|---|---|")
        for it in report["found"]:
            L.append(f"| `{it['series_id']}` | {it['zh']} | {it['series_title']} | {it['group']} | {it['begin_year']} |")
    else:
        L.append("（无）")
    L.append("")

    L.append("## 三、老品类「已核实」sanity check（不动，仅复核存在性）\n")
    L.append("| series_id | 中文品类名 | 在 cu.series | 官方起始年份 vs 映射起始年份 |")
    L.append("|---|---|---|---|")
    for it in report["old_check"]:
        mark = "✅" if it["in_catalog"] else "❌"
        cmp_txt = f"{it['catalog_begin']} vs {it['mapped_begin']}" if it["in_catalog"] else "-"
        L.append(f"| `{it['series_id']}` | {it['zh']} | {mark} | {cmp_txt} |")
    L.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="H1 品类 seriesID 存在性核验（cu.series）")
    ap.add_argument("--input", default=None, help="本地 cu.series 文件路径（离线核验/回归用）；缺省在线下载")
    ap.add_argument("--mapping", default=MAPPING_CSV, help=f"category_mapping.csv 路径（缺省 {MAPPING_CSV}）")
    ap.add_argument("--report", default=REPORT_MD, help=f"核验报告输出路径（缺省 {REPORT_MD}）")
    args = ap.parse_args()
    mapping_csv = args.mapping
    report_md = args.report

    # 1) 取 cu.series 目录
    if args.input:
        if not os.path.exists(args.input):
            print(f"[h1_verify] ERROR: 本地文件不存在：{args.input}", file=sys.stderr)
            return 1
        with open(args.input, encoding="utf-8", errors="replace") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]
        source_note = args.input
    else:
        try:
            lines = load_cu_series_lines(CU_SERIES_URL)
        except Exception as exc:
            print(f"[h1_verify] ERROR: 下载 cu.series 失败：{type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        source_note = CU_SERIES_URL

    try:
        catalog = parse_cu_series(lines)
    except Exception as exc:
        print(f"[h1_verify] ERROR: 解析 cu.series 失败：{exc}", file=sys.stderr)
        return 1
    print(f"[h1_verify] cu.series 载入：{len(catalog)} 条 {PREFIX} 序列（{source_note}）", file=sys.stderr)

    rows = load_mapping(mapping_csv)

    # 2) 分类处理
    found, not_found, old_check = [], [], []
    todo_total = 0
    for r in rows:
        sid = (r.get("series_id") or "").strip()
        status = (r.get("状态") or "").strip()
        code = sid[len(PREFIX):] if sid.startswith(PREFIX) else sid
        if status == STATUS_TODO:
            todo_total += 1
            if sid in catalog:
                r["状态"] = STATUS_DONE
                r["数据起始年份"] = catalog[sid]["begin_year"]
                found.append({
                    "series_id": sid,
                    "zh": (r.get("中文品类名") or "").strip(),
                    "series_title": catalog[sid]["series_title"],
                    "group": (r.get("H1分组") or "").strip(),
                    "begin_year": catalog[sid]["begin_year"],
                })
            else:
                not_found.append({
                    "series_id": sid,
                    "item_code": code,
                    "zh": (r.get("中文品类名") or "").strip(),
                    "group": (r.get("H1分组") or "").strip(),
                    "note": (r.get("备注") or "").strip(),
                })
        elif status == STATUS_DONE:
            old_check.append({
                "series_id": sid,
                "zh": (r.get("中文品类名") or "").strip(),
                "in_catalog": sid in catalog,
                "catalog_begin": catalog.get(sid, {}).get("begin_year", ""),
                "mapped_begin": (r.get("数据起始年份") or "").strip(),
            })
        # 降级/其它状态：不动

    # 3) 写回 mapping + 报告
    write_mapping(rows, mapping_csv)
    report = {
        "verified_at": now_iso(),
        "todo_total": todo_total,
        "found_count": len(found),
        "not_found_count": len(not_found),
        "found": found,
        "not_found": not_found,
        "old_check": old_check,
    }
    write_report(report, report_md)

    print(f"[h1_verify] 待核实 {todo_total} → 通过 {len(found)} / 未通过 {len(not_found)}", file=sys.stderr)
    print(f"[h1_verify] 报告已写：{report_md}", file=sys.stderr)
    if not_found:
        print(f"[h1_verify] FAIL: 以下 seriesID 未通过核验（详见报告）：", file=sys.stderr)
        for it in not_found:
            print(f"    {it['series_id']}  {it['zh']}", file=sys.stderr)
        return 2  # fail loud：有未通过项
    return 0


if __name__ == "__main__":
    sys.exit(main())
