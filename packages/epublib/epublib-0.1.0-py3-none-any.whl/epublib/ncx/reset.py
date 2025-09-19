from pathlib import Path

from bs4.element import NamespacedAttribute

from epublib.exceptions import EPUBError
from epublib.ncx.resource import NCXFile
from epublib.package.metadata import ValuedMetadataItem
from epublib.types import BookProtocol

ncx_template = """<?xml version="1.0" encoding="UTF-8"?>
<ncx version="2005-1" {lang_attr} xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head></head>
<docTitle><text>{title}</text></docTitle>
<navMap></navMap>
</ncx
"""


def get_minimal_ncx_content(title: str, lang: str | None) -> bytes:
    """
    Get a minimal NCX file content with the given title and language.
    Caution: the minimality of this template is in regard to the parsing
    available in this library. To get a minimal valid NCX file, consider
    using `EPUB.generate_ncx` instead.
    """
    if lang:
        lang_attr = f'xml:lang="{lang}"'
    else:
        lang_attr = ""
    return ncx_template.format(title=title, lang_attr=lang_attr).encode()


def generate_ncx(book: BookProtocol, filename: str | Path | None = None) -> NCXFile:
    if filename is None:
        filename = book.base_dir / "toc.ncx"

    if not book.metadata.title:
        raise EPUBError("Can't generate NCX without book title in metadata")

    if not (book.nav and book.nav.toc):
        raise EPUBError("Can't generate NCX without Navigation Document with TOC")

    if book.ncx is not None:
        raise EPUBError(
            "Can't generate NCX as it already exists. Try "
            f"{book.__class__.__name__}.reset_ncx() instead"
        )

    ncx = NCXFile(
        get_minimal_ncx_content(
            book.metadata.title,
            book.metadata.language,
        ),
        filename,
    )

    ncx = reset_ncx(book, ncx)
    book.resources.add(ncx)
    book.spine.tag["toc"] = book.manifest[ncx.filename].id
    return ncx


def reset_ncx(book: BookProtocol, ncx: NCXFile | None = None) -> NCXFile:
    if not book.metadata.title:
        raise EPUBError("Can't reset NCX without book title in metadata")

    if not (book.nav and book.nav.toc):
        raise EPUBError("Can't reset NCX without Navigation Document with TOC")

    if ncx is None:
        ncx = book.ncx

    if ncx is None:
        return generate_ncx(book)

    ncx.title.text = book.metadata.title
    creator = book.metadata.get("creator")
    if isinstance(creator, ValuedMetadataItem):
        __ = ncx.add_author(creator.value)

    if book.metadata.language:
        ncx.soup.ncx[NamespacedAttribute("xml", "lang")] = book.metadata.language

    __ = ncx.sync_toc(book.nav)
    if book.nav.page_list:
        __ = ncx.sync_page_list(book.nav)
    __ = ncx.sync_head(book.metadata)

    return ncx
