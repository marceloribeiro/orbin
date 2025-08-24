"""
Orbin CLI - Command Line Interface for the Orbin framework.

Provides generators and utilities for building AI-powered chat applications.
"""

import sys
import argparse
from typing import Optional
from .generators.app_generator import AppGenerator


def create_app(app_name: str, target_dir: Optional[str] = None):
    """Create a new Orbin application."""
    generator = AppGenerator(app_name, target_dir)
    generator.generate()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Orbin - Framework for AI-powered chat applications",
        prog="orbin"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new Orbin application")
    create_parser.add_argument("app_name", help="Name of the application to create")
    create_parser.add_argument(
        "--dir", 
        help="Target directory (defaults to current directory)",
        default=None
    )
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show Orbin version")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_app(args.app_name, args.dir)
    elif args.command == "version":
        from . import __version__
        print(f"Orbin {__version__}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
