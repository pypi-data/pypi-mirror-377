"""Define abstract base classes and interfaces for data sink operations.

Includes SinkInterface, Sink, and SinkException to manage data persistence.
"""

import abc
from typing import Any


class SinkException(Exception):  # pragma: no cover
    """Exception raised for errors encountered in sink operations."""


class SinkInterface(metaclass=abc.ABCMeta):  # noqa: B024  # pragma: no cover
    """Defines the interface for sink operations.

    def put(self, context: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError()
    """

    @classmethod
    def __subclasshook__(cls, subclass):  # noqa: ANN001, ANN206, D105   # pragma: no cover
        return (
            hasattr(subclass, "put")
            and callable(subclass.put)
            and hasattr(subclass, "delete")
            and callable(subclass.delete)
        ) or NotImplemented


@SinkInterface.register
class Sink(abc.ABC):  # pragma: no cover
    """Abstract class defining methods ('put' and 'delete') to manage persistence of data.

    Somewhere as defined by implementing classes.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:  # pragma: no cover
        """Initialize the Sink with an optional configuration dictionary.

        Args:
            config (dict[str, Any] | None): Optional configuration for the sink.

        """
        self._config = config

    @abc.abstractmethod
    def put(self, context: dict[str, Any] | None = None) -> Any:  # pragma: no cover
        """Persist data as defined by the implementing class.

        Args:
            context (dict[str, Any] | None): Optional context or data to be persisted.

        Returns:
            Any: The result of the put operation.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, context: dict[str, Any] | None = None) -> Any:  # pragma: no cover
        """Delete persisted data as defined by the implementing class.

        Args:
            context (dict[str, Any] | None): Optional context or data to be deleted.

        Returns:
            Any: The result of the delete operation.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        """
        raise NotImplementedError
