"""
Hello World Helper Module

This module provides a simple hello world function.
"""


def hello_world():
    """
    Prints "hello world" to the console.
    
    Returns:
        None
    """
    print("hello world")


def hello_world_with_name(name: str = "World"):
    """
    Prints a personalized hello message.
    
    Args:
        name (str): The name to greet. Defaults to "World".
        
    Returns:
        None
    """
    print(f"hello {name}")


def get_hello_world_message():
    """
    Returns the hello world message as a string instead of printing it.
    
    Returns:
        str: The hello world message
    """
    return "hello world"
