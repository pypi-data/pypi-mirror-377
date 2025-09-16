"""
Base stealth session implementation.

This module provides the BaseStealthSession class that implements SOLID principles:
- Single Responsibility: Manages session lifecycle only
- Open/Closed: Open for extension via inheritance
- Dependency Inversion: Depends on abstractions, not concretions
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Type
from pathlib import Path
from datetime import datetime

from .interfaces import (
    StealthComponent,
    BrowserInterface,
    ProxyInterface,
    AuthProvider,
    APIClient
)
from .exceptions import (
    NetStealthError,
    SessionError,
    ComponentError,
    ConfigurationError,
    ErrorCodes,
    handle_exception
)


class BaseStealthSession(ABC):
    """
    Base stealth session with SOLID principles.
    
    This abstract base class provides the foundation for service-specific
    stealth sessions. It manages component lifecycle, dependency injection,
    and provides extension points for service-specific implementations.
    
    Key SOLID principles implemented:
    - SRP: Only manages session lifecycle and component coordination
    - OCP: Open for extension through abstract methods and component registration
    - LSP: Subclasses can be substituted without breaking functionality
    - ISP: Depends on minimal, focused interfaces
    - DIP: Depends on abstractions (interfaces) not concrete implementations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base stealth session.
        
        Args:
            config: Configuration dictionary for the session
        """
        self.config = config or {}
        self._components: List[StealthComponent] = []
        self._auth_provider: Optional[AuthProvider] = None
        self._browser: Optional[BrowserInterface] = None
        self._proxy: Optional[ProxyInterface] = None
        self._api_client: Optional[APIClient] = None
        
        # Session state
        self.authenticated = False
        self.session_id = self._generate_session_id()
        self.created_at = datetime.now()
        self._initialized = False
        self._closed = False
        
        # Setup logging
        self.logger = self._setup_logging()
        self.logger.info(f"Session {self.session_id} created")
    
    def __enter__(self) -> 'BaseStealthSession':
        """Context manager entry."""
        if not self._initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.cleanup()
    
    # Component Management (Open/Closed Principle)
    
    def register_component(self, component: StealthComponent) -> 'BaseStealthSession':
        """
        Register a stealth component.
        
        This method implements the Open/Closed Principle by allowing
        functionality to be extended through component registration
        without modifying the base session class.
        
        Args:
            component: Component implementing StealthComponent protocol
            
        Returns:
            Self for method chaining
            
        Raises:
            SessionError: If session is already closed
            ComponentError: If component registration fails
        """
        if self._closed:
            raise SessionError(
                "Cannot register component on closed session",
                session_state="closed",
                error_code=ErrorCodes.INVALID_CONFIG
            )
        
        try:
            self._components.append(component)
            self.logger.debug(f"Registered component: {type(component).__name__}")
            return self
        except Exception as e:
            handle_exception(
                e,
                context={"component_type": type(component).__name__},
                reraise_as=ComponentError
            )
    
    def set_browser(self, browser: BrowserInterface) -> 'BaseStealthSession':
        """
        Set browser dependency (Dependency Inversion Principle).
        
        Args:
            browser: Browser implementation
            
        Returns:
            Self for method chaining
        """
        self._browser = browser
        if hasattr(browser, 'initialize') and hasattr(browser, 'cleanup'):
            self.register_component(browser)
        return self
    
    def set_proxy(self, proxy: ProxyInterface) -> 'BaseStealthSession':
        """
        Set proxy dependency (Dependency Inversion Principle).
        
        Args:
            proxy: Proxy implementation
            
        Returns:
            Self for method chaining
        """
        self._proxy = proxy
        if hasattr(proxy, 'initialize') and hasattr(proxy, 'cleanup'):
            self.register_component(proxy)
        return self
    
    def set_auth_provider(self, provider: AuthProvider) -> 'BaseStealthSession':
        """
        Set authentication provider (Dependency Inversion Principle).
        
        Args:
            provider: Authentication provider implementation
            
        Returns:
            Self for method chaining
        """
        self._auth_provider = provider
        return self
    
    def set_api_client(self, client: APIClient) -> 'BaseStealthSession':
        """
        Set API client (Dependency Inversion Principle).
        
        Args:
            client: API client implementation
            
        Returns:
            Self for method chaining
        """
        self._api_client = client
        client.set_session(self)
        return self
    
    # Lifecycle Management (Single Responsibility Principle)
    
    def initialize(self) -> None:
        """
        Initialize the session and all registered components.
        
        This method implements the Single Responsibility Principle by
        focusing only on component initialization coordination.
        
        Raises:
            SessionError: If initialization fails
        """
        if self._initialized:
            self.logger.warning("Session already initialized")
            return
        
        try:
            self.logger.info("Initializing session components...")
            
            # Initialize components in registration order
            for component in self._components:
                try:
                    component.initialize()
                    self.logger.debug(f"Initialized component: {type(component).__name__}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize component {type(component).__name__}: {e}")
                    handle_exception(
                        e,
                        context={
                            "component_type": type(component).__name__,
                            "session_id": self.session_id
                        },
                        reraise_as=ComponentError
                    )
            
            # Call service-specific initialization
            self._service_initialize()
            
            self._initialized = True
            self.logger.info("Session initialization completed")
            
        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            handle_exception(
                e,
                context={"session_id": self.session_id},
                reraise_as=SessionError
            )
    
    def cleanup(self) -> None:
        """
        Clean up the session and all registered components.
        
        This method implements graceful cleanup with error handling
        to ensure all components are properly cleaned up even if
        some fail.
        """
        if self._closed:
            return
        
        self.logger.info("Cleaning up session...")
        
        # Cleanup components in reverse order
        for component in reversed(self._components):
            try:
                component.cleanup()
                self.logger.debug(f"Cleaned up component: {type(component).__name__}")
            except Exception as e:
                self.logger.error(f"Error cleaning up component {type(component).__name__}: {e}")
                # Continue cleanup even if one component fails
        
        # Call service-specific cleanup
        try:
            self._service_cleanup()
        except Exception as e:
            self.logger.error(f"Service cleanup failed: {e}")
        
        self._closed = True
        self.authenticated = False
        self.logger.info(f"Session {self.session_id} closed")
    
    # Abstract Methods (Open/Closed Principle)
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with the service.
        
        Service-specific implementations must provide their own
        authentication logic while using the registered auth provider.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            Dict containing authentication result
        """
        pass
    
    def _service_initialize(self) -> None:
        """
        Service-specific initialization hook.
        
        Override this method to add service-specific initialization
        logic without modifying the base initialization flow.
        """
        pass
    
    def _service_cleanup(self) -> None:
        """
        Service-specific cleanup hook.
        
        Override this method to add service-specific cleanup
        logic without modifying the base cleanup flow.
        """
        pass
    
    # Property Access (Interface Segregation Principle)
    
    @property
    def browser(self) -> Optional[BrowserInterface]:
        """Get the registered browser interface."""
        return self._browser
    
    @property
    def proxy(self) -> Optional[ProxyInterface]:
        """Get the registered proxy interface."""
        return self._proxy
    
    @property
    def auth_provider(self) -> Optional[AuthProvider]:
        """Get the registered auth provider."""
        return self._auth_provider
    
    @property
    def api_client(self) -> Optional[APIClient]:
        """Get the registered API client."""
        return self._api_client
    
    # Status and Information
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive session status.
        
        Returns:
            Dict containing session status information
        """
        component_status = {}
        for component in self._components:
            try:
                component_name = type(component).__name__
                component_status[component_name] = component.get_status()
            except Exception as e:
                component_status[component_name] = {"error": str(e)}
        
        return {
            "session_id": self.session_id,
            "initialized": self._initialized,
            "authenticated": self.authenticated,
            "closed": self._closed,
            "created_at": self.created_at.isoformat(),
            "component_count": len(self._components),
            "components": component_status,
            "config_keys": list(self.config.keys())
        }
    
    def is_healthy(self) -> bool:
        """
        Check if session is in a healthy state.
        
        Returns:
            True if session is healthy
        """
        if self._closed or not self._initialized:
            return False
        
        # Check component health
        for component in self._components:
            try:
                status = component.get_status()
                if not status.get("healthy", True):
                    return False
            except Exception:
                return False
        
        return True
    
    # Utility Methods
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return f"netstealth-{uuid.uuid4().hex[:8]}"
    
    def _setup_logging(self) -> logging.Logger:
        """Setup session-specific logging."""
        logger_name = f"netstealth.session.{self.session_id}"
        logger = logging.getLogger(logger_name)
        
        # Set log level from config
        log_level = self.config.get("log_level", "INFO")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        return logger
    
    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]) -> 'BaseStealthSession':
        """
        Create session from configuration dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Configured session instance
        """
        return cls(config=config_dict)
