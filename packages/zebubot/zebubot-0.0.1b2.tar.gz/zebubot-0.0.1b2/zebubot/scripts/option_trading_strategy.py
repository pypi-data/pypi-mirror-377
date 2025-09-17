"""
Option Trading Strategy Script with Start/End Time
This script places option orders at a specified start time and exits at end time.
No margin checking - places orders directly as requested.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time
from datetime import datetime, timedelta
from collections import deque
import threading
import logging
import requests
import zipfile
import io

# Real-time context variables (injected by ZebuBot):
# - current_symbol: Current symbol being processed
# - current_price: Current price from ticker data
# - current_volume: Current volume from ticker data
# - current_timestamp: Current timestamp
# - ticker_data: Full ticker data dictionary
# - zebubot/bot: ZebuBot instance
# - logger: Logger instance

# Global variables for option trading
price_history = deque(maxlen=1000)
tick_count = 0
strategy_active = False
position_entered = False
entry_time = None
exit_time = None
entry_price = None
entry_quantity = 0
order_placed = False
position_exited = False
session_id = None  # Track current session to prevent duplicate orders
square_off_attempted = False  # Track if square-off has been attempted
leg_orders_placed = {}  # Track which legs have been placed
symbol_cache = {}  # Cache resolved symbols to avoid repeated LTP calculations
websocket_ltp_cache = {}  # Cache LTP data from websocket for fast access
option_symbols_subscribed = set()  # Track which option symbols are subscribed
pre_calculated_symbols = {}  # Store pre-calculated symbol info for instant access

# Master data for NFO, BFO and MCX symbols
nfo_master_data = None
bfo_master_data = None
mcx_master_data = None
master_data_loaded = False

# Leg positions tracking
leg_positions = {}
leg_orders = {}
leg_pnl = {}  # Track P&L for each leg
last_pnl_calculation = 0  # Throttle P&L calculations
overall_pnl = 0  # Track overall P&L

# Strategy configuration (can be overridden by YAML config)
strategy_config = {
    'start_time': '09:30:00',  # Market start time
    'end_time': '15:30:00',    # Market end time
    'option_symbol': 'NSE:NIFTY 50',  # Primary option symbol
    'option_type': 'CE',  # Call or Put option (CE/PE)
    'strike_price': 0,  # 0 means ATM (At The Money)
    'quantity': 1,  # Number of lots
    'order_type': 'market',  # market or limit
    'product_type': 'I',  # I for Intraday, M for MIS
    'entry_delay_seconds': 0,  # Delay after start time before placing order
    'exit_delay_seconds': 0,  # Delay before end time to exit position
    'square_off_time': '15:10:00',  # Square off time
    'overall_target': 1000,  # Overall target in INR
    'overall_stop_loss': 1000,  # Overall stop loss in INR
    'idx_pair': 'NSE:NIFTY 50',  # Index pair
    'legs': {  # Default legs configuration
        1: {
            'exch': 'MCX',
            'symbol': 'CRUDEOIL',
            'expiry': '17-09-2025',
            'option_type': 'CE',
            'strike_price': 'ATM+1',
            'lot_size': 1,
            'order_type': 'market',
            'product_type': 'I',
            'entry_time': '09:30:00',
            'exit_time': '15:30:00'
        }
    }
}

def get_data(url):
    """Download and extract data from zip file URL."""
    try:
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        ur = (url.split("/")[-1].split(".")[0])
        
        with z.open(ur + ".txt") as f:
            data = f.read()
            df = pd.read_csv(io.BytesIO(data), dtype=str)
        return df
    except Exception as e:
        logger.error(f"Error downloading data from {url}: {e}")
        return None

def subscribe_to_option_symbols():
    """Subscribe to all option symbols for real-time LTP data."""
    global websocket_ltp_cache, option_symbols_subscribed, symbol_cache, pre_calculated_symbols
    
    try:
        if not zebubot or not hasattr(zebubot, 'myntapi'):
            logger.error("ZebuBot or MyntAPI not available for websocket subscription")
            return False
        
        # Check if already subscribed to avoid duplicates
        if len(option_symbols_subscribed) > 0:
            logger.info(f"Already subscribed to {len(option_symbols_subscribed)} option symbols, skipping...")
            return True
        
        # Pre-calculate all symbols and cache them to avoid repeated calculations
        logger.info("🚀 Pre-calculating all leg symbols for ultra-fast execution...")
        all_option_symbols = []
        pre_calculated_symbols = {}  # Store pre-calculated symbol info
        
        for leg_id, leg_config in strategy_config.get('legs', {}).items():
            symbol_info = resolve_symbol(leg_config)
            if symbol_info:
                # Create websocket symbol format
                ws_symbol = f"{symbol_info['exchange']}|{symbol_info['token']}"
                all_option_symbols.append(ws_symbol)
                websocket_ltp_cache[ws_symbol] = {'price': 0, 'timestamp': 0}
                
                # Store pre-calculated symbol info for instant access
                pre_calculated_symbols[leg_id] = {
                    'symbol_info': symbol_info,
                    'ws_symbol': ws_symbol,
                    'leg_config': leg_config
                }
                logger.debug(f"✅ Pre-calculated symbol for leg {leg_id}: {ws_symbol}")
        
        if not all_option_symbols:
            logger.warning("No option symbols found to subscribe")
            return False
        
        # Subscribe to all symbols at once
        logger.info(f"📡 Subscribing to {len(all_option_symbols)} option symbols for real-time LTP...")
        for symbol in all_option_symbols:
            if symbol not in option_symbols_subscribed:
                zebubot.myntapi.api.subscribe(symbol)
                option_symbols_subscribed.add(symbol)
                logger.debug(f"📡 Subscribed to {symbol}")
        
        logger.info(f"✅ Subscribed to {len(option_symbols_subscribed)} option symbols")
        return True
        
    except Exception as e:
        logger.error(f"Error subscribing to option symbols: {e}")
        return False

def update_websocket_ltp_cache(symbol, ticker_data):
    """Update LTP cache from websocket data."""
    global websocket_ltp_cache
    
    try:
        if symbol in websocket_ltp_cache:
            websocket_ltp_cache[symbol] = {
                'price': ticker_data.get('price', 0),
                'timestamp': ticker_data.get('timestamp', 0)
            }
            logger.debug(f"📊 Updated LTP cache for {symbol}: ₹{ticker_data.get('price', 0)}")
    except Exception as e:
        logger.debug(f"Error updating LTP cache for {symbol}: {e}")

def get_cached_ltp(exchange, token):
    """Get cached LTP data for a symbol."""
    global websocket_ltp_cache
    
    try:
        symbol_key = f"{exchange}|{token}"
        if symbol_key in websocket_ltp_cache:
            return websocket_ltp_cache[symbol_key]['price']
        return None
    except Exception as e:
        logger.debug(f"Error getting cached LTP for {exchange}|{token}: {e}")
        return None

def load_master_data():
    """Load NFO, BFO and MCX master data."""
    global nfo_master_data, bfo_master_data, mcx_master_data, master_data_loaded
    
    try:
        logger.info("📊 Loading NFO master data...")
        print("📊 Loading NFO master data...")
        
        # Load NFO data
        nfo_master_data = get_data("https://go.mynt.in/NFO_symbols.txt.zip")
        if nfo_master_data is not None:
            nfo_master_data['OptionType'] = nfo_master_data['OptionType'].replace('XX', 'FUT')
            nfo_master_data['Expiry Month'] = pd.to_datetime(nfo_master_data['Expiry'], format='%d-%b-%Y').dt.strftime('%b').str.upper()
            nfo_master_data['Expiry date'] = pd.to_datetime(nfo_master_data['Expiry'], format='%d-%b-%Y').dt.strftime('%d').str.upper()
            nfo_master_data['StrikePrice'] = nfo_master_data['StrikePrice'].astype(str).str.replace(r'\.0$', '', regex=True)
            logger.info(f"✅ NFO master data loaded: {len(nfo_master_data)} symbols")
            print(f"✅ NFO master data loaded: {len(nfo_master_data)} symbols")
        else:
            logger.error("❌ Failed to load NFO master data")
            print("❌ Failed to load NFO master data")
            return False
        
        logger.info("📊 Loading BFO master data...")
        print("📊 Loading BFO master data...")
        
        # Load BFO data
        bfo_master_data = get_data("https://go.mynt.in/BFO_symbols.txt.zip")
        if bfo_master_data is not None:
            bfo_master_data['OptionType'] = bfo_master_data['OptionType'].replace('XX', 'FUT')
            bfo_master_data['Expiry Month'] = pd.to_datetime(bfo_master_data['Expiry'], format='%d-%b-%Y').dt.strftime('%b').str.upper()
            bfo_master_data['Expiry date'] = pd.to_datetime(bfo_master_data['Expiry'], format='%d-%b-%Y').dt.strftime('%d').str.upper()
            
            # BFO uses 'Strike' column instead of 'StrikePrice'
            if 'Strike' in bfo_master_data.columns:
                bfo_master_data['StrikePrice'] = bfo_master_data['Strike'].astype(str).str.replace(r'\.0$', '', regex=True)
            else:
                bfo_master_data['StrikePrice'] = bfo_master_data['StrikePrice'].astype(str).str.replace(r'\.0$', '', regex=True)
            
            logger.info(f"✅ BFO master data loaded: {len(bfo_master_data)} symbols")
            print(f"✅ BFO master data loaded: {len(bfo_master_data)} symbols")
        else:
            logger.error("❌ Failed to load BFO master data")
            print("❌ Failed to load BFO master data")
            return False
        
        logger.info("📊 Loading MCX master data...")
        print("📊 Loading MCX master data...")
        
        # Load MCX data
        mcx_master_data = get_data("https://go.mynt.in/MCX_symbols.txt.zip")
        if mcx_master_data is not None:
            mcx_master_data['OptionType'] = mcx_master_data['OptionType'].replace('XX', 'FUT')
            mcx_master_data['Expiry Month'] = pd.to_datetime(mcx_master_data['Expiry'], format='%d-%b-%Y').dt.strftime('%b').str.upper()
            mcx_master_data['Expiry date'] = pd.to_datetime(mcx_master_data['Expiry'], format='%d-%b-%Y').dt.strftime('%d').str.upper()
            
            # MCX uses 'StrikePrice' column, but for futures (XX) it might be 0 or missing
            if 'StrikePrice' in mcx_master_data.columns:
                mcx_master_data['StrikePrice'] = mcx_master_data['StrikePrice'].astype(str).str.replace(r'\.0$', '', regex=True)
            else:
                # If StrikePrice column doesn't exist, create it with 0 for futures
                mcx_master_data['StrikePrice'] = '0'
            
            logger.info(f"✅ MCX master data loaded: {len(mcx_master_data)} symbols")
            print(f"✅ MCX master data loaded: {len(mcx_master_data)} symbols")
        else:
            logger.error("❌ Failed to load MCX master data")
            print("❌ Failed to load MCX master data")
            return False
        
        master_data_loaded = True
        logger.info("✅ Master data loaded successfully")
        print("✅ Master data loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading master data: {e}")
        print(f"❌ Error loading master data: {e}")
        return False

def load_strategy_config():
    """Load strategy configuration from YAML file or use defaults."""
    global strategy_config
    
    try:
        # Try to load from YAML config if available
        # The 'strategy' variable is injected by RealtimeExecutor
        print(f"🔍 Debug: Checking for strategy in globals...")
        print(f"   'strategy' in globals: {'strategy' in globals()}")
        if 'strategy' in globals():
            print(f"   strategy type: {type(globals()['strategy'])}")
            print(f"   strategy value: {globals()['strategy']}")
        
        if 'strategy' in globals() and isinstance(globals()['strategy'], dict):
            strategy = globals()['strategy']
            # Update strategy_config with values from YAML
            print(f"📋 Loading YAML config: {strategy}")
            strategy_config.update({
                'start_time': strategy.get('start_time', strategy_config['start_time']),
                'end_time': strategy.get('end_time', strategy_config['end_time']),
                'square_off_time': strategy.get('square_off_time', '15:10:00'),
                'overall_target': strategy.get('overall_target', 1000),
                'overall_stop_loss': strategy.get('overall_stop_loss', 1000),
                'idx_pair': strategy.get('idx_pair', 'NSE:NIFTY 50'),
                'legs': strategy.get('legs', {}),
            })
            logger.info("✅ Strategy configuration loaded from YAML")
            print("✅ Strategy configuration loaded from YAML")
        else:
            logger.info("📋 Using default strategy configuration")
            print("📋 Using default strategy configuration")
            
    except Exception as e:
        logger.error(f"❌ Error loading strategy config: {e}")
        print(f"❌ Error loading strategy config: {e}")
        logger.info("📋 Using default strategy configuration")
        print("📋 Using default strategy configuration")

def calculate_expiry_date(expiry_str, base_date=None):
    """Calculate expiry date from string like 'current week', 'next week', etc."""
    if base_date is None:
        base_date = datetime.now()
    
    try:
        if expiry_str.lower() == "current week":
            # Find Thursday of current week
            days_ahead = 3 - base_date.weekday()  # Thursday is 3
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            return base_date + timedelta(days=days_ahead)
        
        elif expiry_str.lower() == "next week":
            # Find Thursday of next week
            days_ahead = 3 - base_date.weekday() + 7
            return base_date + timedelta(days=days_ahead)
        
        elif expiry_str.lower() == "current month":
            # Last Thursday of current month
            next_month = base_date.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            # Find last Thursday
            last_thursday = last_day - timedelta(days=(last_day.weekday() - 3) % 7)
            return last_thursday
        
        elif expiry_str.lower() == "next month":
            # Last Thursday of next month
            next_month = base_date.replace(day=28) + timedelta(days=4)
            next_month = next_month.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            last_thursday = last_day - timedelta(days=(last_day.weekday() - 3) % 7)
            return last_thursday
        
        else:
            # Try to parse as DD-MM-YYYY
            return datetime.strptime(expiry_str, '%d-%m-%Y')
    
    except Exception as e:
        logger.error(f"Error calculating expiry date for '{expiry_str}': {e}")
        return None

def find_closest_strike(target_strike, available_strikes):
    """Find the closest available strike to the target strike."""
    if not available_strikes:
        return None
    
    # Find the closest strike by absolute difference
    closest_strike = min(available_strikes, key=lambda x: abs(x - target_strike))
    return closest_strike

def get_atm_strike(symbol, exchange="NFO"):
    """Get ATM strike price for a symbol."""
    try:
        if not zebubot or not zebubot.myntapi:
            return None
        
        # Get underlying symbol from strategy config
        idx_pair = strategy_config.get('idx_pair', 'NSE:NIFTY 50')
        underlying_symbol = idx_pair
        
        # If idx_pair doesn't contain exchange, add it
        if ':' not in underlying_symbol:
            if exchange.upper() == "MCX":
                underlying_symbol = f"MCX:{symbol}"
            else:
                underlying_symbol = f"NSE:{symbol}"
        
        logger.debug(f"Using underlying symbol for ATM calculation: {underlying_symbol}")
        
        ticker = zebubot.get_ticker(underlying_symbol)
        if not ticker:
            # Fallback to NSE if configured symbol fails
            if exchange.upper() == "MCX":
                underlying_symbol = f"NSE:{symbol}"
            else:
                underlying_symbol = f"NSE:{symbol}"
            ticker = zebubot.get_ticker(underlying_symbol)
            if not ticker:
                return None
        
        current_price = ticker.get('price', 0)
        if current_price <= 0:
            return None
        
        # Log underlying price for reference
        logger.info(f"📊 Underlying Price: {underlying_symbol} = ₹{current_price}")
        
        # Round to appropriate intervals based on symbol
        if symbol.upper() == "NIFTY":
            strike = round(current_price / 50) * 50
        elif symbol.upper() == "BANKNIFTY":
            strike = round(current_price / 100) * 100
        elif symbol.upper() in ["GOLD", "SILVER", "CRUDEOIL", "NATURALGAS", "GOLDTEN", "NATGASMINI"]:
            # MCX commodities - round to nearest 1
            strike = round(current_price)
        else:
            strike = round(current_price)
        
        logger.debug(f"ATM calculation for {symbol}: current_price={current_price}, calculated_strike={strike}")
        
        # For MCX commodities, we need to find the nearest available strike
        if exchange.upper() == "MCX" and symbol.upper() in ["GOLD", "SILVER", "CRUDEOIL", "NATURALGAS", "GOLDTEN", "NATGASMINI"]:
            # We can't find the nearest strike here because we don't have available_strikes
            # This will be handled in the resolve_symbol function
            logger.debug(f"MCX commodity ATM: {strike} (will find nearest available strike later)")
        
        return strike
    
    except Exception as e:
        logger.error(f"Error getting ATM strike for {symbol}: {e}")
        return None

def resolve_symbol(leg_config):
    """Resolve trading symbol from leg configuration using master data."""
    global symbol_cache
    
    try:
        if not master_data_loaded:
            logger.error("Master data not loaded")
            return None
        
        # Create a cache key for this leg configuration
        cache_key = f"{leg_config.get('exch', 'NFO')}_{leg_config.get('symbol', 'NIFTY')}_{leg_config.get('expiry', 'current week')}_{leg_config.get('option_type', 'CE')}_{leg_config.get('strike_price', 0)}_{leg_config.get('price_premium', 'none')}"
        
        # Check if we have a cached result for this configuration
        if cache_key in symbol_cache:
            logger.debug(f"Using cached symbol resolution for {cache_key}")
            return symbol_cache[cache_key]
        
        exch = leg_config.get('exch', 'NFO')
        symbol = leg_config.get('symbol', 'NIFTY')
        expiry = leg_config.get('expiry', 'current week')
        option_type = leg_config.get('option_type', 'CE')
        strike_price = leg_config.get('strike_price', 0)
        
        # Get master data based on exchange
        if exch.upper() == 'NFO':
            master_data = nfo_master_data
        elif exch.upper() == 'BFO':
            master_data = bfo_master_data
        elif exch.upper() == 'MCX':
            master_data = mcx_master_data
        else:
            logger.error(f"Unsupported exchange: {exch}")
            return None
            
        if master_data is None:
            return None
        
        # Filter by exchange and symbol first
        symbol_data = master_data[
            (master_data['Exchange'] == exch.upper()) &
            (master_data['Symbol'] == symbol.upper())
        ]
        
        if len(symbol_data) == 0:
            logger.error(f"No symbols found for {exch}:{symbol}")
            return None
        
        # Calculate expiry date and find matching expiry in master data
        expiry_date = calculate_expiry_date(expiry)
        if not expiry_date:
            return None
        
        # Find the closest expiry date in master data
        symbol_data = symbol_data.copy()  # Avoid SettingWithCopyWarning
        symbol_data['ExpiryDate'] = pd.to_datetime(symbol_data['Expiry'], format='%d-%b-%Y')
        target_expiry = expiry_date
        
        # Find the closest expiry date
        symbol_data['ExpiryDiff'] = abs((symbol_data['ExpiryDate'] - target_expiry).dt.days)
        closest_expiry = symbol_data.loc[symbol_data['ExpiryDiff'].idxmin()]
        actual_expiry_str = closest_expiry['Expiry']
        
        logger.debug(f"Found closest expiry for {symbol}: {actual_expiry_str} (target: {expiry_date.strftime('%d-%b-%Y')})")
        
        # Filter by expiry and option type
        expiry_data = symbol_data[
            (symbol_data['Expiry'] == actual_expiry_str) &
            (symbol_data['OptionType'] == option_type.upper())
        ]
        
        if len(expiry_data) == 0:
            logger.error(f"No {option_type} options found for {exch}:{symbol} {actual_expiry_str}")
            return None
        
        # Get available strike prices from master data for this symbol and expiry
        # For futures (FUT), strike price is 0, so we don't need to filter by strike
        if option_type.upper() == 'FUT':
            available_strikes = [0]  # Futures don't have strike prices
            logger.info(f"Futures contract for {exch}:{symbol} {actual_expiry_str}")
        else:
            # For options, get actual strike prices
            strike_prices = expiry_data['StrikePrice'].astype(str)
            # Filter out '0' and empty values for options
            valid_strikes = strike_prices[(strike_prices != '0') & (strike_prices != '') & (strike_prices != 'nan')]
            available_strikes = [int(s) for s in valid_strikes if s.isdigit() or (s.replace('.', '').replace('-', '').isdigit())]
            available_strikes = sorted(list(set(available_strikes)))  # Remove duplicates and sort
            
        logger.debug(f"Available strikes for {exch}:{symbol} {actual_expiry_str} {option_type}: {len(available_strikes)} strikes")
        if len(available_strikes) <= 20:  # Only log if reasonable number of strikes
            logger.debug(f"Available strikes: {available_strikes}")
        
        # Handle strike price calculation using available strikes
        actual_strike = None
        strike_data = None
        
        # For futures, always use strike 0
        if option_type.upper() == 'FUT':
            actual_strike = 0
            strike_data = expiry_data.iloc[0]  # Take the first (and only) futures contract
            logger.info(f"Futures contract selected: {actual_expiry_str}")
        elif isinstance(strike_price, str):
            if strike_price.upper() == 'ATM':
                target_strike = get_atm_strike(symbol, exch)
                if target_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    actual_strike = find_closest_strike(target_strike, available_strikes)
            elif strike_price.upper() == 'ITM':
                # ITM: For CE, strike below ATM; For PE, strike above ATM
                atm_strike = get_atm_strike(symbol, exch)
                if atm_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    if option_type.upper() == 'CE':
                        # For CE, find strike below ATM
                        itm_strikes = [s for s in available_strikes if s < atm_strike]
                        actual_strike = max(itm_strikes) if itm_strikes else min(available_strikes)
                    else:  # PE
                        # For PE, find strike above ATM
                        itm_strikes = [s for s in available_strikes if s > atm_strike]
                        actual_strike = min(itm_strikes) if itm_strikes else max(available_strikes)
            elif strike_price.upper() == 'OTM':
                # OTM: For CE, strike above ATM; For PE, strike below ATM
                atm_strike = get_atm_strike(symbol, exch)
                if atm_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    if option_type.upper() == 'CE':
                        # For CE, find strike above ATM
                        otm_strikes = [s for s in available_strikes if s > atm_strike]
                        actual_strike = min(otm_strikes) if otm_strikes else max(available_strikes)
                    else:  # PE
                        # For PE, find strike below ATM
                        otm_strikes = [s for s in available_strikes if s < atm_strike]
                        actual_strike = max(otm_strikes) if otm_strikes else min(available_strikes)
            elif strike_price.upper().startswith('ITM+'):
                offset = int(strike_price.split('+')[1])
                atm_strike = get_atm_strike(symbol, exch)
                if atm_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    # Find the nearest available strike to ATM first
                    nearest_atm_strike = find_closest_strike(atm_strike, available_strikes)
                    logger.info(f"🎯 ITM+{offset} {option_type}: Underlying=₹{atm_strike}, Nearest ATM={nearest_atm_strike}")
                    logger.debug(f"Available strikes: {sorted(available_strikes)}")
                    
                    if option_type.upper() == 'CE':
                        # For CE, find strikes below nearest ATM, then go further down
                        itm_strikes = [s for s in available_strikes if s < nearest_atm_strike]
                        if itm_strikes:
                            itm_strikes.sort(reverse=True)  # Sort descending
                            actual_strike = itm_strikes[min(offset-1, len(itm_strikes)-1)]
                            logger.debug(f"ITM+{offset} CE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} below nearest ATM)")
                        else:
                            actual_strike = min(available_strikes)
                            logger.warning(f"ITM+{offset} CE: No strikes below nearest ATM ({nearest_atm_strike}), using lowest: {actual_strike}")
                    else:  # PE
                        # For PE, find strikes above nearest ATM, then go further up
                        itm_strikes = [s for s in available_strikes if s > nearest_atm_strike]
                        if itm_strikes:
                            itm_strikes.sort()  # Sort ascending
                            actual_strike = itm_strikes[min(offset-1, len(itm_strikes)-1)]
                            logger.debug(f"ITM+{offset} PE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} above nearest ATM)")
                        else:
                            actual_strike = max(available_strikes)
                            logger.warning(f"ITM+{offset} PE: No strikes above nearest ATM ({nearest_atm_strike}), using highest: {actual_strike}")
            elif strike_price.upper().startswith('ITM-'):
                offset = int(strike_price.split('-')[1])
                atm_strike = get_atm_strike(symbol, exch)
                if atm_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    # Find the nearest available strike to ATM first
                    nearest_atm_strike = find_closest_strike(atm_strike, available_strikes)
                    logger.info(f"🎯 ITM-{offset} {option_type}: Underlying=₹{atm_strike}, Nearest ATM={nearest_atm_strike}")
                    logger.debug(f"Available strikes: {sorted(available_strikes)}")
                    
                    if option_type.upper() == 'CE':
                        # For CE, find strikes below nearest ATM, then go closer to ATM
                        itm_strikes = [s for s in available_strikes if s < nearest_atm_strike]
                        if itm_strikes:
                            itm_strikes.sort(reverse=True)  # Sort descending
                            actual_strike = itm_strikes[min(offset-1, len(itm_strikes)-1)]
                            logger.debug(f"ITM-{offset} CE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} below nearest ATM, closer)")
                        else:
                            actual_strike = min(available_strikes)
                            logger.warning(f"ITM-{offset} CE: No strikes below nearest ATM ({nearest_atm_strike}), using lowest: {actual_strike}")
                    else:  # PE
                        # For PE, find strikes above nearest ATM, then go closer to ATM
                        itm_strikes = [s for s in available_strikes if s > nearest_atm_strike]
                        if itm_strikes:
                            itm_strikes.sort()  # Sort ascending
                            actual_strike = itm_strikes[min(offset-1, len(itm_strikes)-1)]
                            logger.debug(f"ITM-{offset} PE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} above nearest ATM, closer)")
                        else:
                            actual_strike = max(available_strikes)
                            logger.warning(f"ITM-{offset} PE: No strikes above nearest ATM ({nearest_atm_strike}), using highest: {actual_strike}")
            elif strike_price.upper().startswith('OTM+'):
                offset = int(strike_price.split('+')[1])
                
                # Get the raw underlying price directly instead of using get_atm_strike
                idx_pair = strategy_config.get('idx_pair', 'NSE:NIFTY 50')
                underlying_symbol = idx_pair
                
                # If idx_pair doesn't contain exchange, add it
                if ':' not in underlying_symbol:
                    if exch.upper() == "MCX":
                        underlying_symbol = f"MCX:{symbol}"
                    else:
                        underlying_symbol = f"NSE:{symbol}"
                
                ticker = zebubot.get_ticker(underlying_symbol)
                if not ticker:
                    # Fallback to NSE if configured symbol fails
                    if exch.upper() == "MCX":
                        underlying_symbol = f"NSE:{symbol}"
                    else:
                        underlying_symbol = f"NSE:{symbol}"
                    ticker = zebubot.get_ticker(underlying_symbol)
                    if not ticker:
                        logger.error(f"Could not get underlying price for {symbol}, using first available strike")
                        actual_strike = available_strikes[0] if available_strikes else None
                    else:
                        underlying_price = ticker.get('price', 0)
                        if underlying_price <= 0:
                            logger.error(f"Invalid underlying price for {symbol}, using first available strike")
                            actual_strike = available_strikes[0] if available_strikes else None
                        else:
                            # Use the raw underlying price as reference
                            logger.debug(f"Available strikes: {sorted(available_strikes)}")
                            logger.info(f"🎯 OTM+{offset} {option_type}: Underlying=₹{underlying_price}, Using raw underlying price as reference")
                            
                            if option_type.upper() == 'CE':
                                # For CE, find strikes above underlying price, then go further up
                                otm_strikes = [s for s in available_strikes if s > underlying_price]
                                if otm_strikes:
                                    otm_strikes.sort()  # Sort ascending
                                    logger.info(f"🔍 OTM+{offset} CE: Strikes above {underlying_price}: {otm_strikes}")
                                    if len(otm_strikes) >= offset:
                                        # For OTM+, we want the Nth strike from underlying price
                                        actual_strike = otm_strikes[offset - 1]  # offset-1 because OTM+1 is 1st strike (index 0), OTM+2 is 2nd strike (index 1)
                                        logger.info(f"✅ OTM+{offset} CE: Selected {actual_strike} (strike #{offset} above underlying {underlying_price})")
                                    else:
                                        actual_strike = max(otm_strikes)  # Use the furthest strike available
                                        logger.warning(f"⚠️ OTM+{offset} CE: Not enough strikes above underlying ({underlying_price}), using furthest: {actual_strike}")
                                else:
                                    actual_strike = max(available_strikes)
                                    logger.warning(f"⚠️ OTM+{offset} CE: No strikes above underlying ({underlying_price}), using highest: {actual_strike}")
                            else:  # PE
                                # For PE, find strikes below underlying price, then go further down
                                otm_strikes = [s for s in available_strikes if s < underlying_price]
                                if otm_strikes:
                                    otm_strikes.sort(reverse=True)  # Sort descending (closest to underlying first)
                                    logger.info(f"🔍 OTM+{offset} PE: Strikes below {underlying_price}: {otm_strikes}")
                                    if len(otm_strikes) >= offset:
                                        # For OTM+, we want the Nth strike from underlying price
                                        actual_strike = otm_strikes[offset - 1]  # offset-1 because OTM+1 is 1st strike (index 0), OTM+2 is 2nd strike (index 1)
                                        logger.info(f"✅ OTM+{offset} PE: Selected {actual_strike} (strike #{offset} below underlying {underlying_price})")
                                    else:
                                        actual_strike = min(otm_strikes)  # Use the furthest strike available
                                        logger.warning(f"⚠️ OTM+{offset} PE: Not enough strikes below underlying ({underlying_price}), using furthest: {actual_strike}")
                                else:
                                    actual_strike = min(available_strikes)
                                    logger.warning(f"⚠️ OTM+{offset} PE: No strikes below underlying ({underlying_price}), using lowest: {actual_strike}")
                else:
                    underlying_price = ticker.get('price', 0)
                    if underlying_price <= 0:
                        logger.error(f"Invalid underlying price for {symbol}, using first available strike")
                        actual_strike = available_strikes[0] if available_strikes else None
                    else:
                        # Use the raw underlying price as reference
                        logger.debug(f"Available strikes: {sorted(available_strikes)}")
                        logger.info(f"🎯 OTM+{offset} {option_type}: Underlying=₹{underlying_price}, Using raw underlying price as reference")
                        
                        if option_type.upper() == 'CE':
                            # For CE, find strikes above underlying price, then go further up
                            otm_strikes = [s for s in available_strikes if s > underlying_price]
                            if otm_strikes:
                                otm_strikes.sort()  # Sort ascending
                                logger.info(f"🔍 OTM+{offset} CE: Strikes above {underlying_price}: {otm_strikes}")
                                if len(otm_strikes) >= offset:
                                    # For OTM+, we want the Nth strike from underlying price
                                    actual_strike = otm_strikes[offset - 1]  # offset-1 because list is 0-indexed
                                    logger.info(f"✅ OTM+{offset} CE: Selected {actual_strike} (strike #{offset} above underlying {underlying_price})")
                                else:
                                    actual_strike = max(otm_strikes)  # Use the furthest strike available
                                    logger.warning(f"⚠️ OTM+{offset} CE: Not enough strikes above underlying ({underlying_price}), using furthest: {actual_strike}")
                            else:
                                actual_strike = max(available_strikes)
                                logger.warning(f"⚠️ OTM+{offset} CE: No strikes above underlying ({underlying_price}), using highest: {actual_strike}")
                        else:  # PE
                            # For PE, find strikes below underlying price, then go further down
                            otm_strikes = [s for s in available_strikes if s < underlying_price]
                            if otm_strikes:
                                otm_strikes.sort(reverse=True)  # Sort descending (closest to underlying first)
                                logger.info(f"🔍 OTM+{offset} PE: Strikes below {underlying_price}: {otm_strikes}")
                                if len(otm_strikes) >= offset:
                                    # For OTM+, we want the Nth strike from underlying price
                                    actual_strike = otm_strikes[offset - 1]  # offset-1 because list is 0-indexed
                                    logger.info(f"✅ OTM+{offset} PE: Selected {actual_strike} (strike #{offset} below underlying {underlying_price})")
                                else:
                                    actual_strike = min(otm_strikes)  # Use the furthest strike available
                                    logger.warning(f"⚠️ OTM+{offset} PE: Not enough strikes below underlying ({underlying_price}), using furthest: {actual_strike}")
                            else:
                                actual_strike = min(available_strikes)
                                logger.warning(f"⚠️ OTM+{offset} PE: No strikes below underlying ({underlying_price}), using lowest: {actual_strike}")
            elif strike_price.upper().startswith('OTM-'):
                offset = int(strike_price.split('-')[1])
                atm_strike = get_atm_strike(symbol, exch)
                if atm_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    # Find the nearest available strike to ATM first
                    nearest_atm_strike = find_closest_strike(atm_strike, available_strikes)
                    logger.info(f"🎯 OTM-{offset} {option_type}: Underlying=₹{atm_strike}, Nearest ATM={nearest_atm_strike}")
                    logger.debug(f"Available strikes: {sorted(available_strikes)}")
                    
                    if option_type.upper() == 'CE':
                        # For CE, find strikes above nearest ATM, then go closer to ATM
                        otm_strikes = [s for s in available_strikes if s > nearest_atm_strike]
                        if otm_strikes:
                            otm_strikes.sort()  # Sort ascending
                            actual_strike = otm_strikes[min(offset-1, len(otm_strikes)-1)]
                            logger.debug(f"OTM-{offset} CE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} above nearest ATM, closer)")
                        else:
                            actual_strike = max(available_strikes)
                            logger.warning(f"OTM-{offset} CE: No strikes above nearest ATM ({nearest_atm_strike}), using highest: {actual_strike}")
                    else:  # PE
                        # For PE, find strikes below nearest ATM, then go closer to ATM
                        otm_strikes = [s for s in available_strikes if s < nearest_atm_strike]
                        if otm_strikes:
                            otm_strikes.sort(reverse=True)  # Sort descending
                            actual_strike = otm_strikes[min(offset-1, len(otm_strikes)-1)]
                            logger.debug(f"OTM-{offset} PE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} below nearest ATM, closer)")
                        else:
                            actual_strike = min(available_strikes)
                            logger.warning(f"OTM-{offset} PE: No strikes below nearest ATM ({nearest_atm_strike}), using lowest: {actual_strike}")
            elif strike_price.upper().startswith('ATM+'):
                offset = int(strike_price.split('+')[1])
                atm_strike = get_atm_strike(symbol, exch)
                if atm_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    # Find the nearest available strike to ATM first
                    nearest_atm_strike = find_closest_strike(atm_strike, available_strikes)
                    logger.info(f"🎯 ATM+{offset} {option_type}: Underlying=₹{atm_strike}, Nearest ATM={nearest_atm_strike}")
                    logger.debug(f"Available strikes: {sorted(available_strikes)}")
                    
                    if option_type.upper() == 'CE':
                        # For Call options: ATM+ means strikes below nearest ATM
                        strikes_below_atm = [s for s in available_strikes if s < nearest_atm_strike]
                        strikes_below_atm.sort(reverse=True)  # Sort descending (closest to ATM first)
                        if len(strikes_below_atm) >= offset:
                            actual_strike = strikes_below_atm[offset - 1]
                            logger.debug(f"ATM+{offset} CE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} below nearest ATM)")
                        else:
                            actual_strike = min(available_strikes)
                            logger.warning(f"ATM+{offset} CE: Not enough strikes below nearest ATM ({nearest_atm_strike}), using lowest: {actual_strike}")
                    else:  # PE
                        # For Put options: ATM+ means strikes above nearest ATM
                        strikes_above_atm = [s for s in available_strikes if s > nearest_atm_strike]
                        strikes_above_atm.sort()  # Sort ascending
                        if len(strikes_above_atm) >= offset:
                            actual_strike = strikes_above_atm[offset - 1]
                            logger.debug(f"ATM+{offset} PE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} above nearest ATM)")
                        else:
                            actual_strike = max(available_strikes)
                            logger.warning(f"ATM+{offset} PE: Not enough strikes above nearest ATM ({nearest_atm_strike}), using highest: {actual_strike}")
            elif strike_price.upper().startswith('ATM-'):
                offset = int(strike_price.split('-')[1])
                atm_strike = get_atm_strike(symbol, exch)
                if atm_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    # Find the nearest available strike to ATM first
                    nearest_atm_strike = find_closest_strike(atm_strike, available_strikes)
                    logger.info(f"🎯 ATM-{offset} {option_type}: Underlying=₹{atm_strike}, Nearest ATM={nearest_atm_strike}")
                    logger.debug(f"Available strikes: {sorted(available_strikes)}")
                    
                    if option_type.upper() == 'CE':
                        # For Call options: ATM- means strikes below nearest ATM
                        strikes_below_atm = [s for s in available_strikes if s < nearest_atm_strike]
                        strikes_below_atm.sort(reverse=True)  # Sort descending (closest to ATM first)
                        if len(strikes_below_atm) >= offset:
                            actual_strike = strikes_below_atm[offset - 1]
                            logger.debug(f"ATM-{offset} CE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} below nearest ATM)")
                        else:
                            actual_strike = min(available_strikes)
                            logger.warning(f"ATM-{offset} CE: Not enough strikes below nearest ATM ({nearest_atm_strike}), using lowest: {actual_strike}")
                    else:  # PE
                        # For Put options: ATM- means strikes above nearest ATM (puts are OTM when strike < spot)
                        strikes_above_atm = [s for s in available_strikes if s > nearest_atm_strike]
                        strikes_above_atm.sort()  # Sort ascending
                        if len(strikes_above_atm) >= offset:
                            actual_strike = strikes_above_atm[offset - 1]
                            logger.debug(f"ATM-{offset} PE: Nearest ATM={nearest_atm_strike}, selected {actual_strike} (strike #{offset} above nearest ATM)")
                        else:
                            actual_strike = max(available_strikes)
                            logger.warning(f"ATM-{offset} PE: Not enough strikes above nearest ATM ({nearest_atm_strike}), using highest: {actual_strike}")
            else:
                # Try to parse as number
                try:
                    target_strike = int(strike_price)
                    actual_strike = find_closest_strike(target_strike, available_strikes)
                except ValueError:
                    actual_strike = None
        else:
            if strike_price == 0:
                target_strike = get_atm_strike(symbol, exch)
                if target_strike is None:
                    logger.error(f"Could not get ATM strike for {symbol}, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
                else:
                    actual_strike = find_closest_strike(target_strike, available_strikes)
            else:
                target_strike = int(strike_price)
                actual_strike = find_closest_strike(target_strike, available_strikes)
        
        # Check if we need to select by premium price
        if 'price_premium' in leg_config:
            target_premium = leg_config['price_premium']
            logger.info(f"🎯 Selecting strike by LTP closest to premium: ₹{target_premium}")
            
            # Limit to reasonable number of strikes for performance (around ATM)
            atm_strike = get_atm_strike(symbol, exch)
            if atm_strike:
                # Focus on strikes around ATM (±3 strikes for faster execution)
                relevant_strikes = [s for s in available_strikes if abs(s - atm_strike) <= 150]
                if len(relevant_strikes) > 6:  # Limit to 6 strikes max for speed
                    relevant_strikes = sorted(relevant_strikes, key=lambda x: abs(x - atm_strike))[:6]
            else:
                # If no ATM, take first 6 strikes
                relevant_strikes = available_strikes[:6]
            
            logger.info(f"🔍 Checking LTP for {len(relevant_strikes)} strikes (around ATM) to find closest to ₹{target_premium}")
            
            # Prepare strike symbols for batch LTP retrieval
            strike_symbols = []
            for strike in relevant_strikes:
                strike_data = expiry_data[expiry_data['StrikePrice'] == str(strike)]
                if len(strike_data) > 0:
                    strike_symbols.append({
                        'exchange': exch,
                        'token': str(strike_data.iloc[0]['Token']).strip(),
                        'strike': strike,
                        'trading_symbol': str(strike_data.iloc[0]['TradingSymbol']).strip()
                    })
            
            # Get LTP for all strikes simultaneously using websocket
            if strike_symbols and zebubot and hasattr(zebubot, 'myntapi') and hasattr(zebubot.myntapi, 'get_multiple_strikes_ltp'):
                logger.info(f"🚀 Getting LTP for {len(strike_symbols)} strikes simultaneously...")
                ltp_data = zebubot.myntapi.get_multiple_strikes_ltp(strike_symbols)
                
                # Find the best strike based on premium difference
                best_strike = None
                best_premium_diff = float('inf')
                best_ltp = 0
                
                for strike in relevant_strikes:
                    if str(strike) in ltp_data:
                        ltp_info = ltp_data[str(strike)]
                        ltp_price = ltp_info.get('price', 0)
                        
                        if ltp_price > 0:
                            premium_diff = abs(ltp_price - target_premium)
                            logger.debug(f"Strike {strike}: LTP=₹{ltp_price}, Diff=₹{premium_diff:.2f}")
                            
                            if premium_diff < best_premium_diff:
                                best_premium_diff = premium_diff
                                best_strike = strike
                                best_ltp = ltp_price
                                
                                # Early exit if we find a very close match (within 10% of target)
                                if premium_diff <= target_premium * 0.10:
                                    logger.info(f"🎯 Found very close match! Strike {strike} with LTP ₹{ltp_price} (diff: ₹{premium_diff:.2f})")
                                    break
                
                if best_strike is not None:
                    actual_strike = best_strike
                    logger.info(f"✅ Selected strike {actual_strike} with LTP ₹{best_ltp} (closest to target ₹{target_premium}, diff: ₹{best_premium_diff:.2f})")
                    
                    # Set strike_data for the selected strike
                    strike_data = expiry_data[expiry_data['StrikePrice'] == str(actual_strike)].iloc[0]
                    logger.debug(f"Set strike_data for selected strike {actual_strike}")
                else:
                    logger.warning(f"⚠️ Could not get LTP for any strikes, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
            else:
                # Fallback to individual API calls if batch method not available
                logger.warning("⚠️ Batch LTP method not available, falling back to individual calls")
                best_strike = None
                best_premium_diff = float('inf')
                strike_premiums = {}
                
                for i, strike in enumerate(relevant_strikes):
                    if i % 5 == 0:  # Progress logging every 5 strikes
                        logger.info(f"📊 Progress: {i+1}/{len(relevant_strikes)} strikes checked...")
                    
                    # Find the trading symbol from master data for this strike
                    strike_data = expiry_data[expiry_data['StrikePrice'] == str(strike)]
                    if len(strike_data) == 0:
                        logger.debug(f"No master data found for strike {strike}")
                        continue
                    
                    trading_symbol = str(strike_data.iloc[0]['TradingSymbol']).strip()
                    
                    # Get LTP from websocket cache (much faster than API call)
                    try:
                        token = str(strike_data.iloc[0]['Token']).strip()
                        cached_ltp = get_cached_ltp(exch, token)
                        if cached_ltp and cached_ltp > 0:
                            premium_diff = abs(cached_ltp - target_premium)
                            strike_premiums[strike] = cached_ltp
                            logger.debug(f"Strike {strike} ({trading_symbol}): Cached LTP=₹{cached_ltp}, Diff=₹{premium_diff:.2f}")
                            
                            if premium_diff < best_premium_diff:
                                best_premium_diff = premium_diff
                                best_strike = strike
                                
                                # Early exit if we find a very close match (within 5% of target)
                                if premium_diff <= target_premium * 0.05:
                                    logger.info(f"🎯 Found very close match! Strike {strike} with LTP ₹{cached_ltp} (diff: ₹{premium_diff:.2f})")
                                    break
                        else:
                            # Fallback to websocket-based get_ticker if no cached data
                            logger.debug(f"No cached LTP for strike {strike}, trying websocket-based get_ticker...")
                            if zebubot and hasattr(zebubot, 'get_ticker'):
                                ticker_data = zebubot.get_ticker(f"{exch}:{trading_symbol}")
                                if ticker_data and ticker_data.get('price', 0) > 0:
                                    ltp = ticker_data['price']
                                    premium_diff = abs(ltp - target_premium)
                                    strike_premiums[strike] = ltp
                                    logger.debug(f"Strike {strike} ({trading_symbol}): Websocket LTP=₹{ltp}, Diff=₹{premium_diff:.2f}")
                                    
                                    if premium_diff < best_premium_diff:
                                        best_premium_diff = premium_diff
                                        best_strike = strike
                                        
                                        # Early exit if we find a very close match (within 5% of target)
                                        if premium_diff <= target_premium * 0.05:
                                            logger.info(f"🎯 Found very close match! Strike {strike} with LTP ₹{ltp} (diff: ₹{premium_diff:.2f})")
                                            break
                    except Exception as e:
                        logger.debug(f"Could not get LTP for strike {strike} ({trading_symbol}): {e}")
                        continue
                
                if best_strike is not None:
                    actual_strike = best_strike
                    best_ltp = strike_premiums[best_strike]
                    logger.info(f"✅ Selected strike {actual_strike} with LTP ₹{best_ltp} (closest to target ₹{target_premium}, diff: ₹{best_premium_diff:.2f})")
                    
                    # Set strike_data for the selected strike
                    strike_data = expiry_data[expiry_data['StrikePrice'] == str(actual_strike)].iloc[0]
                    logger.debug(f"Set strike_data for selected strike {actual_strike}")
                else:
                    logger.warning(f"⚠️ Could not get LTP for any strikes, using first available strike")
                    actual_strike = available_strikes[0] if available_strikes else None
        
        elif 'strike_premium' in leg_config:
            premium_price = leg_config['strike_premium']
            logger.info(f"Selecting strike by premium price: ₹{premium_price}")
            
            # Get current market price for the underlying
            underlying_symbol = f"NSE:{symbol}"
            ticker_data = zebubot.get_ticker(underlying_symbol) if zebubot else None
            current_price = ticker_data.get('price', 0) if ticker_data else 0
            
            if current_price > 0:
                # Calculate target strike based on premium
                if option_type.upper() == 'CE':
                    # For Call: strike = current_price - premium
                    target_strike = current_price - premium_price
                elif option_type.upper() == 'PE':
                    # For Put: strike = current_price + premium
                    target_strike = current_price + premium_price
                else:
                    # For Futures, use current price
                    target_strike = current_price
                
                logger.info(f"Calculated target strike from premium: {target_strike}")
                # Find closest available strike
                actual_strike = find_closest_strike(target_strike, available_strikes)
        
        if actual_strike is None:
            return None
        
        # Find exact strike price match in available strikes (skip if already found for futures)
        if strike_data is None:
            if actual_strike in available_strikes:
                strike_data = expiry_data[expiry_data['StrikePrice'] == str(actual_strike)].iloc[0]
                logger.debug(f"Found exact strike match: {actual_strike}")
            else:
                # This should not happen as we're using available_strikes, but just in case
                logger.warning(f"Strike {actual_strike} not found in available strikes, using closest")
                actual_strike = find_closest_strike(actual_strike, available_strikes)
                strike_data = expiry_data[expiry_data['StrikePrice'] == str(actual_strike)].iloc[0]
        
        # Get the final symbol info
        symbol_info = strike_data
        
        result = {
            'trading_symbol': str(symbol_info['TradingSymbol']).strip(),
            'token': str(symbol_info['Token']).strip(),
            'exchange': str(symbol_info['Exchange']).strip(),
            'lot_size': int(symbol_info['LotSize']),
            'strike_price': actual_strike,
            'expiry': actual_expiry_str,
            'option_type': option_type.upper()
        }
        
        # Cache the result to avoid repeated LTP calculations
        symbol_cache[cache_key] = result
        logger.debug(f"Cached symbol resolution for {cache_key}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error resolving symbol for leg {leg_config}: {e}")
        return None

def parse_time(time_str):
    """Parse time string in HH:MM:SS format."""
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        logger.error(f"Invalid time format: {time_str}. Use HH:MM:SS format.")
        return None

def is_market_time():
    """Check if current time is within market hours."""
    try:
        current_time = datetime.now().time()
        start_time = parse_time(strategy_config['start_time'])
        end_time = parse_time(strategy_config['end_time'])
        
        if not start_time or not end_time:
            return False
            
        return start_time <= current_time <= end_time
    except Exception as e:
        logger.error(f"Error checking market time: {e}")
        return False

def is_entry_time():
    """Check if it's time to enter position."""
    try:
        if position_entered or order_placed:
            return False
            
        current_time = datetime.now().time()
        start_time = parse_time(strategy_config['start_time'])
        
        if not start_time:
            return False
            
        # Add entry delay
        entry_time_with_delay = (datetime.combine(datetime.today(), start_time) + 
                               timedelta(seconds=strategy_config['entry_delay_seconds'])).time()
        
        return current_time >= entry_time_with_delay
    except Exception as e:
        logger.error(f"Error checking entry time: {e}")
        return False

def is_exit_time():
    """Check if it's time to exit position."""
    try:
        if not position_entered or position_exited:
            return False
            
        current_time = datetime.now().time()
        end_time = parse_time(strategy_config['end_time'])
        
        if not end_time:
            return False
            
        # Subtract exit delay
        exit_time_with_delay = (datetime.combine(datetime.today(), end_time) - timedelta(seconds=strategy_config['exit_delay_seconds'])).time()
        
        return current_time >= exit_time_with_delay
    except Exception as e:
        logger.error(f"Error checking exit time: {e}")
        return False

def is_square_off_time():
    """Check if it's time to square off all positions."""
    try:
        if not position_entered or position_exited:
            logger.debug(f"Square-off check: position_entered={position_entered}, position_exited={position_exited}")
            return False
            
        current_time = datetime.now().time()
        square_off_time = parse_time(strategy_config.get('square_off_time'))
        
        if not square_off_time:
            logger.debug("Square-off check: No square_off_time configured")
            return False
        
        is_square_off = current_time >= square_off_time
        logger.debug(f"Square-off check: current_time={current_time}, square_off_time={square_off_time}, is_square_off={is_square_off}")
        
        return is_square_off
    except Exception as e:
        logger.error(f"Error checking square off time: {e}")
        return False

def is_pnl_tracking_window():
    """Check if we're in the P&L tracking window (between start_time and end_time)."""
    try:
        current_time = datetime.now().time()
        start_time = parse_time(strategy_config.get('start_time'))
        end_time = parse_time(strategy_config.get('end_time'))
        
        if not start_time or not end_time:
            return False
            
        return start_time <= current_time <= end_time
    except Exception as e:
        logger.error(f"Error checking P&L tracking window: {e}")
        return False

def get_option_symbol():
    """Get the option symbol based on configuration."""
    try:
        base_symbol = strategy_config['option_symbol']
        option_type = strategy_config['option_type']
        strike_price = strategy_config['strike_price']
        
        # For now, return the base symbol
        # In a real implementation, you would construct the option symbol
        # based on strike price, expiry date, etc.
        return base_symbol
    except Exception as e:
        logger.error(f"Error getting option symbol: {e}")
        return strategy_config['option_symbol']

def place_leg_order(leg_id, leg_config, side='buy'):
    """Place order for a specific leg."""
    try:
        logger.info(f"🔍 place_leg_order called: leg_id={leg_id}, side={side}")
        print(f"🔍 place_leg_order called: leg_id={leg_id}, side={side}")
        
        if not zebubot or not zebubot.myntapi:
            print("❌ ZebuBot or MyntAPI not available")
            logger.error("ZebuBot or MyntAPI not available")
            return False
        
        print(f"🔍 MyntAPI available: {zebubot.myntapi is not None}")
        print(f"🔍 ZebuBot available: {zebubot is not None}")
        
        # Check if place_order method exists
        if hasattr(zebubot.myntapi, 'place_order'):
            print(f"🔍 place_order method exists: True")
            print(f"🔍 place_order method: {zebubot.myntapi.place_order}")
        else:
            print(f"❌ place_order method does not exist!")
            print(f"🔍 Available methods: {[method for method in dir(zebubot.myntapi) if not method.startswith('_')]}")
            
            # Try alternative method names
            alternative_methods = ['placeOrder', 'order', 'buy', 'sell', 'place_buy_order', 'place_sell_order']
            for method_name in alternative_methods:
                if hasattr(zebubot.myntapi, method_name):
                    print(f"🔍 Found alternative method: {method_name}")
                    break
            else:
                print(f"❌ No order placement methods found!")
                return False
        
        # Resolve symbol
        print(f"🔍 Resolving symbol for leg {leg_id}: {leg_config}")
        symbol_info = resolve_symbol(leg_config)
        if not symbol_info:
            print(f"❌ Could not resolve symbol for leg {leg_id}")
            logger.error(f"Could not resolve symbol for leg {leg_id}")
            return False
        
        print(f"✅ Symbol resolved for leg {leg_id}: {symbol_info}")
        
        trading_symbol = symbol_info['trading_symbol']
        master_lot_size = symbol_info['lot_size']  # Lot size from master data
        lot_count = leg_config.get('lot_size', 1)  # Number of lots from config
        order_type = leg_config.get('order_type', 'market')
        product_type = leg_config.get('product_type', 'I')
        
        # Calculate total quantity: lot_count * master_lot_size
        total_quantity = lot_count * master_lot_size
        
        # Create API symbol for order placement
        api_symbol = f"{symbol_info['exchange']}|{symbol_info['token']}"
        
        # Create Masters format symbol for MyntAPI symbol lookup
        masters_symbol = f"{symbol_info['exchange']}:{symbol_info['trading_symbol']}"
        
        # Get current price for limit orders
        current_price = None
        if order_type.lower() == 'limit':
            # For limit orders, use order_price if specified
            if 'order_price' in leg_config:
                current_price = leg_config['order_price']
            else:
                # Get current market price using Masters format
                ticker_data = zebubot.get_ticker(masters_symbol)
                if ticker_data:
                    current_price = ticker_data.get('price', 0)
                    if current_price <= 0:
                        logger.warning("Invalid price for limit order, using market order")
                        order_type = 'market'
        
        logger.info(f"🎯 Placing {order_type.upper()} {side.upper()} order for leg {leg_id}")
        logger.info(f"   Symbol: {trading_symbol}")
        logger.info(f"   Lot Count: {lot_count} | Master Lot Size: {master_lot_size} | Total Quantity: {total_quantity}")
        logger.info(f"   Price: {current_price or 'Market'}")
        
        # Place the order using ZebuBot
        print(f"🔍 Placing order with parameters:")
        print(f"   symbol (Masters): {masters_symbol}")
        print(f"   symbol (API): {api_symbol}")
        print(f"   side: {side}")
        print(f"   lot_count: {lot_count} | master_lot_size: {master_lot_size}")
        print(f"   total_quantity: {total_quantity}")
        print(f"   price: {current_price}")
        print(f"   order_type: {order_type}")
        print(f"   product_type: {product_type} (handled by ZebuBot)")
        
        try:
            order_result = zebubot.place_order(
                symbol=masters_symbol,  # Use Masters format for symbol lookup
                side=side,
                amount=total_quantity,
                price=current_price,
                order_type=order_type
            )
            print(f"🔍 Order result: {order_result}")
        except Exception as api_error:
            print(f"❌ API Error in place_order: {api_error}")
            print(f"   Error type: {type(api_error)}")
            print(f"   Error details: {str(api_error)}")
            logger.error(f"API Error in place_order: {api_error}")
            order_result = None
        
        # Check if order was successful
        if order_result and isinstance(order_result, dict):
            # Check for success indicators in the response
            if (order_result.get('stat') == 'Ok' or 
                order_result.get('status') == 'success' or 
                order_result.get('norenordno') or
                'order' in str(order_result).lower()):
                
                # Store order information
                leg_orders[leg_id] = {
                    'order_id': order_result.get('norenordno', ''),
                    'symbol': trading_symbol,
                    'quantity': total_quantity,
                    'price': current_price,
                    'side': side,
                    'timestamp': datetime.now(),
                    'status': 'placed'
                }
                
                print(f"✅ {side.upper()} order placed for leg {leg_id}!")
                print(f"   Symbol: {trading_symbol}")
                print(f"   Lot Count: {lot_count} | Master Lot Size: {master_lot_size}")
                print(f"   Total Quantity: {total_quantity}")
                print(f"   Price: {current_price or 'Market'}")
                print(f"   Order ID: {order_result.get('norenordno', 'N/A')}")
                
                logger.info(f"✅ {side.upper()} order placed for leg {leg_id}: {order_result}")
                return True
            else:
                print(f"❌ Order API returned error: {order_result}")
                logger.error(f"❌ Order API returned error: {order_result}")
                return False
        else:
            print(f"❌ Failed to place {side.upper()} order for leg {leg_id}")
            print(f"   API Symbol: {api_symbol}")
            print(f"   Trading Symbol: {trading_symbol}")
            print(f"   Lot Count: {lot_count} | Master Lot Size: {master_lot_size}")
            print(f"   Total Quantity: {total_quantity}")
            print(f"   Price: {current_price or 'Market'}")
            print(f"   Order Type: {order_type}")
            print(f"   Product Type: {product_type}")
            print(f"   Order Result: {order_result}")
            logger.error(f"❌ Failed to place {side.upper()} order for leg {leg_id}")
            logger.error(f"   API Symbol: {api_symbol}")
            logger.error(f"   Trading Symbol: {trading_symbol}")
            logger.error(f"   Lot Count: {lot_count} | Master Lot Size: {master_lot_size}")
            logger.error(f"   Total Quantity: {total_quantity}")
            logger.error(f"   Price: {current_price or 'Market'}")
            logger.error(f"   Order Type: {order_type}")
            logger.error(f"   Product Type: {product_type}")
            logger.error(f"   Order Result: {order_result}")
            return False
            
    except Exception as e:
        print(f"❌ Error placing {side} order for leg {leg_id}: {e}")
        print(f"   API Symbol: {api_symbol if 'api_symbol' in locals() else 'Not defined'}")
        print(f"   Trading Symbol: {trading_symbol if 'trading_symbol' in locals() else 'Not defined'}")
        print(f"   Leg Config: {leg_config}")
        print(f"   Symbol Info: {symbol_info if 'symbol_info' in locals() else 'Not defined'}")
        logger.error(f"Error placing {side} order for leg {leg_id}: {e}")
        logger.error(f"   API Symbol: {api_symbol if 'api_symbol' in locals() else 'Not defined'}")
        logger.error(f"   Trading Symbol: {trading_symbol if 'trading_symbol' in locals() else 'Not defined'}")
        logger.error(f"   Leg Config: {leg_config}")
        logger.error(f"   Symbol Info: {symbol_info if 'symbol_info' in locals() else 'Not defined'}")
        return False

def place_leg_order_ultra_fast(leg_id, side='buy'):
    """Place order for a specific leg using pre-calculated data (ultra-fast)."""
    try:
        # Use pre-calculated symbol info for instant access
        if leg_id not in pre_calculated_symbols:
            logger.error(f"No pre-calculated data for leg {leg_id}")
            return False
        
        pre_calc = pre_calculated_symbols[leg_id]
        symbol_info = pre_calc['symbol_info']
        leg_config = pre_calc['leg_config']
        
        # Use entry_time if specified, otherwise use start_time
        entry_time_str = leg_config.get('entry_time', strategy_config['start_time'])
        
        # Check if it's time for this leg
        leg_entry_time = parse_time(entry_time_str)
        current_time = datetime.now().time()
        
        if current_time >= leg_entry_time:
            if place_leg_order(leg_id, leg_config, side):
                # Mark this leg as placed
                leg_orders_placed[leg_id] = True
                return True
            else:
                logger.error(f"Failed to place entry order for leg {leg_id}")
                return False
        else:
            logger.info(f"Leg {leg_id} entry time not reached yet: {entry_time_str}")
            return False
    except Exception as e:
        logger.error(f"Error placing order for leg {leg_id}: {e}")
        return False

def place_leg_order_threaded(leg_id, leg_config, side='buy'):
    """Place order for a specific leg in a separate thread."""
    try:
        # Use entry_time if specified, otherwise use start_time
        entry_time_str = leg_config.get('entry_time', strategy_config['start_time'])
        
        # Check if it's time for this leg
        leg_entry_time = parse_time(entry_time_str)
        current_time = datetime.now().time()
        
        if current_time >= leg_entry_time:
            if place_leg_order(leg_id, leg_config, side):
                # Mark this leg as placed
                leg_orders_placed[leg_id] = True
                return True
            else:
                logger.error(f"Failed to place entry order for leg {leg_id}")
                return False
        else:
            logger.info(f"Leg {leg_id} entry time not reached yet: {entry_time_str}")
            return False
    except Exception as e:
        logger.error(f"Error placing order for leg {leg_id}: {e}")
        return False

def place_entry_orders():
    """Place entry orders for all legs using ultra-fast parallel processing."""
    global order_placed, entry_time, position_entered
    
    try:
        # Prevent duplicate order placement
        if order_placed or position_entered:
            logger.warning("Orders already placed or position already entered, skipping...")
            return False
            
        if not strategy_config.get('legs'):
            logger.error("No legs configured")
            return False
        
        logger.info("🚀 Placing entry orders for all legs (ULTRA-FAST parallel processing)...")
        print("🚀 Placing entry orders for all legs (ULTRA-FAST parallel processing)...")
        
        total_legs = len(strategy_config['legs'])
        
        # Use pre-calculated symbols for ultra-fast processing
        if pre_calculated_symbols:
            logger.info("⚡ Using pre-calculated symbols for instant order placement...")
            print("⚡ Using pre-calculated symbols for instant order placement...")
            
            # Create threads for parallel order placement using pre-calculated data
            threads = []
            results = {}
            
            for leg_id in pre_calculated_symbols.keys():
                thread = threading.Thread(
                    target=lambda lid=leg_id: results.update({lid: place_leg_order_ultra_fast(lid, 'buy')}),
                    name=f"UltraFastOrder-{leg_id}"
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Count successful orders
            successful_orders = sum(1 for success in results.values() if success)
            
            if successful_orders > 0:
                order_placed = True
                entry_time = datetime.now()
                position_entered = True
                
                print(f"✅ ULTRA-FAST Entry orders placed: {successful_orders}/{total_legs} successful")
                logger.info(f"✅ ULTRA-FAST Entry orders placed: {successful_orders}/{total_legs} successful")
                return True
            else:
                print(f"❌ No entry orders placed successfully")
                logger.error("❌ No entry orders placed successfully")
                return False
        else:
            # Fallback to regular parallel processing
            logger.info("⚠️ No pre-calculated symbols, using regular parallel processing...")
            print("⚠️ No pre-calculated symbols, using regular parallel processing...")
            
            # Create threads for parallel order placement
            threads = []
            results = {}
            
            for leg_id, leg_config in strategy_config['legs'].items():
                thread = threading.Thread(
                    target=lambda lid=leg_id, lc=leg_config: results.update({lid: place_leg_order_threaded(lid, lc, 'buy')}),
                    name=f"OrderThread-{leg_id}"
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Count successful orders
            successful_orders = sum(1 for success in results.values() if success)
            
            if successful_orders > 0:
                order_placed = True
                entry_time = datetime.now()
                position_entered = True
                
                print(f"✅ Entry orders placed: {successful_orders}/{total_legs} successful")
                logger.info(f"✅ Entry orders placed: {successful_orders}/{total_legs} successful")
                return True
            else:
                print(f"❌ No entry orders placed successfully")
                logger.error("❌ No entry orders placed successfully")
                return False
            
    except Exception as e:
        logger.error(f"Error placing entry orders: {e}")
        return False

def place_exit_orders():
    """Place exit orders for all legs."""
    global position_exited
    
    try:
        if not strategy_config.get('legs'):
            logger.error("No legs configured")
            return False
        
        logger.info("🎯 Placing exit orders for all legs...")
        print("🎯 Placing exit orders for all legs...")
        
        successful_orders = 0
        total_legs = len(strategy_config['legs'])
        
        for leg_id, leg_config in strategy_config['legs'].items():
            # Check if this leg has exit time
            exit_time_str = leg_config.get('exit_time')
            if not exit_time_str:
                continue
            
            # Check if it's time for this leg
            leg_exit_time = parse_time(exit_time_str)
            current_time = datetime.now().time()
            
            if current_time >= leg_exit_time:
                if place_leg_order(leg_id, leg_config, 'sell'):
                    successful_orders += 1
                else:
                    logger.error(f"Failed to place exit order for leg {leg_id}")
            else:
                logger.info(f"Leg {leg_id} exit time not reached yet: {exit_time_str}")
        
        if successful_orders > 0:
            position_exited = True
            
            print(f"✅ Exit orders placed: {successful_orders}/{total_legs} successful")
            logger.info(f"✅ Exit orders placed: {successful_orders}/{total_legs} successful")
            return True
        else:
            print(f"❌ No exit orders placed successfully")
            logger.error("❌ No exit orders placed successfully")
            return False
            
    except Exception as e:
        logger.error(f"Error placing exit orders: {e}")
        return False

def place_square_off_orders():
    """Place square-off orders for all legs (force exit regardless of leg exit times)."""
    global position_exited
    
    try:
        if not strategy_config.get('legs'):
            logger.error("No legs configured for square-off")
            return False
        
        logger.info("🔴 Placing SQUARE-OFF orders for all legs...")
        print("🔴 Placing SQUARE-OFF orders for all legs...")
        
        successful_orders = 0
        total_legs = len(strategy_config['legs'])
        
        for leg_id, leg_config in strategy_config['legs'].items():
            logger.info(f"🔴 Square-off: Placing SELL order for leg {leg_id}")
            print(f"🔴 Square-off: Placing SELL order for leg {leg_id}")
            
            if place_leg_order(leg_id, leg_config, 'sell'):
                successful_orders += 1
                logger.info(f"✅ Square-off order placed for leg {leg_id}")
                print(f"✅ Square-off order placed for leg {leg_id}")
            else:
                logger.error(f"❌ Failed to place square-off order for leg {leg_id}")
                print(f"❌ Failed to place square-off order for leg {leg_id}")
        
        if successful_orders > 0:
            position_exited = True
            
            print(f"✅ Square-off orders placed: {successful_orders}/{total_legs} successful")
            logger.info(f"✅ Square-off orders placed: {successful_orders}/{total_legs} successful")
            return True
        else:
            print(f"❌ No square-off orders placed successfully")
            logger.error("❌ No square-off orders placed successfully")
            return False
            
    except Exception as e:
        logger.error(f"Error placing square-off orders: {e}")
        return False

def calculate_leg_pnl(leg_id, leg_config):
    """Calculate P&L for a specific leg."""
    try:
        if leg_id not in leg_orders:
            return 0
        
        order_info = leg_orders[leg_id]
        if order_info['side'] != 'buy':
            return 0
        
        # Get current price using direct API call
        symbol_info = resolve_symbol(leg_config)
        if not symbol_info:
            return 0
        
        # Use direct API call to get option price
        try:
            exchange = symbol_info['exchange']
            token = symbol_info['token']
            quotes = zebubot.myntapi.api.get_quotes(exchange=exchange, token=token)
            if not quotes or quotes.get('stat') != 'Ok':
                return 0
            current_price = float(quotes.get('lp', 0))
        except Exception as e:
            logger.debug(f"Failed to get price for {symbol_info['trading_symbol']}: {e}")
            return 0
        
        entry_price = order_info.get('price', 0)
        quantity = order_info.get('quantity', 0)
        
        # Handle None values
        if current_price is None:
            current_price = 0
        if entry_price is None:
            entry_price = 0
        if quantity is None:
            quantity = 0
        
        if entry_price <= 0 or current_price <= 0:
            return 0
        
        # Calculate P&L (current_price - entry_price) * quantity
        pnl = (current_price - entry_price) * quantity
        leg_pnl[leg_id] = pnl
        
        return pnl
        
    except Exception as e:
        logger.error(f"Error calculating P&L for leg {leg_id}: {e}")
        return 0

def calculate_overall_pnl():
    """Calculate overall P&L for all legs."""
    global overall_pnl, last_pnl_calculation
    
    try:
        # Throttle P&L calculations to every 5 seconds
        current_time = time.time()
        if current_time - last_pnl_calculation < 5:
            return overall_pnl
        
        last_pnl_calculation = current_time
        overall_pnl = 0
        
        for leg_id, leg_config in strategy_config.get('legs', {}).items():
            leg_pnl_value = calculate_leg_pnl(leg_id, leg_config)
            overall_pnl += leg_pnl_value
        
        return overall_pnl
        
    except Exception as e:
        logger.error(f"Error calculating overall P&L: {e}")
        return 0

def check_leg_target_stop_loss(leg_id, leg_config):
    """Check if leg has hit target or stop loss."""
    try:
        leg_pnl_value = leg_pnl.get(leg_id, 0)
        leg_target = leg_config.get('target', 0)
        leg_stop_loss = leg_config.get('stop_loss', 0)
        
        if leg_target > 0 and leg_pnl_value >= leg_target:
            logger.info(f"🎯 Leg {leg_id} TARGET HIT! P&L: ₹{leg_pnl_value:.2f} (Target: ₹{leg_target})")
            print(f"🎯 Leg {leg_id} TARGET HIT! P&L: ₹{leg_pnl_value:.2f} (Target: ₹{leg_target})")
            return 'target'
        
        if leg_stop_loss > 0 and leg_pnl_value <= -leg_stop_loss:
            logger.info(f"🛑 Leg {leg_id} STOP LOSS HIT! P&L: ₹{leg_pnl_value:.2f} (Stop Loss: ₹{leg_stop_loss})")
            print(f"🛑 Leg {leg_id} STOP LOSS HIT! P&L: ₹{leg_pnl_value:.2f} (Stop Loss: ₹{leg_stop_loss})")
            return 'stop_loss'
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking target/stop loss for leg {leg_id}: {e}")
        return None

def check_overall_target_stop_loss():
    """Check if overall target or stop loss is hit."""
    try:
        overall_pnl_value = calculate_overall_pnl()
        overall_target = strategy_config.get('overall_target', 0)
        overall_stop_loss = strategy_config.get('overall_stop_loss', 0)
        
        if overall_target > 0 and overall_pnl_value >= overall_target:
            logger.info(f"🎯 OVERALL TARGET HIT! P&L: ₹{overall_pnl_value:.2f} (Target: ₹{overall_target})")
            print(f"🎯 OVERALL TARGET HIT! P&L: ₹{overall_pnl_value:.2f} (Target: ₹{overall_target})")
            return 'target'
        
        if overall_stop_loss > 0 and overall_pnl_value <= -overall_stop_loss:
            logger.info(f"🛑 OVERALL STOP LOSS HIT! P&L: ₹{overall_pnl_value:.2f} (Stop Loss: ₹{overall_stop_loss})")
            print(f"🛑 OVERALL STOP LOSS HIT! P&L: ₹{overall_pnl_value:.2f} (Stop Loss: ₹{overall_stop_loss})")
            return 'stop_loss'
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking overall target/stop loss: {e}")
        return None

def check_positions():
    """Check current positions to verify entry/exit status."""
    try:
        if not zebubot or not zebubot.myntapi:
            return False
        
        positions = zebubot.myntapi.get_positions()
        if not positions:
            return False
        
        # Check if any leg has positions
        for leg_id, leg_config in strategy_config.get('legs', {}).items():
            symbol_info = resolve_symbol(leg_config)
            if not symbol_info:
                continue
            
            trading_symbol = symbol_info['trading_symbol']
            
            for position in positions:
                if position.get('tsym') == trading_symbol:
                    net_qty = float(position.get('netqty', 0))
                    if net_qty > 0:
                        return True  # Position exists
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking positions: {e}")
        return False

def on_tick(symbol, ticker_data):
    """Called on every tick/price update."""
    global tick_count, strategy_active, position_entered, position_exited, order_placed, session_id, square_off_attempted, leg_orders_placed
    
    tick_count += 1
    
    # Update websocket LTP cache for option symbols
    update_websocket_ltp_cache(symbol, ticker_data)
    
    # Ensure master data is loaded before any trading logic
    if not master_data_loaded:
        load_master_data()
        if not master_data_loaded:
            return  # Skip this tick if master data couldn't be loaded
    
    # Process ticker data
    current_price = ticker_data.get('price', 0)
    current_volume = ticker_data.get('volume', 0)
    current_time = datetime.now()
    
    # Add current price to history
    price_history.append(current_price)
    
    # Console update with timestamp and status
    timestamp = current_time.strftime("%H:%M:%S")
    status = "WAITING"
    
    if position_entered and not position_exited:
        if is_pnl_tracking_window():
            status = "TRACKING"  # In P&L tracking window
        else:
            status = "POSITION"  # Holding position but not tracking P&L
    elif position_exited:
        status = "EXITED"
    elif order_placed:
        status = "ORDERED"
    
    print(f"\n[{timestamp}] 📊 {symbol} | ₹{current_price:.2f} | Vol: {current_volume:,.0f} | Status: {status} | Tick: {tick_count}")
    
    # Check if it's market time
    if not is_market_time():
        if tick_count % 10 == 0:  # Log every 10 ticks when market is closed
            print(f"   ⏰ Market closed - Waiting for {strategy_config['start_time']}")
            logger.info(f"⏰ Market closed - Waiting for {strategy_config['start_time']}")
        return
    
    # Check for entry time
    if is_entry_time() and not order_placed and not position_entered:
        # Generate session ID for this trading session
        current_session = f"{current_time.strftime('%Y%m%d')}_{strategy_config['start_time']}"
        
        # Check if we've already placed orders in this session
        if session_id == current_session:
            logger.debug(f"Orders already placed in session {current_session}, skipping...")
            return
        
        print(f"   🎯 Entry time reached! Subscribing to option symbols...")
        logger.info("🎯 Entry time reached! Subscribing to option symbols...")
        
        # Set session ID immediately to prevent duplicate attempts
        session_id = current_session
        
        # Subscribe to all option symbols for real-time LTP data
        if subscribe_to_option_symbols():
            print(f"   📡 Option symbols subscribed! Waiting for LTP data...")
            logger.info("📡 Option symbols subscribed! Waiting for LTP data...")
            
            # Wait a moment for websocket data to populate
            import time
            time.sleep(0.05)  # Give websocket time to populate LTP data (reduced from 0.2s to 0.05s)
            
            print(f"   🎯 Placing entry orders with cached LTP data...")
            logger.info("🎯 Placing entry orders with cached LTP data...")
            
            if place_entry_orders():
                print(f"   ✅ Entry orders placed successfully!")
                logger.info("✅ Entry orders placed successfully!")
                # Set order_placed only after successful order placement
                order_placed = True
            else:
                print(f"   ❌ Failed to place entry orders")
                logger.error("❌ Failed to place entry orders")
        else:
            print(f"   ❌ Failed to subscribe to option symbols")
            logger.error("❌ Failed to subscribe to option symbols")
    
    # Check for individual leg entry times (for legs with specific entry times)
    # This should run even if some orders are already placed
    if not position_exited:
        # Check if any leg has a specific entry time that has been reached
        current_time_obj = datetime.now().time()
        for leg_id, leg_config in strategy_config.get('legs', {}).items():
            entry_time_str = leg_config.get('entry_time')
            if entry_time_str:
                leg_entry_time = parse_time(entry_time_str)
                if current_time_obj >= leg_entry_time:
                    # Check if this specific leg has already been placed
                    leg_already_placed = leg_orders_placed.get(leg_id, False)
                    
                    if not leg_already_placed:
                        # Generate session ID for this specific leg entry time
                        leg_session_id = f"{current_time.strftime('%Y%m%d')}_{entry_time_str}_{leg_id}"
                        
                        # Check if we've already attempted to place this leg in this session
                        if session_id != leg_session_id:
                            print(f"   🎯 Leg {leg_id} entry time reached! Placing order for leg {leg_id}...")
                            logger.info(f"🎯 Leg {leg_id} entry time reached! Placing order for leg {leg_id}...")
                            
                            # Set session ID to prevent duplicate attempts
                            session_id = leg_session_id
                            
                            # Place order for this specific leg
                            if place_leg_order(leg_id, leg_config, 'buy'):
                                print(f"   ✅ Leg {leg_id} order placed successfully!")
                                logger.info(f"✅ Leg {leg_id} order placed successfully!")
                                
                                # Mark this leg as placed
                                leg_orders_placed[leg_id] = True
                                
                                # Update position status
                                if not position_entered:
                                    position_entered = True
                                    entry_time = datetime.now()
                            else:
                                print(f"   ❌ Failed to place order for leg {leg_id}")
                                logger.error(f"❌ Failed to place order for leg {leg_id}")
                        else:
                            logger.debug(f"Leg {leg_id} already attempted in this session, skipping...")
                    else:
                        logger.debug(f"Leg {leg_id} already placed, skipping...")
                    break  # Only place one leg per tick
    
    # Check for individual leg exit times (for legs with specific exit times)
    if position_entered and not position_exited:
        current_time_obj = datetime.now().time()
        for leg_id, leg_config in strategy_config.get('legs', {}).items():
            exit_time_str = leg_config.get('exit_time')
            if exit_time_str:
                leg_exit_time = parse_time(exit_time_str)
                if current_time_obj >= leg_exit_time:
                    # Check if this specific leg has already been exited
                    leg_already_exited = leg_orders_placed.get(f"{leg_id}_exited", False)
                    
                    if not leg_already_exited:
                        print(f"   🎯 Leg {leg_id} exit time reached! Exiting leg {leg_id}...")
                        logger.info(f"🎯 Leg {leg_id} exit time reached! Exiting leg {leg_id}...")
                        
                        # Place exit order for this specific leg
                        if place_leg_order(leg_id, leg_config, 'sell'):
                            print(f"   ✅ Leg {leg_id} exit order placed successfully!")
                            logger.info(f"✅ Leg {leg_id} exit order placed successfully!")
                            
                            # Mark this leg as exited
                            leg_orders_placed[f"{leg_id}_exited"] = True
                        else:
                            print(f"   ❌ Failed to place exit order for leg {leg_id}")
                            logger.error(f"❌ Failed to place exit order for leg {leg_id}")
                    else:
                        logger.debug(f"Leg {leg_id} already exited, skipping...")
                    break  # Only exit one leg per tick
    
    # Check for square off time (priority over regular exit time)
    elif is_square_off_time() and position_entered and not position_exited and not square_off_attempted:
        print(f"   🔴 SQUARE OFF TIME reached! Exiting all positions...")
        logger.info("🔴 SQUARE OFF TIME reached! Exiting all positions...")
        
        # Mark square-off as attempted to prevent multiple attempts
        square_off_attempted = True
        
        if place_square_off_orders():
            print(f"   ✅ Square off orders placed successfully!")
            logger.info("✅ Square off orders placed successfully!")
        else:
            print(f"   ❌ Failed to place square off orders")
            logger.error("❌ Failed to place square off orders")
    
    # Debug: Log when square-off is skipped
    elif is_square_off_time() and position_entered and not position_exited and square_off_attempted:
        logger.debug(f"Square-off skipped: already attempted (position_entered={position_entered}, position_exited={position_exited}, square_off_attempted={square_off_attempted})")
    
    # Check for regular exit time
    elif is_exit_time() and position_entered and not position_exited:
        print(f"   🎯 Exit time reached! Placing exit orders...")
        logger.info("🎯 Exit time reached! Placing exit orders...")
        
        if place_exit_orders():
            print(f"   ✅ Exit orders placed successfully!")
            logger.info("✅ Exit orders placed successfully!")
        else:
            print(f"   ❌ Failed to place exit orders")
            logger.error("❌ Failed to place exit orders")
    
    # Check target/stop loss if positions are active AND in P&L tracking window AND square-off not attempted
    if position_entered and not position_exited and is_pnl_tracking_window() and not square_off_attempted:
        # Check overall target/stop loss first
        overall_result = check_overall_target_stop_loss()
        if overall_result:
            print(f"   🎯 Overall {overall_result.upper()} triggered! Exiting all positions...")
            logger.info(f"Overall {overall_result.upper()} triggered! Exiting all positions...")
            if place_exit_orders():
                position_exited = True
                return
        
        # Check individual leg target/stop loss
        for leg_id, leg_config in strategy_config.get('legs', {}).items():
            leg_result = check_leg_target_stop_loss(leg_id, leg_config)
            if leg_result:
                print(f"   🎯 Leg {leg_id} {leg_result.upper()} triggered! Exiting leg...")
                logger.info(f"Leg {leg_id} {leg_result.upper()} triggered! Exiting leg...")
                # Exit only this specific leg
                if place_leg_order(leg_id, leg_config, 'sell'):
                    print(f"   ✅ Leg {leg_id} exit order placed")
                    logger.info(f"Leg {leg_id} exit order placed")
        
        # Calculate and display P&L
        overall_pnl_value = calculate_overall_pnl()
        print(f"   💰 Overall P&L: ₹{overall_pnl_value:.2f}")
    
    # Skip P&L checks if square-off has been attempted
    elif square_off_attempted and position_entered and not position_exited:
        logger.debug("P&L checks skipped: Square-off already attempted")
        
        if entry_time:
            duration = current_time - entry_time
            print(f"   📈 Position held for: {duration}")
            logger.info(f"📈 Position held for: {duration}")
    
    # Log strategy configuration every 50 ticks
    if tick_count % 50 == 0:
        print(f"   ⚙️ Strategy Config: {strategy_config['start_time']} - {strategy_config['end_time']}")
        print(f"   📊 Legs: {len(strategy_config.get('legs', {}))}")
        print(f"   💰 Overall Target: ₹{strategy_config.get('overall_target', 0)}")
        print(f"   🛡️ Overall Stop Loss: ₹{strategy_config.get('overall_stop_loss', 0)}")
        logger.info(f"⚙️ Strategy Config: {strategy_config['start_time']} - {strategy_config['end_time']}")
        logger.info(f"📊 Legs: {len(strategy_config.get('legs', {}))}")
        logger.info(f"💰 Overall Target: ₹{strategy_config.get('overall_target', 0)}")
        logger.info(f"🛡️ Overall Stop Loss: ₹{strategy_config.get('overall_stop_loss', 0)}")

def get_strategy_status():
    """Get current strategy status."""
    current_time = datetime.now().time()
    start_time = parse_time(strategy_config['start_time'])
    end_time = parse_time(strategy_config['end_time'])
    
    # Calculate current P&L
    overall_pnl_value = calculate_overall_pnl()
    
    status = {
        'current_time': current_time.strftime('%H:%M:%S'),
        'start_time': strategy_config['start_time'],
        'end_time': strategy_config['end_time'],
        'square_off_time': strategy_config.get('square_off_time', '15:10:00'),
        'market_time': is_market_time(),
        'entry_time': is_entry_time(),
        'exit_time': is_exit_time(),
        'position_entered': position_entered,
        'position_exited': position_exited,
        'order_placed': order_placed,
        'overall_pnl': overall_pnl_value,
        'overall_target': strategy_config.get('overall_target', 0),
        'overall_stop_loss': strategy_config.get('overall_stop_loss', 0),
        'legs_count': len(strategy_config.get('legs', {})),
        'leg_pnl': dict(leg_pnl),
        'tick_count': tick_count
    }
    
    return status


def main():
    """Main function called on every tick."""
    # Load configuration and master data on first tick
    if tick_count == 1:
        # print(f"🔍 Checking for YAML config...")
        # print(f"   Available globals: {[k for k in globals().keys() if not k.startswith('_')]}")
        # print(f"   'strategy' in globals: {'strategy' in globals()}")
        # if 'strategy' in globals():
        #     print(f"   strategy type: {type(globals()['strategy'])}")
        #     print(f"   strategy value: {globals()['strategy']}")
        
        load_strategy_config()
        if not master_data_loaded:
            load_master_data()
    
    on_tick(current_symbol, ticker_data)
    
    # Log strategy status every 100 ticks
    if tick_count % 100 == 0:
        status = get_strategy_status()
        print(f"\n{'='*60}")
        print(f"📊 OPTION STRATEGY STATUS")
        print(f"{'='*60}")
        for key, value in status.items():
            print(f"   {key}: {value}")
        print(f"{'='*60}")
        logger.info("📊 Option Strategy Status:")
        for key, value in status.items():
            logger.info(f"   {key}: {value}")

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print(f"🎯 MULTI-LEG OPTION TRADING STRATEGY - ENHANCED")
    print(f"{'='*70}")
    print(f"📊 Index Pair: {strategy_config.get('idx_pair', 'NSE:NIFTY 50')}")
    print(f"⏰ Start Time: {strategy_config['start_time']}")
    print(f"⏰ End Time: {strategy_config['end_time']}")
    print(f"⏰ Square Off: {strategy_config.get('square_off_time', '15:10:00')}")
    print(f"💰 Overall Target: ₹{strategy_config.get('overall_target', 1000)}")
    print(f"🛡️ Overall Stop Loss: ₹{strategy_config.get('overall_stop_loss', 1000)}")
    print(f"📊 Legs: {len(strategy_config.get('legs', {}))}")
    print(f"🎯 Features: Target/Stop Loss, Master Data, Symbol Resolution")
    print(f"🚫 Margin Check: DISABLED (as requested)")
    print(f"🇮🇳 Trading via MyntAPI (Noren)")
    print(f"📈 Master Data: NFO, BFO & MCX symbols loaded")
    print(f"{'='*70}")
    
    logger.info("🎯 Multi-Leg Option Trading Strategy Started - Enhanced")
    logger.info(f"📊 Index Pair: {strategy_config.get('idx_pair', 'NSE:NIFTY 50')}")
    logger.info(f"⏰ Start Time: {strategy_config['start_time']}")
    logger.info(f"⏰ End Time: {strategy_config['end_time']}")
    logger.info(f"⏰ Square Off: {strategy_config.get('square_off_time', '15:10:00')}")
    logger.info(f"💰 Overall Target: ₹{strategy_config.get('overall_target', 1000)}")
    logger.info(f"🛡️ Overall Stop Loss: ₹{strategy_config.get('overall_stop_loss', 1000)}")
    logger.info(f"📊 Legs: {len(strategy_config.get('legs', {}))}")
    logger.info("🎯 Features: Target/Stop Loss, Master Data, Symbol Resolution")
    logger.info("🚫 Margin Check: DISABLED (as requested)")
    logger.info("🇮🇳 Trading via MyntAPI (Noren)")
    logger.info("📈 Master Data: NFO, BFO & MCX symbols loaded")
    
    main()
