"""
Gapless Crypto Data - Ultra-fast cryptocurrency data collection with zero gaps guarantee

Core Features:
- 🚀 22x faster than API calls via Binance public data repository
- 📊 Full 11-column microstructure format with order flow and liquidity metrics
- 🔒 Zero gaps guarantee through authentic API-first validation
- ⚡ UV-first modern Python tooling
- 🛡️ Corruption-proof atomic file operations
- 📊 Multi-timeframe support (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h)
- 🔧 Gap detection and filling with authentic data only
- 📈 Production-grade data collection for quantitative trading

Usage:
    from gapless_crypto_data import BinancePublicDataCollector, UniversalGapFiller

    # Collect data
    collector = BinancePublicDataCollector()
    collector.collect_data(
        symbol="SOLUSDT",
        timeframes=["1m", "5m", "1h"],
        start_date="2023-01-01",
        end_date="2023-12-31"
    )

    # Fill gaps
    gap_filler = UniversalGapFiller()
    gap_filler.fill_gaps(directory="./data")

CLI Usage:
    uv run gapless-crypto-data --symbol SOLUSDT --timeframes 1m,3m,5m
    uv run gapless-crypto-data --fill-gaps --directory ./data
"""

__version__ = "2.1.1"
__author__ = "Eon Labs"
__email__ = "terry@eonlabs.ai"

from .collectors.binance_public_data_collector import BinancePublicDataCollector
from .gap_filling.safe_file_operations import AtomicCSVOperations, SafeCSVMerger
from .gap_filling.universal_gap_filler import UniversalGapFiller

__all__ = [
    "BinancePublicDataCollector",
    "UniversalGapFiller",
    "AtomicCSVOperations",
    "SafeCSVMerger",
]
