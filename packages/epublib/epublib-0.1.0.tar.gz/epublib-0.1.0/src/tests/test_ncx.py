import re
from pathlib import Path
from typing import final

import pytest
from bs4 import Tag
from bs4.element import NamespacedAttribute

from epublib import EPUB
from epublib.exceptions import EPUBError
from epublib.nav.util import TOCEntryData
from epublib.resources import ContentDocument
from epublib.util import attr_to_str, strip_fragment


@final
class TestEPUBNCX:
    def test_ncx(self, epub: EPUB, epub_path: Path):
        assert epub.ncx
        assert epub.ncx.head
        assert epub.ncx.title
        assert epub.ncx.nav_map
        assert repr(epub.ncx)

        epub.ncx.title.name = "New title"
        epub.write(epub_path)
        epub = EPUB(epub_path)

        assert epub.ncx
        assert epub.ncx.title.name == "New title"

    def test_metadata(self, epub: EPUB, epub_path: Path):
        assert epub.ncx
        assert epub.ncx.head
        __ = epub.ncx.head.uid
        __ = epub.ncx.head.depth
        __ = epub.ncx.head.total_page_count
        __ = epub.ncx.head.max_page_number

        epub.ncx.head.uid = "new-uid"
        epub.ncx.head.depth = 2
        epub.ncx.head.total_page_count = 100
        epub.ncx.head.max_page_number = 50
        new_item = epub.ncx.head.add(name="custom-meta", content="custom value")

        epub.write(epub_path)
        epub = EPUB(epub_path)
        assert epub.ncx

        assert epub.ncx.head.uid == "new-uid"
        assert epub.ncx.head.depth == 2
        assert epub.ncx.head.total_page_count == 100
        assert epub.ncx.head.max_page_number == 50
        assert epub.ncx.head["custom-meta"] == new_item

    def test_nav_map(self, epub: EPUB, tmp_path: Path):
        assert epub.ncx

        nav_map = epub.ncx.nav_map
        assert nav_map
        assert nav_map.items

        for item in nav_map.items:
            assert item
            assert item.text
            assert item.href

        item = nav_map.items[0]
        nav_map.text = "Spec allows nav map with text"

        item.href = "testhref"
        item.text = "test text"

        __ = nav_map.add_item("New item", "newitemhref", 1)

        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)
        epub = EPUB(outfn)

        assert epub.ncx
        nav_map = epub.ncx.nav_map
        assert nav_map
        assert nav_map.text == "Spec allows nav map with text"
        assert nav_map.items[0].href == "testhref"
        assert nav_map.items[0].text == "test text"

        assert all(
            item.tag.find("text") and item.tag.find("content") for item in nav_map.items
        )

    def test_generate_ncx(self, epub: EPUB, epub_path: Path):
        with pytest.raises(EPUBError):
            __ = epub.generate_ncx()

        assert epub.ncx
        epub.resources.remove(epub.ncx)

        new_ncx = epub.generate_ncx()
        assert not epub.ncx.soup.select("docTitle[text], docAuthor[text]")

        assert epub.ncx
        assert epub.ncx is new_ncx
        assert epub.ncx.nav_map.items
        assert epub.ncx.head
        assert epub.ncx.title
        assert epub.ncx.nav_map
        assert repr(epub.ncx)

        epub.ncx.title.name = "New title"
        epub.write(epub_path)

        with EPUB(epub_path) as epub:
            assert epub.ncx
            assert epub.ncx.title.name == "New title"

            __ = epub.ncx.head.uid
            __ = epub.ncx.head.depth
            __ = epub.ncx.head.total_page_count
            __ = epub.ncx.head.max_page_number

            epub.ncx.head.uid = "new-uid"
            epub.ncx.head.depth = 2
            epub.ncx.head.total_page_count = 100
            epub.ncx.head.max_page_number = 50
            new_item = epub.ncx.head.add(name="custom-meta", content="custom value")
            assert new_item

            nav_map = epub.ncx.nav_map
            assert nav_map
            assert nav_map.items

            for item in nav_map.items:
                assert item
                assert item.text
                assert item.href

            item = nav_map.items[0]
            assert item

    def test_reset_ncx(self, epub: EPUB):
        epub.metadata.title = "Test reset NCX"
        epub.metadata.language = "es-ES"
        __ = epub.reset_ncx()

        assert epub.ncx
        assert epub.ncx.title.text == "Test reset NCX"
        lang_tag = epub.ncx.soup.find("ncx", attrs={"xml:lang": True})
        assert isinstance(lang_tag, Tag)
        assert lang_tag["xml:lang"] == "es-ES"

    def test_reset_ncx_from_non_existant(self, epub: EPUB):
        assert epub.ncx
        epub.resources.remove(epub.ncx)
        assert not epub.ncx

        epub.metadata.title = "Test reset NCX"
        __ = epub.reset_ncx()

        assert epub.ncx
        assert epub.ncx.title.text == "Test reset NCX"

    def test_nav_map_add_after(self, epub: EPUB):
        assert epub.ncx
        assert epub.ncx.nav_map

        item = epub.ncx.nav_map.items[0]
        __ = item.add_after("Uau", "example.com")
        assert epub.ncx.nav_map.tag.select('content[src="example.com"]')

    def test_page_list(self, epub: EPUB):
        assert epub.ncx

        if epub.ncx.soup.select("pageList"):
            assert epub.ncx.page_list

    def test_nav_lists(self, epub: EPUB):
        assert epub.ncx

        if epub.ncx.soup.select("navList"):
            assert epub.ncx.nav_lists
            for nav_list in epub.ncx.nav_lists:
                assert nav_list.items

    def test_create_nav_map(self, epub: EPUB):
        assert epub.ncx
        if epub.ncx.nav_map:
            epub.ncx.nav_map.tag.decompose()
            epub.ncx.on_soup_change()

        if epub.nav and epub.nav.toc:
            epub.nav.toc.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_toc()
        assert epub.ncx.nav_map
        old_len = len(epub.ncx.nav_map.items)

        epub.reset_toc()
        assert epub.ncx.nav_map
        assert epub.ncx.nav_map.items
        assert len(epub.ncx.nav_map.items) == old_len
        assert epub.ncx.nav_map.tag.name == "navMap"
        assert epub.ncx.nav_map.tag.select("content[src]")

        epub.reset_toc(targets_selector="h1")
        assert epub.ncx.nav_map
        assert epub.ncx.nav_map.items
        tag = epub.ncx.nav_map.tag.select_one("content[src]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("src")))

        epub.reset_toc(targets_selector="h1", spine_only=True)
        assert epub.ncx.nav_map
        assert epub.ncx.nav_map.items
        tag = epub.ncx.nav_map.tag.select_one("content[src]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("src")))

    def test_create_nav_map_error(self, epub: EPUB):
        if epub.ncx:
            epub.resources.remove(epub.ncx)

        with pytest.raises(EPUBError):
            epub.create_toc(reset_ncx=True)

        with pytest.raises(EPUBError):
            epub.reset_toc(reset_ncx=True)

    def test_reset_page_list(self, epub: EPUB):
        assert epub.ncx
        assert epub.nav

        if epub.ncx.page_list:
            epub.ncx.page_list.tag.decompose()
            epub.ncx.on_soup_change()

        if epub.nav.page_list:
            epub.nav.page_list.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_page_list()
        assert epub.ncx.page_list
        old_len = len(epub.ncx.page_list.items)

        epub.reset_page_list()
        assert epub.ncx.page_list
        assert epub.ncx.page_list.items
        assert len(epub.ncx.page_list.items) == old_len
        assert epub.ncx.page_list.tag.name == "pageList"
        assert epub.ncx.page_list.tag.select("content[src]")

        __, existing_tag = epub.resources.resolve_href(
            epub.ncx.page_list.items[0].href or "",
            relative_to=epub.ncx.filename,
        )

        assert existing_tag
        existing_id = attr_to_str(existing_tag["id"])

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
        assert len(epub.ncx.page_list.items) == old_len + 1
        ids = [
            re.sub(r".*#(\w)$", "$1", item.href or "")
            for item in epub.ncx.page_list.items
        ]
        assert len(ids) == len(set(ids))

        with pytest.raises(EPUBError):
            epub.create_page_list()

    def test_reset_page_list_error(self, epub: EPUB):
        if epub.ncx:
            epub.resources.remove(epub.ncx)

        with pytest.raises(EPUBError):
            epub.create_page_list(reset_ncx=True)

        with pytest.raises(EPUBError):
            epub.reset_page_list(reset_ncx=True)

    def test_create_nav_list(self, epub: EPUB, epub_path: Path):
        assert epub.ncx

        nav_list = epub.ncx.add_nav_list(
            TOCEntryData(
                doc.filename,
                label=f"Document {index}",
                id=f"i-{index}",
            )
            for index, doc in enumerate(epub.documents(), start=1)
        )
        nav_list.text = "Nav list title"

        epub.write(epub_path)
        epub = EPUB(epub_path)
        assert epub.ncx
        assert epub.ncx.nav_lists
        nav_list = next(nl for nl in epub.ncx.nav_lists if nl.text == "Nav list title")

        assert all(nav_list.items_referencing(doc.filename) for doc in epub.documents())

    def test_add_resource(self, epub: EPUB):
        doc = ContentDocument(b"<h1>Uau!</h1>", "added-document.xhtml")
        assert epub.ncx

        epub.resources.add(doc)
        assert next(epub.ncx.nav_map.items_referencing(doc.filename))

    def test_add_resource_no_ncx(self, epub: EPUB):
        doc = ContentDocument(b"content", "added-document.xhtml")

        epub.resources.add(doc, add_to_ncx=False)
        assert epub.ncx
        assert not next(
            epub.ncx.nav_map.items_referencing(doc.filename),
            None,
        )

    def test_add_resource_no_toc(self, epub: EPUB):
        doc = ContentDocument(b"content", "added-document.xhtml")

        epub.resources.add(doc, add_to_toc=False)
        assert epub.ncx
        assert not next(
            epub.ncx.nav_map.items_referencing(doc.filename),
            None,
        )

    def test_add_resource_error(self, epub: EPUB):
        doc = ContentDocument(b"content", "added-document.xhtml")

        assert epub.ncx
        epub.resources.remove(epub.ncx)

        with pytest.raises(EPUBError):
            epub.resources.add(doc, add_to_ncx=True)

    def test_remove_resource(self, epub: EPUB):
        assert epub.nav
        assert epub.nav.toc
        doc = epub.resources.resolve_href(
            epub.nav.toc.items[0].href,
            False,
            relative_to=epub.nav,
        )
        assert doc

        assert epub.ncx
        assert next(epub.ncx.nav_map.items_referencing(doc.filename))

        epub.resources.remove(doc)

        assert not next(
            epub.ncx.nav_map.items_referencing(doc.filename),
            None,
        )

    def test_rename_resource(self, epub: EPUB):
        assert epub.ncx
        resource = epub.resources.resolve_href(
            epub.ncx.nav_map.items[0].href,
            False,
            relative_to=epub.ncx,
        )
        assert resource

        epub.resources.rename(resource, "renamed-document.xhtml")

        assert (
            Path(strip_fragment(epub.ncx.nav_map.items[0].href)).name
            == "renamed-document.xhtml"
        )

    def test_play_order(self, epub: EPUB):
        assert epub.ncx
        epub.reset_toc()
        __ = epub.reset_ncx()

        assert epub.ncx.nav_map.items[0].play_order == 1
        assert epub.ncx.nav_map.items[1].play_order
        assert epub.ncx.nav_map.items[1].play_order > 1
