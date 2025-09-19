from dataclasses import dataclass

import bs4
from bs4.element import NamespacedAttribute

from epublib.exceptions import warn
from epublib.util import attr_to_str, parse_int

epub_type = NamespacedAttribute(
    prefix="epub",
    name="type",
    namespace="http://www.idpf.org/2007/ops",
)


def detect_page(tag: bs4.Tag):
    page = None
    if tag.string:
        page = parse_int(tag.string)
        if page is not None:
            return page

    if tag.get("title"):
        page = parse_int(attr_to_str(tag["title"]))

        if page is not None:
            return page

    if tag.get("id"):
        page = parse_int(attr_to_str(tag["id"]))
        if page is not None:
            return page

    warn(f"Can't determine page number of pagebreak element: {tag}")
    return None


@dataclass
class PageBreakData:
    """Data for a page break."""

    id: str
    filename: str
    page: int
    label: str = ""

    def __post_init__(self):
        if not self.label:
            self.label = str(self.page)


@dataclass
class TOCEntryData:
    """Data for a table of contents entry."""

    filename: str
    label: str
    id: str | None = None


@dataclass
class LandmarkEntryData(TOCEntryData):
    """Represents a landmark, a special navigation point in an EPUB file."""

    epub_type: str | None = None
