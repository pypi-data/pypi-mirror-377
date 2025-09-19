import shutil
import sys
import types
from pathlib import Path
from typing import Any

import pytest as pytest
from sybil import Sybil
from sybil.parsers.markdown import PythonCodeBlockParser

from epublib.package.metadata import GenericMetadataItem, MetadataItem
from tests.conftest import Samples


def create_some_custom_item() -> MetadataItem:
    return GenericMetadataItem("some", "value", name="custom")


def get_sample(ns: dict[str, Any]) -> None:  # type: ignore[reportAny]
    __ = shutil.copy(Samples.simple_epub, "book.epub")
    __ = shutil.copy(Samples.image, "new-image.jpg")
    __ = shutil.move(Samples.get_folder_epub(), "book-folder")

    custom_item = types.ModuleType("custom_item")
    custom_item.create_some_custom_item = create_some_custom_item  # type: ignore[reportAttributeAccessIssue]
    sys.modules["custom_item"] = custom_item
    Path("book-folder-modified").mkdir(exist_ok=True)


def remove_sample(_ns: dict[str, Any]) -> None:  # type: ignore[reportAny]
    Path("book.epub").unlink(missing_ok=True)
    Path("book-modified.epub").unlink(missing_ok=True)
    Path("new-image.jpg").unlink(missing_ok=True)
    shutil.rmtree("book-folder", ignore_errors=True)
    shutil.rmtree("book-folder-modified", ignore_errors=True)


pytest_collect_file = Sybil(
    parsers=[PythonCodeBlockParser()],
    pattern="*.md",
    setup=get_sample,
    teardown=remove_sample,
).pytest()
