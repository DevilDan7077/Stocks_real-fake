"""
test_app.py - Unit Tests for Stock Tracker API
Mini Project - Part B: Testing Flask Routes & HTTP Methods

Run with:  python -m pytest test_app.py -v
       or: python test_app.py
"""

import sys
import os
import unittest
import json

sys.path.insert(0, os.path.dirname(__file__))
from app import app


class StockTrackerAPITests(unittest.TestCase):

    def setUp(self):
        """Set up Flask test client before each test."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    # ── Index / Health ─────────────────────────────────────────
    def test_index_returns_200(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_index_has_api_key(self):
        res = self.client.get("/")
        data = json.loads(res.data)
        self.assertIn("api", data)
        self.assertEqual(data["api"], "Stock Tracker API")

    # ── Market Summary ─────────────────────────────────────────
    def test_market_summary_returns_indices(self):
        res = self.client.get("/api/market")
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("indices", data["data"])
        self.assertIn("S&P 500", data["data"]["indices"])

    # ── Stock List ─────────────────────────────────────────────
    def test_list_stocks_returns_symbols(self):
        res = self.client.get("/api/stocks")
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["symbols"], list)
        self.assertGreater(len(data["symbols"]), 0)
        self.assertIn("AAPL", data["symbols"])

    # ── Single Stock Quote ─────────────────────────────────────
    def test_get_valid_stock(self):
        res = self.client.get("/api/stock/AAPL")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["symbol"], "AAPL")
        self.assertIn("price", data["data"])
        self.assertIn("change_pct", data["data"])

    def test_get_invalid_stock_returns_404(self):
        res = self.client.get("/api/stock/ZZZZ")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

    def test_get_stock_lowercase_symbol(self):
        """API should accept lowercase symbols."""
        res = self.client.get("/api/stock/aapl")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["data"]["symbol"], "AAPL")

    # ── Batch Quotes ───────────────────────────────────────────
    def test_batch_valid_symbols(self):
        res = self.client.get("/api/stocks/batch?symbols=AAPL,MSFT,TSLA")
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 3)

    def test_batch_missing_symbols_param(self):
        res = self.client.get("/api/stocks/batch")
        self.assertEqual(res.status_code, 400)

    def test_batch_mixed_valid_invalid(self):
        res = self.client.get("/api/stocks/batch?symbols=AAPL,FAKE")
        data = json.loads(res.data)
        self.assertEqual(data["count"], 1)
        self.assertIn("FAKE", data["not_found"])

    # ── Historical Data ────────────────────────────────────────
    def test_history_default_period(self):
        res = self.client.get("/api/stock/AAPL/history")
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["period"], "1mo")
        self.assertGreater(data["count"], 0)

    def test_history_valid_period(self):
        for period in ["1wk", "1mo", "3mo", "6mo", "1y"]:
            res = self.client.get(f"/api/stock/AAPL/history?period={period}")
            data = json.loads(res.data)
            self.assertTrue(data["success"], f"Failed for period {period}")

    def test_history_invalid_period(self):
        res = self.client.get("/api/stock/AAPL/history?period=5y")
        self.assertEqual(res.status_code, 400)

    def test_history_ohlcv_structure(self):
        res = self.client.get("/api/stock/AAPL/history?period=1wk")
        data = json.loads(res.data)
        point = data["data"][0]
        for field in ["date", "open", "high", "low", "close", "volume"]:
            self.assertIn(field, point)

    # ── Portfolio ──────────────────────────────────────────────
    def test_add_to_portfolio_success(self):
        res = self.client.post(
            "/api/portfolio",
            data=json.dumps({"symbol": "AAPL", "quantity": 5}),
            content_type="application/json"
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data["success"])

    def test_add_to_portfolio_missing_symbol(self):
        res = self.client.post(
            "/api/portfolio",
            data=json.dumps({"quantity": 5}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    def test_add_to_portfolio_bad_quantity(self):
        res = self.client.post(
            "/api/portfolio",
            data=json.dumps({"symbol": "AAPL", "quantity": -3}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    def test_add_invalid_symbol_to_portfolio(self):
        res = self.client.post(
            "/api/portfolio",
            data=json.dumps({"symbol": "FAKE", "quantity": 1}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 404)

    def test_add_portfolio_requires_json_content_type(self):
        res = self.client.post(
            "/api/portfolio",
            data='{"symbol": "AAPL", "quantity": 1}',
        )
        self.assertEqual(res.status_code, 415)

    def test_view_portfolio(self):
        # add a stock first
        self.client.post(
            "/api/portfolio",
            data=json.dumps({"symbol": "MSFT", "quantity": 2}),
            content_type="application/json"
        )
        res = self.client.get("/api/portfolio")
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("total_value", data)

    def test_delete_from_portfolio(self):
        self.client.post(
            "/api/portfolio",
            data=json.dumps({"symbol": "NVDA", "quantity": 3}),
            content_type="application/json"
        )
        res = self.client.delete("/api/portfolio/NVDA")
        data = json.loads(res.data)
        self.assertTrue(data["success"])

    def test_delete_nonexistent_portfolio_item(self):
        res = self.client.delete("/api/portfolio/ZZZZ")
        self.assertEqual(res.status_code, 404)

    # ── HTTP Method Enforcement ────────────────────────────────
    def test_post_on_get_only_route_returns_405(self):
        res = self.client.post("/api/market")
        self.assertEqual(res.status_code, 405)

    def test_delete_on_get_only_route_returns_405(self):
        res = self.client.delete("/api/stocks")
        self.assertEqual(res.status_code, 405)


if __name__ == "__main__":
    print("Running Stock Tracker API Tests...")
    unittest.main(verbosity=2)
