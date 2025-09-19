from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from operator import attrgetter
from typing import ClassVar, Self, override

import bs4

from epublib.exceptions import EPUBError
from epublib.nav.util import PageBreakData, TOCEntryData
from epublib.reference import NavigationReference, NavigationRoot
from epublib.soup import NCXSoup
from epublib.util import attr_to_str, get_relative_href, parse_int
from epublib.xml_element import ValueType, XMLElement, XMLParent


@dataclass(kw_only=True)
class NCXMeta(XMLElement):
    """A metadata item in the NCX head section."""

    name: str
    content: str

    @property
    @override
    def tag_name(self):
        return "meta"

    @override
    @classmethod
    def from_tag(cls, tag: bs4.Tag, **kwargs: str) -> Self:
        return super().from_tag(tag=tag)


class NCXHead(XMLParent[NCXMeta]):
    """The head section of the NCX file."""

    def __init__(self, tag: bs4.Tag, filename: str) -> None:
        if not tag.name == "head":
            raise EPUBError("NCXHead tag must be a <head> element")

        self._resource_filename: str = filename
        super().__init__(tag)

    @override
    def create_items(self) -> list[NCXMeta]:
        items: list[NCXMeta] = []
        for tag in self.tag.select("meta"):
            item = NCXMeta.from_tag(tag)
            items.append(item)
        return items

    def add(self, name: str, content: str) -> NCXMeta:
        """Add a new meta item to the head section."""

        return self.add_item(NCXMeta(name=name, content=content))

    @property
    def uid(self) -> str:
        """The unique identifier of the publication."""
        try:
            meta = self["dtb:uid"]
        except KeyError as error:
            raise EPUBError("Expected 'dtb:uid' in NCX head") from error
        return meta.content

    @uid.setter
    def uid(self, value: str) -> None:
        meta = self.get("dtb:uid")
        if meta:
            meta.content = value
        else:
            __ = self.add(name="dtb:uid", content=value)

    @property
    def depth(self) -> int:
        """The depth of the navigation map strucutre."""
        try:
            meta = self["dtb:depth"]
        except KeyError as error:
            raise EPUBError("Expected 'dtb:depth' in NCX head") from error
        return int(meta.content)

    @depth.setter
    def depth(self, value: int) -> None:
        meta = self.get("dtb:depth")
        if meta:
            meta.content = str(value)
        else:
            __ = self.add(name="dtb:depth", content=str(value))

    @property
    def total_page_count(self) -> int | None:
        """
        Total page count of the publication. If there are no navigable
        pages (represented as 0), return None.
        """

        try:
            meta = self["dtb:totalPageCount"]
        except KeyError as error:
            raise EPUBError("Expected 'dtb:totalPageCount' in NCX head") from error
        int_val = int(meta.content)

        return None if int_val == 0 else int_val

    @total_page_count.setter
    def total_page_count(self, value: int | None) -> None:
        meta = self.get("dtb:totalPageCount")

        str_value = "0" if value is None else str(value)

        if meta:
            meta.content = str_value
        else:
            __ = self.add(name="dtb:totalPageCount", content=str_value)

    @property
    def max_page_number(self) -> int | None:
        """
        Largest value attribute on page targets in the page list. If
        there are no navigable pages (represented as 0), return None.
        """

        meta = self["dtb:maxPageNumber"]
        int_val = int(meta.content)

        return None if int_val == 0 else int_val

    @max_page_number.setter
    def max_page_number(self, value: int | None) -> None:
        meta = self.get("dtb:maxPageNumber")

        str_value = "0" if value is None else str(value)

        if meta:
            meta.content = str_value
        else:
            __ = self.add(name="dtb:maxPageNumber", content=str_value)


class NCXDocData(XMLElement, ABC):
    """
    Abstract base class for NCX docTitle or docAuthor elements.
    """

    id: str | None = None

    exclude_from_tag: ClassVar[list[str]] = ["tag", "name", "text"]

    @override
    @classmethod
    def from_tag(cls, tag: bs4.Tag, **kwargs: str) -> Self:
        text = tag.select_one("text")

        if not text:
            raise EPUBError("docAuthor tag must contain a <text> element")

        return super().from_tag(
            tag=tag,
            name=text.string or "",
        )

    @override
    def create_tag(self, soup: bs4.BeautifulSoup, **kwargs: str) -> bs4.Tag:
        tag = super().create_tag(soup, **kwargs)
        text = soup.new_tag("text")
        text.string = self.name
        __ = tag.append(text)

        return tag

    @override
    def update_tag(self, field: str, value: ValueType | None):
        if field == "name":
            text = self.tag.select_one("text")
            if text:
                text.string = str(value)
        else:
            super().update_tag(field, value)

    @property
    def text(self) -> str:
        return self.name

    @text.setter
    def text(self, value: str) -> None:
        self.name: str = value

    @abstractmethod
    def insert_self_in_soup(self, soup: NCXSoup):
        pass


class NCXAuthor(NCXDocData):
    """Authorship in the NCX file."""

    @property
    @override
    def tag_name(self):
        return "docAuthor"

    @override
    def insert_self_in_soup(self, soup: NCXSoup):
        previous_tag = soup.select("docAuthor, docTitle")[-1]
        __ = previous_tag.insert_after(self.tag)


class NCXTitle(NCXDocData):
    """Title in the NCX file."""

    @property
    @override
    def tag_name(self):
        return "docTitle"

    @override
    def insert_self_in_soup(self, soup: NCXSoup):
        previous_tag = soup.head
        __ = previous_tag.insert_after(self.tag)


class NCXNavPoint(NavigationReference["NCXNavPoint"]):
    """A navigation point in NCX table of contents."""

    tag_name: str = "navPoint"
    text_selector: str = "& > navLabel > text"
    text_tag_name: str = "text"
    href_selector: str = "& > content"
    href_tag_name: str = "content"
    href_attr: str = "src"

    @property
    def play_order(self) -> int | None:
        return parse_int(attr_to_str(self.tag.get("playOrder")))

    @play_order.setter
    def play_order(self, value: int | None) -> None:
        if value is None:
            if "playOrder" in self.tag.attrs:
                del self.tag.attrs["playOrder"]
        else:
            self.tag["playOrder"] = str(value)

    @override
    def _create_text(self, value: str) -> bs4.Tag:
        nav_label = self.soup.new_tag("navLabel")
        text_tag = self.soup.new_tag(self.text_tag_name)
        text_tag.string = value
        __ = self.tag.insert(0, nav_label)
        __ = nav_label.append(text_tag)

        return text_tag

    @override
    def _get_children_tags(self) -> list[bs4.Tag]:
        return self.tag.select("navPoint")

    @override
    def _insert_tag(self, position: int, tag: bs4.Tag):
        # Find the last navPoint at the same level
        siblings = self.tag.find_all("navPoint", recursive=False)
        if position >= len(siblings):
            __ = self.tag.append(tag)
        else:
            __ = siblings[position].insert_before(tag)


class NCXNavMap(  # type: ignore[reportUnsafeMultipleInheritance]
    NavigationRoot[NCXNavPoint, TOCEntryData, NCXSoup],
    NCXNavPoint,
):
    """The navigation map in the NCX file."""

    tag_name: str = "navMap"
    child_class: type[NCXNavPoint] = NCXNavPoint  # type: ignore[reportIncompatibleVariableOverride]

    @override
    def _insert_self_in_soup(self):
        ncx = self.soup.ncx
        if not ncx:
            raise EPUBError("Invalid NCX file: couldn't find 'ncx' tag")

        for tag_name in ["head", "docTitle", "docAuthor"]:
            other = ncx.select(tag_name)[-1]
            if other:
                __ = other.insert_after(self.tag)
                return

        __ = ncx.insert(0, self.tag)

    @override
    def reset(self, entries: Sequence[TOCEntryData]):
        new_tag = self._create_own_tag()
        __ = self.tag.replace_with(new_tag)
        self.tag: bs4.Tag = new_tag
        self._items: list[NCXNavPoint] = []

        for entry in entries:
            href = f"{get_relative_href(self.base_filename, entry.filename)}"
            if entry.id is not None:
                href += f"#{entry.id}"
            __ = self.add_item(text=entry.label, href=href)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self.items)} items)"


class NCXPageTarget(NCXNavPoint):
    """A page target in the NCX page list."""

    tag_name: str = "pageTarget"


class NCXPageList(  # type: ignore[reportUnsafeMultipleInheritance]
    NavigationRoot[NCXPageTarget, PageBreakData, NCXSoup],
    NCXPageTarget,
):
    tag_name: str = "pageList"
    child_class: type[NCXPageTarget] = NCXPageTarget  # type: ignore[reportIncompatibleVariableOverride]

    @override
    def _insert_self_in_soup(self):
        __ = self.soup.navMap.insert_after(self.tag)

    @override
    def reset(self, entries: Sequence[PageBreakData]):
        new_tag = self._create_own_tag()
        __ = self.tag.replace_with(new_tag)
        self.tag: bs4.Tag = new_tag
        self._items: list[NCXPageTarget] = []  # type: ignore[reportIncompatibleVariableOverride]

        for pagebreak in sorted(entries, key=attrgetter("page")):
            href = f"{get_relative_href(self.base_filename, pagebreak.filename)}#{pagebreak.id}"
            __ = self.add_item(text=pagebreak.label, href=href)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self.items)} items)"

    @property
    def largest_page_number(self) -> int | None:
        """The largest page number in the page list."""
        if not self.items:
            return None

        return max(parse_int(item.text) or 0 for item in self.items)


class NCXNavList(NCXNavMap):
    """A navigation list in the NCX file."""

    tag_name: str = "navList"

    @override
    def _insert_self_in_soup(self):
        ncx = self.soup.ncx
        if not ncx:
            raise EPUBError("Invalid NCX file: couldn't find 'ncx' tag")

        for tag_name in ["navMap", "pageList"]:
            other = ncx.select(tag_name)[-1]
            if other:
                __ = other.insert_after(self.tag)
                return

        __ = ncx.insert(0, self.tag)
