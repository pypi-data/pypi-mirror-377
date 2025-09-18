#!/usr/bin/env python3
"""
CLI entry point for configuration validation
"""

import sys
import os
from pathlib import Path


def main():
    """Main CLI entry point for configuration validation"""
    # Add current directory to path to find modules
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    # Import and run the config loader script
    try:
        from .dt_config_loader import main as config_main

        return config_main()
    except ImportError as e:
        print(f"Error importing configuration loader: {e}")
        print("Make sure you're in the correct directory and dependencies are installed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
