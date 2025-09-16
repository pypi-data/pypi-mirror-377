# NetStealth

Advanced stealth automation library with anti-detection browser control and proxy management.

## Overview

NetStealth is a Python library that provides comprehensive stealth capabilities for web automation. It's designed with SOLID principles and offers a service-agnostic foundation that can be extended for specific services like TIDAL, Spotify, YouTube Music, and more.

## Key Features

- **🕵️ Advanced Stealth Browser Automation**: Undetected Chrome automation with anti-detection measures
- **🔒 Browser Fingerprint Consistency**: Maintain consistent browser fingerprints across sessions
- **🤖 Human-like Behavior Simulation**: Realistic typing, mouse movements, and timing patterns
- **🌐 Proxy Integration**: Advanced proxy support with mitmproxy integration
- **🏗️ SOLID Architecture**: Extensible design following SOLID principles
- **📦 Modular Components**: Mix and match components based on your needs
- **🔧 Lazy Loading**: Optional dependencies loaded only when needed

## Installation

### Basic Installation
```bash
pip install netstealth
```

### With Browser Support
```bash
pip install netstealth[browser]
```

### With Full Features
```bash
pip install netstealth[full]
```

### Available Extras
- `browser`: Browser automation dependencies (undetected-chromedriver, selenium)
- `proxy`: Proxy management dependencies (mitmproxy)
- `fingerprint`: Fingerprint management dependencies (tls-client)
- `full`: All optional dependencies
- `dev`: Development dependencies

## Quick Start

### Basic Browser Automation

```python
from netstealth import StealthBrowserManager

# Create and initialize browser
browser = StealthBrowserManager(
    headless=False,
    debug_mode=True
)

browser.initialize()

# Navigate to a website
browser.navigate("https://example.com")

# Take a screenshot
browser.take_screenshot("example.png")

# Clean up
browser.cleanup()
```

### Using with Context Manager

```python
from netstealth import StealthBrowserManager

with StealthBrowserManager() as browser:
    browser.navigate("https://example.com")
    title = browser.get_page_title()
    print(f"Page title: {title}")
```

### Creating a Custom Session

```python
from netstealth import BaseStealthSession, StealthBrowserManager

class MyStealthSession(BaseStealthSession):
    def authenticate(self, credentials):
        # Implement your authentication logic
        return {"success": True}

# Create session with browser component
session = MyStealthSession()
browser = StealthBrowserManager(headless=True)

session.set_browser(browser)
session.initialize()

# Use the session
result = session.authenticate({"username": "user", "password": "pass"})
print(f"Auth result: {result}")

session.cleanup()
```

## Architecture

NetStealth follows SOLID principles with a clean separation of concerns:

### Core Interfaces
- `BrowserInterface`: Browser automation abstraction
- `ProxyInterface`: Proxy management abstraction  
- `AuthProvider`: Authentication provider abstraction
- `APIClient`: API client abstraction
- `StealthComponent`: Component lifecycle management

### Base Classes
- `BaseStealthSession`: Foundation for service-specific sessions
- `StealthBrowserManager`: Concrete browser implementation

### Components
- **Browser**: Undetected Chrome automation with stealth measures
- **Proxy**: mitmproxy integration for traffic management
- **Fingerprint**: TLS and browser fingerprint consistency
- **Human Behavior**: Realistic interaction simulation

## Extending NetStealth

NetStealth is designed to be extended for specific services:

```python
from netstealth import BaseStealthSession, AuthProvider

class MyServiceAuthProvider(AuthProvider):
    def authenticate(self, credentials):
        # Service-specific authentication
        pass
    
    def refresh_auth(self, refresh_token):
        # Token refresh logic
        pass

class MyServiceSession(BaseStealthSession):
    def __init__(self):
        super().__init__()
        self.set_auth_provider(MyServiceAuthProvider())
    
    def authenticate(self, credentials):
        return self.auth_provider.authenticate(credentials)
```

## Dependency Management

NetStealth uses lazy loading for optional dependencies. Check what's available:

```python
from netstealth import check_optional_dependencies, print_dependency_status

# Check programmatically
deps = check_optional_dependencies()
print(deps)

# Print status
print_dependency_status()
```

Or use the CLI command:
```bash
netstealth-check
```

## Configuration

### Browser Configuration
```python
browser = StealthBrowserManager(
    proxy_port=8080,
    headless=False,
    debug_mode=True,
    user_agent_hint="music-streaming",
    window_size=(1920, 1080)
)
```

### Session Configuration
```python
config = {
    "log_level": "DEBUG",
    "browser": {
        "headless": True,
        "proxy_port": 8080
    }
}

session = MySession(config=config)
```

## Error Handling

NetStealth provides comprehensive error handling:

```python
from netstealth import BrowserError, handle_exception

try:
    browser.navigate("https://example.com")
except BrowserError as e:
    print(f"Browser error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Context: {e.context}")
```

## Logging

Configure logging for debugging:

```python
from netstealth import setup_logging

# Enable debug logging with colors
setup_logging(level="DEBUG", enable_colors=True)
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/netstealth/netstealth
cd netstealth
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black netstealth/
isort netstealth/
```

### Version Management

```bash
# Bump version
bump2version patch  # 0.1.0 → 0.1.1
bump2version minor  # 0.1.0 → 0.2.0
bump2version major  # 0.1.0 → 1.0.0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related Projects

- **tidal-net**: TIDAL-specific extension of NetStealth
- **netstealth-analyzer**: Log analysis tools for stealth operations

## Support

- 📖 [Documentation](https://netstealth.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/netstealth/netstealth/issues)
- 💬 [Discussions](https://github.com/netstealth/netstealth/discussions)
