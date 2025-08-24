"""
Orbin - Framework for AI-powered chat applications

A comprehensive framework built on FastAPI, SQLAlchemy, and WebSockets 
for creating AI-powered chat applications with convention over configuration.
"""

from .helpers import hello_world, hello_world_with_name, get_hello_world_message

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Framework for AI-powered chat applications built on FastAPI"

__all__ = ['hello_world', 'hello_world_with_name', 'get_hello_world_message']
