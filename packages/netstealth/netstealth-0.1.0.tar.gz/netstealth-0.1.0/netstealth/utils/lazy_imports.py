"""
Lazy import utilities for netstealth.

This module provides lazy loading of optional dependencies to avoid
import errors when packages are not installed or when running in
environments where certain dependencies are not available.
"""

import logging
from typing import Any, Optional
from types import ModuleType


logger = logging.getLogger(__name__)


class LazyImportError(ImportError):
    """Raised when a lazy import fails."""
    pass


class BrowserDependencies:
    """Container for browser-related dependencies."""
    
    def __init__(self):
        self.uc: Optional[ModuleType] = None
        self.By: Optional[Any] = None
        self.WebDriverWait: Optional[Any] = None
        self.EC: Optional[Any] = None
        self.TimeoutException: Optional[Any] = None
        self.WebDriverException: Optional[Any] = None
        self._loaded = False
    
    def __getattr__(self, name: str) -> Any:
        if not self._loaded:
            raise LazyImportError(
                f"Browser dependencies not loaded. Call lazy_import_browser_deps() first."
            )
        
        attr = getattr(self, name, None)
        if attr is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return attr


def lazy_import_browser_deps() -> BrowserDependencies:
    """
    Lazy import browser dependencies.
    
    This function imports browser-related packages only when needed,
    providing better error messages and avoiding import issues during
    package installation or in environments where these packages
    are not available.
    
    Returns:
        BrowserDependencies: Container with imported browser modules
        
    Raises:
        LazyImportError: If required browser dependencies cannot be imported
    """
    deps = BrowserDependencies()
    
    try:
        # Import undetected_chromedriver
        import undetected_chromedriver as uc
        deps.uc = uc
        logger.debug("Successfully imported undetected_chromedriver")
        
    except ImportError as e:
        raise LazyImportError(
            "undetected_chromedriver is required for browser functionality. "
            "Install it with: pip install undetected-chromedriver"
        ) from e
    
    try:
        # Import Selenium components
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, WebDriverException
        
        deps.By = By
        deps.WebDriverWait = WebDriverWait
        deps.EC = EC
        deps.TimeoutException = TimeoutException
        deps.WebDriverException = WebDriverException
        
        logger.debug("Successfully imported Selenium components")
        
    except ImportError as e:
        raise LazyImportError(
            "Selenium is required for browser functionality. "
            "Install it with: pip install selenium"
        ) from e
    
    deps._loaded = True
    return deps


class ProxyDependencies:
    """Container for proxy-related dependencies."""
    
    def __init__(self):
        self.mitmproxy: Optional[ModuleType] = None
        self.subprocess: Optional[ModuleType] = None
        self.threading: Optional[ModuleType] = None
        self._loaded = False
    
    def __getattr__(self, name: str) -> Any:
        if not self._loaded:
            raise LazyImportError(
                f"Proxy dependencies not loaded. Call lazy_import_proxy_deps() first."
            )
        
        attr = getattr(self, name, None)
        if attr is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return attr


def lazy_import_proxy_deps() -> ProxyDependencies:
    """
    Lazy import proxy dependencies.
    
    Returns:
        ProxyDependencies: Container with imported proxy modules
        
    Raises:
        LazyImportError: If required proxy dependencies cannot be imported
    """
    deps = ProxyDependencies()
    
    try:
        # Import mitmproxy (optional)
        import mitmproxy
        deps.mitmproxy = mitmproxy
        logger.debug("Successfully imported mitmproxy")
        
    except ImportError:
        logger.warning(
            "mitmproxy not available. Proxy functionality will be limited. "
            "Install it with: pip install mitmproxy"
        )
        deps.mitmproxy = None
    
    # Import standard library modules (should always work)
    import subprocess
    import threading
    
    deps.subprocess = subprocess
    deps.threading = threading
    
    deps._loaded = True
    return deps


class FingerprintDependencies:
    """Container for fingerprint-related dependencies."""
    
    def __init__(self):
        self.tls_client: Optional[ModuleType] = None
        self.requests: Optional[ModuleType] = None
        self._loaded = False
    
    def __getattr__(self, name: str) -> Any:
        if not self._loaded:
            raise LazyImportError(
                f"Fingerprint dependencies not loaded. Call lazy_import_fingerprint_deps() first."
            )
        
        attr = getattr(self, name, None)
        if attr is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return attr


def lazy_import_fingerprint_deps() -> FingerprintDependencies:
    """
    Lazy import fingerprint dependencies.
    
    Returns:
        FingerprintDependencies: Container with imported fingerprint modules
        
    Raises:
        LazyImportError: If required fingerprint dependencies cannot be imported
    """
    deps = FingerprintDependencies()
    
    try:
        # Import tls_client for TLS fingerprinting
        import tls_client
        deps.tls_client = tls_client
        logger.debug("Successfully imported tls_client")
        
    except ImportError:
        logger.warning(
            "tls_client not available. TLS fingerprinting will be limited. "
            "Install it with: pip install tls-client"
        )
        deps.tls_client = None
    
    try:
        # Import requests as fallback
        import requests
        deps.requests = requests
        logger.debug("Successfully imported requests")
        
    except ImportError as e:
        raise LazyImportError(
            "requests is required for HTTP functionality. "
            "Install it with: pip install requests"
        ) from e
    
    deps._loaded = True
    return deps


def check_optional_dependencies() -> dict[str, bool]:
    """
    Check which optional dependencies are available.
    
    Returns:
        Dict mapping dependency names to availability status
    """
    dependencies = {
        "undetected_chromedriver": False,
        "selenium": False,
        "mitmproxy": False,
        "tls_client": False,
        "requests": False
    }
    
    # Check undetected_chromedriver
    try:
        import undetected_chromedriver
        dependencies["undetected_chromedriver"] = True
    except ImportError:
        pass
    
    # Check selenium
    try:
        from selenium.webdriver.common.by import By
        dependencies["selenium"] = True
    except ImportError:
        pass
    
    # Check mitmproxy
    try:
        import mitmproxy
        dependencies["mitmproxy"] = True
    except ImportError:
        pass
    
    # Check tls_client
    try:
        import tls_client
        dependencies["tls_client"] = True
    except ImportError:
        pass
    
    # Check requests
    try:
        import requests
        dependencies["requests"] = True
    except ImportError:
        pass
    
    return dependencies


def get_missing_dependencies() -> list[str]:
    """
    Get list of missing optional dependencies.
    
    Returns:
        List of missing dependency names
    """
    available = check_optional_dependencies()
    return [name for name, available in available.items() if not available]


def print_dependency_status() -> None:
    """Print status of all optional dependencies."""
    dependencies = check_optional_dependencies()
    
    print("NetStealth Dependency Status:")
    print("=" * 40)
    
    for name, available in dependencies.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"{name:25} {status}")
    
    missing = get_missing_dependencies()
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
    else:
        print("\n✅ All dependencies are available!")
