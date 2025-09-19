import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal, Self, overload, override

import bs4

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.package.spine import SpineItemRef
from epublib.resources import Resource
from epublib.util import attr_to_str, get_absolute_href, get_relative_href
from epublib.xml_element import XMLElement, XMLParent


def detect_remote_resources(soup: bs4.BeautifulSoup):
    for attr in "src", "href":
        for tag in soup.select(f"[{attr}]"):
            ref = attr_to_str(tag.get("src"))
            if ref is not None:
                if re.search(r"^\w+://.*$", ref):
                    return True

                if ref.startswith("/"):
                    return True

    return False


def detect_manifest_properties(soup: bs4.BeautifulSoup) -> list[str]:
    properties: list[str] = []

    if soup.find("math"):
        properties.append("math")

    if detect_remote_resources(soup):
        properties.append("remote-resources")

    if soup.find("script"):
        properties.append("scripted")

    if soup.find("epub:switch"):
        properties.append("switch")

    return properties


@dataclass(kw_only=True)
class ManifestItem(XMLElement):
    """An item in the EPUB manifest."""

    id: EPUBId
    media_type: str
    fallback: str | None = None
    media_overlay: str | None = None
    properties: list[str] | None = None
    _href: str = ""
    manifest_filename: str

    exclude_from_tag: ClassVar[list[str]] = ["tag", "name", "manifest_filename"]
    obj_to_tag: ClassVar[dict[str, str]] = {"_href": "href"}

    @property
    @override
    def tag_name(self):
        return "item"

    @override
    @classmethod
    def from_tag(
        cls,
        tag: bs4.Tag,
        filename: str = "",
        manifest_filename: str = "",
        **kwargs: str,
    ) -> Self:
        assert filename, "Can't initialize manifest item without absolute filename"
        assert manifest_filename, (
            "Can't initialize manifest item without manifest filename"
        )

        return super().from_tag(
            tag=tag,
            name=filename,
            manifest_filename=manifest_filename,
        )

    @property
    def filename(self):
        return self.name

    @filename.setter
    def filename(self, value: str):
        self.name: str = value
        self._href = get_relative_href(self.manifest_filename, value)

    @property
    def href(self):
        return self._href

    @href.setter
    def href(self, value: str):
        self._href = value
        self.name = get_absolute_href(self.manifest_filename, value)

    def __post_init__(self):
        super().__post_init__()
        self.id = EPUBId(self.id)
        self._href = self._href or get_relative_href(self.manifest_filename, self.name)

    def add_property(self, prop: str):
        if self.properties is None:
            self.properties = []
        if prop not in self.properties:
            self.properties.append(prop)

    def has_property(self, prop: str) -> bool:
        if self.properties is None:
            return False
        return prop in self.properties

    def remove_property(self, prop: str):
        if self.properties is None:
            return
        try:
            self.properties.remove(prop)
        except ValueError:
            pass

        if not self.properties:
            self.properties = None


class BookManifest(XMLParent[ManifestItem]):
    """The EPUB manifest, which is a list of all resources in the book."""

    def __init__(self, tag: bs4.Tag, filename: str) -> None:
        self._resource_filename: str = filename
        self._nav: ManifestItem | None = None
        self._cover_image: ManifestItem | None = None

        super().__init__(tag)

    @override
    def create_items(self) -> list[ManifestItem]:
        items: list[ManifestItem] = []

        for tag in self.tag.select("item"):
            absolute_href = get_absolute_href(
                self._resource_filename,
                attr_to_str(tag["href"]),
            )
            item = ManifestItem.from_tag(
                tag,
                absolute_href,
                manifest_filename=self._resource_filename,
            )
            items.append(item)

            if item.properties:
                if "nav" in item.properties:
                    self._nav = item

                if "cover-image" in item.properties:
                    self._cover_image = item

        return items

    @property
    def nav(self):
        if self._nav is None:
            self._nav = next(
                (
                    item
                    for item in self.items
                    if item.properties and "nav" in item.properties
                ),
                None,
            )
        return self._nav

    @property
    def cover_image(self):
        if self._cover_image is None:
            self._cover_image = next(
                (
                    item
                    for item in self.items
                    if item.properties and "cover-image" in item.properties
                ),
                None,
            )
        return self._cover_image

    def set_cover_image(self, item: ManifestItem | str | Path | EPUBId):
        if not isinstance(item, ManifestItem):
            if isinstance(item, EPUBId):
                item = self._get_by_id(item, raise_error=True)
            else:
                item = self[item]

        item.add_property("cover-image")
        for other in self.items:
            if other is not item:
                other.remove_property("cover-image")

    @override
    def add_item(self, item: ManifestItem) -> ManifestItem:
        if item in self.items:
            raise EPUBError(f"Item {item} is already in the manifest")

        if any(
            item.id == other.id or item.filename == other.filename
            for other in self.items
        ):
            if any(item.id == other.id for other in self.items):
                raise EPUBError(f"An item with id {item.id} is already in the manifest")

            if any(item.filename == other.filename for other in self.items):
                raise EPUBError(
                    f"An item with filename {item.filename} is already in the manifest"
                )

        return super().add_item(item)

    @overload
    def _get_by_id(self, id: EPUBId, raise_error: Literal[True]) -> ManifestItem: ...

    @overload
    def _get_by_id(
        self,
        id: EPUBId,
        raise_error: bool = False,
    ) -> ManifestItem | None: ...

    def _get_by_id(self, id: EPUBId, raise_error: bool = False):
        try:
            return next(item for item in self.items if item.id == id)
        except StopIteration as exception:
            if raise_error:
                raise KeyError(id) from exception
            return None

    @override
    def __getitem__(self, name: Path | str | EPUBId | SpineItemRef):
        value = self.get(name)
        if value is None:
            raise KeyError(name)
        return value

    @override
    def get(
        self,
        name: str | Path | Resource | SpineItemRef,
        cls: type[XMLElement] | None = None,
    ):
        if isinstance(name, (EPUBId, SpineItemRef)):
            if isinstance(name, SpineItemRef):
                name = name.idref
            item = self._get_by_id(name, raise_error=False)
            if item is None:
                return None
            name = item.filename

        elif isinstance(name, Resource):
            name = name.filename

        return super().get(str(name))

    def remove(self, filename: str | EPUBId):
        if isinstance(filename, EPUBId):
            filename = self._get_by_id(filename, raise_error=True).filename
        return self.remove_item(self[filename])

    def get_new_id(self, filename: str | Path):
        path = Path(filename)
        stem = path.stem
        suffix = path.suffix

        new_id = f"{stem}{suffix}"

        i = 1
        while self._get_by_id(EPUBId(new_id)) and i < 1000:
            i += 1
            new_id = f"{new_id}-{i}{suffix}"

        return EPUBId(new_id)
