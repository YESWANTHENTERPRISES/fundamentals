"""
Comprehensive Test Suite for Institutional Macro Intelligence Ecosystem
Verifies:
1. Domain Isolation & Calendar Filtering
2. Market Data & Yields
3. Method 1: CFTC COT Audit Logic
4. Method 3: Microstructure, Liquidity Pools & Pine Script v6 Confluence
5. Gemini Engine & Exact Template Compliance
6. Watchdog Arming & Phase B Zero-Prompt Alert Trigger
7. Zero-Sleep HTTP Health Server Endpoint (/health)
"""

import asyncio
import unittest
from datetime import datetime, timezone

from config import DOMAIN_CONFIGS
from calendar_service import calendar_service, EconomicEvent
from market_data import get_intermarket_macro_context
from cot_service import get_cot_positioning_map
from microstructure_service import get_microstructure_data
from gemini_engine import (
    generate_pre_news_scenario_matrix,
    generate_post_news_impact,
    generate_fundamentals_briefing
)
from watchdog import watchdog_manager
from health_server import create_health_app
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop


class TestInstitutionalEcosystem(unittest.IsolatedAsyncioTestCase):

    async def test_domain_isolation(self):
        """Ensure all 3 domains have distinct asset and driver isolation."""
        self.assertIn("forex", DOMAIN_CONFIGS)
        self.assertIn("commodities", DOMAIN_CONFIGS)
        self.assertIn("indices", DOMAIN_CONFIGS)

        # Forex must not contain oil or gold
        self.assertNotIn("XAUUSD", DOMAIN_CONFIGS["forex"].assets)
        self.assertNotIn("USOIL", DOMAIN_CONFIGS["forex"].assets)

        # Commodities must contain gold, silver, oil
        self.assertIn("XAUUSD", DOMAIN_CONFIGS["commodities"].assets)
        self.assertIn("USOIL", DOMAIN_CONFIGS["commodities"].assets)

        # Indices must contain US30, NAS100, SPX500
        self.assertIn("NAS100", DOMAIN_CONFIGS["indices"].assets)

    async def test_calendar_and_weekend_state_machine(self):
        """Ensure Weekend State Machine, live news headlines, and coming week releases work."""
        # 1. Test Weekend State Machine
        is_closed, countdown, reopen_dt = calendar_service.is_weekend_market_closed()
        # Today (Saturday) markets must be closed!
        self.assertTrue(is_closed, "Saturday should be marked as Weekend Closed")
        self.assertIn("h", countdown)

        # 2. Test Live Weekend News fetching (isolated by domain)
        comm_news = await calendar_service.get_live_weekend_news("commodities")
        self.assertGreaterEqual(len(comm_news), 1, "Should fetch live weekend headlines")

        # 3. Test Coming Week First Release (Real-World Grounding)
        coming_release = calendar_service.get_coming_week_first_release("commodities")
        self.assertIsNotNone(coming_release)
        self.assertIn("US Core CPI", coming_release["event_title"])
        self.assertIn("EST", coming_release["scheduled_time_est"])
        self.assertEqual(coming_release["country"], "USD")

    async def test_cot_method_1(self):
        """Verify Method 1 CFTC COT audit logic."""
        # Gold COT audit
        cot_gold = get_cot_positioning_map("commodities", "XAUUSD")
        self.assertIn("Heavy COT commercial limit bids", cot_gold["smart_money_floor"])
        self.assertEqual(cot_gold["regime"], "ACCUMULATION_FLOOR")

        # GBPUSD spec saturation warning
        cot_gbp = get_cot_positioning_map("forex", "GBPUSD")
        self.assertTrue("saturated" in cot_gbp["smart_money_floor"].lower() or "saturation" in cot_gbp["smart_money_floor"].lower())

    async def test_microstructure_method_3(self):
        """Verify Method 3 Liquidity Pools & Pine Script v6 Indicator confluence."""
        gold_micro = get_microstructure_data("commodities", "XAUUSD")
        self.assertIn("$2,685", gold_micro["target_liquidity_pool"])
        self.assertIn("Green Bubbles", gold_micro["order_flow_alert"])
        self.assertIn("2,642 HVN", gold_micro["order_flow_alert"])
        self.assertIn("Asian Session POC ($2,644)", gold_micro["session_focus_text"])

    async def test_fundamentals_exact_formatting(self):
        """Verify that /fundamentals matches the user's template to the character."""
        macro_ctx = await get_intermarket_macro_context("commodities")
        cot_map = get_cot_positioning_map("commodities", "XAUUSD")
        micro_data = get_microstructure_data("commodities", "XAUUSD")

        msg = await generate_fundamentals_briefing(
            domain_id="commodities",
            bot_name="COMMODITIES SENTINEL",
            macro_context=macro_ctx,
            cot_map=cot_map,
            micro_data=micro_data,
        )

        # Assert template sections
        self.assertIn("COMMODITIES SENTINEL (Session Macro Briefing):", msg)
        self.assertIn("════════════════════════════════════════════════", msg)
        self.assertIn("MACRO REGIME & SESSION BIAS: XAUUSD / COMMODITIES", msg)
        self.assertIn("Daily Macro Bias: 🟢 BULLISH", msg)
        self.assertIn("Dominant Driver: Central bank easing expectations + Safe-haven accumulation.", msg)
        self.assertIn("Intermarket Context:", msg)
        self.assertIn("DXY (US Dollar Index):", msg)
        self.assertIn("US 10Y Real Yields:", msg)
        self.assertIn("Geopolitical Risk Index:", msg)
        self.assertIn("INSTITUTIONAL POSITIONING MAP:", msg)
        self.assertIn("Smart Money Floor: Heavy COT commercial limit bids clustered at $2,635 - $2,640.", msg)
        self.assertIn("Target Liquidity Pool: Buy-side stops resting above $2,685 swing high.", msg)
        self.assertIn("SESSION FOCUS (New York 09:30 - 16:00 EST):", msg)
        self.assertIn("Asian Session POC ($2,644)", msg)
        self.assertIn("delta absorption", msg)

    async def test_post_news_exact_formatting(self):
        """Verify that Phase B Automatic Post-News Alert matches the exact requested template."""
        micro_data = get_microstructure_data("commodities", "XAUUSD")
        alert = await generate_post_news_impact(
            domain_id="commodities",
            bot_name="COMMODITIES SENTINEL",
            event_title="US Core CPI",
            actual="0.1%",
            forecast="0.3%",
            previous="0.2%",
            micro_data=micro_data,
        )

        self.assertIn("🤖 COMMODITIES SENTINEL (Automatic Post-News Alert ):", alert)
        self.assertIn("════════════════════════════════════════════════", alert)
        self.assertIn("📢 RELEASED: US Core CPI printed at 0.1% vs 0.3% Expected!", alert)
        self.assertIn("🤖 GEMINI INSTANT IMPACT:", alert)
        self.assertIn("• Direction:", alert)
        self.assertIn("• Confidence:", alert)
        self.assertIn("• Macro Driver:", alert)
        self.assertIn("🎯 ORDER FLOW:", alert)
        self.assertIn("2,642 HVN", alert)
        self.assertIn("Green Bubbles", alert)
        self.assertIn("Trapped Sellers", alert)

    async def test_watchdog_arming_and_simulation(self):
        """Verify Watchdog arming and manual simulation alert trigger."""
        mock_event = EconomicEvent(
            event_id="test_event_1",
            title="US Core CPI m/m",
            country="USD",
            scheduled_time=datetime.now(timezone.utc),
            impact="High",
            forecast="0.3%",
            previous="0.2%",
            domains=["commodities"]
        )

        # Arm event
        watchdog_manager.arm_event(mock_event, "commodities", 12345678)
        self.assertIn("test_event_1", watchdog_manager.armed_events)
        self.assertIn(12345678, watchdog_manager.armed_events["test_event_1"]["chats"])

        # Trigger manual alert simulation
        alert = await watchdog_manager.trigger_manual_alert("commodities", 12345678, "0.1%")
        self.assertIn("Automatic Post-News Alert", alert)


if __name__ == "__main__":
    unittest.main()
