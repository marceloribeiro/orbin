"""
Redis client configuration and utilities for Orbin framework.

Provides Redis connection management and common operations for AI chat applications.
"""

import os
import redis
from typing import Optional, Any, Dict, Union
from urllib.parse import urlparse
import json
import pickle
from datetime import timedelta


class RedisClient:
    """Redis client wrapper with convenience methods for chat applications."""
    
    def __init__(self, redis_url: Optional[str] = None, **kwargs):
        """
        Initialize Redis client.
        
        Args:
            redis_url: Redis connection URL. If None, reads from environment.
            **kwargs: Additional redis.Redis() parameters
        """
        if redis_url is None:
            # Load from environment (look for .env file in current directory)
            from dotenv import load_dotenv
            load_dotenv()
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        self.redis_url = redis_url
        self.client = self._create_client(**kwargs)
    
    def _create_client(self, **kwargs) -> redis.Redis:
        """Create Redis client from URL."""
        try:
            # Parse Redis URL and create client
            parsed_url = urlparse(self.redis_url)
            
            # Extract connection parameters
            host = parsed_url.hostname or 'localhost'
            port = parsed_url.port or 6379
            db = int(parsed_url.path.lstrip('/')) if parsed_url.path else 0
            username = parsed_url.username
            password = parsed_url.password
            
            # SSL support for Redis Cloud, etc.
            ssl_cert_reqs = None
            if parsed_url.scheme == 'rediss':
                kwargs['ssl'] = True
                # For Redis Cloud and similar services
                if 'ssl_cert_reqs' not in kwargs:
                    import ssl
                    kwargs['ssl_cert_reqs'] = ssl.CERT_NONE
            
            client = redis.Redis(
                host=host,
                port=port,
                db=db,
                username=username,
                password=password,
                decode_responses=True,  # Automatically decode responses to strings
                **kwargs
            )
            
            # Test connection
            client.ping()
            return client
            
        except Exception as e:
            print(f"❌ Error connecting to Redis: {e}")
            print(f"Redis URL: {self.redis_url}")
            raise
    
    def ping(self) -> bool:
        """Test Redis connection."""
        try:
            return self.client.ping()
        except Exception:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        return self.client.info()
    
    # Basic key-value operations
    def set(self, key: str, value: Any, ex: Optional[Union[int, timedelta]] = None) -> bool:
        """Set a key-value pair with optional expiration."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.set(key, value, ex=ex)
    
    def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        return self.client.get(key)
    
    def get_json(self, key: str) -> Optional[Dict]:
        """Get a JSON value by key."""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        return self.client.delete(*keys)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return bool(self.client.exists(key))
    
    def expire(self, key: str, time: Union[int, timedelta]) -> bool:
        """Set expiration for a key."""
        return self.client.expire(key, time)
    
    # Chat-specific methods
    def store_conversation(self, conversation_id: str, messages: list, ttl: Optional[int] = None) -> bool:
        """Store conversation messages in Redis."""
        key = f"conversation:{conversation_id}"
        value = json.dumps(messages)
        return self.client.set(key, value, ex=ttl)
    
    def get_conversation(self, conversation_id: str) -> Optional[list]:
        """Retrieve conversation messages from Redis."""
        key = f"conversation:{conversation_id}"
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    def add_message_to_conversation(self, conversation_id: str, message: dict) -> bool:
        """Add a message to an existing conversation."""
        messages = self.get_conversation(conversation_id) or []
        messages.append(message)
        return self.store_conversation(conversation_id, messages)
    
    def store_user_session(self, user_id: str, session_data: dict, ttl: int = 3600) -> bool:
        """Store user session data."""
        key = f"session:{user_id}"
        return self.set(key, session_data, ex=ttl)
    
    def get_user_session(self, user_id: str) -> Optional[dict]:
        """Get user session data."""
        key = f"session:{user_id}"
        return self.get_json(key)
    
    def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session."""
        key = f"session:{user_id}"
        return bool(self.delete(key))
    
    # Caching methods
    def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Cache a value with TTL."""
        cache_key = f"cache:{key}"
        return self.set(cache_key, value, ex=ttl)
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        cache_key = f"cache:{key}"
        return self.get(cache_key)
    
    def cache_get_json(self, key: str) -> Optional[Dict]:
        """Get cached JSON value."""
        cache_key = f"cache:{key}"
        return self.get_json(cache_key)
    
    def cache_delete(self, key: str) -> bool:
        """Delete cached value."""
        cache_key = f"cache:{key}"
        return bool(self.delete(cache_key))
    
    # List operations (useful for message queues)
    def list_push(self, key: str, *values: str) -> int:
        """Push values to the end of a list."""
        return self.client.rpush(key, *values)
    
    def list_pop(self, key: str, timeout: int = 0) -> Optional[tuple]:
        """Pop value from the beginning of a list (blocking)."""
        result = self.client.blpop(key, timeout=timeout)
        return result
    
    def list_length(self, key: str) -> int:
        """Get list length."""
        return self.client.llen(key)
    
    def list_range(self, key: str, start: int = 0, end: int = -1) -> list:
        """Get list range."""
        return self.client.lrange(key, start, end)
    
    # Pub/Sub methods (for real-time features)
    def publish(self, channel: str, message: str) -> int:
        """Publish message to channel."""
        return self.client.publish(channel, message)
    
    def subscribe(self, *channels: str):
        """Subscribe to channels."""
        pubsub = self.client.pubsub()
        pubsub.subscribe(*channels)
        return pubsub
    
    # Hash operations (useful for user profiles, etc.)
    def hash_set(self, name: str, mapping: dict) -> int:
        """Set hash fields."""
        return self.client.hset(name, mapping=mapping)
    
    def hash_get(self, name: str, key: str) -> Optional[str]:
        """Get hash field value."""
        return self.client.hget(name, key)
    
    def hash_get_all(self, name: str) -> dict:
        """Get all hash fields."""
        return self.client.hgetall(name)
    
    def hash_delete(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        return self.client.hdel(name, *keys)
    
    def close(self):
        """Close Redis connection."""
        if hasattr(self.client, 'close'):
            self.client.close()


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client(redis_url: Optional[str] = None) -> RedisClient:
    """
    Get or create Redis client instance.
    
    Args:
        redis_url: Redis connection URL. If None, uses environment variable.
        
    Returns:
        RedisClient instance
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = RedisClient(redis_url)
    
    return _redis_client


def configure_redis(redis_url: str):
    """
    Configure Redis client with a specific URL.
    
    Args:
        redis_url: Redis connection URL
    """
    global _redis_client
    _redis_client = RedisClient(redis_url)


# Convenience functions
def redis_ping() -> bool:
    """Test Redis connection."""
    try:
        client = get_redis_client()
        return client.ping()
    except Exception:
        return False


def redis_info() -> dict:
    """Get Redis server information."""
    client = get_redis_client()
    return client.get_info()
