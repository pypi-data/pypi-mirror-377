"""
Tests for custom exceptions.
"""

import pytest
from computer_talk.exceptions import (
    ComputerTalkError,
    CommunicationError,
    ConfigurationError,
    TimeoutError,
    ValidationError,
)


class TestExceptions:
    """Test cases for custom exceptions."""
    
    def test_computer_talk_error_inheritance(self):
        """Test that all exceptions inherit from ComputerTalkError."""
        assert issubclass(CommunicationError, ComputerTalkError)
        assert issubclass(ConfigurationError, ComputerTalkError)
        assert issubclass(TimeoutError, ComputerTalkError)
        assert issubclass(ValidationError, ComputerTalkError)
        
    def test_computer_talk_error_creation(self):
        """Test creating ComputerTalkError."""
        error = ComputerTalkError("test message")
        assert str(error) == "test message"
        
    def test_communication_error_creation(self):
        """Test creating CommunicationError."""
        error = CommunicationError("communication failed")
        assert str(error) == "communication failed"
        assert isinstance(error, ComputerTalkError)
        
    def test_configuration_error_creation(self):
        """Test creating ConfigurationError."""
        error = ConfigurationError("invalid config")
        assert str(error) == "invalid config"
        assert isinstance(error, ComputerTalkError)
        
    def test_timeout_error_creation(self):
        """Test creating TimeoutError."""
        error = TimeoutError("operation timed out")
        assert str(error) == "operation timed out"
        assert isinstance(error, ComputerTalkError)
        
    def test_validation_error_creation(self):
        """Test creating ValidationError."""
        error = ValidationError("validation failed")
        assert str(error) == "validation failed"
        assert isinstance(error, ComputerTalkError)
        
    def test_exception_chaining(self):
        """Test exception chaining."""
        try:
            try:
                raise ValueError("original error")
            except ValueError as e:
                raise CommunicationError("communication failed") from e
        except CommunicationError as e:
            assert str(e) == "communication failed"
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "original error"
