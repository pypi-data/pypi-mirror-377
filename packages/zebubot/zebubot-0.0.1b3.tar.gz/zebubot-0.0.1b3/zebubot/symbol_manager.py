"""
Symbol data manager for MyntAPI Masters endpoint.
Loads and manages symbol data from https://be.mynt.in/Masters
"""

import json
import requests
import time
import threading
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SymbolManager:
    """Manages symbol data from MyntAPI Masters endpoint."""
    
    def __init__(self, masters_url: str = "https://be.mynt.in/Masters"):
        """Initialize symbol manager."""
        self.masters_url = masters_url
        self.symbols_data = {}
        self.last_refresh = 0
        self.refresh_interval = 300  # 5 minutes
        self.lock = threading.Lock()
        
    def load_symbols(self) -> bool:
        """Load symbols from MyntAPI Masters endpoint."""
        try:
            logger.info(f"Loading symbols from {self.masters_url}")
            response = requests.get(self.masters_url, timeout=30)
            response.raise_for_status()
            
            symbols_data = response.json()
            
            with self.lock:
                self.symbols_data = symbols_data
                self.last_refresh = time.time()
            
            logger.info(f"Loaded {len(symbols_data)} symbols from Masters endpoint")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load symbols from Masters endpoint: {e}")
            return False
    
    def refresh_symbols(self) -> bool:
        """Refresh symbols data if needed."""
        current_time = time.time()
        
        if current_time - self.last_refresh > self.refresh_interval:
            return self.load_symbols()
        
        return True
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, str]]:
        """Get symbol information by symbol name."""
        with self.lock:
            if not self.symbols_data:
                return None
            
            # Try exact match first
            if symbol in self.symbols_data:
                data = self.symbols_data[symbol]
                return {
                    'symbol': symbol,
                    'token': data[0],
                    'name': data[1],
                    'tick_size': data[2],
                    'lot_size': data[3],
                    'is_index': data[4] == 'IDX',
                    'api_symbol': f"{symbol.split(':')[0]}|{data[0]}"  # Convert to API format
                }
            
            # Try partial match
            for key, data in self.symbols_data.items():
                if symbol.upper() in key.upper() or data[1].upper() == symbol.upper():
                    return {
                        'symbol': key,
                        'token': data[0],
                        'name': data[1],
                        'tick_size': data[2],
                        'lot_size': data[3],
                        'is_index': data[4] == 'IDX',
                        'api_symbol': f"{key.split(':')[0]}|{data[0]}"  # Convert to API format
                    }
            
            return None
    
    def search_symbols(self, search_text: str, exchange: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for symbols by text."""
        with self.lock:
            if not self.symbols_data:
                return []
            
            results = []
            search_text = search_text.upper()
            
            for symbol, data in self.symbols_data.items():
                # Filter by exchange if specified
                if exchange and not symbol.startswith(exchange + ':'):
                    continue
                
                # Check if search text matches symbol or name
                if (search_text in symbol.upper() or 
                    search_text in data[1].upper()):
                    
                    results.append({
                        'symbol': symbol,
                        'token': data[0],
                        'name': data[1],
                        'tick_size': data[2],
                        'lot_size': data[3],
                        'is_index': data[4] == 'IDX',
                        'exchange': symbol.split(':')[0] if ':' in symbol else 'NSE',
                        'api_symbol': f"{symbol.split(':')[0]}|{data[0]}"  # Convert to API format
                    })
            
            return results
    
    def get_exchange_symbols(self, exchange: str) -> List[Dict[str, str]]:
        """Get all symbols for a specific exchange."""
        with self.lock:
            if not self.symbols_data:
                return []
            
            results = []
            for symbol, data in self.symbols_data.items():
                if symbol.startswith(exchange + ':'):
                    # Extract trading symbol (tsym) by removing exchange prefix
                    tsym = symbol.split(':', 1)[1] if ':' in symbol else symbol
                    results.append({
                        'symbol': symbol,
                        'tsym': tsym,  # Add tsym field for Noren API compatibility
                        'token': data[0],
                        'name': data[1],
                        'tick_size': data[2],
                        'lot_size': data[3],
                        'is_index': data[4] == 'IDX'
                    })
            
            return results
    
    def get_symbol_count(self) -> int:
        """Get total number of symbols."""
        with self.lock:
            return len(self.symbols_data)
    
    def get_exchange_count(self, exchange: str) -> int:
        """Get number of symbols for specific exchange."""
        with self.lock:
            count = 0
            for symbol in self.symbols_data.keys():
                if symbol.startswith(exchange + ':'):
                    count += 1
            return count
    
    def is_symbol_valid(self, symbol: str) -> bool:
        """Check if symbol exists."""
        with self.lock:
            return symbol in self.symbols_data
    
    def get_symbols_by_type(self, symbol_type: str = 'EQ') -> List[Dict[str, str]]:
        """Get symbols by type (EQ, SM, BE, etc.)."""
        with self.lock:
            if not self.symbols_data:
                return []
            
            results = []
            for symbol, data in self.symbols_data.items():
                if symbol.endswith('-' + symbol_type):
                    results.append({
                        'symbol': symbol,
                        'token': data[0],
                        'name': data[1],
                        'tick_size': data[2],
                        'lot_size': data[3],
                        'is_index': data[4] == 'IDX'
                    })
            
            return results
    
    def save_to_file(self, file_path: str) -> bool:
        """Save symbols data to file."""
        try:
            with self.lock:
                with open(file_path, 'w') as f:
                    json.dump(self.symbols_data, f, indent=2)
            logger.info(f"Symbols data saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save symbols data: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """Load symbols data from file."""
        try:
            if not Path(file_path).exists():
                return False
            
            with open(file_path, 'r') as f:
                symbols_data = json.load(f)
            
            with self.lock:
                self.symbols_data = symbols_data
                self.last_refresh = time.time()
            
            logger.info(f"Symbols data loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load symbols data from file: {e}")
            return False
