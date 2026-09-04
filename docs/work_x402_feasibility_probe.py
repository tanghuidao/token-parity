"""分析 raw_x402/ 14 天归档数据的可行性，供 R_A 校准方法论设计参考。

仅读取，不写任何仓内文件；输出直接打印 + 写入 docs 工作区临时文件供进一步引用。
"""
import gzip
import json
import os
from collections import defaultdict, Counter
from datetime import datetime

ARCHIVE_DIR = r"C:\Users\tanghuidao\WorkBuddy\token-parity\raw_x402"
DATES = sorted(os.listdir(ARCHIVE_DIR)) if os.path.isdir(ARCHIVE_DIR) else []

def parse_endpoint_price(ep):
    """把 endpoint.price_amount 转 float；空字符串或 None 当 None。"""
    pa = ep.get("price_amount")
    if pa is None or pa == "":
        return None
    try:
        return float(pa)
    except (TypeError, ValueError):
        return None


all_rows = []
for fname in DATES:
    path = os.path.join(ARCHIVE_DIR, fname)
    if not fname.endswith(".json.gz"):
        continue
    with gzip.open(path, "rt", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"[!] {fname} parse error: {e}")
            continue
    date = data.get("archive_date")
    fetch_status = data.get("fetch_status")
    total_services = data.get("total_services")
    total_endpoints = data.get("total_endpoints")
    pages = data.get("pages_used")
    truncated = data.get("truncated")
    src = data.get("source")
    for svc in data.get("services", []):
        cat = svc.get("category") or "(uncategorized)"
        for ep in svc.get("endpoints", []):
            pa = parse_endpoint_price(ep)
            all_rows.append({
                "date": date,
                "fetch_status": fetch_status,
                "category": cat,
                "service_id": svc.get("id"),
                "endpoint_url": ep.get("url"),
                "method": ep.get("method"),
                "price_amount_usdc": pa,
                "price_scheme": ep.get("price_scheme"),
                "max_amount": ep.get("max_amount"),
                "min_amount": ep.get("min_amount"),
                "networks": ";".join(svc.get("networks") or []),
                "source": src,
            })


print(f"日期范围: {DATES[0]} → {DATES[-1]}（共 {len(DATES)} 天）")
print(f"总 endpoint 行数: {len(all_rows)}")


by_date = defaultdict(lambda: {"endpoints": 0, "with_price": 0, "services": set()})
for r in all_rows:
    d = by_date[r["date"]]
    d["endpoints"] += 1
    if r["price_amount_usdc"] is not None:
        d["with_price"] += 1
    d["services"].add(r["service_id"])

print("\n--- 每日概览 ---")
for d in sorted(by_date):
    info = by_date[d]
    print(f"  {d}: endpoints={info['endpoints']:>5}, w/price={info['with_price']:>5}, services={len(info['services']):>4}")


cat_counter = Counter(r["category"] for r in all_rows)
print("\n--- 全部 14 天 category 分布（按 endpoint 行数计） ---")
for cat, n in cat_counter.most_common():
    print(f"  {cat:<20} {n:>6}")


inf_rows = [r for r in all_rows if r["category"] == "Inference"]
print(f"\n--- Inference 类别 endpoint 样本数：{len(inf_rows)} ---")
prices_inf = [r["price_amount_usdc"] for r in inf_rows if r["price_amount_usdc"] is not None]
if prices_inf:
    prices_inf_sorted = sorted(prices_inf)
    n = len(prices_inf_sorted)
    print(f"  Inference 价分布（每次调用 USDC，{n} 条有价样本）：")
    print(f"    min={min(prices_inf):.6f}, p10={prices_inf_sorted[n//10]:.6f}, "
          f"p50={prices_inf_sorted[n//2]:.6f}, p90={prices_inf_sorted[9*n//10]:.6f}, "
          f"max={max(prices_inf):.6f}, mean={sum(prices_inf)/n:.6f}")
else:
    print("  无价样本")


print("\n--- source 取值分布 ---")
for s, n in Counter(r["source"] for r in all_rows).most_common():
    print(f"  {s:<30} {n:>6}")


print("\n--- price_scheme 分布 ---")
for s, n in Counter(r["price_scheme"] for r in all_rows if r["price_scheme"]).most_common():
    print(f"  {s:<20} {n:>6}")


print("\n--- fetch_status 分布 ---")
for s, n in Counter(r["fetch_status"] for r in all_rows).most_common():
    print(f"  {s:<10} {n:>6}")


distinct_inf_services = set(r["service_id"] for r in inf_rows)
print(f"\n--- Inference 类 distinct service 计数：{len(distinct_inf_services)} ---")
for sid in sorted(distinct_inf_services)[:30]:
    eps = [r for r in inf_rows if r["service_id"] == sid]
    has_price = sum(1 for r in eps if r["price_amount_usdc"] is not None)
    print(f"  {sid:<40} endpoints={len(eps):>2}, w/price={has_price:>2}")
