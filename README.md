# Orbin

A powerful framework for building AI-powered chat applications with FastAPI, SQLAlchemy, and convention over configuration.

🚀 **Convention over Configuration** • 🤖 **AI/Agent Ready** • ⚡ **FastAPI Powered** • �️ **Code Generators**

## Overview

Orbin brings productivity and elegance to Python for building AI-powered chat applications. With automatic code generation, database migrations, and RESTful conventions, you can focus on building intelligent agents while Orbin handles the infrastructure.

### Key Features

- 🎯 **Powerful Generators**: Scaffold models, controllers, and complete CRUD resources
- 🗃️ **Database Migrations**: Alembic-powered schema management with smart conventions  
- 🛣️ **RESTful Routing**: Automatic route generation with FastAPI
- 🧪 **Testing Framework**: Auto-generated tests with fixtures
- 🎮 **Interactive Console**: Developer console with app context
- 📦 **Convention over Configuration**: Opinionated structure that scales

## Installation

### From PyPI (Recommended)

```bash
pip install orbin
```

### From Source (Development)

```bash
git clone https://github.com/marceloribeiro/orbin.git
cd orbin
pip install -e .
```

## Quick Start

### 1. Create a New Application

```bash
orbin create my_chat_app
cd my_chat_app
```

This generates a complete FastAPI application structure:
```
my_chat_app/
├── app/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   └── main.py
├── config/
├── db/migrations/
├── tests/
└── requirements.txt
```

### 2. Set Up Database and Redis

**PostgreSQL Setup:**
```bash
# Create PostgreSQL databases (development & test)
orbin db-create

# Run migrations
orbin db-migrate

# Test database connection
orbin db        # Opens psql console
```

**Redis Setup:**
```bash
# Test Redis connection
orbin redis-ping

# Open Redis console
orbin redis     # Opens redis-cli console
```

### 3. Generate Resources

```bash
# Generate a complete CRUD resource (model + controller + tests)
orbin generate scaffold User name:string email:string role:string

# Generate just a model with migration
orbin generate model Message content:text user_id:integer

# Generate a RESTful controller for existing model
orbin generate resource Message

# Generate a custom controller with specific actions
orbin generate controller Chat index show create
```

### 4. Start Development Server

```bash
orbin server
```

Visit:
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **ReDoc**: http://localhost:8000/redoc

## Core Commands

### Application Management
```bash
orbin create <app_name>           # Create new Orbin application
orbin server                      # Start development server
orbin console                     # Interactive Python console with app context
orbin test                        # Run test suite with pytest
```

### Database Operations
```bash
orbin db-create                   # Create development and test databases
orbin db-migrate                  # Run pending migrations
orbin db                          # Open database console (psql)
orbin db-test-prepare            # Prepare test database
```

### Redis Operations
```bash
orbin redis-ping                  # Test Redis connection
orbin redis                       # Open Redis console (redis-cli)
```

### Code Generators
```bash
orbin generate scaffold <Model> <attrs>     # Complete CRUD (model + controller + tests)
orbin generate model <Model> <attrs>        # SQLAlchemy model + migration
orbin generate controller <Name> <actions>  # FastAPI controller with actions
orbin generate resource <Model>             # RESTful controller for existing model
```

## Example: Building a Chat System

```bash
# Create the application
orbin create ai_chat
cd ai_chat

# Set up database and Redis
orbin db-create && orbin db-migrate
orbin redis-ping  # Verify Redis connection

# Generate core models
orbin generate scaffold User name:string email:string
orbin generate scaffold Conversation title:string user_id:integer
orbin generate scaffold Message content:text conversation_id:integer role:string

# Run migrations
orbin db-migrate

# Start server
orbin server
```

**Chat Features Available:**
```python
# In your controllers - Redis-powered features
from config.redis import store_conversation, get_conversation, cache_set

# Cache recent conversations
cache_set(f"recent_conversations:{user_id}", conversations, ttl=300)

# Store real-time conversation context
store_conversation(conversation_id, messages, ttl=86400)

# Pub/sub for real-time updates
redis_client.publish(f"conversation:{conversation_id}", new_message)
```

You now have a complete chat API with:
- **Users management**: `GET/POST/PUT/DELETE /users`
- **Conversations**: `GET/POST/PUT/DELETE /conversations`  
- **Messages**: `GET/POST/PUT/DELETE /messages`
- **Automatic tests** and **database fixtures**

## Smart Conventions

### Directory Structure
```
app/
├── controllers/          # FastAPI route handlers
├── models/              # SQLAlchemy models  
└── routes/              # Route definitions
config/
├── database.py          # Database configuration
└── settings.py          # Application settings
db/migrations/           # Alembic migration files
tests/
├── controllers/         # Controller tests
└── fixtures/           # Test data (YAML)
```

### RESTful Routes
Orbin automatically generates RESTful endpoints:

| HTTP Verb | Path | Action | Description |
|-----------|------|--------|-------------|
| GET | `/users` | index | List all users |
| GET | `/users/{id}` | show | Get specific user |
| POST | `/users` | create | Create new user |
| PUT | `/users/{id}` | update | Update user |
| DELETE | `/users/{id}` | destroy | Delete user |

### Model Conventions
```python
# Generated User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Generated Tests
Orbin automatically creates comprehensive tests:

```python
# Generated test for User controller
def test_create_user(self):
    user_data = {"name": "John Doe", "email": "john@example.com"}
    response = self.client.post("/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["name"] == "John Doe"
```

## AI/Agent Integration

Orbin is designed for AI applications with built-in patterns for:

- **Message-based Communication**: Models for conversations, messages, and user interactions
- **Agent Workflows**: Controllers that can handle AI agent responses  
- **WebSocket Support**: Real-time chat capabilities with FastAPI WebSockets
- **Redis Integration**: Fast caching, session management, and real-time pub/sub messaging
- **Conversation Storage**: Efficient Redis-based chat history and context management
- **Database Optimizations**: Efficient queries for chat history and conversation management

### Redis AI Features
```python
# Store conversation context in Redis
from config.redis import store_conversation, get_conversation

# Cache AI responses
redis_client.cache_set(f"ai_response:{prompt_hash}", response, ttl=3600)

# Real-time notifications
redis_client.publish("chat_updates", json.dumps({"user_id": 123, "message": "New message"}))

# Session management for stateful agents
redis_client.store_user_session("user_123", {"context": "...", "state": "waiting"})
```

## Advanced Usage

### Custom Generators

Extend Orbin with custom generators:

```python
from orbin.generators.base_generator import BaseGenerator

class MyCustomGenerator(BaseGenerator):
    def generate(self):
        # Your custom generation logic
        pass
```

### Database Console

```bash
# Open PostgreSQL console
orbin db

# Common psql commands:
\dt                    # List tables
\d users              # Describe users table  
SELECT * FROM users;  # Query users
```

### Interactive Console

```bash
orbin console
# Auto-imports app, settings, database, and models
>>> from app.models.user import User
>>> users = session.query(User).all()
>>> print(f"Total users: {len(users)}")
```

## Configuration

Before starting your Orbin application, you need to set up PostgreSQL and Redis servers.

### Prerequisites Setup

#### PostgreSQL Installation
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Windows
# Download and install from https://www.postgresql.org/download/windows/
```

#### Redis Installation
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows
# Download and install from https://redis.io/download
```

### Environment Variables (.env)
```bash
# Application
APP_NAME=MyApp
APP_ENV=development
DEBUG=true

# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/myapp_development
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/myapp_test

# Redis Cache/Session Store
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-change-this-in-production
```

### Database Configuration (config/database.py)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Redis Configuration (config/redis.py)
```python
from orbin.redis_client import get_redis_client
from config.settings import settings

# Get Redis client
redis_client = get_redis_client(settings.REDIS_URL)

# Usage examples
redis_client.cache_set("key", "value", ttl=3600)
redis_client.store_conversation("conv_123", messages)
redis_client.store_user_session("user_456", session_data)
```

### Quick Setup Verification
```bash
# Test PostgreSQL connection
orbin db

# Test Redis connection  
orbin redis-ping

# Test full application
orbin server
```

## Requirements

- **Python 3.8+**
- **PostgreSQL 10+** (primary database)
- **Redis 6.0+** (caching, sessions, real-time features)
- **FastAPI 0.104+**
- **SQLAlchemy 2.0+**

## Architecture

Orbin follows proven conventions adapted for Python:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Controllers   │───▶│     Models      │───▶│    Database     │
│   (FastAPI)     │    │  (SQLAlchemy)   │    │ (PostgreSQL)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Routes      │    │   Migrations    │    │      Tests      │
│   (Auto-gen)    │    │   (Alembic)     │    │   (Pytest)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Development

### Running Tests

```bash
# Run all tests
orbin test

# Run specific test file
orbin test tests/controllers/test_users_controller.py

# Run with verbose output
orbin test -v

# Skip database preparation (faster for repeated runs)
orbin test --skip-prepare
```

### Development Workflow

1. **Generate scaffold**: `orbin g scaffold Post title:string content:text`
2. **Run migration**: `orbin db-migrate`  
3. **Run tests**: `orbin test`
4. **Start server**: `orbin server`
5. **Iterate**: Modify controllers, add business logic, enhance tests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`orbin test`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### 0.1.0 (2025-08-24)
- Initial release
- Powerful generators (scaffold, model, controller, resource)
- FastAPI integration with automatic routing
- PostgreSQL database support with Alembic migrations
- Comprehensive testing framework with auto-generated tests
- Interactive console and development server
- Convention over configuration architecture
