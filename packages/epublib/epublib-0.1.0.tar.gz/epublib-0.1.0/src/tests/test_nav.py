import re
from pathlib import Path
from typing import final

import pytest
from bs4.element import NamespacedAttribute

from epublib import EPUB
from epublib.exceptions import EPUBError
from epublib.resources import ContentDocument


@final
class TestEPUBNav:
    def test_nav(self, epub: EPUB):
        assert epub.nav
        assert epub.manifest.nav
        assert repr(epub.nav)

    def test_toc(self, tmp_path: Path, epub: EPUB):
        assert epub.nav

        toc = epub.nav.toc
        assert toc
        assert toc.text
        assert toc.items
        assert toc.tag.get("epub:type") == "toc"
        for item in toc.items:
            assert item
            assert item.text
            assert item.href

        item = toc.items[0]
        toc.text = "testtoctitle"
        item.href = "testhref"
        item.text = "test text"

        item = toc.add_item("New item", "newitemhref", 1)
        assert item.tag.select("& > a")

        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)
        epub = EPUB(outfn)

        assert epub.nav
        toc = epub.nav.toc
        assert toc
        assert toc.text == "testtoctitle"
        assert toc.items[0].href == "testhref"

        assert all(not (item.tag.a and item.tag.span) for item in toc.items)

    def test_toc_add_after(self, epub: EPUB):
        assert epub.nav
        assert epub.nav.toc

        item = epub.nav.toc.items[0]
        __ = item.add_after("Uau", "example.com")
        assert epub.nav.toc.tag.select('[href="example.com"]')

    def test_page_list(self, epub: EPUB):
        assert epub.nav

        if epub.nav.soup.select("[epub|type='page-list']"):
            pl = epub.nav.toc
            assert pl

    def test_landmarks(self, epub: EPUB):
        assert epub.nav

        if epub.nav.soup.select("[epub|type='landmarks']"):
            pl = epub.nav.toc
            assert pl
            assert pl.items
            assert pl.items[0].href

    def test_reset_page_list(self, epub: EPUB):
        assert epub.nav
        if epub.nav.page_list:
            epub.nav.page_list.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_page_list()
        assert epub.nav.page_list
        old_len = len(epub.nav.page_list.items)

        epub.reset_page_list()
        assert epub.nav.page_list
        assert epub.nav.page_list.items
        assert len(epub.nav.page_list.items) == old_len
        assert epub.nav.page_list.tag.get("epub:type") == "page-list"
        assert epub.nav.page_list.tag.select("[href]")

        _, existing = epub.resources.resolve_href(
            epub.nav.page_list.items[0].href or "",
            relative_to=epub.nav.filename,
        )
        assert existing
        existing_id = str(existing["id"])

        res = next(epub.resources.filter(ContentDocument))
        new_tag = res.soup.new_tag(
            "p",
            string="3",
            attrs={
                NamespacedAttribute(
                    "epub",
                    "type",
                    "http://www.idpf.org/2007/ops",
                ): "pagebreak",
                "id": existing_id,
            },
        )
        assert res.soup.body
        assert res.soup.body.append(new_tag)

        epub.reset_page_list()
        assert len(epub.nav.page_list.items) == old_len + 1
        ids = [
            re.sub(r".*#(\w)$", "$1", item.href or "")
            for item in epub.nav.page_list.items
        ]
        assert len(ids) == len(set(ids))

        with pytest.raises(EPUBError):
            epub.create_page_list()

    def test_reset_page_list_error(self, epub: EPUB):
        if epub.nav:
            epub.resources.remove(epub.nav)

        with pytest.raises(EPUBError):
            epub.create_page_list()

        with pytest.raises(EPUBError):
            epub.reset_page_list()

    def test_create_toc(self, epub: EPUB):
        assert epub.nav
        if epub.nav.toc:
            epub.nav.toc.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_toc()
        assert epub.nav.toc
        old_len = len(epub.nav.toc.items)

        epub.reset_toc()
        assert epub.nav.toc
        assert epub.nav.toc.items
        assert len(epub.nav.toc.items) == old_len
        assert epub.nav.toc.tag.get("epub:type") == "toc"
        assert epub.nav.toc.tag.select("[href]")

        epub.reset_toc(targets_selector="h1")
        assert epub.nav.toc
        assert epub.nav.toc.items
        assert epub.nav.toc.tag.get("epub:type") == "toc"
        tag = epub.nav.toc.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))

        epub.reset_toc(targets_selector="h1", spine_only=True)
        assert epub.nav.toc
        assert epub.nav.toc.items
        assert epub.nav.toc.tag.get("epub:type") == "toc"
        tag = epub.nav.toc.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))

    def test_create_toc_error(self, epub: EPUB):
        with pytest.raises(EPUBError):
            epub.create_toc()

        if epub.nav:
            epub.resources.remove(epub.nav)

        with pytest.raises(EPUBError):
            epub.create_toc()

        with pytest.raises(EPUBError):
            epub.reset_toc()

    def test_create_landmarks(self, epub: EPUB):
        assert epub.nav
        if epub.nav.landmarks:
            epub.nav.landmarks.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_landmarks()
        assert epub.nav.landmarks
        old_len = len(epub.nav.landmarks.items)

        epub.reset_landmarks()
        assert epub.nav.landmarks
        assert epub.nav.landmarks.items
        assert len(epub.nav.landmarks.items) == old_len
        assert epub.nav.landmarks.tag.get("epub:type") == "landmarks"
        assert epub.nav.landmarks.tag.select("[href]")

        assert epub.nav.toc
        del epub.nav.toc.tag["id"]

        epub.reset_landmarks(targets_selector="h1")
        assert epub.nav.landmarks
        assert epub.nav.landmarks.items
        assert epub.nav.landmarks.tag.get("epub:type") == "landmarks"
        tag = epub.nav.landmarks.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))

        epub.reset_landmarks(targets_selector="h1")
        assert epub.nav.landmarks
        assert epub.nav.landmarks.items
        assert epub.nav.landmarks.tag.get("epub:type") == "landmarks"
        tag = epub.nav.landmarks.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))
        titles = [item.text for item in epub.nav.landmarks.items]
        assert len(set(titles)) == len(titles)

    def test_create_landmarks_error(self, epub: EPUB):
        with pytest.raises(EPUBError):
            epub.create_landmarks()

        if epub.nav:
            epub.resources.remove(epub.nav)

        with pytest.raises(EPUBError):
            epub.create_landmarks()

        with pytest.raises(EPUBError):
            epub.reset_landmarks()

    def test_items_referencing(self, epub: EPUB):
        epub.reset_toc(include_filenames=True)
        assert epub.nav
        assert epub.nav.toc

        assert list(epub.nav.toc.items_referencing("nonexisting")) == []
        assert all(
            list(epub.nav.toc.items_referencing(doc.filename))
            for doc in epub.documents()
        )

        epub.reset_toc(targets_selector="never")
        assert len(epub.nav.toc.items) == 0

        __ = epub.nav.toc.add_item("Self referential link", "#some-id")
        assert list(epub.nav.toc.items_referencing(epub.nav.filename))

        assert list(
            epub.nav.toc.items_referencing(
                f"{epub.nav.filename}#some-id",
                ignore_fragment=False,
            )
        )
        assert not list(
            epub.nav.toc.items_referencing(
                f"{epub.nav.filename}#some-other",
                ignore_fragment=False,
            )
        )
