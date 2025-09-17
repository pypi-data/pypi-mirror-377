"""
Real-time script execution engine for ZebuBot.
"""

import os
import sys
import importlib.util
import threading
import time
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable

from .config import ConfigManager
from .core import ZebuBot


def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging configuration based on config file."""
    try:
        logging_config = config.get('logging', {})
        log_file = logging_config.get('file', 'zebubot.log')
        log_level = logging_config.get('level', 'INFO')
        max_size = logging_config.get('max_size', '10MB')
        backup_count = logging_config.get('backup_count', 5)
        
        # Convert max_size to bytes
        if max_size.endswith('MB'):
            max_bytes = int(max_size[:-2]) * 1024 * 1024
        elif max_size.endswith('KB'):
            max_bytes = int(max_size[:-2]) * 1024
        else:
            max_bytes = int(max_size)
        
        # Convert log level string to logging constant
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        log_level_value = level_map.get(log_level.upper(), logging.INFO)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level_value)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level_value)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level_value)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Log the setup
        root_logger.info(f"Logging configured - File: {log_file}, Level: {log_level}, Max Size: {max_size}")
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)


class RealtimeExecutor:
    """Handles real-time execution of trading scripts with websocket feeds."""
    
    def __init__(self):
        """Initialize the real-time executor."""
        self.config_manager = ConfigManager()
        self.logger = logging.getLogger(__name__)
        self.running_scripts = {}
        self.zebubot = None
        self.running = False
    
    def initialize(self, config_path: str = "zebubot_config.yaml") -> bool:
        """Initialize the executor with configuration."""
        try:
            # Look for config file in project root if not found in current directory
            if not Path(config_path).exists():
                # Try to find the project root by looking for zebubot_config.yaml
                current_dir = Path.cwd()
                project_root = current_dir
                
                # Walk up the directory tree to find the config file
                while project_root != project_root.parent:
                    config_file = project_root / "zebubot_config.yaml"
                    if config_file.exists():
                        config_path = str(config_file)
                        break
                    project_root = project_root.parent
                
                # If still not found, try the original path
                if not Path(config_path).exists():
                    self.logger.error(f"Configuration file not found: {config_path}")
                    return False
            
            # Load configuration
            config = self.config_manager.load_config(config_path)
            
            # Setup logging first
            setup_logging(config)
            
            # Initialize ZebuBot with config
            self.zebubot = ZebuBot(config)
            self.logger.info("Real-time executor initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize real-time executor: {e}")
            return False
    
    def start_script(self, script_path: Path, symbols: List[str], 
                    exchange_name: Optional[str] = None) -> bool:
        """Start real-time execution of a script."""
        try:
            if not self.zebubot:
                self.logger.error("Executor not initialized. Call initialize() first.")
                return False
            
            if not script_path.exists():
                self.logger.error(f"Script not found: {script_path}")
                return False
            
            # Load the script module
            script_module = self._load_script(script_path)
            if not script_module:
                return False
            
            # Load per-script config if present (configs/script.yaml)
            script_config = {}
            configs_dir = Path('configs')
            script_config_path = configs_dir / f"{script_path.stem}.yaml"
            if script_config_path.exists():
                try:
                    with open(script_config_path, 'r', encoding='utf-8') as f:
                        script_config = yaml.safe_load(f) or {}
                    # Override symbols and exchange from script config
                    symbols = script_config.get('symbols', symbols) or symbols
                    exchange_name = script_config.get('exchange', exchange_name) or exchange_name
                    self.logger.info(f"Loaded script config: {script_config_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to load script config {script_config_path}: {e}")

            strategy_params = script_config.get('strategy', {}) if isinstance(script_config, dict) else {}
            risk_params = script_config.get('risk', {}) if isinstance(script_config, dict) else {}

            # Create callback function
            def script_callback(symbol: str, ticker_data: Dict[str, Any]):
                try:
                    # Inject strategy and risk params into the module
                    try:
                        setattr(script_module, 'strategy', strategy_params)
                        setattr(script_module, 'risk', risk_params)
                        # Flatten common strategy params as direct vars for convenience
                        if isinstance(strategy_params, dict):
                            for key, value in strategy_params.items():
                                # Do not overwrite existing attributes if not desired
                                setattr(script_module, key, value)
                    except Exception:
                        pass

                    # Set up script context
                    self._setup_script_context(script_module, symbol, ticker_data)
                    
                    # Execute the script's main function
                    if hasattr(script_module, 'main'):
                        script_module.main()
                    elif hasattr(script_module, 'on_tick'):
                        script_module.on_tick(symbol, ticker_data)
                    else:
                        self.logger.warning(f"No main() or on_tick() function found in {script_path}")
                        
                except Exception as e:
                    self.logger.error(f"Script execution error for {symbol}: {e}")
            
            # Start real-time execution
            success = self.zebubot.start_realtime_execution(symbols, script_callback, exchange_name)
            
            if success:
                self.running_scripts[str(script_path)] = {
                    'script_path': script_path,
                    'symbols': symbols,
                    'exchange': exchange_name,
                    'start_time': time.time()
                }
                self.running = True
                self.logger.info(f"Started real-time execution of {script_path} for {symbols}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to start script {script_path}: {e}")
            return False
    
    def stop_script(self, script_path: Path) -> bool:
        """Stop real-time execution of a script."""
        try:
            script_key = str(script_path)
            
            if script_key not in self.running_scripts:
                self.logger.warning(f"Script {script_path} is not running")
                return False
            
            # Stop the real-time execution
            self.zebubot.stop_realtime_execution()
            
            # Remove from running scripts
            del self.running_scripts[script_key]
            
            if not self.running_scripts:
                self.running = False
            
            self.logger.info(f"Stopped real-time execution of {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop script {script_path}: {e}")
            return False
    
    def stop_all_scripts(self) -> bool:
        """Stop all running scripts."""
        try:
            if self.zebubot:
                self.zebubot.stop_realtime_execution()
            
            self.running_scripts.clear()
            self.running = False
            
            self.logger.info("Stopped all real-time scripts")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop all scripts: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get executor status."""
        return {
            'running': self.running,
            'running_scripts': len(self.running_scripts),
            'script_details': {
                name: {
                    'symbols': info['symbols'],
                    'exchange': info['exchange'],
                    'start_time': info['start_time'],
                    'runtime': time.time() - info['start_time']
                }
                for name, info in self.running_scripts.items()
            },
            'zebubot_status': self.zebubot.get_status() if self.zebubot else None
        }
    
    def _load_script(self, script_path: Path):
        """Load a script module."""
        try:
            # Add the script directory to Python path
            script_dir = script_path.parent
            if str(script_dir) not in sys.path:
                sys.path.insert(0, str(script_dir))
            
            # Load the module
            spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            self.logger.error(f"Failed to load script {script_path}: {e}")
            return None
    
    def _setup_script_context(self, module, symbol: str, ticker_data: Dict[str, Any]):
        """Set up the script execution context."""
        # Set up ZebuBot context
        module.zebubot = self.zebubot
        module.bot = self.zebubot  # Alias for convenience
        
        # Set up real-time data context with fallback values
        module.current_symbol = symbol
        module.current_price = ticker_data.get('price', 0) if ticker_data.get('price', 0) > 0 else getattr(module, 'current_price', 0)
        module.current_volume = ticker_data.get('volume', 0) if ticker_data.get('volume', 0) > 0 else getattr(module, 'current_volume', 0)
        module.current_timestamp = ticker_data.get('timestamp', 0)
        module.ticker_data = ticker_data
        
        # Set up additional context variables
        module.current_high = ticker_data.get('high', 0) if ticker_data.get('high', 0) > 0 else getattr(module, 'current_high', 0)
        module.current_low = ticker_data.get('low', 0) if ticker_data.get('low', 0) > 0 else getattr(module, 'current_low', 0)
        module.current_open = ticker_data.get('open', 0) if ticker_data.get('open', 0) > 0 else getattr(module, 'current_open', 0)
        
        # Set up logging
        module.logger = logging.getLogger(f"{module.__name__}.{symbol}")
        
        # Set up common imports
        module.pd = __import__('pandas')
        module.np = __import__('numpy')
        module.time = __import__('time')
        module.datetime = __import__('datetime').datetime
        
        # Set up utility functions
        module.get_realtime_data = lambda s: self.zebubot.get_realtime_data(s)
        module.get_market_data = lambda s, t, l: self.zebubot.get_market_data(s, t, l)
        module.place_order = lambda s, side, amount, price=None: self.zebubot.place_order(s, side, amount, price)
        module.get_balance = lambda: self.zebubot.get_balance()
    
    def create_realtime_script_template(self, script_name: str, output_dir: str = "scripts") -> Path:
        """Create a real-time script template."""
        scripts_dir = Path(output_dir)
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = scripts_dir / script_name
        
        if script_path.exists():
            raise FileExistsError(f"Script {script_name} already exists")
        
        template_content = self._get_realtime_template()
        
        with open(script_path, 'w') as f:
            f.write(template_content)
        
        self.logger.info(f"Created real-time script template: {script_path}")
        return script_path
    
    def _get_realtime_template(self) -> str:
        """Get real-time script template."""
        return '''"""
Real-time Trading Strategy Script
Generated by ZebuBot
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Real-time context variables (injected by ZebuBot):
# - current_symbol: Current symbol being processed
# - current_price: Current price from ticker data (uses previous value if missing)
# - current_volume: Current volume from ticker data (uses previous value if missing)
# - current_high: Current high price (uses previous value if missing)
# - current_low: Current low price (uses previous value if missing)
# - current_open: Current open price (uses previous value if missing)
# - current_timestamp: Current timestamp
# - ticker_data: Full ticker data dictionary
# - zebubot/bot: ZebuBot instance
# - logger: Logger instance

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def on_tick(symbol, ticker_data):
    """Called on every tick/price update."""
    # Check if we have valid price data
    if current_price > 0:
        logger.info(f"[TICK] {symbol}: ${current_price:.2f} (Vol: {current_volume:,.0f})")
        
        # Your real-time trading logic here
        # This function is called every time there's a price update
        
        # Example: Simple price monitoring
        if current_price > 50000:  # Example threshold
            logger.info(f"[BUY] {symbol} price above $50,000: ${current_price:.2f}")
        elif current_price < 40000:  # Example threshold
            logger.info(f"[SELL] {symbol} price below $40,000: ${current_price:.2f}")
    else:
        logger.debug(f"[TICK] {symbol}: No price data available, using previous values")

def main():
    """Main function called on every tick."""
    # This is called for every price update
    on_tick(current_symbol, ticker_data)
    
    # Example: Get historical data for technical analysis
    try:
        # Get recent OHLCV data for RSI calculation
        ohlcv = get_market_data(current_symbol, "1h", 50)
        if ohlcv and len(ohlcv) > 14:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Calculate RSI
            rsi = calculate_rsi(df['close'])
            current_rsi = rsi.iloc[-1]
            
            logger.info(f"[RSI] {current_symbol} RSI: {current_rsi:.2f}")
            
            # RSI trading logic
            if current_rsi < 30:
                logger.info(f"[BUY] {current_symbol} RSI < 30: Potential BUY signal")
                # Add your buy logic here
                # amount = zebubot.calculate_position_size(zebubot.get_balance()['USDT']['free'])
                # zebubot.place_order(current_symbol, 'buy', amount)
                
            elif current_rsi > 70:
                logger.info(f"[SELL] {current_symbol} RSI > 70: Potential SELL signal")
                # Add your sell logic here
                # amount = zebubot.calculate_position_size(zebubot.get_balance()['BTC']['free'])
                # zebubot.place_order(current_symbol, 'sell', amount)
                
    except Exception as e:
        logger.error(f"Error in main(): {e}")

if __name__ == "__main__":
    # This will be called on every tick when running in real-time mode
    main()
'''
