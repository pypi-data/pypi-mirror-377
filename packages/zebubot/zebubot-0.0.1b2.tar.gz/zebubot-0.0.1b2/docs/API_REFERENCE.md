# ZebuBot API Reference

## Table of Contents
1. [Core Functions](#core-functions)
2. [Data Functions](#data-functions)
3. [Trading Functions](#trading-functions)
4. [Technical Indicators](#technical-indicators)
5. [Utility Functions](#utility-functions)
6. [Configuration Reference](#configuration-reference)
7. [Error Handling](#error-handling)

## Core Functions

### `on_tick(symbol, ticker_data)`
**Description**: Main strategy function called on every price update.

**Parameters**:
- `symbol` (str): Symbol being processed (e.g., "NSE:RELIANCE-EQ")
- `ticker_data` (dict): Current ticker data dictionary

**Example**:
```python
def on_tick(symbol, ticker_data):
    current_price = ticker_data.get('price', 0)
    print(f"Price update: {symbol} @ ₹{current_price:.2f}")
```

### `main()`
**Description**: Main function called on every tick. Should call `on_tick()`.

**Example**:
```python
def main():
    on_tick(current_symbol, ticker_data)
```

## Data Functions

### `get_ticker(symbol)`
**Description**: Get current ticker data for a symbol.

**Parameters**:
- `symbol` (str): Symbol to get data for

**Returns**: `dict` or `None`
```python
{
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

**Example**:
```python
ticker_data = get_ticker("NSE:RELIANCE-EQ")
if ticker_data:
    print(f"Current price: ₹{ticker_data['price']:.2f}")
```

### `get_tpseries(symbol, start_time, end_time, interval)`
**Description**: Get historical time series data using MyntAPI's tpseries endpoint.

**Parameters**:
- `symbol` (str): Symbol to get data for
- `start_time` (int): Start time as Unix timestamp
- `end_time` (int): End time as Unix timestamp
- `interval` (int): Time interval in minutes (1, 3, 5, 15, 30, 60, 120, 240, 1440)

**Returns**: `list` or `None`
```python
[
    {
        'timestamp': 1699123456789,
        'time': '01-11-2023 10:30:00',
        'open': 2445.00,
        'high': 2460.00,
        'low': 2440.00,
        'close': 2450.50,
        'volume': 1500000,
        'oi': 0
    },
    ...
]
```

**Example**:
```python
import time

# Get 1-minute data for last 7 days
end_time = int(time.time())
start_time = end_time - (7 * 24 * 3600)
historical_data = get_tpseries("NSE:RELIANCE-EQ", start_time, end_time, 1)

if historical_data:
    print(f"Loaded {len(historical_data)} data points")
```

### `get_market_data(symbol, timeframe, limit)`
**Description**: Get OHLCV market data in array format.

**Parameters**:
- `symbol` (str): Symbol to get data for
- `timeframe` (str): Timeframe (e.g., "1h", "1d")
- `limit` (int): Number of periods to retrieve

**Returns**: `list` or `None`
```python
[
    [timestamp, open, high, low, close, volume],
    [timestamp, open, high, low, close, volume],
    ...
]
```

**Example**:
```python
# Get 1-hour data for last 100 periods
ohlcv_data = get_market_data("NSE:RELIANCE-EQ", "1h", 100)
if ohlcv_data:
    latest = ohlcv_data[-1]
    print(f"Latest OHLCV: {latest}")
```

## Trading Functions

### `place_order(symbol, side, quantity, price, order_type, exchange)`
**Description**: Place a trading order.

**Parameters**:
- `symbol` (str): Symbol to trade (e.g., "NSE:RELIANCE-EQ")
- `side` (str): "buy" or "sell"
- `quantity` (int): Number of shares/units
- `price` (float): Price for limit orders (0 for market orders)
- `order_type` (str): "market" or "limit"
- `exchange` (str): "myntapi" for MyntAPI integration

**Returns**: `dict` or `None`
```python
{
    'stat': 'Ok',
    'norenordno': '123456789',
    'request_time': '01-11-2023 10:30:00',
    'exch': 'NSE',
    'tsym': 'RELIANCE-EQ',
    'prc': '2450.50',
    'qty': '10',
    'prd': 'I',
    'trantype': 'B',
    'prctyp': 'L'
}
```

**Example**:
```python
# Market buy order
order = place_order("NSE:RELIANCE-EQ", "buy", 10, 0, "market", "myntapi")

# Limit sell order
order = place_order("NSE:RELIANCE-EQ", "sell", 10, 2500.00, "limit", "myntapi")

if order and order.get('stat') == 'Ok':
    print(f"Order placed successfully: {order['norenordno']}")
else:
    print("Order placement failed")
```

### `get_positions()`
**Description**: Get current positions.

**Returns**: `list`
```python
[
    {
        'exch': 'NSE',
        'tsym': 'RELIANCE-EQ',
        'netqty': '10',
        'netprice': '2450.50',
        'netval': '24505.00',
        'daybuyqty': '10',
        'daybuyval': '24505.00',
        'daysellqty': '0',
        'daysellval': '0.00',
        'daybuyavgprc': '2450.50',
        'daysellavgprc': '0.00',
        'cfbuyqty': '0',
        'cfsellqty': '0',
        'cfbuyavgprc': '0.00',
        'cfsellavgprc': '0.00',
        'cfbuyval': '0.00',
        'cfsellval': '0.00',
        'dayavgprc': '2450.50',
        'ltp': '2450.50',
        'urmtom': '0.00',
        'rpnl': '0.00',
        'bep': '2450.50'
    },
    ...
]
```

**Example**:
```python
positions = get_positions()
for position in positions:
    symbol = f"{position['exch']}:{position['tsym']}"
    qty = float(position['netqty'])
    if qty > 0:
        print(f"Long position: {symbol} - {qty} shares")
    elif qty < 0:
        print(f"Short position: {symbol} - {abs(qty)} shares")
```

### `get_orders()`
**Description**: Get current orders.

**Returns**: `list`
```python
[
    {
        'exch': 'NSE',
        'tsym': 'RELIANCE-EQ',
        'norenordno': '123456789',
        'prc': '2450.50',
        'qty': '10',
        'prd': 'I',
        'trantype': 'B',
        'prctyp': 'L',
        'ret': 'DAY',
        'uid': 'USER123',
        'actid': 'USER123',
        'pp': '2',
        'ls': '1',
        'ti': '0.05',
        'prcftr': '0.00',
        'status': 'OPEN',
        'rqty': '10',
        'rejqty': '0',
        'exd': '01-11-2023',
        'exdt': '01-11-2023 10:30:00',
        'ordenttm': '01-11-2023 10:30:00',
        'exchordid': '123456789',
        'exchprc': '2450.50',
        'exchqty': '10',
        'fillshares': '0',
        'fillprice': '0.00',
        'unfilledshares': '10',
        'qtyunits': '10',
        'fillid': '',
        'mktpro': 'N',
        'remarks': 'ZebuBot'
    },
    ...
]
```

**Example**:
```python
orders = get_orders()
open_orders = [order for order in orders if order['status'] == 'OPEN']
print(f"Open orders: {len(open_orders)}")
```

### `get_balance()`
**Description**: Get account balance.

**Returns**: `dict` or `None`
```python
{
    'cash': 100000.0,
    'margin_used': 25000.0,
    'available_margin': 75000.0
}
```

**Example**:
```python
balance = get_balance()
if balance:
    print(f"Available margin: ₹{balance['available_margin']:,.2f}")
    print(f"Margin used: ₹{balance['margin_used']:,.2f}")
```

## Technical Indicators

### `calculate_rsi(prices, period)`
**Description**: Calculate RSI (Relative Strength Index) indicator.

**Parameters**:
- `prices` (list): List of price values
- `period` (int): RSI period (default: 14)

**Returns**: `float` or `None`

**Example**:
```python
rsi = calculate_rsi(price_list, 14)
if rsi is not None:
    if rsi < 30:
        print("Oversold condition")
    elif rsi > 70:
        print("Overbought condition")
```

### `calculate_sma(prices, period)`
**Description**: Calculate Simple Moving Average.

**Parameters**:
- `prices` (list): List of price values
- `period` (int): SMA period

**Returns**: `float` or `None`

**Example**:
```python
sma_20 = calculate_sma(price_list, 20)
sma_50 = calculate_sma(price_list, 50)

if sma_20 and sma_50:
    if sma_20 > sma_50:
        print("Uptrend: Fast MA above Slow MA")
    else:
        print("Downtrend: Fast MA below Slow MA")
```

### `calculate_ema(prices, period)`
**Description**: Calculate Exponential Moving Average.

**Parameters**:
- `prices` (list): List of price values
- `period` (int): EMA period

**Returns**: `float` or `None`

**Example**:
```python
ema_12 = calculate_ema(price_list, 12)
ema_26 = calculate_ema(price_list, 26)

if ema_12 and ema_26:
    print(f"EMA 12: {ema_12:.2f}, EMA 26: {ema_26:.2f}")
```

### `calculate_bollinger_bands(prices, period, std_dev)`
**Description**: Calculate Bollinger Bands.

**Parameters**:
- `prices` (list): List of price values
- `period` (int): BB period (default: 20)
- `std_dev` (float): Standard deviation multiplier (default: 2.0)

**Returns**: `tuple` or `None`
```python
(upper_band, middle_band, lower_band)
```

**Example**:
```python
bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(price_list, 20, 2.0)

if all(x is not None for x in [bb_upper, bb_middle, bb_lower]):
    if current_price < bb_lower:
        print("Price below lower Bollinger Band - potential buy signal")
    elif current_price > bb_upper:
        print("Price above upper Bollinger Band - potential sell signal")
```

### `calculate_macd(prices, fast, slow, signal)`
**Description**: Calculate MACD (Moving Average Convergence Divergence) indicator.

**Parameters**:
- `prices` (list): List of price values
- `fast` (int): Fast EMA period (default: 12)
- `slow` (int): Slow EMA period (default: 26)
- `signal` (int): Signal line period (default: 9)

**Returns**: `tuple` or `None`
```python
(macd_line, signal_line, histogram)
```

**Example**:
```python
macd, signal_line, histogram = calculate_macd(price_list, 12, 26, 9)

if all(x is not None for x in [macd, signal_line, histogram]):
    if macd > signal_line:
        print("MACD bullish: MACD line above signal line")
    else:
        print("MACD bearish: MACD line below signal line")
```

## Utility Functions

### `process_ticker_data(ticker_data)`
**Description**: Process ticker data efficiently with Cython optimization.

**Parameters**:
- `ticker_data` (dict): Raw ticker data dictionary

**Returns**: `dict`
```python
{
    'price': 2450.50,
    'volume': 1500000,
    'high': 2460.00,
    'low': 2440.00,
    'open': 2445.00,
    'change': 5.50,
    'change_percent': 0.22
}
```

**Example**:
```python
processed = process_ticker_data(ticker_data)
print(f"Price change: {processed['change']:.2f} ({processed['change_percent']:.2f}%)")
```

### `load_historical_data(symbol, days_back, interval_minutes)`
**Description**: Load historical price data using get_tpseries method.

**Parameters**:
- `symbol` (str): Symbol to load data for
- `days_back` (int): Number of days to load (default: 30)
- `interval_minutes` (int): Data interval in minutes (default: 1)

**Returns**: `bool`

**Example**:
```python
success = load_historical_data("NSE:RELIANCE-EQ", days_back=30, interval_minutes=1)
if success:
    print("Historical data loaded successfully")
```

### `refresh_historical_data(symbol, days_back)`
**Description**: Refresh historical data periodically.

**Parameters**:
- `symbol` (str): Symbol to refresh data for
- `days_back` (int): Number of days to refresh (default: 7)

**Returns**: `bool`

**Example**:
```python
# Call this periodically to refresh data
refresh_historical_data("NSE:RELIANCE-EQ", days_back=7)
```

## Configuration Reference

### Strategy Configuration (`strategy`)

```yaml
strategy:
  # Technical indicator parameters
  rsi_period: 14              # RSI calculation period
  sma_fast: 20                # Fast SMA period
  sma_slow: 50                # Slow SMA period
  bb_period: 20               # Bollinger Bands period
  bb_stddev: 2.0              # Bollinger Bands standard deviation
  macd_fast: 12               # MACD fast EMA period
  macd_slow: 26               # MACD slow EMA period
  macd_signal: 9              # MACD signal line period
  
  # Additional symbols to trade on signals
  additional_symbols:
    - NSE:RELIANCE-EQ
    - NSE:TCS-EQ
  
  # Custom parameters
  custom_param1: "value1"
  custom_param2: 123
```

### Risk Configuration (`risk`)

```yaml
risk:
  min_position_inr: 1000              # Minimum position size in INR
  max_position_pct: 0.04              # Maximum position as % of margin
  additional_symbol_position_pct: 0.005  # Position size for additional symbols
  stop_loss_pct: 0.02                 # Stop loss percentage
  take_profit_pct: 0.04               # Take profit percentage
```

### Accessing Configuration

```python
# Access strategy configuration
rsi_period = strategy.get('rsi_period', 14)
sma_fast = strategy.get('sma_fast', 20)

# Access risk configuration
min_position = risk.get('min_position_inr', 1000)
max_position_pct = risk.get('max_position_pct', 0.04)
```

## Error Handling

### Common Exceptions

#### `ConnectionError`
Raised when MyntAPI connection fails.

```python
try:
    ticker_data = get_ticker("NSE:RELIANCE-EQ")
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
```

#### `OrderError`
Raised when order placement fails.

```python
try:
    order = place_order("NSE:RELIANCE-EQ", "buy", 10, 2500, "limit", "myntapi")
except OrderError as e:
    logger.error(f"Order failed: {e}")
```

#### `DataError`
Raised when data retrieval fails.

```python
try:
    historical_data = get_tpseries("NSE:RELIANCE-EQ", start_time, end_time, 1)
except DataError as e:
    logger.error(f"Data retrieval failed: {e}")
```

### Error Handling Best Practices

```python
def safe_place_order(symbol, side, quantity, price, order_type, exchange):
    """Safely place an order with error handling."""
    try:
        order = place_order(symbol, side, quantity, price, order_type, exchange)
        if order and order.get('stat') == 'Ok':
            logger.info(f"Order placed successfully: {order['norenordno']}")
            return order
        else:
            logger.error(f"Order placement failed: {order}")
            return None
    except Exception as e:
        logger.error(f"Order error: {e}")
        return None

def safe_get_ticker(symbol):
    """Safely get ticker data with error handling."""
    try:
        ticker_data = get_ticker(symbol)
        if ticker_data and ticker_data.get('price', 0) > 0:
            return ticker_data
        else:
            logger.warning(f"Invalid ticker data for {symbol}")
            return None
    except Exception as e:
        logger.error(f"Ticker data error for {symbol}: {e}")
        return None
```

### Logging Levels

```python
import logging

# Debug level - detailed information
logger.debug("Processing tick data")

# Info level - general information
logger.info("Order placed successfully")

# Warning level - warning messages
logger.warning("Low volume detected")

# Error level - error messages
logger.error("Order placement failed")
```

## Performance Tips

### 1. Use Cython Functions When Available

```python
try:
    from zebubot.performance import calculate_rsi_fast
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False

def calculate_rsi(prices, period=14):
    if CYTHON_AVAILABLE and len(prices) > period:
        prices_array = np.array(prices, dtype=np.float64)
        return calculate_rsi_fast(prices_array, period)
    else:
        # Fallback implementation
        pass
```

### 2. Use Efficient Data Structures

```python
from collections import deque

# Use deque for efficient price history
price_history = deque(maxlen=1000)  # Automatically removes old data

# Use numpy arrays for calculations
import numpy as np
prices_array = np.array(price_list, dtype=np.float64)
```

### 3. Minimize Function Calls

```python
# Cache frequently used values
last_rsi = None
last_signal = None

def on_tick(symbol, ticker_data):
    global last_rsi, last_signal
    
    # Only calculate RSI if we have new data
    if len(price_history) > rsi_period:
        rsi = calculate_rsi(list(price_history), rsi_period)
        if rsi != last_rsi:
            last_rsi = rsi
            # Process RSI change
```

### 4. Use Appropriate Data Types

```python
# Use appropriate data types for better performance
prices_array = np.array(price_list, dtype=np.float64)  # Use float64 for calculations
quantities = np.array(quantity_list, dtype=np.int32)   # Use int32 for quantities
```

This API reference provides comprehensive documentation for all available functions in the ZebuBot trading strategy framework. Use this as a reference when developing your custom trading strategies.
