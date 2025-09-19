import enum
import os.path
import re
import unicodedata
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import cast, overload

import bs4

from epublib.exceptions import EPUBError


def normalize_path[T: (str, Path)](path: T) -> T:
    # Resolve ..'s
    absolute = os.path.normpath(path)
    if isinstance(path, Path):
        return Path(absolute)
    return absolute


def get_absolute_href[T: (str, Path)](origin_href: str | Path, href: T) -> T:
    path = Path(origin_href).parent / Path(href)
    if isinstance(href, str):
        return str(normalize_path(path))
    return normalize_path(path)


def get_relative_href[T: (str, Path)](relative_to: str | Path, absolute_href: T) -> T:
    path = Path(absolute_href).relative_to(Path(relative_to).parent, walk_up=True)

    if isinstance(absolute_href, str):
        return str(path)
    return path


@overload
def parse_int(value: str) -> int | None: ...
@overload
def parse_int(value: None) -> None: ...


def parse_int(value: str | None):
    """Lenient integer parsing"""
    if value is None:
        return None

    value = "".join(filter(str.isdigit, value))
    try:
        return int(value)
    except ValueError:
        return None


def tag_ids(tag: bs4.Tag):
    return {attr_to_str(t["id"]) for t in tag.select("[id]") if tag.get("id")}


def new_id(base: str, gone: set[str], add_to_gone: bool = True) -> str:
    if base not in gone:
        if add_to_gone:
            gone.add(base)
        return base

    for i in range(1, 1000):
        new = f"{base}-{i}"
        if new not in gone:
            if add_to_gone:
                gone.add(new)
            return new

    raise EPUBError(f"Exhausted unique id possibilities for {base}")


def new_id_in_tag(base: str, tag: bs4.Tag):
    ids = tag_ids(tag)
    return new_id(base, ids, False)


def get_content_document_title(soup: bs4.BeautifulSoup):
    if soup.h1 and soup.h1.string:
        return soup.h1.string

    if soup.title and soup.title.string:
        return soup.title.string

    tag = cast(bs4.Tag, soup.find(string=True))
    if tag and tag.string:
        return tag.string

    return ""


def split_fragment(href: str) -> tuple[str, str | None]:
    values = href.split("#", 1)
    if len(values) < 1:
        return "", None
    if len(values) < 2:
        return values[0], None
    return values[0], values[1]


def strip_fragment(href: str) -> str:
    return split_fragment(href)[0]


def slugify(value: str):
    """
    Adapted from django's utils.text

    Convert to ASCII. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


class ResolutionType(enum.Enum):
    """Strategy for converting a list of BeautifulSoup attribute values into a single string."""

    JOIN = enum.auto()
    FIRST = enum.auto()


@overload
def attr_to_str(
    value: str | list[str],
    resolution_type: ResolutionType = ResolutionType.JOIN,
) -> str: ...


@overload
def attr_to_str(
    value: str | list[str] | None,
    resolution_type: ResolutionType = ResolutionType.JOIN,
) -> str | None: ...


def attr_to_str(
    value: str | list[str] | None,
    resolution_type: ResolutionType = ResolutionType.JOIN,
) -> str | None:
    if value is None:
        return None

    if isinstance(value, list):
        match resolution_type:
            case ResolutionType.JOIN:
                return " ".join(value)
            case ResolutionType.FIRST:
                return value[0]

    return value


def get_actual_tag_position(tag: bs4.Tag, position: int) -> int:
    """
    Given a tag `tag` and a position `i`, return the index `ret` of
    `position`-th child of tag (i.e. disregarding NavigableString
    children of tag). If `position` is out of bounds, return position for
    last child + 1.
    """

    tags = [el for el in tag.find_all(recursive=False) if isinstance(el, bs4.Tag)]

    if position >= len(tags):
        return len(list(tag.children))

    sucessor = tags[position]
    return tag.index(sucessor)


def datetime_to_str(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.astimezone()

    dt = dt.astimezone(timezone.utc)

    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def get_epublib_version() -> str | None:
    try:
        return version("epublib")
    except PackageNotFoundError:
        return None
