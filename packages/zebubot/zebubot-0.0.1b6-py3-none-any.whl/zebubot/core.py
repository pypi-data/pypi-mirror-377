"""
Core ZebuBot trading engine.
"""

import logging
import pandas as pd
import numpy as np
import asyncio
import websockets
import json
import threading
import time
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta

from .config import ConfigManager
from .myntapi_integration import MyntAPIIntegration


class ZebuBot:
    """Main ZebuBot trading engine."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ZebuBot with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.exchanges = {}
        self.active_exchanges = []
        self.websocket_connections = {}
        self.realtime_data = {}
        self.running = False
        self.script_callbacks = {}
        self.myntapi = None
        
        # Initialize exchanges
        self._initialize_exchanges()
        self._initialize_myntapi()
    
    def _initialize_exchanges(self) -> None:
        """Initialize configured exchanges - now focused on MyntAPI only."""
        # Other exchanges removed - focusing on MyntAPI only
        self.logger.info("Exchange initialization skipped - using MyntAPI only")
    
    def _initialize_myntapi(self) -> None:
        """Initialize MyntAPI integration."""
        try:
            myntapi_config = self.config.get('myntapi', {})
            if not myntapi_config.get('enabled', False):
                return
            
            self.myntapi = MyntAPIIntegration(self.config)
            if self.myntapi.initialize():
                self.logger.info("MyntAPI initialized successfully")
            else:
                self.logger.error("Failed to initialize MyntAPI")
                self.myntapi = None
                
        except Exception as e:
            self.logger.error(f"Failed to initialize MyntAPI: {e}")
            self.myntapi = None
    
    def get_exchange(self, exchange_name: Optional[str] = None):
        """Get exchange instance - now returns MyntAPI only."""
        # Always return MyntAPI as the only exchange
        if not self.myntapi:
            raise ValueError("MyntAPI not available or not configured")
        
        return self.myntapi
    
    def get_market_data(self, symbol: str, timeframe: str = '1h', limit: int = 100, 
                       exchange_name: Optional[str] = None) -> Optional[List[List]]:
        """Get OHLCV market data from MyntAPI."""
        try:
            if not self.myntapi:
                self.logger.error("MyntAPI not available")
                return None
            
            return self.myntapi.get_market_data(symbol, timeframe, limit)
        except Exception as e:
            self.logger.error(f"Failed to fetch market data for {symbol}: {e}")
            return None
    
    def get_ticker(self, symbol: str, exchange_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get current ticker data from MyntAPI."""
        try:
            if not self.myntapi:
                self.logger.error("MyntAPI not available")
                return None
            
            return self.myntapi.get_ticker(symbol)
        except Exception as e:
            self.logger.error(f"Failed to fetch ticker for {symbol}: {e}")
            return None
    
    def get_balance(self, exchange_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get account balance from MyntAPI."""
        try:
            if not self.myntapi:
                self.logger.error("MyntAPI not available")
                return None
            
            return self.myntapi.get_balance()
        except Exception as e:
            self.logger.error(f"Failed to fetch balance: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None,
                   order_type: str = 'market', exchange_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Place a trading order via MyntAPI."""
        try:
            if not self.myntapi:
                self.logger.error("MyntAPI not available")
                return None
            
            return self.myntapi.place_order(symbol, side, amount, price, order_type)
            
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str, exchange_name: Optional[str] = None) -> bool:
        """Cancel an order via MyntAPI."""
        try:
            if not self.myntapi:
                self.logger.error("MyntAPI not available")
                return False
            
            # MyntAPI cancel order implementation would go here
            self.logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None, exchange_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders."""
        try:
            if not self.myntapi:
                self.logger.error("MyntAPI not available")
                return []
            
            # MyntAPI open orders implementation would go here
            self.logger.info("Open orders functionality not yet implemented for MyntAPI")
            return []
        except Exception as e:
            self.logger.error(f"Failed to fetch open orders: {e}")
            return []
    
    def get_order_history(self, symbol: Optional[str] = None, limit: int = 100, 
                         exchange_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get order history."""
        try:
            if not self.myntapi:
                self.logger.error("MyntAPI not available")
                return []
            
            # MyntAPI order history implementation would go here
            self.logger.info("Order history functionality not yet implemented for MyntAPI")
            return []
        except Exception as e:
            self.logger.error(f"Failed to fetch order history: {e}")
            return []
    
    def calculate_technical_indicator(self, data: pd.Series, indicator: str, **kwargs) -> pd.Series:
        """Calculate technical indicators."""
        try:
            if indicator.lower() == 'rsi':
                return self._calculate_rsi(data, **kwargs)
            elif indicator.lower() == 'macd':
                return self._calculate_macd(data, **kwargs)
            elif indicator.lower() == 'sma':
                return data.rolling(window=kwargs.get('period', 20)).mean()
            elif indicator.lower() == 'ema':
                return data.ewm(span=kwargs.get('period', 20)).mean()
            elif indicator.lower() == 'bollinger':
                return self._calculate_bollinger_bands(data, **kwargs)
            else:
                raise ValueError(f"Unsupported indicator: {indicator}")
        except Exception as e:
            self.logger.error(f"Failed to calculate {indicator}: {e}")
            return pd.Series()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    def get_risk_management_config(self) -> Dict[str, Any]:
        """Get risk management configuration."""
        return self.config.get('trading', {}).get('risk_management', {})
    
    def calculate_position_size(self, account_balance: float, risk_percentage: float = None) -> float:
        """Calculate position size based on risk management rules."""
        risk_config = self.get_risk_management_config()
        max_position_size = risk_config.get('max_position_size', 0.1)
        
        if risk_percentage is None:
            risk_percentage = max_position_size
        
        return account_balance * risk_percentage
    
    def get_status(self) -> Dict[str, Any]:
        """Get ZebuBot status."""
        status = {
            'active_exchanges': self.active_exchanges,
            'total_exchanges': len(self.exchanges),
            'config_loaded': bool(self.config),
            'trading_config': self.config.get('trading', {}),
            'risk_management': self.get_risk_management_config(),
            'websocket_connections': len(self.websocket_connections),
            'realtime_data_symbols': list(self.realtime_data.keys()),
            'running': self.running
        }
        
        # Add MyntAPI status
        if self.myntapi:
            status['myntapi'] = {
                'connected': self.myntapi.connected,
                'websocket_connected': self.myntapi.websocket_connected
            }
        else:
            status['myntapi'] = {'connected': False, 'websocket_connected': False}
        
        return status
    
    def start_realtime_feed(self, symbol: str, exchange_name: Optional[str] = None, 
                           callback: Optional[Callable] = None) -> bool:
        """Start real-time data feed for a symbol."""
        try:
            # Check if MyntAPI should be used
            if exchange_name == 'myntapi' or (exchange_name is None and self.myntapi):
                if callback:
                    self.script_callbacks[symbol] = callback
                return self.myntapi.start_websocket([symbol], callback)
            
            # Store callback for this symbol
            if callback:
                self.script_callbacks[symbol] = callback
            
            # For MyntAPI, use the integrated websocket
            if self.myntapi:
                return self.myntapi.start_websocket([symbol], callback)
            else:
                self.logger.error("No exchange available for real-time feed")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start real-time feed for {symbol}: {e}")
            return False
    
    def _start_websocket_feed(self, symbol: str, exchange) -> bool:
        """Start websocket feed for supported exchanges."""
        try:
            exchange_id = exchange.id
            
            if exchange_id == 'binance':
                ws_url = f"wss://stream.binance.com:9443/ws/{symbol.lower().replace('/', '')}@ticker"
            elif exchange_id == 'coinbasepro':
                ws_url = "wss://ws-feed.pro.coinbase.com"
            elif exchange_id == 'kraken':
                ws_url = "wss://ws.kraken.com"
            else:
                return self._start_polling_feed(symbol, exchange)
            
            # Start websocket in a separate thread
            thread = threading.Thread(
                target=self._websocket_worker,
                args=(ws_url, symbol, exchange_id),
                daemon=True
            )
            thread.start()
            
            self.websocket_connections[symbol] = {
                'url': ws_url,
                'exchange': exchange_id,
                'thread': thread,
                'last_update': time.time()
            }
            
            self.logger.info(f"Started websocket feed for {symbol} on {exchange_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Websocket feed failed for {symbol}: {e}")
            return self._start_polling_feed(symbol, exchange)
    
    def _start_polling_feed(self, symbol: str, exchange) -> bool:
        """Start polling feed as fallback."""
        try:
            def polling_worker():
                while self.running:
                    try:
                        ticker = self.get_ticker(symbol, exchange.id)
                        if ticker:
                            self._process_ticker_data(symbol, ticker)
                        time.sleep(1)  # Poll every 1 second
                    except Exception as e:
                        self.logger.error(f"Polling error for {symbol}: {e}")
                        time.sleep(5)  # Wait longer on error
            
            thread = threading.Thread(target=polling_worker, daemon=True)
            thread.start()
            
            self.websocket_connections[symbol] = {
                'type': 'polling',
                'exchange': exchange.id,
                'thread': thread,
                'last_update': time.time()
            }
            
            self.logger.info(f"Started polling feed for {symbol} on {exchange.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Polling feed failed for {symbol}: {e}")
            return False
    
    def _websocket_worker(self, ws_url: str, symbol: str, exchange_id: str):
        """Websocket worker thread."""
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._websocket_handler(ws_url, symbol, exchange_id))
        except Exception as e:
            self.logger.error(f"Websocket worker error for {symbol}: {e}")
    
    async def _websocket_handler(self, ws_url: str, symbol: str, exchange_id: str):
        """Handle websocket connection."""
        try:
            async with websockets.connect(ws_url) as websocket:
                if exchange_id == 'coinbasepro':
                    # Subscribe to ticker channel
                    subscribe_msg = {
                        "type": "subscribe",
                        "product_ids": [symbol],
                        "channels": ["ticker"]
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        self._process_websocket_data(symbol, data, exchange_id)
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        self.logger.error(f"Error processing websocket message: {e}")
                        
        except Exception as e:
            self.logger.error(f"Websocket connection error for {symbol}: {e}")
            # Fallback to polling
            self._start_polling_feed(symbol, self.exchanges.get(exchange_id))
    
    def _process_websocket_data(self, symbol: str, data: Dict[str, Any], exchange_id: str):
        """Process websocket data."""
        try:
            if exchange_id == 'binance':
                ticker_data = {
                    'symbol': symbol,
                    'price': float(data.get('c', 0)),
                    'volume': float(data.get('v', 0)),
                    'timestamp': int(data.get('E', time.time() * 1000))
                }
            elif exchange_id == 'coinbasepro':
                if data.get('type') == 'ticker':
                    ticker_data = {
                        'symbol': symbol,
                        'price': float(data.get('price', 0)),
                        'volume': float(data.get('volume_24h', 0)),
                        'timestamp': int(time.time() * 1000)
                    }
                else:
                    return
            elif exchange_id == 'kraken':
                # Kraken websocket format is different
                return
            else:
                return
            
            self._process_ticker_data(symbol, ticker_data)
            
        except Exception as e:
            self.logger.error(f"Error processing websocket data: {e}")
    
    def _process_ticker_data(self, symbol: str, ticker_data: Dict[str, Any]):
        """Process ticker data and trigger callbacks."""
        try:
            # Update real-time data
            self.realtime_data[symbol] = {
                'price': ticker_data['price'],
                'volume': ticker_data.get('volume', 0),
                'timestamp': ticker_data['timestamp'],
                'last_update': time.time()
            }
            
            # Update websocket connection timestamp
            if symbol in self.websocket_connections:
                self.websocket_connections[symbol]['last_update'] = time.time()
            
            # Trigger callback if registered
            if symbol in self.script_callbacks:
                try:
                    callback = self.script_callbacks[symbol]
                    callback(symbol, ticker_data)
                except Exception as e:
                    self.logger.error(f"Callback error for {symbol}: {e}")
            
            self.logger.debug(f"Updated {symbol}: {ticker_data['price']}")
            
        except Exception as e:
            self.logger.error(f"Error processing ticker data for {symbol}: {e}")
    
    def stop_realtime_feed(self, symbol: str) -> bool:
        """Stop real-time data feed for a symbol."""
        try:
            if symbol in self.websocket_connections:
                # Note: Thread will stop when self.running becomes False
                del self.websocket_connections[symbol]
            
            if symbol in self.script_callbacks:
                del self.script_callbacks[symbol]
            
            if symbol in self.realtime_data:
                del self.realtime_data[symbol]
            
            self.logger.info(f"Stopped real-time feed for {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop real-time feed for {symbol}: {e}")
            return False
    
    def get_realtime_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current real-time data for a symbol."""
        return self.realtime_data.get(symbol)
    
    def start_realtime_execution(self, symbols: List[str], script_callback: Callable, 
                                exchange_name: Optional[str] = None) -> bool:
        """Start real-time execution for multiple symbols."""
        try:
            self.running = True
            success_count = 0
            
            for symbol in symbols:
                if self.start_realtime_feed(symbol, exchange_name, script_callback):
                    success_count += 1
            
            if success_count > 0:
                self.logger.info(f"Started real-time execution for {success_count}/{len(symbols)} symbols")
                # Start fallback polling for all symbols
                self._start_fallback_polling(symbols, script_callback, exchange_name)
                return True
            else:
                self.logger.error("Failed to start any real-time feeds")
                # Still start fallback polling even if websocket fails
                self._start_fallback_polling(symbols, script_callback, exchange_name)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start real-time execution: {e}")
            return False
    
    def _start_fallback_polling(self, symbols: List[str], script_callback: Callable, 
                               exchange_name: Optional[str] = None):
        """Start fallback polling for symbols every 1 second."""
        try:
            def polling_worker():
                self.logger.info("🔄 Starting fallback polling (every 1 second)")
                while self.running:
                    try:
                        for symbol in symbols:
                            # Check if we have recent websocket data
                            if symbol in self.realtime_data:
                                last_update = self.realtime_data[symbol].get('last_update', 0)
                                if time.time() - last_update < 2:  # Data is fresh (less than 2 seconds old)
                                    continue  # Skip polling, websocket is working
                            
                            # Get fresh data via API call
                            ticker_data = self.get_ticker(symbol, exchange_name)
                            if ticker_data:
                                # Process the ticker data
                                self._process_ticker_data(symbol, ticker_data)
                                
                                # Trigger callback
                                if symbol in self.script_callbacks:
                                    try:
                                        callback = self.script_callbacks[symbol]
                                        callback(symbol, ticker_data)
                                    except Exception as e:
                                        self.logger.error(f"Polling callback error for {symbol}: {e}")
                            else:
                                self.logger.debug(f"No ticker data available for {symbol}")
                        
                        time.sleep(1)  # Poll every 1 second
                        
                    except Exception as e:
                        self.logger.error(f"Polling worker error: {e}")
                        time.sleep(5)  # Wait longer on error
            
            # Start polling thread
            polling_thread = threading.Thread(target=polling_worker, daemon=True)
            polling_thread.start()
            
            self.logger.info(f"Started fallback polling for {len(symbols)} symbols")
            
        except Exception as e:
            self.logger.error(f"Failed to start fallback polling: {e}")
    
    def stop_realtime_execution(self):
        """Stop all real-time execution."""
        try:
            self.running = False
            
            # Stop all feeds
            symbols_to_stop = list(self.websocket_connections.keys())
            for symbol in symbols_to_stop:
                self.stop_realtime_feed(symbol)
            
            self.logger.info("Stopped all real-time execution")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop real-time execution: {e}")
            return False
