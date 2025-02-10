"""
Configuration package for the Telegram Film Bot.
Contains configuration files and settings.
"""

from .messages import *
from .paths import *

try:
    from .config import *
except ImportError:
    print("Warning: config.py not found. Please create it with your bot settings.")
