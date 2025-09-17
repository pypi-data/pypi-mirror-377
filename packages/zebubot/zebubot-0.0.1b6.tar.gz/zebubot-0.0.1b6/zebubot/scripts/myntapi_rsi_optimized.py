"""
MyntAPI RSI Optimized Strategy
A high-performance RSI-based trading strategy optimized for MyntAPI
"""

import pandas as pd
import numpy as np
from collections import deque
import time

# Global variables for strategy state
price_history = deque(maxlen=1000)
rsi_period = 14
last_signal = None
position = None

def calculate_rsi(prices, period=14):
    """Calculate RSI using pandas for efficiency"""
    if len(prices) < period + 1:
        return None
    
    prices_series = pd.Series(prices)
    delta = prices_series.diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if not rsi.empty else None

def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])

def on_tick(symbol, ticker_data):
    """Main strategy logic executed on each tick"""
    global last_signal, position
    
    current_price = ticker_data.get('price', 0)
    if current_price <= 0:
        return
    
    # Add price to history
    price_history.append(current_price)
    
    # Need at least RSI period + 1 prices for calculation
    if len(price_history) < rsi_period + 1:
        return
    
    # Convert to list for calculations
    prices = list(price_history)
    
    # Calculate RSI
    rsi = calculate_rsi(prices, rsi_period)
    if rsi is None:
        return
    
    # Calculate SMA for trend confirmation
    sma_20 = calculate_sma(prices, 20)
    sma_50 = calculate_sma(prices, 50)
    
    # Log current status
    print(f"[RSI] {symbol} RSI: {rsi:.2f}")
    
    # RSI Strategy Logic
    if rsi < 30 and last_signal != 'BUY':
        # Oversold condition - potential buy signal
        if sma_20 and sma_50 and sma_20 > sma_50:
            # Additional trend confirmation
            print(f"🟢 [BUY] {symbol} RSI < 30: Potential BUY signal (RSI: {rsi:.2f})")
            last_signal = 'BUY'
            position = 'LONG'
            
            # Place buy order
            place_order(symbol, 'buy', 10, current_price, 'limit', 'myntapi')
            
    elif rsi > 70 and last_signal != 'SELL':
        # Overbought condition - potential sell signal
        if sma_20 and sma_50 and sma_20 < sma_50:
            # Additional trend confirmation
            print(f"🔴 [SELL] {symbol} RSI > 70: Potential SELL signal (RSI: {rsi:.2f})")
            last_signal = 'SELL'
            position = 'SHORT'
            
            # Place sell order
            place_order(symbol, 'sell', 10, current_price, 'limit', 'myntapi')
    
    # Additional price-based signals
    if current_price < 40000:
        print(f"[SELL] {symbol} price below $40,000: {current_price}")
    elif current_price > 50000:
        print(f"[BUY] {symbol} price above $50,000: {current_price}")

def main():
    """Main function called by the executor"""
    # This will be called with current_symbol and ticker_data
    # The actual call is handled by the executor
    pass

# Strategy configuration
strategy_config = {
    'name': 'MyntAPI RSI Optimized',
    'description': 'RSI-based trading strategy with trend confirmation',
    'version': '1.0.0',
    'author': 'ZebuBot Team',
    'parameters': {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'sma_fast': 20,
        'sma_slow': 50
    }
}
