"""Core ObjectFactory implementation for dependency injection and testing."""

import inspect
import threading
from collections import defaultdict, deque
from contextlib import contextmanager
from typing import Any, Callable, Deque, Dict, List, Optional, Type, TypeVar, Union
from uuid import uuid4

from .interfaces import (
    ClassType,
    Constructor,
    ConstructorParameterInfo,
    IConstructorCalledWith,
    IObjectWithId,
)

T = TypeVar("T")


class ObjectFactory:
    """
    Dependency injection factory for creating objects with test double support.

    Provides a clean API for object creation while allowing test doubles to be
    injected for testing purposes. Supports all microfeatures from the SpecRec
    ObjectFactory design.
    """

    def __init__(self) -> None:
        """Initialize a new ObjectFactory instance."""
        self._lock = threading.RLock()

        # Test double queues - single use (FIFO)
        self._set_one_queue: Dict[ClassType, Deque[Any]] = defaultdict(deque)

        # Persistent test doubles - always return these
        self._set_always: Dict[ClassType, Any] = {}

        # Object registration for clean logging
        self._registered_objects: Dict[str, Any] = {}

        # Global singleton instance
        self._instance: Optional["ObjectFactory"] = None

    def create(self, cls: Type[T]) -> Callable[..., T]:
        """
        Create a curried function for object creation.

        This returns a function that, when called with constructor arguments,
        will create an instance of the specified class.

        Args:
            cls: The class to create instances of

        Returns:
            A function that takes constructor arguments and returns an instance

        Raises:
            TypeError: If cls is None or not a type

        Example:
            create_service = factory.create(EmailService)
            service = create_service("smtp.server", 587)
        """
        if cls is None:
            raise TypeError("Cannot create factory for None type")
        if not isinstance(cls, type):
            raise TypeError(f"Expected a type, got {type(cls).__name__}")

        def creator(*args: Any, **kwargs: Any) -> T:
            return self._create_instance(cls, *args, **kwargs)

        return creator

    def create_direct(self, cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """
        Create an instance directly with constructor arguments.

        Args:
            cls: The class to create an instance of
            *args: Positional arguments for the constructor
            **kwargs: Keyword arguments for the constructor

        Returns:
            New instance of the specified class

        Raises:
            TypeError: If cls is None or not a type
        """
        if cls is None:
            raise TypeError("Cannot create instance of None type")
        if not isinstance(cls, type):
            raise TypeError(f"Expected a type, got {type(cls).__name__}")

        return self._create_instance(cls, *args, **kwargs)

    def _create_instance(self, cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """Internal method to create instances with test double support."""
        with self._lock:
            # Check for persistent test double first (takes precedence)
            if cls in self._set_always:
                return self._set_always[cls]

            # Check for single-use test double
            if cls in self._set_one_queue and self._set_one_queue[cls]:
                return self._set_one_queue[cls].popleft()

            # Create new instance normally
            instance = cls(*args, **kwargs)

            # Track constructor parameters if object supports it
            self._track_constructor_parameters(instance, *args, **kwargs)

            return instance

    def _track_constructor_parameters(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        """Track constructor parameters for objects that implement IConstructorCalledWith."""
        if not isinstance(instance, IConstructorCalledWith):
            return

        try:
            # Get constructor signature
            sig = inspect.signature(instance.__class__.__init__)
            params_info: List[ConstructorParameterInfo] = []

            # Skip 'self' parameter
            param_names = list(sig.parameters.keys())[1:]

            # Process positional arguments
            for i, (param_name, arg_value) in enumerate(zip(param_names, args)):
                param_info = ConstructorParameterInfo(
                    index=i,
                    name=param_name,
                    type_name=type(arg_value).__name__,
                    value=arg_value
                )
                params_info.append(param_info)

            # Process keyword arguments
            for i, (param_name, arg_value) in enumerate(kwargs.items(), len(args)):
                param_info = ConstructorParameterInfo(
                    index=i,
                    name=param_name,
                    type_name=type(arg_value).__name__,
                    value=arg_value
                )
                params_info.append(param_info)

            instance.constructor_called_with(params_info)

        except (ValueError, TypeError):
            # If introspection fails, call with empty list
            instance.constructor_called_with([])

    def set_one(self, cls: ClassType, instance: Any) -> None:
        """
        Queue a test double to be returned the next time this type is requested.

        The test double is consumed after one use and subsequent requests will
        create new instances normally (or return other queued doubles).

        Args:
            cls: The class type to inject for
            instance: The test double instance to return
        """
        with self._lock:
            self._set_one_queue[cls].append(instance)

    def set_always(self, cls: ClassType, instance: Any) -> None:
        """
        Set a test double to always be returned for this type.

        Unlike set_one, this persists until explicitly cleared and will
        be returned for every request of this type.

        Args:
            cls: The class type to inject for
            instance: The test double instance to always return
        """
        with self._lock:
            self._set_always[cls] = instance

    def clear_one(self, cls: ClassType) -> None:
        """
        Clear all test doubles for a specific type.

        Args:
            cls: The class type to clear test doubles for
        """
        with self._lock:
            if cls in self._set_one_queue:
                self._set_one_queue[cls].clear()
            self._set_always.pop(cls, None)

    def clear_all(self) -> None:
        """Clear all test doubles for all types."""
        with self._lock:
            self._set_one_queue.clear()
            self._set_always.clear()
            self._registered_objects.clear()

    def register_object(self, obj: Any, object_id: Optional[str] = None) -> str:
        """
        Register an object with an ID for clean logging and tracking.

        Args:
            obj: The object to register
            object_id: Optional custom ID, generates UUID if not provided

        Returns:
            The ID assigned to the object
        """
        with self._lock:
            if object_id is None:
                object_id = str(uuid4())

            self._registered_objects[object_id] = obj

            # Set the object_id attribute if the object supports it
            if hasattr(obj, 'object_id') or isinstance(obj, IObjectWithId):
                if hasattr(obj, '_object_id'):
                    obj._object_id = object_id
                elif hasattr(obj, 'object_id') and isinstance(obj.object_id, property):
                    # If it's a property, we can't set it directly
                    pass
                else:
                    obj.object_id = object_id  # type: ignore

            return object_id

    def get_registered_object(self, object_id: str) -> Optional[Any]:
        """
        Get a registered object by its ID.

        Args:
            object_id: The ID of the object to retrieve

        Returns:
            The registered object, or None if not found
        """
        with self._lock:
            return self._registered_objects.get(object_id)

    @contextmanager
    def context(self):
        """
        Context manager for isolated test double management.

        Creates a temporary context where test doubles can be set and will
        be automatically cleared when the context exits.

        Example:
            with factory.context():
                factory.set_one(EmailService, mock_service)
                service = factory.create(EmailService)()  # Returns mock
            # Test doubles automatically cleared here
        """
        # Save current state
        saved_one_queue = {cls: deque(queue) for cls, queue in self._set_one_queue.items()}
        saved_always = dict(self._set_always)
        saved_registered = dict(self._registered_objects)

        try:
            yield self
        finally:
            # Restore previous state
            with self._lock:
                self._set_one_queue.clear()
                self._set_one_queue.update(saved_one_queue)
                self._set_always.clear()
                self._set_always.update(saved_always)
                self._registered_objects.clear()
                self._registered_objects.update(saved_registered)


# Global singleton instance with thread-safe initialization
_factory_lock = threading.RLock()
_global_factory: Optional[ObjectFactory] = None


def get_instance() -> ObjectFactory:
    """Get the global singleton ObjectFactory instance."""
    global _global_factory
    if _global_factory is None:
        with _factory_lock:
            if _global_factory is None:
                _global_factory = ObjectFactory()
    return _global_factory


def reset_instance() -> None:
    """Reset the global singleton (primarily for testing)."""
    global _global_factory
    with _factory_lock:
        _global_factory = None