"""
ZebuBot CLI interface.
"""

import click
import os
import sys
import time
from pathlib import Path
from typing import Optional

from .config import ConfigManager
from .executor import ScriptExecutor
from .realtime_executor import RealtimeExecutor
from .core import ZebuBot


def _find_config_file(config_name: str) -> Optional[Path]:
    """Find configuration file in current directory or parent directories"""
    current_path = Path.cwd()
    
    # Check current directory first
    config_path = current_path / config_name
    if config_path.exists():
        return config_path
    
    # Check parent directories up to 3 levels
    for _ in range(3):
        current_path = current_path.parent
        config_path = current_path / config_name
        if config_path.exists():
            return config_path
    
    return None


def _find_script_file(script_name: str, output_dir: str = "scripts") -> Optional[Path]:
    """Find script file with priority: zebubot/scripts/ -> outside scripts/ -> current directory"""
    
    # Ensure script_name has .py extension
    if not script_name.endswith('.py'):
        script_name += '.py'
    
    # 1. First priority: Look in zebubot/scripts/ directory (inside package)
    zebubot_scripts_dir = Path("zebubot") / "scripts"
    if zebubot_scripts_dir.exists():
        script_path = zebubot_scripts_dir / script_name
        if script_path.exists():
            return script_path
    
    # 2. Second priority: Look in project's scripts/ directory
    project_scripts_dir = Path("scripts")
    if project_scripts_dir.exists():
        script_path = project_scripts_dir / script_name
        if script_path.exists():
            return script_path
    
    # 3. Third priority: Look in specified output directory
    output_scripts_dir = Path(output_dir)
    if output_scripts_dir.exists():
        script_path = output_scripts_dir / script_name
        if script_path.exists():
            return script_path
    
    # 4. Fourth priority: Look in current directory
    current_dir_script = Path(script_name)
    if current_dir_script.exists():
        return current_dir_script
    
    # 5. Fifth priority: Look in parent directories' scripts folders
    current_path = Path.cwd()
    for _ in range(3):
        current_path = current_path.parent
        parent_scripts_dir = current_path / "scripts"
        if parent_scripts_dir.exists():
            script_path = parent_scripts_dir / script_name
            if script_path.exists():
                return script_path
    
    # 6. Sixth priority: Look for absolute path or relative path from current directory
    script_path = Path(script_name)
    if script_path.is_absolute() and script_path.exists():
        return script_path
    
    return None




@click.group()
@click.version_option(version="0.1.0")
def main():
    """ZebuBot - A trading bot framework with API configuration and script execution."""
    pass


@main.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.option('--file', '-f', default='zebubot_config.yaml', help='Configuration file path')
def init(file: str):
    """Initialize ZebuBot configuration."""
    config_manager = ConfigManager()
    config_path = Path(file)
    
    if config_path.exists():
        click.confirm(f"Configuration file {file} already exists. Overwrite?", abort=True)
    
    config_manager.create_default_config(file)
    click.echo(f"[OK] Configuration file created: {file}")
    click.echo("[INFO] Please edit the configuration file with your API credentials.")


@config.command()
@click.option('--file', '-f', default='zebubot_config.yaml', help='Configuration file path')
def validate(file: str):
    """Validate configuration file."""
    config_manager = ConfigManager()
    
    try:
        config = config_manager.load_config(file)
        click.echo("[OK] Configuration file is valid")
        click.echo(f"[INFO] Found {len(config.get('exchanges', {}))} configured exchanges")
    except Exception as e:
        click.echo(f"[ERROR] Configuration error: {e}")
        sys.exit(1)


@main.command()
@click.argument('script_name', required=False)
@click.option('--template', '-t', help='Template to use for the script')
@click.option('--output-dir', '-o', default='scripts', help='Output directory for scripts')
@click.option('--config', '-c', default='zebubot_config.yaml', help='Configuration file path')
@click.option('--help-strategies', is_flag=True, help='Show available strategies and exit')
def create(script_name: Optional[str], template: Optional[str], output_dir: str, config: str, help_strategies: bool):
    """Create and execute a trading script with real-time MyntAPI integration."""
    if help_strategies:
        # Show available strategies
        all_scripts = []
        
        # Check zebubot/scripts directory first
        zebubot_scripts_dir = Path("zebubot") / "scripts"
        if zebubot_scripts_dir.exists():
            scripts = [f for f in zebubot_scripts_dir.glob("*.py")]
            for script in scripts:
                all_scripts.append((script, "zebubot/scripts"))
        
        # Check project scripts directory
        scripts_dir = Path("scripts")
        if scripts_dir.exists():
            scripts = [f for f in scripts_dir.glob("*.py")]
            for script in scripts:
                all_scripts.append((script, "scripts"))
        
        if not all_scripts:
            click.echo("[INFO] No strategies found. Create one with 'zebubot strategy create <name>'")
            return
        
        click.echo("[STRATEGIES] Available strategies:")
        for script, location in sorted(all_scripts, key=lambda x: x[0].name):
            config_path = Path("configs") / f"{script.stem}.yaml"
            config_status = "✓" if config_path.exists() else "✗"
            click.echo(f"  {config_status} {script.name} (from {location}, config: {config_status})")
        return
    
    if not script_name:
        click.echo("[ERROR] Script name is required. Use --help-strategies to see available strategies.")
        return
    
    # Ensure script_name ends with .py
    if not script_name.endswith('.py'):
        script_name += '.py'
    
    # Load configuration from YAML
    config_manager = ConfigManager()
    try:
        # Try to find config file in current directory or parent directories
        config_path = _find_config_file(config)
        if not config_path:
            click.echo(f"[ERROR] Configuration file not found: {config}")
            click.echo("[INFO] Please run 'zebubot config init' to create a configuration file")
            sys.exit(1)
        
        config_data = config_manager.load_config(str(config_path))
    except Exception as e:
        click.echo(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)
    
    # Get symbols and exchange from config
    myntapi_config = config_data.get('myntapi', {})
    if not myntapi_config.get('enabled', False):
        click.echo("[ERROR] MyntAPI is not enabled in configuration")
        sys.exit(1)
    
    # Get default symbols from config
    symbols = [config_data.get('trading', {}).get('default_pair', 'NSE|2885')]
    exchange = 'myntapi'
    
    click.echo(f"[START] Starting real-time execution: {script_name}")
    click.echo(f"[INFO] Using symbols: {symbols}")
    click.echo(f"[INFO] Using exchange: {exchange}")
    
    realtime_executor = RealtimeExecutor()
    
    if not realtime_executor.initialize():
        click.echo("[ERROR] Failed to initialize real-time executor")
        sys.exit(1)
    
    # Try to find existing script first
    script_path = _find_script_file(script_name, output_dir)
    
    if not script_path:
    # Create real-time script template if it doesn't exist
    script_path = Path(output_dir) / script_name
        click.echo(f"[CREATE] Creating real-time script: {script_name}")
        realtime_executor.create_realtime_script_template(script_name, output_dir)
    else:
        click.echo(f"[FOUND] Using existing script: {script_path}")
    
    # Create per-script config template if it doesn't exist
    configs_dir = Path('configs')
    configs_dir.mkdir(parents=True, exist_ok=True)
    script_config_path = configs_dir / f"{script_path.stem}.yaml"
    if not script_config_path.exists():
        try:
            template_yaml = (
                "# Per-script configuration for ZebuBot (MyntAPI)\n"
                f"# Script: {script_name}\n"
                "# Symbols use user-friendly format like NSE:SBIN-EQ; they will be converted automatically.\n"
                "symbols:\n"
                "  - NSE:SBIN-EQ\n"
                "exchange: myntapi\n"
                "strategy:\n"
                "  rsi_period: 14\n"
                "  sma_fast: 20\n"
                "  sma_slow: 50\n"
                "  bb_period: 20\n"
                "  bb_stddev: 2.0\n"
                "  macd_fast: 12\n"
                "  macd_slow: 26\n"
                "  macd_signal: 9\n"
                "risk:\n"
                "  min_position_inr: 1000\n"
                "  max_position_pct: 0.04\n"
            )
            script_config_path.write_text(template_yaml, encoding='utf-8')
            click.echo(f"[CREATE] Created script config: {script_config_path}")
        except Exception as e:
            click.echo(f"[WARN] Failed to create script config: {e}")
    
    # Start real-time execution
    try:
        success = realtime_executor.start_script(script_path, symbols, exchange)
        if success:
            click.echo(f"[OK] Real-time execution started for {symbols}")
            click.echo("[INFO] Press Ctrl+C to stop...")
            
            try:
                # Keep running until interrupted
                while realtime_executor.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n[STOP] Stopping real-time execution...")
                realtime_executor.stop_all_scripts()
                click.echo("[OK] Real-time execution stopped")
        else:
            click.echo("[ERROR] Failed to start real-time execution")
            sys.exit(1)
    except Exception as e:
        click.echo(f"[ERROR] Real-time execution failed: {e}")
        sys.exit(1)


@main.group()
def list():
    """List available resources."""
    pass


@list.command()
def scripts():
    """List available trading scripts."""
    all_scripts = []
    
    # Check zebubot/scripts directory first
    zebubot_scripts_dir = Path("zebubot") / "scripts"
    if zebubot_scripts_dir.exists():
        scripts = [f for f in zebubot_scripts_dir.glob("*.py")]
        for script in scripts:
            all_scripts.append((script, "zebubot/scripts"))
    
    # Check project scripts directory
    scripts_dir = Path("scripts")
    if scripts_dir.exists():
        scripts = [f for f in scripts_dir.glob("*.py")]
        for script in scripts:
            all_scripts.append((script, "scripts"))
    
    if not all_scripts:
        click.echo("[INFO] No scripts found. Create one with 'zebubot create <script_name>'")
        return
    
    click.echo("[SCRIPTS] Available scripts:")
    for script, location in sorted(all_scripts, key=lambda x: x[0].name):
        click.echo(f"  - {script.name} (from {location})")


@main.command()
@click.option('--config', '-c', default='zebubot_config.yaml', help='Configuration file path')
def status(config: str):
    """Show ZebuBot status and configuration summary."""
    try:
        config_manager = ConfigManager()
        config_data = config_manager.load_config(config)
        
        click.echo("ZebuBot Status")
        click.echo("=" * 50)
        click.echo(f"Configuration: {config}")
        click.echo(f"Exchanges: {len(config_data.get('exchanges', {}))}")
        click.echo(f"Scripts Directory: scripts/")
        
        # Check if scripts directory exists
        scripts_dir = Path("scripts")
        if scripts_dir.exists():
            script_count = len(list(scripts_dir.glob("*.py")))
            click.echo(f"Scripts: {script_count}")
        else:
            click.echo("Scripts: 0 (scripts directory not found)")
            
    except Exception as e:
        click.echo(f"[ERROR] Error loading configuration: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


# -------------------- Strategy Scaffold Commands --------------------

@main.group()
def strategy():
    """Strategy management commands."""
    pass


@strategy.command('list')
def strategy_list():
    """List available strategies."""
    all_scripts = []
    
    # Check zebubot/scripts directory first
    zebubot_scripts_dir = Path("zebubot") / "scripts"
    if zebubot_scripts_dir.exists():
        scripts = [f for f in zebubot_scripts_dir.glob("*.py")]
        for script in scripts:
            all_scripts.append((script, "zebubot/scripts"))
    
    # Check project scripts directory
    scripts_dir = Path("scripts")
    if scripts_dir.exists():
        scripts = [f for f in scripts_dir.glob("*.py")]
        for script in scripts:
            all_scripts.append((script, "scripts"))
    
    if not all_scripts:
        click.echo("[INFO] No strategies found. Create one with 'zebubot strategy create <name>'")
        return
    
    click.echo("[STRATEGIES] Available strategies:")
    for script, location in sorted(all_scripts, key=lambda x: x[0].name):
        config_path = Path("configs") / f"{script.stem}.yaml"
        config_status = "✓" if config_path.exists() else "✗"
        click.echo(f"  {config_status} {script.name} (from {location}, config: {config_status})")


@strategy.command('create')
@click.argument('name')
@click.option('--type', '-t', 'strategy_type', 
              type=click.Choice(['basic', 'rsi', 'moving_average', 'option_trading', 'custom']), 
              default='basic', help='Strategy type to create')
@click.option('--output-dir', '-o', default='scripts', help='Directory for the new strategy')
@click.option('--config-dir', '-c', default='configs', help='Directory for the configuration file')
def strategy_create(name: str, strategy_type: str, output_dir: str, config_dir: str):
    """Create a new strategy (Python + YAML)."""
    scripts_dir = Path(output_dir)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    configs_dir = Path(config_dir)
    configs_dir.mkdir(parents=True, exist_ok=True)

    # Ensure .py extension
    py_name = name if name.endswith('.py') else f"{name}.py"
    strategy_path = scripts_dir / py_name
    yaml_path = configs_dir / f"{Path(py_name).stem}.yaml"

    if strategy_path.exists() or yaml_path.exists():
        click.echo(f"[ERROR] Strategy already exists: {strategy_path} / {yaml_path}")
        sys.exit(1)

    # Generate strategy based on type
    if strategy_type == 'option_trading':
        strategy_template, yaml_template = _generate_option_trading_strategy(py_name)
    elif strategy_type == 'rsi':
        strategy_template, yaml_template = _generate_rsi_strategy(py_name)
    elif strategy_type == 'moving_average':
        strategy_template, yaml_template = _generate_moving_average_strategy(py_name)
    else:  # basic or custom
        strategy_template, yaml_template = _generate_basic_strategy(py_name)

    try:
        strategy_path.write_text(strategy_template, encoding='utf-8')
        yaml_path.write_text(yaml_template, encoding='utf-8')
        click.echo(f"[CREATE] Strategy created: {strategy_path}")
        click.echo(f"[CREATE] Config created: {yaml_path}")
        click.echo(f"[RUN] python -m zebubot create {strategy_path.name}")
    except Exception as e:
        click.echo(f"[ERROR] Failed to create strategy: {e}")
        sys.exit(1)


def _generate_basic_strategy(py_name: str):
    """Generate basic strategy template"""
    strategy_template = (
        '"""\n'
        'Basic Strategy Template (MyntAPI)\n'
        'This file is executed on each tick.\n'
        'Injected context: zebubot, bot, logger, current_symbol, ticker_data, current_price, current_volume, current_high, current_low, current_open, strategy, risk\n'
        '"""\n\n'
        'from collections import deque\n'
        'import time\n\n'
        'price_history = deque(maxlen=1000)\n\n'
        'def on_tick(symbol, data):\n'
        '    price = data.get("price", 0.0)\n'
        '    if price <= 0:\n'
        '        logger.debug(f"{symbol} no valid price, skipping")\n'
        '        return\n'
        '    price_history.append(price)\n'
        '    # Example: use strategy params\n'
        '    rsi_period = strategy.get("rsi_period", 14) if isinstance(strategy, dict) else 14\n'
        '    logger.info(f"[TICK] {symbol} price={price} rsi_period={rsi_period}")\n\n'
        'def main():\n'
        '    on_tick(current_symbol, ticker_data)\n'
    )

    yaml_template = (
        "# Basic strategy configuration\n"
        f"# Script: {py_name}\n"
        "symbols:\n"
        "  - NSE:SBIN-EQ\n"
        "exchange: myntapi\n"
        "strategy:\n"
        "  rsi_period: 14\n"
        "risk:\n"
        "  min_position_inr: 1000\n"
    )

    return strategy_template, yaml_template


@strategy.command('option')
@click.argument('name')
@click.option('--output-dir', '-o', default='scripts', help='Directory for the new strategy')
@click.option('--config-dir', '-c', default='configs', help='Directory for the configuration file')
def strategy_option(name: str, output_dir: str, config_dir: str):
    """Create a new option trading strategy."""
    strategy_create(name, 'option_trading', output_dir, config_dir)


def _generate_rsi_strategy(py_name: str):
    """Generate RSI strategy template"""
    strategy_template = (
        '"""\n'
        'RSI Strategy Template (MyntAPI)\n'
        'This file implements a simple RSI-based trading strategy.\n'
        '"""\n\n'
        'from collections import deque\n'
        'import pandas as pd\n'
        'import time\n\n'
        'price_history = deque(maxlen=1000)\n'
        'last_signal = None\n\n'
        'def calculate_rsi(prices, period=14):\n'
        '    """Calculate RSI indicator"""\n'
        '    if len(prices) < period + 1:\n'
        '        return None\n'
        '    delta = pd.Series(prices).diff()\n'
        '    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()\n'
        '    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()\n'
        '    rs = gain / loss\n'
        '    rsi = 100 - (100 / (1 + rs))\n'
        '    return rsi.iloc[-1]\n\n'
        'def on_tick(symbol, data):\n'
        '    global last_signal\n'
        '    \n'
        '    price = data.get("price", 0.0)\n'
        '    if price <= 0:\n'
        '        logger.debug(f"{symbol} no valid price, skipping")\n'
        '        return\n'
        '    \n'
        '    price_history.append(price)\n'
        '    \n'
        '    # Get strategy parameters\n'
        '    rsi_period = strategy.get("rsi_period", 14) if isinstance(strategy, dict) else 14\n'
        '    oversold_level = strategy.get("oversold_level", 30) if isinstance(strategy, dict) else 30\n'
        '    overbought_level = strategy.get("overbought_level", 70) if isinstance(strategy, dict) else 70\n'
        '    \n'
        '    if len(price_history) >= rsi_period + 1:\n'
        '        prices = list(price_history)\n'
        '        rsi = calculate_rsi(prices, rsi_period)\n'
        '        \n'
        '        if rsi is not None:\n'
        '            if rsi < oversold_level and last_signal != "BUY":\n'
        '                logger.info(f"🟢 BUY Signal! RSI: {rsi:.2f}")\n'
        '                last_signal = "BUY"\n'
        '                # Place buy order here\n'
        '                # place_order(symbol, "buy", 10, price, "limit", "myntapi")\n'
        '            elif rsi > overbought_level and last_signal != "SELL":\n'
        '                logger.info(f"🔴 SELL Signal! RSI: {rsi:.2f}")\n'
        '                last_signal = "SELL"\n'
        '                # Place sell order here\n'
        '                # place_order(symbol, "sell", 10, price, "limit", "myntapi")\n'
        '            \n'
        '            logger.info(f"[TICK] {symbol} price={price:.2f} RSI={rsi:.2f}")\n\n'
        'def main():\n'
        '    on_tick(current_symbol, ticker_data)\n'
    )

    yaml_template = (
        "# RSI Strategy Configuration\n"
        f"# Script: {py_name}\n"
        "symbols:\n"
        "  - NSE:SBIN-EQ\n"
        "exchange: myntapi\n"
        "strategy:\n"
        "  rsi_period: 14\n"
        "  oversold_level: 30\n"
        "  overbought_level: 70\n"
        "risk:\n"
        "  min_position_inr: 1000\n"
        "  max_position_pct: 0.04\n"
    )
    
    return strategy_template, yaml_template


@strategy.command('option')
@click.argument('name')
@click.option('--output-dir', '-o', default='scripts', help='Directory for the new strategy')
@click.option('--config-dir', '-c', default='configs', help='Directory for the configuration file')
def strategy_option(name: str, output_dir: str, config_dir: str):
    """Create a new option trading strategy."""
    strategy_create(name, 'option_trading', output_dir, config_dir)


def _generate_moving_average_strategy(py_name: str):
    """Generate Moving Average strategy template"""
    strategy_template = (
        '"""\n'
        'Moving Average Strategy Template (MyntAPI)\n'
        'This file implements a simple moving average crossover strategy.\n'
        '"""\n\n'
        'from collections import deque\n'
        'import pandas as pd\n'
        'import time\n\n'
        'price_history = deque(maxlen=1000)\n'
        'last_signal = None\n\n'
        'def calculate_sma(prices, period):\n'
        '    """Calculate Simple Moving Average"""\n'
        '    if len(prices) < period:\n'
        '        return None\n'
        '    return sum(prices[-period:]) / period\n\n'
        'def on_tick(symbol, data):\n'
        '    global last_signal\n'
        '    \n'
        '    price = data.get("price", 0.0)\n'
        '    if price <= 0:\n'
        '        logger.debug(f"{symbol} no valid price, skipping")\n'
        '        return\n'
        '    \n'
        '    price_history.append(price)\n'
        '    \n'
        '    # Get strategy parameters\n'
        '    fast_period = strategy.get("sma_fast", 20) if isinstance(strategy, dict) else 20\n'
        '    slow_period = strategy.get("sma_slow", 50) if isinstance(strategy, dict) else 50\n'
        '    \n'
        '    if len(price_history) >= slow_period:\n'
        '        prices = list(price_history)\n'
        '        sma_fast = calculate_sma(prices, fast_period)\n'
        '        sma_slow = calculate_sma(prices, slow_period)\n'
        '        \n'
        '        if sma_fast is not None and sma_slow is not None:\n'
        '            if sma_fast > sma_slow and last_signal != "BUY":\n'
        '                logger.info(f"🟢 BUY Signal! SMA Fast: {sma_fast:.2f}, SMA Slow: {sma_slow:.2f}")\n'
        '                last_signal = "BUY"\n'
        '                # Place buy order here\n'
        '            elif sma_fast < sma_slow and last_signal != "SELL":\n'
        '                logger.info(f"🔴 SELL Signal! SMA Fast: {sma_fast:.2f}, SMA Slow: {sma_slow:.2f}")\n'
        '                last_signal = "SELL"\n'
        '                # Place sell order here\n'
        '            \n'
        '            logger.info(f"[TICK] {symbol} price={price:.2f} SMA Fast={sma_fast:.2f} SMA Slow={sma_slow:.2f}")\n\n'
        'def main():\n'
        '    on_tick(current_symbol, ticker_data)\n'
    )

    yaml_template = (
        "# Moving Average Strategy Configuration\n"
        f"# Script: {py_name}\n"
        "symbols:\n"
        "  - NSE:SBIN-EQ\n"
        "exchange: myntapi\n"
        "strategy:\n"
        "  sma_fast: 20\n"
        "  sma_slow: 50\n"
        "risk:\n"
        "  min_position_inr: 1000\n"
        "  max_position_pct: 0.04\n"
    )
    
    return strategy_template, yaml_template


@strategy.command('option')
@click.argument('name')
@click.option('--output-dir', '-o', default='scripts', help='Directory for the new strategy')
@click.option('--config-dir', '-c', default='configs', help='Directory for the configuration file')
def strategy_option(name: str, output_dir: str, config_dir: str):
    """Create a new option trading strategy."""
    strategy_create(name, 'option_trading', output_dir, config_dir)


def _generate_option_trading_strategy(py_name: str):
    """Generate Option Trading strategy template"""
    strategy_template = (
        '"""\n'
        'Option Trading Strategy Template (MyntAPI)\n'
        'This file implements option trading strategies.\n'
        '"""\n\n'
        'from collections import deque\n'
        'import pandas as pd\n'
        'import time\n'
        'from datetime import datetime\n\n'
        'price_history = deque(maxlen=1000)\n'
        'last_signal = None\n'
        'positions = {}\n'
        'total_pnl = 0.0\n\n'
        'def calculate_rsi(prices, period=14):\n'
        '    """Calculate RSI indicator"""\n'
        '    if len(prices) < period + 1:\n'
        '        return None\n'
        '    delta = pd.Series(prices).diff()\n'
        '    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()\n'
        '    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()\n'
        '    rs = gain / loss\n'
        '    rsi = 100 - (100 / (1 + rs))\n'
        '    return rsi.iloc[-1]\n\n'
        'def get_current_time():\n'
        '    """Get current market time"""\n'
        '    return datetime.now().time()\n\n'
        'def is_market_hours():\n'
        '    """Check if current time is within market hours"""\n'
        '    current_time = get_current_time()\n'
        '    start_time = datetime.strptime(strategy.get("start_time", "09:15:00"), "%H:%M:%S").time()\n'
        '    end_time = datetime.strptime(strategy.get("end_time", "15:30:00"), "%H:%M:%S").time()\n'
        '    return start_time <= current_time <= end_time\n\n'
        'def should_entry():\n'
        '    """Determine if strategy should enter positions"""\n'
        '    if not is_market_hours():\n'
        '        return False\n'
        '    # Add your entry logic here\n'
        '    return True\n\n'
        'def should_exit():\n'
        '    """Determine if strategy should exit positions"""\n'
        '    current_time = get_current_time()\n'
        '    square_off_time = datetime.strptime(strategy.get("square_off_time", "15:25:00"), "%H:%M:%S").time()\n'
        '    return current_time >= square_off_time\n\n'
        'def on_tick(symbol, data):\n'
        '    global last_signal, total_pnl\n'
        '    \n'
        '    price = data.get("price", 0.0)\n'
        '    if price <= 0:\n'
        '        logger.debug(f"{symbol} no valid price, skipping")\n'
        '        return\n'
        '    \n'
        '    price_history.append(price)\n'
        '    \n'
        '    # Get strategy parameters\n'
        '    rsi_period = strategy.get("rsi_period", 14) if isinstance(strategy, dict) else 14\n'
        '    \n'
        '    # Check for entry\n'
        '    if should_entry() and len(positions) == 0:\n'
        '        logger.info("🟢 Entry signal detected")\n'
        '        # Add your option entry logic here\n'
        '        \n'
        '    # Check for exit\n'
        '    if should_exit() and len(positions) > 0:\n'
        '        logger.info("🔴 Exit signal detected")\n'
        '        # Add your option exit logic here\n'
        '        \n'
        '    # Log status\n'
        '    if len(price_history) >= rsi_period + 1:\n'
        '        prices = list(price_history)\n'
        '        rsi = calculate_rsi(prices, rsi_period)\n'
        '        if rsi is not None:\n'
        '            logger.info(f"[TICK] {symbol} price={price:.2f} RSI={rsi:.2f} Positions={len(positions)}")\n\n'
        'def main():\n'
        '    on_tick(current_symbol, ticker_data)\n'
    )

    yaml_template = (
        "# Option Trading Strategy Configuration\n"
        f"# Script: {py_name}\n"
        "symbols:\n"
        "  - NSE:NIFTY 50\n"
        "exchange: myntapi\n"
        "strategy:\n"
        "  start_time: \"09:15:00\"\n"
        "  end_time: \"15:30:00\"\n"
        "  square_off_time: \"15:25:00\"\n"
        "  overall_target: 5000\n"
        "  overall_stop_loss: 3000\n"
        "  idx_pair: \"NSE:NIFTY 50\"\n"
        "  rsi_period: 14\n"
        "  legs:\n"
        "    1:\n"
        "      exch: \"NFO\"\n"
        "      symbol: \"NIFTY\"\n"
        "      expiry: \"current_week\"\n"
        "      option_type: \"CE\"\n"
        "      strike_selection: \"ATM\"\n"
        "      lot_size: 1\n"
        "      order_type: \"market\"\n"
        "      product_type: \"I\"\n"
        "      price_premium: 0\n"
        "    2:\n"
        "      exch: \"NFO\"\n"
        "      symbol: \"NIFTY\"\n"
        "      expiry: \"current_week\"\n"
        "      option_type: \"PE\"\n"
        "      strike_selection: \"ATM\"\n"
        "      lot_size: 1\n"
        "      order_type: \"market\"\n"
        "      product_type: \"I\"\n"
        "      price_premium: 0\n"
        "risk:\n"
        "  min_position_inr: 1000\n"
        "  max_position_pct: 0.04\n"
    )
    
    return strategy_template, yaml_template


@strategy.command('option')
@click.argument('name')
@click.option('--output-dir', '-o', default='scripts', help='Directory for the new strategy')
@click.option('--config-dir', '-c', default='configs', help='Directory for the configuration file')
def strategy_option(name: str, output_dir: str, config_dir: str):
    """Create a new option trading strategy."""
    strategy_create(name, 'option_trading', output_dir, config_dir)
