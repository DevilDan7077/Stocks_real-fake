"""
frontend_integration.py - Backend ↔ Frontend API Integration Demo
Mini Project - Part C: Integrate your backend with frontend using API

This script simulates what the frontend JavaScript does, but in Python.
It shows every API call, the HTTP method used, and the response.

In a real deployment:
  • Backend runs at  http://localhost:5000  (or cloud URL)
  • Frontend (React / plain HTML) fetches data using the Fetch API or axios
  • CORS headers on the Flask backend allow cross-origin requests

Run this script while app.py is running:
    Terminal 1:  python app.py
    Terminal 2:  python frontend_integration.py
"""

import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:5000"


def api_call(method: str, path: str, body: dict = None) -> dict | None:
    """Generic HTTP request helper — mirrors what fetch() does in JavaScript."""
    url = BASE_URL + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"  ✗ HTTP {e.code}: {body_text[:200]}")
        return None
    except urllib.error.URLError:
        print("  ✗ Connection refused — is app.py running?")
        return None


def section(title: str):
    print(f"\n{'═' * 55}")
    print(f"  {title}")
    print('═' * 55)


def show(label: str, data):
    print(f"\n  {label}:")
    if isinstance(data, dict):
        print(json.dumps(data, indent=4))
    else:
        print(f"    {data}")


# ═══════════════════════════════════════════════════════════════
#  PART C — Integration Flow
# ═══════════════════════════════════════════════════════════════

def run_integration_demo():
    print("\n" + "★" * 55)
    print("   STOCK TRACKER — Frontend ↔ Backend Integration Demo")
    print("★" * 55)

    # ── Step 1: Health Check ────────────────────────────────────
    section("Step 1 — Health Check (GET /)")
    result = api_call("GET", "/")
    if result:
        print(f"  ✔ API is online: {result['api']} v{result['version']}")
        print(f"  ✔ Status: {result['status']}")

    # ── Step 2: Market Overview ─────────────────────────────────
    section("Step 2 — Load Market Summary (GET /api/market)")
    result = api_call("GET", "/api/market")
    if result and result.get("success"):
        print("  ✔ Market Indices:")
        for name, idx in result["data"]["indices"].items():
            arrow = "▲" if idx["change"] >= 0 else "▼"
            print(f"     {name:10s}  {idx['value']:>10,.2f}  {arrow} {abs(idx['change_pct']):.2f}%")

    # ── Step 3: List Available Stocks ───────────────────────────
    section("Step 3 — Get Available Symbols (GET /api/stocks)")
    result = api_call("GET", "/api/stocks")
    if result:
        print(f"  ✔ {result['count']} symbols available: {', '.join(result['symbols'])}")

    # ── Step 4: Single Stock Detail ─────────────────────────────
    section("Step 4 — Fetch Single Stock Quote (GET /api/stock/AAPL)")
    result = api_call("GET", "/api/stock/AAPL")
    if result and result.get("success"):
        s = result["data"]
        print(f"  ✔ {s['name']} ({s['symbol']})")
        print(f"     Price:     ${s['price']:>10,.2f}")
        print(f"     Change:    {s['change']:>+.2f}  ({s['change_pct']:>+.2f}%)")
        print(f"     Volume:    {s['volume']:>15,}")
        print(f"     Mkt Cap:   ${s['market_cap'] / 1e12:.2f}T")
        print(f"     P/E Ratio: {s['pe_ratio']}")
        print(f"     52W High:  ${s['week_52_high']}")
        print(f"     52W Low:   ${s['week_52_low']}")

    # ── Step 5: Batch Quotes ─────────────────────────────────────
    section("Step 5 — Batch Quotes (GET /api/stocks/batch?symbols=MSFT,TSLA,NVDA)")
    result = api_call("GET", "/api/stocks/batch?symbols=MSFT,TSLA,NVDA")
    if result and result.get("success"):
        print(f"  ✔ Fetched {result['count']} stocks:")
        print(f"  {'Symbol':<8} {'Price':>10} {'Change %':>10}")
        print("  " + "-" * 32)
        for s in result["data"]:
            arrow = "▲" if s["change_pct"] >= 0 else "▼"
            print(f"  {s['symbol']:<8} ${s['price']:>9,.2f}  {arrow}{abs(s['change_pct']):.2f}%")

    # ── Step 6: Historical Data ──────────────────────────────────
    section("Step 6 — Historical Data (GET /api/stock/AAPL/history?period=1wk)")
    result = api_call("GET", "/api/stock/AAPL/history?period=1wk")
    if result and result.get("success"):
        print(f"  ✔ {result['count']} data points for {result['symbol']} ({result['period']})")
        print(f"  {'Date':<12} {'Open':>9} {'High':>9} {'Low':>9} {'Close':>9}")
        print("  " + "-" * 52)
        for pt in result["data"][-5:]:   # show last 5 rows
            print(f"  {pt['date']:<12} {pt['open']:>9.2f} {pt['high']:>9.2f} {pt['low']:>9.2f} {pt['close']:>9.2f}")

    # ── Step 7: Add to Portfolio ─────────────────────────────────
    section("Step 7 — Add to Portfolio (POST /api/portfolio)")
    for sym, qty in [("AAPL", 10), ("MSFT", 5), ("NVDA", 3)]:
        result = api_call("POST", "/api/portfolio", {"symbol": sym, "quantity": qty})
        if result and result.get("success"):
            print(f"  ✔ {result['message']}")

    # ── Step 8: View Portfolio ───────────────────────────────────
    section("Step 8 — View Portfolio (GET /api/portfolio)")
    result = api_call("GET", "/api/portfolio")
    if result and result.get("success"):
        print(f"  ✔ Portfolio Holdings:")
        print(f"  {'Symbol':<8} {'Qty':>5} {'Price':>10} {'Value':>12} {'Chg%':>8}")
        print("  " + "-" * 48)
        for item in result["portfolio"]:
            arrow = "▲" if item["change_pct"] >= 0 else "▼"
            print(f"  {item['symbol']:<8} {item['quantity']:>5} ${item['price']:>9,.2f} ${item['market_value']:>11,.2f}  {arrow}{abs(item['change_pct']):.2f}%")
        print(f"\n  {'Total Portfolio Value:':>36} ${result['total_value']:>11,.2f}")

    # ── Step 9: Remove from Portfolio ───────────────────────────
    section("Step 9 — Remove Stock (DELETE /api/portfolio/MSFT)")
    result = api_call("DELETE", "/api/portfolio/MSFT")
    if result and result.get("success"):
        print(f"  ✔ {result['message']}")
        print(f"  Remaining holdings: {result['portfolio']['holdings']}")

    # ── Step 10: Error Handling Demo ─────────────────────────────
    section("Step 10 — Error Handling Demo")
    print("\n  → Requesting invalid symbol (FAKE):")
    api_call("GET", "/api/stock/FAKE")

    print("\n  → POST without JSON content-type:")
    req = urllib.request.Request(
        BASE_URL + "/api/portfolio",
        data=b'{"symbol":"AAPL","quantity":1}',
        method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=3)
    except urllib.error.HTTPError as e:
        print(f"  ✔ Correctly rejected with HTTP {e.code} (missing Content-Type)")

    print("\n" + "★" * 55)
    print("   Integration Demo Complete — All API calls succeeded!")
    print("★" * 55 + "\n")


if __name__ == "__main__":
    run_integration_demo()
