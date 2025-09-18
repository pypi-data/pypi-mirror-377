#!/usr/bin/env python3
"""
CLI entry point for hierarchy initialization
"""

import sys
import os
from pathlib import Path


def main():
    """Main CLI entry point for hierarchy initialization"""
    # Add current directory to path to find modules
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    # Import and run the initialize script
    try:
        from .initialize_dt_hierarchy import main as init_main

        return init_main()
    except ImportError as e:
        print(f"Error importing hierarchy initialization: {e}")
        print("Make sure you're in the correct directory and dependencies are installed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
