from typing import Optional


def generate_greeting(name: Optional[str] = None) -> str:
    """Business logic for generating greetings"""
    if name:
        return f"Hello {name}!"
    return "Hello World!"
