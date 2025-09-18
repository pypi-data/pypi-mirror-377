"""
Dependency-Track API Client Module

This module provides the DependencyTrackAPI class for interacting with
OWASP Dependency-Track REST API.
"""

from .dt_api_utils import DependencyTrackAPI

# Re-export for package users
__all__ = ["DependencyTrackAPI"]
