"""
Institutional Macro Intelligence Telegram Ecosystem
Configuration and Domain Definitions
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys & Tokens
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TG_BOT_TOKEN_FOREX = os.getenv("TG_BOT_TOKEN_FOREX", "")
TG_BOT_TOKEN_COMMODITIES = os.getenv("TG_BOT_TOKEN_COMMODITIES", "")
TG_BOT_TOKEN_INDICES = os.getenv("TG_BOT_TOKEN_INDICES", "")

# Server & Runtime Configuration
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() in ("true", "1", "yes")

# Gemini Model Settings
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]


@dataclass
class DomainConfig:
    domain_id: str
    display_name: str
    bot_name: str
    assets: List[str]
    currencies: List[str]
    central_banks: List[str]
    key_drivers: List[str]
    high_impact_keywords: List[str]
    cot_category: str
    default_session_window: str = "New York 09:30 - 16:00 EST"
    regime_header: str = ""


# Domain Isolation Specifications
DOMAIN_CONFIGS: Dict[str, DomainConfig] = {
    "forex": DomainConfig(
        domain_id="forex",
        display_name="Forex & G10 Currencies",
        bot_name="FOREX SENTINEL",
        assets=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"],
        currencies=["USD", "EUR", "GBP", "JPY", "AUD"],
        central_banks=["Fed", "ECB", "BoE", "BoJ"],
        key_drivers=[
            "Fed / ECB / BoE / BoJ Interest Rate Decisions",
            "US CPI & Core Inflation",
            "Non-Farm Payrolls (NFP)",
            "DXY Dollar Index Dynamics",
            "G10 Yield Differentials",
        ],
        high_impact_keywords=[
            "CPI", "Rate", "FOMC", "NFP", "Non-Farm", "ECB", "BOE", "BOJ",
            "Interest", "GDP", "Retail Sales", "Employment", "Fed"
        ],
        cot_category="Financial Currencies (EUR, GBP, JPY, AUD)",
        regime_header="EURUSD & G10 / FOREX"
    ),
    "commodities": DomainConfig(
        domain_id="commodities",
        display_name="Commodities & Precious Metals",
        bot_name="COMMODITIES SENTINEL",
        assets=["XAUUSD", "XAGUSD", "USOIL"],
        currencies=["USD"],
        central_banks=["Fed", "OPEC+"],
        key_drivers=[
            "US 10-Year Real Yields (TIPS / TNX)",
            "DXY (US Dollar Index)",
            "OPEC+ Production Quotas & Inventories",
            "Geopolitical Risk Index (GPR)",
            "Central Bank Gold Accumulation",
        ],
        high_impact_keywords=[
            "CPI", "PCE", "Crude", "Oil", "Inventory", "OPEC", "Yield",
            "FOMC", "10-Year", "Treasury", "War", "Middle East", "Gold"
        ],
        cot_category="Commodities (Gold, Silver, WTI Crude)",
        regime_header="XAUUSD / COMMODITIES"
    ),
    "indices": DomainConfig(
        domain_id="indices",
        display_name="US Futures & Wall Street Indices",
        bot_name="FUTURES & INDICES SENTINEL",
        assets=["US30", "NAS100", "SPX500"],
        currencies=["USD"],
        central_banks=["Federal Reserve"],
        key_drivers=[
            "US GDP & Economic Growth",
            "ISM Manufacturing & Services PMIs",
            "Mega-Cap Tech Earnings (Magnificent 7)",
            "Federal Reserve Rate Cut Probabilities",
            "Systemic Liquidity & VIX Volatility",
        ],
        high_impact_keywords=[
            "GDP", "ISM", "PMI", "FOMC", "Fed", "Earnings", "CPI", "Jobs",
            "Consumer Confidence", "Retail Sales", "Treasury Refunding"
        ],
        cot_category="Equity Indices (E-mini S&P 500, Nasdaq 100, Dow 30)",
        regime_header="US30 & NAS100 / FUTURES & INDICES"
    ),
}
