"""
Template-based App Generator for Orbin framework.

Creates the initial application structure using Jinja2 templates.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import shutil

from .base_generator import BaseGenerator


class AppGenerator(BaseGenerator):
    """Generator for creating new Orbin applications using templates."""
    
    def __init__(self, app_name: str, target_dir: Optional[str] = None):
        """
        Initialize the app generator.
        
        Args:
            app_name: Name of the application to create
            target_dir: Target directory (defaults to current directory)
        """
        # Validate app name
        if not app_name.isidentifier():
            raise ValueError(f"App name '{app_name}' is not a valid Python identifier")
        
        self.app_name = app_name
        super().__init__(app_name, target_dir)
    
    def _build_context(self) -> Dict[str, Any]:
        """Build the template context for app generation."""
        return {
            "app_name": self.app_name,
            "timestamp": datetime.now().isoformat(),
            "year": datetime.now().year,
        }
    
    def generate(self):
        """Generate the complete application structure."""
        print(f"Creating Orbin application '{self.app_name}'...")
        
        # Check if directory already exists
        if self.output_path.exists():
            print(f"Error: Directory '{self.output_path}' already exists!")
            sys.exit(1)
        
        try:
            # Create directory structure
            self._create_directory_structure()
            
            # Copy all template files
            self._copy_template_files()
            
            # Set up virtual environment and install dependencies
            self._setup_environment()
            
            # Set up database migrations
            self._setup_database()
            
            # Print success message
            self._print_success_message()
            
        except Exception as e:
            print(f"❌ Error creating application: {e}")
            # Clean up on failure
            if self.output_path.exists():
                shutil.rmtree(self.output_path)
            sys.exit(1)
    
    def _create_directory_structure(self):
        """Create the basic directory structure."""
        directories = [
            ".",
            "app",
            "app/routes", 
            "app/controllers",
            "app/models",
            "config",
            "db",
            "db/migrations",
            "tests"
        ]
        
        for directory in directories:
            self.create_directory(directory)
    
    def _copy_template_files(self):
        """Copy and render all template files."""
        # Copy the entire app template directory
        self.copy_template_directory("app")
    
    def _setup_environment(self):
        """Set up Python virtual environment and install dependencies."""
        print("🔧 Setting up virtual environment...")
        
        try:
            # Create virtual environment
            self.run_command(f"{sys.executable} -m venv .venv")
            
            # Determine the correct pip path
            if os.name == 'nt':  # Windows
                pip_path = self.output_path / ".venv" / "Scripts" / "pip"
            else:  # Unix/Linux/macOS
                pip_path = self.output_path / ".venv" / "bin" / "pip"
            
            print("📦 Installing dependencies...")
            
            # Install dependencies
            install_result = subprocess.run(
                [str(pip_path), "install", "-r", "requirements.txt"],
                cwd=self.output_path,
                capture_output=True,
                text=True
            )
            
            if install_result.returncode != 0:
                print("⚠️  Warning: Some dependencies failed to install.")
                print("You can install them manually later with:")
                print(f"   cd {self.app_name}")
                print("   source .venv/bin/activate")
                print("   pip install -r requirements.txt")
            
        except subprocess.CalledProcessError:
            print("⚠️  Warning: Virtual environment setup failed.")
            print("You can set it up manually later with:")
            print(f"   cd {self.app_name}")
            print("   python -m venv .venv")
            print("   source .venv/bin/activate")
            print("   pip install -r requirements.txt")
    
    def _setup_database(self):
        """Set up database migrations with Alembic."""
        print("🗃️  Setting up database migrations...")
        
        try:
            # Determine the correct python path
            if os.name == 'nt':  # Windows
                python_path = self.output_path / ".venv" / "Scripts" / "python"
                alembic_path = self.output_path / ".venv" / "Scripts" / "alembic"
            else:  # Unix/Linux/macOS  
                python_path = self.output_path / ".venv" / "bin" / "python"
                alembic_path = self.output_path / ".venv" / "bin" / "alembic"
            
            # Initialize Alembic
            alembic_result = subprocess.run(
                [str(alembic_path), "init", "db/migrations"],
                cwd=self.output_path,
                capture_output=True,
                text=True
            )
            
            if alembic_result.returncode == 0:
                # Configure alembic.ini to not have a hardcoded database URL
                self._configure_alembic()
                # Configure env.py for Orbin
                self._configure_alembic_env()
                print("✅ Database migrations configured successfully")
            else:
                print("⚠️  Warning: Database setup failed:", alembic_result.stderr)
                print("You can set up Alembic manually later with:")
                print(f"   cd {self.app_name}")
                print("   source .venv/bin/activate")
                print("   alembic init db/migrations")
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️  Warning: Database setup failed: {e}")
            print("You can set up Alembic manually later with:")
            print(f"   cd {self.app_name}")
            print("   source .venv/bin/activate")
            print("   alembic init db/migrations")
    
    def _configure_alembic(self):
        """Configure alembic.ini file to work with Orbin."""
        alembic_ini_path = self.output_path / "alembic.ini"
        if alembic_ini_path.exists():
            content = alembic_ini_path.read_text()
            # Comment out the hardcoded sqlalchemy.url
            content = content.replace(
                "sqlalchemy.url = driver://user:pass@localhost/dbname",
                "# sqlalchemy.url = driver://user:pass@localhost/dbname"
            )
            alembic_ini_path.write_text(content)
    
    def _configure_alembic_env(self):
        """Configure the Alembic env.py file for Orbin."""
        env_py_path = self.output_path / "db" / "migrations" / "env.py"
        if env_py_path.exists():
            # Replace the env.py with our custom version
            env_py_content = '''import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv

from alembic import context

# Load environment variables
load_dotenv()

# Add the app directory to the path so we can import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the database base and models
from config.database import Base
from app.models import *  # Import all models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from environment variable
database_url = os.getenv('DATABASE_URL')
if database_url:
    config.set_main_option('sqlalchemy.url', database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
            env_py_path.write_text(env_py_content)
    
    def _print_success_message(self):
        """Print the success message with next steps."""
        print(f"✅ Successfully created Orbin application '{self.app_name}'!")
        print(f"📁 Location: {self.output_path}")
        print()
        print("🚀 To get started:")
        print(f"   cd {self.app_name}")
        print("   source .venv/bin/activate")
        print("   uvicorn app.main:app --reload")
        print()
        print("📖 Then visit:")
        print("   - App: http://localhost:8000")
        print("   - API docs: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
