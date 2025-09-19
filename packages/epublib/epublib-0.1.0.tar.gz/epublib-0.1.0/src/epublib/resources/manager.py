from collections.abc import Callable, Generator, Iterable
from pathlib import Path
from typing import Literal, TypedDict, Unpack, cast, overload

import bs4

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.mediatype import Category, MediaType
from epublib.nav.resource import NavigationDocument
from epublib.ncx.resource import NCXFile
from epublib.package.manifest import BookManifest, ManifestItem
from epublib.package.resource import PackageDocument, resource_to_manifest_item
from epublib.package.spine import BookSpine, SpineItemRef
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    XMLResource,
)
from epublib.util import (
    attr_to_str,
    get_absolute_href,
    get_relative_href,
    normalize_path,
    split_fragment,
)

type ResourceIdentifier = str | Path | EPUBId | ManifestItem | SpineItemRef
type ResourceQuery = type[Resource] | MediaType | Category | str


class AddResourceOptions(TypedDict, total=False):
    is_cover: bool
    after: Resource | ResourceIdentifier | None
    before: Resource | ResourceIdentifier | None
    add_to_manifest: bool | None
    identifier: str | EPUBId | None
    add_to_spine: bool | None
    spine_position: int | None
    linear: bool | None
    add_to_toc: bool | None
    toc_position: int | None
    add_to_ncx: bool | None
    ncx_position: int | None


def ri_to_filename(
    identifier: ResourceIdentifier,
    manifest: BookManifest,
) -> str:
    """
    Convert various resource identifier types to its corresponding filename
    """

    if isinstance(identifier, ManifestItem):
        return identifier.filename

    if isinstance(identifier, (EPUBId, SpineItemRef)):
        return manifest[identifier].filename

    return str(identifier)


def ri_to_id(
    identifier: ResourceIdentifier,
    manifest: BookManifest,
) -> EPUBId:
    """
    Convert various resource identifier types to its corresponding EPUBId
    """

    if isinstance(identifier, ManifestItem):
        return identifier.id

    if isinstance(identifier, EPUBId):
        return identifier

    if isinstance(identifier, SpineItemRef):
        return identifier.idref

    return manifest[identifier].id


class ResourceManager:
    def __init__(
        self,
        resources_list: Iterable[Resource],
        container_file: XMLResource,
        package_document: PackageDocument,
        nav_getter: Callable[[], NavigationDocument | None] = lambda: None,
        ncx_getter: Callable[[], NCXFile | None] = lambda: None,
    ):
        self._resources: list[Resource] = list(resources_list)
        self.container_file: XMLResource = container_file
        self.package_document: PackageDocument = package_document
        self._get_nav: Callable[[], NavigationDocument | None] = nav_getter
        self._get_ncx: Callable[[], NCXFile | None] = ncx_getter

    def ri_to_filename(self, identifier: ResourceIdentifier) -> str:
        return ri_to_filename(identifier, self.manifest)

    def ri_to_id(self, identifier: ResourceIdentifier) -> EPUBId:
        return ri_to_id(identifier, self.manifest)

    @property
    def manifest(self) -> BookManifest:
        return self.package_document.manifest

    @property
    def spine(self) -> BookSpine:
        return self.package_document.spine

    @property
    def ncx(self) -> NCXFile | None:
        return self._get_ncx()

    @property
    def nav(self) -> NavigationDocument | None:
        return self._get_nav()

    @overload
    def filter[R: Resource](self, query: type[R]) -> Generator[R]: ...
    @overload
    def filter(self, query: type[Resource] = Resource) -> Generator[Resource]: ...
    @overload
    def filter(
        self, query: Literal[MediaType.XHTML, MediaType.IMAGE_SVG]
    ) -> Generator[ContentDocument]: ...
    @overload
    def filter(self, query: Literal[MediaType.NCX]) -> Generator[NCXFile]: ...
    @overload
    def filter(self, query: MediaType | Category) -> Generator[PublicationResource]: ...

    def filter(self, query: ResourceQuery = Resource) -> Generator[Resource]:
        if isinstance(query, type):
            yield from (
                resource for resource in self._resources if isinstance(resource, query)
            )
        elif isinstance(query, Category):
            yield from (
                resource
                for resource in self._resources
                if isinstance(resource, PublicationResource)
                and isinstance(resource.media_type, MediaType)
                and resource.media_type.category is query
            )
        else:
            yield from (
                resource
                for resource in self._resources
                if isinstance(resource, PublicationResource)
                and resource.media_type == MediaType.coalesce(query)
            )

    @overload
    def get[R: PublicationResource](
        self, identifier: EPUBId | ManifestItem, cls: type[R]
    ) -> R | None: ...
    @overload
    def get(
        self,
        identifier: EPUBId | ManifestItem | SpineItemRef,
        cls: type[PublicationResource] = PublicationResource,
    ) -> PublicationResource | None: ...
    @overload
    def get[R: Resource](self, identifier: str | Path, cls: type[R]) -> R | None: ...
    @overload
    def get(
        self, identifier: str | Path, cls: type[Resource] = Resource
    ) -> Resource | None: ...

    def get(
        self, identifier: ResourceIdentifier, cls: type[Resource] = Resource
    ) -> Resource | None:
        identifier = self.ri_to_filename(identifier)

        return next(
            (
                resource
                for resource in self.filter(cls)
                if resource.filename == identifier
            ),
            None,
        )

    @overload
    def __getitem__(self, identifier: slice) -> list[Resource]: ...
    @overload
    def __getitem__(self, identifier: ResourceIdentifier | int) -> Resource: ...
    def __getitem__(self, identifier: ResourceIdentifier | int | slice):
        if isinstance(identifier, (int, slice)):
            return self._resources[identifier]

        resource = self.get(identifier)
        if resource is None:
            raise KeyError(identifier)

        return resource

    def __iter__(self) -> Generator[Resource]:
        yield from self._resources

    def __len__(self) -> int:
        return len(self._resources)

    def _resolve_position(
        self,
        default: int,
        position: int | None = None,
        after: Resource | None = None,
        before: Resource | None = None,
    ):
        if after and position is None:
            try:
                return self._resources.index(after) + 1
            except ValueError as error:
                raise EPUBError(
                    f"resource provided as argument 'after' ('{after}') "
                    "must be part of this epub"
                ) from error
        if before and position is None:
            try:
                return self._resources.index(before) - 1
            except ValueError as error:
                raise EPUBError(
                    f"resource provided as argument 'before' ('{after}') "
                    "must be part of this epub"
                ) from error
        if position:
            return position
        return default

    @staticmethod
    def _should_be_manifested(resource: Resource) -> bool:
        return Path(resource.filename).parts[0] != "META-INF"

    @staticmethod
    def _should_be_in_spine(resource: Resource) -> bool:
        return isinstance(resource, ContentDocument)

    @staticmethod
    def _should_be_spine_linear(_resource: Resource) -> bool:
        return True

    def add_to_manifest[T: Resource](
        self,
        resource: T,
        media_type: MediaType | str | None = None,
        identifier: EPUBId | str | None = None,
        fallback: str | None = None,
        media_overlay: str | None = None,
        is_cover: bool = False,
        is_nav: bool = False,
        properties: list[str] | None = None,
        detect_properties: bool = True,
        exists_ok: bool = True,
    ) -> tuple[T, ManifestItem]:
        """
        Add a resource to the manifest, if not already present. The
        resource may be promoted to a PublicationResource if needed, so
        the resource is returned as well.
        """
        manifest_item = self.manifest.get(resource.filename)
        if manifest_item:
            if exists_ok:
                return resource, manifest_item
            raise EPUBError(f"Resource '{resource.filename}' already in manifest")

        # Promoting to PublicationResource
        if not isinstance(resource, PublicationResource):
            new_resource = PublicationResource.from_resource(resource, media_type)
            try:
                index = self._resources.index(resource)
                self._resources[index] = new_resource
            except ValueError:
                pass

            resource = new_resource

        manifest_item = resource_to_manifest_item(
            resource,
            self.package_document,
            media_type=media_type,
            identifier=identifier,
            fallback=fallback,
            media_overlay=media_overlay,
            is_cover=is_cover,
            is_nav=is_nav,
            properties=properties,
            detect_properties=detect_properties,
        )
        __ = self.manifest.add_item(manifest_item)

        return resource, manifest_item

    def add(
        self,
        resource: Resource,
        is_cover: bool = False,
        position: int | None = None,
        after: Resource | ResourceIdentifier | None = None,
        before: Resource | ResourceIdentifier | None = None,
        add_to_manifest: bool | None = None,
        identifier: str | EPUBId | None = None,
        add_to_spine: bool | None = None,
        spine_position: int | None = None,
        linear: bool | None = None,
        add_to_toc: bool | None = None,
        toc_position: int | None = None,
        add_to_ncx: bool | None = None,
        ncx_position: int | None = None,
    ) -> None:
        is_nav = isinstance(resource, NavigationDocument)

        if not isinstance(after, Resource) and after is not None:
            after = self.get(after)
        if not isinstance(before, Resource) and before is not None:
            before = self.get(before)

        position = self._resolve_position(len(self._resources), position, after, before)
        self._resources.insert(position, resource)

        if add_to_manifest is False and add_to_spine:
            raise EPUBError("Cannot add to spine without adding to manifest")

        if add_to_manifest is False and add_to_toc:
            raise EPUBError(
                "Cannot update navigation document without adding to manifest"
            )

        if add_to_manifest is None:
            add_to_manifest = add_to_spine or self._should_be_manifested(resource)

        if add_to_spine is None:
            add_to_spine = add_to_manifest and self._should_be_in_spine(resource)

        if add_to_toc is None:
            add_to_toc = add_to_spine

        if add_to_ncx and not self.ncx:
            raise EPUBError.missing_ncx(self, "add_resource", "add_to_ncx")

        if add_to_ncx is None:
            add_to_ncx = self.ncx is not None and add_to_toc

        if ncx_position is None:
            ncx_position = toc_position

        manifest_item: None | ManifestItem = None

        if add_to_manifest:
            resource, manifest_item = self.add_to_manifest(
                resource,
                identifier=identifier,
                is_cover=is_cover,
                is_nav=is_nav,
                exists_ok=False,
            )

            if spine_position is None:
                spine_position = len(self.spine.items)

            if add_to_spine:
                if linear is None:
                    linear = self._should_be_spine_linear(resource)
                spine_item = SpineItemRef(
                    name=manifest_item.id,
                    linear=linear,
                )
                __ = self.spine.insert_item(spine_position, spine_item)

            if add_to_toc and self.nav:
                __ = self.nav.add_to_toc(
                    resource.filename,
                    resource.get_title(),
                    position=toc_position,
                )

            if add_to_ncx and self.ncx:
                __ = self.ncx.add_to_nav_map(
                    resource.filename,
                    resource.get_title(),
                    position=ncx_position,
                )

    def insert(
        self,
        position: int,
        resource: Resource,
        **kwargs: Unpack[AddResourceOptions],
    ) -> None:
        return self.add(resource, **kwargs, position=position)

    def append(
        self,
        resource: Resource,
        **kwargs: Unpack[AddResourceOptions],
    ) -> None:
        return self.add(resource, **kwargs)

    def remove(
        self,
        resource: ResourceIdentifier | Resource,
        remove_css_js_links: bool = False,
    ):
        """
        Remove a resource from this EPUB. If it is a CSS or JS file,
        you can set the remove_css_js_links flag To remove any link
        from content documents to it.
        """

        if not isinstance(resource, Resource):
            res = self.get(resource)
            if res is None:
                raise EPUBError(
                    f"Can't remove resource '{resource}' not in this epub ('{self}')"
                )

            resource = res

        elif resource not in self:
            raise EPUBError(f"Resource '{resource}' not in EPUB")

        if resource is self.package_document:
            raise EPUBError("Can't remove package document")

        if resource is self.container_file:
            raise EPUBError("Can't remove container file")

        elif self.nav:
            self.nav.remove(resource.filename)

        if self.ncx and resource is not self.ncx:
            self.ncx.remove(resource.filename)

        self.package_document.remove(resource.filename)
        self._resources.remove(resource)

        if remove_css_js_links:
            if (
                not isinstance(resource, PublicationResource)
                or isinstance(resource.media_type, str)
                or not (resource.media_type.is_css() or resource.media_type.is_js())
            ):
                raise EPUBError(
                    "Can't remove CSS and JavaScript links for file "
                    "that is neither CSS nor JavaScript"
                )

            for res in self.filter(ContentDocument):
                relative_href = get_relative_href(res.filename, resource.filename)
                for tag in res.soup.find_all(
                    "link",
                    rel="stylesheet",
                    href=relative_href,
                ):
                    tag.decompose()
                for tag in res.soup.find_all(
                    "script",
                    src=relative_href,
                ):
                    tag.decompose()

    def rename(
        self,
        resource: ResourceIdentifier | Resource,
        new_filename: str,
        update_references: bool = True,
        reference_attrs: list[str] | None = None,
    ):
        """
        Rename the resource, optionally updating references to it
        """

        if not isinstance(resource, Resource):
            res = self.get(resource)
            if res is None:
                raise EPUBError(
                    f"Can't rename resource '{resource}' not in this epub ('{self}')"
                )

            resource = res

        elif resource not in self:
            raise EPUBError(
                f"Can't rename resource '{resource}' not in this epub ('{self}')"
            )

        if resource is self.container_file:
            raise EPUBError("Can't rename container file")

        if reference_attrs is None:
            reference_attrs = ["href", "src", "full-path", "xlink:href"]
        selector = ", ".join(f"[{attr.replace(':', '|')}]" for attr in reference_attrs)

        if update_references:
            for other_resource in self.filter(XMLResource):
                if other_resource == resource:
                    continue

                old_ref = get_relative_href(other_resource.filename, resource.filename)
                new_ref = get_relative_href(other_resource.filename, new_filename)

                for tag in other_resource.soup.select(selector):
                    for attr in reference_attrs:
                        value = attr_to_str(tag.get(attr))
                        if value is not None:
                            if attr == "full-path":
                                if resource.filename == value:
                                    tag[attr] = new_filename
                            else:
                                ref, identifier = split_fragment(value)
                                if ref == old_ref:
                                    tag[attr] = new_ref + (
                                        f"#{identifier}" if identifier else ""
                                    )

            if isinstance(resource, XMLResource):
                prefix = get_relative_href(new_filename, Path(resource.filename)).parent
                if str(prefix) != ".":
                    soup = cast(bs4.BeautifulSoup, resource.soup)
                    for tag in soup.select(selector):
                        for attr in reference_attrs:
                            value = attr_to_str(tag.get(attr))
                            if value is not None:
                                ref, identifier = split_fragment(value)
                                if ref:
                                    new_ref = str(normalize_path(prefix / ref))
                                    tag[attr] = new_ref

        resource.filename = new_filename

    @overload
    def resolve_href[R: Resource](
        self,
        href: str,
        with_tag: Literal[True],
        relative_to: Resource | ResourceIdentifier | None,
        cls: type[R],
    ) -> tuple[R, bs4.Tag | None] | tuple[None, None]: ...

    @overload
    def resolve_href[R: Resource](
        self,
        href: str,
        with_tag: Literal[False],
        relative_to: Resource | ResourceIdentifier | None,
        cls: type[R],
    ) -> R | None: ...

    @overload
    def resolve_href(
        self,
        href: str,
        with_tag: Literal[True] = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        cls: type[XMLResource] = XMLResource,
    ) -> tuple[XMLResource | None, bs4.Tag | None] | tuple[None, None]: ...

    @overload
    def resolve_href(
        self,
        href: str,
        with_tag: Literal[False],
        relative_to: Resource | ResourceIdentifier | None = None,
        cls: type[Resource] = Resource,
    ) -> Resource | None: ...

    def resolve_href(
        self,
        href: str,
        with_tag: bool = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        cls: type[Resource] = Resource,
    ) -> tuple[Resource | None, bs4.Tag | None] | tuple[None, None] | Resource | None:
        """
        Resolve an href (possibly with a fragment identifier) to a
        resource. Optionally return the tag of the matched fragment
        within that resource.
        """

        if relative_to is not None:
            if isinstance(relative_to, Resource):
                relative_to = relative_to.filename
            else:
                relative_to = self.ri_to_filename(relative_to)

            filename = get_absolute_href(relative_to, href)
        else:
            filename = href

        filename, identifier = split_fragment(filename)
        resource = self.get(filename, cls)

        if not with_tag:
            return resource

        if resource is None:
            return None, None

        if not isinstance(resource, XMLResource):
            return resource, None

        resource = cast(XMLResource, resource)
        return resource, cast(
            bs4.Tag, resource.soup.find(id=identifier)
        ) if identifier is not None else None
