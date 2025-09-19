from dataclasses import dataclass
from typing import ClassVar, SupportsIndex, override

import bs4

from epublib.identifier import EPUBId
from epublib.xml_element import XMLElement, XMLParent


@dataclass(kw_only=True)
class SpineItemRef(XMLElement):
    """An item reference in the EPUB spine."""

    id: str | None = None
    linear: bool | None = None
    properties: str | None = None

    obj_to_tag: ClassVar[dict[str, str]] = {"name": "idref"}

    @property
    @override
    def tag_name(self):
        return "itemref"

    @property
    def idref(self) -> EPUBId:
        return EPUBId(self.name)

    @idref.setter
    def idref(self, value: EPUBId):
        self.name: str = EPUBId(value)

    @override
    def create_tag(self, soup: bs4.BeautifulSoup, **kwargs: str) -> bs4.Tag:
        tag = super().create_tag(soup, **kwargs)
        if self.linear:
            del tag["linear"]

        return tag

    @override
    def __post_init__(self):
        super().__post_init__()
        self.name = EPUBId(self.name)


class BookSpine(XMLParent[SpineItemRef]):
    """The EPUB spine, which defines the linear reading order of the book."""

    tag_name: str | None = "spine"
    default_item_type: type[SpineItemRef] = SpineItemRef

    @override
    def create_items(self):
        items: list[SpineItemRef] = []
        for tag in self.tag.children:
            if isinstance(tag, bs4.Tag):
                items.append(SpineItemRef.from_tag(tag))

        return items

    def add(self, id_ref: str | EPUBId):
        __ = self.add_item(SpineItemRef(name=id_ref))

    def insert(self, position: int, id_ref: str):
        __ = self.insert_item(position, SpineItemRef(name=id_ref))

    def get_position(self, idref: str | EPUBId) -> int | None:
        return next(
            (i for i, item in enumerate(self.items) if item.idref == idref), None
        )

    def remove(self, idref: str | EPUBId):
        self.remove_item(self[idref])

    def _move_tag(self, item: SpineItemRef, new_position: int):
        tags = list(self.tag.select("itemref"))
        successor = tags[new_position]
        actual_new_position = self.tag.index(successor)

        __ = item.tag.extract()
        __ = self.tag.insert(actual_new_position, item.tag)

    def move_item(self, item: int | str | SpineItemRef, new_position: int):
        if isinstance(item, (str, int)):
            item = self[item]
        else:
            if item not in self.items:
                raise ValueError(f"Item {item} not in spine")

        self._items.remove(item)
        self._items.insert(new_position, item)
        self._move_tag(item, new_position)

    def reorder(self, items: list[SpineItemRef]):
        new_items_set = {item.idref for item in items}
        curr_items_set = {item.idref for item in self.items}

        if len(new_items_set) != len(items):
            raise ValueError("Duplicate items in new order")

        if new_items_set != curr_items_set:
            raise ValueError("Items do not match current spine items")

        self._items: list[SpineItemRef] = items

        self.tag.clear()
        for item in items:
            __ = self.tag.append(item.tag)

    @override
    def __getitem__(self, name: str | SupportsIndex) -> SpineItemRef:
        if isinstance(name, SupportsIndex):
            return self.items[name]
        return super().__getitem__(name)
