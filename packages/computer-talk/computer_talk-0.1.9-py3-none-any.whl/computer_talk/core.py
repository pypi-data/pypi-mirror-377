"""
Core functionality for computer communication.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from .exceptions import ComputerTalkError, CommunicationError
from .config import get_task_description
from .desktop import DesktopManager


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
        self.desktop = DesktopManager()
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
        # Get user's task description
        task_description = get_task_description()
        
        # Simple echo response for demonstration
        if message.lower().startswith("hello"):
            return f"Hello! I received your message: {message}"
        elif message.lower().startswith("time"):
            return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        elif message.lower().startswith("status"):
            return f"Status: Running, uptime: {time.time():.2f} seconds"
        elif message.lower().startswith("task"):
            if task_description:
                return f"Your current task: {task_description}"
            else:
                return "No task description set. Run 'computer-talk --interactive' to set one."
        elif message.lower().startswith("clear task"):
            from .config import set_task_description
            set_task_description("")
            return "✅ Task cleared. You can set a new one anytime."
        elif message.lower().startswith("open "):
            # Handle app opening commands
            app_name = message[5:].strip()
            try:
                result = self.open_app(app_name)
                return f"✅ {result['message']}"
            except Exception as e:
                return f"❌ Failed to open {app_name}: {e}"
        elif message.lower() == "list apps" or message.lower().startswith("list apps"):
            try:
                apps = self.list_apps()
                if apps:
                    app_list = "\n".join([f"• {app['name']}: {app['description']}" for app in apps[:10]])
                    return f"Available apps:\n{app_list}\n\n(Showing first 10 apps)"
                else:
                    return "No apps available"
            except Exception as e:
                return f"❌ Failed to list apps: {e}"
        elif message.lower() == "running apps" or message.lower().startswith("running apps"):
            try:
                apps = self.list_running_apps()
                if apps:
                    app_list = "\n".join([f"• {app['name']}" for app in apps[:10]])
                    return f"Running apps:\n{app_list}\n\n(Showing first 10 apps)"
                else:
                    return "No running apps detected"
            except Exception as e:
                return f"❌ Failed to list running apps: {e}"
        elif message.lower().startswith("close "):
            # Handle app closing commands
            app_name = message[6:].strip()
            try:
                result = self.interact_with_app(app_name, "quit")
                return f"✅ {result['message']}"
            except Exception as e:
                return f"❌ Failed to close {app_name}: {e}"
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
            "desktop_apps",
            "app_control",
        ]
        
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def open_app(self, app_name: str, **kwargs) -> Dict[str, Any]:
        """
        Open a desktop application.
        
        Args:
            app_name: Name of the application to open
            **kwargs: Additional arguments
            
        Returns:
            Result of opening the application
        """
        if not self.is_running:
            raise CommunicationError("ComputerTalk is not running")
        
        try:
            return self.desktop.open_application(app_name, **kwargs)
        except Exception as e:
            raise CommunicationError(f"Failed to open {app_name}: {e}")
    
    def list_apps(self) -> List[Dict[str, Any]]:
        """
        List available applications.
        
        Returns:
            List of available applications
        """
        if not self.is_running:
            raise CommunicationError("ComputerTalk is not running")
        
        try:
            return self.desktop.get_common_apps()
        except Exception as e:
            raise CommunicationError(f"Failed to list apps: {e}")
    
    def list_running_apps(self) -> List[Dict[str, Any]]:
        """
        List currently running applications.
        
        Returns:
            List of running applications
        """
        if not self.is_running:
            raise CommunicationError("ComputerTalk is not running")
        
        try:
            return self.desktop.list_running_apps()
        except Exception as e:
            raise CommunicationError(f"Failed to list running apps: {e}")
    
    def interact_with_app(self, app_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Interact with a running application.
        
        Args:
            app_name: Name of the application
            action: Action to perform (activate, close, quit, minimize, maximize)
            **kwargs: Additional parameters
            
        Returns:
            Result of the interaction
        """
        if not self.is_running:
            raise CommunicationError("ComputerTalk is not running")
        
        try:
            return self.desktop.interact_with_app(app_name, action, **kwargs)
        except Exception as e:
            raise CommunicationError(f"Failed to interact with {app_name}: {e}")
    
    def close_app(self, app_id: str) -> Dict[str, Any]:
        """
        Close a tracked application.
        
        Args:
            app_id: ID of the application to close
            
        Returns:
            Result of closing the application
        """
        if not self.is_running:
            raise CommunicationError("ComputerTalk is not running")
        
        try:
            return self.desktop.close_app(app_id)
        except Exception as e:
            raise CommunicationError(f"Failed to close app {app_id}: {e}")
