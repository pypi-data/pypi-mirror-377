import random
import shutil
import subprocess
from pathlib import Path
from typing import final
from zipfile import ZipFile

from epublib import EPUB

SAMPLES_DIR = Path(__file__).parent / "samples"


@final
class Samples:
    epub = SAMPLES_DIR / "sample.epub"
    simple_epub = SAMPLES_DIR / "simple.epub"
    image = SAMPLES_DIR / "image.jpg"
    tmp_dir = SAMPLES_DIR / "tmp"

    @classmethod
    def get_tmp_dir(cls):
        if cls.tmp_dir.is_dir():
            shutil.rmtree(cls.tmp_dir)

        cls.tmp_dir.mkdir(parents=True, exist_ok=True)
        return SAMPLES_DIR / "tmp"

    @classmethod
    def get_folder_epub(cls):
        folder = cls.get_tmp_dir() / "folder_epub"
        epub = EPUB(cls.epub)
        assert isinstance(epub.source, ZipFile)
        epub.source.extractall(folder)

        return folder


def view_epub(file: str | Path | EPUB):
    if isinstance(file, EPUB):
        filename = Samples.get_tmp_dir() / "tmp.epub"
        file.write(filename)
    else:
        filename = file
    __ = subprocess.call(["xdg-open", str(filename)])


def shuffled[T](lst: list[T]) -> list[T]:
    """
    Return a shuffled copy of a list, making sure it is different from
    the original. The seed is used for reproducibility.
    """

    if len(lst) < 2:
        return lst[:]

    new_list = lst[:]
    i = 100
    seed = 42
    rng = random.Random()

    while new_list == lst and i > 0:
        rng.seed(seed)
        rng.shuffle(new_list)
        seed += 1
        i -= 1

    if i == 0:
        raise RuntimeError("Could not shuffle the list")

    return new_list
