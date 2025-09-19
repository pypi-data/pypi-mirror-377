from pathlib import Path
from typing import IO, cast, override
from zipfile import ZipInfo

import bs4

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.mediatype import MediaType, guess_file_type
from epublib.package.manifest import (
    BookManifest,
    ManifestItem,
    detect_manifest_properties,
)
from epublib.package.metadata import BookMetadata
from epublib.package.spine import BookSpine
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    XMLResource,
)
from epublib.soup import PackageDocumentSoup


class PackageDocument(XMLResource[PackageDocumentSoup]):
    """The package document of the EPUB file, sometimes known as the 'content.opf' file."""

    soup_class: type[PackageDocumentSoup] = PackageDocumentSoup

    def __init__(self, file: IO[bytes] | bytes, info: ZipInfo | str | Path) -> None:
        super().__init__(file, info)
        self._manifest: BookManifest | None = None
        self._metadata: BookMetadata | None = None
        self._spine: BookSpine | None = None

    @property
    def manifest(self):
        if self._manifest is None:
            self._manifest = BookManifest(self.soup.manifest, self.filename)
        return self._manifest

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = BookMetadata(self.soup.metadata)
        return self._metadata

    @property
    def spine(self):
        if self._spine is None:
            self._spine = BookSpine(self.soup.spine)
        return self._spine

    def remove(self, filename: str):
        item = self.manifest[filename]
        spine_item = self.spine.get(item.id)
        if spine_item:
            self.spine.remove_item(spine_item)
        self.manifest.remove_item(item)

    def on_soup_change(self):
        del self._manifest
        del self._metadata
        del self._spine
        self._manifest = None
        self._metadata = None
        self._spine = None

    @override
    def on_content_change(self):
        super().on_content_change()
        self.on_soup_change()


def resource_to_manifest_item(
    resource: Resource,
    package: PackageDocument,
    identifier: EPUBId | str | None = None,
    media_type: str | MediaType | None = None,
    fallback: str | None = None,
    media_overlay: str | None = None,
    is_nav: bool = False,
    is_cover: bool = False,
    properties: list[str] | None = None,
    detect_properties: bool = True,
):
    name = resource.filename

    if identifier is None:
        identifier = package.manifest.get_new_id(resource.filename)
    elif package.manifest.get(identifier) is not None:
        raise EPUBError(f"Identifier '{identifier}' is already used in the manifest")

    if media_type is None:
        media_type = (
            resource.media_type
            if isinstance(resource, PublicationResource)
            else guess_file_type(resource.filename)
        )

    if not media_type:
        raise EPUBError(f"Can't determine media type of file {resource.filename}")

    if detect_properties or is_nav or is_cover:
        properties = properties if properties is not None else []

        if detect_properties and isinstance(resource, ContentDocument):
            properties += detect_manifest_properties(
                cast(ContentDocument[bs4.BeautifulSoup], resource).soup
            )

        if is_nav:
            properties.append("nav")

        if is_cover:
            properties.append("cover-image")

        properties = list(set(properties))

    return ManifestItem(
        name=name,
        id=EPUBId(identifier),
        media_type=str(media_type),
        media_overlay=media_overlay,
        fallback=fallback,
        properties=properties,
        manifest_filename=package.filename,
    )
