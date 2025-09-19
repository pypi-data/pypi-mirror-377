from collections.abc import Generator
from pathlib import Path
from typing import IO, Any, cast, override
from zipfile import ZipFile, is_zipfile

from epublib.create import EPUBCreator
from epublib.exceptions import ClosedEPUBError, EPUBError, NotEPUBError
from epublib.identifier import EPUBId
from epublib.mediatype import Category, MediaType
from epublib.nav.reset import (
    create_landmarks,
    create_page_list,
    create_toc,
    reset_landmarks,
    reset_page_list,
    reset_toc,
)
from epublib.nav.resource import NavigationDocument
from epublib.ncx.reset import generate_ncx, reset_ncx
from epublib.ncx.resource import NCXFile
from epublib.package.manifest import (
    BookManifest,
    ManifestItem,
    detect_manifest_properties,
)
from epublib.package.metadata import BookMetadata, ValuedMetadataItem
from epublib.package.resource import PackageDocument
from epublib.package.spine import BookSpine, SpineItemRef
from epublib.parse import parse
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    XMLResource,
)
from epublib.resources.manager import ResourceIdentifier, ResourceManager
from epublib.source import (
    DirectorySink,
    DirectorySource,
    SinkProtocol,
    SourceProtocol,
)
from epublib.util import get_epublib_version


class EPUB:
    """
    The main class for reading, writing, and manipulating EPUB files.
    """

    def __init__(
        self,
        file: IO[bytes] | str | Path | None = None,
        generator_tag: bool = True,
    ) -> None:
        self.source: SourceProtocol

        if file is None:
            self.source = ZipFile(
                EPUBCreator(add_generator_tag=generator_tag).to_file()
            )
        elif is_zipfile(file):
            self.source = ZipFile(file)
        elif (isinstance(file, str) or isinstance(file, Path)) and Path(file).is_dir():
            self.source = DirectorySource(file)
        else:
            raise NotEPUBError(f"file '{file}' is not ZIP nor folder")

        self._closed: bool = False
        self.container_file: XMLResource
        self.package_document: PackageDocument
        self.container_file, self.package_document, resources = parse(self.source)
        self.resources: ResourceManager = ResourceManager(
            resources,
            container_file=self.container_file,
            package_document=self.package_document,
            nav_getter=lambda: self.nav,
            ncx_getter=lambda: self.ncx,
        )

        self.original_path: Path | None = (
            Path(file) if isinstance(file, str) or isinstance(file, Path) else None
        )

        if generator_tag:
            self.add_generator_tag()

    def close(self):
        for resource in self.resources:
            resource.close()
        self._closed = True

    def is_closed(self):
        return self._closed

    def _check_closed(self, msg: str = "EPUB is already closed"):
        if self._closed:
            raise ClosedEPUBError(msg)

    def __enter__(self):
        return self

    def __exit__(self, *args: Any):  # type: ignore[Any]
        self.close()

    def add_generator_tag(self):
        """Add a generator meta tag to the metadata."""

        generator = self.metadata.get("generator")
        if not generator:
            generator = self.metadata.add("generator", "Edited with epublib")

        version = get_epublib_version()
        version_item = self.metadata.get("epublib version")
        if not version_item and version:
            __ = self.metadata.add("epublib version", version)

    def remove_generator_tag(self):
        """Remove the epublib generator tag of the metadata, if any."""

        generator = self.metadata.get("generator")
        if (
            generator
            and isinstance(generator, ValuedMetadataItem)
            and "epublib" in generator.value
        ):
            self.metadata.remove_item(generator)

        version_item = self.metadata.get("epublib version")
        if version_item:
            self.metadata.remove_item(version_item)

    def write_to_sink(self, out: SinkProtocol):
        """Write this epub to a sink"""

        self._check_closed("trying to write closed EPUB")

        for resource in self.resources:
            out.writestr(resource.zipinfo, resource.content)
            resource.free()

    def write(self, output_file: IO[bytes] | str | Path) -> None:
        """Write this epub to a zip file"""

        out_zip = ZipFile(output_file, mode="w")
        self.write_to_sink(out_zip)

    def write_to_folder(self, folder: str | Path):
        """Write this epub to a folder ('unzipped')"""

        if not Path(folder).is_dir():
            raise EPUBError(f"Path '{folder}' is not a directory")

        out = DirectorySink(folder)
        self.write_to_sink(out)

    def documents(self) -> Generator[ContentDocument]:
        """
        Retrieve all content documents (XHTML or SVG) from this EPUB
        """

        yield from self.resources.filter(ContentDocument)

    def images(self) -> Generator[PublicationResource]:
        """
        Retrieve all image resources from this EPUB
        """

        yield from self.resources.filter(Category.IMAGE)

    def scripts(self) -> Generator[PublicationResource]:
        """
        Retrieve all JavaScript resources from this EPUB
        """

        return (
            resource
            for resource in self.resources.filter(Category.OTHER)
            if cast(MediaType, resource.media_type).is_js()
        )

    def styles(self) -> Generator[PublicationResource]:
        """
        Retrieve all CSS resources from this EPUB
        """

        return (
            resource
            for resource in self.resources.filter(Category.STYLE)
            if cast(MediaType, resource.media_type).is_css()
        )

    def get_spine_item(
        self,
        resource: Resource | ResourceIdentifier,
    ) -> SpineItemRef | None:
        """Get spine item associated with a resource or filename"""

        if isinstance(resource, EPUBId):
            return self.spine.get(resource)

        if isinstance(resource, ManifestItem):
            manifest_item = resource
        else:
            manifest_item = self.manifest.get(resource)

        if not manifest_item:
            return None

        return self.spine.get(manifest_item.id)

    def rename_id(
        self,
        old: Resource | ResourceIdentifier,
        new: EPUBId,
    ) -> None:
        """
        Rename a manifest identifier. Look for references for updating
        it in the spine items, the cover-image metadata tag, and the toc
        attribute of the spine element. Using this function is not
        recommended, as there may be other references to the old id that
        will become outdated.
        """

        if not isinstance(old, ManifestItem):
            manifest_item = self.manifest.get(old)
        else:
            manifest_item = old

        if not manifest_item:
            raise EPUBError(f"Can't rename '{old}: not in manifest")

        old_id = manifest_item.id

        existing = self.manifest.get(new)
        if existing:
            raise EPUBError(f"Can't rename to already existing id '{new}' ({existing})")

        # cover-image in metadata
        cover = self.metadata.get("cover-image")
        if cover and cover:
            cover.value = new

        # spine tag
        if self.spine.tag.attrs["toc"] == old_id:
            self.spine.tag.attrs["toc"] = new

        spine_item = self.spine.get(old_id)
        if spine_item:
            spine_item.idref = new

        manifest_item.id = new

    def get_spine_position(
        self,
        resource: Resource | ResourceIdentifier,
    ) -> int | None:
        """Get the 0-indexed position of a resource in the spine"""

        if isinstance(resource, EPUBId):
            epub_id = resource
        else:
            if isinstance(resource, ManifestItem):
                manifest_item = resource
            else:
                manifest_item = self.manifest.get(resource)

            if not manifest_item:
                return None
            epub_id = manifest_item.id

        return self.spine.get_position(epub_id)

    def update_manifest_properties(self) -> None:
        """
        Update manifest properties by detecting them from the resources
        See https://www.w3.org/TR/epub-33/#sec-item-resource-properties
        """

        for item in self.manifest.items:
            resource = self.resources.get(item.name, XMLResource)
            if resource:
                item.properties = list(
                    set(
                        (item.properties if item.properties is not None else [])
                        + detect_manifest_properties(resource.soup)
                    )
                )

    def reset_toc(
        self,
        targets_selector: str | None = None,
        include_filenames: bool = False,
        spine_only: bool = False,  # ensures correct ordering
        reset_ncx: bool | None = None,
        resource_class: type[Resource] = ContentDocument,
    ):
        """
        Reset the table of contents in the navigation document by
        detecting targets in content documents. May replace any
        existing TOC.
        """
        return reset_toc(
            self,
            targets_selector,
            include_filenames,
            spine_only,
            reset_ncx,
            resource_class,
        )

    def create_toc(
        self,
        targets_selector: str | None = None,
        include_filenames: bool = False,
        spine_only: bool = False,  # ensures correct ordering
        reset_ncx: bool | None = None,
        resource_class: type[Resource] = ContentDocument,
    ):
        """
        Create o new table of contents in the navigation document by
        detecting targets in content documents. Will raise an error if
        a TOC already exists.
        """
        return create_toc(
            self,
            targets_selector,
            include_filenames,
            spine_only,
            reset_ncx,
            resource_class,
        )

    def reset_page_list(
        self,
        id_format: str = "page_{page}",
        label_format: str = "{page}",
        pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
        reset_ncx: bool | None = None,
    ):
        """
        Reset the page list in the navigation document by detecting
        pagebreaks in content documents. Will replace any existing page
        list.
        """
        return reset_page_list(
            self,
            id_format,
            label_format,
            pagebreak_selector,
            reset_ncx,
        )

    def create_page_list(
        self,
        id_format: str = "page_{page}",
        label_format: str = "{page}",
        pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
        reset_ncx: bool | None = None,
    ):
        """
        Create new page list in the navigation document by detecting
        pagebreaks in content documents. Will raise an error if a page
        list already exists.
        """
        return create_page_list(
            self,
            id_format,
            label_format,
            pagebreak_selector,
            reset_ncx,
        )

    def reset_landmarks(
        self,
        include_toc: bool = True,
        targets_selector: str | None = None,
    ):
        """
        Reset the landmarks in the navigation document by detecting
        targets in content documents, and optionally including the TOC.
        Will replace existing landmarks.
        """

        return reset_landmarks(self, include_toc, targets_selector)

    def create_landmarks(
        self,
        include_toc: bool = True,
        targets_selector: str | None = None,
    ):
        """
        Create landmarks in the navigation document by detecting
        targets in content documents, and optionally including the TOC.
        Will raise error if landmarks already exist.
        """

        return create_landmarks(self, include_toc, targets_selector)

    def generate_ncx(self, filename: str | Path | None = None) -> NCXFile:
        return generate_ncx(self, filename)

    def reset_ncx(self, ncx: NCXFile | None = None) -> NCXFile:
        return reset_ncx(self, ncx)

    @property
    def base_dir(self):
        """
        The base directory for the resources in this EPUB. This is an
        holistic property, and the spec does not define it. There may be
        more than one base directory in an EPUB. This is the one
        containing the package document.
        """

        return Path(self.package_document.filename).parent

    @property
    def manifest(self) -> BookManifest:
        return self.package_document.manifest

    @property
    def metadata(self) -> BookMetadata:
        return self.package_document.metadata

    @property
    def spine(self) -> BookSpine:
        return self.package_document.spine

    @property
    def nav(self):
        return (
            self.resources.get(self.manifest.nav.filename, NavigationDocument)
            if self.manifest.nav
            else None
        )

    @property
    def ncx(self) -> NCXFile | None:
        return next(self.resources.filter(NCXFile), None)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title='{self.metadata.title or id(self)}')"
