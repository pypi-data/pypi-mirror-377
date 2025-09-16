# TimeStrader Preprocessing Package

[![PyPI version](https://badge.fury.io/py/timestrader-preprocessing.svg)](https://badge.fury.io/py/timestrader-preprocessing)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A comprehensive data preprocessing package optimized for TimesNet and PPO model training in financial trading systems. This package provides historical data processing, normalization, and technical indicator calculation for financial time series data.

## Features

- **Historical Data Processing**: Efficient processing of financial time series data
- **Advanced Normalization**: Multiple normalization methods including z-score with customizable scalers
- **Technical Indicators**: Built-in technical analysis indicators
- **Data Leakage Prevention**: Proper train/validation/test splitting with scaler management
- **Performance Optimized**: Designed for high-frequency trading applications

## Installation

```bash
pip install timestrader-preprocessing
```

## Quick Start

```python
import pandas as pd
from timestrader_preprocessing import HistoricalProcessor

# Initialize processor
processor = HistoricalProcessor()

# Process your financial data
data = pd.DataFrame({
    'open': [100, 101, 102, 103, 104],
    'high': [101, 102, 103, 104, 105],
    'low': [99, 100, 101, 102, 103],
    'close': [100.5, 101.5, 102.5, 103.5, 104.5],
    'volume': [1000, 1100, 1200, 1300, 1400]
})

# Normalize data with proper train/validation/test splitting
train_data, scaler = processor.normalize_data(train_data, return_scaler=True)
val_data = processor.normalize_data(val_data, scaler=scaler)
test_data = processor.normalize_data(test_data, scaler=scaler)
```

## Advanced Usage

### Data Leakage Prevention

The package provides robust data leakage prevention for machine learning pipelines:

```python
from sklearn.preprocessing import StandardScaler
from timestrader_preprocessing import HistoricalProcessor

processor = HistoricalProcessor()

# Training phase - fit scaler on training data only
train_normalized, scaler = processor.normalize_data(
    training_data,
    return_scaler=True,
    method='zscore'
)

# Validation phase - use existing scaler
val_normalized = processor.normalize_data(
    validation_data,
    scaler=scaler
)

# Test phase - use existing scaler
test_normalized = processor.normalize_data(
    test_data,
    scaler=scaler
)
```

### Technical Indicators

```python
# Calculate technical indicators
processed_data = processor.calculate_technical_indicators(data)

# Available indicators include:
# - Moving Averages (SMA, EMA)
# - RSI (Relative Strength Index)
# - MACD (Moving Average Convergence Divergence)
# - Bollinger Bands
# - And many more...
```

## Requirements

- Python 3.9+
- pandas>=2.0.0
- numpy>=1.26.0
- scikit-learn>=1.3.0
- pydantic>=1.10.0

## Integration with TimeStrader

This package is designed to work seamlessly with the TimeStrader trading system:

1. **TimesNet Training**: Provides properly normalized historical data for time series forecasting
2. **PPO Training**: Supplies normalized features with proper train/validation/test splits
3. **Production Inference**: Efficient real-time data processing for trading decisions

## Version History

### Version 1.0.9
- Fixed data leakage prevention in normalize_data method
- Added scaler parameter support for consistent normalization
- Improved train/validation/test data splitting
- Enhanced performance for high-frequency trading applications

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support and questions, please visit our [GitHub repository](https://github.com/your-org/timestrader).

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.