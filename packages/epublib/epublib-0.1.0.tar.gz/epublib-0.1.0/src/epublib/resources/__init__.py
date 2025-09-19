import io
from mimetypes import guess_file_type
from pathlib import Path
from typing import IO, override
from zipfile import ZipInfo

import bs4

from epublib.exceptions import EPUBError
from epublib.mediatype import Category, MediaType
from epublib.source import zip_info_now
from epublib.util import get_absolute_href


def info_to_zipinfo(info: ZipInfo | str | Path) -> ZipInfo:
    if isinstance(info, ZipInfo):
        return info

    return ZipInfo(filename=str(info), date_time=zip_info_now())


class Resource:
    """Base class for all resources (i.e. files) in an EPUB file."""

    def __init__(self, file: IO[bytes] | bytes, info: ZipInfo | str | Path) -> None:
        self.zipinfo: ZipInfo = info_to_zipinfo(info)
        self._file: IO[bytes] | None = (
            io.BytesIO(file) if isinstance(file, bytes) else file
        )
        self._content: bytes | None = None
        self._closed: bool = False

    @classmethod
    def from_path(cls, filename: str | Path, location: str | Path):
        file = open(filename, "rb")
        zipinfo = ZipInfo.from_file(filename, location, strict_timestamps=False)
        return cls(file, zipinfo)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.filename})"

    def on_content_change(self):
        pass

    @property
    def filename(self):
        return self.zipinfo.filename

    @filename.setter
    def filename(self, value: str):
        self._set_filename(value)

    def _set_filename(self, value: str):
        self.zipinfo.filename = value

    @property
    def content(self) -> bytes:
        self.check_closed()
        if self._content is None:
            if self._file is None:
                return b""
            self._content = self._file.read()
            __ = self._file.seek(0)
        return self._content

    @content.setter
    def content(self, value: bytes):
        self.check_closed()
        self._set_content(value)

    def _set_content(self, value: bytes, content_change: bool = True):
        self._content = value
        if content_change:
            self.on_content_change()

    def free(self):
        del self._content
        self._content = None
        self.on_content_change()

    def get_title(self):
        return self.filename

    def check_closed(self):
        if self._closed:
            raise EPUBError(f"Using resource {self.filename} after closing")

    def close(self):
        self.free()
        if self._file is not None:
            self._file.close()
            self._file = None

    def href_to_filename[T: (str, Path)](self, href: T) -> T:
        return get_absolute_href(self.filename, href)


class XMLResource[S: bs4.BeautifulSoup = bs4.BeautifulSoup](Resource):
    """A resource that is an XML file."""

    soup_class: type[S] = bs4.BeautifulSoup  # type: ignore[reportAssignmentType]

    def __init__(self, file: IO[bytes] | bytes, info: ZipInfo | str | Path) -> None:
        super().__init__(file, info)
        self._soup: None | S = None

    @property
    def soup(self) -> S:
        if self._soup is None:
            self._soup = self.soup_class(self.content, "xml")
        return self._soup

    @soup.setter
    def soup(self, value: S):
        self._set_soup(value)

    def _set_soup(self, value: S):
        self._soup = value

    @property
    @override
    def content(self):
        if self._soup is not None:
            self._set_content(self._soup.encode(), content_change=False)
        return super().content

    @content.setter
    def content(self, value: bytes):
        super()._set_content(value)

    @override
    def on_content_change(self):
        super().on_content_change()
        del self._soup
        self._soup = None

    @override
    def get_title(self):
        if self.soup.title and self.soup.title.string:
            return self.soup.title.string
        return super().get_title()


class PublicationResource(Resource):
    """
    A resource that contributes to the logic and rendering of the publication.

    This includes resources like the package document, content documents (XHTML),
    CSS stylesheets, audio, video, images, fonts, and scripts.
    """

    def __init__(
        self,
        file: IO[bytes] | bytes,
        info: ZipInfo | str | Path,
        media_type: MediaType | str | None = None,
    ) -> None:
        super().__init__(file, info)
        if media_type is None:
            media_type = guess_file_type(self.zipinfo.filename)[0]
            if media_type is None:
                raise EPUBError(
                    f"Cannot determine media type of {self.zipinfo.filename}"
                )

            media_type = MediaType.coalesce(media_type)
        self.media_type: MediaType | str = media_type

    @property
    def is_foreign(self):
        return isinstance(self.media_type, str)

    @property
    def category(self):
        if isinstance(self.media_type, str):
            return Category.FOREIGN
        return self.media_type.category

    @classmethod
    def from_resource(cls, other: Resource, media_type: str | MediaType | None = None):
        if other._file is None or other._closed:
            raise EPUBError(f"Using resource {other} after closing")

        return cls(other._file, other.zipinfo, media_type)


class ContentDocument[S: bs4.BeautifulSoup = bs4.BeautifulSoup](  # type: ignore[reportUnsafeMultipleInheritance]
    PublicationResource,
    XMLResource[S],
):
    """
    A publication resource referenced from the spine or a manifest fallback
    chain that conforms to either the XHTML or SVG content document definitions.
    """

    @override
    def get_title(self):
        if self.soup.h1 and self.soup.h1.string:
            return self.soup.h1.string
        return super().get_title()
