from pathlib import Path
from typing import IO, override
from zipfile import ZipInfo

from epublib.mediatype import MediaType
from epublib.nav import LandmarksRoot, PageListRoot, TocRoot
from epublib.nav.util import LandmarkEntryData, PageBreakData, TOCEntryData
from epublib.resources import ContentDocument
from epublib.util import get_relative_href


class NavigationDocument(ContentDocument):
    """
    A specialization of the XHTML content document that contains human- and
    machine-readable global navigation information.
    """

    def __init__(
        self,
        file: IO[bytes] | bytes,
        info: ZipInfo | str | Path,
        media_type: MediaType | str,
    ) -> None:
        super().__init__(file, info, media_type)
        self._toc: TocRoot | None = None
        self._page_list: PageListRoot | None = None
        self._landmarks: LandmarksRoot | None = None

    def add_to_toc(
        self,
        filename: str,
        title: str,
        position: int | None = None,
    ):
        href = get_relative_href(self.filename, filename)

        if self.toc is None:
            self._toc = TocRoot(self.soup, tag=None, base_filename=self.filename)

        assert self.toc is not None
        return self.toc.add_item(href=href, text=title, position=position)

    @property
    def toc(self):
        if self._toc is None:
            tag = self.soup.select_one('nav[epub|type="toc"]')
            if tag:
                self._toc = TocRoot(self.soup, tag, self.filename)
        return self._toc

    @property
    def page_list(self):
        if self._page_list is None:
            tag = self.soup.select_one('nav[epub|type="page-list"]')
            if tag:
                self._page_list = PageListRoot(self.soup, tag, self.filename)
        return self._page_list

    @property
    def landmarks(self):
        if self._landmarks is None:
            tag = self.soup.select_one('nav[epub|type="landmarks"]')
            if tag:
                self._landmarks = LandmarksRoot(self.soup, tag, self.filename)
        return self._landmarks

    def reset_page_list(self, pagebreaks: list[PageBreakData]):
        if self.page_list is None:
            self._page_list = PageListRoot(
                self.soup,
                tag=None,
                base_filename=self.filename,
            )

        assert self.page_list
        self.page_list.reset(pagebreaks)

    def reset_toc(self, entries: list[TOCEntryData]):
        if self.toc is None:
            self._toc = TocRoot(self.soup, tag=None, base_filename=self.filename)

        assert self.toc
        self.toc.reset(entries)

    def reset_landmarks(self, entries: list[LandmarkEntryData]):
        if self.landmarks is None:
            self._landmarks = LandmarksRoot(
                self.soup,
                tag=None,
                base_filename=self.filename,
            )

        assert self.landmarks
        self.landmarks.reset(entries)

    def remove(self, filename: str):
        if self.toc:
            self.toc.remove(filename)
        if self.landmarks:
            self.landmarks.remove(filename)
        if self.page_list:
            self.page_list.remove(filename)

    def on_soup_change(self):
        del self._toc
        del self._page_list
        del self._landmarks
        self._toc = None
        self._page_list = None
        self._landmarks = None

    @override
    def on_content_change(self):
        super().on_content_change()
        self.on_soup_change()
