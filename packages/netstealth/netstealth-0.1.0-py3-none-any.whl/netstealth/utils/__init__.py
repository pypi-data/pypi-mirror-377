"""
Utility modules for netstealth.

This package contains utility functions and classes that support
the core netstealth functionality.
"""

from .lazy_imports import (
    LazyImportError,
    BrowserDependencies,
    ProxyDependencies,
    FingerprintDependencies,
    lazy_import_browser_deps,
    lazy_import_proxy_deps,
    lazy_import_fingerprint_deps,
    check_optional_dependencies,
    get_missing_dependencies,
    print_dependency_status
)

__all__ = [
    "LazyImportError",
    "BrowserDependencies",
    "ProxyDependencies", 
    "FingerprintDependencies",
    "lazy_import_browser_deps",
    "lazy_import_proxy_deps",
    "lazy_import_fingerprint_deps",
    "check_optional_dependencies",
    "get_missing_dependencies",
    "print_dependency_status"
]
