from datetime import datetime
from pathlib import Path
from typing import IO, Literal, Protocol, override
from zipfile import ZipInfo

from epublib.exceptions import EPUBError


def zip_info_now():
    now = datetime.now()

    if now.year > 2107:
        now = now.replace(year=2107, month=12, day=31)

    return (
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second,
    )


class SourceProtocol(Protocol):
    """Protocol for a source of EPUB data."""

    def getinfo(self, name: str) -> ZipInfo: ...
    def open(
        self,
        name: str | ZipInfo,
        mode: Literal["r", "w"] = "r",
        pwd: bytes | None = None,
        *,
        force_zip64: bool = False,
    ) -> IO[bytes]: ...
    def infolist(self) -> list[ZipInfo]: ...


class SinkProtocol(Protocol):
    """Protocol for a sink of EPUB data."""

    def writestr(
        self,
        zinfo_or_arcname: str | ZipInfo,
        data: bytes | str,
        compress_type: int | None = None,
        compresslevel: int | None = None,
    ) -> None: ...


class DirectorySource(SourceProtocol):
    """An EPUB source that reads the book from a directory on the filesystem (an 'unzipped' EPUB)."""

    def __init__(self, path: str | Path):
        self.path: Path = Path(path)
        if not self.path.is_dir():
            raise EPUBError(f"'{path}' is not a directory")

    @override
    def infolist(self) -> list[ZipInfo]:
        return [
            self._to_zipinfo(str(file.relative_to(self.path)))
            for file in self.path.rglob("*")
            if not file.is_dir()
        ]

    @override
    def getinfo(self, name: str) -> ZipInfo:
        target = self.path / name
        if target.is_file():
            return self._to_zipinfo(name)
        raise KeyError("There is no item named '{name}' in the folder")

    def _to_zipinfo(self, name: str):
        return ZipInfo.from_file(
            self.path / name,
            arcname=name,
            strict_timestamps=False,
        )

    @override
    def open(
        self,
        name: str | ZipInfo,
        mode: Literal["r", "w"] = "r",
        pwd: bytes | None = None,
        *,
        force_zip64: bool = False,
    ) -> IO[bytes]:
        if isinstance(name, ZipInfo):
            filename = self.path / name.filename
        else:
            filename = self.path / name

        return open(filename, mode + "b")


class DirectorySink(SinkProtocol):
    """An EPUB sink that writes the book to a directory on the filesystem (as an 'unzipped' EPUB)."""

    def __init__(self, path: str | Path) -> None:
        self.path: Path = Path(path)
        if not self.path.is_dir():
            raise EPUBError(f"'{path}' is not a directory")

    @override
    def writestr(
        self,
        zinfo_or_arcname: str | ZipInfo,
        data: bytes | str,
        compress_type: int | None = None,
        compresslevel: int | None = None,
    ) -> None:
        if isinstance(zinfo_or_arcname, ZipInfo):
            filename = zinfo_or_arcname.filename
        else:
            filename = zinfo_or_arcname

        full_path = self.path / filename

        if str(full_path.parent) != ".":
            full_path.parent.mkdir(exist_ok=True, parents=True)

        mode = "w" if isinstance(data, str) else "wb"
        with open(full_path, mode) as f:
            __ = f.write(data)
