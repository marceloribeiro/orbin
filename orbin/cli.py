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
from .generators.controller_generator import ControllerGenerator
from .generators.resource_generator import ResourceGenerator
from .generators.scaffold_generator import ScaffoldGenerator
from .database import create_database, migrate_database, prepare_test_database


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


def generate_controller(controller_name: str, actions: List[str]):
    """Generate a new controller with specified actions."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    generator = ControllerGenerator(controller_name, actions)
    generator.generate()


def generate_resource(model_name: str):
    """Generate a RESTful controller for an existing model."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    generator = ResourceGenerator(model_name)
    generator.generate()


def generate_scaffold(model_name: str, attributes: List[str]):
    """Generate complete CRUD scaffolding: model + migration + controller."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    generator = ScaffoldGenerator(model_name, attributes)
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


def db_test_prepare():
    """Prepare test database by recreating it as a schema copy of development database."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    success = prepare_test_database()
    if not success:
        sys.exit(1)


def db_console():
    """Open an interactive database console using psql."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    # Load database URL from environment
    from dotenv import load_dotenv
    load_dotenv(Path.cwd() / ".env")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment variables or .env file")
        print("💡 Tip: Make sure your .env file contains DATABASE_URL")
        sys.exit(1)
    
    app_name = get_app_name()
    print(f"🗃️  Opening database console for {app_name}")
    print("💡 Type \\q to exit the console")
    print("📚 Common commands: \\dt (list tables), \\d table_name (describe table)")
    print()
    
    try:
        # Use psql to connect to the database
        subprocess.run([
            "psql", 
            database_url
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error opening database console: {e}")
        print("💡 Make sure PostgreSQL client (psql) is installed")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: psql command not found")
        print("💡 Please install PostgreSQL client tools:")
        print("   - macOS: brew install postgresql")
        print("   - Ubuntu: sudo apt-get install postgresql-client")
        print("   - Windows: Download from https://www.postgresql.org/download/")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Database console closed")


def redis_console():
    """Open an interactive Redis console using redis-cli."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    # Load Redis URL from environment
    from dotenv import load_dotenv
    load_dotenv(Path.cwd() / ".env")
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app_name = get_app_name()
    print(f"🔴 Opening Redis console for {app_name}")
    print("💡 Type quit to exit the console")
    print("📚 Common commands: KEYS *, GET key, SET key value, INFO")
    print()
    
    try:
        # Parse Redis URL for redis-cli
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)
        
        cmd = ["redis-cli"]
        if parsed.hostname:
            cmd.extend(["-h", parsed.hostname])
        if parsed.port:
            cmd.extend(["-p", str(parsed.port)])
        if parsed.password:
            cmd.extend(["-a", parsed.password])
        if parsed.path and len(parsed.path) > 1:
            db = parsed.path.lstrip('/')
            cmd.extend(["-n", db])
        
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error opening Redis console: {e}")
        print("💡 Make sure Redis client (redis-cli) is installed")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: redis-cli command not found")
        print("💡 Please install Redis client tools:")
        print("   - macOS: brew install redis")
        print("   - Ubuntu: sudo apt-get install redis-tools")
        print("   - Windows: Download from https://redis.io/download")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Redis console closed")


def redis_ping():
    """Test Redis connection."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    try:
        # Add current directory to Python path to import app modules
        sys.path.insert(0, os.getcwd())
        
        from orbin.redis_client import get_redis_client
        from dotenv import load_dotenv
        load_dotenv(Path.cwd() / ".env")
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        print("🔴 Testing Redis connection...")
        client = get_redis_client(redis_url)
        
        if client.ping():
            info = client.get_info()
            print("✅ Redis connection successful!")
            print(f"📊 Redis version: {info.get('redis_version', 'unknown')}")
            print(f"🗃️  Connected clients: {info.get('connected_clients', 'unknown')}")
            print(f"💾 Used memory: {info.get('used_memory_human', 'unknown')}")
        else:
            print("❌ Redis connection failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")
        print("💡 Make sure Redis server is running and connection details are correct")
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


def run_tests(test_path: Optional[str] = None, verbose: bool = False, skip_prepare: bool = False):
    """Run tests using pytest."""
    if not is_orbin_app():
        print("❌ Error: Not in an Orbin application directory")
        print("Run this command from within an Orbin app directory")
        sys.exit(1)
    
    app_name = get_app_name()
    print(f"🧪 Running tests for {app_name}")
    
    # Prepare test database unless skipped
    if not skip_prepare:
        print("🔄 Preparing test database...")
        if not prepare_test_database():
            print("❌ Failed to prepare test database")
            sys.exit(1)
        print()
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test path or default to tests directory
    if test_path:
        cmd.append(test_path)
    else:
        tests_dir = Path.cwd() / "tests"
        if tests_dir.exists():
            cmd.append("tests/")
        else:
            print("❌ Error: tests/ directory not found")
            print("💡 Tip: Generate some controllers to create tests")
            sys.exit(1)
    
    # Add verbose flag if requested
    if verbose:
        cmd.extend(["-v", "--tb=short"])
    else:
        cmd.extend(["--tb=short"])
    
    # Add coverage if available
    try:
        import pytest_cov
        cmd.extend(["--cov=app", "--cov-report=term-missing"])
        print("📊 Running with coverage analysis")
    except ImportError:
        print("💡 Tip: Install pytest-cov for coverage reports: pip install pytest-cov")
    
    print(f"🔍 Command: {' '.join(cmd[2:])}")
    print()
    
    try:
        # Run pytest
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
            sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted")
        sys.exit(1)


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
    print("  - config.redis (Redis client)")
    
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

try:
    from config.redis import redis_client, cache_set, cache_get
    print("✅ Imported: redis_client, cache_set, cache_get (Redis)")
except ImportError as e:
    print(f"⚠️  Could not import config.redis: {e}")

# Try to import SQLAlchemy session
try:
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    print("✅ Imported: session (Database session)")
except ImportError as e:
    print(f"⚠️  Could not create database session: {e}")

print("\\n🎯 Ready! Try: app.title, settings.APP_NAME, redis_client.ping(), or session.execute('SELECT 1')")
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
        
        # Test command
        test_parser = subparsers.add_parser(
            "test",
            aliases=["t"],
            help="Run tests using pytest"
        )
        test_parser.add_argument(
            "test_path",
            nargs="?",
            help="Specific test file or directory (defaults to tests/)"
        )
        test_parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Run tests in verbose mode"
        )
        test_parser.add_argument(
            "--skip-prepare",
            action="store_true",
            help="Skip test database preparation (faster for repeated test runs)"
        )
        
        # Generate command group
        generate_parser = subparsers.add_parser("generate", aliases=["g"], help="Generate code")
        generate_subparsers = generate_parser.add_subparsers(dest="generate_type", help="What to generate")
        
        # Generate model command
        model_parser = generate_subparsers.add_parser("model", help="Generate a model with migration")
        model_parser.add_argument("model_name", help="Name of the model (singular or plural)")
        model_parser.add_argument("attributes", nargs="*", help="Model attributes (e.g., name:string age:integer)")
        
        # Generate controller command
        controller_parser = generate_subparsers.add_parser("controller", help="Generate a controller with actions")
        controller_parser.add_argument("controller_name", help="Name of the controller (e.g., Users, PostsController)")
        controller_parser.add_argument("actions", nargs="*", help="Controller actions (e.g., index show create update destroy)")
        
        # Set default actions if none provided
        controller_parser.set_defaults(actions=["index", "show", "create", "update", "destroy"])
        
        # Generate resource command
        resource_parser = generate_subparsers.add_parser("resource", help="Generate RESTful controller for existing model")
        resource_parser.add_argument("model_name", help="Name of the existing model (e.g., User, Post)")
        
        # Generate scaffold command
        scaffold_parser = generate_subparsers.add_parser("scaffold", help="Generate model + migration + RESTful controller")
        scaffold_parser.add_argument("model_name", help="Name of the model to create (e.g., User, Post)")
        scaffold_parser.add_argument("attributes", nargs="*", help="Model attributes (e.g., name:string email:string)")
        
        # Database commands
        db_create_parser = subparsers.add_parser("db-create", help="Create the PostgreSQL databases (development and test)")
        db_migrate_parser = subparsers.add_parser("db-migrate", help="Run database migrations")
        db_test_prepare_parser = subparsers.add_parser("db-test-prepare", help="Prepare test database as schema copy of development database")
        db_console_parser = subparsers.add_parser("db", help="Open interactive database console (psql)")
        
        # Redis commands
        redis_console_parser = subparsers.add_parser("redis", help="Open interactive Redis console (redis-cli)")
        redis_ping_parser = subparsers.add_parser("redis-ping", help="Test Redis connection")
        
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
    elif args.command in ["test", "t"]:
        run_tests(args.test_path, args.verbose, args.skip_prepare)
    elif args.command in ["generate", "g"]:
        if args.generate_type == "model":
            generate_model(args.model_name, args.attributes)
        elif args.generate_type == "controller":
            # Use default actions if none provided
            actions = args.actions if args.actions else ["index", "show", "create", "update", "destroy"]
            generate_controller(args.controller_name, actions)
        elif args.generate_type == "resource":
            generate_resource(args.model_name)
        elif args.generate_type == "scaffold":
            generate_scaffold(args.model_name, args.attributes)
        else:
            print("❌ Error: Unknown generate type. Available: model, controller, resource, scaffold")
            sys.exit(1)
    elif args.command == "db-create":
        db_create()
    elif args.command == "db-migrate":
        db_migrate()
    elif args.command == "db-test-prepare":
        db_test_prepare()
    elif args.command == "db":
        db_console()
    elif args.command == "redis":
        redis_console()
    elif args.command == "redis-ping":
        redis_ping()
    elif args.command == "version":
        from . import __version__
        print(f"Orbin {__version__}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
