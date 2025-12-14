"""
Contract specifications for NSE futures
Updated: December 2025
"""

NSE_FUTURES = {
    "SCOM": {
        "name": "Safaricom",
        "sector": "Telecommunications",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 28.21
    },
    "EQTY": {
        "name": "Equity Group",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 60.13
    },
    "KCBG": {
        "name": "KCB Group",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 56.84
    },
    "EABL": {
        "name": "East African Breweries",
        "sector": "Manufacturing",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 230.45
    },
    "BATK": {
        "name": "BAT Kenya",
        "sector": "Manufacturing",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 437.40
    },
    "ABSA": {
        "name": "ABSA Kenya",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 22.05
    },
    "NCBA": {
        "name": "NCBA Group",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 78.17
    },
    "COOP": {
        "name": "Co-operative Bank",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 22.00
    },
    "SCBK": {
        "name": "Standard Chartered Kenya",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 287.60
    },
    "IMHP": {
        "name": "I&M Holdings",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 45.45
    },
    "N25I": {
        "name": "NSE 25 Index Future",
        "sector": "Index",
        "min_tick": 0.1,
        "contract_size": 1,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 3155.58
    },
    "25MN": {
        "name": "NSE 25 Mini Future",
        "sector": "Index",
        "min_tick": 0.1,
        "contract_size": 1,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 3178.41
    },
    "10MN": {
        "name": "NSE 10 Mini Future",
        "sector": "Index",
        "min_tick": 0.1,
        "contract_size": 1,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"],
        "mtm_price": 1614.38
    }
}