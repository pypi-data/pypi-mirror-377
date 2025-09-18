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
        
        # Add debug logging
        self.logger.debug(f"Processing message: '{message}'")
        
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
        elif message.lower().startswith("open ") or message.lower().startswith("pen ") or message.lower().startswith("ope "):
            # Handle app opening commands with intelligent parsing (including common typos)
            self.logger.debug(f"Processing open message: '{message}'")
            # Fix common typos
            if message.lower().startswith("pen "):
                message = "open " + message[4:]
            elif message.lower().startswith("ope "):
                message = "open " + message[4:]
            return self._handle_open_command(message)
        elif "send a message to " in message.lower() and (" saying " in message.lower() or self._is_likely_message_command(message)):
            # Handle direct message commands without "open"
            self.logger.debug(f"Processing direct message: '{message}'")
            return self._handle_direct_message_command(message)
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
        elif message.lower() == "list contacts" or message.lower().startswith("list contacts"):
            return "📱 To see your contacts, open the Messages app and check the sidebar. The contact name must match exactly as it appears in Messages (e.g., 'Enya Mistry' not 'Enya')."
        elif message.lower().startswith("find contact "):
            contact_name = message[13:].strip()
            return f"🔍 To find contact '{contact_name}':\n1. Open Messages app\n2. Look in the sidebar for exact name match\n3. Use the exact name as it appears there\n\nTip: Contact names are case-sensitive and must match exactly!"
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
            # Check for fuzzy matches to "open" command
            if self._is_likely_open_command(message):
                self.logger.debug(f"Detected likely open command: '{message}'")
                # Try to fix the command
                fixed_message = self._fix_open_command(message)
                if fixed_message:
                    return self._handle_open_command(fixed_message)
            
            return f"Echo: {message}"
    
    def _handle_open_command(self, message: str) -> str:
        """
        Handle 'open' commands with intelligent parsing.
        
        Args:
            message: The full message starting with 'open'
            
        Returns:
            Response string
        """
        # Remove 'open' prefix
        command = message[5:].strip()
        self.logger.debug(f"Processing open command: '{command}'")
        
        # Parse different types of open commands
        if " and send a message to " in command.lower() or " and send a message " in command.lower():
            self.logger.debug("Detected message command")
            return self._handle_open_and_message_command(command)
        elif " and " in command.lower():
            self.logger.debug("Detected action command")
            return self._handle_open_and_action_command(command)
        else:
            # Simple app opening - extract just the app name
            self.logger.debug("Detected simple app opening")
            app_name = self._extract_app_name(command)
            self.logger.debug(f"Extracted app name: '{app_name}'")
            try:
                result = self.open_app(app_name)
                return f"✅ {result['message']}"
            except Exception as e:
                return f"❌ Failed to open {app_name}: {e}"
    
    def _handle_open_and_message_command(self, command: str) -> str:
        """
        Handle commands like 'open messages and send a message to X that says Y'
        
        Args:
            command: The command after 'open'
            
        Returns:
            Response string
        """
        try:
            # Parse: "messages and send a message to enya mistry that says 'it works!'"
            # or "messages and send a message to enya saying it works!"
            if " and send a message to " in command.lower():
                parts = command.split(" and send a message to ")
            elif " and send a message " in command.lower():
                parts = command.split(" and send a message ")
            else:
                return f"❌ Could not parse message command: {command}"
            
            if len(parts) != 2:
                return f"❌ Could not parse message command: {command}"
            
            app_name = self._extract_app_name(parts[0].strip())
            message_part = parts[1].strip()
            
            # Extract recipient and message - handle both patterns
            if " that says " in message_part:
                recipient, message_text = message_part.split(" that says ", 1)
                recipient = recipient.strip()
                message_text = message_text.strip().strip("'\"")
            elif " saying " in message_part:
                recipient, message_text = message_part.split(" saying ", 1)
                recipient = recipient.strip()
                message_text = message_text.strip().strip("'\"")
            else:
                # Try to parse without "saying" - be smarter about recipient vs message
                words = message_part.split()
                if len(words) < 2:
                    return f"❌ Could not parse message: {message_part}"
                
                # Look for common patterns to separate recipient from message
                # If we have "Enya Mistry it works!", we want "Enya Mistry" as recipient and "it works!" as message
                if len(words) >= 3:
                    # Try to find where the message starts by looking for common message words
                    message_start = 0
                    for i, word in enumerate(words):
                        if word.lower() in ["it", "this", "that", "hello", "hi", "hey", "thanks", "thank"]:
                            message_start = i
                            break
                    
                    if message_start > 0:
                        recipient = " ".join(words[:message_start])
                        message_text = " ".join(words[message_start:])
                    else:
                        # Fallback: assume last word is message
                        recipient = " ".join(words[:-1])
                        message_text = words[-1]
                else:
                    # Only 2 words, assume first is recipient, second is message
                    recipient = words[0]
                    message_text = words[1]
            
            # Open the app first
            try:
                result = self.open_app(app_name)
                if not result.get('success'):
                    return f"❌ Failed to open {app_name}: {result.get('message', 'Unknown error')}"
            except Exception as e:
                return f"❌ Failed to open {app_name}: {e}"
            
            # Wait a moment for app to open
            import time
            time.sleep(2)
            
            # Send the message
            try:
                message_result = self._send_message_to_app(app_name, recipient, message_text)
                if message_result.get('success'):
                    return f"✅ Opened {app_name} and sent message to {recipient}: '{message_text}'"
                else:
                    return f"✅ Opened {app_name}, but failed to send message: {message_result.get('message', 'Unknown error')}"
            except Exception as e:
                return f"✅ Opened {app_name}, but failed to send message: {e}"
                
        except Exception as e:
            return f"❌ Failed to process message command: {e}"
    
    def _handle_open_and_action_command(self, command: str) -> str:
        """
        Handle commands like 'open app and do something'
        
        Args:
            command: The command after 'open'
            
        Returns:
            Response string
        """
        try:
            parts = command.split(" and ", 1)
            if len(parts) != 2:
                return f"❌ Could not parse action command: {command}"
            
            app_name = parts[0].strip()
            action = parts[1].strip()
            
            # Open the app first
            try:
                result = self.open_app(app_name)
                if not result.get('success'):
                    return f"❌ Failed to open {app_name}: {result.get('message', 'Unknown error')}"
            except Exception as e:
                return f"❌ Failed to open {app_name}: {e}"
            
            # Handle the action
            return f"✅ Opened {app_name}. Action '{action}' would be executed here."
            
        except Exception as e:
            return f"❌ Failed to process action command: {e}"
    
    def _handle_direct_message_command(self, message: str) -> str:
        """
        Handle direct message commands like 'send a message to X saying Y'
        
        Args:
            message: The full message
            
        Returns:
            Response string
        """
        try:
            # Parse: "send a message to enya saying it works!" or "send a message to enya it works!"
            if "send a message to " in message.lower():
                if " saying " in message.lower():
                    # Extract recipient and message with "saying"
                    parts = message.split(" saying ", 1)
                    if len(parts) != 2:
                        return f"❌ Could not parse direct message: {message}"
                    
                    recipient_part = parts[0].replace("send a message to ", "").strip()
                    message_text = parts[1].strip().strip("'\"")
                    recipient = recipient_part.strip()
                else:
                    # Extract recipient and message without "saying"
                    parts = message.split("send a message to ", 1)
                    if len(parts) != 2:
                        return f"❌ Could not parse direct message: {message}"
                    
                    after_send = parts[1].strip()
                    # Split into recipient and message
                    words = after_send.split()
                    if len(words) < 2:
                        return f"❌ Could not parse recipient and message: {after_send}"
                    
                    # Assume last word(s) are the message, rest is recipient
                    recipient = " ".join(words[:-1])
                    message_text = words[-1]
                
                # Open Messages app first
                try:
                    result = self.open_app("messages")
                    if not result.get('success'):
                        return f"❌ Failed to open Messages: {result.get('message', 'Unknown error')}"
                except Exception as e:
                    return f"❌ Failed to open Messages: {e}"
                
                # Wait a moment for app to open
                import time
                time.sleep(2)
                
                # Send the message
                try:
                    message_result = self._send_message_to_app("messages", recipient, message_text)
                    if message_result.get('success'):
                        return f"✅ Opened Messages and sent message to {recipient}: '{message_text}'"
                    else:
                        return f"✅ Opened Messages, but failed to send message: {message_result.get('message', 'Unknown error')}"
                except Exception as e:
                    return f"✅ Opened Messages, but failed to send message: {e}"
            else:
                return f"❌ Could not parse direct message command: {message}"
                
        except Exception as e:
            return f"❌ Failed to process direct message: {e}"
    
    def _is_likely_open_command(self, message: str) -> bool:
        """
        Check if a message is likely an "open" command with a typo.
        
        Args:
            message: The message to check
            
        Returns:
            True if likely an open command
        """
        message_lower = message.lower()
        
        # Check for common patterns that suggest an open command
        open_patterns = [
            "pen ", "ope ", "oen ", "opne ", "opn ", "op ", "oen ", "opne "
        ]
        
        for pattern in open_patterns:
            if message_lower.startswith(pattern):
                return True
        
        # Check if it contains app-related keywords
        app_keywords = ["messages", "safari", "chrome", "firefox", "terminal", "finder", "notes", "calendar"]
        if any(keyword in message_lower for keyword in app_keywords):
            # Check if it starts with something close to "open"
            first_word = message_lower.split()[0] if message_lower.split() else ""
            if len(first_word) >= 2 and first_word[:2] in ["op", "pe", "oe"]:
                return True
        
        return False
    
    def _fix_open_command(self, message: str) -> str:
        """
        Try to fix a message that looks like an open command.
        
        Args:
            message: The message to fix
            
        Returns:
            Fixed message or None if can't fix
        """
        message_lower = message.lower()
        
        # Common typo fixes
        typo_fixes = {
            "pen ": "open ",
            "ope ": "open ",
            "oen ": "open ",
            "opne ": "open ",
            "opn ": "open ",
            "op ": "open ",
        }
        
        for typo, fix in typo_fixes.items():
            if message_lower.startswith(typo):
                return fix + message[len(typo):]
        
        # If it contains app keywords but doesn't start with "open", try adding it
        app_keywords = ["messages", "safari", "chrome", "firefox", "terminal", "finder", "notes", "calendar"]
        if any(keyword in message_lower for keyword in app_keywords):
            first_word = message.split()[0] if message.split() else ""
            if len(first_word) >= 2 and first_word[:2] in ["op", "pe", "oe"]:
                return "open " + message[len(first_word):].lstrip()
        
        return None
    
    def _is_likely_message_command(self, message: str) -> bool:
        """
        Check if a message is likely a message command even without "saying".
        
        Args:
            message: The message to check
            
        Returns:
            True if likely a message command
        """
        message_lower = message.lower()
        
        # Check for message command patterns
        if "send a message to " in message_lower:
            # Check if it has a recipient and some text after
            parts = message_lower.split("send a message to ")
            if len(parts) > 1:
                after_send = parts[1].strip()
                # If there's text after the recipient, it's likely a message
                if len(after_send.split()) > 1:  # Has recipient + message
                    return True
        
        return False
    
    def _list_contacts(self) -> List[str]:
        """
        List contacts from the Messages app.
        
        Returns:
            List of contact names
        """
        try:
            import subprocess
            
            script = '''
            tell application "Messages"
                set targetService to first service whose service type = iMessage
                set buddyList to buddies of targetService
                set contactNames to {}
                repeat with buddy in buddyList
                    set end of contactNames to name of buddy
                end repeat
                return contactNames
            end tell
            '''
            
            result = subprocess.run(["osascript", "-e", script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse the AppleScript list output
                contacts = []
                for line in result.stdout.strip().split(','):
                    contact = line.strip().strip('"')
                    if contact:
                        contacts.append(contact)
                return contacts
            else:
                self.logger.warning(f"Failed to get contacts: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error listing contacts: {e}")
            return []
    
    def _extract_app_name(self, command: str) -> str:
        """
        Extract app name from a command string.
        
        Args:
            command: The command string
            
        Returns:
            Extracted app name
        """
        # Common patterns to extract app names
        command_lower = command.lower()
        
        # Handle special cases first
        message_commands = [
            "a message", "message", "messages", "send message", "new message",
            "compose message", "write message", "text message", "imessage",
            "my messages app", "messages app", "my message app", "message app"
        ]
        
        # Check if any message command is in the string
        for msg_cmd in message_commands:
            if msg_cmd in command_lower:
                return "Messages"
        
        # Also check for patterns like "my X app" where X contains "message"
        if "my" in command_lower and "app" in command_lower and "message" in command_lower:
            return "Messages"
        
        # Look for common app names
        app_patterns = [
            "messages", "message", "mail", "email", "safari", "chrome", "firefox",
            "terminal", "finder", "notes", "calendar", "slack", "discord", "zoom",
            "notion", "figma", "vscode", "code", "xcode", "photos", "preview",
            "spotify", "music", "itunes", "textedit", "pages", "numbers", "keynote"
        ]
        
        for pattern in app_patterns:
            if pattern in command_lower:
                return pattern.title() if pattern in ["vscode", "xcode"] else pattern.capitalize()
        
        # If no pattern matches, try to extract the first word
        words = command.split()
        if words:
            return words[0].capitalize()
        
        return command.strip()
    
    def _send_message_to_app(self, app_name: str, recipient: str, message: str) -> Dict[str, Any]:
        """
        Send a message through an app.
        
        Args:
            app_name: Name of the app to use
            recipient: Recipient of the message
            message: Message content
            
        Returns:
            Result dictionary
        """
        try:
            if app_name.lower() in ["messages", "message"]:
                return self._send_imessage(recipient, message)
            elif app_name.lower() in ["slack"]:
                return self._send_slack_message(recipient, message)
            elif app_name.lower() in ["discord"]:
                return self._send_discord_message(recipient, message)
            else:
                return {
                    "success": False,
                    "message": f"Message sending not supported for {app_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send message: {e}"
            }
    
    def _send_imessage(self, recipient: str, message: str) -> Dict[str, Any]:
        """Send an iMessage using AppleScript."""
        try:
            import subprocess
            
            # Escape special characters for AppleScript
            def escape_applescript(text):
                return text.replace('"', '\\"').replace('\\', '\\\\')
            
            escaped_recipient = escape_applescript(recipient)
            escaped_message = escape_applescript(message)
            
            # Use UI method which is more forgiving with contact names
            script_api = f'''
            tell application "Messages"
                activate
                delay 2
                tell application "System Events"
                    keystroke "n" using command down
                    delay 2
                    keystroke "{escaped_recipient}"
                    delay 1
                    keystroke return
                    delay 3
                    keystroke tab
                    delay 1
                    keystroke "{escaped_message}"
                    delay 1
                    keystroke return
                end tell
            end tell
            '''
            
            result = subprocess.run(["osascript", "-e", script_api], 
                                  capture_output=True, text=True, timeout=30)
            
            self.logger.debug(f"Messages API result: returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "iMessage sent via API",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            # Fallback to UI automation if API fails
            self.logger.warning("Messages API failed, trying UI automation fallback")
            script_ui = f'''
            tell application "Messages"
                activate
                delay 2
                tell application "System Events"
                    keystroke "n" using command down
                    delay 2
                    keystroke "{escaped_recipient}"
                    delay 1
                    keystroke return
                    delay 3
                    keystroke tab
                    delay 1
                    keystroke "{escaped_message}"
                    delay 1
                    keystroke return
                end tell
            end tell
            '''
            
            result = subprocess.run(["osascript", "-e", script_ui], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "iMessage sent successfully",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to send iMessage. This might be because the contact '{recipient}' doesn't exist in your Messages app. Try using 'list contacts' to see available contacts, or use the exact name as it appears in Messages.",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send iMessage: {e}"
            }
    
    def _send_slack_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """Send a Slack message (placeholder)."""
        return {
            "success": False,
            "message": "Slack integration not yet implemented"
        }
    
    def _send_discord_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """Send a Discord message (placeholder)."""
        return {
            "success": False,
            "message": "Discord integration not yet implemented"
        }
            
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
