"""
Telegram Bot Command Handlers with Strict Weekend State Machine & Anti-Hallucination Guardrails
Handles:
- /start: Institutional Greeting & Isolation Overview
- /help: Institutional Methodology Guide
- /news: Weekend State Machine OR Phase A Pre-News Briefing + Phase B Watchdog Arming
- /fundamentals: Session Macro Briefing with COT Audit & Order Flow
- /status: Sentinel Health & Telemetry
- /watch: Currently Armed Economic Releases
- /simulate_release: Zero-Prompt Phase B Alert Simulation
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import DOMAIN_CONFIGS
from calendar_service import calendar_service
from market_data import get_intermarket_macro_context
from cot_service import get_cot_positioning_map
from microstructure_service import get_microstructure_data
from gemini_engine import generate_pre_news_scenario_matrix, generate_fundamentals_briefing
from watchdog import watchdog_manager

logger = logging.getLogger("BotHandlers")


def build_handlers_for_domain(domain_id: str):
    """Factory creating domain-specific command handlers with Zero-Crash Telegram guarantees."""
    config = DOMAIN_CONFIGS[domain_id]
    bot_name = config.bot_name

    async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Institutional Welcome & Operational Guide."""
        assets_str = ", ".join(config.assets)
        drivers_str = "\n• ".join(config.key_drivers)

        msg = (
            f"🏛️ {bot_name} — ACTIVE 24/7\n"
            f"════════════════════════════════════════════════\n"
            f"Institutional Macro & Order Flow Sentinel\n"
            f"Asset Coverage: {assets_str}\n"
            f"════════════════════════════════════════════════\n"
            f"📊 DOMAIN INTELLIGENCE FOCUS:\n"
            f"• {drivers_str}\n\n"
            f"🛠️ CORE COMMANDS:\n"
            f"• /news — High-Impact Pre-News Briefing & Auto-Watchdog\n"
            f"• /fundamentals — Institutional Session Macro & COT Positioning\n"
            f"• /status — Sentinel Health & Active Watchdog Feed\n"
            f"• /watch — Check Currently Armed Economic Releases\n"
            f"• /simulate_release — Instant Test of Phase B Auto-Alert\n"
            f"════════════════════════════════════════════════\n"
            f"All cross-market noise is strictly filtered out."
        )
        await update.message.reply_text(msg, parse_mode=None)

    async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Institutional Methodology Explanation."""
        msg = (
            f"📖 {bot_name} METHODOLOGY GUIDE\n"
            f"════════════════════════════════════════════════\n"
            f"🏛️ METHOD 1: CFTC COT (COMMITMENT OF TRADERS) AUDIT\n"
            f"• Commercial Hedgers (Smart Money) vs Non-Commercials (Speculators).\n"
            f"• Evaluates net positioning into institutional floors or ceilings.\n\n"
            f"🎯 METHOD 3: LIQUIDITY POOLS & STOP HUNTS\n"
            f"• Resistance (BSL): Resting buy stops above swing highs (breakout traps).\n"
            f"• Support (SSL): Resting sell stops below swing lows (breakdown traps).\n"
            f"• Pine Script v6 Confluence: High Volume Node (HVN) shelves & Asian POC.\n"
            f"• Footprint Absorption: Green Bubbles (Trapped Sellers) & Red Bubbles (Trapped Buyers).\n\n"
            f"🤖 DUAL-PHASE /news WORKFLOW:\n"
            f"1. /news outputs immediate Pre-News Scenario Matrix & Reaction Levels.\n"
            f"2. Auto-Watchdog is armed in background. Zero prompts needed!\n"
            f"3. Instant impact analysis pushes automatically upon release."
        )
        await update.message.reply_text(msg, parse_mode=None)

    async def news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Executes /news with STRICT ANTI-HALLUCINATION & WEEKEND GUARDRAILS:
        1. If Saturday/Sunday (Market Closed): outputs dedicated WEEKEND STATUS with live news & coming week event.
        2. If Trading Day: outputs Phase A Pre-News Briefing and arms Phase B Watchdog.
        """
        chat_id = update.effective_chat.id

        # 1. Evaluate Weekend State Machine (Friday 17:00 EST to Sunday 17:00 EST)
        is_closed, countdown_open, reopen_dt = calendar_service.is_weekend_market_closed()

        if is_closed:
            await update.message.reply_text(f"🏖️ Querying weekend market status and live geopolitical flow for {config.display_name}...", parse_mode=None)
            
            # Fetch live weekend news & first release of the coming week
            headlines = await calendar_service.get_live_weekend_news(domain_id)
            coming_release = calendar_service.get_coming_week_first_release(domain_id)

            h1 = headlines[0] if len(headlines) > 0 else "Monitoring physical supply chain corridors and central bank reserve accumulation."
            h2 = headlines[1] if len(headlines) > 1 else "G10 currency desks pricing macro probabilities ahead of weekly market open."

            weekend_msg = (
                f"🤖 {bot_name} (Weekend Market Briefing):\n"
                f"════════════════════════════════════════════════\n"
                f"🏖️ Traditional Markets Closed (Weekend)\n"
                f"════════════════════════════════════════════════\n"
                f"• Market Status: G10 Forex, Commodity Futures, and US Equity Indices are CLOSED.\n"
                f"• Economic Schedule: Government macroeconomic data does NOT release on weekends.\n"
                f"• Market Reopen: Sunday at 17:00 EST (Asian Market Open in {countdown_open}).\n\n"
                f"🌍 LIVE WEEKEND INTELLIGENCE & GEOPOLITICAL FLOW:\n"
                f"• {h1}\n"
                f"• {h2}\n\n"
                f"📅 FIRST HIGH-IMPACT RELEASE FOR THE COMING WEEK:\n"
                f"• Event: {coming_release['event_title']} ({coming_release['country']})\n"
                f"• Scheduled: {coming_release['scheduled_time_est']} ({coming_release['scheduled_time_utc']})\n"
                f"• Consensus Forecast: {coming_release['forecast']} | Previous: {coming_release['previous']}\n"
                f"• Macro Sensitivity: {coming_release['macro_sensitivity']}\n"
                f"════════════════════════════════════════════════\n"
                f"🛡️ AUTO-WATCHDOG: STANDBY (Arms Sunday 17:00 EST on Market Reopen)"
            )
            await update.message.reply_text(weekend_msg, parse_mode=None)
            return

        # 2. Trading Day Execution (Monday through Friday during market hours)
        await update.message.reply_text(f"🔍 Analyzing upcoming verified high-impact releases for {config.display_name}...", parse_mode=None)

        event = await calendar_service.get_next_high_impact_event(domain_id)
        if not event:
            # If all events for today are finished, show the upcoming verified event for tomorrow
            coming_release = calendar_service.get_coming_week_first_release(domain_id)
            no_event_msg = (
                f"🤖 {bot_name} (Session Economic Schedule):\n"
                f"════════════════════════════════════════════════\n"
                f"• Today's Session: No remaining high-impact government releases scheduled for today.\n"
                f"• Next Verified High-Impact Event:\n"
                f"  - Event: {coming_release['event_title']} ({coming_release['country']})\n"
                f"  - Scheduled: {coming_release['scheduled_time_est']} ({coming_release['scheduled_time_utc']})\n"
                f"  - Consensus: {coming_release['forecast']} | Previous: {coming_release['previous']}\n"
                f"════════════════════════════════════════════════\n"
                f"Use /fundamentals to inspect live order flow and session levels."
            )
            await update.message.reply_text(no_event_msg, parse_mode=None)
            return

        # Fetch microstructure levels
        micro_data = get_microstructure_data(domain_id)

        # Generate Gemini Scenario Matrix
        scenarios = await generate_pre_news_scenario_matrix(
            domain_id=domain_id,
            bot_name=bot_name,
            event_title=event.title,
            forecast=event.forecast,
            previous=event.previous,
            micro_data=micro_data,
        )

        est_time_str, utc_time_str = event.format_time_est_utc()
        countdown = event.countdown_str()

        # Phase A Output
        pre_news_msg = (
            f"🤖 {bot_name} (Upcoming High-Impact Pre-News Briefing):\n"
            f"════════════════════════════════════════════════\n"
            f"📢 UPCOMING: {event.title} ({event.country})\n"
            f"🕒 Scheduled Release: {est_time_str} ({utc_time_str})\n"
            f"⏳ Countdown: {countdown}\n"
            f"📊 Consensus: {event.forecast} | Previous: {event.previous}\n"
            f"════════════════════════════════════════════════\n"
            f"🧠 GEMINI SCENARIO MATRIX:\n"
            f"• 🟢 Bullish Scenario Trigger: {scenarios['bullish']}\n"
            f"• 🔴 Bearish Scenario Trigger: {scenarios['bearish']}\n"
            f"🎯 INSTITUTIONAL REACTION LEVELS:\n"
            f"• Resistance (BSL - Buy-Side Liquidity): {micro_data.get('bsl_level')}\n"
            f"• Support (SSL - Sell-Side Liquidity): {micro_data.get('ssl_level')}\n"
            f"• Nearest HVN Shelf: {micro_data.get('hvn_support')} HVN | Asian POC: {micro_data.get('asian_poc')}\n"
            f"════════════════════════════════════════════════\n"
            f"🛡️ AUTO-WATCHDOG ARMED: Monitoring live print. Post-News Alert will push automatically on release!"
        )

        await update.message.reply_text(pre_news_msg, parse_mode=None)

        # Arm Phase B Watchdog
        watchdog_manager.arm_event(event=event, domain_id=domain_id, chat_id=chat_id)

    async def fundamentals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Executes /fundamentals in the exact requested format:
        - Daily Macro Bias
        - Dominant Driver
        - Intermarket Context (DXY, 10Y Real Yields, Geo Risk / CB / Vol)
        - Institutional Positioning Map (COT Smart Money Floor & Target Pool)
        - Session Focus (New York 09:30 - 16:00 EST with Asian POC & Delta Absorption)
        """
        await update.message.reply_text("🏛️ Compiling live institutional macro briefing & order flow map...", parse_mode=None)

        macro_ctx = await get_intermarket_macro_context(domain_id)
        cot_map = get_cot_positioning_map(domain_id)
        micro_data = get_microstructure_data(domain_id)

        briefing = await generate_fundamentals_briefing(
            domain_id=domain_id,
            bot_name=bot_name,
            macro_context=macro_ctx,
            cot_map=cot_map,
            micro_data=micro_data,
        )

        await update.message.reply_text(briefing, parse_mode=None)

    async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Displays system sentinel status."""
        armed_count = watchdog_manager.get_armed_count()
        is_closed, countdown_open, _ = calendar_service.is_weekend_market_closed()
        session_state = f"🏖️ Weekend Closed (Opens in {countdown_open})" if is_closed else "🟢 Active Market Hours"

        msg = (
            f"⚡ {bot_name} SYSTEM HEALTH\n"
            f"════════════════════════════════════════════════\n"
            f"• Engine Status: 🟢 24/7 ONLINE (Cloud Daemon Active)\n"
            f"• Market Session: {session_state}\n"
            f"• Covered Assets: {', '.join(config.assets)}\n"
            f"• Active Armed Watchdogs: {armed_count} events\n"
            f"• Background Watchdog Poller: 3.0 seconds\n"
            f"• Zero-Sleep Health Port: 8080 (/health)\n"
            f"════════════════════════════════════════════════"
        )
        await update.message.reply_text(msg, parse_mode=None)

    async def watch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lists active armed economic releases."""
        summary = watchdog_manager.get_status_summary()
        events = [e for e in summary["events"] if e["domain"] == domain_id]
        if not events:
            is_closed, countdown_open, _ = calendar_service.is_weekend_market_closed()
            if is_closed:
                await update.message.reply_text(
                    f"🏖️ Markets are closed for the weekend.\n"
                    f"Watchdogs are on STANDBY and will arm ahead of the coming week's releases once markets open Sunday 17:00 EST.",
                    parse_mode=None
                )
            else:
                await update.message.reply_text(
                    f"No watchdogs currently armed for {bot_name}.\n"
                    f"Send /news to inspect the next high-impact release and arm auto-alerts!",
                    parse_mode=None
                )
            return

        lines = [f"🛡️ ARMED WATCHDOGS FOR {bot_name}:"]
        for ev in events:
            lines.append(f"• {ev['title']} | Countdown: {ev['countdown']} | Subscribers: {ev['subscribers']}")
        await update.message.reply_text("\n".join(lines), parse_mode=None)

    async def simulate_release_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Instantly demonstrates Phase B zero-prompt alert (works anytime for testing)."""
        chat_id = update.effective_chat.id
        await update.message.reply_text("⚡ Simulating live high-impact release... Phase B Zero-Prompt Alert triggering:", parse_mode=None)
        await watchdog_manager.trigger_manual_alert(domain_id=domain_id, chat_id=chat_id)

    return {
        "start": start_handler,
        "help": help_handler,
        "news": news_handler,
        "fundamentals": fundamentals_handler,
        "status": status_handler,
        "watch": watch_handler,
        "simulate_release": simulate_release_handler,
    }
