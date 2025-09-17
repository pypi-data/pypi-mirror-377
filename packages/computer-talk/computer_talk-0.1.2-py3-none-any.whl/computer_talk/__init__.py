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

__all__ = [
    "ComputerTalk",
    "ComputerTalkError",
    "CommunicationError", 
    "ConfigurationError",
]
