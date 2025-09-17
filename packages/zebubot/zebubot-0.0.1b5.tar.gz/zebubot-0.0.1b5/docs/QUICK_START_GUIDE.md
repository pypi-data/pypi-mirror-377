# ZebuBot Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you create and run your first trading strategy with ZebuBot.

## Prerequisites

- Python 3.8 or higher
- MyntAPI (Noren) account and credentials
- Basic knowledge of Python programming

## Installation

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

## Your First Strategy

### Step 1: Create a Simple Strategy

Create a file called `my_first_strategy.py` in the `scripts/` directory:

```python
# scripts/my_first_strategy.py
"""
My First Trading Strategy
A simple RSI-based strategy
"""

from collections import deque
import pandas as pd

# Global variables
price_history = deque(maxlen=1000)
rsi_period = 14
last_signal = None

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator."""
    if len(prices) < period + 1:
        return None
    
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def on_tick(symbol, ticker_data):
    """Main strategy function called on every price update."""
    global last_signal
    
    # Get current price
    current_price = ticker_data.get('price', 0)
    current_volume = ticker_data.get('volume', 0)
    
    # Add price to history
    price_history.append(current_price)
    
    # Print current status
    print(f"📊 {symbol}: ₹{current_price:.2f} | Vol: {current_volume:,.0f}")
    
    # Calculate RSI if we have enough data
    if len(price_history) >= rsi_period + 1:
        prices = list(price_history)
        rsi = calculate_rsi(prices, rsi_period)
        
        if rsi is not None:
            print(f"   📈 RSI: {rsi:.2f}")
            
            # Generate trading signals
            if rsi < 30 and last_signal != 'BUY':
                print(f"   🟢 BUY Signal! RSI: {rsi:.2f}")
                last_signal = 'BUY'
                # Place buy order (uncomment to enable trading)
                # place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
                
            elif rsi > 70 and last_signal != 'SELL':
                print(f"   🔴 SELL Signal! RSI: {rsi:.2f}")
                last_signal = 'SELL'
                # Place sell order (uncomment to enable trading)
                # place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')
                
            elif 30 <= rsi <= 70:
                if last_signal:
                    print(f"   🟡 Neutral Zone: RSI {rsi:.2f}")
                    last_signal = None

def main():
    """Main function called on every tick."""
    on_tick(current_symbol, ticker_data)

if __name__ == "__main__":
    print("🚀 My First Strategy Started!")
    main()
```

### Step 2: Create Configuration

Create a file called `my_first_strategy.yaml` in the `configs/` directory:

```yaml
# configs/my_first_strategy.yaml
symbols:
  - NSE:RELIANCE-EQ
exchange: myntapi
strategy:
  rsi_period: 14
risk:
  min_position_inr: 1000
  max_position_pct: 0.02
```

### Step 3: Run Your Strategy

```bash
python -m zebubot --config configs/my_first_strategy.yaml --script scripts/my_first_strategy.py
```

## Understanding the Output

When you run your strategy, you'll see output like this:

```
🚀 My First Strategy Started!

[10:30:15] 📊 NSE:RELIANCE-EQ | ₹2450.50 | Vol: 1,500,000
   📈 RSI: 45.23

[10:30:16] 📊 NSE:RELIANCE-EQ | ₹2451.25 | Vol: 1,520,000
   📈 RSI: 45.67

[10:30:17] 📊 NSE:RELIANCE-EQ | ₹2449.80 | Vol: 1,480,000
   📈 RSI: 44.89
```

## Enable Trading

To enable actual trading, uncomment the `place_order` lines in your strategy:

```python
# Uncomment these lines to enable trading
place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')
```

## Common Patterns

### 1. Moving Average Crossover

```python
def on_tick(symbol, ticker_data):
    current_price = ticker_data.get('price', 0)
    price_history.append(current_price)
    
    if len(price_history) >= 50:
        prices = list(price_history)
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)
        
        if sma_20 and sma_50:
            if sma_20 > sma_50 and last_signal != 'BUY':
                print("🟢 Bullish Crossover!")
                last_signal = 'BUY'
            elif sma_20 < sma_50 and last_signal != 'SELL':
                print("🔴 Bearish Crossover!")
                last_signal = 'SELL'
```

### 2. Multi-Indicator Strategy

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
        
        # Count signals
        bullish_signals = 0
        if rsi and rsi < 30:
            bullish_signals += 1
        if sma_20 and current_price > sma_20:
            bullish_signals += 1
        if bb_lower and current_price < bb_lower:
            bullish_signals += 1
        
        # Generate signal based on confirmation
        if bullish_signals >= 2 and last_signal != 'BUY':
            print(f"🟢 Strong BUY Signal! ({bullish_signals}/3 confirmations)")
            last_signal = 'BUY'
```

### 3. Risk Management

```python
def calculate_position_size(signal_strength, available_margin):
    """Calculate position size based on signal strength and available margin."""
    base_size = available_margin * 0.01  # 1% base
    signal_multiplier = min(signal_strength / 3.0, 1.0)  # Max 3x
    position_size = base_size * signal_multiplier
    
    # Apply risk limits
    max_size = available_margin * risk.get('max_position_pct', 0.04)
    min_size = risk.get('min_position_inr', 1000)
    
    return max(min_size, min(position_size, max_size))

def on_tick(symbol, ticker_data):
    # ... your strategy logic ...
    
    if should_buy():
        balance = get_balance()
        if balance:
            position_size = calculate_position_size(3, balance['available_margin'])
            quantity = int(position_size / current_price)
            if quantity > 0:
                place_order(symbol, 'buy', quantity, current_price, 'limit', 'myntapi')
```

## Configuration Options

### Basic Configuration

```yaml
symbols:
  - NSE:RELIANCE-EQ
  - NSE:TCS-EQ
exchange: myntapi
strategy:
  rsi_period: 14
  sma_fast: 20
  sma_slow: 50
risk:
  min_position_inr: 1000
  max_position_pct: 0.04
```

### Advanced Configuration

```yaml
symbols:
  - NSE:RELIANCE-EQ
  - NSE:TCS-EQ
  - NSE:HDFCBANK-EQ
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

## Troubleshooting

### Common Issues

1. **"No ticker data received"**
   - Check if MyntAPI is connected
   - Verify symbol format (use NSE:SYMBOL-EQ)
   - Check if market is open

2. **"Order placement failed"**
   - Check account balance
   - Verify symbol is tradeable
   - Check order parameters

3. **"Historical data loading failed"**
   - Check MyntAPI connection
   - Verify symbol exists
   - Check time range parameters

### Debug Mode

Enable debug logging:

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
        print(f"⚠️ Slow execution: {execution_time:.3f}s")
```

## Next Steps

1. **Read the full documentation**: Check out `STRATEGY_DEVELOPMENT_GUIDE.md` for detailed information
2. **Explore examples**: Look at existing strategies in the `scripts/` directory
3. **Join the community**: Connect with other ZebuBot users
4. **Contribute**: Share your strategies and improvements

## Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs and request features on GitHub
- **Community**: Join our Discord/Telegram group

Happy trading! 🚀📈
