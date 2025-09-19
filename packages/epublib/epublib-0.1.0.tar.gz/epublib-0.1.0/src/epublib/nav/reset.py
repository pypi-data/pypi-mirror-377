from typing import cast

import bs4

from epublib.exceptions import EPUBError
from epublib.nav.resource import NavigationDocument
from epublib.nav.util import LandmarkEntryData, PageBreakData, TOCEntryData, detect_page
from epublib.resources import ContentDocument, Resource, XMLResource
from epublib.types import BookProtocol
from epublib.util import (
    attr_to_str,
    get_content_document_title,
    new_id,
    new_id_in_tag,
    slugify,
    tag_ids,
)


def reset_toc(
    book: BookProtocol,
    targets_selector: str | None = None,
    include_filenames: bool = False,
    spine_only: bool = False,  # ensures correct ordering
    reset_ncx: bool | None = None,
    resource_class: type[Resource] = ContentDocument,
):
    """
    Reset the table of contents in the navigation document by
    detecting targets in content documents. May replace any
    existing TOC.
    """

    if not book.nav:
        raise EPUBError("Can't reset TOC in EPUB without navigation document")

    if reset_ncx and not book.ncx:
        raise EPUBError.missing_ncx(book, "reset_toc")

    entries: list[TOCEntryData] = []
    if spine_only:
        resources = (book.resources[item] for item in book.spine.items)
    else:
        resources = book.resources.filter(resource_class)

    for resource in resources:
        if targets_selector is None or include_filenames:
            if isinstance(resource, XMLResource) and resource is not book.nav:
                label = get_content_document_title(
                    cast(bs4.BeautifulSoup, resource.soup)
                )
            else:
                label = resource.filename
            entries.append(TOCEntryData(resource.filename, label=label))
        if (
            targets_selector
            and isinstance(resource, XMLResource)
            and resource is not book.nav
        ):
            soup = cast(bs4.BeautifulSoup, resource.soup)
            used_ids: set[str] = set()
            for index, tag in enumerate(soup.select(targets_selector)):
                label = tag.get_text()
                identifier = attr_to_str(tag.get("id"))
                if not identifier:
                    base_id = slugify(label) if label else f"toc-target-{index + 1}"
                    identifier = tag["id"] = new_id(base_id, used_ids, False)
                used_ids.add(identifier)
                entries.append(
                    TOCEntryData(
                        resource.filename,
                        label=label,
                        id=identifier,
                    )
                )

    book.nav.reset_toc(entries)
    if book.ncx and (reset_ncx or reset_ncx is None):
        book.ncx.reset_nav_map(entries)


def create_toc(
    book: BookProtocol,
    targets_selector: str | None = None,
    include_filenames: bool = False,
    spine_only: bool = False,  # ensures correct ordering
    reset_ncx: bool | None = None,
    resource_class: type[Resource] = ContentDocument,
):
    """
    Create o new table of contents in the navigation document by
    detecting targets in content documents. Will raise an error if
    a TOC already exists.
    """

    if not book.nav:
        raise EPUBError("Can't create TOC in EPUB without navigation document")

    if book.nav.toc is not None:
        raise EPUBError(
            "Can't create TOC as it already exists. "
            f"Consider using '{book.__class__.__name__}.reset_toc'"
        )

    if reset_ncx and not book.ncx:
        raise EPUBError.missing_ncx(book, "create_toc")

    reset_toc(
        book,
        targets_selector,
        include_filenames,
        spine_only,
        reset_ncx,
        resource_class,
    )


def reset_page_list(
    book: BookProtocol,
    id_format: str = "page_{page}",
    label_format: str = "{page}",
    pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
    reset_ncx: bool | None = None,
):
    """
    Reset the page list in the navigation document by detecting
    pagebreaks in content documents. Will replace any existing page
    list.
    """
    pagebreaks: list[PageBreakData] = []

    if reset_ncx and not book.ncx:
        raise EPUBError.missing_ncx(book, "create_toc")

    if not book.nav:
        raise EPUBError("Can't reset page list in EPUB without navigation document")

    for resource in book.resources.filter(ContentDocument):
        used_ids = tag_ids(resource.soup)
        for tag in resource.soup.select(pagebreak_selector):
            page = detect_page(tag)
            if page is not None:
                if not tag.get("id"):
                    tag["id"] = new_id(id_format.format(page=page), used_ids, False)
                used_ids.add(attr_to_str(tag["id"]))
                pagebreaks.append(
                    PageBreakData(
                        id=attr_to_str(tag["id"]),
                        filename=resource.filename,
                        page=page,
                        label=label_format.format(page=page),
                    )
                )

    book.nav.reset_page_list(pagebreaks)
    if book.ncx and (reset_ncx or reset_ncx is None):
        book.ncx.reset_page_list(pagebreaks)


def create_page_list(
    book: BookProtocol,
    id_format: str = "page_{page}",
    label_format: str = "{page}",
    pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
    reset_ncx: bool | None = None,
):
    """
    Create new page list in the navigation document by detecting
    pagebreaks in content documents. Will raise an error if a page
    list already exists.
    """

    if reset_ncx and not book.ncx:
        raise EPUBError.missing_ncx(book, "create_page_list")

    if not book.nav:
        raise EPUBError("Can't create page list in EPUB without navigation document")

    if book.nav.page_list is not None:
        raise EPUBError(
            "Can't create page list as it already exists. "
            f"Consider using '{book.__class__.__name__}.reset_page_list'"
        )

    return reset_page_list(
        book,
        id_format,
        label_format,
        pagebreak_selector,
        reset_ncx,
    )


def reset_landmarks(
    book: BookProtocol,
    include_toc: bool = True,
    targets_selector: str | None = None,
):
    """
    Reset the landmarks in the navigation document by detecting
    targets in content documents, and optionally including the TOC.
    Will replace existing landmarks.
    """

    if not book.nav:
        raise EPUBError("Can't reset landmarks in EPUB without navigation document")

    entries: list[LandmarkEntryData] = []
    if include_toc and book.nav and book.nav.toc:
        tag = book.nav.toc.tag
        if not tag.get("id"):
            tag["id"] = new_id_in_tag("toc", book.nav.soup)

        entries.append(
            LandmarkEntryData(
                book.nav.filename,
                book.nav.toc.text,
                attr_to_str(tag["id"]),
                epub_type="toc",
            )
        )
    if targets_selector:
        for resource in book.resources.filter(XMLResource):
            if include_toc and isinstance(resource, NavigationDocument):
                continue

            used_ids = tag_ids(resource.soup)
            for index, tag in enumerate(resource.soup.select(targets_selector)):
                label = tag.get_text()
                identifier = attr_to_str(tag.get("id"))
                if not identifier:
                    base_id = slugify(label) if label else f"toc-target-{index + 1}"
                    identifier = tag["id"] = new_id(base_id, used_ids, False)
                used_ids.add(identifier)
                entries.append(
                    LandmarkEntryData(
                        resource.filename,
                        label=label,
                        id=identifier,
                    )
                )
    book.nav.reset_landmarks(entries)


def create_landmarks(
    book: BookProtocol,
    include_toc: bool = True,
    targets_selector: str | None = None,
):
    """
    Create landmarks in the navigation document by detecting
    targets in content documents, and optionally including the TOC.
    Will raise error if landmarks already exist.
    """

    if not book.nav:
        raise EPUBError("Can't create landmarks in EPUB without navigation document")

    if book.nav.landmarks is not None:
        raise EPUBError(
            "Can't create landmarks as it already exists. "
            f"Consider using '{book.__class__.__name__}.reset_landmarks'"
        )

    return reset_landmarks(book, include_toc, targets_selector)
