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
            "tests",
            "tests/controllers",
            "tests/fixtures"
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
            # The alembic.ini template is already copied by _copy_template_files()
            # We just need to configure the env.py file
            self._configure_alembic_env()
            print("✅ Database migrations configured successfully")
            
        except Exception as e:
            print(f"⚠️  Warning: Database setup failed: {e}")
            print("You can set up Alembic manually later with:")
            print(f"   cd {self.app_name}")
            print("   source .venv/bin/activate")
            print("   alembic init db/migrations")
    
    def _configure_alembic_env(self):
        """Configure the Alembic env.py file for Orbin."""
        # The env.py template is already copied by _copy_template_files()
        # No additional configuration needed
        pass
    
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
