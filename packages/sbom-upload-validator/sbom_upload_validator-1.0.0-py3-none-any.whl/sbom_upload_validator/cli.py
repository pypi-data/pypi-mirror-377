#!/usr/bin/env python3
"""
CLI entry point for SBOM Upload Validator server
"""

import argparse
import os
import sys
from pathlib import Path


def main():
    """Main CLI entry point for SBOM validator server"""
    parser = argparse.ArgumentParser(
        description="SBOM Upload Validator API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sbom-validator                           # Start server with default settings
  sbom-validator --port 8080              # Start server on port 8080
  sbom-validator --host 0.0.0.0           # Bind to all interfaces
  sbom-validator --debug                  # Enable debug mode
        """,
    )

    parser.add_argument(
        "--host", "-H", default="127.0.0.1", help="Host to bind server to (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.environ.get("PORT", "8888")),
        help="Port to run server on (default: 8888)",
    )

    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")

    parser.add_argument("--config", "-c", help="Path to configuration file")

    args = parser.parse_args()

    # Import Flask app (after args parsing to catch import errors early)
    try:
        # Add current directory to path to find modules
        current_dir = Path(__file__).parent.parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        from app import app
    except ImportError as e:
        print(f"Error importing Flask application: {e}")
        print("Make sure you're in the correct directory and dependencies are installed.")
        return 1

    print(f"🚀 Starting SBOM Upload Validator API server")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Debug: {args.debug}")
    print(f"   Environment: {'development' if args.debug else 'production'}")
    print()

    try:
        # Set environment variables
        if args.debug:
            os.environ["FLASK_ENV"] = "development"

        # Start Flask application
        app.run(host=args.host, port=args.port, debug=args.debug)

    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
