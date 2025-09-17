#!/usr/bin/env python3
"""
ZebuBot Setup Script
This script helps set up ZebuBot for first-time users
"""

import os
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = ['scripts', 'configs', 'logs', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_config_file():
    """Create configuration file from template"""
    if not Path('zebubot_config.yaml').exists():
        if Path('zebubot_config_template.yaml').exists():
            shutil.copy('zebubot_config_template.yaml', 'zebubot_config.yaml')
            print("✅ Created zebubot_config.yaml from template")
            print("⚠️  Please edit zebubot_config.yaml with your MyntAPI credentials")
        else:
            print("❌ Configuration template not found")
    else:
        print("ℹ️  Configuration file already exists")

def create_sample_strategy():
    """Create a sample strategy"""
    scripts_dir = Path('scripts')
    configs_dir = Path('configs')
    
    # Create sample RSI strategy
    sample_script = scripts_dir / 'sample_rsi_strategy.py'
    if not sample_script.exists():
        sample_script.write_text('''#!/usr/bin/env python3
"""
Sample RSI Strategy
This is a sample strategy to get you started
"""

from collections import deque
import pandas as pd

price_history = deque(maxlen=1000)
last_signal = None

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return None
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def on_tick(symbol, data):
    global last_signal
    
    price = data.get("price", 0.0)
    if price <= 0:
        logger.debug(f"{symbol} no valid price, skipping")
        return
    
    price_history.append(price)
    
    # Get strategy parameters
    rsi_period = strategy.get("rsi_period", 14) if isinstance(strategy, dict) else 14
    oversold_level = strategy.get("oversold_level", 30) if isinstance(strategy, dict) else 30
    overbought_level = strategy.get("overbought_level", 70) if isinstance(strategy, dict) else 70
    
    if len(price_history) >= rsi_period + 1:
        prices = list(price_history)
        rsi = calculate_rsi(prices, rsi_period)
        
        if rsi is not None:
            if rsi < oversold_level and last_signal != "BUY":
                logger.info(f"🟢 BUY Signal! RSI: {rsi:.2f}")
                last_signal = "BUY"
                # Place buy order here
                # place_order(symbol, "buy", 10, price, "limit", "myntapi")
            elif rsi > overbought_level and last_signal != "SELL":
                logger.info(f"🔴 SELL Signal! RSI: {rsi:.2f}")
                last_signal = "SELL"
                # Place sell order here
                # place_order(symbol, "sell", 10, price, "limit", "myntapi")
            
            logger.info(f"[TICK] {symbol} price={price:.2f} RSI={rsi:.2f}")

def main():
    on_tick(current_symbol, ticker_data)
''')
        print("✅ Created sample RSI strategy")

    # Create sample config
    sample_config = configs_dir / 'sample_rsi_strategy.yaml'
    if not sample_config.exists():
        sample_config.write_text('''# Sample RSI Strategy Configuration
symbols:
  - NSE:SBIN-EQ
exchange: myntapi
strategy:
  rsi_period: 14
  oversold_level: 30
  overbought_level: 70
risk:
  min_position_inr: 1000
  max_position_pct: 0.04
''')
        print("✅ Created sample strategy configuration")

def main():
    """Main setup function"""
    print("🚀 Setting up ZebuBot...")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Create configuration file
    create_config_file()
    
    # Create sample strategy
    create_sample_strategy()
    
    print("\n" + "=" * 40)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit zebubot_config.yaml with your MyntAPI credentials")
    print("2. Run: python -m zebubot strategy create my_strategy --type rsi")
    print("3. Run: python -m zebubot create my_strategy.py")
    print("\nFor option trading:")
    print("4. Run: python -m zebubot strategy option my_option_strategy")
    print("5. Run: python -m zebubot create my_option_strategy.py")

if __name__ == "__main__":
    main()
