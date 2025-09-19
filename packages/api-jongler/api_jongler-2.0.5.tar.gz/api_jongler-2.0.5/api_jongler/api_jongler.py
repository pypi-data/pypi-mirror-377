"""
Main APIJongler class for managing multiple API keys and connections
"""

import os
import json
import logging
import configparser
import requests
import glob
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from colorama import init

from .colored_formatter import ColoredFormatter
from .api_connector import APIConnector

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class APIJongler:
    """Main APIJongler class for managing multiple API keys and connections"""
    
    def __init__(self, api_connector_name: str, is_tor_enabled: Optional[bool] = False):
        """
        Initialize APIJongler
        
        Args:
            api_connector_name: Name of the API connector to use
            is_tor_enabled: Whether to use Tor for requests (optional)
        """
        self._api_connector_name = api_connector_name
        self._is_tor_enabled = is_tor_enabled
        self._api_connector = None
        self._current_api_key = None
        self._current_api_key_name = None
        self._session = None
        self._lock_file_path = None
        self._lockdown_file_path = None
        self._logger = None
        self._tried_keys_in_connection = set()  # Track keys tried in current connection
        self._timeout = self._resolveTimeout()  # Configurable request timeout
        
        # Set up logging
        self._setupLogging()
        # In some test/mocked scenarios logging infrastructure may be replaced; guard against None
        if self._logger is not None:
            self._logger.debug(f"Request timeout set to {self._timeout} seconds")
        
        # Connect to the API
        self._connect(api_connector_name, is_tor_enabled)

    @property
    def ApiConnectorName(self) -> str:
        """Get the API connector name"""
        return self._api_connector_name

    @property
    def IsTorEnabled(self) -> bool:
        """Get whether Tor is enabled"""
        return self._is_tor_enabled

    @property
    def ApiConnector(self) -> Optional[APIConnector]:
        """Get the API connector instance"""
        return self._api_connector

    @property
    def CurrentApiKey(self) -> Optional[str]:
        """Get the current API key"""
        return self._current_api_key

    @property
    def Session(self) -> Optional[requests.Session]:
        """Get the requests session"""
        return self._session

    @property
    def LockFilePath(self) -> Optional[Path]:
        """Get the lock file path"""
        return self._lock_file_path

    @property
    def Logger(self) -> Optional[logging.Logger]:
        """Get the logger instance"""
        return self._logger
        
    @property
    def Timeout(self) -> float:
        """Get the request timeout"""
        return self._timeout

    def _resolveTimeout(self) -> float:
        """Resolve request timeout from environment (APIJONGLER_TIMEOUT) or default to 60 seconds."""
        val = os.getenv("APIJONGLER_TIMEOUT", "").strip()
        if not val:
            return 60.0
        try:
            timeout = float(val)
            if timeout <= 0:
                raise ValueError
            return timeout
        except Exception:
            return 60.0
    
    def _setupLogging(self) -> None:
        """Set up logging configuration"""
        log_level = os.getenv('APIJONGLER_LOG_LEVEL', 'INFO').upper()
        log_format = '%(timestamp)s - %(funcName)s - %(levelname)s - %(message)s'
        
        # Create logger
        self._logger = logging.getLogger('APIJongler')
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter(log_format)
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        # File handler without colors
        log_dir = Path.home() / '.api_jongler' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'api_jongler.log'
        
        file_handler = logging.FileHandler(log_file)
        file_formatter = ColoredFormatter(log_format)
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        
        # Add colored attribute for console output
        for handler in self._logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream.name == '<stderr>':
                handler.addFilter(lambda record: setattr(record, 'colored', True) or True)
        
    def _connect(self, api_connector_name: str, is_tor_enabled: bool) -> None:
        """
        Connect to the API service
        
        Args:
            api_connector_name: Name of the API connector
            is_tor_enabled: Whether to use Tor connection
        """
        self._logger.info(f"Connecting to API connector: {api_connector_name}")
        
        # Load API connector configuration
        self._api_connector = self._loadApiConnector(api_connector_name)
        
        # Set up Tor connection if enabled
        if is_tor_enabled:
            self._setupTorConnection()
        else:
            self._session = requests.Session()
        
        # Get available API keys and select one
        if not self._selectApiKey():
            raise RuntimeError("No API keys available for initial connection")
        
        self._logger.info(f"Successfully connected to {api_connector_name}")
    
    def _loadApiConnector(self, connector_name: str) -> APIConnector:
        """Load API connector configuration from JSON file"""
        # Get the package directory
        package_dir = Path(__file__).parent
        connector_file = package_dir / 'connectors' / f'{connector_name}.json'
        
        if not connector_file.exists():
            raise FileNotFoundError(f"API connector configuration not found: {connector_file}")
        
        try:
            with open(connector_file, 'r') as f:
                config_data = json.load(f)
            return APIConnector(config_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in connector file {connector_file}: {e}")
    
    def _setupTorConnection(self) -> None:
        """Set up Tor connection for requests"""
        self._logger.info("Setting up Tor connection")
        
        self._session = requests.Session()
        
        # Configure Tor proxy (default Tor SOCKS proxy)
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        self._session.proxies.update(proxies)
        
        # Test Tor connection
        try:
            response = self._session.get('https://httpbin.org/ip', timeout=60)
            self._logger.info(f"Tor connection established. IP: {response.json().get('origin', 'unknown')}")
        except Exception as e:
            self._logger.warning(f"Could not verify Tor connection: {e}")
    
    def _getLockDirectory(self) -> Path:
        """Get the lock directory path"""
        lock_dir = Path.home() / '.api_jongler' / 'locks'
        lock_dir.mkdir(parents=True, exist_ok=True)
        return lock_dir
    
    def _getConfigFilePath(self) -> str:
        """Get the configuration file path from environment variable"""
        config_path = os.getenv('APIJONGLER_CONFIG')
        if not config_path:
            raise ValueError("APIJONGLER_CONFIG environment variable not set")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        return config_path
    
    def _getApiKeys(self) -> Dict[str, str]:
        """Get API keys from configuration file"""
        config_path = self._getConfigFilePath()
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if self._api_connector_name not in config:
            error_message = self._generateNoKeysErrorMessage({}, set())
            raise ValueError(error_message)
        
        return dict(config[self._api_connector_name])
    
    def _getKeyStates(self) -> Dict[str, set]:
        """Get sets of API keys organized by their current state"""
        lock_dir = self._getLockDirectory()
        
        # Get locked keys
        lock_files = glob.glob(str(lock_dir / f"{self._api_connector_name}_*.lock"))
        locked_keys = {Path(f).stem.replace(f"{self._api_connector_name}_", "") for f in lock_files}
        
        # Get lockdown keys
        lockdown_files = glob.glob(str(lock_dir / f"{self._api_connector_name}_*.lockdown"))
        lockdown_keys = {Path(f).stem.replace(f"{self._api_connector_name}_", "") for f in lockdown_files}
        
        # Get error keys (maintaining compatibility)
        error_files = glob.glob(str(lock_dir / f"{self._api_connector_name}_*.error"))
        error_keys = {Path(f).stem.replace(f"{self._api_connector_name}_", "") for f in error_files}
        
        # Get all configured keys
        api_keys = self._getApiKeys()
        all_keys = set(api_keys.keys())
        
        # Vacant keys are those not in any other state
        vacant_keys = all_keys - locked_keys - lockdown_keys - error_keys
        
        return {
            'vacant': vacant_keys,
            'locked': locked_keys,
            'lockdown': lockdown_keys,
            'error': error_keys
        }
    
    def _getLockedAndErrorKeys(self) -> set:
        """Get set of API keys that are locked or have errors (legacy method for compatibility)"""
        states = self._getKeyStates()
        unavailable_keys = states['locked'] | states['error']
        
        if unavailable_keys:
            self._logger.debug(f"Unavailable keys: {unavailable_keys}")
        
        return unavailable_keys

    def _generateNoKeysErrorMessage(self, api_keys: Dict[str, str], unavailable_keys: set) -> str:
        """Generate a meaningful error message when no API keys are available"""
        total_keys = len(api_keys)
        locked_files = glob.glob(str(self._getLockDirectory() / f"{self._api_connector_name}_*.lock"))
        error_files = glob.glob(str(self._getLockDirectory() / f"{self._api_connector_name}_*.error"))
        
        if total_keys == 0:
            return (
                f"❌ No API keys configured for '{self._api_connector_name}'.\n\n"
                f"📝 Please add API keys to your configuration file:\n"
                f"   Environment variable: APIJONGLER_CONFIG\n"
                f"   Current config path: {os.getenv('APIJONGLER_CONFIG', 'Not set')}\n\n"
                f"📋 Configuration format:\n"
                f"   [{self._api_connector_name}]\n"
                f"   key1 = your-api-key-1\n"
                f"   key2 = your-api-key-2\n"
                f"   key3 = your-api-key-3\n\n"
                f"💡 Then restart your application."
            )
        
        locked_count = len(locked_files)
        error_count = len(error_files)
        
        message = (
            f"❌ All API keys for '{self._api_connector_name}' are currently unavailable.\n\n"
            f"📊 Status summary:\n"
            f"   • Total keys: {total_keys}\n"
            f"   • Locked keys: {locked_count}\n"
            f"   • Error keys: {error_count}\n"
            f"   • Available keys: 0\n\n"
        )
        
        if locked_count > 0:
            message += (
                f"🔓 To unlock all keys for this connector:\n"
                f"   python -m api_jongler --cleanup {self._api_connector_name}\n\n"
                f"🔓 To unlock all keys for all connectors:\n"
                f"   python -m api_jongler --cleanup-all\n\n"
            )
        
        if error_count > 0:
            message += (
                f"🚨 Some keys are in error state. Clear errors with the cleanup commands above.\n\n"
            )
        
        message += (
            f"🔍 Lock/error files location:\n"
            f"   {self._getLockDirectory()}\n\n"
            f"💡 You can also manually remove lock files if needed."
        )
        
        return message
    
    def _setKeyState(self, key_name: str, state: str) -> None:
        """Set the state of an API key by creating/removing appropriate files"""
        lock_dir = self._getLockDirectory()
        base_name = f"{self._api_connector_name}_{key_name}"
        
        # Remove all existing state files for this key
        for ext in ['lock', 'lockdown', 'error']:
            file_path = lock_dir / f"{base_name}.{ext}"
            if file_path.exists():
                file_path.unlink()
        
        # Create new state file if not vacant
        if state != 'vacant':
            state_file = lock_dir / f"{base_name}.{state}"
            state_file.touch()
            
            # Store paths for cleanup
            if state == 'lock':
                self._lock_file_path = state_file
            elif state == 'lockdown':
                self._lockdown_file_path = state_file
    
    def _getKeyState(self, key_name: str) -> str:
        """Get the current state of a specific API key"""
        lock_dir = self._getLockDirectory()
        base_name = f"{self._api_connector_name}_{key_name}"
        
        for state in ['lock', 'lockdown', 'error']:
            if (lock_dir / f"{base_name}.{state}").exists():
                return state
        
        return 'vacant'
    
    def _isRateLimitError(self, status_code: int) -> bool:
        """Check if the status code indicates a rate limit or throttling error"""
        # Common rate limiting and throttling status codes
        rate_limit_codes = {
            429,  # Too Many Requests
            403,  # Forbidden (often used for quota exceeded)
            503,  # Service Unavailable (sometimes used for rate limiting)
            509,  # Bandwidth Limit Exceeded
        }
        return status_code in rate_limit_codes
    
    def _isSuccessfulResponse(self, status_code: int) -> bool:
        """Check if the status code indicates a successful response"""
        # 2xx codes are successful, 3xx redirects are also considered successful
        return 200 <= status_code < 400
    
    def _selectApiKey(self) -> bool:
        """
        Select an available API key using the new state-based logic.
        Returns True if a key was selected, False if no keys available.
        """
        api_keys = self._getApiKeys()
        states = self._getKeyStates()
        
        # Priority 1: Try VACANT keys first
        available_vacant = states['vacant'] - self._tried_keys_in_connection
        if available_vacant:
            key_name = list(available_vacant)[0]
            self._current_api_key = api_keys[key_name]
            self._current_api_key_name = key_name
            self._setKeyState(key_name, 'lock')
            self._tried_keys_in_connection.add(key_name)
            self._logger.info(f"Selected VACANT key: {key_name} (locked)")
            return True
        
        # Priority 2: Try LOCKDOWN keys that haven't been tried in this connection
        available_lockdown = states['lockdown'] - self._tried_keys_in_connection
        if available_lockdown:
            key_name = list(available_lockdown)[0]
            self._current_api_key = api_keys[key_name]
            self._current_api_key_name = key_name
            self._setKeyState(key_name, 'lock')
            self._tried_keys_in_connection.add(key_name)
            self._logger.info(f"Selected LOCKDOWN key: {key_name} (locked)")
            return True
        
        # No available keys
        if not api_keys:
            error_message = self._generateNoKeysErrorMessage(api_keys, set())
            raise RuntimeError(error_message)
        
        # All keys have been tried or are in error state
        error_message = self._generateNoKeysErrorMessage(api_keys, states['locked'] | states['error'])
        raise RuntimeError(error_message)
    
    def _handleRequestFailure(self, status_code: int) -> bool:
        """
        Handle request failure by updating key state and optionally retrying.
        Returns True if should retry with a different key, False if should return response.
        """
        if self._current_api_key_name:
            if self._isRateLimitError(status_code):
                # Move current key to LOCKDOWN
                self._setKeyState(self._current_api_key_name, 'lockdown')
                self._logger.info(f"Key {self._current_api_key_name} moved to LOCKDOWN due to rate limit (status {status_code})")
                
                # Try to select another key
                try:
                    if self._selectApiKey():
                        return True  # Retry with new key
                except RuntimeError:
                    # No more keys available, will return current response
                    pass
            else:
                # Non-rate-limit error, just remove lock
                self._setKeyState(self._current_api_key_name, 'vacant')
                self._logger.debug(f"Key {self._current_api_key_name} returned to VACANT after non-rate-limit error")
        
        return False  # Don't retry
    
    def _handleRequestSuccess(self) -> None:
        """Handle successful request by updating key state appropriately"""
        if self._current_api_key_name:
            # Check if the key was in LOCKDOWN before this request
            states = self._getKeyStates()
            if self._current_api_key_name in states['lockdown']:
                # Key was in lockdown, recover it to LOCKED (not VACANT - connection is still active)
                self._setKeyState(self._current_api_key_name, 'lock')
                self._logger.info(f"Key {self._current_api_key_name} recovered from LOCKDOWN to LOCKED after successful request")
            else:
                # Key was already locked, keep it locked (don't change to vacant during active connection)
                self._logger.debug(f"Key {self._current_api_key_name} remains LOCKED during active connection")

    def request(self, method: str, endpoint: str, request: str) -> Tuple[str, int]:
        """
        Execute API request with retry logic and intelligent key management
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: Relative path to append to base URL
            request: Request body as string
        
        Returns:
            Tuple of (response_text, status_code)
        """
        self._logger.info(f"Executing {method} request to {endpoint}")
        
        # Reset tried keys for this new request, but keep the current connection key
        self._tried_keys_in_connection = set()
        if self._current_api_key_name:
            self._tried_keys_in_connection.add(self._current_api_key_name)
        
        # Use the key already selected during connection, don't select a new one
        if not self._current_api_key or not self._current_api_key_name:
            if not self._selectApiKey():
                raise RuntimeError("No API keys available for request")
        
        last_response_text = ""
        last_status_code = 500
        
        while True:
            # Prepare request
            url = f"{self._api_connector.BaseUrl}{endpoint}"
            headers = self._prepareHeaders()
            
            # For Google/Gemini APIs, add API key as query parameter
            params = {}
            if self._api_connector.Name in ['generativelanguage.googleapis.com', 'google'] and self._current_api_key:
                params['key'] = self._current_api_key
                # Remove Authorization header for Google APIs since they use query param
                if 'Authorization' in headers:
                    del headers['Authorization']
            
            try:
                # Make the request
                response = self._session.request(
                    method=method.upper(),
                    url=url,
                    data=request,
                    headers=headers,
                    params=params,
                    timeout=self._timeout
                )
                
                last_response_text = response.text
                last_status_code = response.status_code
                
                # Check if response is successful
                if self._isSuccessfulResponse(response.status_code):
                    self._logger.info(f"Request successful, status code: {response.status_code}")
                    self._handleRequestSuccess()
                    return response.text, response.status_code
                
                # Handle failure - check if we should retry
                if self._handleRequestFailure(response.status_code):
                    self._logger.info(f"Retrying request with different key after status {response.status_code}")
                    continue  # Retry with new key
                else:
                    # No retry, return the response
                    self._logger.info(f"Returning response with status {response.status_code} (no retry)")
                    return response.text, response.status_code
                    
            except requests.exceptions.RequestException as e:
                self._logger.error(f"Request failed with exception: {e}")
                # For network errors, don't move to lockdown, just try next key if available
                if self._current_api_key_name:
                    self._setKeyState(self._current_api_key_name, 'vacant')
                
                try:
                    if self._selectApiKey():
                        self._logger.info(f"Retrying request with different key after network error")
                        continue  # Retry with new key
                except RuntimeError:
                    pass  # No more keys available
                
                # No more keys or failed to select, raise the original exception
                raise RuntimeError(f"Request failed: {e}")
    
    def _prepareHeaders(self) -> Dict[str, str]:
        """Prepare request headers including API key"""
        headers = {
            'Content-Type': 'application/json' if self._api_connector.Format == 'json' else 'application/xml',
        }
        
        if self._api_connector.RequiresApiKey and self._current_api_key:
            # Check if connector specifies custom auth header
            api_key_header = self._api_connector.getAttribute('api_key_header')
            if api_key_header:
                prefix = self._api_connector.getAttribute('api_key_prefix', '')
                headers[api_key_header] = f'{prefix}{self._current_api_key}'
            else:
                # Default to Bearer token authentication
                headers['Authorization'] = f'Bearer {self._current_api_key}'
        
        return headers
    
    def _getCurrentKeyName(self) -> str:
        """Get the current API key name"""
        return self._current_api_key_name if self._current_api_key_name else ""
    
    def _disconnect(self) -> None:
        """Disconnect and cleanup resources"""
        self._logger.info("Disconnecting from API")
        
        # Clean up current key state - return to appropriate state
        if self._current_api_key_name:
            current_state = self._getKeyState(self._current_api_key_name)
            if current_state == 'lock':
                # If still locked, return to vacant (normal disconnection)
                self._setKeyState(self._current_api_key_name, 'vacant')
                self._logger.info(f"Returned key {self._current_api_key_name} to VACANT status")
        
        # Close session
        if self._session:
            self._session.close()

    def requestJSON(self, endpoint: str, method: str = 'POST', data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request with automatic JSON handling
        
        Args:
            endpoint: API endpoint (relative path)
            method: HTTP method (default: POST)
            data: Request data as dictionary (will be JSON-encoded)
        
        Returns:
            Response as dictionary
        """
        import json as json_lib
        
        # Convert data to JSON string if provided
        if data is not None:
            request_body = json_lib.dumps(data)
        else:
            request_body = ""
        
        # Use the existing request method
        response_text, status_code = self.request(method, endpoint, request_body)
        
        # Try to parse as JSON
        try:
            return json_lib.loads(response_text)
        except json_lib.JSONDecodeError:
            # Return as plain text if not valid JSON
            return {"text": response_text, "status_code": status_code}

    # Backward compatibility aliases
    def run(self, method: str, endpoint: str, request: str) -> Tuple[str, int]:
        """
        DEPRECATED: Use request() instead. This method will be removed in a future version.
        """
        import warnings
        warnings.warn("run() is deprecated, use request() instead", DeprecationWarning, stacklevel=2)
        return self.request(method, endpoint, request)
    
    def makeRequest(self, endpoint: str, method: str = 'POST', data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        DEPRECATED: Use requestJSON() instead. This method will be removed in a future version.
        """
        import warnings
        warnings.warn("makeRequest() is deprecated, use requestJSON() instead", DeprecationWarning, stacklevel=2)
        return self.requestJSON(endpoint, method, data)

    def __del__(self):
        """Destructor - cleanup resources safely during interpreter shutdown.

        Avoid logging and imports that may fail when Python is finalizing.
        Perform best-effort cleanup and never raise from __del__.
        """
        try:
            import sys  # local import in case globals are torn down
            is_finalizing = getattr(sys, "is_finalizing", lambda: False)
            finalizing = True if not callable(is_finalizing) else bool(is_finalizing())
        except Exception:
            finalizing = True

        if finalizing:
            # Minimal, no-logging cleanup path
            try:
                lock_path = getattr(self, "_lock_file_path", None)
                if lock_path:
                    try:
                        import os  # local import
                        os.unlink(str(lock_path))
                    except FileNotFoundError:
                        pass
                    except Exception:
                        pass
            except Exception:
                pass

            try:
                sess = getattr(self, "_session", None)
                if sess:
                    try:
                        sess.close()
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            # Normal cleanup path; still guard to never raise from __del__
            try:
                self._disconnect()
            except Exception:
                try:
                    sess = getattr(self, "_session", None)
                    if sess:
                        sess.close()
                except Exception:
                    pass
    
    @staticmethod
    def cleanUp(api_connector: Optional[str] = None) -> None:
        """
        Clean up lock and error files
        
        Args:
            api_connector: Specific API connector to clean up, or None for all
        """
        logger = logging.getLogger('APIJongler')
        lock_dir = Path.home() / '.api_jongler' / 'locks'
        
        if not lock_dir.exists():
            logger.info("No lock directory found, nothing to clean up")
            return
        
        if api_connector:
            pattern = f"{api_connector}_*"
            logger.info(f"Cleaning up files for API connector: {api_connector}")
        else:
            pattern = "*"
            logger.info("Cleaning up all lock and error files")
        
        # Remove lock files
        lock_files = glob.glob(str(lock_dir / f"{pattern}.lock"))
        for lock_file in lock_files:
            try:
                os.unlink(lock_file)
                logger.info(f"Removed lock file: {Path(lock_file).name}")
            except Exception as e:
                logger.error(f"Failed to remove lock file {lock_file}: {e}")
        
        # Remove error files
        error_files = glob.glob(str(lock_dir / f"{pattern}.error"))
        for error_file in error_files:
            try:
                os.unlink(error_file)
                logger.info(f"Removed error file: {Path(error_file).name}")
            except Exception as e:
                logger.error(f"Failed to remove error file {error_file}: {e}")
        
        removed_count = len(lock_files) + len(error_files)
        logger.info(f"Cleanup completed. Removed {removed_count} files.")

    def disconnect(self) -> None:
        """Public method to disconnect and cleanup resources"""
        self._disconnect()

    def getAvailableKeys(self) -> Dict[str, str]:
        """Get all available API keys for the current connector (VACANT + LOCKDOWN states)"""
        api_keys = self._getApiKeys()
        states = self._getKeyStates()
        # Available means VACANT or LOCKDOWN (can be retried)
        available_keys = states['vacant'] | states['lockdown']
        return {k: v for k, v in api_keys.items() if k in available_keys}

    def getLockedKeys(self) -> set:
        """Get currently locked API keys"""
        states = self._getKeyStates()
        return states['locked']

    def getErrorKeys(self) -> set:
        """Get API keys marked as having errors"""
        states = self._getKeyStates()
        return states['error']
    
    def getLockdownKeys(self) -> set:
        """Get API keys currently in lockdown state"""
        states = self._getKeyStates()
        return states['lockdown']
    
    def getVacantKeys(self) -> set:
        """Get API keys in vacant state (immediately available)"""
        states = self._getKeyStates()
        return states['vacant']
    
    def getKeyStates(self) -> Dict[str, set]:
        """Get detailed state information for all keys"""
        return self._getKeyStates()

    def clearErrorKey(self, key_name: str) -> bool:
        """Clear error status for a specific API key"""
        lock_dir = self._getLockDirectory()
        error_file = lock_dir / f"{self._api_connector_name}_{key_name}.error"
        if error_file.exists():
            try:
                error_file.unlink()
                self._logger.info(f"Cleared error status for key: {key_name}")
                return True
            except Exception as e:
                self._logger.error(f"Failed to clear error for key {key_name}: {e}")
                return False
        return False

    def refreshConnection(self) -> None:
        """Refresh the connection by reconnecting"""
        self._disconnect()
        self._connect(self._api_connector_name, self._is_tor_enabled)
