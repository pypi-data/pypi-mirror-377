"""
SBOM Upload Validator

A production-ready API service for GitLab pipeline SBOM uploads to OWASP Dependency-Track
with hierarchical project management and federal network support.

This package provides:
- Flask API server for SBOM uploads
- Dependency-Track API client
- Hierarchical project management
- YAML-based bulk configuration
- Federal network deployment templates
"""

__version__ = "1.0.0"
__author__ = "SBOM Upload Validator Project"
__email__ = "sbom-validator@example.com"
__license__ = "Apache-2.0"

# Public API exports
from .dt_api_client import DependencyTrackAPI
from .hierarchy_manager import ProjectHierarchyManager
from .config_loader import DTConfigLoader

# Version info
try:
    # Handle release candidates and other pre-release versions
    base_version = __version__.split("rc")[0].split("a")[0].split("b")[0]
    VERSION_INFO = tuple(map(int, base_version.split(".")))
except ValueError:
    VERSION_INFO = (1, 0, 0)

__all__ = [
    "DependencyTrackAPI",
    "ProjectHierarchyManager",
    "DTConfigLoader",
    "__version__",
    "VERSION_INFO",
]
