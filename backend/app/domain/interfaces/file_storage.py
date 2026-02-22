"""
File Storage interface — abstract contract for file persistence.

Concrete implementations: LocalStorage, S3Storage (Phase 13).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO


class IFileStorage(ABC):
    """Port for file upload / retrieval operations."""

    @abstractmethod
    def save(self, file_obj: BinaryIO, destination: str) -> str:
        """
        Persist a file and return the storage path / key.

        Args:
            file_obj: A file-like object with a `read()` method.
            destination: Desired destination path or key.

        Returns:
            The actual stored path or URL.
        """
        ...

    @abstractmethod
    def retrieve(self, path: str) -> BinaryIO:
        """
        Open a previously stored file for reading.

        Args:
            path: The path or key returned by ``save()``.

        Returns:
            A file-like object.
        """
        ...

    @abstractmethod
    def delete(self, path: str) -> bool:
        """
        Delete a stored file.

        Args:
            path: The path or key returned by ``save()``.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check whether a file exists at the given path."""
        ...
