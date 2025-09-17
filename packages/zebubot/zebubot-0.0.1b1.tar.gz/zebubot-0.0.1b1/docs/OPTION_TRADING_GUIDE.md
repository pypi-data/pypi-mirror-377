# Multi-Leg Option Trading Strategy Guide

This guide explains how to use the enhanced multi-leg option trading strategy in ZebuBot.

## Overview

The Multi-Leg Option Trading Strategy is designed to place multiple option orders at specified start times and exit at end times without margin checking, as requested. The strategy supports:

- Multi-leg option strategies (spreads, straddles, strangles, etc.)
- Time-based entry and exit for each leg
- Master data integration (NFO & BFO symbols)
- Automatic symbol resolution using trading symbols
- No margin validation (places orders directly)
- Configurable timing parameters for each leg

## Files

- `scripts/option_trading_strategy.py` - Main multi-leg strategy script
- `configs/option_trading_strategy.yaml` - Multi-leg configuration file
- `scripts/test_multi_leg_strategy.py` - Test script for multi-leg functionality

## Configuration

### YAML Configuration

Edit `configs/option_trading_strategy.yaml` to customize your multi-leg strategy:

```yaml
strategy:
  start_time: "09:30:00"        # Overall start time (HH:MM:SS)
  end_time: "15:30:00"          # Overall end time (HH:MM:SS)
  square_off_time: "15:10:00"   # Square off time (HH:MM:SS)
  overall_target: 1000          # Overall target in INR
  overall_stop_loss: 1000       # Overall stop loss in INR
  idx_pair: "NSE:NIFTY 50"      # Index pair for ATM calculations
  
  legs:
    1:
      exch: "NFO"               # Exchange (NFO/BFO)
      symbol: "NIFTY"           # Base symbol
      expiry: "current week"    # Expiry (current week, next week, current month, next month, DD-MM-YYYY)
      option_type: "CE"         # Option type (CE, PE, FUT)
      strike_price: 0           # Strike (0=ATM, ATM+1, ATM-1, or specific value)
      lot_size: 1               # Number of lots
      order_type: "market"      # Order type (market/limit)
      product_type: "I"         # Product type (I for Intraday, M for MIS)
      entry_time: "09:30:00"    # Entry time for this leg
      exit_time: "15:30:00"     # Exit time for this leg
      target: 1000              # Target for this leg (optional)
      stop_loss: 1000           # Stop loss for this leg (optional)
      order_price: 100          # Order price for limit orders (optional)
      strike_premium: 100       # Select strike based on premium price (optional)
```

### Key Parameters

#### Overall Strategy Parameters
- **start_time**: Overall strategy start time
- **end_time**: Overall strategy end time
- **square_off_time**: Square off time for all positions
- **overall_target**: Overall profit target in INR
- **overall_stop_loss**: Overall stop loss in INR
- **idx_pair**: Index pair for ATM calculations

#### Leg Parameters
- **exch**: Exchange (NFO for NSE F&O, BFO for BSE F&O)
- **symbol**: Base symbol (NIFTY, BANKNIFTY, etc.)
- **expiry**: Expiry date (current week, next week, current month, next month, or DD-MM-YYYY)
- **option_type**: CE for Call, PE for Put, FUT for Futures
- **strike_price**: Strike price (0=ATM, ATM+1, ATM-1, or specific value)
- **lot_size**: Number of lots to trade
- **order_type**: "market" for immediate execution, "limit" for specific price
- **product_type**: "I" for Intraday, "M" for MIS
- **entry_time**: Entry time for this specific leg
- **exit_time**: Exit time for this specific leg

## Master Data Integration

The strategy automatically loads master data from MyntAPI:

- **NFO Symbols**: NSE F&O symbols from `https://go.mynt.in/NFO_symbols.txt.zip`
- **BFO Symbols**: BSE F&O symbols from `https://go.mynt.in/BFO_symbols.txt.zip`
- **MCX Symbols**: MCX commodity symbols from `https://go.mynt.in/MCX_symbols.txt.zip`

### Symbol Resolution

The strategy automatically resolves trading symbols using:
- Exchange (NFO/BFO/MCX)
- Base symbol (NIFTY, BANKNIFTY, GOLD, SILVER, etc.)
- Expiry date calculation
- Strike price calculation (ATM, ITM, OTM)
- Option type (CE, PE, FUT)

### Expiry Date Calculation

Supports multiple expiry formats:
- `current week`: Thursday of current week
- `next week`: Thursday of next week  
- `current month`: Last Thursday of current month
- `next month`: Last Thursday of next month
- `DD-MM-YYYY`: Specific date (e.g., 10-09-2025)

### Strike Price Calculation

The strategy uses **master data strike prices** to ensure only available strikes are selected. It supports various strike price formats:

#### Basic Strike Types
- `0` or `ATM`: At The Money (closest to current price from available strikes)
- `ITM`: In The Money (1 strike ITM from available strikes)
- `OTM`: Out The Money (1 strike OTM from available strikes)

#### Offset-Based Strikes
- `ATM+1`, `ATM+2`, etc.: ATM plus offset (from available strikes)
- `ATM-1`, `ATM-2`, etc.: ATM minus offset (from available strikes)
- `ITM+1`, `ITM+2`, etc.: ITM plus offset (from available strikes)
- `ITM-1`, `ITM-2`, etc.: ITM minus offset (from available strikes)
- `OTM+1`, `OTM+2`, etc.: OTM plus offset (from available strikes)
- `OTM-1`, `OTM-2`, etc.: OTM minus offset (from available strikes)

#### Specific Values
- Specific number: Closest available strike to the specified price
- `strike_premium`: Select strike based on premium price (from available strikes)

#### ITM/OTM Logic
- **Call Options (CE)**:
  - ITM: Strike below ATM (higher intrinsic value)
  - OTM: Strike above ATM (lower intrinsic value)
- **Put Options (PE)**:
  - ITM: Strike above ATM (higher intrinsic value)
  - OTM: Strike below ATM (lower intrinsic value)

#### Master Data Integration
- **Available Strikes**: Only strikes that exist in the master data are considered
- **Closest Match**: If exact strike not available, finds the closest available strike
- **Real-time Validation**: Ensures all selected strikes are tradeable

#### Premium-Based Strike Selection

When using `strike_premium` in leg configuration:
- **Call Options**: `strike = current_price - premium`
- **Put Options**: `strike = current_price + premium`
- **Futures**: `strike = current_price`

The system automatically rounds to appropriate strike intervals:
- NIFTY: 50-point intervals
- BANKNIFTY: 100-point intervals
- MCX Commodities (GOLD, SILVER, CRUDEOIL, NATURALGAS): 1-point intervals
- Other symbols: 1-point intervals

## Usage

### 1. Basic Usage

```python
# The strategy will automatically:
# 1. Load master data (NFO & BFO symbols)
# 2. Wait for start_time
# 3. Place entry orders for all legs
# 4. Hold positions
# 5. Place exit orders at end_time
```

### 2. Running the Strategy

```bash
# Run with ZebuBot CLI
python -m zebubot run-script scripts/option_trading_strategy.py

# Or run directly
python scripts/option_trading_strategy.py
```

### 3. Using Configuration File

```bash
# Run with specific config
python -m zebubot run-script scripts/option_trading_strategy.py --config configs/option_trading_strategy.yaml
```

## Strategy Flow

1. **Initialization**: Load configuration and connect to MyntAPI
2. **Wait Phase**: Wait for market to open and start time
3. **Entry Phase**: Place entry order at start time (+ delay)
4. **Hold Phase**: Monitor position until exit time
5. **Exit Phase**: Place exit order at end time (- delay)
6. **Complete**: Strategy execution finished

## Features

### Time-Based Trading
- Precise entry and exit timing
- Configurable delays
- Market hours validation

### No Margin Checking
- Places orders directly as requested
- No position size validation
- No risk management checks

### Real-Time Monitoring
- Live price updates
- Position status tracking
- Order execution monitoring

### Configuration Flexibility
- YAML-based configuration
- Runtime parameter updates
- Multiple symbol support

## Example Scenarios

### Scenario 1: NIFTY Straddle Strategy
```yaml
strategy:
  start_time: "09:30:00"
  end_time: "15:30:00"
  square_off_time: "15:10:00"
  overall_target: 2000
  overall_stop_loss: 1000
  idx_pair: "NSE:NIFTY 50"
  
  legs:
    1:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "CE"
      strike_price: 0  # ATM
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
    2:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "PE"
      strike_price: 0  # ATM
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
```

### Scenario 2: NIFTY Call Spread Strategy
```yaml
strategy:
  start_time: "09:30:00"
  end_time: "15:30:00"
  overall_target: 1500
  overall_stop_loss: 1000
  idx_pair: "NSE:NIFTY 50"
  
  legs:
    1:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "CE"
      strike_price: "ATM"  # Buy ATM Call
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
    2:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "CE"
      strike_price: "ATM+2"  # Sell ATM+2 Call
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
```

### Scenario 3: Multi-Expiry Strategy
```yaml
strategy:
  start_time: "09:30:00"
  end_time: "15:30:00"
  overall_target: 3000
  overall_stop_loss: 1500
  idx_pair: "NSE:NIFTY 50"
  
  legs:
    1:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "CE"
      strike_price: 0
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
    2:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "next week"
      option_type: "PE"
      strike_price: "ATM-1"
      lot_size: 1
      order_type: "limit"
      product_type: "I"
      order_price: 50
      entry_time: "10:00:00"
      exit_time: "15:00:00"
    3:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current month"
      option_type: "FUT"
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:45:00"
      exit_time: "15:15:00"
```

### Scenario 4: Premium-Based Strike Selection
```yaml
strategy:
  start_time: "09:30:00"
  end_time: "15:30:00"
  overall_target: 2500
  overall_stop_loss: 1200
  idx_pair: "NSE:NIFTY 50"
  
  legs:
    1:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "CE"
      strike_premium: 50  # Select strike with ₹50 premium
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
      target: 1000
      stop_loss: 500
    2:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "PE"
      strike_premium: 75  # Select strike with ₹75 premium
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
      target: 800
      stop_loss: 400
```

### Scenario 5: MCX Commodity Trading
```yaml
strategy:
  start_time: "09:00:00"
  end_time: "23:30:00"
  overall_target: 5000
  overall_stop_loss: 2500
  idx_pair: "MCX:GOLD"
  
  legs:
    1:
      exch: "MCX"
      symbol: "GOLD"
      expiry: "current month"
      option_type: "CE"
      strike_price: 0  # ATM
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:00:00"
      exit_time: "23:30:00"
      target: 2000
      stop_loss: 1000
    2:
      exch: "MCX"
      symbol: "SILVER"
      expiry: "current month"
      option_type: "PE"
      strike_premium: 100  # Select strike with ₹100 premium
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:00:00"
      exit_time: "23:30:00"
      target: 1500
      stop_loss: 750
```

### Scenario 6: ITM/OTM Strategy
```yaml
strategy:
  start_time: "09:30:00"
  end_time: "15:30:00"
  overall_target: 1500
  overall_stop_loss: 750
  idx_pair: "NSE:NIFTY 50"
  
  legs:
    1:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "CE"
      strike_price: "ITM"  # Buy ITM Call (strike below ATM)
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
      target: 800
      stop_loss: 400
    2:
      exch: "NFO"
      symbol: "NIFTY"
      expiry: "current week"
      option_type: "PE"
      strike_price: "OTM+2"  # Buy OTM+2 Put (2 strikes below ATM)
      lot_size: 1
      order_type: "market"
      product_type: "I"
      entry_time: "09:30:00"
      exit_time: "15:30:00"
      target: 700
      stop_loss: 350
```

## Monitoring

The strategy provides real-time monitoring with:

- Current price and volume
- Position status (WAITING/ORDERED/POSITION/EXITED)
- Time remaining until entry/exit
- Order execution status

## Logging

All activities are logged to:
- Console output (real-time)
- Log files (zebubot.log)
- Order execution details

## Testing

Run the test script to verify configuration:

```bash
python scripts/test_option_strategy.py
```

## Important Notes

1. **No Margin Checking**: As requested, the strategy does not check margins
2. **Direct Order Placement**: Orders are placed immediately when conditions are met
3. **Time-Based Only**: Strategy relies on time, not technical indicators
4. **MyntAPI Required**: Requires valid MyntAPI credentials
5. **Market Hours**: Only works during market hours

## Troubleshooting

### Common Issues

1. **MyntAPI Connection Failed**
   - Check credentials in zebubot_config.yaml
   - Verify network connectivity

2. **Invalid Time Format**
   - Use HH:MM:SS format (24-hour)
   - Check for typos in configuration

3. **Order Placement Failed**
   - Verify symbol exists
   - Check account balance
   - Ensure market is open

4. **Configuration Not Loading**
   - Check YAML syntax
   - Verify file path
   - Check permissions

### Debug Mode

Enable debug logging in zebubot_config.yaml:

```yaml
logging:
  level: DEBUG
```

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify configuration parameters
3. Test with the test script
4. Check MyntAPI connection

## Disclaimer

This strategy places orders without margin checking as requested. Please ensure you have sufficient funds and understand the risks involved in option trading.
