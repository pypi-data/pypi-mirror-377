from datetime import datetime
from pathlib import Path
from typing import final

from epublib import EPUB
from epublib.package.metadata import GenericMetadataItem

from . import SAMPLES_DIR


@final
class TestEPUBMetadata:
    sample_filename = SAMPLES_DIR / "sample.epub"

    def test_metadata(self, epub: EPUB):
        assert epub.metadata
        assert epub.package_document.metadata
        assert repr(epub.metadata)

    def test_read(self, epub: EPUB):
        assert epub.metadata.identifier
        assert epub.metadata.title
        assert epub.metadata.modified
        assert epub.metadata.language

    def test_edit(self, epub: EPUB, epub_path: Path):
        date = datetime.now()
        epub.metadata.identifier = "987654321"
        epub.metadata.title = "Testing title"
        epub.metadata.modified = date
        epub.metadata.language = "ps-AR"
        __ = epub.metadata.add(name="test", value="test value")

        epub.write(epub_path)
        epub = EPUB(epub_path)

        assert epub.metadata.identifier == "987654321"
        assert epub.metadata.title == "Testing title"
        assert epub.metadata.modified
        assert epub.metadata.modified.astimezone() == date.astimezone().replace(
            microsecond=0
        )
        assert epub.metadata.language == "ps-AR"

        new_item = epub.metadata.get("test", GenericMetadataItem)
        assert new_item
        assert new_item.value == "test value"

    def test_edit_no_dups(self, epub: EPUB):
        epub.metadata.title = "Test title"
        assert len(epub.metadata.tag.find_all("dc:title")) == 1

        epub.metadata.identifier = "123456789"
        assert len(epub.metadata.tag.find_all("dc:identifier")) == 1

        epub.metadata.language = "es-ES"
        assert len(epub.metadata.tag.find_all("dc:language")) == 1

        epub.metadata.modified = datetime.now()
        print(epub.metadata.tag)
        assert (
            len(
                epub.metadata.tag.find_all(
                    "opf:meta",
                    attrs={"property": "dcterms:modified"},
                )
            )
            == 1
        )

    def test_edit_extra_attr(self, epub: EPUB, epub_path: Path):
        epub = EPUB(self.sample_filename)

        title = epub.metadata.get("title")
        assert title

        title.tag["data-testattr"] = "testval"

        epub.write(epub_path)
        epub = EPUB(epub_path)
        title = epub.metadata.get("title")

        assert title
        assert title.tag["data-testattr"] == "testval"
