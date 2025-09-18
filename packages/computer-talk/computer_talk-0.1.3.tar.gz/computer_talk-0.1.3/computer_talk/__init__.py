"""
Computer Talk - A Python package for computer communication and interaction.

This package provides tools and utilities for computer communication,
interaction, and automation tasks.
"""

__version__ = "0.1.0"
__author__ = "Jordan"
__email__ = "jordan@example.com"

from .core import ComputerTalk
from .exceptions import ComputerTalkError, CommunicationError, ConfigurationError
from .config import get_user_config_path

# Check for first run on import
try:
    from .first_run import check_and_run_onboarding
    check_and_run_onboarding()
except ImportError:
    pass

__all__ = [
    "ComputerTalk",
    "ComputerTalkError",
    "CommunicationError", 
    "ConfigurationError",
    "get_user_config_path",
]
