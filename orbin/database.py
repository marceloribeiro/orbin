"""
Database utilities for Orbin framework.

Handles database creation, migration, and other database operations.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse


class DatabaseManager:
    """Manages database operations for Orbin applications."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL database URL. If None, reads from environment.
        """
        if database_url is None:
            # Load from environment (look for .env file in current directory)
            from dotenv import load_dotenv
            load_dotenv(Path.cwd() / ".env")
            database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables or .env file")
        
        self.database_url = database_url
        self.parsed_url = urlparse(database_url)
        self.db_name = self.parsed_url.path[1:]  # Remove leading slash
        
        # Create connection URL without database name for admin operations
        self.admin_url = database_url.replace(f"/{self.db_name}", "/postgres")
    
    def database_exists(self) -> bool:
        """Check if the database exists."""
        try:
            conn = psycopg2.connect(self.admin_url)
            conn.autocommit = True
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (self.db_name,)
                )
                return cursor.fetchone() is not None
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error checking database existence: {e}")
            return False
    
    def create_database(self):
        """Create the PostgreSQL database if it doesn't exist."""
        if self.database_exists():
            print(f"✅ Database '{self.db_name}' already exists")
            return True
        
        try:
            print(f"🗃️  Creating database '{self.db_name}'...")
            
            # Connect without using context manager to avoid transactions
            conn = psycopg2.connect(self.admin_url)
            conn.autocommit = True
            cursor = conn.cursor()
            
            try:
                # Create database
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name))
                )
                print(f"✅ Successfully created database '{self.db_name}'")
                return True
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def run_migrations(self):
        """Run Alembic migrations."""
        try:
            print("🔄 Running database migrations...")
            
            # Check if we're in an Orbin app directory
            if not Path.cwd().joinpath("app", "main.py").exists():
                print("❌ Error: Not in an Orbin application directory")
                return False
            
            # Check if alembic.ini exists
            alembic_ini = Path.cwd() / "alembic.ini"
            if not alembic_ini.exists():
                print("❌ Error: alembic.ini not found. Run 'alembic init db/migrations' first.")
                return False
            
            # Run alembic upgrade
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=Path.cwd(),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Migrations completed successfully")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print("❌ Migration failed:")
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print("❌ Error: Alembic not found. Please install with 'pip install alembic'")
            return False
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            return False


def create_database():
    """Create the PostgreSQL database for the current Orbin app."""
    try:
        db_manager = DatabaseManager()
        return db_manager.create_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def migrate_database():
    """Run database migrations for the current Orbin app."""
    try:
        db_manager = DatabaseManager()
        
        # First ensure database exists
        if not db_manager.database_exists():
            print("🗃️  Database doesn't exist, creating it first...")
            if not db_manager.create_database():
                return False
        
        # Run migrations
        return db_manager.run_migrations()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
