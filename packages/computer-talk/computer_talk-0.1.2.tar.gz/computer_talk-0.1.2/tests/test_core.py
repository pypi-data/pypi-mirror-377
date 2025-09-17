"""
Tests for the core ComputerTalk functionality.
"""

import pytest
import time
from computer_talk.core import ComputerTalk
from computer_talk.exceptions import ComputerTalkError, CommunicationError


class TestComputerTalk:
    """Test cases for ComputerTalk class."""
    
    def test_init_default(self):
        """Test initialization with default config."""
        talk = ComputerTalk()
        assert talk.config == {}
        assert not talk.is_running
        
    def test_init_with_config(self):
        """Test initialization with custom config."""
        config = {"log_level": "DEBUG", "timeout": 30}
        talk = ComputerTalk(config)
        assert talk.config == config
        assert not talk.is_running
        
    def test_start_stop(self):
        """Test starting and stopping the system."""
        talk = ComputerTalk()
        
        # Should not be running initially
        assert not talk.is_running
        
        # Start the system
        talk.start()
        assert talk.is_running
        
        # Stop the system
        talk.stop()
        assert not talk.is_running
        
    def test_start_when_already_running(self):
        """Test starting when already running raises error."""
        talk = ComputerTalk()
        talk.start()
        
        with pytest.raises(ComputerTalkError, match="already running"):
            talk.start()
            
    def test_stop_when_not_running(self):
        """Test stopping when not running raises error."""
        talk = ComputerTalk()
        
        with pytest.raises(ComputerTalkError, match="not running"):
            talk.stop()
            
    def test_send_message_when_not_running(self):
        """Test sending message when not running raises error."""
        talk = ComputerTalk()
        
        with pytest.raises(CommunicationError, match="not running"):
            talk.send_message("test")
            
    def test_send_message_hello(self):
        """Test sending hello message."""
        talk = ComputerTalk()
        talk.start()
        
        try:
            response = talk.send_message("hello world")
            assert "Hello!" in response
            assert "hello world" in response
        finally:
            talk.stop()
            
    def test_send_message_time(self):
        """Test sending time message."""
        talk = ComputerTalk()
        talk.start()
        
        try:
            response = talk.send_message("time")
            assert "Current time:" in response
        finally:
            talk.stop()
            
    def test_send_message_status(self):
        """Test sending status message."""
        talk = ComputerTalk()
        talk.start()
        
        try:
            response = talk.send_message("status")
            assert "Status:" in response
            assert "Running" in response
        finally:
            talk.stop()
            
    def test_send_message_echo(self):
        """Test sending echo message."""
        talk = ComputerTalk()
        talk.start()
        
        try:
            message = "test echo message"
            response = talk.send_message(message)
            assert f"Echo: {message}" == response
        finally:
            talk.stop()
            
    def test_get_status(self):
        """Test getting status information."""
        talk = ComputerTalk({"test": "value"})
        
        # Status when not running
        status = talk.get_status()
        assert status["is_running"] is False
        assert status["config"] == {"test": "value"}
        assert status["uptime"] == 0
        
        # Status when running
        talk.start()
        try:
            status = talk.get_status()
            assert status["is_running"] is True
            assert status["config"] == {"test": "value"}
            assert status["uptime"] > 0
        finally:
            talk.stop()
            
    def test_list_capabilities(self):
        """Test listing capabilities."""
        talk = ComputerTalk()
        capabilities = talk.list_capabilities()
        
        expected_capabilities = [
            "echo_messages",
            "time_queries", 
            "status_queries",
            "custom_responses",
        ]
        
        assert capabilities == expected_capabilities
        
    def test_context_manager_usage(self):
        """Test using ComputerTalk as context manager."""
        with ComputerTalk() as talk:
            assert talk.is_running
            response = talk.send_message("hello")
            assert "Hello!" in response
            
        # Should be stopped after context
        assert not talk.is_running
        
    def test_multiple_start_stop_cycles(self):
        """Test multiple start/stop cycles."""
        talk = ComputerTalk()
        
        for _ in range(3):
            talk.start()
            assert talk.is_running
            talk.stop()
            assert not talk.is_running
