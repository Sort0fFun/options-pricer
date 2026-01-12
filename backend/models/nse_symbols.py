"""
NSE (Nairobi Securities Exchange) Derivatives Symbols Configuration

Contains symbol definitions, metadata, and utility functions for NSE derivatives trading.
"""

from typing import Dict, List, Optional


# NSE Derivatives Symbols
NSE_SYMBOLS: Dict[str, Dict] = {
    # Index Futures
    "N25I": {
        "name": "NSE 25 Index",
        "type": "INDEX",
        "description": "NSE 25 Share Index Futures",
        "contract_size": 1000,
        "tick_size": 0.25,
        "currency": "KES"
    },
    "25MN": {
        "name": "NSE 25 Mini Index",
        "type": "INDEX",
        "description": "NSE 25 Mini Share Index Futures",
        "contract_size": 100,
        "tick_size": 0.25,
        "currency": "KES"
    },
    "10MN": {
        "name": "NSE 10 Mini Index",
        "type": "INDEX",
        "description": "NSE 10 Mini Share Index Futures",
        "contract_size": 100,
        "tick_size": 0.25,
        "currency": "KES"
    },
    
    # Single Stock Futures - Banking Sector
    "SCOM": {
        "name": "Safaricom PLC",
        "type": "STOCK",
        "sector": "Telecommunications",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "EQTY": {
        "name": "Equity Group Holdings",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "KCBG": {
        "name": "KCB Group PLC",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "EABL": {
        "name": "East African Breweries Ltd",
        "type": "STOCK",
        "sector": "Manufacturing",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "BATK": {
        "name": "BAT Kenya PLC",
        "type": "STOCK",
        "sector": "Manufacturing",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "ABSA": {
        "name": "ABSA Bank Kenya PLC",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "NCBA": {
        "name": "NCBA Group PLC",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "COOP": {
        "name": "Co-operative Bank of Kenya",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "SCBK": {
        "name": "Standard Chartered Bank Kenya",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "IMHP": {
        "name": "I&M Holdings PLC",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "SBIC": {
        "name": "Stanbic Holdings PLC",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "DTBK": {
        "name": "Diamond Trust Bank Kenya",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "HFCK": {
        "name": "HF Group PLC",
        "type": "STOCK",
        "sector": "Banking",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "NMG": {
        "name": "Nation Media Group",
        "type": "STOCK",
        "sector": "Media",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "KPLC": {
        "name": "Kenya Power & Lighting Co",
        "type": "STOCK",
        "sector": "Energy",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "KQ": {
        "name": "Kenya Airways",
        "type": "STOCK",
        "sector": "Aviation",
        "contract_size": 1000,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "BAMB": {
        "name": "Bamburi Cement",
        "type": "STOCK",
        "sector": "Construction",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    },
    "ARM": {
        "name": "ARM Cement PLC",
        "type": "STOCK",
        "sector": "Construction",
        "contract_size": 100,
        "tick_size": 0.05,
        "currency": "KES"
    }
}


def get_symbol_list() -> List[Dict]:
    """Get list of all symbols for dropdown."""
    return [
        {
            "symbol": k,
            "name": v["name"],
            "type": v["type"],
            "sector": v.get("sector", "")
        }
        for k, v in NSE_SYMBOLS.items()
    ]


def get_stocks_only() -> List[Dict]:
    """Get only stock symbols."""
    return [
        {
            "symbol": k,
            "name": v["name"],
            "sector": v.get("sector", "")
        }
        for k, v in NSE_SYMBOLS.items()
        if v["type"] == "STOCK"
    ]


def get_indices_only() -> List[Dict]:
    """Get only index symbols."""
    return [
        {
            "symbol": k,
            "name": v["name"]
        }
        for k, v in NSE_SYMBOLS.items()
        if v["type"] == "INDEX"
    ]


def get_symbol_info(symbol: str) -> Optional[Dict]:
    """Get detailed info for a symbol."""
    return NSE_SYMBOLS.get(symbol.upper())


def get_symbols_by_sector(sector: str) -> List[Dict]:
    """Get symbols filtered by sector."""
    return [
        {
            "symbol": k,
            "name": v["name"],
            "sector": v.get("sector", "")
        }
        for k, v in NSE_SYMBOLS.items()
        if v.get("sector", "").lower() == sector.lower()
    ]


def get_all_sectors() -> List[str]:
    """Get list of all available sectors."""
    sectors = set()
    for v in NSE_SYMBOLS.values():
        if "sector" in v:
            sectors.add(v["sector"])
    return sorted(list(sectors))
