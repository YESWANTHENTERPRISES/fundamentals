# 🏛️ Institutional Macro Intelligence Telegram Ecosystem (3 Sentinels)

A high-performance, asynchronous Python-based 24/7 cloud service orchestrating **THREE (3) dedicated institutional Telegram Bots**. Each bot operates as an Institutional Macro & Order Flow Sentinel for a specific asset class, powered by **Google Gemini AI (Gemini 2.5 Flash)**, live macroeconomic calendar feeds, CFTC COT positioning audits, and market microstructure liquidity models.

---

## ⚡ Ecosystem Architecture & Asset Class Sentinels

```
                                  ┌───────────────────────────────────────────────┐
                                  │   Unified Asyncio Event Loop (Python 3.11+)   │
                                  └───────┬───────────────────────────────┬───────┘
                                          │                               │
                ┌─────────────────────────┼─────────────────────────┐     │
                ▼                         ▼                         ▼     ▼
    ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐ ┌─────────────────────────┐
    │     BOT 1: FOREX      │ │   BOT 2: COMMODITIES  │ │    BOT 3: INDICES     │ │  Zero-Sleep HTTP Server │
    │       SENTINEL        │ │       SENTINEL        │ │       SENTINEL        │ │      (aiohttp :8080)    │
    ├───────────────────────┤ ├───────────────────────┤ ├───────────────────────┤ ├─────────────────────────┤
    │ • EURUSD, GBPUSD      │ │ • Gold (XAUUSD)       │ │ • US30 (Dow Jones)    │ │ • GET /health (JSON)    │
    │ • USDJPY, AUDUSD      │ │ • Silver (XAGUSD)     │ │ • NAS100 (Nasdaq)     │ │ • GET / (Status UI)     │
    │ • Fed, ECB, BoE, BoJ  │ │ • Crude Oil (USOIL)   │ │ • SPX500 (S&P 500)    │ │ Keeps cloud awake 24/7  │
    │ • CPI, NFP, Rates     │ │ • US 10Y Real Yields  │ │ • Tech Earnings, GDP  │ │ Prevents idle sleeping  │
    │ • DXY Dynamics        │ │ • OPEC+, Geopolitics  │ │ • ISM PMIs, VIX       │ └─────────────────────────┘
    └───────────┬───────────┘ └───────────┬───────────┘ └───────────┬───────────┘
                │                         │                         │
                └─────────────────────────┼─────────────────────────┘
                                          ▼
                      ┌──────────────────────────────────────┐
                      │    Zero-Prompt Background Watchdog   │
                      │   (Polls every 3s at release time)   │
                      └───────────────────┬──────────────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
           ┌────────────────────────┐          ┌────────────────────────┐
           │   Method 1: CFTC COT   │          │  Method 3: Order Flow  │
           │      Audit Engine      │          │     Microstructure     │
           │ (Smart Money Hedgers   │          │ (BSL / SSL Stops, HVN, │
           │ vs Spec Squeeze Risk)  │          │  POC, Green Bubbles)   │
           └────────────────────────┘          └────────────────────────┘
```

---

## 🛡️ Asset Domain Isolation (Zero Cross-Market Noise)

When a user interacts with a specific bot, that bot **strictly processes and outputs news, fundamentals, and levels relevant to its domain**:

| Sentinel | Asset Coverage | Central Banks & Macro Drivers | Noise Filtered Out |
| :--- | :--- | :--- | :--- |
| **BOT 1: FOREX SENTINEL** | EURUSD, GBPUSD, USDJPY, AUDUSD | Fed, ECB, BoE, BoJ, G10 CPI, NFP, Rate Decisions, DXY | No commodity inventories, no corporate earnings |
| **BOT 2: COMMODITIES SENTINEL** | Gold (XAUUSD), Silver (XAGUSD), WTI Oil (USOIL) | US 10Y Real Yields (TIPS), DXY, OPEC+ Quotas, Geopolitical Risk Index | No G10 retail sales, no tech index earnings |
| **BOT 3: INDICES SENTINEL** | US30 (Dow Jones), NAS100 (Nasdaq), SPX500 | US GDP, ISM Manufacturing/Services PMIs, Fed Rate Probabilities, Mega-Cap Earnings | No non-US currencies, no oil inventories |

---

## 🤖 Command Specifications & Dual-Phase Behavior

### 1. `/news` — Dual-Phase Lifecycle

#### PHASE A: Instant Pre-News Briefing
- Immediately queries the live economic calendar for the next upcoming high-impact event for that domain.
- Generates a **Gemini Pre-News Scenario Matrix** (Bullish vs. Bearish triggers based on consensus vs. previous).
- Identifies Institutional Reaction Levels ahead of release (Resistance BSL vs. Support SSL, High Volume Nodes, and Asian Session POC).
- **Arms the background zero-prompt watchdog**.

#### PHASE B: Zero-Prompt Automatic Post-News Alert
- The bot registers a background watchdog task for that event's release time.
- **The user DOES NOT need to prompt the bot again**.
- The moment release time arrives, the background scraper polls live actual data **every 3 seconds**.
- The moment actual data is printed, it prompts Gemini and automatically pushes the alert into the Telegram chat:

```text
🤖 BOT (Automatic Post-News Alert ):
════════════════════════════════════════════════
📢 RELEASED: US Core CPI printed at 0.1% vs 0.3% Expected! 🟢 COOLING
🤖 GEMINI INSTANT IMPACT:
• Direction: 🟢 STRONG BULLISH (Gold / Risk-On)
• Confidence: 94%
• Macro Driver: Major disinflation beat. Bond yields plunging 9 bps. 
  Institutional flow aggressively bidding commodities.
🎯 ORDER FLOW:
• Institutions are defending the 2,642 HVN support. Look only for Trapped Sellers (Green Bubbles) to ride the trend up!
```

---

### 2. `/fundamentals` — Institutional Session Macro Briefing

Generates an institutional macro session briefing combining central bank posture, intermarket context, CFTC COT positioning, and order flow microstructure:

```text
User: /fundamentals
🤖 BOT (Session Macro Briefing):
════════════════════════════════════════════════
🏛️ MACRO REGIME & SESSION BIAS: XAUUSD / COMMODITIES
════════════════════════════════════════════════
• Daily Macro Bias: 🟢 BULLISH
• Dominant Driver: Central bank easing expectations + Safe-haven accumulation.
• Intermarket Context:
  - DXY (US Dollar Index): 101.10 (Bearish rejection at 50 EMA)
  - US 10Y Real Yields: Declining (-4 bps) ➔ Macro tailwind for Gold.
  - Geopolitical Risk Index: Elevated (Middle East tensions).
🏛️ INSTITUTIONAL POSITIONING MAP:
• Smart Money Floor: Heavy COT commercial limit bids clustered at $2,635 - $2,640.
• Target Liquidity Pool: Buy-side stops resting above $2,685 swing high.
🕒 SESSION FOCUS (New York 09:30 - 16:00 EST):
• Bias to the long side. If price pulls back into the Asian Session POC ($2,644), 
  watch for delta absorption to join institutional continuation.
```

---

## 🏛️ Institutional Positioning Engine

### METHOD 1: CFTC COT (Commitment of Traders) Audit
- Tracks weekly positioning of **Commercial Hedgers (Smart Money / Bullion Banks)** vs. **Non-Commercials (Large Speculators / Hedge Funds & CTAs)**.
- **Institutional Accumulation Zone**: If Commercials are accumulating heavy net long contracts or reducing short hedges ➔ Flagged as a *"Smart Money Floor"*.
- **Speculative Squeeze Risk**: If Non-Commercial Specs reach extreme long saturation (e.g., >85th percentile) ➔ Warns of potential long-squeeze liquidation.

### METHOD 3: Liquidity Pools & Stop Hunts (Trapped Liquidity)
- **Buy-Side Liquidity (BSL)**: Resting buy stop-losses clustered above equal highs / swing highs (where breakout buyers get trapped and absorbed).
- **Sell-Side Liquidity (SSL)**: Resting sell stop-losses clustered below equal lows / swing lows (where breakdown sellers get trapped and absorbed).
- **Confluence with Pine Script v6 Indicator ("my edge")**:
  - References High Volume Node (**HVN**) shelves and Point of Control (**POC**).
  - Highlights circular absorption bubbles:
    - **🟢 Green Bubbles**: Trapped Sellers (delta absorption defending support).
    - **🔴 Red Bubbles**: Trapped Buyers (delta exhaustion at resistance).

---

## ☁️ 24/7 Zero-Sleep Cloud Deployment Guide

The service includes an asynchronous `aiohttp` web server running on port `8080` (or the dynamic `PORT` env var provided by cloud hosts) serving `/health` and `/`.

### Option A: Render (1-Click Blueprint)
1. Fork or push this repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), click **New + ➔ Blueprint**.
3. Select your repository. Render automatically reads [`render.yaml`](file:///c:/Users/abith/Downloads/Telegram%20Desktop/fundamentals-forex-futures-commodities/render.yaml).
4. Set your Environment Variables:
   - `GEMINI_API_KEY`
   - `TG_BOT_TOKEN_FOREX`
   - `TG_BOT_TOKEN_COMMODITIES`
   - `TG_BOT_TOKEN_INDICES`
5. Click **Apply**. The service deploys and connects all 3 bots automatically.

### Option B: Railway
1. In [Railway](https://railway.app/), click **New Project ➔ Deploy from GitHub repo**.
2. Railway detects [`railway.json`](file:///c:/Users/abith/Downloads/Telegram%20Desktop/fundamentals-forex-futures-commodities/railway.json) and [`Dockerfile`](file:///c:/Users/abith/Downloads/Telegram%20Desktop/fundamentals-forex-futures-commodities/Dockerfile).
3. Add environment variables in the Railway dashboard (`Variables` tab).
4. Railway keeps the instance alive 24/7 via the `/health` endpoint.

### Option C: Fly.io
1. Install `flyctl` and run:
   ```bash
   fly launch
   fly secrets set GEMINI_API_KEY="..." TG_BOT_TOKEN_FOREX="..." TG_BOT_TOKEN_COMMODITIES="..." TG_BOT_TOKEN_INDICES="..."
   fly deploy
   ```

### Option D: Local / VPS Execution
```bash
# 1. Clone repository
git clone <repo-url>
cd fundamentals-forex-futures-commodities

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env configuration
cp .env.example .env
# Edit .env with your tokens and API keys

# 4. Run test suite
python -m unittest discover tests

# 5. Start unified 24/7 orchestrator
python main.py
```

---

## 🛠️ Environment Configuration Reference

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini AI API Key | **Yes** | — |
| `TG_BOT_TOKEN_FOREX` | Telegram Bot Token for Forex Sentinel | **Yes** | — |
| `TG_BOT_TOKEN_COMMODITIES` | Telegram Bot Token for Commodities Sentinel | **Yes** | — |
| `TG_BOT_TOKEN_INDICES` | Telegram Bot Token for Indices Sentinel | **Yes** | — |
| `PORT` | Health check HTTP port for zero-sleep keepalive | No | `8080` |
| `HOST` | Health check bind address | No | `0.0.0.0` |
| `GEMINI_MODEL` | Gemini Model ID | No | `gemini-2.5-flash` |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` |

---

## 🧪 Testing & Verification

Run the comprehensive institutional test suite:
```bash
python -m unittest discover tests
```

Tests verify:
- Calendar feed ingestion and strict domain filtering.
- Method 1 CFTC COT audit logic (accumulation floor vs. spec squeeze).
- Method 3 Liquidity Pools & Pine Script v6 indicator confluence.
- Character-for-character compliance with required template formats.
- Zero-prompt Watchdog arming and simulation alert execution.
- Zero-sleep HTTP health server endpoints (`/health` and `/`).
