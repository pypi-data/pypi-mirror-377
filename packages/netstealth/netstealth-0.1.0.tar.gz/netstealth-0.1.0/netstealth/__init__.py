"""
NetStealth - Advanced stealth automation library.

This library provides comprehensive stealth capabilities for web automation,
including:

- Enhanced undetected browser automation
- Browser fingerprint consistency 
- Human-like behavior simulation
- Advanced proxy support with mitmproxy integration
- Session management and component lifecycle
- Extensible architecture following SOLID principles

The library is designed to be service-agnostic and can be extended
for specific services like TIDAL, Spotify, etc.
"""

from ._version import __version__

# Core abstractions and base classes
from .core import (
    # Interfaces
    StealthComponent,
    BrowserInterface,
    ProxyInterface,
    AuthProvider,
    APIClient,
    FingerprintManager,
    HumanBehaviorSimulator,
    
    # Base session
    BaseStealthSession,
    
    # Exceptions
    NetStealthError,
    BrowserError,
    ProxyError,
    FingerprintError,
    AuthenticationError,
    NetworkError,
    ConfigurationError,
    SessionError,
    ComponentError,
    ErrorCodes,
    handle_exception
)

# Components
from .components.browser import StealthBrowserManager

# Utilities
from .utils import (
    LazyImportError,
    check_optional_dependencies,
    get_missing_dependencies,
    print_dependency_status
)

__author__ = "NetStealth Contributors"
__email__ = "contributors@netstealth.io"
__description__ = "Advanced stealth automation library with anti-detection browser control and proxy management"

# Main exports
__all__ = [
    # Version
    "__version__",
    
    # Core interfaces
    "StealthComponent",
    "BrowserInterface",
    "ProxyInterface", 
    "AuthProvider",
    "APIClient",
    "FingerprintManager",
    "HumanBehaviorSimulator",
    
    # Base classes
    "BaseStealthSession",
    
    # Components
    "StealthBrowserManager",
    
    # Exceptions
    "NetStealthError",
    "BrowserError",
    "ProxyError",
    "FingerprintError", 
    "AuthenticationError",
    "NetworkError",
    "ConfigurationError",
    "SessionError",
    "ComponentError",
    "ErrorCodes",
    "handle_exception",
    
    # Utilities
    "LazyImportError",
    "check_optional_dependencies",
    "get_missing_dependencies",
    "print_dependency_status",
    
    # Metadata
    "__author__",
    "__email__",
    "__description__"
]


def get_version() -> str:
    """Get the current version of netstealth."""
    return __version__


def get_info() -> dict[str, str]:
    """Get information about netstealth library."""
    return {
        "name": "netstealth",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "homepage": "https://github.com/netstealth/netstealth",
    }


# Configure logging for the library
import logging
import sys
from typing import Optional

def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    enable_colors: bool = True
) -> None:
    """
    Setup logging configuration for netstealth.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        enable_colors: Whether to enable colored output
    """
    try:
        import colorlog
        
        if format_string is None:
            if enable_colors:
                format_string = "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                handler = colorlog.StreamHandler(sys.stdout)
                handler.setFormatter(colorlog.ColoredFormatter(format_string))
            else:
                format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(logging.Formatter(format_string))
        else:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(format_string))
            
    except ImportError:
        # Fallback to standard logging if colorlog is not available
        format_string = format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(format_string))
    
    # Configure root logger for netstealth
    logger = logging.getLogger("netstealth")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    for existing_handler in logger.handlers[:]:
        logger.removeHandler(existing_handler)
    
    logger.addHandler(handler)
    logger.propagate = False


# Setup default logging configuration
setup_logging(level="INFO")

# Library-wide constants
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Default timeouts (in seconds)
DEFAULT_TIMEOUTS = {
    "browser_startup": 30,
    "page_load": 30, 
    "element_wait": 10,
    "api_request": 30,
    "proxy_connect": 45,
}

# Default retry configuration
DEFAULT_RETRY_CONFIG = {
    "max_attempts": 3,
    "backoff_factor": 2,
    "retry_on_status": [429, 500, 502, 503, 504],
}
