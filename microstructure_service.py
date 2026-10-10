"""
Market Microstructure & Liquidity Pools Service
Implements METHOD 3:
- Buy-Side Liquidity (BSL) & Sell-Side Liquidity (SSL) stop clusters
- Confluence with Pine Script v6 Indicator ("my edge"):
  * High Volume Node (HVN) shelves
  * Point of Control (POC) (e.g., Asian Session POC, Weekly POC)
  * Trapped Buyer / Trapped Seller absorption bubbles:
    - Green Bubbles: Trapped Sellers / Delta Absorption at support
    - Red Bubbles: Trapped Buyers / Delta Exhaustion at resistance
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("MicrostructureService")

# Microstructure Liquidity Map for Key Assets
MICROSTRUCTURE_MAP: Dict[str, Dict[str, Any]] = {
    # COMMODITIES
    "XAUUSD": {
        "current_ref_price": 2652.0,
        "target_liquidity_pool": "Buy-side stops resting above $2,685 swing high.",
        "bsl_level": "$2,685.00",
        "ssl_level": "$2,632.00",
        "hvn_support": "2,642",
        "asian_poc": "$2,644",
        "session_focus_text": (
            "Bias to the long side. If price pulls back into the Asian Session POC ($2,644), "
            "watch for delta absorption to join institutional continuation."
        ),
        "order_flow_alert": (
            "Institutions are defending the 2,642 HVN support. Look only for Trapped Sellers "
            "(Green Bubbles) to ride the trend up!"
        )
    },
    "XAGUSD": {
        "current_ref_price": 31.80,
        "target_liquidity_pool": "Buy-side liquidity resting above $32.40 double top.",
        "bsl_level": "$32.40",
        "ssl_level": "$31.10",
        "hvn_support": "$31.35",
        "asian_poc": "$31.50",
        "session_focus_text": (
            "Bullish continuation bias. Watch for retest of the $31.50 Asian POC. "
            "Confirm with Green Bubble trapped seller absorption before engaging."
        ),
        "order_flow_alert": (
            "Price accepted above the $31.35 HVN shelf. Target BSL pool at $32.40. "
            "Look for Trapped Sellers (Green Bubbles) on 5m pullbacks!"
        )
    },
    "USOIL": {
        "current_ref_price": 73.40,
        "target_liquidity_pool": "Sell-side liquidity resting below $71.80 swing low.",
        "bsl_level": "$75.20",
        "ssl_level": "$71.80",
        "hvn_support": "$72.40",
        "asian_poc": "$73.10",
        "session_focus_text": (
            "Range-bound consolidation. Resistance at $74.60 HVN; support at $72.40. "
            "Watch for trapped breakout buyers (Red Bubbles) near resistance."
        ),
        "order_flow_alert": (
            "Heavy seller absorption at the $72.40 HVN. Wait for trapped breakdown sellers "
            "(Green Bubbles) before triggering longs!"
        )
    },

    # FOREX
    "EURUSD": {
        "current_ref_price": 1.0965,
        "target_liquidity_pool": "Buy-side stops resting above 1.1015 London high.",
        "bsl_level": "1.1015",
        "ssl_level": "1.0890",
        "hvn_support": "1.0925",
        "asian_poc": "1.0940",
        "session_focus_text": (
            "Long bias targeting 1.1015 BSL. If price dips toward the 1.0940 Asian POC, "
            "look for footprint delta absorption (Green Bubbles) to confirm buyer defense."
        ),
        "order_flow_alert": (
            "Institutions are defending the 1.0925 HVN support shelf. Look only for Trapped Sellers "
            "(Green Bubbles) to ride the continuation up!"
        )
    },
    "GBPUSD": {
        "current_ref_price": 1.3120,
        "target_liquidity_pool": "Sell-side stops resting below 1.3060 equal lows.",
        "bsl_level": "1.3180",
        "ssl_level": "1.3060",
        "hvn_support": "1.3090",
        "asian_poc": "1.3105",
        "session_focus_text": (
            "Caution on long breakout due to spec saturation. Look for liquidity raid "
            "under 1.3060 SSL followed by immediate reclaim and Green Bubble absorption."
        ),
        "order_flow_alert": (
            "Institutional liquidity sweep below 1.3060 SSL completed. Reclaim above 1.3090 HVN "
            "confirms trapped sellers (Green Bubbles)!"
        )
    },
    "USDJPY": {
        "current_ref_price": 148.80,
        "target_liquidity_pool": "Sell-side liquidity resting below 147.50 swing low.",
        "bsl_level": "150.20",
        "ssl_level": "147.50",
        "hvn_support": "148.20",
        "asian_poc": "148.60",
        "session_focus_text": (
            "Short bias on dollar weakness. Rejection at 149.40 HVN resistance confirms "
            "trapped buyers (Red Bubbles). Target 147.50 SSL pool."
        ),
        "order_flow_alert": (
            "Smart money absorption defending 149.40 resistance. Look for Trapped Buyers "
            "(Red Bubbles) to position for the dump into 147.50 SSL!"
        )
    },
    "AUDUSD": {
        "current_ref_price": 0.6740,
        "target_liquidity_pool": "Buy-side stops resting above 0.6795 swing high.",
        "bsl_level": "0.6795",
        "ssl_level": "0.6690",
        "hvn_support": "0.6715",
        "asian_poc": "0.6725",
        "session_focus_text": (
            "Bullish continuation. Holding above the 0.6725 Asian POC targets 0.6795 BSL. "
            "Monitor volume delta for trapped sellers (Green Bubbles)."
        ),
        "order_flow_alert": (
            "Institutions defending the 0.6715 HVN volume shelf. Look for Trapped Sellers "
            "(Green Bubbles) to ride the commodity bid!"
        )
    },

    # INDICES / FUTURES
    "US30": {
        "current_ref_price": 42350.0,
        "target_liquidity_pool": "Buy-side stops resting above 42,600 all-time high shelf.",
        "bsl_level": "42,600",
        "ssl_level": "41,950",
        "hvn_support": "42,120",
        "asian_poc": "42,240",
        "session_focus_text": (
            "Long bias into NY open. If price pulls back into 42,240 Asian POC / 42,120 HVN, "
            "look for aggressive delta absorption to target 42,600 BSL."
        ),
        "order_flow_alert": (
            "Dealers defending 42,120 HVN support. Look only for Trapped Sellers "
            "(Green Bubbles) to ride the institutional momentum up!"
        )
    },
    "NAS100": {
        "current_ref_price": 20180.0,
        "target_liquidity_pool": "Buy-side stops resting above 20,450 major swing high.",
        "bsl_level": "20,450",
        "ssl_level": "19,920",
        "hvn_support": "20,040",
        "asian_poc": "20,110",
        "session_focus_text": (
            "Bullish tech trend. Pullbacks into 20,110 Asian POC provide high-probability "
            "long re-entries. Confirm with Pine Script v6 Green Bubbles."
        ),
        "order_flow_alert": (
            "Institutions are defending the 20,040 HVN support shelf. Look only for Trapped Sellers "
            "(Green Bubbles) to ride the trend up!"
        )
    },
    "SPX500": {
        "current_ref_price": 5780.0,
        "target_liquidity_pool": "Buy-side stops resting above 5,825 swing high.",
        "bsl_level": "5,825",
        "ssl_level": "5,715",
        "hvn_support": "5,745",
        "asian_poc": "5,760",
        "session_focus_text": (
            "Systematic CTA bid active. Retest of 5,760 Asian POC with absorption "
            "favors long continuation toward 5,825 BSL pool."
        ),
        "order_flow_alert": (
            "CTAs defending 5,745 HVN volume shelf. Look only for Trapped Sellers "
            "(Green Bubbles) to capture the trend expansion!"
        )
    },
}


def get_microstructure_data(domain_id: str, symbol: str = "") -> Dict[str, Any]:
    """Retrieves microstructure levels, liquidity pools, and indicator confluence."""
    if not symbol:
        if domain_id == "commodities":
            symbol = "XAUUSD"
        elif domain_id == "forex":
            symbol = "EURUSD"
        else:
            symbol = "NAS100"

    data = MICROSTRUCTURE_MAP.get(symbol, MICROSTRUCTURE_MAP["XAUUSD"])
    return {
        "symbol": symbol,
        "target_liquidity_pool": data["target_liquidity_pool"],
        "bsl_level": data["bsl_level"],
        "ssl_level": data["ssl_level"],
        "hvn_support": data["hvn_support"],
        "asian_poc": data["asian_poc"],
        "session_focus_text": data["session_focus_text"],
        "order_flow_alert": data["order_flow_alert"],
    }
