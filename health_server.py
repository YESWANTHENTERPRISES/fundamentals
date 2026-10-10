"""
Zero-Sleep Asynchronous HTTP Health Server
Provides /health and / endpoints via aiohttp running concurrently in the asyncio loop.
Enables cloud platforms (Render, Railway, Fly.io, UptimeRobot) to keep the service awake 24/7.
"""

import logging
import time
from datetime import datetime, timezone
from aiohttp import web
from config import HOST, PORT
from watchdog import watchdog_manager

logger = logging.getLogger("HealthServer")

START_TIME = time.time()


async def health_handler(request: web.Request) -> web.Response:
    """JSON health endpoint for automated cloud health checks."""
    uptime = int(time.time() - START_TIME)
    data = {
        "status": "ok",
        "service": "macro_sentinel_bots",
        "version": "2.0.0",
        "uptime_seconds": uptime,
        "bots_online": {
            "forex_sentinel": "FOREX" in [b.upper() for b in watchdog_manager.bot_instances.keys()],
            "commodities_sentinel": "COMMODITIES" in [b.upper() for b in watchdog_manager.bot_instances.keys()],
            "indices_sentinel": "INDICES" in [b.upper() for b in watchdog_manager.bot_instances.keys()],
        },
        "watchdogs_armed": watchdog_manager.get_armed_count(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return web.json_response(data)


async def root_handler(request: web.Request) -> web.Response:
    """Rich institutional dashboard endpoint for uptime monitors."""
    uptime = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_fmt = f"{hours}h {minutes}m {seconds}s"
    armed_count = watchdog_manager.get_armed_count()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Institutional Macro Sentinel Ecosystem | 24/7 Status</title>
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: rgba(18, 26, 43, 0.85);
            --border: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-green: #10b981;
            --accent-blue: #38bdf8;
            --accent-gold: #f59e0b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{
            background: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}
        .container {{
            max-width: 720px;
            width: 100%;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 36px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(12px);
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
        }}
        .pulse {{
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.4); opacity: 0.5; }}
        }}
        .title {{ font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
        .subtitle {{ font-size: 14px; color: var(--text-muted); margin-top: 4px; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }}
        .card {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
        }}
        .card-title {{ font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
        .card-val {{ font-size: 16px; font-weight: 600; color: var(--text-main); }}
        .bot-list {{ display: flex; flex-direction: column; gap: 12px; }}
        .bot-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 18px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            border-radius: 10px;
        }}
        .bot-name {{ font-weight: 600; font-size: 14px; }}
        .bot-assets {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}
        .status-ok {{ color: var(--accent-green); font-size: 13px; font-weight: 600; }}
        .footer {{
            margin-top: 28px;
            padding-top: 18px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 class="title">Institutional Macro Sentinel</h1>
                <p class="subtitle">3-Bot Autonomous Telegram Cloud Ecosystem</p>
            </div>
            <div class="badge">
                <span class="pulse"></span> 24/7 ONLINE
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">System Uptime</div>
                <div class="card-val">{uptime_fmt}</div>
            </div>
            <div class="card">
                <div class="card-title">Health Port</div>
                <div class="card-val">{PORT} (/health)</div>
            </div>
            <div class="card">
                <div class="card-title">Armed Watchdogs</div>
                <div class="card-val">{armed_count} Active</div>
            </div>
        </div>

        <div class="bot-list">
            <div class="bot-row">
                <div>
                    <div class="bot-name">⚡ BOT 1: FOREX SENTINEL</div>
                    <div class="bot-assets">EURUSD • GBPUSD • USDJPY • AUDUSD • Fed/ECB/BoE/BoJ</div>
                </div>
                <div class="status-ok">● ACTIVE</div>
            </div>
            <div class="bot-row">
                <div>
                    <div class="bot-name">🟡 BOT 2: COMMODITIES SENTINEL</div>
                    <div class="bot-assets">Gold (XAUUSD) • Silver (XAGUSD) • Crude Oil (USOIL) • TIPS Yields</div>
                </div>
                <div class="status-ok">● ACTIVE</div>
            </div>
            <div class="bot-row">
                <div>
                    <div class="bot-name">📈 BOT 3: INDICES SENTINEL</div>
                    <div class="bot-assets">US30 (Dow) • NAS100 (Nasdaq) • SPX500 • ISM PMIs • Earnings</div>
                </div>
                <div class="status-ok">● ACTIVE</div>
            </div>
        </div>

        <div class="footer">
            <span>Method 1 (COT Audit) + Method 3 (Order Flow Liquidity Pools)</span>
            <span>Zero-Sleep Cloud Architecture</span>
        </div>
    </div>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")


def create_health_app() -> web.Application:
    """Builds the aiohttp web application."""
    app = web.Application()
    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/status", health_handler)
    return app


async def start_health_server(host: str = HOST, port: int = PORT) -> web.AppRunner:
    """Starts the asynchronous HTTP health server on the given host and port."""
    app = create_health_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"Zero-Sleep HTTP Health Server running at http://{host}:{port}/health")
    return runner
