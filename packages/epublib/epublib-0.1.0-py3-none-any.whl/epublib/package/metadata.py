from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Self, override

import bs4

from epublib.exceptions import EPUBError, warn
from epublib.util import datetime_to_str
from epublib.xml_element import ValueType, XMLElement, XMLParent


class EPUBMetadataError(EPUBError):
    """An error occurred while parsing EPUB metadata."""


@dataclass(kw_only=True)
class MetadataItem(XMLElement, ABC):
    """Abstract base class for EPUB metadata items."""

    @classmethod
    def detect(cls, tag: bs4.Tag):
        if tag.name == "link" and tag.get("href"):
            return LinkMetadataItem.from_tag(tag)
        if tag.prefix == "dc":
            return DublinCoreMetadataItem.from_tag(tag)
        if tag.name == "meta" and tag.get("content"):
            return OPF2MetadataItem.from_tag(tag)
        if tag.name == "meta" and tag.get("property") and tag.string:
            return GenericMetadataItem.from_tag(tag)
        raise ValueError(f"{tag.name} is not a metadata item")


@dataclass(kw_only=True)
class LinkMetadataItem(MetadataItem):
    """A link metadata item, used for linking to resources."""

    # 'name' corresponds to href in the xml
    hreflang: str | None = None
    media_type: str | None = None
    properties: str | None = None
    refines: str | None = None
    rel: str | None = None

    obj_to_tag: ClassVar[dict[str, str]] = {"name": "href"}

    @property
    @override
    def tag_name(self):
        return "link"

    @classmethod
    @override
    def from_tag(cls, tag: bs4.Tag, **kwargs: str) -> Self:
        if not tag.name == "link" or not tag["href"]:
            raise ValueError(f"{tag.name} is not generic metadata item")

        return super().from_tag(tag, **kwargs)


@dataclass
class ValuedMetadataItem(MetadataItem, ABC):
    """Abstract base class for all metadata items that have a value (i.e., all except LinkMetadataItem)."""

    value: str
    id: str | None = None


@dataclass
class DublinCoreMetadataItem(ValuedMetadataItem):
    """A Dublin Core metadata item."""

    dir: str | None = None
    lang: str | None = None

    obj_to_tag: ClassVar[dict[str, str]] = {"lang": "xml:lang"}
    exclude_from_tag: ClassVar[list[str]] = ["tag", "name", "value"]

    @property
    @override
    def tag_name(self):
        return f"dc:{self.name}"

    @override
    def create_tag(self, soup: bs4.BeautifulSoup, **kwargs: str) -> bs4.Tag:
        tag = super().create_tag(soup, **kwargs)
        tag.string = self.value

        return tag

    @classmethod
    @override
    def from_tag(cls, tag: bs4.Tag, **kwargs: str) -> Self:
        if not tag.prefix == "dc":
            raise ValueError(f"{tag.name} is no Dublin Core metadata item")

        name = tag.name
        value = tag.string if tag.string is not None else ""

        return super().from_tag(tag, name=name, value=value)

    @override
    def update_tag(self, field: str, value: ValueType | None):
        if field == "name" and isinstance(value, str):
            self.tag.name = value
        elif field == "value":
            if value is None:
                self.tag.string = ""
            else:
                self.tag.string = self.value_to_str(field, value)
        else:
            super().update_tag(field, value)


@dataclass
class OPF2MetadataItem(ValuedMetadataItem):
    """An OPF2 metadata item."""

    obj_to_tag: ClassVar[dict[str, str]] = {"value": "content"}

    @property
    @override
    def tag_name(self):
        return "meta"

    @classmethod
    @override
    def from_tag(cls, tag: bs4.Tag, **kwargs: str) -> Self:
        if (
            tag.name != "meta"
            or tag.prefix not in [None, "opf"]
            or not (tag.get("content") and tag.get("name"))
        ):
            raise ValueError(f"{tag.name} is not OPF2 metadata item")

        return super().from_tag(tag, **kwargs)


@dataclass
class GenericMetadataItem(ValuedMetadataItem):
    """A generic metadata item"""

    dir: str | None = None
    lang: str | None = None
    refines: str | None = None
    scheme: str | None = None

    obj_to_tag: ClassVar[dict[str, str]] = {"name": "property", "lang": "xml:lang"}
    exclude_from_tag: ClassVar[list[str]] = ["tag", "value"]

    @property
    @override
    def tag_name(self):
        return "meta"

    @override
    def create_tag(self, soup: bs4.BeautifulSoup, **kwargs: str) -> bs4.Tag:
        tag = super().create_tag(soup, **kwargs)
        tag.string = self.value
        return tag

    @classmethod
    @override
    def from_tag(cls, tag: bs4.Tag, **kwargs: str) -> Self:
        if not tag.name == "meta" or not tag.get("property"):
            raise ValueError(f"{tag.name} is not generic metadata item")

        value = tag.string if tag.string is not None else ""
        return super().from_tag(tag, value=value, **kwargs)

    @override
    def update_tag(self, field: str, value: ValueType | None):
        if field == "value":
            if value is None:
                self.tag.string = ""
            else:
                self.tag.string = self.value_to_str(field, value)
        else:
            super().update_tag(field, value)


class BookMetadata(XMLParent[MetadataItem]):
    """The EPUB metadata, which contains information about the book."""

    default_item_type: type[MetadataItem] = MetadataItem
    tag_name: str | None = "metadata"

    @override
    def create_items(self) -> list[MetadataItem]:
        items: list[MetadataItem] = []
        for tag in self.tag.children:
            if isinstance(tag, bs4.Tag):
                try:
                    items.append(MetadataItem.detect(tag))
                except EPUBMetadataError:
                    warn(f"Couldn't parse metadata item {tag}")

        return items

    def add(self, name: str, value: str):
        item = GenericMetadataItem(name=name, value=value)
        __ = self.add_item(item)

        return item

    def add_dc(self, name: str, value: str):
        item = DublinCoreMetadataItem(name=name, value=value)
        __ = self.add_item(item)

        return item

    @property
    def identifier(self):
        item = self.get("identifier")
        if item and isinstance(item, DublinCoreMetadataItem):
            return item.value
        return None

    @identifier.setter
    def identifier(self, value: str):
        item = self.get("identifier")
        if item and isinstance(item, DublinCoreMetadataItem):
            item.value = value
            return

        item = DublinCoreMetadataItem(
            name="identifier",
            value=value,
        )
        __ = self.add_item(item)

    @property
    def title(self):
        item = self.get("title")
        if item and isinstance(item, DublinCoreMetadataItem):
            return item.value
        return None

    @title.setter
    def title(self, value: str):
        item = self.get("title")
        if item and isinstance(item, DublinCoreMetadataItem):
            item.value = value
            return

        item = DublinCoreMetadataItem(name="title", value=value)
        __ = self.add_item(item)

    @property
    def language(self):
        item = self.get("language")
        if item and isinstance(item, DublinCoreMetadataItem):
            return item.value
        return None

    @language.setter
    def language(self, value: str):
        item = self.get("language")
        if item and isinstance(item, DublinCoreMetadataItem):
            item.value = value
            return

        item = DublinCoreMetadataItem(name="language", value=value)
        __ = self.add_item(item)

    @property
    def modified(self) -> datetime | None:
        item = self.get("dcterms:modified")
        if item and isinstance(item, GenericMetadataItem):
            try:
                return datetime.fromisoformat(item.value)
            except ValueError:
                return None
        return None

    @modified.setter
    def modified(self, value: datetime):
        str_value = datetime_to_str(value)
        item = self.get("dcterms:modified")
        if item and isinstance(item, GenericMetadataItem):
            item.value = str_value
            return

        item = GenericMetadataItem(name="dcterms:modified", value=str_value)
        __ = self.add_item(item)
