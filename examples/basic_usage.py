#!/usr/bin/env python3
"""
Example usage of the orbin package.

This script demonstrates how to use the hello world helper functions.
"""

# Import the functions from orbin
from orbin import hello_world, hello_world_with_name, get_hello_world_message


def main():
    """Main function demonstrating orbin usage."""
    print("=== Orbin Package Example ===\n")
    
    # Basic hello world
    print("1. Basic hello world:")
    hello_world()
    
    print("\n2. Hello world with default name:")
    hello_world_with_name()
    
    print("\n3. Hello world with custom name:")
    hello_world_with_name("Alice")
    hello_world_with_name("Bob")
    
    print("\n4. Getting message as string:")
    message = get_hello_world_message()
    print(f"Retrieved message: '{message}'")
    
    print("\n5. Alternative import style:")
    from orbin.helpers import hello_world_helper
    print("Using direct module import:")
    hello_world_helper.hello_world()
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
