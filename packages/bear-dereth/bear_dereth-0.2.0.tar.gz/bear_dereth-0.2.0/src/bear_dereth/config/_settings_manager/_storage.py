import fcntl
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
import tomllib
from typing import IO, Any, Literal

import tomli_w

from bear_dereth.config._settings_manager._base_classes import Storage
from bear_dereth.files import touch

HandleMode = Literal["default", "temp"]
DataShape = dict[str, dict[str, Any]]


class JsonStorage(Storage):
    def __init__(self, filename: str | Path, file_mode: str = "r+", encoding: str = "utf-8") -> None:
        super().__init__()
        self.filename: Path = touch(filename, mkdir=True)
        self.temp_handle: IO[Any] = self.open(mode="temp", file_mode=file_mode, encoding=encoding)
        self.file_handle: IO[Any] = self.open(self.filename, file_mode, encoding)
        self.handle_map: dict[HandleMode, IO | None] = {"default": self.file_handle, "temp": self.temp_handle}

    def _handle(self, mode: HandleMode = "default") -> IO[Any] | None:
        if mode not in self.handle_map:
            raise ValueError(f"Invalid mode '{mode}'. Valid modes are: {list(self.handle_map.keys())}")
        return self.handle_map.get(mode, self.file_handle)

    def open(
        self,
        filename: Path = Path("/dev/null"),
        file_mode: str = "r+",
        encoding: str = "utf-8",
        mode: str = "default",
        **kwargs,
    ) -> IO[Any]:
        if mode == "temp":
            return NamedTemporaryFile(delete_on_close=True, mode=file_mode, encoding=encoding, **kwargs)
        return open(filename, file_mode, encoding=encoding, **kwargs)

    def read(self, mode: HandleMode = "default") -> DataShape | None:
        handle: IO[Any] | None = self._handle(mode)
        if handle is None:
            return None
        fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
        handle.seek(0)
        try:
            data: dict[str, dict[str, Any]] = json.load(handle)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return data

    def write(self, data: dict[str, Any], mode: HandleMode = "default") -> None:
        handle: IO[Any] | None = self._handle(mode)
        if handle is None:
            raise ValueError(f"No handle for mode '{mode}'")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.seek(0)
            handle.truncate(0)  # Clear file
            json.dump(data, handle, indent=4)
            handle.flush()  # Force write to disk
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def close(self) -> None:
        for mode, handle in self.handle_map.copy().items():
            if handle and not handle.closed:
                handle.close()
                self.handle_map[mode] = None

    def closed(self) -> bool:
        return all(handle is None or handle.closed for handle in self.handle_map.values())

    def __del__(self) -> None:
        self.close()


class TomlStorage(Storage):
    def __init__(self, filename: str | Path, file_mode: str = "r+", encoding: str = "utf-8") -> None:
        super().__init__()
        self.filename: Path = touch(filename, mkdir=True)
        self.file_mode: str = file_mode
        self.encoding: str = encoding
        self.file_handle: IO[Any] = self.open(self.filename, file_mode, encoding)

    def open(self, filename: Path, file_mode: str = "r+", encoding: str = "utf-8", **kwargs) -> IO[Any]:
        return open(filename, file_mode, encoding=encoding, **kwargs)

    def read(self) -> DataShape | None:
        with self.file_handle as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
            handle.seek(0)
            try:
                data: dict[str, dict[str, Any]] = tomllib.load(handle)
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return data

    def write(self, data: dict[str, Any]) -> None:
        with self.file_handle as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                handle.seek(0)
                handle.truncate()
                tomli_w.dump(data, handle)
                handle.flush()  # Force write to disk
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def close(self) -> None:
        if not self.file_handle.closed:
            self.file_handle.close()

    def closed(self) -> bool:
        return self.file_handle.closed


class InMemoryStorage(Storage):
    def __init__(self) -> None:
        super().__init__()
        self._data: DataShape | None = None

    def read(self) -> DataShape | None:
        return self._data

    def write(self, data: DataShape) -> None:
        self._data = data

    def close(self) -> None:
        if self._data is not None:
            self._data = None

    def closed(self) -> bool:
        return self._data is None
