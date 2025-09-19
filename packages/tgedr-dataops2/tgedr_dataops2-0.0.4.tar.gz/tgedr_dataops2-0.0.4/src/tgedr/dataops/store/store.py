"""Store module providing abstract base classes and exceptions for data persistence operations."""

import abc
from typing import Any


class StoreException(Exception):  # pragma: no cover
    """Base exception for errors raised by store operations."""


class NoStoreException(StoreException):  # pragma: no cover
    """Exception raised when no store is available or configured."""


class StoreInterface(metaclass=abc.ABCMeta):  # noqa: B024, D101   # pragma: no cover
    @classmethod
    def __subclasshook__(cls, subclass):  # noqa: ANN001, ANN206, D105   # pragma: no cover
        return (
            hasattr(subclass, "get")
            and callable(subclass.get)
            and hasattr(subclass, "delete")
            and callable(subclass.delete)
            and hasattr(subclass, "save")
            and callable(subclass.save)
            and hasattr(subclass, "update")
            and callable(subclass.update)
        ) or NotImplemented


@StoreInterface.register
class Store(abc.ABC):  # pragma: no cover
    """abstract class used to manage persistence, defining CRUD-like (CreateReadUpdateDelete) methods."""

    def __init__(self, config: dict[str, Any] | None = None):  # pragma: no cover
        """Initialize the Store with an optional configuration dictionary.

        Parameters
        ----------
        config : dict[str, Any] or None, optional
            Configuration parameters for the store.

        """
        self._config = config

    @abc.abstractmethod
    def get(self, key: str, **kwargs) -> Any:  # pragma: no cover
        """Retrieve an object from the store by its key.

        Parameters
        ----------
        key : str
            The key identifying the object to retrieve.
        **kwargs
            Additional arguments for retrieval.

        Returns
        -------
        Any
            The object associated with the given key.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, key: str, **kwargs) -> None:  # pragma: no cover
        """Delete an object from the store by its key.

        Parameters
        ----------
        key : str
            The key identifying the object to delete.
        **kwargs
            Additional arguments for deletion.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, df: Any, key: str, **kwargs) -> None:  # pragma: no cover
        """Save an object to the store under the specified key.

        Parameters
        ----------
        df : Any
            The object to be saved.
        key : str
            The key under which to save the object.
        **kwargs
            Additional arguments for saving.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, df: Any, key: str, **kwargs) -> None:  # pragma: no cover
        """Update an existing object in the store under the specified key.

        Parameters
        ----------
        df : Any
            The object with updated data to be saved.
        key : str
            The key identifying the object to update.
        **kwargs
            Additional arguments for updating.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.

        """
        raise NotImplementedError
