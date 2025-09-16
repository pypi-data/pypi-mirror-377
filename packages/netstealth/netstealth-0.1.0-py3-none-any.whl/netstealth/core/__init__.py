"""
Core netstealth modules.

This package contains the fundamental abstractions and base classes
for the netstealth library, implementing balanced SOLID principles.
"""

from .interfaces import (
    StealthComponent,
    BrowserInterface,
    ProxyInterface,
    AuthProvider,
    APIClient,
    FingerprintManager,
    HumanBehaviorSimulator
)

from .exceptions import (
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

from .session import BaseStealthSession

__all__ = [
    # Interfaces
    "StealthComponent",
    "BrowserInterface", 
    "ProxyInterface",
    "AuthProvider",
    "APIClient",
    "FingerprintManager",
    "HumanBehaviorSimulator",
    
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
    
    # Base classes
    "BaseStealthSession"
]
