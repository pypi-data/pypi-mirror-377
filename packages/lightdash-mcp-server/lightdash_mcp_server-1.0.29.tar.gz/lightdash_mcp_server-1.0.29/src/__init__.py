"""Lightdash MCP Server Bridge"""

__version__ = "1.0.0"

from .client import LightdashClient
from .main import app

__all__ = ["LightdashClient", "app"]