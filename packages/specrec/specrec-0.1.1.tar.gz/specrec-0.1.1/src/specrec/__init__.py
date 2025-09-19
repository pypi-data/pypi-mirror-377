"""
SpecRec ObjectFactory - Dependency injection for testing legacy code.

This module provides a clean API for object creation with test double injection
capabilities, making legacy code testable with minimal changes.

Main exports:
    create: Curried function for object creation
    ObjectFactory: Main factory class for advanced usage
    get_instance: Get the global factory instance
"""

from .interfaces import (
    ConstructorParameterInfo,
    IConstructorCalledWith,
    IObjectWithId,
)
from .object_factory import ObjectFactory, get_instance, reset_instance

# Global function wrappers that always use current singleton instance
def create(cls):
    """Curried function for object creation using global instance."""
    return get_instance().create(cls)

def create_direct(cls, *args, **kwargs):
    """Direct creation using global instance."""
    return get_instance().create_direct(cls, *args, **kwargs)

def set_one(cls, instance):
    """Set single-use test double using global instance."""
    return get_instance().set_one(cls, instance)

def set_always(cls, instance):
    """Set persistent test double using global instance."""
    return get_instance().set_always(cls, instance)

def clear_one(cls):
    """Clear test doubles for specific type using global instance."""
    return get_instance().clear_one(cls)

def clear_all():
    """Clear all test doubles using global instance."""
    return get_instance().clear_all()

def register_object(obj, object_id=None):
    """Register object with ID using global instance."""
    return get_instance().register_object(obj, object_id)

def get_registered_object(object_id):
    """Get registered object using global instance."""
    return get_instance().get_registered_object(object_id)

def context():
    """Get context manager using global instance."""
    return get_instance().context()

# Export key types and protocols
__all__ = [
    # Main classes
    "ObjectFactory",
    "get_instance",
    "reset_instance",

    # Primary API functions
    "create",
    "create_direct",

    # Test double management
    "set_one",
    "set_always",
    "clear_one",
    "clear_all",
    "context",

    # Object registration
    "register_object",
    "get_registered_object",

    # Protocols and types
    "IConstructorCalledWith",
    "IObjectWithId",
    "ConstructorParameterInfo",
]