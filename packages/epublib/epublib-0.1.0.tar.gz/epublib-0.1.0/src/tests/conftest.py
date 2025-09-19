from pathlib import Path

import pytest

from epublib import EPUB
from epublib.resources.create import create_resource_from_path

from . import Samples


@pytest.fixture
def epub():
    with EPUB(Samples.epub) as epub:
        yield epub


@pytest.fixture
def folder_epub():
    with EPUB(Samples.get_folder_epub()) as epub:
        yield epub


@pytest.fixture
def resource():
    return create_resource_from_path(Samples.image)


@pytest.fixture
def epub_path(tmp_path: Path):
    return tmp_path / "tmp.epub"


@pytest.fixture
def resources():
    def yield_resources():
        while True:
            yield create_resource_from_path(Samples.image)

    return yield_resources()
