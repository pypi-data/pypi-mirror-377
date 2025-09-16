"""
Stealth browser management component.

This module provides enhanced undetected_chromedriver functionality
with generic stealth configurations, extracted from the original
tidal_stealth implementation and made service-agnostic.
"""

import os
import time
import random
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

from ..core.interfaces import BrowserInterface, StealthComponent
from ..core.exceptions import BrowserError, ComponentError, ErrorCodes, handle_exception
from ..utils.lazy_imports import lazy_import_browser_deps


class StealthBrowserManager:
    """
    Enhanced stealth browser management with SOLID principles.
    
    This class implements both BrowserInterface and StealthComponent protocols,
    providing generic stealth browser functionality that can be used by any
    service-specific implementation.
    
    Key features:
    - Undetected Chrome automation
    - Advanced anti-detection measures
    - Proxy integration support
    - Fingerprint consistency
    - Comprehensive logging and debugging
    """
    
    def __init__(
        self,
        proxy_port: Optional[int] = None,
        proxy_host: str = "localhost",
        headless: bool = False,
        debug_mode: bool = False,
        logs_dir: Optional[Path] = None,
        user_agent_hint: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        window_size: Optional[tuple[int, int]] = None
    ):
        """
        Initialize stealth browser manager.
        
        Args:
            proxy_port: Proxy port to use (if any)
            proxy_host: Proxy hostname (default: localhost)
            headless: Run browser in headless mode
            debug_mode: Enable debug logging and features
            logs_dir: Directory for debug logs and screenshots
            user_agent_hint: Hint for user agent selection (e.g., "music-streaming")
            extra_headers: Additional headers to set
            window_size: Custom window size (width, height)
        """
        self.proxy_port = proxy_port
        self.proxy_host = proxy_host
        self.headless = headless
        self.debug_mode = debug_mode
        self.logs_dir = logs_dir or Path("logs") / "browser"
        self.user_agent_hint = user_agent_hint
        self.extra_headers = extra_headers or {}
        self.window_size = window_size
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Browser state
        self.driver = None
        self._initialized = False
        self._browser_deps = None
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
        
        # Browser fingerprint data
        self.fingerprint_data: Dict[str, Any] = {}
        
        self.logger.info("StealthBrowserManager initialized")
    
    # StealthComponent Protocol Implementation
    
    def initialize(self) -> None:
        """Initialize the browser component."""
        if self._initialized:
            self.logger.warning("Browser already initialized")
            return
        
        try:
            self.logger.info("Initializing stealth browser...")
            
            # Lazy load browser dependencies
            self._browser_deps = lazy_import_browser_deps()
            
            # Create and configure browser
            options = self._create_chrome_options()
            
            # Create undetected Chrome instance
            self.driver = self._browser_deps.uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect installed Chrome version
                driver_executable_path=None  # Use auto-downloaded driver
            )
            
            # Apply additional stealth measures
            self._apply_stealth_scripts()
            
            # Enable network monitoring
            self._enable_network_monitoring()
            
            self._initialized = True
            self.logger.info("Stealth browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Browser initialization failed: {e}")
            handle_exception(
                e,
                context={
                    "component": "StealthBrowserManager",
                    "proxy_port": self.proxy_port,
                    "headless": self.headless
                },
                reraise_as=ComponentError
            )
    
    def cleanup(self) -> None:
        """Clean up browser resources."""
        if not self._initialized:
            return
        
        self.logger.info("Cleaning up stealth browser...")
        
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            self.logger.warning(f"Error during browser cleanup: {e}")
        finally:
            self._initialized = False
            self.logger.info("Browser cleanup completed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current browser status."""
        return {
            "healthy": self.is_running(),
            "initialized": self._initialized,
            "running": self.is_running(),
            "headless": self.headless,
            "proxy_configured": self.proxy_port is not None,
            "current_url": self.get_current_url() if self.is_running() else None,
            "page_title": self.get_page_title() if self.is_running() else None,
            "window_size": self._get_window_size() if self.is_running() else None
        }
    
    # BrowserInterface Protocol Implementation
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL with error handling.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if navigation successful
        """
        if not self.is_running():
            raise BrowserError(
                "Browser not running",
                browser_state="not_running",
                error_code=ErrorCodes.BROWSER_STARTUP_FAILED
            )
        
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page load
            self._browser_deps.WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Log navigation result
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            self.logger.info(f"Navigation completed - Title: {page_title}")
            self.logger.debug(f"Current URL: {current_url}")
            
            return True
            
        except self._browser_deps.TimeoutException:
            self.logger.error("Timeout waiting for page load")
            raise BrowserError(
                "Page load timeout",
                url=url,
                browser_state="timeout",
                error_code=ErrorCodes.BROWSER_NAVIGATION_FAILED
            )
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            raise BrowserError(
                f"Navigation failed: {e}",
                url=url,
                browser_state="error",
                error_code=ErrorCodes.BROWSER_NAVIGATION_FAILED
            ) from e
    
    def execute_script(self, script: str) -> Any:
        """
        Execute JavaScript in browser context.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Script execution result
        """
        if not self.is_running():
            raise BrowserError("Browser not running")
        
        try:
            result = self.driver.execute_script(script)
            self.logger.debug(f"Script executed successfully: {script[:100]}...")
            return result
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
            raise BrowserError(
                f"Script execution failed: {e}",
                error_code=ErrorCodes.SCRIPT_EXECUTION_FAILED
            ) from e
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
        """
        Wait for element to be present.
        
        Args:
            selector: CSS selector for the element
            timeout: Wait timeout in seconds
            
        Returns:
            WebElement if found
            
        Raises:
            BrowserError: If element not found within timeout
        """
        if not self.is_running():
            raise BrowserError("Browser not running")
        
        try:
            element = self._browser_deps.WebDriverWait(self.driver, timeout).until(
                self._browser_deps.EC.presence_of_element_located(
                    (self._browser_deps.By.CSS_SELECTOR, selector)
                )
            )
            self.logger.debug(f"Element found: {selector}")
            return element
        except self._browser_deps.TimeoutException:
            self.logger.error(f"Element not found within {timeout}s: {selector}")
            raise BrowserError(
                f"Element not found: {selector}",
                browser_state="element_not_found",
                error_code=ErrorCodes.ELEMENT_NOT_FOUND
            )
    
    def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Take screenshot for debugging.
        
        Args:
            filename: Screenshot filename (auto-generated if None)
            
        Returns:
            Screenshot file path or None if failed
        """
        if not self.is_running():
            return None
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = self.logs_dir / filename
            self.driver.save_screenshot(str(screenshot_path))
            
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
    
    # Additional Browser Methods
    
    def get_current_url(self) -> str:
        """Get current browser URL."""
        if not self.is_running():
            return ""
        try:
            return self.driver.current_url
        except Exception:
            return ""
    
    def get_page_title(self) -> str:
        """Get current page title."""
        if not self.is_running():
            return ""
        try:
            return self.driver.title
        except Exception:
            return ""
    
    def get_console_logs(self) -> list:
        """Get browser console logs for debugging."""
        if not self.is_running():
            return []
        
        try:
            logs = self.driver.get_log('browser')
            return logs
        except Exception as e:
            self.logger.debug(f"Could not get console logs: {e}")
            return []
    
    def is_running(self) -> bool:
        """Check if browser is running."""
        return self._initialized and self.driver is not None
    
    # Private Implementation Methods
    
    def _create_chrome_options(self):
        """Create Chrome options with stealth configuration."""
        options = self._browser_deps.uc.ChromeOptions()
        
        # Proxy configuration
        if self.proxy_port:
            proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
            options.add_argument(f'--proxy-server={proxy_url}')
            self.logger.info(f"Browser configured to use proxy: {proxy_url}")
            
            # Certificate handling for proxy
            options.add_argument('--ignore-certificate-errors-spki-list')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-web-security')
        
        # Enhanced stealth options
        stealth_args = [
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-translate',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-client-side-phishing-detection',
            '--disable-sync',
            '--metrics-recording-only',
            '--no-report-upload',
            '--disable-blink-features=AutomationControlled'
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
        
        # User data directory for session persistence
        user_data_dir = Path("browser_data")
        user_data_dir.mkdir(exist_ok=True)
        options.add_argument(f'--user-data-dir={user_data_dir.absolute()}')
        
        # Debug logging
        if self.debug_mode:
            options.add_argument('--enable-logging')
            options.add_argument('--log-level=0')
            log_file = self.logs_dir / "chrome_debug.log"
            options.add_argument(f'--log-file={log_file}')
        
        # Window configuration
        if self.headless:
            options.add_argument('--headless=new')
        else:
            if self.window_size:
                width, height = self.window_size
            else:
                # Randomize window size slightly (anti-fingerprinting)
                width = random.randint(1200, 1920)
                height = random.randint(800, 1080)
            
            options.add_argument(f'--window-size={width},{height}')
            options.add_argument('--start-maximized')
        
        return options
    
    def _apply_stealth_scripts(self) -> None:
        """Apply additional JavaScript stealth measures."""
        try:
            stealth_script = '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override plugins to look realistic
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {0: {type: "application/x-google-chrome-pdf", suffixes: "pdf"}},
                        {0: {type: "application/pdf", suffixes: "pdf"}}
                    ]
                });
                
                // Add realistic permissions handling
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Override chrome runtime
                if (window.chrome && window.chrome.runtime) {
                    Object.defineProperty(window.chrome.runtime, 'onConnect', {
                        value: undefined
                    });
                }
            '''
            
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_script
            })
            
            self.logger.debug("Applied stealth JavaScript overrides")
            
        except Exception as e:
            self.logger.warning(f"Failed to apply some stealth scripts: {e}")
    
    def _enable_network_monitoring(self) -> None:
        """Enable network monitoring for debugging and analysis."""
        try:
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Page.enable', {})
            self.logger.debug("Network monitoring enabled")
        except Exception as e:
            self.logger.warning(f"Failed to enable network monitoring: {e}")
    
    def _get_window_size(self) -> Optional[Dict[str, int]]:
        """Get current window size."""
        if not self.is_running():
            return None
        
        try:
            size = self.driver.get_window_size()
            return {"width": size["width"], "height": size["height"]}
        except Exception:
            return None
