from pathlib import Path
from typing import IO
from zipfile import ZipInfo

from epublib.exceptions import EPUBError
from epublib.mediatype import MediaType
from epublib.nav.resource import NavigationDocument
from epublib.ncx.resource import NCXFile
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    info_to_zipinfo,
)


def create_resource(
    file: IO[bytes] | bytes,
    info: ZipInfo | str | Path,
    media_type: MediaType | str | None = None,
    is_nav: bool = False,
):
    zipinfo = info_to_zipinfo(info)

    if media_type is None:
        media_type = MediaType.from_filename(zipinfo.filename)

    if (
        media_type is None
        or Path(zipinfo.filename).parts[0] == "META-INF"
        or zipinfo.filename == "mimetype"
    ):
        return Resource(file, zipinfo)

    if media_type is MediaType.NCX:
        return NCXFile(file, zipinfo, media_type)

    if media_type is MediaType.IMAGE_SVG or media_type is MediaType.XHTML:
        if is_nav:
            return NavigationDocument(file, zipinfo, media_type)
        return ContentDocument(file, zipinfo, media_type)

    if is_nav:
        raise EPUBError(
            f"Found media type of '{zipinfo.filename}' to be "
            f"'{media_type}', which is incompatible with argument "
            "'is_nav=True'. Only XHTML or SVG documents can be the "
            "navigation document"
        )

    return PublicationResource(file, zipinfo, media_type)


def create_resource_from_path(
    path: str | Path,
    info: ZipInfo | str | Path | None = None,
    media_type: MediaType | str | None = None,
    is_nav: bool = False,
):
    file = open(path, "rb")

    if info is None:
        info = Path(path).name

    zipinfo = info

    if not isinstance(info, ZipInfo):
        zipinfo = ZipInfo.from_file(path, info, strict_timestamps=False)

    return create_resource(file, zipinfo, media_type, is_nav)
