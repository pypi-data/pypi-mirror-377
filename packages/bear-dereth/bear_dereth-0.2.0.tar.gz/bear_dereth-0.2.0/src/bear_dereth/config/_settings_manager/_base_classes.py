from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping  # noqa: TC003
from typing import TYPE_CHECKING, Any, NoReturn, Protocol, Self, runtime_checkable

from bear_dereth.config._settings_manager._common import OpType, ValueType  # noqa: TC001
from bear_dereth.freezing import BaseHashValue, BaseNotCacheable

if TYPE_CHECKING:
    from types import NoneType


class Document(dict):
    """A document stored in the database.

    This class provides a way to access both a document's content and
    its ID using ``doc.id``.
    """

    def __init__(self, value: Mapping[str, ValueType], doc_id: int) -> NoneType:
        """Initialize the Document with its content and ID.

        Args:
            value: The content of the document as a dictionary.
            doc_id: The unique identifier for the document.
        """
        super().__init__(value)
        self.id: int = doc_id


class HashValue(BaseHashValue):
    """A simple frozen model to hold a hash value for query caching."""

    op: OpType | None

    def combine(self, other: BaseHashValue, **kwargs) -> HashValue:
        """Combine multiple hash values into one."""
        return HashValue(value=[self, other], **kwargs)

    def __hash__(self) -> int:
        if not self.cacheable:
            raise TypeError("This HashValue is not cacheable")
        return super().__hash__()


class NotCacheable(HashValue, BaseNotCacheable):
    """A singleton representing a non-cacheable hash value, contains a frozen cacheable=False flag."""

    def __init__(self) -> None: ...

    def __hash__(self) -> int:
        raise TypeError("This HashValue is not cacheable")

    def combine(self, other: BaseHashValue, **kwargs) -> NoReturn:  # noqa: ARG002
        raise TypeError("This object is not cacheable")


@runtime_checkable
class Table(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Self: ...
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...
    def search(self, query: Any) -> list[Document]: ...
    def all(self) -> list[Document]: ...
    def upsert(self, record: dict[str, Any], query: Any) -> None: ...
    def contains(self, query: Any) -> bool: ...
    def close(self) -> None: ...


class Storage(ABC):
    """The abstract base class for all Storages.

    A Storage (de)serializes the current state of the database and stores it in
    some place (memory, file on disk, ...).
    """

    @abstractmethod
    def read(self) -> dict[str, dict[str, Any]] | None:
        """Read the current state.

        Any kind of deserialization should go here.

        Return ``None`` here to indicate that the storage is empty.
        """
        raise NotImplementedError("To be overridden!")

    @abstractmethod
    def write(self, data: dict[str, dict[str, Any]]) -> None:
        """Write the current state of the database to the storage.

        Any kind of serialization should go here.

        Args:
            data: The current state of the database.
        """
        raise NotImplementedError("To be overridden!")

    @abstractmethod
    def close(self) -> None:
        """Optional: Close open file handles, etc."""

    @abstractmethod
    def closed(self) -> bool:
        """Check if the storage is closed."""
        raise NotImplementedError("To be overridden!")
