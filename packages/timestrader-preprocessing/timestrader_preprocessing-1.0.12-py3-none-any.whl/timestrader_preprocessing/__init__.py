"""
TimeStrader Preprocessing Package

A comprehensive data preprocessing package optimized for TimesNet and PPO model training.
Provides historical data processing, normalization, and technical indicator calculation
for financial time series data.

Version: 1.0.10
"""

__version__ = "1.0.11"
__author__ = "TimeStrader Team"
__email__ = "team@timestrader.com"

# Core imports for easy access
from .historical.processor import HistoricalProcessor

__all__ = [
    "HistoricalProcessor"
]