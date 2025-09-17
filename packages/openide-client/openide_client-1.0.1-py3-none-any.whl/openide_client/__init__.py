"""
OpenIDE Client Library
Python библиотека для взаимодействия с OpenIDE API
"""

from .client import (
    OpenIDEClient,
    OpenIDEAPIClient,
    OpenIDEConfig,
    create_client,
    create_api_client
)

__version__ = "1.0.1"
__author__ = "ArtemJS"
__email__ = "artemjs@example.com"
__description__ = "Python client library for OpenIDE container system"

__all__ = [
    "OpenIDEClient",
    "OpenIDEAPIClient", 
    "OpenIDEConfig",
    "create_client",
    "create_api_client",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]
