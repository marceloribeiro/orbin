"""
Orbin CLI - Command Line Interface for the Orbin framework.

Provides generators and utilities for building AI-powered chat applications.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List
from .generators.app_generator import AppGenerator
from .generators.model_generator import ModelGenerator
from .database import create_database, migrate_database


def is_orbin_app() -> bool:
    """Check if current directory is an Orbin application."""
    current_dir = Path.cwd()
    
    # Check for Orbin app indicators
    indicators = [
        current_dir / "app" / "main.py",
        current_dir / "config" / "settings.py",
        current_dir / "pyproject.toml"
    ]
    
    return all(indicator.exists() for indicator in indicators)


def get_app_name() -> str:
    """Get the application name from the current directory."""
    try:
        # Try to get from settings.py
        settings_path = Path.cwd() / "config" / "settings.py"
        if settings_path.exists():
            content = settings_path.read_text()
            for line in content.split('\n'):
                if 'APP_NAME:' in line and '=' in line:
                    # Extract app name from line like: APP_NAME: str = "my_app"
                    return line.split('"')[1]
    except:
        pass
    
    # Fallback to directory name
    return Path.cwd().name


def create_app(app_name: str, target_dir: Optional[str] = None):
    """Create a new Orbin application."""
    generator = AppGenerator(app_name, target_dir)
    generator.generate()


def generate_model(model_name: str, attributes: List[str]):
    """Generate a new model with migration."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    generator = ModelGenerator(model_name, attributes)
    generator.generate()


def db_create():
    """Create the PostgreSQL database."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    success = create_database()
    if not success:
        sys.exit(1)


def db_migrate():
    """Run database migrations."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    success = migrate_database()
    if not success:
        sys.exit(1)


def start_server(bind: str = "127.0.0.1", port: int = 8000):
    """Start the development server."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    app_name = get_app_name()
    print(f"🚀 Starting {app_name} server on {bind}:{port}")
    print(f"📖 API docs: http://{bind}:{port}/docs")
    print(f"🔄 ReDoc: http://{bind}:{port}/redoc")
    print(f"⚡ Press Ctrl+C to stop the server")
    
    try:
        # Use uvicorn to start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--host", bind,
            "--port", str(port),
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


def start_console():
    """Start an interactive Python console with app context."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    app_name = get_app_name()
    print(f"🐍 Starting interactive console for {app_name}")
    print("📦 Available imports:")
    print("  - app.main (FastAPI app)")
    print("  - config.settings (App settings)")
    print("  - config.database (Database connection)")
    
    # Create startup script for the console
    startup_script = """
# Orbin Console - Auto-imports
import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Import common modules
try:
    from app.main import app
    print("✅ Imported: app (FastAPI application)")
except ImportError as e:
    print(f"⚠️  Could not import app.main: {e}")

try:
    from config.settings import settings
    print("✅ Imported: settings (Application settings)")
except ImportError as e:
    print(f"⚠️  Could not import config.settings: {e}")

try:
    from config.database import get_db, Base, engine
    print("✅ Imported: get_db, Base, engine (Database)")
except ImportError as e:
    print(f"⚠️  Could not import config.database: {e}")

# Try to import SQLAlchemy session
try:
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    print("✅ Imported: session (Database session)")
except ImportError as e:
    print(f"⚠️  Could not create database session: {e}")

print("\\n🎯 Ready! Try: app.title, settings.APP_NAME, or session.execute('SELECT 1')")
print("📚 Type help() for Python help, or dir() to see available objects")
"""
    
    # Write startup script to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(startup_script)
        startup_file = f.name
    
    try:
        # Start IPython if available, otherwise fall back to standard Python
        try:
            subprocess.run([
                sys.executable, "-c", 
                f"import IPython; IPython.start_ipython(argv=['-i', '{startup_file}'])"
            ], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to standard Python REPL
            print("📝 IPython not available, using standard Python console")
            subprocess.run([
                sys.executable, "-i", startup_file
            ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Console closed")
    finally:
        # Clean up temp file
        try:
            os.unlink(startup_file)
        except:
            pass


def main():
    """Main CLI entry point."""
    in_app = is_orbin_app()
    
    if in_app:
        app_name = get_app_name()
        parser = argparse.ArgumentParser(
            description=f"Orbin - {app_name} application commands",
            prog="orbin"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Server command
        server_parser = subparsers.add_parser(
            "server", 
            aliases=["s"],
            help="Start the development server"
        )
        server_parser.add_argument(
            "-p", "--port",
            type=int,
            default=8000,
            help="Port to run the server on (default: 8000)"
        )
        server_parser.add_argument(
            "-b", "--bind",
            default="127.0.0.1",
            help="IP address to bind to (default: 127.0.0.1)"
        )
        
        # Console command
        console_parser = subparsers.add_parser(
            "console",
            aliases=["c"],
            help="Start interactive Python console with app context"
        )
        
        # Generate command group
        generate_parser = subparsers.add_parser("generate", aliases=["g"], help="Generate code")
        generate_subparsers = generate_parser.add_subparsers(dest="generate_type", help="What to generate")
        
        # Generate model command
        model_parser = generate_subparsers.add_parser("model", help="Generate a model with migration")
        model_parser.add_argument("model_name", help="Name of the model (singular or plural)")
        model_parser.add_argument("attributes", nargs="*", help="Model attributes (e.g., name:string age:integer)")
        
        # Database commands
        db_create_parser = subparsers.add_parser("db-create", help="Create the PostgreSQL database")
        db_migrate_parser = subparsers.add_parser("db-migrate", help="Run database migrations")
        
        # Version command
        version_parser = subparsers.add_parser("version", help="Show Orbin version")
        
    else:
        # Outside app context - show framework commands
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
    
    if args.command in ["create"]:
        if in_app:
            print("❌ Error: Cannot create app from within an existing app directory")
            sys.exit(1)
        create_app(args.app_name, args.dir)
    elif args.command in ["server", "s"]:
        start_server(args.bind, args.port)
    elif args.command in ["console", "c"]:
        start_console()
    elif args.command in ["generate", "g"]:
        if args.generate_type == "model":
            generate_model(args.model_name, args.attributes)
        else:
            print("❌ Error: Unknown generate type. Available: model")
            sys.exit(1)
    elif args.command == "db-create":
        db_create()
    elif args.command == "db-migrate":
        db_migrate()
    elif args.command == "version":
        from . import __version__
        print(f"Orbin {__version__}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
