"""
Colored logging formatter for APIJongler
"""

import logging
from datetime import datetime
from colorama import Fore, Style


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._colors = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
        }

    @property
    def Colors(self) -> dict:
        """Get the color mapping for log levels"""
        return self._colors.copy()

    def format(self, record):
        """Format log record with colors and additional context"""
        log_color = self._colors.get(record.levelname, Fore.WHITE)
        
        # Add function name and timestamp
        record.funcName = getattr(record, 'funcName', 'unknown')
        record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the message
        formatted = super().format(record)
        
        # Apply color to console output
        if hasattr(record, 'colored') and record.colored:
            return f"{log_color}{formatted}{Style.RESET_ALL}"
        return formatted

    def setColor(self, level: str, color: str) -> None:
        """Set custom color for a log level"""
        if level in self._colors:
            self._colors[level] = color

    def resetColors(self) -> None:
        """Reset colors to default values"""
        self._colors = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
        }
