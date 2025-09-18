"""
Desktop application integration for computer-talk.
Provides capabilities to open and interact with desktop applications.
"""

import subprocess
import platform
import time
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json

from .exceptions import ComputerTalkError, CommunicationError


class DesktopManager:
    """
    Manages desktop application interactions and control.
    """
    
    def __init__(self):
        """Initialize the desktop manager."""
        self.system = platform.system().lower()
        self.logger = logging.getLogger(__name__)
        self.running_apps = {}
        
    def open_application(self, app_name: str, **kwargs) -> Dict[str, Any]:
        """
        Open a desktop application.
        
        Args:
            app_name: Name or path of the application to open
            **kwargs: Additional arguments for the application
            
        Returns:
            Dictionary with app info and status
            
        Raises:
            ComputerTalkError: If app cannot be opened
        """
        try:
            self.logger.info(f"Opening application: {app_name}")
            
            if self.system == "darwin":  # macOS
                result = self._open_macos_app(app_name, **kwargs)
            elif self.system == "windows":
                result = self._open_windows_app(app_name, **kwargs)
            elif self.system == "linux":
                result = self._open_linux_app(app_name, **kwargs)
            else:
                raise ComputerTalkError(f"Unsupported operating system: {self.system}")
            
            # Store app info
            app_id = f"{app_name}_{int(time.time())}"
            self.running_apps[app_id] = {
                "name": app_name,
                "pid": result.get("pid"),
                "started_at": time.time(),
                "status": "running"
            }
            
            return {
                "success": True,
                "app_id": app_id,
                "app_name": app_name,
                "pid": result.get("pid"),
                "message": f"Successfully opened {app_name}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to open {app_name}: {e}")
            raise ComputerTalkError(f"Failed to open application {app_name}: {e}")
    
    def _open_macos_app(self, app_name: str, **kwargs) -> Dict[str, Any]:
        """Open application on macOS."""
        # Try different approaches for macOS
        commands = [
            # Direct app name
            ["open", "-a", app_name],
            # App bundle path
            ["open", app_name],
            # Using osascript
            ["osascript", "-e", f'tell application "{app_name}" to activate']
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return {"pid": None, "command": cmd}
            except subprocess.TimeoutExpired:
                continue
            except Exception:
                continue
        
        raise ComputerTalkError(f"Could not open {app_name} on macOS")
    
    def _open_windows_app(self, app_name: str, **kwargs) -> Dict[str, Any]:
        """Open application on Windows."""
        try:
            # Try to start the application
            result = subprocess.run(
                ["start", app_name], 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return {"pid": None, "command": ["start", app_name]}
        except Exception as e:
            raise ComputerTalkError(f"Could not open {app_name} on Windows: {e}")
    
    def _open_linux_app(self, app_name: str, **kwargs) -> Dict[str, Any]:
        """Open application on Linux."""
        try:
            # Try different approaches for Linux
            commands = [
                [app_name],
                ["xdg-open", app_name],
                ["gnome-open", app_name],
                ["kde-open", app_name]
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {"pid": result.pid, "command": cmd}
                except FileNotFoundError:
                    continue
            
            raise ComputerTalkError(f"Could not open {app_name} on Linux")
        except Exception as e:
            raise ComputerTalkError(f"Could not open {app_name} on Linux: {e}")
    
    def list_running_apps(self) -> List[Dict[str, Any]]:
        """
        List currently running applications.
        
        Returns:
            List of running application information
        """
        try:
            if self.system == "darwin":
                return self._list_macos_apps()
            elif self.system == "windows":
                return self._list_windows_apps()
            elif self.system == "linux":
                return self._list_linux_apps()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to list apps: {e}")
            return []
    
    def _list_macos_apps(self) -> List[Dict[str, Any]]:
        """List running apps on macOS."""
        try:
            result = subprocess.run(
                ["osascript", "-e", "tell application \"System Events\" to get name of every process"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                apps = [app.strip() for app in result.stdout.split(",")]
                return [{"name": app, "system": "macOS"} for app in apps if app]
            return []
        except Exception:
            return []
    
    def _list_windows_apps(self) -> List[Dict[str, Any]]:
        """List running apps on Windows."""
        try:
            result = subprocess.run(
                ["tasklist", "/fo", "csv"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                apps = []
                for line in lines:
                    parts = line.split(',')
                    if len(parts) >= 1:
                        app_name = parts[0].strip('"')
                        apps.append({"name": app_name, "system": "Windows"})
                return apps
            return []
        except Exception:
            return []
    
    def _list_linux_apps(self) -> List[Dict[str, Any]]:
        """List running apps on Linux."""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                apps = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 11:
                        app_name = parts[10]
                        if not app_name.startswith('['):  # Skip kernel processes
                            apps.append({"name": app_name, "system": "Linux"})
                return apps
            return []
        except Exception:
            return []
    
    def discover_apps(self) -> List[Dict[str, Any]]:
        """
        Dynamically discover applications installed on the system.
        
        Returns:
            List of discovered applications with their names and descriptions
        """
        try:
            if self.system == "darwin":
                return self._discover_macos_apps()
            elif self.system == "windows":
                return self._discover_windows_apps()
            elif self.system == "linux":
                return self._discover_linux_apps()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to discover apps: {e}")
            return []
    
    def _discover_macos_apps(self) -> List[Dict[str, Any]]:
        """Discover macOS applications from /Applications directory."""
        apps = []
        try:
            # Get applications from /Applications
            import os
            applications_dir = "/Applications"
            if os.path.exists(applications_dir):
                for item in os.listdir(applications_dir):
                    if item.endswith('.app'):
                        app_name = item[:-4]  # Remove .app extension
                        app_path = os.path.join(applications_dir, item)
                        
                        # Get app info
                        info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
                        description = self._get_app_description(info_plist_path, app_name)
                        
                        apps.append({
                            "name": app_name,
                            "description": description,
                            "path": app_path,
                            "command": app_name
                        })
            
            # Also check user applications
            user_apps_dir = os.path.expanduser("~/Applications")
            if os.path.exists(user_apps_dir):
                for item in os.listdir(user_apps_dir):
                    if item.endswith('.app'):
                        app_name = item[:-4]
                        app_path = os.path.join(user_apps_dir, item)
                        
                        info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
                        description = self._get_app_description(info_plist_path, app_name)
                        
                        apps.append({
                            "name": app_name,
                            "description": description,
                            "path": app_path,
                            "command": app_name
                        })
            
            self.logger.info(f"Discovered {len(apps)} macOS applications")
            return apps
            
        except Exception as e:
            self.logger.error(f"Failed to discover macOS apps: {e}")
            return []
    
    def _get_app_description(self, info_plist_path: str, app_name: str) -> str:
        """Get app description from Info.plist or generate one."""
        try:
            import plistlib
            if os.path.exists(info_plist_path):
                with open(info_plist_path, 'rb') as f:
                    plist = plistlib.load(f)
                    description = plist.get('CFBundleShortVersionString', '')
                    if description:
                        return f"{app_name} {description}"
            
            # Fallback to generic description based on app name
            return self._generate_app_description(app_name)
        except Exception:
            return self._generate_app_description(app_name)
    
    def _generate_app_description(self, app_name: str) -> str:
        """Generate a description based on app name."""
        descriptions = {
            'Safari': 'Web browser',
            'Chrome': 'Web browser', 
            'Firefox': 'Web browser',
            'Terminal': 'Command line terminal',
            'Finder': 'File manager',
            'TextEdit': 'Text editor',
            'Notes': 'Note-taking app',
            'Calendar': 'Calendar app',
            'Mail': 'Email client',
            'Messages': 'Messaging app',
            'Spotify': 'Music streaming',
            'VSCode': 'Code editor',
            'Visual Studio Code': 'Code editor',
            'Xcode': 'iOS development',
            'Photos': 'Photo management',
            'Preview': 'PDF and image viewer',
            'Notion': 'Note-taking and productivity',
            'Slack': 'Team communication',
            'Discord': 'Voice and text chat',
            'Zoom': 'Video conferencing',
            'Figma': 'Design tool',
            'PyCharm': 'Python IDE',
            'IntelliJ IDEA': 'Java IDE',
            'WebStorm': 'JavaScript IDE',
            'DataGrip': 'Database IDE',
            'Android Studio': 'Android development',
            'Xcode': 'iOS development',
            'iTerm': 'Terminal emulator',
            'Alacritty': 'Terminal emulator',
            'Hyper': 'Terminal emulator',
            'Docker Desktop': 'Container platform',
            'Postman': 'API development',
            'Insomnia': 'API client',
            'TablePlus': 'Database client',
            'Sequel Pro': 'MySQL client',
            'Navicat': 'Database client',
            'MongoDB Compass': 'MongoDB client',
            'Redis Desktop Manager': 'Redis client',
            'DBeaver': 'Database client',
            'MySQL Workbench': 'MySQL client',
            'pgAdmin': 'PostgreSQL client',
            'Robo 3T': 'MongoDB client',
            'Studio 3T': 'MongoDB client',
            'MongoDB Compass': 'MongoDB client',
            'Redis Desktop Manager': 'Redis client',
            'DBeaver': 'Database client',
            'MySQL Workbench': 'MySQL client',
            'pgAdmin': 'PostgreSQL client',
            'Robo 3T': 'MongoDB client',
            'Studio 3T': 'MongoDB client'
        }
        
        return descriptions.get(app_name, f"{app_name} application")
    
    def _discover_windows_apps(self) -> List[Dict[str, Any]]:
        """Discover Windows applications."""
        # Windows app discovery would go here
        return []
    
    def _discover_linux_apps(self) -> List[Dict[str, Any]]:
        """Discover Linux applications."""
        # Linux app discovery would go here
        return []
    
    def get_common_apps(self) -> List[Dict[str, Any]]:
        """
        Get list of discovered applications.
        
        Returns:
            List of discovered applications with their names and descriptions
        """
        return self.discover_apps()
    
    def interact_with_app(self, app_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Interact with a running application.
        
        Args:
            app_name: Name of the application
            action: Action to perform
            **kwargs: Additional parameters
            
        Returns:
            Result of the interaction
        """
        try:
            self.logger.info(f"Interacting with {app_name}: {action}")
            
            if self.system == "darwin":
                return self._interact_macos_app(app_name, action, **kwargs)
            elif self.system == "windows":
                return self._interact_windows_app(app_name, action, **kwargs)
            elif self.system == "linux":
                return self._interact_linux_app(app_name, action, **kwargs)
            else:
                raise ComputerTalkError(f"Unsupported operating system: {self.system}")
                
        except Exception as e:
            self.logger.error(f"Failed to interact with {app_name}: {e}")
            raise CommunicationError(f"Failed to interact with {app_name}: {e}")
    
    def _interact_macos_app(self, app_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """Interact with macOS application using AppleScript."""
        actions = {
            "activate": f'tell application "{app_name}" to activate',
            "close": f'tell application "{app_name}" to close',
            "quit": f'tell application "{app_name}" to quit',
            "minimize": f'tell application "{app_name}" to set minimized of window 1 to true',
            "maximize": f'tell application "{app_name}" to set zoomed of window 1 to true'
        }
        
        if action not in actions:
            raise ComputerTalkError(f"Unknown action: {action}")
        
        try:
            result = subprocess.run(
                ["osascript", "-e", actions[action]],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return {"success": True, "action": action, "result": result.stdout.strip()}
            else:
                return {"success": False, "action": action, "error": result.stderr.strip()}
        except Exception as e:
            raise ComputerTalkError(f"Failed to execute action {action}: {e}")
    
    def _interact_windows_app(self, app_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """Interact with Windows application."""
        # Windows interaction would require more complex automation
        # For now, return a basic response
        return {"success": True, "action": action, "message": f"Action {action} on {app_name} (Windows)"}
    
    def _interact_linux_app(self, app_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """Interact with Linux application."""
        # Linux interaction would require X11/Wayland automation
        # For now, return a basic response
        return {"success": True, "action": action, "message": f"Action {action} on {app_name} (Linux)"}
    
    def get_app_status(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a tracked application.
        
        Args:
            app_id: ID of the application
            
        Returns:
            Application status or None if not found
        """
        return self.running_apps.get(app_id)
    
    def close_app(self, app_id: str) -> Dict[str, Any]:
        """
        Close a tracked application.
        
        Args:
            app_id: ID of the application
            
        Returns:
            Result of closing the application
        """
        if app_id not in self.running_apps:
            raise ComputerTalkError(f"Application {app_id} not found")
        
        app_info = self.running_apps[app_id]
        app_name = app_info["name"]
        
        try:
            result = self.interact_with_app(app_name, "quit")
            self.running_apps[app_id]["status"] = "closed"
            return result
        except Exception as e:
            self.logger.error(f"Failed to close {app_name}: {e}")
            return {"success": False, "error": str(e)}
