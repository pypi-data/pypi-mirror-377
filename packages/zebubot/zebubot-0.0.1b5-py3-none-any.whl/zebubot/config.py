"""
Configuration management for ZebuBot.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages ZebuBot configuration files and API credentials."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        load_dotenv()  # Load environment variables from .env file
    
    def create_default_config(self, config_path: str) -> None:
        """Create a default configuration file."""
        config_data = {
            "zebubot": {
                "version": "0.1.0",
                "debug": False,
                "log_level": "INFO"
            },
            "exchanges": {
                # Other exchanges removed - focusing on MyntAPI only
            },
            "myntapi": {
                "enabled": True,
                "host": "https://go.mynt.in/NorenWClientTP/",
                "websocket": "wss://go.mynt.in/NorenWSTP/",
                "masters_url": "https://be.mynt.in/Masters",
                "userid": "${MYNTAPI_USERID}",
                "password": "${MYNTAPI_PASSWORD}",
                "twoFA": "${MYNTAPI_TWOFA}",
                "vendor_code": "${MYNTAPI_VENDOR_CODE}",
                "api_secret": "${MYNTAPI_API_SECRET}",
                "imei": "${MYNTAPI_IMEI}",
                "symbol_refresh_interval": 300
            },
            "trading": {
                "default_exchange": "myntapi",
                "default_pair": "NSE|2885",  # Reliance
                "risk_management": {
                    "max_position_size": 0.1,  # 10% of portfolio
                    "stop_loss_percentage": 0.02,  # 2% stop loss
                    "take_profit_percentage": 0.04  # 4% take profit
                },
                "fees": {
                    "maker": 0.001,  # 0.1%
                    "taker": 0.001   # 0.1%
                }
            },
            "scripts": {
                "directory": "scripts",
                "templates": "templates",
                "auto_execute": False,
                "log_execution": True
            },
            "logging": {
                "level": "INFO",
                "file": "zebubot.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
        else:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        # Replace environment variables
        config_data = self._replace_env_vars(config_data)
        
        return config_data
    
    def _replace_env_vars(self, data: Any) -> Any:
        """Recursively replace environment variables in configuration data."""
        if isinstance(data, dict):
            return {key: self._replace_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._replace_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        else:
            return data
    
    def get_exchange_config(self, exchange_name: str, config_path: str = "zebubot_config.yaml") -> Optional[Dict[str, Any]]:
        """Get configuration for a specific exchange."""
        config = self.load_config(config_path)
        exchanges = config.get('exchanges', {})
        return exchanges.get(exchange_name)
    
    def is_exchange_enabled(self, exchange_name: str, config_path: str = "zebubot_config.yaml") -> bool:
        """Check if an exchange is enabled."""
        exchange_config = self.get_exchange_config(exchange_name, config_path)
        return exchange_config and exchange_config.get('enabled', False)
    
    def get_trading_config(self, config_path: str = "zebubot_config.yaml") -> Dict[str, Any]:
        """Get trading configuration."""
        config = self.load_config(config_path)
        return config.get('trading', {})
    
    def get_scripts_config(self, config_path: str = "zebubot_config.yaml") -> Dict[str, Any]:
        """Get scripts configuration."""
        config = self.load_config(config_path)
        return config.get('scripts', {})
    
    def validate_config(self, config_path: str) -> bool:
        """Validate configuration file."""
        try:
            config = self.load_config(config_path)
            
            # Check required sections
            required_sections = ['exchanges', 'trading', 'scripts']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required section: {section}")
            
            # Check exchange configurations
            exchanges = config.get('exchanges', {})
            for exchange_name, exchange_config in exchanges.items():
                if exchange_config.get('enabled', False):
                    required_keys = ['api_key', 'secret_key']
                    for key in required_keys:
                        if key not in exchange_config or not exchange_config[key]:
                            raise ValueError(f"Exchange {exchange_name} is enabled but missing {key}")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}")
    
    def create_env_template(self, env_path: str = ".env.template") -> None:
        """Create a template .env file for API credentials."""
        env_template = """# ZebuBot API Credentials
# Copy this file to .env and fill in your actual API credentials

# Binance API
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# Coinbase Pro API
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_SECRET_KEY=your_coinbase_secret_key_here
COINBASE_PASSPHRASE=your_coinbase_passphrase_here

# Kraken API
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_SECRET_KEY=your_kraken_secret_key_here

# Add more API credentials as needed
"""
        
        env_file = Path(env_path)
        with open(env_file, 'w') as f:
            f.write(env_template)
