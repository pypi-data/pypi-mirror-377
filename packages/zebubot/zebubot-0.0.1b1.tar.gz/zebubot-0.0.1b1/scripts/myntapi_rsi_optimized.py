"""
MyntAPI RSI Trading Strategy Script - Cython Optimized
This script uses MyntAPI (Noren) for Indian stock market trading with Cython performance optimizations.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time
from collections import deque

# Try to import Cython optimized functions
try:
    from zebubot.performance import (
        calculate_rsi_fast, 
        calculate_sma_fast, 
        calculate_ema_fast,
        calculate_bollinger_bands_fast,
        calculate_macd_fast,
        process_ticker_data_fast,
        calculate_volatility_fast
    )
    CYTHON_AVAILABLE = True
    print("🚀 Cython optimizations loaded - Maximum performance mode!")
except ImportError:
    CYTHON_AVAILABLE = False
    print("⚠️ Cython not available - using standard Python functions")

# Real-time context variables (injected by ZebuBot):
# - current_symbol: Current symbol being processed
# - current_price: Current price from ticker data
# - current_volume: Current volume from ticker data
# - current_timestamp: Current timestamp
# - ticker_data: Full ticker data dictionary
# - zebubot/bot: ZebuBot instance
# - logger: Logger instance

# Global variables for RSI calculation
price_history = deque(maxlen=1000)  # Increased buffer for better analysis
rsi_period = 14
last_rsi = None
last_signal = None
last_sma_20 = None
last_sma_50 = None
last_bb_upper = None
last_bb_lower = None
last_macd = None
last_macd_signal = None
last_volatility = None
tick_count = 0
historical_data_loaded = False

# Additional symbols to trade when signals are generated (can be overridden by YAML config)
additional_symbols = [
    "NSE:RELIANCE-EQ",  # Reliance Industries
    "NSE:TCS-EQ",       # Tata Consultancy Services
    "NSE:HDFCBANK-EQ",  # HDFC Bank
    "NSE:INFY-EQ",      # Infosys
    "NSE:HINDUNILVR-EQ" # Hindustan Unilever
]

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator - uses Cython if available."""
    if CYTHON_AVAILABLE and len(prices) > period:
        prices_array = np.array(prices, dtype=np.float64)
        return calculate_rsi_fast(prices_array, period)
    else:
        # Fallback to standard calculation
        if len(prices) < period + 1:
            return None
        
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

def calculate_sma(prices, period):
    """Calculate Simple Moving Average - uses Cython if available."""
    if CYTHON_AVAILABLE and len(prices) >= period:
        prices_array = np.array(prices, dtype=np.float64)
        return calculate_sma_fast(prices_array, period)[-1]
    else:
        # Fallback to standard calculation
        return pd.Series(prices).rolling(window=period).mean().iloc[-1]

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average - uses Cython if available."""
    if CYTHON_AVAILABLE and len(prices) >= period:
        prices_array = np.array(prices, dtype=np.float64)
        return calculate_ema_fast(prices_array, period)[-1]
    else:
        # Fallback to standard calculation
        return pd.Series(prices).ewm(span=period).mean().iloc[-1]

def calculate_bollinger_bands(prices, period=20, std_dev=2.0):
    """Calculate Bollinger Bands - uses Cython if available."""
    if CYTHON_AVAILABLE and len(prices) >= period:
        prices_array = np.array(prices, dtype=np.float64)
        upper, middle, lower = calculate_bollinger_bands_fast(prices_array, period, std_dev)
        return upper[-1], middle[-1], lower[-1]
    else:
        # Fallback to standard calculation
        sma = pd.Series(prices).rolling(window=period).mean()
        std = pd.Series(prices).rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper.iloc[-1], sma.iloc[-1], lower.iloc[-1]

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD - uses Cython if available."""
    if CYTHON_AVAILABLE and len(prices) >= slow:
        prices_array = np.array(prices, dtype=np.float64)
        macd_line, signal_line, histogram = calculate_macd_fast(prices_array, fast, slow, signal)
        return macd_line[-1], signal_line[-1], histogram[-1]
    else:
        # Fallback to standard calculation
        ema_fast = pd.Series(prices).ewm(span=fast).mean()
        ema_slow = pd.Series(prices).ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]

def calculate_volatility(prices, period=20):
    """Calculate historical volatility - uses Cython if available."""
    if CYTHON_AVAILABLE and len(prices) >= period:
        prices_array = np.array(prices, dtype=np.float64)
        volatility_result = calculate_volatility_fast(prices_array, period)
        # Ensure we return a scalar value, not an array
        if isinstance(volatility_result, np.ndarray):
            return float(volatility_result[-1]) if len(volatility_result) > 0 else None
        else:
            return float(volatility_result) if volatility_result is not None else None
    else:
        # Fallback to standard calculation
        if len(prices) < period + 1:
            return None
        
        returns = pd.Series(prices).pct_change().dropna()
        volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
        return volatility.iloc[-1] if not volatility.empty else None

def load_historical_data(symbol, days_back=30, interval_minutes=1):
    """Load historical price data using get_tpseries method."""
    global price_history, historical_data_loaded
    
    try:
        if not zebubot or not zebubot.myntapi:
            logger.warning("ZebuBot or MyntAPI not available for historical data")
            return False
        
        # Calculate time range
        end_time = int(time.time())
        start_time = end_time - (days_back * 24 * 3600)  # days_back days ago
        
        logger.info(f"📊 Loading {days_back} days of historical data for {symbol}")
        print(f"📊 Loading {days_back} days of historical data for {symbol}...")
        
        # Get historical data using tpseries
        historical_data = zebubot.myntapi.get_tpseries(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            interval=interval_minutes
        )
        
        if not historical_data:
            logger.warning(f"No historical data received for {symbol}")
            return False
        
        # Clear existing price history and populate with historical data
        price_history.clear()
        
        # Add historical prices to the deque
        for data_point in historical_data:
            close_price = data_point.get('close', 0)
            if close_price > 0:
                price_history.append(close_price)
        
        historical_data_loaded = True
        logger.info(f"✅ Loaded {len(price_history)} historical data points for {symbol}")
        print(f"✅ Loaded {len(price_history)} historical data points for {symbol}")
        
        # Calculate initial indicators with historical data
        if len(price_history) >= max(rsi_period + 1, 50):
            prices_list = list(price_history)
            
            # Calculate initial RSI
            initial_rsi = calculate_rsi(prices_list, rsi_period)
            if initial_rsi:
                logger.info(f"📈 Initial RSI: {initial_rsi:.2f}")
                print(f"📈 Initial RSI: {initial_rsi:.2f}")
            
            # Calculate initial SMAs
            sma_20 = calculate_sma(prices_list, 20)
            sma_50 = calculate_sma(prices_list, 50)
            if sma_20 and sma_50:
                logger.info(f"📊 Initial SMAs - 20: {sma_20:.2f}, 50: {sma_50:.2f}")
                print(f"📊 Initial SMAs - 20: {sma_20:.2f}, 50: {sma_50:.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load historical data for {symbol}: {e}")
        print(f"❌ Failed to load historical data for {symbol}: {e}")
        return False

def process_ticker_data(ticker_data):
    """Process ticker data - uses Cython if available."""
    if CYTHON_AVAILABLE:
        return process_ticker_data_fast(ticker_data)
    else:
        price = ticker_data.get('price', 0.0)
        volume = ticker_data.get('volume', 0.0)
        high = ticker_data.get('high', price)
        low = ticker_data.get('low', price)
        open_price = ticker_data.get('open', price)
        
        return {
            'price': price,
            'volume': volume,
            'high': high,
            'low': low,
            'open': open_price,
            'change': price - open_price if open_price > 0 else 0.0,
            'change_percent': ((price - open_price) / open_price * 100.0) if open_price > 0 else 0.0
        }

def place_orders_on_additional_symbols(signal_type, signal_strength, primary_price):
    """Place orders on additional symbols when primary signal is generated."""
    try:
        if not zebubot or not zebubot.myntapi:
            logger.warning("ZebuBot or MyntAPI not available for additional orders")
            return
        
        # Get additional symbols from strategy config if available
        symbols_to_trade = additional_symbols
        if hasattr(globals(), 'strategy') and isinstance(strategy, dict):
            config_symbols = strategy.get('additional_symbols', [])
            if config_symbols:
                symbols_to_trade = config_symbols
                logger.info(f"Using additional symbols from config: {symbols_to_trade}")
        
        if not symbols_to_trade:
            logger.info("No additional symbols configured for trading")
            return
        
        # Get current balance
        balance = get_balance()
        if not balance or 'available_margin' not in balance:
            logger.warning("No balance available for additional orders")
            return
        
        available_margin = balance['available_margin']
        
        # Get position size percentage from risk config
        position_pct = 0.005  # Default 0.5%
        if hasattr(globals(), 'risk') and isinstance(risk, dict):
            position_pct = risk.get('additional_symbol_position_pct', 0.005)
        
        # Calculate position size for additional symbols (smaller than primary)
        # Use configured percentage of margin per additional symbol, scaled by signal strength
        position_size_per_symbol = available_margin * (position_pct * signal_strength)
        
        if position_size_per_symbol < 500:  # Minimum ₹500 per additional symbol
            logger.info(f"Position size too small for additional symbols: ₹{position_size_per_symbol:.2f}")
            return
        
        logger.info(f"🎯 Placing {signal_type} orders on {len(symbols_to_trade)} additional symbols")
        logger.info(f"💰 Position size per symbol: ₹{position_size_per_symbol:.2f}")
        
        successful_orders = 0
        failed_orders = 0
        
        for symbol in symbols_to_trade:
            try:
                # Get current price for the additional symbol
                symbol_ticker = zebubot.get_ticker(symbol)
                if not symbol_ticker:
                    logger.warning(f"No ticker data for {symbol}")
                    failed_orders += 1
                    continue
                
                symbol_price = symbol_ticker.get('price', 0)
                if symbol_price <= 0:
                    logger.warning(f"Invalid price for {symbol}: {symbol_price}")
                    failed_orders += 1
                    continue
                
                # Calculate quantity based on price
                quantity = int(position_size_per_symbol / symbol_price)
                if quantity < 1:
                    logger.warning(f"Quantity too small for {symbol}: {quantity}")
                    failed_orders += 1
                    continue
                
                # Place order
                if signal_type == 'BUY':
                    order = place_order(symbol, 'buy', quantity, symbol_price, 'limit', 'myntapi')
                    order_type = "BUY"
                else:  # SELL
                    # For sell orders, check if we have position first
                    positions = zebubot.myntapi.get_positions() if zebubot.myntapi else []
                    has_position = False
                    for position in positions:
                        if position.get('tsym') == symbol.split(':')[1] if ':' in symbol else symbol:
                            net_qty = float(position.get('netqty', 0))
                            if net_qty > 0:
                                quantity = min(quantity, int(net_qty))
                                has_position = True
                                break
                    
                    if not has_position:
                        logger.info(f"No position to sell for {symbol}")
                        failed_orders += 1
                        continue
                    
                    order = place_order(symbol, 'sell', quantity, symbol_price, 'limit', 'myntapi')
                    order_type = "SELL"
                
                if order:
                    print(f"   ✅ {order_type} order on {symbol}: {quantity} shares @ ₹{symbol_price:.2f}")
                    logger.info(f"✅ {order_type} order placed on {symbol}: {quantity} shares @ ₹{symbol_price:.2f}")
                    successful_orders += 1
                else:
                    print(f"   ❌ Failed {order_type} order on {symbol}")
                    logger.error(f"❌ Failed to place {order_type} order on {symbol}")
                    failed_orders += 1
                    
            except Exception as e:
                logger.error(f"Error placing order on {symbol}: {e}")
                failed_orders += 1
        
        # Summary
        print(f"   📊 Additional orders: {successful_orders} successful, {failed_orders} failed")
        logger.info(f"📊 Additional orders summary: {successful_orders} successful, {failed_orders} failed")
        
    except Exception as e:
        logger.error(f"Error in place_orders_on_additional_symbols: {e}")

def on_tick(symbol, ticker_data):
    """Called on every tick/price update - optimized version."""
    global last_rsi, last_signal, last_sma_20, last_sma_50, last_bb_upper, last_bb_lower, last_macd, last_macd_signal, last_volatility, tick_count, historical_data_loaded
    
    tick_count += 1
    
    # Load historical data on first tick if not already loaded
    if not historical_data_loaded and tick_count == 1:
        print(f"🔄 First tick detected - loading historical data...")
        logger.info("🔄 First tick detected - loading historical data...")
        load_historical_data(symbol, days_back=30, interval_minutes=1)
    
    # Process ticker data efficiently
    processed_data = process_ticker_data(ticker_data)
    current_price = processed_data['price']
    current_volume = processed_data['volume']
    
    # Console update with timestamp and status
    timestamp = time.strftime("%H:%M:%S")
    signal_status = f" | Signal: {last_signal}" if last_signal else " | Signal: None"
    
    # Check if data is from websocket or polling
    data_source = "WS" if ticker_data.get('timestamp', 0) > 0 else "POLL"
    
    print(f"\n[{timestamp}] 📊 {symbol} | ₹{current_price:.2f} | Vol: {current_volume:,.0f}{signal_status} | Tick: {tick_count} | {data_source}")
    
    # Add current price to history
    price_history.append(current_price)
    
    # Calculate indicators if we have enough data
    if len(price_history) >= max(rsi_period + 1, 50):  # Need at least 50 for all indicators
        prices_list = list(price_history)
        
        # Calculate RSI
        current_rsi = calculate_rsi(prices_list, rsi_period)
        
        # Calculate SMAs
        sma_20 = calculate_sma(prices_list, 20)
        sma_50 = calculate_sma(prices_list, 50)
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(prices_list, 20, 2.0)
        
        # Calculate MACD
        macd, macd_signal, macd_histogram = calculate_macd(prices_list, 12, 26, 9)
        
        # Calculate Volatility
        try:
            current_volatility = calculate_volatility(prices_list, 20)
        except Exception as e:
            logger.warning(f"Volatility calculation failed: {e}")
            current_volatility = None
        
        # Update global variables
        last_rsi = current_rsi
        last_sma_20 = sma_20
        last_sma_50 = sma_50
        last_bb_upper = bb_upper
        last_bb_lower = bb_lower
        last_macd = macd
        last_macd_signal = macd_signal
        last_volatility = current_volatility
        
        # Enhanced console output with all indicators
        print(f"   📈 RSI: {current_rsi:.2f} | SMA20: {sma_20:.2f} | SMA50: {sma_50:.2f}")
        print(f"   📊 BB: U:{bb_upper:.2f} M:{bb_middle:.2f} L:{bb_lower:.2f} | MACD: {macd:.4f}")
        if current_volatility is not None:
            print(f"   📊 Volatility: {current_volatility:.2%} (20-day annualized)")
        else:
            print(f"   📊 Volatility: Calculating...")
        
        # Enhanced logging with all indicators
        logger.info(f"📊 {symbol}: ₹{current_price:.2f} | RSI: {current_rsi:.2f} | SMA20: {sma_20:.2f} | SMA50: {sma_50:.2f}")
        logger.info(f"📈 BB: U:{bb_upper:.2f} M:{bb_middle:.2f} L:{bb_lower:.2f} | MACD: {macd:.4f} | Vol: {current_volume:,.0f}")
        if current_volatility is not None:
            logger.info(f"📊 Volatility: {current_volatility:.2%} (20-day annualized)")
        else:
            logger.info(f"📊 Volatility: Calculating...")
        

        print("Current Volatility: ", current_volatility)
        # Enhanced trading logic for Indian stocks
        if current_rsi is not None:
            # Multi-indicator confirmation
            bullish_signals = 0
            bearish_signals = 0
            
            # RSI signals
            if current_rsi < 30:
                bullish_signals += 1
            elif current_rsi > 70:
                bearish_signals += 1
            
            # SMA signals
            if sma_20 > sma_50:
                bullish_signals += 1
            elif sma_20 < sma_50:
                bearish_signals += 1
            
            # Bollinger Bands signals
            if current_price < bb_lower:
                bullish_signals += 1
            elif current_price > bb_upper:
                bearish_signals += 1
            
            # MACD signals
            if macd > macd_signal:
                bullish_signals += 1
            elif macd < macd_signal:
                bearish_signals += 1
            
            # Volatility signals (if available)
            if current_volatility is not None:
                # High volatility can indicate strong momentum
                if current_volatility > 0.25:  # 25% annualized volatility
                    if current_rsi < 50:  # Oversold with high volatility = bullish
                        bullish_signals += 1
                    elif current_rsi > 50:  # Overbought with high volatility = bearish
                        bearish_signals += 1
                # Low volatility can indicate consolidation
                elif current_volatility < 0.15:  # 15% annualized volatility
                    # In low volatility, look for breakout signals
                    if current_price > bb_upper:
                        bullish_signals += 1
                    elif current_price < bb_lower:
                        bearish_signals += 1
            
            # Trading decision based on multiple confirmations (now up to 5 signals)
            if bullish_signals >= 3 and last_signal != 'BUY':
                print(f"   🟢 STRONG BUY SIGNAL! (Confirms: {bullish_signals}/5)")
                print(f"   💰 RSI: {current_rsi:.2f} | Price vs BB: {current_price:.2f} vs {bb_lower:.2f}")
                if current_volatility is not None:
                    print(f"   📊 Volatility: {current_volatility:.2%}")
                logger.info(f"🟢 {symbol} STRONG BUY SIGNAL! (Confirms: {bullish_signals}/5)")
                logger.info(f"   RSI: {current_rsi:.2f} | Price vs BB: {current_price:.2f} vs {bb_lower:.2f}")
                if current_volatility is not None:
                    logger.info(f"   📊 Volatility: {current_volatility:.2%}")
                last_signal = 'BUY'
                
                # Enhanced buy logic
                try:
                    balance = get_balance()
                    if balance and 'available_margin' in balance:
                        available_margin = balance['available_margin']
                        # Dynamic position sizing based on signal strength
                        position_size = available_margin * (0.01 * bullish_signals)  # 1-4% based on signals
                        
                        if position_size > 1000:  # Minimum ₹1000 position
                            print(f"   💵 Placing BUY order: ₹{position_size:.2f} @ ₹{current_price:.2f}")
                            order = place_order(symbol, 'buy', position_size, current_price, 'limit', 'myntapi')
                            if order:
                                print(f"   ✅ BUY order placed: {order}")
                                logger.info(f"✅ BUY order placed: {order}")
                                
                                # Place orders on additional symbols
                                place_orders_on_additional_symbols('BUY', bullish_signals, current_price)
                            else:
                                print(f"   ❌ Failed to place BUY order")
                                logger.error("❌ Failed to place BUY order")
                        else:
                            print(f"   ⚠️ Insufficient margin: ₹{available_margin:.2f}")
                            logger.warning(f"⚠️ Insufficient margin for {symbol}: ₹{available_margin:.2f}")
                            
                except Exception as e:
                    logger.error(f"❌ Buy order failed: {e}")
                
            elif bearish_signals >= 3 and last_signal != 'SELL':
                print(f"   🔴 STRONG SELL SIGNAL! (Confirms: {bearish_signals}/5)")
                print(f"   💸 RSI: {current_rsi:.2f} | Price vs BB: {current_price:.2f} vs {bb_upper:.2f}")
                if current_volatility is not None:
                    print(f"   📊 Volatility: {current_volatility:.2%}")
                logger.info(f"🔴 {symbol} STRONG SELL SIGNAL! (Confirms: {bearish_signals}/5)")
                logger.info(f"   RSI: {current_rsi:.2f} | Price vs BB: {current_price:.2f} vs {bb_upper:.2f}")
                if current_volatility is not None:
                    logger.info(f"   📊 Volatility: {current_volatility:.2%}")
                last_signal = 'SELL'
                
                # Enhanced sell logic
                try:
                    positions = zebubot.myntapi.get_positions() if zebubot.myntapi else []
                    primary_sell_successful = False
                    
                    for position in positions:
                        if position.get('tsym') == symbol.split('|')[1] if '|' in symbol else symbol:
                            net_qty = float(position.get('netqty', 0))
                            if net_qty > 0:
                                print(f"   💸 Placing SELL order: {net_qty} shares @ ₹{current_price:.2f}")
                                order = place_order(symbol, 'sell', net_qty, current_price, 'limit', 'myntapi')
                                if order:
                                    print(f"   ✅ SELL order placed: {order}")
                                    logger.info(f"✅ SELL order placed: {order}")
                                    primary_sell_successful = True
                                else:
                                    print(f"   ❌ Failed to place SELL order")
                                    logger.error("❌ Failed to place SELL order")
                            else:
                                print(f"   ⚠️ No position to sell")
                                logger.warning(f"⚠️ No position to sell for {symbol}")
                            break
                    else:
                        logger.warning(f"⚠️ No position found for {symbol}")
                    
                    # Place orders on additional symbols if primary sell was successful
                    if primary_sell_successful:
                        place_orders_on_additional_symbols('SELL', bearish_signals, current_price)
                        
                except Exception as e:
                    logger.error(f"❌ Sell order failed: {e}")
                
            elif 30 <= current_rsi <= 70 and abs(bullish_signals - bearish_signals) <= 1:
                if last_signal:
                    volatility_info = f" | Vol: {current_volatility:.2%}" if current_volatility is not None else ""
                    print(f"   🟡 NEUTRAL ZONE: {current_rsi:.2f} (Previous: {last_signal}){volatility_info}")
                    logger.info(f"🟡 {symbol} NEUTRAL ZONE: {current_rsi:.2f} (Previous: {last_signal}){volatility_info}")
                    last_signal = None
        else:
            print(f"   ⏳ RSI: Calculating... | Vol: {current_volume:,.0f}")
            logger.info(f"📊 {symbol}: ₹{current_price:.2f} | RSI: Calculating... | Vol: {current_volume:,.0f}")
    else:
        print(f"   📊 Collecting data ({len(price_history)}/{max(rsi_period + 1, 50)}) | Vol: {current_volume:,.0f}")
        logger.info(f"📊 {symbol}: ₹{current_price:.2f} | Collecting data ({len(price_history)}/{max(rsi_period + 1, 50)}) | Vol: {current_volume:,.0f}")

def refresh_historical_data(symbol, days_back=7):
    """Refresh historical data periodically to keep indicators accurate."""
    global historical_data_loaded
    
    try:
        if not zebubot or not zebubot.myntapi:
            return False
        
        # Only refresh if we have some data and it's been a while
        if len(price_history) > 0 and tick_count % 100 == 0:  # Every 100 ticks
            logger.info(f"🔄 Refreshing historical data for {symbol}")
            print(f"🔄 Refreshing historical data for {symbol}...")
            
            # Load recent data (last 7 days) to update indicators
            success = load_historical_data(symbol, days_back=days_back, interval_minutes=1)
            if success:
                logger.info("✅ Historical data refreshed successfully")
                print("✅ Historical data refreshed successfully")
            return success
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to refresh historical data: {e}")
        return False

def get_market_summary():
    """Get a summary of current market conditions."""
    if not zebubot or not zebubot.myntapi:
        return
    
    try:
        realtime_data = zebubot.realtime_data
        
        if realtime_data:
            print(f"\n{'='*60}")
            print(f"📈 MARKET SUMMARY (Indian Stocks) - Optimized")
            print(f"{'='*60}")
            for symbol, data in realtime_data.items():
                price = data.get('price', 0)
                volume = data.get('volume', 0)
                last_update = data.get('last_update', 0)
                age = time.time() - last_update
                
                print(f"   {symbol}: ₹{price:.2f} (Vol: {volume:,.0f}, Age: {age:.1f}s)")
            print(f"{'='*60}")
            logger.info("📈 Market Summary (Indian Stocks) - Optimized:")
            for symbol, data in realtime_data.items():
                price = data.get('price', 0)
                volume = data.get('volume', 0)
                last_update = data.get('last_update', 0)
                age = time.time() - last_update
                
                logger.info(f"   {symbol}: ₹{price:.2f} (Vol: {volume:,.0f}, Age: {age:.1f}s)")
        else:
            print(f"\n📈 No real-time data available")
            logger.info("📈 No real-time data available")
            
    except Exception as e:
        print(f"\n❌ Error getting market summary: {e}")
        logger.error(f"Error getting market summary: {e}")

def main():
    """Main function called on every tick."""
    on_tick(current_symbol, ticker_data)
    
    # Refresh historical data periodically
    refresh_historical_data(current_symbol, days_back=7)
    
    # Get market summary every 20 ticks for performance
    if len(price_history) % 20 == 0:
        get_market_summary()

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print(f"🤖 MYNTAPI RSI STRATEGY - CYTHON OPTIMIZED")
    print(f"{'='*70}")
    print(f"📊 Primary Symbol: {current_symbol}")
    print(f"🎯 Additional Symbols: {', '.join(additional_symbols)}")
    print(f"⚙️ RSI Period: {rsi_period}")
    print(f"📊 Volatility: 20-day annualized calculation")
    print(f"🚀 Performance: {'Cython Optimized' if CYTHON_AVAILABLE else 'Standard Python'}")
    print(f"🔄 Data Feed: Websocket (real-time) + Polling (1s fallback)")
    print(f"📈 Historical Data: 30 days (1-min intervals) loaded on startup")
    print(f"🔄 Data Refresh: Every 100 ticks (7 days recent data)")
    print(f"📡 Status: WS=Websocket, POLL=Polling fallback")
    print(f"🇮🇳 Trading Indian stocks via MyntAPI (Noren)")
    print(f"{'='*70}")
    
    logger.info("🤖 MyntAPI RSI Strategy Started - Cython Optimized")
    logger.info(f"📊 Primary Symbol: {current_symbol}")
    logger.info(f"🎯 Additional Symbols: {', '.join(additional_symbols)}")
    logger.info(f"⚙️ RSI Period: {rsi_period}")
    logger.info("📊 Volatility: 20-day annualized calculation")
    logger.info(f"🚀 Performance: {'Cython Optimized' if CYTHON_AVAILABLE else 'Standard Python'}")
    logger.info("🔄 Data Feed: Websocket (real-time) + Polling (1s fallback)")
    logger.info("📈 Historical Data: 30 days (1-min intervals) loaded on startup")
    logger.info("🔄 Data Refresh: Every 100 ticks (7 days recent data)")
    logger.info("🇮🇳 Trading Indian stocks via MyntAPI (Noren)")
    main()
