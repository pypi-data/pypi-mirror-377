from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator, Sequence
from typing import Any, Self, cast, override

import bs4

from epublib.exceptions import EPUBError
from epublib.util import (
    attr_to_str,
    get_relative_href,
    split_fragment,
    strip_fragment,
)


class NavigationReference[
    C: NavigationReference,
    S: bs4.BeautifulSoup = bs4.BeautifulSoup,
](ABC):
    """
    Abstract base class for nested references containing text and href.
    This simplest form assumes there is a text tag, and an href tag,
    show href_attr stores the href.
    """

    tag_name: str
    text_selector: str
    text_tag_name: str
    href_selector: str
    href_tag_name: str
    href_attr: str
    child_class: type[C] | None = None

    def __init__(
        self,
        soup: S,
        tag: bs4.Tag | None = None,
        parent: NavigationReference[Any] | None = None,  # type: ignore[reportAny]
        text: str | None = None,
        href: str | None = None,
        depth: int = 0,
    ):
        # Child is responsible for creating new tag if tag is None, but
        # will not insert itself in its parent
        self.soup: S = soup
        self.tag: bs4.Tag = tag if tag else self._create_own_tag()
        self.depth: int = depth
        self.parent: NavigationReference[Any] | None = parent  # type: ignore[reportAny]

        self._items: list[C] = self._init_items()

        if text is not None:
            self.text = text

        if href is not None:
            self.href = href

    def _create_own_tag(self) -> bs4.Tag:
        tag = self.soup.new_tag(self.tag_name)

        return tag

    def _get_text_tag(self) -> bs4.Tag | None:
        return self.tag.select_one(self.text_selector)

    def _get_href_tag(self) -> bs4.Tag | None:
        return self.tag.select_one(self.href_selector)

    def _create_text(self, value: str) -> bs4.Tag:
        text_tag = self.soup.new_tag(self.text_tag_name)
        text_tag.string = value
        __ = self.tag.insert(0, text_tag)

        return text_tag

    def _create_href(self, value: str) -> bs4.Tag | None:
        href_tag = self.soup.new_tag(self.href_tag_name)
        href_tag[self.href_attr] = value
        __ = self.tag.append(href_tag)

        return href_tag

    @property
    def text(self) -> str:
        text_tag = self._get_text_tag()
        if not text_tag:
            return ""
        return text_tag.get_text()

    @text.setter
    def text(self, value: str) -> None:
        text_tag = self._get_text_tag()

        if text_tag:
            text_tag.string = value

        else:
            __ = self._create_text(value)

    def _set_href_tag(self, value: str) -> None:
        href_tag = self._get_href_tag()

        if href_tag:
            href_tag[self.href_attr] = value

        else:
            __ = self._create_href(value)

    @property
    def href(self) -> str:
        href_tag = self._get_href_tag()
        if not href_tag:
            return ""
        return attr_to_str(href_tag[self.href_attr])

    @href.setter
    def href(self, value: str) -> None:
        self._set_href_tag(value)

    @property
    def items(self) -> Sequence[C]:
        return tuple(self._items)

    def _get_child_class(self) -> type[C]:
        return (
            cast(type[C], self.__class__)
            if self.child_class is None
            else self.child_class
        )

    @abstractmethod
    def _get_children_tags(self) -> list[bs4.Tag]:
        pass

    def _init_items(self) -> list[C]:
        items: list[C] = []
        cls = self._get_child_class()

        for child_tag in self._get_children_tags():
            items.append(
                cls(
                    self.soup,
                    child_tag,
                    parent=self,  # type: ignore[reportArgumentType]
                    depth=self.depth + 1,
                )
            )

        return items

    @abstractmethod
    def _insert_tag(self, position: int, tag: bs4.Tag):
        pass

    def add_item(
        self,
        text: str | None,
        href: str | None,
        position: int | None = None,
    ):
        position = len(self.items) if position is None else position

        item = self._get_child_class()(
            self.soup,
            parent=self,
            text=text,
            href=href,
            depth=self.depth + 1,
        )
        self._insert_tag(position, item.tag)
        self._items.insert(position, item)

        return item

    @override
    def __repr__(self) -> str:
        repr = f"{self.__class__.__name__}({self.tag.name}"
        if self.items:
            repr += f", {len(self.items)} items"

        repr += ")"

        return repr

    def remove_item(self, item: C):
        if item not in self.items:
            raise EPUBError(
                f"Can't remove item '{item}' as it is not present in '{self}'"
            )

        __ = item.tag.extract()
        self._items.remove(item)

    def remove(
        self,
        base_filename: str,
        filename: str,
        ignore_fragment: bool = False,
    ):
        relative_href = get_relative_href(base_filename, filename) if filename else None
        for item in self.items:
            cmp = strip_fragment(item.href) if ignore_fragment else item.href
            if cmp == relative_href:
                self.remove_item(item)
            else:
                item.remove(base_filename, filename, ignore_fragment)

    def items_referencing(
        self,
        filename: str,
        ignore_fragment: bool = False,
    ) -> Generator[Self | C]:
        if self.href:
            cmp = strip_fragment(self.href) if ignore_fragment else self.href
            if cmp == filename:
                yield self

        for item in self.items:
            yield from (
                cast(C, it)
                for it in item.items_referencing(
                    filename,
                    ignore_fragment,
                )
            )

    def add_after(self, text: str | None, href: str | None) -> C:
        """Add item with text and href after this item in the parent's list."""
        if not self.parent:
            raise EPUBError("Can't add after root item")

        position = self.parent.items.index(self)
        return cast(C, self.parent.add_item(text, href, position + 1))

    @property
    def max_depth(self) -> int:
        if not self.items:
            return self.depth

        return max(self.depth, *(item.max_depth for item in self.items))


class NavigationRoot[
    C: NavigationReference[Any],
    D,
    S: bs4.BeautifulSoup = bs4.BeautifulSoup,
](
    NavigationReference[C, S],
    ABC,
):
    """
    Abstract base class for root of list of references containing only text
    and href.
    """

    def __init__(
        self,
        soup: S,
        tag: bs4.Tag | None,
        base_filename: str,
        text: str | None = None,
    ):
        self.base_filename: str = base_filename
        super().__init__(soup, tag, parent=None, text=text)
        if tag is None:
            self._insert_self_in_soup()

    @abstractmethod
    def _insert_self_in_soup(self):
        pass

    @abstractmethod
    def reset(self, entries: Sequence[D]) -> None:
        pass

    @override
    def remove(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        filename: str,
        ignore_fragment: bool = True,
    ):
        return super().remove(self.base_filename, filename, ignore_fragment)

    @override
    def items_referencing(
        self,
        filename: str,
        ignore_fragment: bool = True,
    ) -> Generator[C]:
        relative_filenames: list[str] = []

        base, fragment = split_fragment(filename)
        if base == self.base_filename:
            relative_filenames.append("" if fragment is None else f"#{fragment}")

        relative_filenames.append(get_relative_href(self.base_filename, filename))

        for item in self.items:
            for relative_filename in relative_filenames:
                yield from (
                    cast(C, it)
                    for it in item.items_referencing(
                        relative_filename,
                        ignore_fragment,
                    )
                )

    @property
    @override
    def href(self) -> str:
        raise EPUBError(f"Root navigation list ({self.__class__.__name__}) has no href")

    @href.setter
    @override
    def href(self, value: str) -> None:
        raise EPUBError(
            f"Can't set href on root of navigation list ({self.__class__.__name__})"
        )
