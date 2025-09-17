"""
MyntAPI (Noren) integration for ZebuBot.
"""

import logging
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

# Import the Noren API
import sys
sys.path.append(str(Path(__file__).parent.parent))
from .noren import NorenApi, ProductType, PriceType, BuyorSell, FeedType

from .symbol_manager import SymbolManager


class MyntAPIIntegration:
    """MyntAPI (Noren) integration for ZebuBot."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize MyntAPI integration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api = None
        self.connected = False
        self.websocket_connected = False
        self.subscribers = {}
        self.callbacks = {}
        self.symbol_manager = SymbolManager()
        self.previous_data = {}  # Store previous values for each symbol
        
    def initialize(self) -> bool:
        """Initialize MyntAPI connection."""
        try:
            # Get MyntAPI configuration
            mynt_config = self.config.get('myntapi', {})
            if not mynt_config.get('enabled', False):
                self.logger.warning("MyntAPI not enabled in configuration")
                return False
            
            # Initialize Noren API
            host = mynt_config.get('host', 'https://go.mynt.in/NorenWClientTP/')
            websocket = mynt_config.get('websocket', 'wss://go.mynt.in/NorenWSTP/')
            
            self.api = NorenApi(host, websocket)
            
            # Login
            login_result = self.api.login(
                userid=mynt_config.get('userid'),
                password=mynt_config.get('password'),
                twoFA=mynt_config.get('twoFA'),
                vendor_code=mynt_config.get('vendor_code'),
                api_secret=mynt_config.get('api_secret'),
                imei=mynt_config.get('imei')
            )
            
            if login_result and login_result.get('stat') == 'Ok':
                self.connected = True
                self.logger.info("MyntAPI connected successfully")
                
                # Load symbols from Masters endpoint
                if self.symbol_manager.load_symbols():
                    self.logger.info("Symbols loaded from Masters endpoint")
                else:
                    self.logger.warning("Failed to load symbols from Masters endpoint")
                
                return True
            else:
                self.logger.error(f"MyntAPI login failed: {login_result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize MyntAPI: {e}")
            return False
    
    def _convert_symbol_format(self, symbol: str) -> Optional[str]:
        """Convert symbol format from NSE:SYMBOL-EQ to NSE|TOKEN."""
        try:
            # If already in API format (NSE|TOKEN), return as is
            if '|' in symbol and not ':' in symbol:
                return symbol
            
            # If in Masters format (NSE:SYMBOL-EQ), convert to API format
            if ':' in symbol:
                symbol_info = self.symbol_manager.get_symbol_info(symbol)
                if symbol_info:
                    api_symbol = symbol_info.get('api_symbol')
                    return api_symbol
            
            # Try to search for the symbol
            if ':' in symbol:
                exchange = symbol.split(':')[0]
                search_text = symbol.split(':')[1].replace('-EQ', '').replace('-SM', '').replace('-BE', '')
            else:
                exchange = 'NSE'
                search_text = symbol
            
            search_results = self.symbol_manager.search_symbols(search_text, exchange)
            if search_results:
                api_symbol = search_results[0].get('api_symbol')
                return api_symbol
            
            self.logger.error(f"❌ Failed to convert symbol format: {symbol}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Exception in _convert_symbol_format: {e}")
            return None
    
    def get_market_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[List[List]]:
        """Get OHLCV market data for a symbol."""
        try:
            if not self.connected:
                return None
            
            # Convert symbol format if needed
            api_symbol = self._convert_symbol_format(symbol)
            if not api_symbol:
                return None
            
            # Parse symbol (format: EXCHANGE|TOKEN)
            exchange, token = api_symbol.split('|')
            
            # Get time series data
            end_time = int(time.time())
            start_time = end_time - (limit * 3600)  # Approximate for 1h timeframe
            
            data = self.api.get_time_price_series(
                exchange=exchange,
                token=token,
                starttime=start_time,
                endtime=end_time,
                interval=60  # 1 hour in minutes
            )
            
            if not data:
                return None
            
            # Convert to OHLCV format
            ohlcv = []
            for item in data:
                if item.get('stat') == 'Ok':
                    ohlcv.append([
                        int(time.mktime(time.strptime(item['time'], '%d-%m-%Y %H:%M:%S')) * 1000),  # timestamp
                        float(item.get('into', 0)),  # open
                        float(item.get('inth', 0)),  # high
                        float(item.get('intl', 0)),  # low
                        float(item.get('intc', 0)),  # close
                        float(item.get('intv', 0))   # volume
                    ])
            
            return ohlcv
            
        except Exception as e:
            self.logger.error(f"Failed to get market data for {symbol}: {e}")
            return None
    
    def get_tpseries(self, symbol: str, start_time: int, end_time: int, 
                     interval: int = 1) -> Optional[List[Dict[str, Any]]]:
        """Get time price series (chart data) for a symbol.
        
        Args:
            symbol: Symbol in format NSE:SYMBOL-EQ or NSE|TOKEN
            start_time: Start time as Unix timestamp
            end_time: End time as Unix timestamp
            interval: Time interval in minutes (1, 3, 5, 15, 30, 60, 120, 240, 1440)
            
        Returns:
            List of OHLCV data points or None if failed
        """
        try:
            if not self.connected:
                return None
            
            # Convert symbol format if needed
            api_symbol = self._convert_symbol_format(symbol)
            if not api_symbol:
                return None
            
            # Parse symbol (format: EXCHANGE|TOKEN)
            exchange, token = api_symbol.split('|')
            
            # Get time price series data
            data = self.api.get_time_price_series(
                exchange=exchange,
                token=token,
                starttime=start_time,
                endtime=end_time,
                interval=interval
            )
            
            if not data:
                return None
            
            # Convert to standardized format
            tpseries = []
            for item in data:
                if item.get('stat') == 'Ok':
                    # Parse the time string and convert to timestamp
                    try:
                        time_str = item.get('time', '')
                        if time_str:
                            # Parse time format: 'dd-mm-yyyy hh:mm:ss'
                            time_obj = time.strptime(time_str, '%d-%m-%Y %H:%M:%S')
                            timestamp = int(time.mktime(time_obj) * 1000)  # Convert to milliseconds
                        else:
                            timestamp = int(time.time() * 1000)
                    except ValueError:
                        timestamp = int(time.time() * 1000)
                    
                    tpseries.append({
                        'timestamp': timestamp,
                        'time': time_str,
                        'open': float(item.get('into', 0)),
                        'high': float(item.get('inth', 0)),
                        'low': float(item.get('intl', 0)),
                        'close': float(item.get('intc', 0)),
                        'volume': float(item.get('intv', 0)),
                        'oi': float(item.get('intoi', 0))  # Open Interest
                    })
            
            return tpseries
            
        except Exception as e:
            self.logger.error(f"Failed to get tpseries for {symbol}: {e}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current ticker data for a symbol using websocket data."""
        try:
            if not self.connected:
                return None
            
            # Convert symbol format if needed
            api_symbol = self._convert_symbol_format(symbol)
            if not api_symbol:
                return None
            
            # Parse symbol (format: EXCHANGE|TOKEN)
            exchange, token = api_symbol.split('|')
            
            # First try to get data from websocket cache
            if api_symbol in self.subscribers:
                subscriber_data = self.subscribers[api_symbol]
                if subscriber_data.get('ltp_data'):
                    ltp_data = subscriber_data['ltp_data']
                    return {
                        'symbol': symbol,
                        'price': ltp_data.get('price', 0.0),
                        'volume': ltp_data.get('volume', 0.0),
                        'timestamp': ltp_data.get('timestamp', int(time.time() * 1000)),
                        'high': ltp_data.get('high', 0.0),
                        'low': ltp_data.get('low', 0.0),
                        'open': ltp_data.get('open', 0.0),
                        'close': ltp_data.get('close', 0.0)
                    }
            
            # Try to get from previous_data cache (websocket data)
            if api_symbol in self.previous_data:
                prev_data = self.previous_data[api_symbol]
                return {
                    'symbol': symbol,
                    'price': prev_data.get('price', 0.0),
                    'volume': prev_data.get('volume', 0.0),
                    'timestamp': prev_data.get('timestamp', int(time.time() * 1000)),
                    'high': prev_data.get('high', 0.0),
                    'low': prev_data.get('low', 0.0),
                    'open': prev_data.get('open', 0.0),
                    'close': prev_data.get('close', 0.0)
                }
            
            # If no websocket data available, subscribe to the symbol and wait briefly
            self.logger.debug(f"No websocket data for {symbol}, subscribing...")
            self.api.subscribe(api_symbol)
            
            # Wait briefly for websocket data
            time.sleep(0.05)  # Reduced from 0.2s to 0.05s
            
            # Check again after subscription
            if api_symbol in self.subscribers:
                subscriber_data = self.subscribers[api_symbol]
                if subscriber_data.get('ltp_data'):
                    ltp_data = subscriber_data['ltp_data']
                    return {
                        'symbol': symbol,
                        'price': ltp_data.get('price', 0.0),
                        'volume': ltp_data.get('volume', 0.0),
                        'timestamp': ltp_data.get('timestamp', int(time.time() * 1000)),
                        'high': ltp_data.get('high', 0.0),
                        'low': ltp_data.get('low', 0.0),
                        'open': ltp_data.get('open', 0.0),
                        'close': ltp_data.get('close', 0.0)
                    }
            
            # If still no data, return default ticker
            self.logger.debug(f"No websocket data available for {symbol}, returning default ticker")
            return {
                'symbol': symbol,
                'price': 0.0,
                'volume': 0.0,
                'timestamp': int(time.time() * 1000),
                'high': 0.0,
                'low': 0.0,
                'open': 0.0,
                'close': 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get ticker for {symbol}: {e}")
            return None
    
    def get_balance(self) -> Optional[Dict[str, Any]]:
        """Get account balance."""
        try:
            if not self.connected:
                return None
            
            limits = self.api.get_limits()
            if not limits or limits.get('stat') != 'Ok':
                return None
            
            return {
                'cash': float(limits.get('cash', 0)),
                'margin_used': float(limits.get('marginused', 0)),
                'available_margin': float(limits.get('cash', 0)) - float(limits.get('marginused', 0))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get balance: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None,
                   order_type: str = 'market', product_type: str = 'I') -> Optional[Dict[str, Any]]:
        """Place a trading order."""
        try:
            self.logger.info(f"🎯 Placing {order_type.upper()} {side.upper()} order for {symbol}")
            
            
            if not self.connected:
                self.logger.error("❌ MyntAPI not connected")
                return None
            
            # Convert symbol format if needed
            api_symbol = self._convert_symbol_format(symbol)
            if not api_symbol:
                self.logger.error("❌ Failed to convert symbol format")
                return None
            
            # Get symbol info for trading symbol
            # We need to convert API symbol back to Masters format for symbol_manager
            exchange, token = api_symbol.split('|')
            
            # Try to find the symbol in the symbol manager using the token
            symbol_info = None
            try:
                # Get all symbols for this exchange
                exchange_symbols = self.symbol_manager.get_exchange_symbols(exchange)
                
                # Find the symbol with matching token
                for sym in exchange_symbols:
                    if str(sym.get('token', '')) == str(token):
                        symbol_info = sym
                        break
                
                if not symbol_info:
                    self.logger.error(f"❌ No symbol found with token {token} in exchange {exchange}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"❌ Error searching for symbol: {e}")
                return None
            
            # Extract trading symbol from the symbol info
            trading_symbol = symbol_info.get('tsym', '') or symbol_info.get('symbol', '')
            if not trading_symbol:
                self.logger.error("❌ No trading symbol found in symbol info")
                return None
            
            # Convert side
            buy_or_sell = 'B' if side.lower() == 'buy' else 'S'
            
            # Convert order type
            if order_type.lower() == 'market':
                price_type = PriceType.Market
                price = 0.0
            elif order_type.lower() == 'limit':
                price_type = PriceType.Limit
            else:
                price_type = PriceType.Limit
            
            # Place order
            
            result = self.api.place_order(
                buy_or_sell=buy_or_sell,
                product_type=product_type,
                exchange=exchange,
                tradingsymbol=trading_symbol,
                quantity=int(amount),
                discloseqty=0,
                price_type=price_type,
                price=price or 0.0,
                trigger_price=0.0,
                retention='DAY',
                remarks='ZebuBot'
            )
            
            if result and result.get('stat') == 'Ok':
                self.logger.info(f"✅ Order placed successfully: {result.get('norenordno', 'N/A')}")
            else:
                self.logger.error(f"❌ Order placement failed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to place order: {e}")
            return None
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions."""
        try:
            if not self.connected:
                return []
            
            positions = self.api.get_positions()
            if not positions:
                return []
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return []
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get current orders."""
        try:
            if not self.connected:
                return []
            
            orders = self.api.get_order_book()
            if not orders:
                return []
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            return []
    
    def start_websocket(self, symbols: List[str], callback: Callable) -> bool:
        """Start websocket feed for symbols."""
        try:
            if not self.connected:
                return False
            
            # Store callback
            self.callbacks['market_data'] = callback
            
            # Start websocket
            self.api.start_websocket(
                subscribe_callback=self._on_market_data,
                order_update_callback=self._on_order_update,
                socket_open_callback=self._on_websocket_open,
                socket_close_callback=self._on_websocket_close
            )
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.websocket_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.websocket_connected:
                self.logger.error("Websocket connection timeout")
                return False
            
            # Subscribe to symbols
            for symbol in symbols:
                # Convert symbol format if needed
                api_symbol = self._convert_symbol_format(symbol)
                if api_symbol:
                    self.api.subscribe(api_symbol)
                else:
                    self.logger.warning(f"Could not convert symbol {symbol} for subscription")
            
            self.logger.info(f"Websocket started for {len(symbols)} symbols")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start websocket: {e}")
            return False
    
    def stop_websocket(self):
        """Stop websocket connection."""
        try:
            if self.api and self.websocket_connected:
                self.api.close_websocket()
                self.websocket_connected = False
                self.logger.info("Websocket stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop websocket: {e}")
    
    def _on_market_data(self, data):
        """Handle market data from websocket."""
        try:
            if self.callbacks.get('market_data'):
                symbol = f"{data.get('e', 'NSE')}|{data.get('tk', '')}"
                
                # Get previous data for this symbol
                prev_data = self.previous_data.get(symbol, {})
                
                # Process new data, using previous values when new data is missing or 0
                new_price = float(data.get('lp', 0))
                new_volume = float(data.get('v', 0))
                new_high = float(data.get('h', 0))
                new_low = float(data.get('l', 0))
                new_open = float(data.get('o', 0))
                
                # Use previous values if new values are missing or 0
                price = new_price if new_price > 0 else prev_data.get('price', 0)
                volume = new_volume if new_volume > 0 else prev_data.get('volume', 0)
                high = new_high if new_high > 0 else prev_data.get('high', 0)
                low = new_low if new_low > 0 else prev_data.get('low', 0)
                open_price = new_open if new_open > 0 else prev_data.get('open', 0)
                
                # Convert MyntAPI format to ZebuBot format
                ticker_data = {
                    'symbol': symbol,
                    'price': price,
                    'volume': volume,
                    'timestamp': int(time.time() * 1000),
                    'high': high,
                    'low': low,
                    'open': open_price
                }
                
                # Update previous data with current values (only if they're valid)
                if new_price > 0:
                    self.previous_data[symbol] = {
                        'price': price,
                        'volume': volume,
                        'high': high,
                        'low': low,
                        'open': open_price,
                        'timestamp': ticker_data['timestamp']
                    }
                
                # Update subscriber data for multiple strikes LTP function
                if symbol in self.subscribers:
                    self.subscribers[symbol]['ltp_data'] = ticker_data
                    self.subscribers[symbol]['last_update'] = time.time()
                
                self.callbacks['market_data'](ticker_data['symbol'], ticker_data)
                
        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
    
    def _on_order_update(self, data):
        """Handle order updates from websocket."""
        try:
            if self.callbacks.get('order_update'):
                self.callbacks['order_update'](data)
        except Exception as e:
            self.logger.error(f"Error processing order update: {e}")
    
    def _on_websocket_open(self):
        """Handle websocket open."""
        self.websocket_connected = True
        self.logger.info("MyntAPI websocket connected")
    
    def _on_websocket_close(self):
        """Handle websocket close."""
        self.websocket_connected = False
        self.logger.info("MyntAPI websocket disconnected")
    
    def search_symbol(self, exchange: str, search_text: str) -> Optional[List[Dict[str, Any]]]:
        """Search for symbols using symbol manager."""
        try:
            # Refresh symbols if needed
            self.symbol_manager.refresh_symbols()
            
            # Search using symbol manager
            results = self.symbol_manager.search_symbols(search_text, exchange)
            
            # Convert to expected format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'exch': result['exchange'],
                    'token': result['token'],
                    'tsym': result['symbol'],
                    'cname': result['name'],
                    'pp': '2',  # Price precision
                    'ls': result['lot_size'],
                    'ti': result['tick_size']
                })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Failed to search symbols: {e}")
            return None
    
    def get_security_info(self, exchange: str, token: str) -> Optional[Dict[str, Any]]:
        """Get security information."""
        try:
            if not self.connected:
                return None
            
            result = self.api.get_security_info(exchange=exchange, token=token)
            if result and result.get('stat') == 'Ok':
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get security info: {e}")
            return None
    
    def refresh_symbols(self) -> bool:
        """Refresh symbols from Masters endpoint."""
        try:
            return self.symbol_manager.refresh_symbols()
        except Exception as e:
            self.logger.error(f"Failed to refresh symbols: {e}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information."""
        try:
            return self.symbol_manager.get_symbol_info(symbol)
        except Exception as e:
            self.logger.error(f"Failed to get symbol info: {e}")
            return None
    
    def get_symbols_count(self) -> int:
        """Get total number of symbols."""
        return self.symbol_manager.get_symbol_count()
    
    def get_exchange_symbols(self, exchange: str) -> List[Dict[str, Any]]:
        """Get all symbols for an exchange."""
        try:
            return self.symbol_manager.get_exchange_symbols(exchange)
        except Exception as e:
            self.logger.error(f"Failed to get exchange symbols: {e}")
            return []
    
    def get_multiple_strikes_ltp(self, strike_symbols: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get LTP for multiple strikes simultaneously using websocket data.
        
        Args:
            strike_symbols: List of dicts with keys: 'exchange', 'token', 'strike', 'trading_symbol'
            
        Returns:
            Dict with strike as key and LTP data as value
        """
        try:
            if not self.connected:
                self.logger.error("MyntAPI not connected")
                return {}
            
            # Subscribe to all strike symbols if not already subscribed
            symbols_to_subscribe = []
            for strike_info in strike_symbols:
                api_symbol = f"{strike_info['exchange']}|{strike_info['token']}"
                if api_symbol not in self.subscribers:
                    symbols_to_subscribe.append(api_symbol)
                    self.subscribers[api_symbol] = {
                        'strike': strike_info['strike'],
                        'trading_symbol': strike_info['trading_symbol'],
                        'last_update': 0,
                        'ltp_data': None
                    }
            
            # Subscribe to new symbols
            if symbols_to_subscribe:
                for symbol in symbols_to_subscribe:
                    self.api.subscribe(symbol)
                self.logger.info(f"📡 Subscribed to {len(symbols_to_subscribe)} strike symbols for LTP")
                
                # Reduced wait time for websocket data to populate
                time.sleep(0.1)  # Reduced from 0.5s to 0.1s
            
            # Collect LTP data from websocket cache
            ltp_results = {}
            for strike_info in strike_symbols:
                api_symbol = f"{strike_info['exchange']}|{strike_info['token']}"
                strike = strike_info['strike']
                
                if api_symbol in self.subscribers:
                    subscriber_data = self.subscribers[api_symbol]
                    if subscriber_data['ltp_data']:
                        ltp_results[str(strike)] = {
                            'strike': strike,
                            'trading_symbol': strike_info['trading_symbol'],
                            'price': subscriber_data['ltp_data'].get('price', 0),
                            'volume': subscriber_data['ltp_data'].get('volume', 0),
                            'timestamp': subscriber_data['ltp_data'].get('timestamp', 0),
                            'high': subscriber_data['ltp_data'].get('high', 0),
                            'low': subscriber_data['ltp_data'].get('low', 0),
                            'open': subscriber_data['ltp_data'].get('open', 0)
                        }
                    else:
                        # Fallback to websocket-based get_ticker if no cached data
                        ticker_data = self.get_ticker(f"{strike_info['exchange']}:{strike_info['trading_symbol']}")
                        if ticker_data and ticker_data.get('price', 0) > 0:
                            ltp_results[str(strike)] = {
                                'strike': strike,
                                'trading_symbol': strike_info['trading_symbol'],
                                'price': ticker_data.get('price', 0),
                                'volume': ticker_data.get('volume', 0),
                                'timestamp': ticker_data.get('timestamp', 0),
                                'high': ticker_data.get('high', 0),
                                'low': ticker_data.get('low', 0),
                                'open': ticker_data.get('open', 0)
                            }
                        else:
                            ltp_results[str(strike)] = {
                                'strike': strike,
                                'trading_symbol': strike_info['trading_symbol'],
                                'price': 0,
                                'volume': 0,
                                'timestamp': int(time.time() * 1000),
                                'high': 0,
                                'low': 0,
                                'open': 0
                            }
            
            self.logger.info(f"📊 Retrieved LTP for {len(ltp_results)} strikes")
            return ltp_results
            
        except Exception as e:
            self.logger.error(f"Failed to get multiple strikes LTP: {e}")
            return {}
    
    def logout(self):
        """Logout from MyntAPI."""
        try:
            if self.connected and self.api:
                self.api.logout()
                self.connected = False
                self.logger.info("MyntAPI logged out")
        except Exception as e:
            self.logger.error(f"Failed to logout: {e}")
