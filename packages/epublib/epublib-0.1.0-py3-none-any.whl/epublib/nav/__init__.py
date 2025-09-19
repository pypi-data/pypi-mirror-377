from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from operator import attrgetter
from typing import Literal, override

import bs4

from epublib.nav.util import LandmarkEntryData, PageBreakData, TOCEntryData, epub_type
from epublib.reference import NavigationReference, NavigationRoot
from epublib.util import (
    get_actual_tag_position,
    get_relative_href,
)


class NavItem(NavigationReference["NavItem"]):
    """
    A navigation item in the navigation document. The text tag and the
    href tag are the same.

    Example of tag:

    .. code-block:: html

        <li>
          <a href="chapter1.xhtml">Chapter 1</a>
          <ol>[...children]</ol>
        </li>
    """

    tag_name: str = "li"
    text_selector: str = "& > span, a"
    text_tag_name: str = "span"
    href_selector: str = "& > a"
    href_tag_name: str = "a"
    href_attr: str = "href"

    @property
    @override
    def items(self) -> Sequence[NavItem]:
        return tuple(self._items)

    @override
    def _get_children_tags(self) -> list[bs4.Tag]:
        parent_tag = self.tag.ol
        if not parent_tag:
            return []

        return parent_tag.select("li")

    @override
    def _insert_tag(self, position: int, tag: bs4.Tag):
        ol = self.tag.ol

        if not ol:
            ol = self.soup.new_tag("ol")
            __ = self.tag.append(ol)

        __ = ol.insert(get_actual_tag_position(ol, position), tag)

    @override
    def _create_href(self, value: str) -> bs4.Tag | None:
        text_tag = self._get_text_tag()

        if text_tag is None:
            text_tag = self._create_text("")

        text_tag.name = "a"
        text_tag[self.href_attr] = value

        return text_tag

    @override
    def _get_href_tag(self) -> bs4.Tag | None:
        return super()._get_text_tag()  # href tag is the same as text tag

    @override
    def _set_href_tag(self, value: str) -> None:
        super()._set_href_tag(value)
        text_tag = self._get_text_tag()
        if text_tag:
            text_tag.name = "a"


class NavRoot[D](  # type: ignore[reportUnsafeMultipleInheritance]
    NavigationRoot[NavItem, D],
    NavItem,
    ABC,
):
    text_selector: str = "& > h1, & > h2, & > h3, & > h4, & > h5, & > h6"
    new_attrs: dict[str, str] = {}
    child_class: type[NavItem] = NavItem  # type: ignore[reportIncompatibleVariableOverride]

    @override
    def _create_own_tag(self):
        tag = self.soup.new_tag("nav", attrs=self.new_attrs.copy())
        __ = tag.append(self.soup.new_tag("ol"))

        return tag

    @override
    def _insert_self_in_soup(self):
        if self.soup.body:
            __ = self.soup.body.insert(0, self.tag)

        __ = self.soup.insert(0, self.tag)

    def _find_heading_level(self) -> Literal["h1", "h2", "h3", "h4", "h5", "h6"]:
        if self.soup.find("h1"):
            return "h2"
        return "h1"

    @override
    def _create_text(self, value: str) -> bs4.Tag:
        htag = self.soup.new_tag(self._find_heading_level())
        htag.string = value
        __ = self.tag.insert(0, htag)

        return htag


class TocRoot(NavRoot[TOCEntryData]):
    new_attrs: dict[str, str] = {
        epub_type: "toc",
        "role": "doc-toc",
        "id": "toc",
    }

    @override
    def _insert_self_in_soup(self):
        assert not self.soup.select_one('nav[epub|type="toc"]'), "toc already existent!"

        landmarks = self.soup.select_one('nav[epub|type="landmarks"]')
        if landmarks:
            __ = landmarks.insert_before(self.tag)
            return

        page_list = self.soup.select_one('nav[epub|type="page-list"]')
        if page_list:
            __ = page_list.insert_before(self.tag)
            return

        super()._insert_self_in_soup()

    @override
    def reset(self, entries: Sequence[TOCEntryData]):
        new_tag = self._create_own_tag()
        __ = self.tag.replace_with(new_tag)
        self.tag: bs4.Tag = new_tag
        self._items: list[NavItem] = []

        for entry in entries:
            href = f"{get_relative_href(self.base_filename, entry.filename)}"
            if entry.id is not None:
                href += f"#{entry.id}"
            __ = self.add_item(text=entry.label, href=href)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self.items)} items)"


class PageListRoot(NavRoot[PageBreakData]):
    new_attrs: dict[str, str] = {
        epub_type: "page-list",
        "id": "page-list",
        "hidden": "",
    }

    @override
    def _insert_self_in_soup(self):
        assert not self.soup.select_one('nav[epub|type="page-list"]'), (
            "page list already existent!"
        )

        toc = self.soup.select_one('nav[epub|type="toc"]')
        if toc:
            __ = toc.insert_after(self.tag)
            return

        landmarks = self.soup.select_one('nav[epub|type="toc"]')
        if landmarks:
            __ = landmarks.insert_before(self.tag)
            return

        super()._insert_self_in_soup()

    @override
    def reset(self, entries: Sequence[PageBreakData]):
        new_tag = self._create_own_tag()
        __ = self.tag.replace_with(new_tag)
        self.tag: bs4.Tag = new_tag
        self._items: list[NavItem] = []

        for pagebreak in sorted(entries, key=attrgetter("page")):
            href = f"{get_relative_href(self.base_filename, pagebreak.filename)}#{pagebreak.id}"
            __ = self.add_item(text=pagebreak.label, href=href)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self.items)} items)"


class LandmarksRoot(NavRoot[LandmarkEntryData]):
    new_attrs: dict[str, str] = {
        epub_type: "landmarks",
        "id": "landmarks",
        "hidden": "",
    }

    @override
    def _insert_self_in_soup(self):
        assert not self.soup.select_one('nav[epub|type="landmarks"]'), (
            "landmarks already existent!"
        )

        page_list = self.soup.select_one('nav[epub|type="page-list"]')
        if page_list:
            __ = page_list.insert_after(self.tag)
            return

        toc = self.soup.select_one('nav[epub|type="toc"]')
        if toc:
            __ = toc.insert_after(self.tag)
            return

        super()._insert_self_in_soup()

    @override
    def reset(self, entries: Sequence[LandmarkEntryData]):
        new_tag = self._create_own_tag()
        __ = self.tag.replace_with(new_tag)
        self.tag: bs4.Tag = new_tag
        self._items: list[NavItem] = []

        for entry in entries:
            href = f"{get_relative_href(self.base_filename, entry.filename)}"

            if entry.id is not None:
                href += f"#{entry.id}"

            item = self.add_item(text=entry.label, href=href)
            if entry.epub_type:
                item.tag.attrs[epub_type] = entry.epub_type

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self.items)} items)"
