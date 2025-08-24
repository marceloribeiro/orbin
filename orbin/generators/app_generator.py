"""
App Generator for Orbin framework.

Creates the initial application structure with FastAPI, SQLAlchemy, and Alembic.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
import shutil


class AppGenerator:
    """Generator for creating new Orbin applications."""
    
    def __init__(self, app_name: str, target_dir: Optional[str] = None):
        """
        Initialize the app generator.
        
        Args:
            app_name: Name of the application to create
            target_dir: Target directory (defaults to current directory)
        """
        self.app_name = app_name
        self.target_dir = Path(target_dir) if target_dir else Path.cwd()
        self.app_path = self.target_dir / app_name
        
        # Validate app name
        if not app_name.isidentifier():
            raise ValueError(f"App name '{app_name}' is not a valid Python identifier")
    
    def generate(self):
        """Generate the complete application structure."""
        print(f"Creating Orbin application '{self.app_name}'...")
        
        # Check if directory already exists
        if self.app_path.exists():
            print(f"Error: Directory '{self.app_path}' already exists!")
            sys.exit(1)
        
        try:
            # Create directory structure
            self._create_directory_structure()
            
            # Create configuration files
            self._create_config_files()
            
            # Create main application files
            self._create_app_files()
            
            # Create requirements and setup files
            self._create_requirements()
            
            # Initialize virtual environment and install dependencies
            self._setup_environment()
            
            # Initialize database and migrations
            self._setup_database()
            
            print(f"✅ Successfully created Orbin application '{self.app_name}'!")
            print(f"📁 Location: {self.app_path}")
            print(f"🚀 To get started:")
            print(f"   cd {self.app_name}")
            print(f"   source .venv/bin/activate")
            print(f"   uvicorn app.main:app --reload")
            
        except Exception as e:
            print(f"❌ Error creating application: {e}")
            # Clean up on error
            if self.app_path.exists():
                shutil.rmtree(self.app_path)
            sys.exit(1)
    
    def _create_directory_structure(self):
        """Create the directory structure."""
        directories = [
            self.app_path,
            self.app_path / "app",
            self.app_path / "app" / "routes",
            self.app_path / "app" / "controllers", 
            self.app_path / "app" / "models",
            self.app_path / "config",
            self.app_path / "db",
            self.app_path / "db" / "migrations",
            self.app_path / "tests",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory.relative_to(self.app_path)}")
    
    def _create_config_files(self):
        """Create configuration files."""
        
        # .env file
        env_content = f'''# Environment Configuration for {self.app_name}
APP_NAME={self.app_name}
APP_ENV=development
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/{self.app_name}_dev
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/{self.app_name}_test

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-change-this-in-production
'''
        self._write_file(".env", env_content)
        
        # config/database.py
        database_config = '''"""
Database configuration for the application.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        self._write_file("config/database.py", database_config)
        
        # config/settings.py
        settings_config = f'''"""
Application settings and configuration.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    APP_NAME: str = "{self.app_name}"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "")
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"


settings = Settings()
'''
        self._write_file("config/settings.py", settings_config)
        
        # config/__init__.py
        self._write_file("config/__init__.py", '"""Configuration package."""\n')
    
    def _create_app_files(self):
        """Create main application files."""
        
        # app/__init__.py
        self._write_file("app/__init__.py", '"""Main application package."""\n')
        
        # app/main.py
        main_content = f'''"""
Main FastAPI application for {self.app_name}.
"""

from datetime import datetime
from fastapi import FastAPI
from config.settings import settings
from app.routes import router

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered chat application built with Orbin",
    version="1.0.0",
    debug=settings.DEBUG
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {{
        "app_name": settings.APP_NAME,
        "timestamp": datetime.now().isoformat(),
        "status": "ok"
    }}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {{
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "app_name": settings.APP_NAME
    }}
'''
        self._write_file("app/main.py", main_content)
        
        # app/controllers/__init__.py
        self._write_file("app/controllers/__init__.py", '"""Controllers package."""\n')
        
        # app/controllers/base_controller.py
        base_controller = '''"""
Base controller class for all controllers.
"""

from typing import Any, Dict
from fastapi import HTTPException, status


class BaseController:
    """Base controller with common functionality."""
    
    def __init__(self):
        """Initialize the controller."""
        pass
    
    def render_json(self, data: Any, status_code: int = 200) -> Dict[str, Any]:
        """Render JSON response."""
        return {"data": data, "status": status_code}
    
    def render_error(self, message: str, status_code: int = 400) -> HTTPException:
        """Render error response."""
        raise HTTPException(status_code=status_code, detail=message)
    
    def not_found(self, message: str = "Resource not found") -> HTTPException:
        """Render 404 error."""
        return self.render_error(message, status.HTTP_404_NOT_FOUND)
    
    def unauthorized(self, message: str = "Unauthorized") -> HTTPException:
        """Render 401 error."""
        return self.render_error(message, status.HTTP_401_UNAUTHORIZED)
    
    def forbidden(self, message: str = "Forbidden") -> HTTPException:
        """Render 403 error."""
        return self.render_error(message, status.HTTP_403_FORBIDDEN)
'''
        self._write_file("app/controllers/base_controller.py", base_controller)
        
        # app/models/__init__.py
        self._write_file("app/models/__init__.py", '"""Models package."""\n')
        
        # app/routes/__init__.py
        routes_init = '''"""
Routes package - handles URL routing to controllers.
"""

from fastapi import APIRouter

router = APIRouter()

# Import route modules here
# from .example_routes import router as example_router
# router.include_router(example_router, prefix="/examples", tags=["examples"])
'''
        self._write_file("app/routes/__init__.py", routes_init)
        
        # tests/__init__.py
        self._write_file("tests/__init__.py", '"""Tests package."""\n')
        
        # Basic test file
        test_content = f'''"""
Basic tests for {self.app_name}.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "{self.app_name}"
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "{self.app_name}"
    assert "timestamp" in data
'''
        self._write_file("tests/test_main.py", test_content)
    
    def _create_requirements(self):
        """Create requirements and setup files."""
        
        # requirements.txt
        requirements = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary>=2.9.7
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.2
'''
        self._write_file("requirements.txt", requirements)
        
        # pyproject.toml
        pyproject = f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.app_name}"
version = "1.0.0"
description = "AI-powered chat application built with Orbin"
readme = "README.md"
license = "MIT"
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.23",
    "alembic>=1.12.1",
    "psycopg2-binary>=2.9.9",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "httpx>=0.25.2",
    "black>=23.0.0",
    "flake8>=6.0.0",
]

[tool.black]
line-length = 88
target-version = ['py38']
'''
        self._write_file("pyproject.toml", pyproject)
        
        # README.md
        readme = f'''# {self.app_name}

AI-powered chat application built with the Orbin framework.

## Getting Started

1. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Set up the database:**
   - Make sure PostgreSQL is running
   - Create the database: `createdb {self.app_name}_dev`
   - Run migrations: `alembic upgrade head`

3. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Visit your application:**
   - Main app: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Project Structure

```
{self.app_name}/
├── app/                    # Main application code
│   ├── controllers/        # Request handlers
│   ├── models/            # Database models
│   ├── routes/            # URL routing
│   └── main.py            # FastAPI app
├── config/                # Configuration files
├── db/                    # Database related files
│   └── migrations/        # Alembic migrations
├── tests/                 # Test files
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

## Development

- **Run tests:** `pytest`
- **Format code:** `black .`
- **Lint code:** `flake8`

## Database Migrations

- **Create migration:** `alembic revision --autogenerate -m "description"`
- **Apply migrations:** `alembic upgrade head`
- **Rollback:** `alembic downgrade -1`

Built with ❤️ using the Orbin framework.
'''
        self._write_file("README.md", readme)
        
        # .gitignore
        gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite

# Logs
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/

# Alembic
# Note: Keep alembic.ini and migration files
'''
        self._write_file(".gitignore", gitignore)
    
    def _setup_environment(self):
        """Set up Python virtual environment and install dependencies."""
        print("🔧 Setting up virtual environment...")
        
        try:
            # Create virtual environment
            venv_path = self.app_path / ".venv"
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True, cwd=self.app_path)
            
            # Get pip path
            if os.name == "nt":  # Windows
                pip_path = venv_path / "Scripts" / "pip"
                python_path = venv_path / "Scripts" / "python"
            else:  # Unix/Linux/macOS
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"
            
            # Install dependencies
            print("📦 Installing dependencies...")
            result = subprocess.run([
                str(pip_path), "install", "-r", "requirements.txt"
            ], capture_output=True, text=True, cwd=self.app_path)
            
            if result.returncode != 0:
                print("⚠️  Warning: Some dependencies failed to install.")
                print("You can install them manually later with:")
                print(f"   cd {self.app_name}")
                print("   source .venv/bin/activate")
                print("   pip install -r requirements.txt")
                # Don't fail the entire process
                self.python_path = python_path
                self.pip_path = pip_path
                return
            
            # Store paths for later use
            self.python_path = python_path
            self.pip_path = pip_path
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Virtual environment setup failed: {e}")
            print("You can set it up manually later with:")
            print(f"   cd {self.app_name}")
            print("   python -m venv .venv")
            print("   source .venv/bin/activate")
            print("   pip install -r requirements.txt")
            # Set dummy paths to avoid errors in database setup
            self.python_path = "python"
            self.pip_path = "pip"
    
    def _setup_database(self):
        """Set up Alembic for database migrations."""
        print("🗃️  Setting up database migrations...")
        
        try:
            # Initialize Alembic
            subprocess.run([
                str(self.python_path), "-m", "alembic", "init", "db/migrations"
            ], check=True, cwd=self.app_path)
            
            # Update alembic.ini
            alembic_ini_path = self.app_path / "alembic.ini"
            if alembic_ini_path.exists():
                # Read current content
                content = alembic_ini_path.read_text()
                
                # Replace sqlalchemy.url
                content = content.replace(
                    "sqlalchemy.url = driver://user:pass@localhost/dbname",
                    "sqlalchemy.url = postgresql://postgres:password@localhost:5432/" + f"{self.app_name}_dev"
                )
                
                alembic_ini_path.write_text(content)
            
            # Update env.py in migrations
            env_py_path = self.app_path / "db" / "migrations" / "env.py"
            if env_py_path.exists():
                env_content = '''import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

# Import your models here
# from app.models import Base
from config.database import Base

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with environment variable
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", ""))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
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
                env_py_path.write_text(env_content)
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️  Warning: Database setup failed: {e}")
            print("You can set up Alembic manually later with:")
            print(f"   cd {self.app_name}")
            print("   source .venv/bin/activate")
            print("   alembic init db/migrations")
            # Don't fail the entire process
    
    def _write_file(self, relative_path: str, content: str):
        """Write content to a file."""
        file_path = self.app_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        print(f"📄 Created file: {relative_path}")
