"""
Orbin - A powerful framework for AI-powered chat applications

A comprehensive framework built on FastAPI, SQLAlchemy, Alembic, and Redis
for creating AI-powered chat applications with convention over configuration.

Key Features:
- Powerful generators (scaffold, model, controller, resource)
- Automatic database migrations with Alembic
- Redis integration for caching, sessions, and real-time features
- RESTful routing conventions
- Comprehensive testing framework
- Interactive console and development tools
- Convention over configuration architecture

Usage:
    # Create a new application
    orbin create my_chat_app
    
    # Generate complete CRUD resources  
    orbin generate scaffold User name:string email:string
    
    # Start development server
    orbin server

For more information, visit: https://github.com/marceloribeiro/orbin
"""

from .helpers import hello_world, hello_world_with_name, get_hello_world_message

# Redis client is available but not auto-imported to avoid import errors
# Users can import it explicitly: from orbin.redis_client import get_redis_client

__version__ = "0.1.0"
__author__ = "Marcelo Ribeiro"
__email__ = "marcelo@floox.ai"
__description__ = "A powerful framework for building AI-powered chat applications with FastAPI"

__all__ = ['hello_world', 'hello_world_with_name', 'get_hello_world_message']
