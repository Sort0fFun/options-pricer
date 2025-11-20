"""
Contract specifications for NSE futures
"""

NSE_FUTURES = {
    "SCOM": {
        "name": "Safaricom",
        "sector": "Telecommunications",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"]
    },
    "EQTY": {
        "name": "Equity Group",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"]
    },
    "KCB": {
        "name": "KCB Group",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"]
    },
    "ABSA": {
        "name": "ABSA Kenya",
        "sector": "Banking",
        "min_tick": 0.05,
        "contract_size": 100,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"]
    },
    "NSE25": {
        "name": "NSE 25 Index Future",
        "sector": "Index",
        "min_tick": 0.1,
        "contract_size": 1,
        "expiry_months": ["MAR", "JUN", "SEP", "DEC"]
    }
}