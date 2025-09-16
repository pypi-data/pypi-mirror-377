"""
Core exceptions for netstealth library.

This module defines the base exception hierarchy following SOLID principles:
- Single responsibility for each exception type
- Open for extension by service-specific libraries
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class NetStealthError(Exception):
    """
    Base exception for all netstealth errors.
    
    This base class provides common functionality for all netstealth exceptions
    including error codes, context information, and structured error data.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize base netstealth exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format.
        
        Returns:
            Dict containing structured error information
        """
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "original_exception": str(self.original_exception) if self.original_exception else None
        }


class BrowserError(NetStealthError):
    """
    Browser-related errors.
    
    Raised when browser operations fail, including startup, navigation,
    element interaction, or script execution issues.
    """
    
    def __init__(
        self,
        message: str,
        browser_state: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize browser error.
        
        Args:
            message: Error message
            browser_state: Current browser state when error occurred
            url: URL being accessed when error occurred
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if browser_state:
            context["browser_state"] = browser_state
        if url:
            context["url"] = url
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ProxyError(NetStealthError):
    """
    Proxy-related errors.
    
    Raised when proxy operations fail, including startup, connection,
    authentication, or certificate issues.
    """
    
    def __init__(
        self,
        message: str,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize proxy error.
        
        Args:
            message: Error message
            proxy_host: Proxy hostname/IP
            proxy_port: Proxy port
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if proxy_host:
            context["proxy_host"] = proxy_host
        if proxy_port:
            context["proxy_port"] = proxy_port
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class FingerprintError(NetStealthError):
    """
    Fingerprint-related errors.
    
    Raised when fingerprint operations fail, including capture,
    verification, or consistency checks.
    """
    
    def __init__(
        self,
        message: str,
        fingerprint_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize fingerprint error.
        
        Args:
            message: Error message
            fingerprint_type: Type of fingerprint (TLS, browser, etc.)
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if fingerprint_type:
            context["fingerprint_type"] = fingerprint_type
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class AuthenticationError(NetStealthError):
    """
    Authentication-related errors.
    
    Raised when authentication operations fail, including login,
    token refresh, or credential validation.
    """
    
    def __init__(
        self,
        message: str,
        auth_method: Optional[str] = None,
        username: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            auth_method: Authentication method used
            username: Username (if safe to include)
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if auth_method:
            context["auth_method"] = auth_method
        if username:
            context["username"] = username
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class NetworkError(NetStealthError):
    """
    Network-related errors.
    
    Raised when network operations fail, including connection timeouts,
    DNS resolution, or HTTP errors.
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize network error.
        
        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            url: URL that failed
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if status_code:
            context["status_code"] = status_code
        if url:
            context["url"] = url
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ConfigurationError(NetStealthError):
    """
    Configuration-related errors.
    
    Raised when configuration is invalid, missing, or incompatible.
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_value: Invalid configuration value
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if config_key:
            context["config_key"] = config_key
        if config_value is not None:
            context["config_value"] = str(config_value)
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class SessionError(NetStealthError):
    """
    Session management errors.
    
    Raised when session operations fail, including initialization,
    component registration, or lifecycle management.
    """
    
    def __init__(
        self,
        message: str,
        session_state: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize session error.
        
        Args:
            message: Error message
            session_state: Current session state
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if session_state:
            context["session_state"] = session_state
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ComponentError(NetStealthError):
    """
    Component-related errors.
    
    Raised when stealth component operations fail, including
    initialization, cleanup, or status checks.
    """
    
    def __init__(
        self,
        message: str,
        component_name: Optional[str] = None,
        component_state: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize component error.
        
        Args:
            message: Error message
            component_name: Name of the component that failed
            component_state: Current component state
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        if component_name:
            context["component_name"] = component_name
        if component_state:
            context["component_state"] = component_state
        
        kwargs["context"] = context
        super().__init__(message, **kwargs)


# Error code constants for common scenarios
class ErrorCodes:
    """Common error codes used throughout netstealth."""
    
    # Browser errors
    BROWSER_STARTUP_FAILED = "BROWSER_STARTUP_FAILED"
    BROWSER_NAVIGATION_FAILED = "BROWSER_NAVIGATION_FAILED"
    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    SCRIPT_EXECUTION_FAILED = "SCRIPT_EXECUTION_FAILED"
    
    # Proxy errors
    PROXY_STARTUP_FAILED = "PROXY_STARTUP_FAILED"
    PROXY_CONNECTION_FAILED = "PROXY_CONNECTION_FAILED"
    PROXY_AUTH_FAILED = "PROXY_AUTH_FAILED"
    CERTIFICATE_ERROR = "CERTIFICATE_ERROR"
    
    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    AUTH_FLOW_FAILED = "AUTH_FLOW_FAILED"
    
    # Network errors
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    DNS_RESOLUTION_FAILED = "DNS_RESOLUTION_FAILED"
    HTTP_ERROR = "HTTP_ERROR"
    
    # Configuration errors
    MISSING_CONFIG = "MISSING_CONFIG"
    INVALID_CONFIG = "INVALID_CONFIG"
    INCOMPATIBLE_CONFIG = "INCOMPATIBLE_CONFIG"


def handle_exception(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    reraise_as: Optional[type] = None
) -> None:
    """
    Handle and optionally re-raise exceptions with additional context.
    
    Args:
        exception: The original exception
        context: Additional context to add
        reraise_as: Exception class to re-raise as (defaults to NetStealthError)
        
    Raises:
        NetStealthError or specified exception type
    """
    if isinstance(exception, NetStealthError):
        # Already a netstealth exception, just add context if provided
        if context:
            exception.context.update(context)
        raise exception
    
    # Convert to netstealth exception
    error_class = reraise_as or NetStealthError
    raise error_class(
        message=str(exception),
        context=context,
        original_exception=exception
    ) from exception
