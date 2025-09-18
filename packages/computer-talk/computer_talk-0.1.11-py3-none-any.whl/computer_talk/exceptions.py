"""
Custom exceptions for the computer-talk package.
"""


class ComputerTalkError(Exception):
    """Base exception for all ComputerTalk errors."""
    pass


class CommunicationError(ComputerTalkError):
    """Raised when communication fails."""
    pass


class ConfigurationError(ComputerTalkError):
    """Raised when configuration is invalid."""
    pass


class TimeoutError(ComputerTalkError):
    """Raised when an operation times out."""
    pass


class ValidationError(ComputerTalkError):
    """Raised when input validation fails."""
    pass
