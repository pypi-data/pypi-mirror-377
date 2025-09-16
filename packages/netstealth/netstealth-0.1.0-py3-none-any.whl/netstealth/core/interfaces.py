"""
Core interfaces for netstealth library.

This module defines the key abstractions using balanced SOLID principles:
- Protocol classes for dependency injection (DIP)
- Abstract base classes for extension points (OCP)
- Minimal, focused interfaces (ISP)
"""

from abc import ABC, abstractmethod
from typing import Protocol, Optional, Dict, Any, List, runtime_checkable


@runtime_checkable
class StealthComponent(Protocol):
    """
    Minimal interface for stealth components.
    
    This protocol defines the basic lifecycle methods that all stealth
    components should implement for consistent management.
    """
    
    def initialize(self) -> None:
        """Initialize the component."""
        ...
    
    def cleanup(self) -> None:
        """Clean up resources used by the component."""
        ...
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the component."""
        ...


@runtime_checkable
class BrowserInterface(Protocol):
    """
    Browser abstraction for dependency injection.
    
    This protocol defines the essential browser operations needed
    for stealth automation without coupling to specific implementations.
    """
    
    def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        ...
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript in the browser."""
        ...
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
        """Wait for an element to be present."""
        ...
    
    def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """Take a screenshot of the current page."""
        ...


@runtime_checkable
class ProxyInterface(Protocol):
    """
    Proxy abstraction for dependency injection.
    
    This protocol defines the essential proxy operations for
    network traffic management and authentication.
    """
    
    def start(self) -> bool:
        """Start the proxy service."""
        ...
    
    def stop(self) -> None:
        """Stop the proxy service."""
        ...
    
    def is_running(self) -> bool:
        """Check if proxy is currently running."""
        ...
    
    def get_local_port(self) -> int:
        """Get the local port the proxy is listening on."""
        ...


class AuthProvider(ABC):
    """
    Abstract authentication provider.
    
    This abstract base class defines the contract for service-specific
    authentication implementations, following the Open/Closed Principle.
    """
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with the service.
        
        Args:
            credentials: Authentication credentials (username, password, etc.)
            
        Returns:
            Dict containing authentication result with keys:
            - success: bool
            - access_token: Optional[str]
            - refresh_token: Optional[str]
            - user_id: Optional[str]
            - expires_at: Optional[datetime]
            - error_message: Optional[str]
        """
        pass
    
    @abstractmethod
    def refresh_auth(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh authentication using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dict with same structure as authenticate()
        """
        pass
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return False


class APIClient(ABC):
    """
    Abstract API client.
    
    This abstract base class provides the foundation for service-specific
    API implementations with built-in stealth capabilities.
    """
    
    @abstractmethod
    def make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an API request with stealth measures.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            headers: Optional headers
            params: Optional query parameters
            data: Optional request body data
            **kwargs: Additional request options
            
        Returns:
            Dict containing the API response
        """
        pass
    
    def set_session(self, session: 'BaseStealthSession') -> None:
        """Set the parent session for accessing stealth components."""
        pass


class FingerprintManager(ABC):
    """
    Abstract fingerprint manager.
    
    This abstract base class defines the interface for browser fingerprint
    management and consistency verification.
    """
    
    @abstractmethod
    def capture(self, browser: BrowserInterface) -> Dict[str, Any]:
        """
        Capture browser fingerprint.
        
        Args:
            browser: Browser interface to capture fingerprint from
            
        Returns:
            Dict containing fingerprint data
        """
        pass
    
    @abstractmethod
    def verify_consistency(self, fingerprint_data: Dict[str, Any]) -> bool:
        """
        Verify fingerprint consistency.
        
        Args:
            fingerprint_data: Previously captured fingerprint data
            
        Returns:
            True if fingerprint is consistent
        """
        pass
    
    def get_fingerprint_data(self) -> Optional[Dict[str, Any]]:
        """Get current fingerprint data."""
        return None


class HumanBehaviorSimulator(ABC):
    """
    Abstract human behavior simulator.
    
    This abstract base class defines the interface for simulating
    human-like interactions with web pages.
    """
    
    @abstractmethod
    def human_like_typing(self, element: Any, text: str) -> None:
        """
        Type text with human-like delays and patterns.
        
        Args:
            element: The input element to type into
            text: Text to type
        """
        pass
    
    @abstractmethod
    def human_like_mouse_move(self, browser: BrowserInterface, element: Any) -> None:
        """
        Move mouse to element with human-like movement.
        
        Args:
            browser: Browser interface
            element: Target element
        """
        pass
    
    @abstractmethod
    def wait_like_human(
        self,
        min_seconds: float = 1.0,
        max_seconds: float = 3.0,
        reason: str = "general"
    ) -> None:
        """
        Wait with human-like timing patterns.
        
        Args:
            min_seconds: Minimum wait time
            max_seconds: Maximum wait time
            reason: Reason for waiting (affects timing pattern)
        """
        pass
