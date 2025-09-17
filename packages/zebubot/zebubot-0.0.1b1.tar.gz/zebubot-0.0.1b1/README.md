# ZebuBot - Advanced Algorithmic Trading Platform

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MyntAPI](https://img.shields.io/badge/MyntAPI-Noren-orange.svg)](https://api.shoonya.com)

ZebuBot is a high-performance algorithmic trading platform designed specifically for Indian stock markets via MyntAPI (Noren). It provides a flexible framework for creating custom trading strategies with real-time data processing, technical indicators, and automated order execution.

## 🚀 Key Features

- **Real-time Data**: WebSocket + Polling fallback for reliable data feeds
- **Cython Optimization**: High-performance technical indicator calculations
- **Historical Data**: Automatic loading of 30 days historical data for accurate indicators
- **Multi-Symbol Trading**: Trade multiple symbols simultaneously
- **Risk Management**: Built-in position sizing and risk controls
- **Flexible Configuration**: YAML-based strategy configuration
- **MyntAPI Integration**: Seamless integration with Indian stock markets

## 📊 Performance

- **Cython Optimized**: Up to 10x faster indicator calculations
- **Real-time Processing**: Sub-millisecond tick processing
- **Memory Efficient**: Automatic data management with deque buffers
- **Scalable**: Handle multiple symbols and strategies simultaneously

## 🛠️ Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/zebubot.git
cd zebubot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up credentials**:
```bash
python setup_credentials.py
```

4. **Build Cython optimizations** (optional, for better performance):
```bash
python setup_cython.py build_ext --inplace
```

### Your First Strategy

Create a simple RSI strategy:

```python
# scripts/my_strategy.py
from collections import deque
import pandas as pd

price_history = deque(maxlen=1000)
rsi_period = 14
last_signal = None

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def on_tick(symbol, ticker_data):
    global last_signal
    
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= rsi_period + 1:
        prices = list(price_history)
        rsi = calculate_rsi(prices, rsi_period)
        
        if rsi is not None:
            if rsi < 30 and last_signal != 'BUY':
                print(f"🟢 BUY Signal! RSI: {rsi:.2f}")
                last_signal = 'BUY'
                place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
            elif rsi > 70 and last_signal != 'SELL':
                print(f"🔴 SELL Signal! RSI: {rsi:.2f}")
                last_signal = 'SELL'
                place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')

def main():
    on_tick(current_symbol, ticker_data)
```

Create configuration:

```yaml
# configs/my_strategy.yaml
symbols:
  - NSE:RELIANCE-EQ
exchange: myntapi
strategy:
  rsi_period: 14
risk:
  min_position_inr: 1000
  max_position_pct: 0.02
```

Run your strategy:

```bash
python -m zebubot --config configs/my_strategy.yaml --script scripts/my_strategy.py
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START_GUIDE.md)** - Get started in 5 minutes
- **[Strategy Development Guide](docs/STRATEGY_DEVELOPMENT_GUIDE.md)** - Complete guide to creating strategies
- **[API Reference](docs/API_REFERENCE.md)** - Detailed function documentation

## 🏗️ Architecture

```
ZebuBot Core
├── MyntAPI Integration (Real-time data & orders)
├── Symbol Manager (Symbol lookup & conversion)
├── Performance Engine (Cython-optimized calculations)
├── Strategy Executor (Your custom strategy)
└── Risk Manager (Position sizing & controls)
```

## 📈 Available Indicators

- **RSI** (Relative Strength Index)
- **SMA** (Simple Moving Average)
- **EMA** (Exponential Moving Average)
- **Bollinger Bands**
- **MACD** (Moving Average Convergence Divergence)
- **Custom Indicators** (Easy to add)

## 🔧 Configuration

### Strategy Configuration

```yaml
symbols:
  - NSE:RELIANCE-EQ
  - NSE:TCS-EQ
exchange: myntapi
strategy:
  rsi_period: 14
  sma_fast: 20
  sma_slow: 50
  bb_period: 20
  bb_stddev: 2.0
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9
  additional_symbols:
    - NSE:INFY-EQ
    - NSE:HINDUNILVR-EQ
risk:
  min_position_inr: 1000
  max_position_pct: 0.04
  additional_symbol_position_pct: 0.005
  stop_loss_pct: 0.02
  take_profit_pct: 0.04
```

## 🎯 Example Strategies

### 1. RSI Mean Reversion

```python
def on_tick(symbol, ticker_data):
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= 15:
        prices = list(price_history)
        rsi = calculate_rsi(prices, 14)
        
        if rsi < 30:
            print("🟢 RSI Oversold - BUY Signal")
            place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
        elif rsi > 70:
            print("🔴 RSI Overbought - SELL Signal")
            place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')
```

### 2. Moving Average Crossover

```python
def on_tick(symbol, ticker_data):
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= 50:
        prices = list(price_history)
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)
        
        if sma_20 > sma_50 and last_signal != 'BUY':
            print("🟢 Bullish Crossover - BUY Signal")
            last_signal = 'BUY'
            place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
        elif sma_20 < sma_50 and last_signal != 'SELL':
            print("🔴 Bearish Crossover - SELL Signal")
            last_signal = 'SELL'
            place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')
```

### 3. Multi-Indicator Strategy

```python
def on_tick(symbol, ticker_data):
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= 50:
        prices = list(price_history)
        
        # Calculate multiple indicators
        rsi = calculate_rsi(prices, 14)
        sma_20 = calculate_sma(prices, 20)
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(prices, 20, 2.0)
        macd, macd_signal, macd_hist = calculate_macd(prices, 12, 26, 9)
        
        # Count signals
        bullish_signals = 0
        if rsi and rsi < 30:
            bullish_signals += 1
        if sma_20 and current_price > sma_20:
            bullish_signals += 1
        if bb_lower and current_price < bb_lower:
            bullish_signals += 1
        if macd and macd_signal and macd > macd_signal:
            bullish_signals += 1
        
        # Generate signal based on confirmation
        if bullish_signals >= 3 and last_signal != 'BUY':
            print(f"🟢 Strong BUY Signal! ({bullish_signals}/4 confirmations)")
            last_signal = 'BUY'
            place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
```

## 🚀 Performance Optimization

### Cython Integration

ZebuBot includes Cython-optimized functions for maximum performance:

```python
try:
    from zebubot.performance import (
        calculate_rsi_fast,
        calculate_sma_fast,
        calculate_ema_fast,
        calculate_bollinger_bands_fast,
        calculate_macd_fast,
        process_ticker_data_fast
    )
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False
```

### Memory Management

```python
from collections import deque
import numpy as np

# Use deque for efficient price history
price_history = deque(maxlen=1000)  # Automatically removes old data

# Use numpy arrays for calculations
prices_array = np.array(price_list, dtype=np.float64)
```

## 🔒 Risk Management

### Built-in Risk Controls

- **Position Sizing**: Dynamic position sizing based on signal strength
- **Margin Management**: Automatic margin calculation and monitoring
- **Stop Loss**: Configurable stop loss percentages
- **Take Profit**: Configurable take profit percentages
- **Maximum Position**: Limits on maximum position size

### Risk Management Example

```python
def calculate_position_size(signal_strength, available_margin):
    base_size = available_margin * 0.01  # 1% base
    signal_multiplier = min(signal_strength / 4.0, 1.0)  # Max 4x
    position_size = base_size * signal_multiplier
    
    # Apply risk limits
    max_size = available_margin * risk.get('max_position_pct', 0.04)
    min_size = risk.get('min_position_inr', 1000)
    
    return max(min_size, min(position_size, max_size))
```

## 📊 Real-time Data

### Data Sources

- **Primary**: MyntAPI WebSocket feed
- **Fallback**: MyntAPI REST API polling
- **Historical**: MyntAPI tpseries endpoint

### Data Format

```python
ticker_data = {
    'symbol': 'NSE:RELIANCE-EQ',
    'price': 2450.50,
    'volume': 1500000,
    'timestamp': 1699123456789,
    'high': 2460.00,
    'low': 2440.00,
    'open': 2445.00,
    'close': 2450.50
}
```

## 🛠️ Development

### Project Structure

```
zebubot/
├── zebubot/                 # Core library
│   ├── myntapi_integration.py
│   ├── symbol_manager.py
│   ├── performance.pyx      # Cython optimizations
│   └── ...
├── scripts/                 # Strategy scripts
│   ├── myntapi_rsi_optimized.py
│   └── ...
├── configs/                 # Configuration files
│   ├── myntapi_rsi_optimized.yaml
│   └── ...
├── docs/                    # Documentation
│   ├── QUICK_START_GUIDE.md
│   ├── STRATEGY_DEVELOPMENT_GUIDE.md
│   └── API_REFERENCE.md
└── tests/                   # Test files
```

### Building Cython Extensions

```bash
# Build Cython extensions
python setup_cython.py build_ext --inplace

# Or use the build script
python build_cython.py
```

### Running Tests

```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## 📞 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs and request features on GitHub
- **Community**: Join our Discord/Telegram group

## 🙏 Acknowledgments

- MyntAPI (Noren) for providing the trading API
- The Python community for excellent libraries
- Contributors and users who help improve ZebuBot

---

**Happy Trading! 🚀📈**

*Built with ❤️ for the Indian trading community*
