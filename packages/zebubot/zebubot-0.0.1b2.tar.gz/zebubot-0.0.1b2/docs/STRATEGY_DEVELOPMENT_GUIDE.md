# ZebuBot Trading Strategy Development Guide

## Table of Contents
1. [Overview](#overview)
2. [Strategy Architecture](#strategy-architecture)
3. [Creating Your First Strategy](#creating-your-first-strategy)
4. [Configuration System](#configuration-system)
5. [Available Functions](#available-functions)
6. [Real-time Context Variables](#real-time-context-variables)
7. [Performance Optimization](#performance-optimization)
8. [Best Practices](#best-practices)
9. [Example Strategies](#example-strategies)
10. [Troubleshooting](#troubleshooting)

## Overview

ZebuBot is a high-performance algorithmic trading platform designed for Indian stock markets via MyntAPI (Noren). It provides a flexible framework for creating custom trading strategies with real-time data processing, technical indicators, and automated order execution.

### Key Features
- **Real-time Data**: WebSocket + Polling fallback for reliable data feeds
- **Cython Optimization**: High-performance technical indicator calculations
- **Historical Data**: Automatic loading of 30 days historical data for accurate indicators
- **Multi-Symbol Trading**: Trade multiple symbols simultaneously
- **Risk Management**: Built-in position sizing and risk controls
- **Flexible Configuration**: YAML-based strategy configuration

## Strategy Architecture

### Core Components

```
ZebuBot Core
├── MyntAPI Integration (Real-time data & orders)
├── Symbol Manager (Symbol lookup & conversion)
├── Performance Engine (Cython-optimized calculations)
├── Strategy Executor (Your custom strategy)
└── Risk Manager (Position sizing & controls)
```

### Strategy Lifecycle

1. **Initialization**: Load configuration, connect to MyntAPI
2. **Historical Data Loading**: Load 30 days of historical data
3. **Real-time Processing**: Process live ticker data
4. **Indicator Calculation**: Calculate technical indicators
5. **Signal Generation**: Generate buy/sell signals
6. **Order Execution**: Place orders based on signals
7. **Risk Management**: Monitor positions and risk

## Creating Your First Strategy

### Step 1: Create Strategy File

Create a new Python file in the `scripts/` directory:

```python
# scripts/my_custom_strategy.py
"""
My Custom Trading Strategy
A simple moving average crossover strategy
"""

import pandas as pd
import numpy as np
from collections import deque
import time

# Global variables for strategy state
price_history = deque(maxlen=1000)
sma_fast_period = 10
sma_slow_period = 20
last_signal = None

def on_tick(symbol, ticker_data):
    """Main strategy function called on every price update."""
    global last_signal
    
    # Extract price data
    current_price = ticker_data.get('price', 0)
    current_volume = ticker_data.get('volume', 0)
    
    # Add to price history
    price_history.append(current_price)
    
    # Calculate indicators if we have enough data
    if len(price_history) >= sma_slow_period:
        prices = list(price_history)
        
        # Calculate moving averages
        sma_fast = pd.Series(prices).rolling(window=sma_fast_period).mean().iloc[-1]
        sma_slow = pd.Series(prices).rolling(window=sma_slow_period).mean().iloc[-1]
        
        # Generate signals
        if sma_fast > sma_slow and last_signal != 'BUY':
            print(f"🟢 BUY Signal: {symbol} @ ₹{current_price:.2f}")
            last_signal = 'BUY'
            # Place buy order
            place_order(symbol, 'buy', 100, current_price, 'limit', 'myntapi')
            
        elif sma_fast < sma_slow and last_signal != 'SELL':
            print(f"🔴 SELL Signal: {symbol} @ ₹{current_price:.2f}")
            last_signal = 'SELL'
            # Place sell order
            place_order(symbol, 'sell', 100, current_price, 'limit', 'myntapi')

def main():
    """Main function called on every tick."""
    on_tick(current_symbol, ticker_data)

if __name__ == "__main__":
    print("🚀 My Custom Strategy Started")
    main()
```

### Step 2: Create Configuration File

Create a YAML configuration file in the `configs/` directory:

```yaml
# configs/my_custom_strategy.yaml
symbols:
  - NSE:RELIANCE-EQ
  - NSE:TCS-EQ
exchange: myntapi
strategy:
  sma_fast: 10
  sma_slow: 20
  min_volume: 1000000
risk:
  min_position_inr: 1000
  max_position_pct: 0.02
```

### Step 3: Run Your Strategy

```bash
python -m zebubot --config configs/my_custom_strategy.yaml --script scripts/my_custom_strategy.py
```

## Configuration System

### YAML Configuration Structure

```yaml
# symbols: List of symbols to trade
symbols:
  - NSE:RELIANCE-EQ    # NSE format
  - BSE:500325         # BSE format
  - MCX:CRUDEOIL19SEP25 # MCX format

# exchange: Trading exchange
exchange: myntapi

# strategy: Strategy-specific parameters
strategy:
  # Technical indicator parameters
  rsi_period: 14
  sma_fast: 20
  sma_slow: 50
  bb_period: 20
  bb_stddev: 2.0
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9
  
  # Additional symbols to trade on signals
  additional_symbols:
    - NSE:RELIANCE-EQ
    - NSE:TCS-EQ
  
  # Custom parameters
  custom_param1: "value1"
  custom_param2: 123

# risk: Risk management parameters
risk:
  min_position_inr: 1000        # Minimum position size in INR
  max_position_pct: 0.04        # Maximum position as % of margin
  additional_symbol_position_pct: 0.005  # Position size for additional symbols
  stop_loss_pct: 0.02           # Stop loss percentage
  take_profit_pct: 0.04         # Take profit percentage
```

### Accessing Configuration in Strategy

```python
# Access strategy configuration
rsi_period = strategy.get('rsi_period', 14)
sma_fast = strategy.get('sma_fast', 20)

# Access risk configuration
min_position = risk.get('min_position_inr', 1000)
max_position_pct = risk.get('max_position_pct', 0.04)
```

## Available Functions

### Data Functions

#### `get_ticker(symbol)`
Get current ticker data for a symbol.

```python
ticker_data = get_ticker("NSE:RELIANCE-EQ")
# Returns: {
#   'symbol': 'NSE:RELIANCE-EQ',
#   'price': 2450.50,
#   'volume': 1500000,
#   'timestamp': 1699123456789,
#   'high': 2460.00,
#   'low': 2440.00,
#   'open': 2445.00,
#   'close': 2450.50
# }
```

#### `get_tpseries(symbol, start_time, end_time, interval)`
Get historical time series data.

```python
# Get 1-minute data for last 7 days
end_time = int(time.time())
start_time = end_time - (7 * 24 * 3600)
historical_data = get_tpseries("NSE:RELIANCE-EQ", start_time, end_time, 1)

# Returns list of OHLCV data points:
# [
#   {
#     'timestamp': 1699123456789,
#     'time': '01-11-2023 10:30:00',
#     'open': 2445.00,
#     'high': 2460.00,
#     'low': 2440.00,
#     'close': 2450.50,
#     'volume': 1500000,
#     'oi': 0
#   },
#   ...
# ]
```

#### `get_market_data(symbol, timeframe, limit)`
Get OHLCV market data in array format.

```python
# Get 1-hour data for last 100 periods
ohlcv_data = get_market_data("NSE:RELIANCE-EQ", "1h", 100)
# Returns: [[timestamp, open, high, low, close, volume], ...]
```

### Trading Functions

#### `place_order(symbol, side, quantity, price, order_type, exchange)`
Place a trading order.

```python
# Market buy order
order = place_order("NSE:RELIANCE-EQ", "buy", 10, 0, "market", "myntapi")

# Limit sell order
order = place_order("NSE:RELIANCE-EQ", "sell", 10, 2500.00, "limit", "myntapi")

# Returns order details or None if failed
```

**Parameters:**
- `symbol`: Symbol to trade (e.g., "NSE:RELIANCE-EQ")
- `side`: "buy" or "sell"
- `quantity`: Number of shares/units
- `price`: Price for limit orders (0 for market orders)
- `order_type`: "market" or "limit"
- `exchange`: "myntapi" for MyntAPI integration

#### `get_positions()`
Get current positions.

```python
positions = get_positions()
# Returns list of position dictionaries
```

#### `get_orders()`
Get current orders.

```python
orders = get_orders()
# Returns list of order dictionaries
```

#### `get_balance()`
Get account balance.

```python
balance = get_balance()
# Returns: {
#   'cash': 100000.0,
#   'margin_used': 25000.0,
#   'available_margin': 75000.0
# }
```

### Technical Indicator Functions

#### `calculate_rsi(prices, period)`
Calculate RSI indicator.

```python
rsi = calculate_rsi(price_list, 14)
# Returns RSI value or None if insufficient data
```

#### `calculate_sma(prices, period)`
Calculate Simple Moving Average.

```python
sma = calculate_sma(price_list, 20)
# Returns SMA value
```

#### `calculate_ema(prices, period)`
Calculate Exponential Moving Average.

```python
ema = calculate_ema(price_list, 20)
# Returns EMA value
```

#### `calculate_bollinger_bands(prices, period, std_dev)`
Calculate Bollinger Bands.

```python
upper, middle, lower = calculate_bollinger_bands(price_list, 20, 2.0)
# Returns (upper_band, middle_band, lower_band)
```

#### `calculate_macd(prices, fast, slow, signal)`
Calculate MACD indicator.

```python
macd, signal_line, histogram = calculate_macd(price_list, 12, 26, 9)
# Returns (macd_line, signal_line, histogram)
```

### Utility Functions

#### `process_ticker_data(ticker_data)`
Process ticker data efficiently.

```python
processed = process_ticker_data(ticker_data)
# Returns: {
#   'price': 2450.50,
#   'volume': 1500000,
#   'high': 2460.00,
#   'low': 2440.00,
#   'open': 2445.00,
#   'change': 5.50,
#   'change_percent': 0.22
# }
```

## Real-time Context Variables

These variables are automatically injected into your strategy:

### Global Variables
- `current_symbol`: Current symbol being processed
- `current_price`: Current price from ticker data
- `current_volume`: Current volume from ticker data
- `current_timestamp`: Current timestamp
- `ticker_data`: Full ticker data dictionary

### ZebuBot Instances
- `zebubot`: Main ZebuBot instance
- `bot`: Alias for zebubot
- `logger`: Logger instance for logging

### Configuration Objects
- `strategy`: Strategy configuration dictionary
- `risk`: Risk management configuration dictionary

### Example Usage

```python
def on_tick(symbol, ticker_data):
    # Access injected variables
    print(f"Processing {current_symbol} at ₹{current_price}")
    
    # Access configuration
    rsi_period = strategy.get('rsi_period', 14)
    
    # Log information
    logger.info(f"Price update: {current_price}")
    
    # Access ZebuBot instance
    balance = zebubot.get_balance()
```

## Performance Optimization

### Cython Integration

ZebuBot includes Cython-optimized functions for maximum performance:

```python
# Try to import Cython functions
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

### Using Cython Functions

```python
def calculate_rsi(prices, period=14):
    if CYTHON_AVAILABLE and len(prices) > period:
        prices_array = np.array(prices, dtype=np.float64)
        return calculate_rsi_fast(prices_array, period)
    else:
        # Fallback to standard calculation
        # ... standard implementation
```

### Memory Management

```python
# Use deque for efficient price history
from collections import deque
price_history = deque(maxlen=1000)  # Automatically removes old data

# Use numpy arrays for calculations
prices_array = np.array(price_list, dtype=np.float64)
```

## Best Practices

### 1. Error Handling

```python
def on_tick(symbol, ticker_data):
    try:
        # Your strategy logic here
        pass
    except Exception as e:
        logger.error(f"Error in strategy: {e}")
        # Handle error gracefully
```

### 2. Data Validation

```python
def on_tick(symbol, ticker_data):
    # Validate ticker data
    if not ticker_data or ticker_data.get('price', 0) <= 0:
        logger.warning("Invalid ticker data received")
        return
    
    current_price = ticker_data.get('price', 0)
    if current_price <= 0:
        return
```

### 3. Signal Management

```python
# Track last signal to avoid duplicate orders
last_signal = None

def on_tick(symbol, ticker_data):
    global last_signal
    
    # Generate signal
    if should_buy() and last_signal != 'BUY':
        last_signal = 'BUY'
        place_order(symbol, 'buy', quantity, price, 'limit', 'myntapi')
    elif should_sell() and last_signal != 'SELL':
        last_signal = 'SELL'
        place_order(symbol, 'sell', quantity, price, 'limit', 'myntapi')
```

### 4. Risk Management

```python
def calculate_position_size(signal_strength, available_margin):
    # Dynamic position sizing based on signal strength
    base_size = available_margin * 0.01  # 1% base
    signal_multiplier = min(signal_strength / 4.0, 1.0)  # Max 4x
    position_size = base_size * signal_multiplier
    
    # Apply risk limits
    max_size = available_margin * risk.get('max_position_pct', 0.04)
    min_size = risk.get('min_position_inr', 1000)
    
    return max(min_size, min(position_size, max_size))
```

### 5. Logging

```python
def on_tick(symbol, ticker_data):
    # Use appropriate log levels
    logger.debug(f"Processing tick: {symbol}")
    logger.info(f"Price: ₹{current_price:.2f}")
    logger.warning(f"Low volume detected: {current_volume}")
    logger.error(f"Order failed: {error_message}")
```

## Example Strategies

### 1. RSI Mean Reversion Strategy

```python
"""
RSI Mean Reversion Strategy
Buys when RSI < 30, sells when RSI > 70
"""

import pandas as pd
from collections import deque

price_history = deque(maxlen=1000)
rsi_period = 14
last_signal = None

def on_tick(symbol, ticker_data):
    global last_signal
    
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= rsi_period + 1:
        prices = list(price_history)
        rsi = calculate_rsi(prices, rsi_period)
        
        if rsi is not None:
            if rsi < 30 and last_signal != 'BUY':
                print(f"🟢 RSI Oversold: {rsi:.2f}")
                last_signal = 'BUY'
                place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
                
            elif rsi > 70 and last_signal != 'SELL':
                print(f"🔴 RSI Overbought: {rsi:.2f}")
                last_signal = 'SELL'
                place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')

def main():
    on_tick(current_symbol, ticker_data)
```

### 2. Moving Average Crossover Strategy

```python
"""
Moving Average Crossover Strategy
Buys when fast MA crosses above slow MA, sells when it crosses below
"""

import pandas as pd
from collections import deque

price_history = deque(maxlen=1000)
sma_fast_period = 10
sma_slow_period = 20
last_signal = None
last_fast_ma = None
last_slow_ma = None

def on_tick(symbol, ticker_data):
    global last_signal, last_fast_ma, last_slow_ma
    
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= sma_slow_period:
        prices = list(price_history)
        fast_ma = calculate_sma(prices, sma_fast_period)
        slow_ma = calculate_sma(prices, sma_slow_period)
        
        if last_fast_ma is not None and last_slow_ma is not None:
            # Check for crossover
            if (last_fast_ma <= last_slow_ma and fast_ma > slow_ma and 
                last_signal != 'BUY'):
                print(f"🟢 Bullish Crossover: Fast MA {fast_ma:.2f} > Slow MA {slow_ma:.2f}")
                last_signal = 'BUY'
                place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
                
            elif (last_fast_ma >= last_slow_ma and fast_ma < slow_ma and 
                  last_signal != 'SELL'):
                print(f"🔴 Bearish Crossover: Fast MA {fast_ma:.2f} < Slow MA {slow_ma:.2f}")
                last_signal = 'SELL'
                place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')
        
        last_fast_ma = fast_ma
        last_slow_ma = slow_ma

def main():
    on_tick(current_symbol, ticker_data)
```

### 3. Multi-Indicator Strategy

```python
"""
Multi-Indicator Strategy
Uses RSI, SMA, Bollinger Bands, and MACD for confirmation
"""

import pandas as pd
from collections import deque

price_history = deque(maxlen=1000)
rsi_period = 14
sma_period = 20
bb_period = 20
last_signal = None

def on_tick(symbol, ticker_data):
    global last_signal
    
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= max(rsi_period, bb_period) + 1:
        prices = list(price_history)
        
        # Calculate all indicators
        rsi = calculate_rsi(prices, rsi_period)
        sma = calculate_sma(prices, sma_period)
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(prices, bb_period, 2.0)
        macd, macd_signal, macd_hist = calculate_macd(prices, 12, 26, 9)
        
        if all(x is not None for x in [rsi, sma, bb_upper, bb_lower, macd, macd_signal]):
            # Count bullish and bearish signals
            bullish_signals = 0
            bearish_signals = 0
            
            # RSI signals
            if rsi < 30:
                bullish_signals += 1
            elif rsi > 70:
                bearish_signals += 1
            
            # SMA signals
            if current_price > sma:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # Bollinger Bands signals
            if current_price < bb_lower:
                bullish_signals += 1
            elif current_price > bb_upper:
                bearish_signals += 1
            
            # MACD signals
            if macd > macd_signal:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # Generate signals based on confirmation
            if bullish_signals >= 3 and last_signal != 'BUY':
                print(f"🟢 Strong BUY Signal ({bullish_signals}/4 confirmations)")
                last_signal = 'BUY'
                place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
                
            elif bearish_signals >= 3 and last_signal != 'SELL':
                print(f"🔴 Strong SELL Signal ({bearish_signals}/4 confirmations)")
                last_signal = 'SELL'
                place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')

def main():
    on_tick(current_symbol, ticker_data)
```

## Troubleshooting

### Common Issues

#### 1. "No ticker data received"
- Check if MyntAPI is connected
- Verify symbol format (use NSE:SYMBOL-EQ format)
- Check if market is open

#### 2. "Order placement failed"
- Check account balance
- Verify symbol is tradeable
- Check order parameters (quantity, price)

#### 3. "Historical data loading failed"
- Check MyntAPI connection
- Verify symbol exists
- Check time range parameters

#### 4. "Cython functions not available"
- Install Cython: `pip install cython`
- Rebuild performance module: `python setup_cython.py build_ext --inplace`

### Debug Mode

Enable debug logging in your strategy:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring

```python
import time

def on_tick(symbol, ticker_data):
    start_time = time.time()
    
    # Your strategy logic here
    
    execution_time = time.time() - start_time
    if execution_time > 0.1:  # Log if execution takes > 100ms
        logger.warning(f"Slow execution: {execution_time:.3f}s")
```

## Conclusion

ZebuBot provides a powerful and flexible framework for creating algorithmic trading strategies. With its real-time data processing, technical indicators, and risk management features, you can build sophisticated trading systems tailored to your specific needs.

For more examples and advanced features, check the `scripts/` directory for existing strategies and the `docs/` directory for additional documentation.

Happy trading! 🚀
