"""
ZebuBot - A trading bot framework with API configuration and script execution.
"""

__version__ = "0.1.0"
__author__ = "ZebuBot Team"
__email__ = "team@zebubot.com"

from .core import ZebuBot
from .config import ConfigManager
from .executor import ScriptExecutor

__all__ = ["ZebuBot", "ConfigManager", "ScriptExecutor"]
