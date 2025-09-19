from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import IO, override
from zipfile import ZipInfo

from epublib.exceptions import EPUBError
from epublib.mediatype import MediaType
from epublib.nav import NavItem
from epublib.nav.resource import NavigationDocument
from epublib.nav.util import PageBreakData, TOCEntryData
from epublib.ncx import (
    NCXAuthor,
    NCXHead,
    NCXNavList,
    NCXNavMap,
    NCXNavPoint,
    NCXPageList,
    NCXTitle,
)
from epublib.package.metadata import BookMetadata
from epublib.resources import PublicationResource, XMLResource
from epublib.soup import NCXSoup
from epublib.util import get_absolute_href, get_relative_href


class NCXFile(  # type: ignore[reportUnsafeMultipleInheritance]
    PublicationResource,
    XMLResource[NCXSoup],
):
    """
    The NCX document of the EPUB file, sometimes known as the 'toc.ncx' file.
    This is used in EPUB2 files for navigation, and was largely superseded by
    the package document in EPUB3. Support for it in EPUB3 is optional.
    """

    soup_class: type[NCXSoup] = NCXSoup

    def __init__(
        self,
        file: IO[bytes] | bytes,
        info: ZipInfo | str | Path,
        media_type: MediaType | str = MediaType.NCX,
    ) -> None:
        super().__init__(file, info, media_type)
        self._head: NCXHead | None = None
        self._title: NCXTitle | None = None
        self._authors: Sequence[NCXAuthor] | None = None
        self._nav_map: NCXNavMap | None = None
        self._page_list: NCXPageList | None = None
        self._nav_lists: Sequence[NCXNavList] | None = None

    @property
    def head(self) -> NCXHead:
        if self._head is None:
            self._head = NCXHead(self.soup.head, self.filename)
        return self._head

    @property
    def title(self) -> NCXTitle:
        if self._title is None:
            self._title = NCXTitle.from_tag(self.soup.docTitle)
        return self._title

    @property
    def authors(self) -> Sequence[NCXAuthor]:
        if self._authors is None:
            self._authors = tuple(
                NCXAuthor.from_tag(tag) for tag in self.soup.select("docAuthor")
            )

        return self._authors

    @property
    def nav_map(self) -> NCXNavMap:
        if self._nav_map is None:
            self._nav_map = NCXNavMap(self.soup, self.soup.navMap, self.filename)
        return self._nav_map

    @property
    def page_list(self) -> NCXPageList | None:
        if self._page_list is None:
            tag = self.soup.select_one("pageList")
            if tag:
                self._page_list = NCXPageList(self.soup, tag, self.filename)
        return self._page_list

    @property
    def nav_lists(self) -> Sequence[NCXNavList]:
        if self._nav_lists is None:
            self._nav_lists = tuple(
                NCXNavList(self.soup, tag, self.filename)
                for tag in self.soup.select("navList")
            )

        return self._nav_lists

    def add_to_nav_map(
        self,
        filename: str,
        title: str,
        position: int | None = None,
    ):
        href = get_relative_href(self.filename, filename)
        return self.nav_map.add_item(href=href, text=title, position=position)

    def remove(self, filename: str):
        # Todo: remove references to images and audio as well
        self.nav_map.remove(filename)
        if self.page_list:
            self.page_list.remove(filename)
        for nav_list in self.nav_lists:
            nav_list.remove(filename)

    def add_author(self, name: str) -> NCXAuthor:
        author = NCXAuthor(name=name)
        author.insert_self_in_soup(self.soup)

        return author

    def add_nav_list(self, items: Iterable[TOCEntryData]) -> NCXNavList:
        nav_list = NCXNavList(
            self.soup,
            tag=None,
            base_filename=self.filename,
        )

        for entry in items:
            href = get_relative_href(self.filename, entry.filename) + (
                f"#{entry.id}" if entry.id is not None else ""
            )
            __ = nav_list.add_item(href=href, text=entry.label)

        return nav_list

    def reset_nav_map(self, entries: list[TOCEntryData]):
        self.nav_map.reset(entries)

    def reset_page_list(self, entries: list[PageBreakData]):
        if not self.page_list:
            self._page_list = NCXPageList(
                self.soup,
                tag=None,
                base_filename=self.filename,
            )

        assert self.page_list
        self.page_list.reset(entries)

    def update_total_page_count(self):
        if not self.page_list:
            raise EPUBError("No page list to update total page count from")

        self.head.total_page_count = (
            len(self.page_list.items) if self.page_list else None
        )

    def update_depth(self):
        self.head.depth = self.nav_map.max_depth

    def update_max_page_number(self):
        if not self.page_list:
            raise EPUBError("No page list to update max page number from from")
        self.head.max_page_number = (
            self.page_list.largest_page_number if self.page_list else None
        )

    def _update_play_order_recursive(
        self,
        nav_point: NCXNavPoint,
        start: int,
    ) -> int:
        for item in nav_point.items:
            item.play_order = start
            start = self._update_play_order_recursive(item, start + 1)

        return start + 1

    def update_play_order(self) -> None:
        __ = self._update_play_order_recursive(self.nav_map, 1)

    def update_numbers(self):
        """
        Update required numbers in the head and nav map of the NCX file:
        - max depth;
        - max page number (if there is a page list);
        - total page count (if there is a page list);
        - play order.
        """

        self.update_depth()
        self.update_play_order()

        if self.page_list:
            self.update_max_page_number()
            self.update_total_page_count()

    def sync_head(self, metadata: BookMetadata):
        """
        Sync metadata from the package document metadata to the NCX
        document, erasing any existing head > meta items. Should be used
        after populating the navMap and pageList (if there is one), to
        get an accurate page and depth count.
        """
        head = NCXHead(self.soup.new_tag("head"), self.filename)

        if metadata.identifier:
            head.uid = metadata.identifier

        self.head.depth = 0
        head.total_page_count = None
        head.max_page_number = None

        __ = self.soup.head.replace_with(head.tag)
        self._head = head
        self.update_numbers()

        return head

    def sync_toc(self, nav: NavigationDocument):
        """
        Sync the NCX navMap to match the given TOC structure, erasing
        any existing navMap items. Should be used after populating.
        """
        if not nav.toc:
            raise EPUBError("No TOC in navigation document to sync from")

        original_filename = nav.filename

        nav_map = NCXNavMap(self.soup, tag=None, base_filename=self.filename)

        count = 1 << 16

        def recurse_items(
            nav_point: NCXNavPoint,
            toc_item: NavItem,
        ):
            nonlocal count
            count -= 1

            if count <= 0:
                raise EPUBError("Infinite recursion detected in TOC structure")

            for sub_toc_item in toc_item.items:
                absolute_filename = get_absolute_href(
                    original_filename,
                    sub_toc_item.href,
                )
                relative_filename = get_relative_href(
                    self.filename,
                    absolute_filename,
                )
                sub_nav_point = nav_point.add_item(sub_toc_item.text, relative_filename)
                recurse_items(sub_nav_point, sub_toc_item)

        recurse_items(nav_map, nav.toc)

        __ = self.soup.navMap.replace_with(nav_map.tag)
        self._nav_map = nav_map

        return nav_map

    def sync_page_list(self, nav: NavigationDocument):
        if not nav.page_list:
            raise EPUBError("No page list in navigation document to sync from")
        original_filename = nav.filename

        self.reset_page_list([])
        assert self.page_list

        for item in nav.page_list.items:
            absolute_filename = get_absolute_href(
                original_filename,
                item.href,
            )
            relative_filename = get_relative_href(
                self.filename,
                absolute_filename,
            )

            __ = self.page_list.add_item(item.text, relative_filename)

    def on_soup_change(self):
        del self._head
        del self._title
        del self._authors
        del self._nav_map
        del self._page_list
        del self._nav_lists
        self._head = None
        self._title = None
        self._authors = None
        self._nav_map = None
        self._page_list = None
        self._nav_lists = None

    @override
    def on_content_change(self):
        super().on_content_change()
        self.on_soup_change()
