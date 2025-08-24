"""
Base TestCase class for Orbin framework tests.

This provides common functionality for all test classes including:
- Database session management
- Test database setup and teardown
- Common fixtures and utilities
"""

import os
import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from typing import Generator, Dict, Any

from config.database import get_db, Base


class BaseTestCase:
    """Base test case class with common database and testing utilities."""
    
    @classmethod
    def setup_class(cls):
        """Set up class-level test configuration."""
        # Load environment variables
        load_dotenv()
        
        # Get test database URL
        cls.test_database_url = os.getenv("TEST_DATABASE_URL")
        if not cls.test_database_url:
            raise ValueError("TEST_DATABASE_URL not found in environment variables")
        
        # Create test database engine
        cls.engine = create_engine(cls.test_database_url)
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
    
    @pytest.fixture(scope="function")
    def db_session(self) -> Generator:
        """Create a fresh database session for each test."""
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        db = self.TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            # Clean up - drop all tables after test
            Base.metadata.drop_all(bind=self.engine)
    
    @pytest.fixture(scope="function") 
    def client(self, db_session) -> TestClient:
        """Create a test client with database dependency override."""
        from app.main import app
        
        def override_get_db():
            """Override database dependency for testing."""
            try:
                yield db_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        return TestClient(app)
    
    def load_fixtures(self, fixture_name: str) -> Dict[str, Any]:
        """Load YAML fixtures by name."""
        # Find the app root directory by looking for the current working directory
        # when running tests, we should be in the app root
        import os
        app_root = os.getcwd()
        fixtures_path = os.path.join(app_root, "tests", "fixtures", f"{fixture_name}.yml")
        
        with open(fixtures_path, 'r') as file:
            return yaml.safe_load(file)
