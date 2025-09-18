#!/usr/bin/env python3
"""
Setup script for SBOM Upload Validator PyPI package
"""

from setuptools import setup, find_packages
import os


# Read version from __init__.py
def get_version():
    """Get version from package __init__.py"""
    import re

    with open(os.path.join("sbom_upload_validator", "__init__.py"), "r") as f:
        content = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


# Read long description from README
def get_long_description():
    """Get long description from README.md"""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "SBOM Upload Validator for Dependency-Track integration"


setup(
    name="sbom-upload-validator",
    version=get_version(),
    author="SBOM Upload Validator Project",
    author_email="sbom-validator@example.com",
    description="Production-ready API for GitLab SBOM uploads to Dependency-Track with hierarchical management",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/StL-Jim/sbom-upload-validator",
    project_urls={
        "Bug Reports": "https://github.com/StL-Jim/sbom-upload-validator/issues",
        "Source": "https://github.com/StL-Jim/sbom-upload-validator",
        "Documentation": "https://github.com/StL-Jim/sbom-upload-validator/blob/main/README.md",
        "Docker Hub": "https://hub.docker.com/r/stljim/sbom-upload-validator",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Environment :: Web Environment",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.3.0,<3.0.0",
        "requests>=2.31.0,<3.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "PyYAML>=6.0.0,<7.0.0",
        "Werkzeug>=2.3.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docker": [
            "gunicorn>=21.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sbom-validator=sbom_upload_validator.cli:main",
            "dt-hierarchy-init=sbom_upload_validator.hierarchy_cli:main",
            "dt-config-validate=sbom_upload_validator.config_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sbom_upload_validator": [
            "templates/*.html",
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    zip_safe=False,
    keywords=[
        "sbom",
        "software bill of materials",
        "dependency-track",
        "owasp",
        "security",
        "vulnerability",
        "gitlab",
        "cicd",
        "federal",
        "compliance",
        "api",
        "flask",
    ],
)
