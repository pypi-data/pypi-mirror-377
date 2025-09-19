"""Protocol definitions for SpecRec ObjectFactory."""

from typing import Any, List, Protocol, runtime_checkable
from typing_extensions import TypedDict


class ConstructorParameterInfo(TypedDict):
    """Information about a constructor parameter."""
    index: int
    name: str
    type_name: str
    value: Any


@runtime_checkable
class IConstructorCalledWith(Protocol):
    """Protocol for objects that want to track their constructor parameters."""

    def constructor_called_with(self, params: List[ConstructorParameterInfo]) -> None:
        """Called after object construction with parameter information.

        Args:
            params: List of constructor parameters used to create this object
        """
        ...


@runtime_checkable
class IObjectWithId(Protocol):
    """Protocol for objects that have an ID for logging/tracking purposes."""

    @property
    def object_id(self) -> str:
        """Unique identifier for this object instance."""
        ...


# Type aliases for better readability
ClassType = type
Constructor = type