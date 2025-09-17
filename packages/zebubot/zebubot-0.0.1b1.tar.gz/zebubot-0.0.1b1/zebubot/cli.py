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
@click.option('--help-strategies', is_flag=True, help='Show available strategies and exit')
def create(script_name: Optional[str], template: Optional[str], output_dir: str, help_strategies: bool):
    """Create and execute a trading script with real-time MyntAPI integration."""
    if help_strategies:
        # Show available strategies
        scripts_dir = Path("scripts")
        if not scripts_dir.exists():
            click.echo("[INFO] No scripts directory found. Create one with 'zebubot strategy create <name>'")
            return
        
        scripts = [f for f in scripts_dir.glob("*.py")]
        if not scripts:
            click.echo("[INFO] No strategies found in scripts directory")
            return
        
        click.echo("[STRATEGIES] Available strategies:")
        for script in sorted(scripts):
            config_path = Path("configs") / f"{script.stem}.yaml"
            config_status = "✓" if config_path.exists() else "✗"
            click.echo(f"  {config_status} {script.name} (config: {config_status})")
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
        config = config_manager.load_config('zebubot_config.yaml')
    except Exception as e:
        click.echo(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)
    
    # Get symbols and exchange from config
    myntapi_config = config.get('myntapi', {})
    if not myntapi_config.get('enabled', False):
        click.echo("[ERROR] MyntAPI is not enabled in configuration")
        sys.exit(1)
    
    # Get default symbols from config
    symbols = [config.get('trading', {}).get('default_pair', 'NSE|2885')]
    exchange = 'myntapi'
    
    click.echo(f"[START] Starting real-time execution: {script_name}")
    click.echo(f"[INFO] Using symbols: {symbols}")
    click.echo(f"[INFO] Using exchange: {exchange}")
    
    realtime_executor = RealtimeExecutor()
    
    if not realtime_executor.initialize():
        click.echo("[ERROR] Failed to initialize real-time executor")
        sys.exit(1)
    
    # Create real-time script template if it doesn't exist
    script_path = Path(output_dir) / script_name
    if not script_path.exists():
        click.echo(f"[CREATE] Creating real-time script: {script_name}")
        realtime_executor.create_realtime_script_template(script_name, output_dir)
    
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
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        click.echo("[INFO] No scripts directory found. Create one with 'zebubot create <script_name>'")
        return
    
    scripts = list(scripts_dir.glob("*.py"))
    if not scripts:
        click.echo("[INFO] No scripts found in scripts directory")
        return
    
    click.echo("[SCRIPTS] Available scripts:")
    for script in sorted(scripts):
        click.echo(f"  - {script.name}")


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
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        click.echo("[INFO] No scripts directory found. Create one with 'zebubot strategy create <name>'")
        return
    
    scripts = [f for f in scripts_dir.glob("*.py")]
    if not scripts:
        click.echo("[INFO] No strategies found in scripts directory")
        return
    
    click.echo("[STRATEGIES] Available strategies:")
    for script in sorted(scripts):
        config_path = Path("configs") / f"{script.stem}.yaml"
        config_status = "✓" if config_path.exists() else "✗"
        click.echo(f"  {config_status} {script.name} (config: {config_status})")


@strategy.command('create')
@click.argument('name')
@click.option('--output-dir', '-o', default='scripts', help='Directory for the new strategy')
def strategy_create(name: str, output_dir: str):
    """Create a new custom strategy (Python + YAML)."""
    scripts_dir = Path(output_dir)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    configs_dir = Path('configs')
    configs_dir.mkdir(parents=True, exist_ok=True)

    # Ensure .py extension
    py_name = name if name.endswith('.py') else f"{name}.py"
    strategy_path = scripts_dir / py_name
    yaml_path = configs_dir / f"{Path(py_name).stem}.yaml"

    if strategy_path.exists() or yaml_path.exists():
        click.echo(f"[ERROR] Strategy already exists: {strategy_path} / {yaml_path}")
        sys.exit(1)

    # Minimal strategy template leveraging injected context and strategy params
    strategy_template = (
        '"""\n'
        'Custom Strategy Template (MyntAPI)\n'
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
        "# Per-strategy configuration\n"
        f"# Script: {py_name}\n"
        "symbols:\n"
        "  - NSE:SBIN-EQ\n"
        "exchange: myntapi\n"
        "strategy:\n"
        "  rsi_period: 14\n"
        "risk:\n"
        "  min_position_inr: 1000\n"
    )

    try:
        strategy_path.write_text(strategy_template, encoding='utf-8')
        yaml_path.write_text(yaml_template, encoding='utf-8')
        click.echo(f"[CREATE] Strategy created: {strategy_path}")
        click.echo(f"[CREATE] Config created: {yaml_path}")
        click.echo(f"[RUN] python -m zebubot create {strategy_path.name}")
    except Exception as e:
        click.echo(f"[ERROR] Failed to create strategy: {e}")
        sys.exit(1)
