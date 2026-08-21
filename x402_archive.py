#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x402 生态付费端点每日归档（x402-archive v1.0）
================================================

只归档，不计算，不进任何指数、不上任何网页。
本模块是独立旁路：不改 parity_index.py / build_site.py / daily.yml 的任何一行。

数据源（2026-08-21 实测，均免 key、免登录；任务书 v1.0 决策记录见交付简报）：
  主源 Agentic.Market（Coinbase x402 服务目录，2026-04 上线）:
    GET https://api.agentic.market/v1/services?limit=200&offset=N
    实测 total=2310，每页上限 200 → 全量需 12 次请求（项目所有者已确认接受，
    超出任务书"≤10"红线 2 次；均为同一公开 JSON 接口的标准分页，非爬站式抓取）。
    返回结构: {"services":[{id,name,description,domain,category,networks,enriched,
              endpoints:[{url,method,description,pricing:{amount,currency,network,
              scheme,maxAmount,minAmount},...}],...}], "total":N, "limit":200, "offset":N}
  备源 CDP x402 Bazaar（仅作失败时的可达性探针，不用于归档数据）:
    GET https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources
    实测 total=15165，每页上限 100 → 全量需 152 次请求、约 15MB，不满足红线
    与体量假设，故按项目所有者拍板降级为一次性探测记录。

归档内容（体量控制，对齐 raw/ 对 OpenRouter 的处理）：
  - 每个服务只保留精简字段：id/名称/类目/domain/链/是否 curated，
    端点只保留 url/method/挂牌价与计价单位（amount+scheme，非空时才带 max/min；
    币种 100% 为 USDC，统一上提为顶层 settlement_assets）。
  - 剔除 description、iconUrl、parameters、quality 等大字段。
  - 单文件 >2MB 时打印 WARNING 并继续写入（只叫不咬）。
  - 当日重复运行覆盖当日文件；抓取失败时写入 fetch_status: failed 的最小文件，
    绝不复制昨日数据冒充当日。

用法：
  python x402_archive.py                # 归档今天
  python x402_archive.py --date 2026-08-21   # 归档指定日期（用于补跑/重跑）
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone, date as date_cls

import requests

# --------------------------------------------------------------------------
# 常量
# --------------------------------------------------------------------------
AGENTIC_URL = "https://api.agentic.market/v1/services"
AGENTIC_PAGE_SIZE = 200          # 实测上限，超过会被钳回 200
AGENTIC_MAX_PAGES = 12           # 项目所有者确认：全量 2,310 服务 = 12 页；超量时截断并警告
CDP_URL = "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources"
CDP_PROBE_LIMIT = 20             # 探针仅取一页，验证可达性
ARCHIVE_DIR = "raw_x402"
TIMEOUT = 30
UA = "x402-archive/1.0 (daily archive; no key; see github.com/tanghuidao/token-parity)"

# 交付简报用的 reasoning 类关键词（分类边界会变，仅用于统计，不写入归档）
REASONING_KEYWORDS = (
    "inference", "reasoning", "llm", "chat/completions", "v1/messages",
    "anthropic", "openai", "gemini", "deepseek", "claude", "grok",
    "completion", "language-model", "model",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def trim_endpoint(ep: dict) -> dict:
    """端点精简：只保留 url / method / 挂牌价与计价单位。
    体积控制：min/max 空值时省略键（upto 方案才有意义）；
    币种 100% 为 USDC，上提为顶层 settlement_assets（若未来出现多币种仍会记录集合）。"""
    pricing = ep.get("pricing") or {}
    out = {
        "url": ep.get("url", ""),
        "method": ep.get("method", ""),
        "price_amount": str(pricing.get("amount", "")),
        "price_scheme": str(pricing.get("scheme", "")),
    }
    for key, src in (("max_amount", "maxAmount"), ("min_amount", "minAmount")):
        val = str(pricing.get(src, ""))
        if val:
            out[key] = val
    return out


def trim_service(svc: dict) -> dict:
    """服务精简：id/slug、名称、类目、链、curated 标记 + 精简端点列表。"""
    endpoints = [trim_endpoint(ep) for ep in (svc.get("endpoints") or [])]
    return {
        "id": svc.get("id", ""),
        "name": svc.get("name", ""),
        "category": svc.get("category", ""),
        "domain": svc.get("domain", ""),
        "networks": svc.get("networks") or [],
        "enriched": bool(svc.get("enriched")),
        "endpoints": endpoints,
    }


def fetch_agentic_market(session: requests.Session):
    """全量抓取 Agentic.Market 服务目录（分页）。返回 (services, total, pages_used, truncated)。"""
    services = []
    total = None
    pages_used = 0
    truncated = False
    offset = 0
    while True:
        if pages_used >= AGENTIC_MAX_PAGES:
            truncated = True
            break
        params = {"limit": AGENTIC_PAGE_SIZE, "offset": offset}
        resp = session.get(AGENTIC_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        page = data.get("services") or []
        total = data.get("total", total)
        services.extend(page)
        pages_used += 1
        if not page or len(services) >= (total or 0):
            break
        offset = len(services)
        time.sleep(0.2)  # 轻微限速，礼貌起见；失败不重试
    if truncated:
        print(f"WARNING: total services {total} > {AGENTIC_MAX_PAGES * AGENTIC_PAGE_SIZE}; "
              f"archived first {len(services)} (truncated)")
    return services, total, pages_used, truncated


def probe_cdp(session: requests.Session) -> dict:
    """CDP Bazaar 可达性探针（1 次请求），供失败降级文件记录当日各源状态。"""
    probe = {"url": CDP_URL, "http_status": None, "error": None, "note": "probe only (full list infeasible: 15165 resources)"}
    try:
        resp = session.get(CDP_URL, params={"type": "http", "limit": CDP_PROBE_LIMIT}, timeout=15)
        probe["http_status"] = resp.status_code
        if resp.ok:
            data = resp.json()
            probe["total"] = (data.get("pagination") or {}).get("total")
        else:
            probe["error"] = resp.text[:200]
    except Exception as exc:
        probe["error"] = f"{type(exc).__name__}: {exc}"
    return probe


def classify_reasoning(services: list) -> int:
    """用关键词统计 reasoning 类服务数（仅交付简报用，不入档）。"""
    n = 0
    for svc in services:
        if (svc.get("category") or "").lower() in ("inference", "reasoning"):
            n += 1
            continue
        hay = " ".join([svc.get("name", ""), svc.get("domain", "")]).lower()
        if any(k in hay for k in REASONING_KEYWORDS):
            n += 1
    return n


def pricing_unit_distribution(services: list) -> dict:
    """计价方式分布（交付简报用，不入档）：
    exact+有价 = 按次固定价；upto = 按次但设上下限；空价 = 未披露（疑似按用量/token 动态）。"""
    dist = {"fixed_per_request": 0, "upto_cap": 0, "price_not_disclosed": 0}
    for svc in services:
        for ep in svc.get("endpoints", []):
            scheme = ep.get("price_scheme", "")
            amount = ep.get("price_amount", "")
            if scheme == "upto":
                dist["upto_cap"] += 1
            elif amount and scheme:
                dist["fixed_per_request"] += 1
            else:
                dist["price_not_disclosed"] += 1
    return dist


def write_archive(doc: dict, day: str) -> str:
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    path = os.path.join(ARCHIVE_DIR, f"{day}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(path)
    if size > 2 * 1024 * 1024:
        print(f"WARNING: {path} size {size} bytes exceeds 2MB (written anyway)")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="x402 生态付费端点每日归档")
    ap.add_argument("--date", default=None, help="归档日期 YYYY-MM-DD（默认今天）")
    args = ap.parse_args()
    day = args.date or date_cls.today().isoformat()
    fetched_at = now_iso()

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "application/json"})

    doc = {
        "archive_date": day,
        "fetched_at": fetched_at,
        "source": "agentic_market",
        "source_endpoint": f"{AGENTIC_URL}?limit={AGENTIC_PAGE_SIZE}&offset=N",
        "fetch_status": "ok",
    }

    try:
        services, total, pages_used, truncated = fetch_agentic_market(session)
        # 币种从原始响应统计（trim 后不再保留该字段）
        currencies = sorted({str((ep.get("pricing") or {}).get("currency", ""))
                             for s in services for ep in (s.get("endpoints") or [])} - {""})
        trimmed = [trim_service(s) for s in services]
        doc["total_services"] = total
        doc["total_endpoints"] = sum(len(s["endpoints"]) for s in trimmed)
        doc["pages_used"] = pages_used
        doc["truncated"] = truncated
        doc["settlement_assets"] = currencies
        doc["services"] = trimmed
        print(f"fetched {len(services)}/{total} services in {pages_used} pages (truncated={truncated})")
    except Exception as exc:
        # 失败降级：写入最小文件 + 当日各源可达性探针；绝不复制昨日数据
        print(f"ERROR: Agentic.Market fetch failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        doc["fetch_status"] = "failed"
        doc["error"] = f"{type(exc).__name__}: {exc}"
        doc["probes"] = {
            "agentic_market": {"url": AGENTIC_URL, "http_status": None, "error": doc["error"]},
            "cdp_bazaar": probe_cdp(session),
        }
        del doc["source_endpoint"], doc["source"]  # 失败文件不保留伪装的源标记
        doc["attempted_sources"] = [AGENTIC_URL, CDP_URL]

    path = write_archive(doc, day)

    if doc["fetch_status"] == "ok":
        services = doc["services"]
        reasoning = classify_reasoning(services)
        units = pricing_unit_distribution(services)
        print(f"archived {len(services)} services, {doc['total_endpoints']} endpoints to {path}")
        print(f"reasoning-class services: {reasoning}")
        print(f"pricing-unit distribution: {json.dumps(units, ensure_ascii=False)}")
    else:
        print(f"archive failed; wrote minimal probe file to {path}")

    return 0 if doc["fetch_status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
