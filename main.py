"""
24/7 Institutional Macro Intelligence Telegram Ecosystem
Unified Multi-Bot Orchestrator & Zero-Sleep Cloud Service

Orchestrates:
1. BOT 1 (FOREX SENTINEL)
2. BOT 2 (COMMODITIES SENTINEL)
3. BOT 3 (FUTURES / INDICES SENTINEL)
4. Background 24/7 Watchdog Manager (3-second event polling)
5. Zero-Sleep aiohttp Health Server (Port 8080, /health)
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Dict, List, Optional
from telegram.ext import Application, ApplicationBuilder, CommandHandler

from config import (
    PORT, HOST,
    TG_BOT_TOKEN_FOREX,
    TG_BOT_TOKEN_COMMODITIES,
    TG_BOT_TOKEN_INDICES,
    LOG_LEVEL,
    DOMAIN_CONFIGS
)
from bot_handlers import build_handlers_for_domain
from watchdog import watchdog_manager
from health_server import start_health_server

# Setup structured institutional logging
logging.basicConfig(
    format="%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)
logger = logging.getLogger("MainOrchestrator")

# Map domain to configured token
BOT_TOKENS: Dict[str, str] = {
    "forex": TG_BOT_TOKEN_FOREX,
    "commodities": TG_BOT_TOKEN_COMMODITIES,
    "indices": TG_BOT_TOKEN_INDICES,
}


async def setup_bot_application(domain_id: str, token: str) -> Optional[Application]:
    """Builds and initializes a domain-isolated Telegram Application."""
    config = DOMAIN_CONFIGS[domain_id]
    if not token or token.strip() in ("", "YOUR_FOREX_BOT_TOKEN", "YOUR_COMMODITIES_BOT_TOKEN", "YOUR_INDICES_BOT_TOKEN"):
        logger.warning(
            f"⚠️ Token for {config.bot_name} ({domain_id}) is not set in .env. "
            f"Add TG_BOT_TOKEN_{domain_id.upper()} to activate this bot."
        )
        return None

    try:
        app = ApplicationBuilder().token(token.strip()).build()

        # Build domain handlers
        handlers = build_handlers_for_domain(domain_id)
        app.add_handler(CommandHandler("start", handlers["start"]))
        app.add_handler(CommandHandler("help", handlers["help"]))
        app.add_handler(CommandHandler("news", handlers["news"]))
        app.add_handler(CommandHandler("fundamentals", handlers["fundamentals"]))
        app.add_handler(CommandHandler("status", handlers["status"]))
        app.add_handler(CommandHandler("watch", handlers["watch"]))
        app.add_handler(CommandHandler("simulate_release", handlers["simulate_release"]))
        app.add_handler(CommandHandler("testalert", handlers["simulate_release"]))

        # Register bot in Watchdog Manager
        watchdog_manager.register_bot_instance(domain_id, app.bot)

        logger.info(f"✅ {config.bot_name} configured and registered with domain isolation.")
        return app
    except Exception as e:
        logger.error(f"Failed to configure {config.bot_name}: {e}", exc_info=True)
        return None


async def start_bot_with_retry(app: Application, domain_id: str, stop_event: asyncio.Event):
    """
    Runs a single bot application with exponential backoff on network failures.
    Ensures 24/7 self-healing long-polling connectivity.
    """
    config = DOMAIN_CONFIGS[domain_id]
    retry_delay = 2.0
    max_retry_delay = 60.0

    while not stop_event.is_set():
        try:
            logger.info(f"Starting polling for {config.bot_name}...")
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            retry_delay = 2.0  # Reset on successful launch

            # Keep running until stop event is signaled
            while not stop_event.is_set():
                await asyncio.sleep(1.0)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Network / connection drop in {config.bot_name}: {e}. Retrying in {retry_delay:.1f}s...")
            try:
                if app.updater and app.updater.running:
                    await app.updater.stop()
                if app.running:
                    await app.stop()
            except Exception:
                pass

            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.5, max_retry_delay)
        finally:
            try:
                if app.updater and app.updater.running:
                    await app.updater.stop()
                if app.running:
                    await app.stop()
                await app.shutdown()
            except Exception as e:
                logger.debug(f"Error shutting down {config.bot_name}: {e}")


async def main():
    """Unified Orchestrator running all 3 bots, health server, and watchdog loop."""
    logger.info("=" * 60)
    logger.info("INSTITUTIONAL MACRO INTELLIGENCE TELEGRAM ECOSYSTEM")
    logger.info("Starting 24/7 Cloud Engine on Unified Asyncio Event Loop...")
    logger.info("=" * 60)

    stop_event = asyncio.Event()

    # Graceful shutdown handling
    loop = asyncio.get_running_loop()
    def _sig_handler():
        logger.info("Shutdown signal received. Gracefully terminating all sentinels...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _sig_handler)
        except NotImplementedError:
            # Windows signal handler fallback
            pass

    # 1. Start Zero-Sleep HTTP Health Server
    health_runner = None
    try:
        health_runner = await start_health_server(host=HOST, port=PORT)
    except Exception as e:
        logger.error(f"Failed to start Zero-Sleep HTTP Health Server on port {PORT}: {e}")

    # 2. Start Background Watchdog Manager
    await watchdog_manager.start()

    # 3. Initialize all 3 Telegram Bots
    active_apps: Dict[str, Application] = {}
    for domain_id, token in BOT_TOKENS.items():
        app = await setup_bot_application(domain_id, token)
        if app:
            active_apps[domain_id] = app

    if not active_apps:
        logger.warning(
            "⚠️ No valid Telegram Bot tokens detected in environment! "
            "Please configure TG_BOT_TOKEN_FOREX, TG_BOT_TOKEN_COMMODITIES, and/or TG_BOT_TOKEN_INDICES in .env. "
            "The Zero-Sleep Health Server is running and active at /health."
        )

    # 4. Launch polling tasks concurrently with fault tolerance
    bot_tasks: List[asyncio.Task] = []
    for domain_id, app in active_apps.items():
        task = asyncio.create_task(
            start_bot_with_retry(app, domain_id, stop_event),
            name=f"bot_{domain_id}"
        )
        bot_tasks.append(task)

    logger.info(f"Ecosystem running: {len(active_apps)}/3 Sentinels active, Watchdog armed, Health server online.")

    # Wait until stop event is signaled
    try:
        while not stop_event.is_set():
            await asyncio.sleep(1.0)
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()

    # Cleanup and graceful shutdown
    logger.info("Stopping all background tasks and bot connections...")
    await watchdog_manager.stop()

    for task in bot_tasks:
        task.cancel()
    if bot_tasks:
        await asyncio.gather(*bot_tasks, return_exceptions=True)

    if health_runner:
        await health_runner.cleanup()

    logger.info("Institutional Macro Intelligence Ecosystem shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
