from enum import Enum, IntEnum, auto
from mimetypes import guess_file_type as base_guess_file_type
from pathlib import Path
from typing import Self, override


def guess_file_type(path: str | Path) -> str | None:
    """Guess the media type of a file based on its filename or path."""
    path = Path(path)
    print(path)

    if path.suffix.lower() == ".ncx":
        return "application/x-dtbncx+xml"

    return base_guess_file_type(path)[0]


class Category(IntEnum):
    """Broad categories of media types."""

    IMAGE = auto()
    AUDIO = auto()
    STYLE = auto()
    FONT = auto()
    OTHER = auto()
    FOREIGN = auto()
    SENTINEL = auto()


class MediaType(Enum):
    """An EPUB media type, also known as a MIME type."""

    value: str  # type: ignore[reportIncompatibleMethodOverride]

    # Images
    IMAGE_GIF = "image/gif", Category.IMAGE
    IMAGE_JPEG = "image/jpeg", Category.IMAGE
    IMAGE_PNG = "image/png", Category.IMAGE
    IMAGE_SVG = "image/svg+xml", Category.IMAGE
    IMAGE_WEBP = "image/webp", Category.IMAGE

    # Audio
    AUDIO_MPEG = "audio/mpeg", Category.AUDIO
    AUDIO_MP4 = "audio/mp4", Category.AUDIO
    AUDIO_OGG = "audio/ogg", Category.AUDIO

    # Style
    CSS = "text/css", Category.STYLE

    # Fonts
    FONT_TTF = "font/ttf", Category.FONT
    FONT_SFNT = "application/font-sfnt", Category.FONT
    FONT_OTF = "font/otf", Category.FONT
    VND_MS_OPENTYPE = "application/vnd.ms-opentype", Category.FONT
    FONT_WOFF = "font/woff", Category.FONT
    APPLICATION_FONT_WOFF = "application/font-woff", Category.FONT
    FONT_WOFF2 = "font/woff2", Category.FONT

    # Other
    XHTML = "application/xhtml+xml", Category.OTHER
    JAVASCRIPT = "application/javascript", Category.OTHER
    ECMASCRIPT = "application/ecmascript", Category.OTHER
    TEXT_JAVASCRIPT = "text/javascript", Category.OTHER
    NCX = "application/x-dtbncx+xml", Category.OTHER
    SMIL_XML = "application/smil+xml", Category.OTHER

    category: Category

    def __new__(cls, value: str, category: Category):
        obj = object.__new__(cls)
        obj._value_ = value

        return obj

    def is_css(self):
        return self is MediaType.CSS

    def is_js(self):
        return (
            self is self.JAVASCRIPT
            or self is self.ECMASCRIPT
            or self is self.TEXT_JAVASCRIPT
        )

    def __init__(self, value: str, category: Category = Category.SENTINEL) -> None:
        self.category = category
        super().__init__()

    @classmethod
    def coalesce(cls, value: str | Self):
        if isinstance(value, cls):
            return value

        try:
            return cls(value)
        except ValueError:
            return value

    @override
    def __str__(self) -> str:
        return self.value

    def _directory_name(self):
        if self is self.XHTML:
            return "Text"

        match self.category:
            case Category.IMAGE:
                return "Images"
            case Category.AUDIO:
                return "Audio"
            case Category.STYLE:
                return "Styles"
            case Category.FONT:
                return "Fonts"
            case Category.OTHER:
                return "Fonts"
            case _:
                return "Misc"

    @classmethod
    def directory_name(cls, value: "MediaType | str | None"):
        """Default directory name for each category of file. Follows Sigil's defaults"""
        if isinstance(value, cls):
            return value._directory_name()

        return "Misc"

    @classmethod
    def from_filename(cls, value: str | Path):
        """
        Detect media type from filename or path. If a mimetype for the
        path is found, but is not supported by MediaType, return it as a string.
        """

        guessed = guess_file_type(value)
        if not guessed:
            return None
        return cls.coalesce(guessed)
