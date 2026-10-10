"""
Test Suite for Zero-Sleep HTTP Health Server
"""

import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from health_server import create_health_app


class TestHealthServer(AioHTTPTestCase):

    async def get_application(self):
        return create_health_app()

    @unittest_run_loop
    async def test_health_json(self):
        """GET /health must return 200 with JSON status."""
        resp = await self.client.request("GET", "/health")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "macro_sentinel_bots")
        self.assertIn("uptime_seconds", data)
        self.assertIn("bots_online", data)

    @unittest_run_loop
    async def test_root_dashboard(self):
        """GET / must return 200 with HTML dashboard."""
        resp = await self.client.request("GET", "/")
        self.assertEqual(resp.status, 200)
        text = await resp.text()
        self.assertIn("Institutional Macro Sentinel", text)
        self.assertIn("24/7 ONLINE", text)


if __name__ == "__main__":
    unittest.main()
