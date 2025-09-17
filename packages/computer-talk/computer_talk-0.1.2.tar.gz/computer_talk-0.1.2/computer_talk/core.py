"""
Core functionality for computer communication.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from .exceptions import ComputerTalkError, CommunicationError


class ComputerTalk:
    """
    Main class for computer communication and interaction.
    
    This class provides the core functionality for establishing
    communication channels and sending/receiving messages.
    
    Can be used as a context manager for automatic cleanup.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ComputerTalk instance.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def start(self) -> None:
        """
        Start the communication system.
        
        Raises:
            ComputerTalkError: If already running or startup fails
        """
        if self.is_running:
            raise ComputerTalkError("ComputerTalk is already running")
            
        try:
            self.logger.info("Starting ComputerTalk...")
            # Initialize communication channels
            self._initialize_channels()
            self.is_running = True
            self.logger.info("ComputerTalk started successfully")
        except Exception as e:
            raise ComputerTalkError(f"Failed to start ComputerTalk: {e}")
            
    def stop(self) -> None:
        """
        Stop the communication system.
        
        Raises:
            ComputerTalkError: If not running or shutdown fails
        """
        if not self.is_running:
            raise ComputerTalkError("ComputerTalk is not running")
            
        try:
            self.logger.info("Stopping ComputerTalk...")
            # Clean up communication channels
            self._cleanup_channels()
            self.is_running = False
            self.logger.info("ComputerTalk stopped successfully")
        except Exception as e:
            raise ComputerTalkError(f"Failed to stop ComputerTalk: {e}")
            
    def send_message(self, message: str, **kwargs) -> str:
        """
        Send a message and get response.
        
        Args:
            message: The message to send
            **kwargs: Additional message parameters
            
        Returns:
            Response message
            
        Raises:
            CommunicationError: If communication fails
        """
        if not self.is_running:
            raise CommunicationError("ComputerTalk is not running")
            
        try:
            self.logger.debug(f"Sending message: {message}")
            # Simulate message processing
            response = self._process_message(message, **kwargs)
            self.logger.debug(f"Received response: {response}")
            return response
        except Exception as e:
            raise CommunicationError(f"Failed to send message: {e}")
            
    def _initialize_channels(self) -> None:
        """Initialize communication channels."""
        # Placeholder for channel initialization
        self.logger.debug("Initializing communication channels...")
        time.sleep(0.1)  # Simulate initialization time
        
    def _cleanup_channels(self) -> None:
        """Clean up communication channels."""
        # Placeholder for channel cleanup
        self.logger.debug("Cleaning up communication channels...")
        time.sleep(0.1)  # Simulate cleanup time
        
    def _process_message(self, message: str, **kwargs) -> str:
        """
        Process incoming message and generate response.
        
        Args:
            message: The message to process
            **kwargs: Additional parameters
            
        Returns:
            Processed response
        """
        # Simple echo response for demonstration
        if message.lower().startswith("hello"):
            return f"Hello! I received your message: {message}"
        elif message.lower().startswith("time"):
            return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        elif message.lower().startswith("status"):
            return f"Status: Running, uptime: {time.time():.2f} seconds"
        else:
            return f"Echo: {message}"
            
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status information.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "is_running": self.is_running,
            "config": self.config,
            "uptime": time.time() if self.is_running else 0,
        }
        
    def list_capabilities(self) -> List[str]:
        """
        List available capabilities.
        
        Returns:
            List of capability strings
        """
        return [
            "echo_messages",
            "time_queries", 
            "status_queries",
            "custom_responses",
        ]
        
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
