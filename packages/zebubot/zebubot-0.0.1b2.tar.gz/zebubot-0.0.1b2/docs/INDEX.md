# ZebuBot Documentation Index

Welcome to the ZebuBot documentation! This index will help you find the information you need to get started with algorithmic trading using ZebuBot.

## 📚 Documentation Overview

ZebuBot is a high-performance algorithmic trading platform designed specifically for Indian stock markets via MyntAPI (Noren). This documentation covers everything from basic setup to advanced strategy development.

## 🚀 Getting Started

### For Beginners
1. **[Quick Start Guide](QUICK_START_GUIDE.md)** - Get up and running in 5 minutes
2. **[Installation Guide](#installation)** - Set up ZebuBot on your system
3. **[Your First Strategy](QUICK_START_GUIDE.md#your-first-strategy)** - Create a simple RSI strategy

### For Developers
1. **[Strategy Development Guide](STRATEGY_DEVELOPMENT_GUIDE.md)** - Complete guide to creating strategies
2. **[API Reference](API_REFERENCE.md)** - Detailed function documentation
3. **[Architecture Overview](#architecture)** - Understanding the system design

## 📖 Core Documentation

### [Quick Start Guide](QUICK_START_GUIDE.md)
- **Purpose**: Get started with ZebuBot quickly
- **Audience**: Beginners, new users
- **Content**: Installation, first strategy, basic configuration
- **Time to Complete**: 5-10 minutes

### [Strategy Development Guide](STRATEGY_DEVELOPMENT_GUIDE.md)
- **Purpose**: Complete guide to creating trading strategies
- **Audience**: Strategy developers, intermediate users
- **Content**: 
  - Strategy architecture
  - Creating custom strategies
  - Configuration system
  - Available functions
  - Real-time context variables
  - Performance optimization
  - Best practices
  - Example strategies
- **Time to Complete**: 30-60 minutes

### [API Reference](API_REFERENCE.md)
- **Purpose**: Detailed function documentation
- **Audience**: Developers, advanced users
- **Content**:
  - Core functions
  - Data functions
  - Trading functions
  - Technical indicators
  - Utility functions
  - Configuration reference
  - Error handling
- **Time to Complete**: Reference material

## 🏗️ System Architecture

### Core Components
```
ZebuBot Core
├── MyntAPI Integration (Real-time data & orders)
├── Symbol Manager (Symbol lookup & conversion)
├── Performance Engine (Cython-optimized calculations)
├── Strategy Executor (Your custom strategy)
└── Risk Manager (Position sizing & controls)
```

### Data Flow
1. **Real-time Data**: WebSocket + Polling fallback
2. **Historical Data**: 30 days of 1-minute data loaded on startup
3. **Strategy Processing**: Your custom `on_tick()` function
4. **Order Execution**: Automated order placement via MyntAPI
5. **Risk Management**: Position sizing and risk controls

## 🎯 Strategy Development

### Strategy Template
- **File**: `scripts/strategy_template.py`
- **Config**: `configs/strategy_template.yaml`
- **Purpose**: Starting point for new strategies
- **Features**: Multi-indicator strategy with RSI, SMA, Bollinger Bands, MACD

### Available Indicators
- **RSI** (Relative Strength Index)
- **SMA** (Simple Moving Average)
- **EMA** (Exponential Moving Average)
- **Bollinger Bands**
- **MACD** (Moving Average Convergence Divergence)

### Configuration System
- **YAML-based**: Easy to modify and version control
- **Hierarchical**: Strategy, risk, and system parameters
- **Validation**: Automatic parameter validation
- **Override**: Command-line parameter overrides

## 📊 Trading Features

### Order Management
- **Market Orders**: Immediate execution at current price
- **Limit Orders**: Execution at specified price
- **Position Management**: Automatic position tracking
- **Order History**: Complete order audit trail

### Risk Management
- **Position Sizing**: Dynamic sizing based on signal strength
- **Margin Management**: Automatic margin calculation
- **Stop Loss**: Configurable stop loss percentages
- **Take Profit**: Configurable take profit percentages
- **Daily Limits**: Maximum daily loss and trade limits

### Multi-Symbol Trading
- **Primary Symbol**: Main symbol for signal generation
- **Additional Symbols**: Trade multiple symbols on signals
- **Portfolio Management**: Unified portfolio view
- **Risk Distribution**: Spread risk across multiple symbols

## 🚀 Performance

### Cython Optimization
- **10x Faster**: Cython-optimized indicator calculations
- **Memory Efficient**: Optimized data structures
- **Scalable**: Handle multiple symbols simultaneously
- **Fallback**: Automatic fallback to Python implementations

### Real-time Processing
- **Sub-millisecond**: Tick processing latency
- **WebSocket**: Primary real-time data source
- **Polling Fallback**: Reliable data delivery
- **Historical Context**: 30 days of historical data

## 🔧 Configuration

### Strategy Configuration
```yaml
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
    - NSE:RELIANCE-EQ
    - NSE:TCS-EQ
```

### Risk Configuration
```yaml
risk:
  min_position_inr: 1000
  max_position_pct: 0.04
  additional_symbol_position_pct: 0.005
  stop_loss_pct: 0.02
  take_profit_pct: 0.04
```

## 📈 Example Strategies

### 1. RSI Mean Reversion
- **Concept**: Buy oversold, sell overbought
- **Indicators**: RSI only
- **Signals**: RSI < 30 (buy), RSI > 70 (sell)
- **Risk**: Medium

### 2. Moving Average Crossover
- **Concept**: Trend following
- **Indicators**: SMA 20, SMA 50
- **Signals**: Fast MA crosses above/below slow MA
- **Risk**: Medium

### 3. Multi-Indicator Strategy
- **Concept**: Confirmation-based trading
- **Indicators**: RSI, SMA, Bollinger Bands, MACD
- **Signals**: Multiple indicator confirmation
- **Risk**: Low

### 4. Bollinger Bands Strategy
- **Concept**: Mean reversion with volatility
- **Indicators**: Bollinger Bands
- **Signals**: Price touches bands
- **Risk**: Medium

## 🛠️ Development

### Project Structure
```
zebubot/
├── zebubot/                 # Core library
│   ├── myntapi_integration.py
│   ├── symbol_manager.py
│   ├── performance.pyx
│   └── ...
├── scripts/                 # Strategy scripts
│   ├── myntapi_rsi_optimized.py
│   ├── strategy_template.py
│   └── ...
├── configs/                 # Configuration files
│   ├── myntapi_rsi_optimized.yaml
│   ├── strategy_template.yaml
│   └── ...
├── docs/                    # Documentation
│   ├── QUICK_START_GUIDE.md
│   ├── STRATEGY_DEVELOPMENT_GUIDE.md
│   ├── API_REFERENCE.md
│   └── INDEX.md
└── tests/                   # Test files
```

### Building from Source
```bash
# Clone repository
git clone https://github.com/your-username/zebubot.git
cd zebubot

# Install dependencies
pip install -r requirements.txt

# Build Cython extensions
python setup_cython.py build_ext --inplace

# Run tests
python -m pytest tests/
```

## 🔒 Security & Risk

### Security Features
- **Credential Management**: Secure credential storage
- **API Security**: Encrypted API communication
- **Access Control**: User-based access controls
- **Audit Trail**: Complete activity logging

### Risk Management
- **Position Limits**: Maximum position sizes
- **Daily Limits**: Maximum daily loss
- **Stop Loss**: Automatic stop loss orders
- **Margin Monitoring**: Real-time margin tracking

### Disclaimer
⚠️ **Important**: This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## 📞 Support & Community

### Getting Help
1. **Documentation**: Check this index and linked guides
2. **GitHub Issues**: Report bugs and request features
3. **Community Forum**: Ask questions and share strategies
4. **Email Support**: Direct support for premium users

### Contributing
1. **Fork Repository**: Create your own fork
2. **Create Branch**: Work on feature or bug fix
3. **Submit PR**: Submit pull request for review
4. **Code Review**: Participate in code review process

### Community Guidelines
- **Be Respectful**: Treat all community members with respect
- **Share Knowledge**: Help others learn and grow
- **Follow Rules**: Adhere to community guidelines
- **Report Issues**: Help improve the platform

## 📋 Quick Reference

### Essential Commands
```bash
# Run strategy
python -m zebubot --config configs/my_strategy.yaml --script scripts/my_strategy.py

# Build Cython
python setup_cython.py build_ext --inplace

# Run tests
python -m pytest tests/

# Install dependencies
pip install -r requirements.txt
```

### Key Files
- **Strategy Template**: `scripts/strategy_template.py`
- **Config Template**: `configs/strategy_template.yaml`
- **Main Integration**: `zebubot/myntapi_integration.py`
- **Performance Module**: `zebubot/performance.pyx`

### Important Functions
- **`on_tick(symbol, ticker_data)`**: Main strategy function
- **`place_order(...)`**: Place trading orders
- **`get_ticker(symbol)`**: Get current price data
- **`get_tpseries(...)`**: Get historical data
- **`calculate_rsi(prices, period)`**: Calculate RSI indicator

## 🎯 Next Steps

1. **Start Here**: Read the [Quick Start Guide](QUICK_START_GUIDE.md)
2. **Learn More**: Study the [Strategy Development Guide](STRATEGY_DEVELOPMENT_GUIDE.md)
3. **Reference**: Use the [API Reference](API_REFERENCE.md) as needed
4. **Practice**: Try the example strategies
5. **Create**: Build your own custom strategies
6. **Share**: Contribute to the community

---

**Happy Trading! 🚀📈**

*Built with ❤️ for the Indian trading community*
