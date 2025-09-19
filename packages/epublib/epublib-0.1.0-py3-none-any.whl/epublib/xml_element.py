import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from datetime import datetime
from itertools import islice
from types import UnionType
from typing import (
    ClassVar,
    Self,
    cast,
    get_args,
    get_origin,
    overload,
    override,
)

import bs4

from epublib.identifier import EPUBId

sentinel_tag = bs4.BeautifulSoup("", "xml").new_tag("sentinel")


type ValueType = str | datetime | bool | list[str] | EPUBId


@dataclass(kw_only=True)
class XMLElement(ABC):
    """Abstract base class for an XML element."""

    name: str
    tag: bs4.Tag = field(default=sentinel_tag)

    obj_to_tag: ClassVar[dict[str, str]] = {}
    exclude_from_tag: ClassVar[list[str]] = ["tag"]

    @property
    @abstractmethod
    def tag_name(self) -> str:
        raise NotImplementedError

    def __post_init__(self):
        if self.tag is sentinel_tag:
            self.tag = self.create_tag(bs4.BeautifulSoup("", "xml"))

    def value_to_str(self, _attr: str, /, value: ValueType) -> str:
        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, bool):
            return "yes" if value else "no"

        if isinstance(value, list):
            return " ".join(str(el) for el in value)

        return value

    @staticmethod
    def _resolve_type[T: ValueType | UnionType | None](typ: type[T]):
        origin: type[T] = get_origin(typ) or typ

        if origin is UnionType:
            args = cast(tuple[type[T], ...], get_args(typ))
            origin = cast(
                type[T],
                operator.or_(
                    *(
                        cast(
                            type[T],
                            get_origin(arg) or arg,  # type: ignore[reportGeneralTypeIssues]
                        )
                        for arg in args
                    )
                ),
            )

        return origin

    @classmethod
    def to_value[T: ValueType | UnionType | None](
        cls,
        value: str | None,
        typ: type[T],
    ) -> T | None:
        if value is None:
            return None

        typ = cls._resolve_type(typ)

        if issubclass(list, typ):
            return value.split()  # type: ignore[reportReturnType]

        if issubclass(datetime, typ):
            return datetime.fromisoformat(value)  # type: ignore[reportReturnType]

        if issubclass(bool, typ):
            return value != "no"  # type: ignore[reportReturnType]

        if issubclass(EPUBId, typ):
            return EPUBId(value)  # type: ignore[reportReturnType]

        return str(value)  # type: ignore[reportReturnType]

    @override
    def __setattr__(self, name: str, value: ValueType | None) -> None:
        ret = super().__setattr__(name, value)
        if name != "tag":
            self.update_tag(name, value)
        return ret

    def create_tag(self, soup: bs4.BeautifulSoup, **kwargs: str) -> bs4.Tag:
        tag = soup.new_tag(self.tag_name)

        for fld in fields(self):
            val: ValueType | None = getattr(self, fld.name, None)
            if val is not None and fld.name not in self.exclude_from_tag:
                attr = self.obj_to_tag.get(fld.name, fld.name)
                tag[attr.replace("_", "-")] = self.value_to_str(fld.name, val)

        for key, val in kwargs.items():
            tag[key] = val

        return tag

    @classmethod
    def from_tag(cls, tag: bs4.Tag, **kwargs: str) -> Self:
        return cls(
            tag=tag,
            **kwargs,  # type: ignore[reportUnknownArgumentType]
            **{
                field.name: cls.to_value(
                    tag.attrs.get(  # type: ignore[reportArgumentType]
                        cls.obj_to_tag.get(field.name, field.name)
                        .replace("_", "-")
                        .lower()
                    ),
                    field.type,  # type: ignore[reportArgumentType]
                )
                for field in fields(cls)
                if field.name not in cls.exclude_from_tag
            },
        )

    def update_tag(self, field: str, value: ValueType | None):
        if field in self.exclude_from_tag:
            return

        attr = self.obj_to_tag.get(field, field).replace("_", "-").lower()
        if value is None:
            del self.tag[attr]
        else:
            self.tag[attr] = self.value_to_str(field, value)

    @override
    def __repr__(self):
        name_field_name = self.obj_to_tag.get("name", "name")
        return f"{self.__class__.__name__}({name_field_name}={self.name})"


class XMLParent[I: XMLElement](ABC):
    """Abstract base class for an XML element that contains other XML elements."""

    default_item_type: type[I] = XMLElement  # type: ignore[reportAssignmentType]
    tag_name: str | None = None

    def __init__(
        self,
        tag: bs4.Tag,
    ) -> None:
        self.tag: bs4.Tag = tag
        self._items: list[I] = self.create_items()

    @abstractmethod
    def create_items(self) -> list[I]:
        raise NotImplementedError

    @overload
    def get[J: XMLElement](self, name: str, cls: type[J]) -> J | None: ...

    @overload
    def get(self, name: str, cls: type[I] | None = None) -> I | None: ...

    def get(self, name: str, cls: type[I] | None = None):
        if cls is None:
            cls = self.default_item_type

        return next(
            (
                item
                for item in self._items
                if item.name == name and isinstance(item, cls)
            ),
            None,
        )

    def __getitem__(self, name: str):
        value = self.get(name)
        if value is None:
            raise KeyError(name)
        return value

    def add_item(self, item: I) -> I:
        self._items.append(item)
        __ = self.tag.append(item.tag)

        return item

    def insert_item(self, position: int, item: I) -> I:
        self._items.insert(position, item)
        try:
            nth_child = cast(
                bs4.Tag,
                next(islice(self.tag.find_all(True, recursive=False), position, None)),
            )
            __ = nth_child.insert_before(item.tag)
        except StopIteration:
            __ = self.tag.append(item.tag)

        return item

    def remove_item(self, item: I) -> None:
        self._items.remove(item)
        item.tag.decompose()

    @property
    def items(self):
        return tuple(self._items)

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}({len(self.items)} items)"
