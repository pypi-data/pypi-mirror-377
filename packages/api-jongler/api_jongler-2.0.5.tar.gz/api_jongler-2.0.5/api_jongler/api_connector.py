"""
API connector configuration class
"""

from typing import Dict, Any


class APIConnector:
    """Represents an API connector configuration"""
    
    def __init__(self, config_data: Dict[str, Any]):
        """Initialize APIConnector with configuration data"""
        self._name = config_data.get("name", "")
        self._host = config_data.get("host", "")
        self._port = config_data.get("port", 443 if config_data.get("protocol") == "https" else 80)
        self._protocol = config_data.get("protocol", "https")
        self._format = config_data.get("format", "json")
        self._requires_api_key = config_data.get("requires_api_key", True)
        
        # Store any additional custom attributes from the config
        self._custom_attributes = {}
        for key, value in config_data.items():
            if not hasattr(self, f'_{key}'):
                self._custom_attributes[key] = value

    @property
    def Name(self) -> str:
        """Get the connector name"""
        return self._name

    @property
    def Host(self) -> str:
        """Get the connector host"""
        return self._host

    @property
    def Port(self) -> int:
        """Get the connector port"""
        return self._port

    @property
    def Protocol(self) -> str:
        """Get the connector protocol"""
        return self._protocol

    @property
    def Format(self) -> str:
        """Get the connector format"""
        return self._format

    @property
    def RequiresApiKey(self) -> bool:
        """Get whether the connector requires an API key"""
        return self._requires_api_key

    @property
    def BaseUrl(self) -> str:
        """Get the base URL for the API"""
        if self._port in [80, 443] and self._protocol in ["http", "https"]:
            return f"{self._protocol}://{self._host}"
        return f"{self._protocol}://{self._host}:{self._port}"

    @property
    def CustomAttributes(self) -> Dict[str, Any]:
        """Get custom attributes from configuration"""
        return self._custom_attributes.copy()

    def getAttribute(self, name: str, default: Any = None) -> Any:
        """Get a custom attribute value"""
        return self._custom_attributes.get(name, default)

    def hasAttribute(self, name: str) -> bool:
        """Check if custom attribute exists"""
        return name in self._custom_attributes

    def setName(self, name: str) -> None:
        """Set the connector name"""
        self._name = name

    def setHost(self, host: str) -> None:
        """Set the connector host"""
        self._host = host

    def setPort(self, port: int) -> None:
        """Set the connector port"""
        self._port = port

    def setProtocol(self, protocol: str) -> None:
        """Set the connector protocol"""
        self._protocol = protocol

    def setFormat(self, format_type: str) -> None:
        """Set the connector format"""
        self._format = format_type

    def setRequiresApiKey(self, requires: bool) -> None:
        """Set whether the connector requires an API key"""
        self._requires_api_key = requires
