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
    
    def __init__(self, database_url: Optional[str] = None, test_mode: bool = False):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL database URL. If None, reads from environment.
            test_mode: If True, uses TEST_DATABASE_URL instead of DATABASE_URL.
        """
        if database_url is None:
            # Load from environment (look for .env file in current directory)
            from dotenv import load_dotenv
            load_dotenv(Path.cwd() / ".env")
            
            if test_mode:
                database_url = os.getenv("TEST_DATABASE_URL")
                if not database_url:
                    raise ValueError("TEST_DATABASE_URL not found in environment variables or .env file")
            else:
                database_url = os.getenv("DATABASE_URL")
                if not database_url:
                    raise ValueError("DATABASE_URL not found in environment variables or .env file")
        
        self.database_url = database_url
        self.parsed_url = urlparse(database_url)
        self.db_name = self.parsed_url.path[1:]  # Remove leading slash
        self.test_mode = test_mode
        
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
    
    def drop_database(self):
        """Drop the PostgreSQL database if it exists."""
        if not self.database_exists():
            print(f"✅ Database '{self.db_name}' doesn't exist")
            return True
        
        try:
            print(f"🗑️  Dropping database '{self.db_name}'...")
            
            # Connect without using context manager to avoid transactions
            conn = psycopg2.connect(self.admin_url)
            conn.autocommit = True
            cursor = conn.cursor()
            
            try:
                # Terminate active connections to the database
                cursor.execute(
                    sql.SQL("""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = %s AND pid <> pg_backend_pid()
                    """),
                    (self.db_name,)
                )
                
                # Drop database
                cursor.execute(
                    sql.SQL("DROP DATABASE {}").format(sql.Identifier(self.db_name))
                )
                print(f"✅ Successfully dropped database '{self.db_name}'")
                return True
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"❌ Error dropping database: {e}")
            return False
    
    def recreate_database(self):
        """Drop and recreate the database."""
        print(f"🔄 Recreating database '{self.db_name}'...")
        
        # Drop existing database
        if not self.drop_database():
            return False
        
        # Create new database
        return self.create_database()
    
    def copy_schema_from(self, source_db_manager):
        """Copy schema from another database (without data)."""
        try:
            print(f"📋 Copying schema from '{source_db_manager.db_name}' to '{self.db_name}'...")
            
            # Ensure both databases exist
            if not source_db_manager.database_exists():
                print(f"❌ Error: Source database '{source_db_manager.db_name}' doesn't exist")
                return False
            
            if not self.database_exists():
                if not self.create_database():
                    return False
            
            # Use pg_dump to get schema only
            dump_command = [
                "pg_dump",
                "--schema-only",  # Schema only, no data
                "--no-privileges",  # Don't dump privileges
                "--no-owner",      # Don't dump ownership
                source_db_manager.database_url
            ]
            
            # Run pg_dump to get schema
            dump_result = subprocess.run(
                dump_command,
                capture_output=True,
                text=True
            )
            
            if dump_result.returncode != 0:
                print(f"❌ Error dumping schema: {dump_result.stderr}")
                return False
            
            # Apply schema to target database
            restore_command = [
                "psql",
                self.database_url
            ]
            
            restore_result = subprocess.run(
                restore_command,
                input=dump_result.stdout,
                capture_output=True,
                text=True
            )
            
            if restore_result.returncode != 0:
                print(f"❌ Error restoring schema: {restore_result.stderr}")
                return False
            
            print(f"✅ Successfully copied schema to '{self.db_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error copying schema: {e}")
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
    """Create both development and test PostgreSQL databases for the current Orbin app."""
    try:
        # Create development database
        print("🗃️  Creating development database...")
        dev_db_manager = DatabaseManager(test_mode=False)
        dev_success = dev_db_manager.create_database()
        
        # Create test database
        print("🧪 Creating test database...")
        test_db_manager = DatabaseManager(test_mode=True)
        test_success = test_db_manager.create_database()
        
        if dev_success and test_success:
            print("✅ Successfully created both development and test databases")
            return True
        else:
            return False
            
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


def prepare_test_database():
    """Recreate test database as a schema copy of the development database."""
    try:
        print("🧪 Preparing test database...")
        
        # Get both database managers
        dev_db_manager = DatabaseManager(test_mode=False)
        test_db_manager = DatabaseManager(test_mode=True)
        
        # Ensure development database exists
        if not dev_db_manager.database_exists():
            print("❌ Error: Development database doesn't exist. Run 'orbin db-create' first.")
            return False
        
        # Recreate test database
        if not test_db_manager.recreate_database():
            return False
        
        # Copy schema from development to test database
        if not test_db_manager.copy_schema_from(dev_db_manager):
            return False
        
        print("✅ Test database prepared successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
