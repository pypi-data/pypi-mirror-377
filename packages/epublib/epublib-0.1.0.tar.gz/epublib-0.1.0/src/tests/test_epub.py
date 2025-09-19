import shutil
import zipfile
from collections.abc import Generator
from pathlib import Path
from typing import cast, final

import bs4
import pytest

from epublib import EPUB
from epublib.create import EPUBCreator
from epublib.exceptions import ClosedEPUBError, EPUBError, NotEPUBError
from epublib.identifier import EPUBId
from epublib.mediatype import MediaType
from epublib.nav.resource import NavigationDocument
from epublib.package.resource import PackageDocument
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    XMLResource,
)
from epublib.resources.create import create_resource, create_resource_from_path
from epublib.util import (
    get_absolute_href,
    get_relative_href,
    split_fragment,
)

from . import Samples


@final
class TestEPUB:
    @pytest.fixture
    def not_epubs(self, tmp_path: Path):
        fname = tmp_path / "zip.zip"

        def files() -> Generator[Path]:
            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr("test.txt", "xpto")
            yield fname

            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr("META-INF/container.xml", "not xml")
            yield fname

            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr(
                    "META-INF/container.xml",
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<container version="1.0" '
                    'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                    "</container>",
                )
            yield fname

            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr(
                    "META-INF/container.xml",
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<container version="1.0" '
                    'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                    "<rootfiles>"
                    '<rootfile media-type="application/oebps-package+xml"/>'
                    "</rootfiles>"
                    "</container>",
                )
            yield fname

        return files()

    def test_non_epub(self, not_epubs: Generator[Path]):
        with pytest.raises(NotEPUBError):
            __ = EPUB(Samples.image)

        for fname in not_epubs:
            with pytest.raises(NotEPUBError):
                __ = EPUB(fname)

    def test_ignore_dirs(self, tmp_path: Path):
        fname = shutil.copy(Samples.epub, tmp_path / "tmp.epub")
        with zipfile.ZipFile(fname, "a") as zf:
            zf.writestr("somefolder/", "")

        with EPUB(fname) as epub:
            assert not any(res.filename == "somefolder" for res in epub.resources)

    def test_context(self, tmp_path: Path):
        with EPUB(Samples.epub) as epub:
            self._test_epub(epub)

        assert epub.is_closed()
        with pytest.raises(ClosedEPUBError):
            epub.write(tmp_path / "tmp.epub")

    def _test_epub(self, epub: EPUB):
        assert len(epub.resources)
        assert repr(epub)
        assert any(
            isinstance(resource, PackageDocument) for resource in epub.resources
        ), "Package document does not exist"
        assert any(
            isinstance(resource, ContentDocument) for resource in epub.resources
        ), "No content document exists"

    def test_read(self, epub: EPUB):
        self._test_epub(epub)

    def test_folder_read(self, folder_epub: EPUB):
        self._test_epub(folder_epub)

    def test_write(self, tmp_path: Path, epub: EPUB):
        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)

        out = EPUB(outfn)
        self._test_epub(out)

    def test_folder_write(self, tmp_path: Path, epub: EPUB):
        outfn = tmp_path / "folder_epub"
        outfn.mkdir(exist_ok=True)
        epub.write_to_folder(outfn)

        epub = EPUB(outfn)
        self._test_epub(epub)

    def test_read_after_write(self, tmp_path: Path, epub: EPUB):
        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)

        self._test_epub(epub)

    def test_edit_xml(self, tmp_path: Path, epub: EPUB):
        xml = next(
            cast(ContentDocument[bs4.BeautifulSoup], res)
            for res in epub.resources
            if isinstance(res, ContentDocument) and res.media_type is MediaType.XHTML
        )

        soup = xml.soup
        filename = xml.filename
        div = soup.new_tag("div")
        div["id"] = "testid-xxx"

        assert xml.soup.html
        _ = xml.soup.html.append(div)

        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)

        out = EPUB(outfn)
        new_xml = out.resources.get(filename, XMLResource)
        assert new_xml
        assert new_xml.soup.find(id="testid-xxx"), filename

    def test_resolve_href(self, epub: EPUB):
        resource = epub.resources.resolve_href("OEBPS/Text/Section0001.xhtml", False)
        assert resource
        assert resource.filename == "OEBPS/Text/Section0001.xhtml"

        resource = epub.resources.resolve_href(
            "Section0001.xhtml",
            False,
            relative_to="OEBPS/Text/other_text.xhtml",
        )
        assert resource
        assert resource.filename == "OEBPS/Text/Section0001.xhtml"

        resource = epub.resources.resolve_href(
            "../Text/Section0001.xhtml",
            False,
            relative_to=epub.resources.get("OEBPS/Styles/Style0001.css"),
        )
        assert resource
        assert resource.filename == "OEBPS/Text/Section0001.xhtml"

        resource, tag = epub.resources.resolve_href(
            "OEBPS/Text/Section0001.xhtml#lorem-ipsum",
            cls=ContentDocument,
        )
        assert resource
        assert tag
        assert tag.name == "h1"

        assert epub.resources.resolve_href("xpto/xpto", False) is None
        assert epub.resources.resolve_href("xpto/xpto") == (None, None)

        resource, tag = epub.resources.resolve_href(
            "OEBPS/Text/Section0001.xhtml#lorem ipsum",
            cls=ContentDocument,
        )
        assert tag is None

    def test_create_epub(self, epub_path: Path):
        epub = EPUB()

        assert epub.metadata
        assert epub.metadata.get("language")
        assert epub.metadata.get("identifier")
        assert epub.metadata.get("title")

        assert epub.manifest
        assert epub.spine
        assert epub.nav
        assert epub.nav.toc

        assert len(epub.resources)

        epub.resources.add(ContentDocument(b"", "Text/chapter1.xhtml"))

        epub.write(epub_path)

        with EPUB(epub_path) as epub:
            assert epub.metadata
            assert epub.manifest
            assert epub.spine
            assert len(epub.resources)
            assert epub.resources.get("Text/chapter1.xhtml")

    def test_create_epub_with_options(self):
        file = EPUBCreator(
            language="es-ES",
            book_title="title",
            unique_identifier="other-id",
            package_document_path="some/path/to/opf.opf",
            navigation_document_path="another/path/to/nav.xhtml",
            navigation_document_title="Nav Title",
            toc_title="Table of Contents",
        ).to_file()
        epub = EPUB(file)

        assert epub.metadata
        assert epub.metadata.language == "es-ES"
        assert epub.metadata.title == "title"
        assert epub.package_document.soup.package
        assert epub.package_document.soup.package["unique-identifier"] == "other-id"
        assert epub.package_document.filename == "some/path/to/opf.opf"
        assert epub.nav
        assert epub.nav.filename == "another/path/to/nav.xhtml"
        title_tag = epub.nav.soup.select_one("head > title")
        assert title_tag
        assert title_tag.string == "Nav Title"
        assert epub.nav.toc
        assert epub.nav.toc.text == "Table of Contents"
        assert all(
            item.text == "Table of Contents"
            for item in epub.nav.toc.items_referencing(epub.nav.filename)
        )


class TestResourceManagement:
    def test_get_by_id(self, epub: EPUB):
        identifier = epub.spine.items[0].idref
        assert epub.resources.get(EPUBId(identifier))

    def test_resource_class_choice(self):
        assert type(create_resource(b"", "META-INF/xpto.xml")) is Resource
        assert (
            type(create_resource(b"", "xpto.xhtml", MediaType.XHTML)) is ContentDocument
        )
        assert (
            type(create_resource(b"", "xpto.xhtml", MediaType.XHTML, True))
            is NavigationDocument
        )
        assert type(
            create_resource(b"", "xpto.svg", MediaType.IMAGE_SVG) is ContentDocument
        )
        assert (
            type(create_resource(b"", "xpto.jpeg", MediaType.IMAGE_JPEG))
            is PublicationResource
        )
        assert type(
            create_resource(b"", "xpto.js", MediaType.JAVASCRIPT) is PublicationResource
        )

    def test_create_resource(self):
        resource = create_resource_from_path(Samples.image)
        assert Path(resource.filename).name == Samples.image.name

        with pytest.raises(EPUBError):
            resource = create_resource_from_path(Samples.image, is_nav=True)

    @pytest.mark.parametrize("identifier", [None, EPUBId("custom-id"), "string-ig"])
    def test_add(self, epub: EPUB, resource: Resource, identifier: str | EPUBId | None):
        epub.resources.add(resource, identifier=identifier)

        assert epub.resources.get(resource.filename)
        manifest_item = epub.manifest.get(resource.filename)
        assert manifest_item
        assert manifest_item.id
        if identifier is not None:
            assert manifest_item.id == identifier
        assert type(manifest_item.id) is EPUBId
        assert epub.spine.get(manifest_item.id) is None

    def test_add_after_before_error(self, epub: EPUB, resources: Generator[Resource]):
        resource = next(resources)
        other_resource = next(resources)

        with pytest.raises(EPUBError):
            epub.resources.add(resource, after=other_resource)

        with pytest.raises(EPUBError):
            epub.resources.add(resource, before=other_resource)

    def test_add_no_manifest_errors(self, epub: EPUB, resource: Resource):
        with pytest.raises(EPUBError):
            epub.resources.add(resource, add_to_manifest=False, add_to_spine=True)

        with pytest.raises(EPUBError):
            epub.resources.add(resource, add_to_manifest=False, add_to_toc=True)

    def test_add_with_position(self, epub: EPUB, resource: Resource):
        epub.resources.add(resource, position=3)
        assert epub.resources[3] is resource

    def test_add_to_spine(self, epub: EPUB, resource: Resource):
        epub.resources.add(resource, add_to_spine=True)

        manifest_item = epub.manifest.get(resource.filename)
        assert manifest_item
        assert epub.spine.get(manifest_item.id)

    def test_add_to_spine_with_position(self, epub: EPUB, resource: Resource):
        epub.resources.add(resource, add_to_spine=True, spine_position=2)

        tag = epub.spine.tag.find_all("itemref")[2]
        assert tag
        assert isinstance(tag, bs4.Tag)
        assert tag["idref"] == epub.manifest[resource.filename].id

    def test_add_cover(self, epub: EPUB, resource: Resource):
        epub.resources.add(resource, is_cover=True)

        manifest_item = epub.manifest.get(resource.filename)
        assert manifest_item
        assert manifest_item.properties
        assert "cover-image" in manifest_item.properties

    def test_add_to_nav(self, epub: EPUB, resource: Resource):
        epub.resources.add(resource, add_to_toc=True)

        assert epub.nav
        assert epub.nav.toc
        assert epub.nav.toc.tag.select(f'[href$="{Path(resource.filename).name}"]')

    @pytest.mark.parametrize("n", range(2))
    def test_add_to_nav_with_position(self, epub: EPUB, resource: Resource, n: int):
        epub.resources.add(resource, add_to_toc=True, toc_position=n)

        assert epub.nav
        assert epub.nav.toc
        assert (
            Path(epub.nav.toc.items[n].href or "").name == Path(resource.filename).name
        )

    @pytest.mark.parametrize("n", range(4))
    def test_resource_removal(self, epub: EPUB, epub_path: Path, n: int):
        resource = next(
            r
            for r in epub.resources.filter(ContentDocument)
            if not isinstance(r, NavigationDocument)
        )
        if n == 0:
            epub.resources.remove(resource.filename)
        elif n == 1:
            epub.resources.remove(resource)
        elif n == 2:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.remove(item)
        elif n == 3:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.remove(item.id)

        epub.write(epub_path)

        epub = EPUB(epub_path)

        never = epub.resources.get(resource.filename)
        assert never is None

        assert epub.manifest.get(resource.filename) is None
        assert epub.get_spine_item(resource.filename) is None
        assert epub.nav
        assert resource.filename not in epub.nav.content.decode()

    def test_css_removal(self, epub: EPUB, epub_path: Path):
        resource = next(epub.resources.filter(MediaType.CSS))
        epub.resources.remove(resource, remove_css_js_links=True)
        epub.write(epub_path)

        epub = EPUB(epub_path)

        never = epub.resources.get(resource.filename)
        assert never is None

        for res in epub.resources.filter(ContentDocument):
            for tag in res.soup.find_all("link", rel="stylesheet", href=True):
                assert isinstance(tag, bs4.Tag)
                relative_href = get_relative_href(res.filename, resource.filename)
                assert tag["href"] != relative_href

    def test_js_removal(self, epub: EPUB, epub_path: Path):
        resource = next(epub.resources.filter(MediaType.JAVASCRIPT))
        epub.resources.remove(resource, remove_css_js_links=True)
        epub.write(epub_path)

        epub = EPUB(epub_path)

        never = epub.resources.get(resource.filename)
        assert never is None

        for res in epub.resources.filter(ContentDocument):
            for tag in res.soup.find_all("script", src=True):
                assert isinstance(tag, bs4.Tag)
                relative_href = get_relative_href(res.filename, resource.filename)
                assert tag["src"] != relative_href

    def test_removal_errors(self, epub: EPUB, resource: Resource):
        with pytest.raises(EPUBError):
            epub.resources.remove(epub.package_document)

        with pytest.raises(EPUBError):
            epub.resources.remove(epub.container_file)

        with pytest.raises(EPUBError):
            epub.resources.remove(resource)

        with pytest.raises(EPUBError):
            existing = next(epub.resources.filter(MediaType.XHTML))
            epub.resources.remove(existing, remove_css_js_links=True)

    def _valid_hrefs(self, epub: EPUB):
        reference_attrs = ["href", "src", "full-path", "xlink:href"]
        selector = ", ".join(f"[{attr.replace(':', '|')}]" for attr in reference_attrs)

        for resource in epub.resources.filter(XMLResource):
            for tag in resource.soup.select(selector):
                for attr in reference_attrs:
                    value = tag.get(attr)
                    if value is not None:
                        ref, identifier = split_fragment(str(value))
                        if ref:
                            if attr == "full-path":
                                absolute_href = ref
                            else:
                                absolute_href = get_absolute_href(
                                    resource.filename,
                                    ref,
                                )
                            if identifier:
                                absolute_href += f"#{identifier}"

                            res, ref_tag = epub.resources.resolve_href(absolute_href)
                            assert res, absolute_href

                            if "#" in value:
                                assert ref_tag

    @pytest.mark.parametrize("n", range(4))
    def test_resource_rename(self, epub: EPUB, epub_path: Path, n: int):
        self._valid_hrefs(epub)
        assert epub.nav

        resource = next(
            r
            for r in epub.resources.filter(ContentDocument)
            if not isinstance(r, NavigationDocument)
            and Path(r.filename).name in epub.nav.content.decode()
        )

        new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"

        if n == 0:
            epub.resources.rename(resource, new_filename)
        elif n == 1:
            epub.resources.rename(resource.filename, new_filename)
        elif n == 2:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.rename(item, new_filename)
        elif n == 3:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.rename(item.id, new_filename)

        epub.write(epub_path)
        epub = EPUB(epub_path)

        new_resource = epub.resources.get(new_filename)
        assert new_resource
        self._valid_hrefs(epub)

        assert epub.manifest.get(new_filename)
        assert epub.get_spine_item(new_filename)
        assert epub.nav
        assert Path(new_filename).name in epub.nav.content.decode()

    def test_nav_rename(self, epub: EPUB, epub_path: Path):
        self._valid_hrefs(epub)
        assert epub.nav
        resource = epub.nav

        new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
        epub.resources.rename(resource, new_filename)
        epub.write(epub_path)
        epub = EPUB(epub_path)

        new_resource = epub.resources.get(new_filename)
        assert new_resource
        self._valid_hrefs(epub)

        assert epub.manifest.get(new_filename)
        assert epub.get_spine_item(new_filename)
        assert epub.nav

    def test_package_document_rename(self, epub: EPUB, epub_path: Path):
        self._valid_hrefs(epub)
        resource = epub.package_document

        new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
        epub.resources.rename(resource, new_filename)
        epub.write(epub_path)
        epub = EPUB(epub_path)

        new_resource = epub.resources.get(new_filename)
        assert new_resource
        self._valid_hrefs(epub)

    def test_rename_errors(self, epub: EPUB, resource: Resource):
        with pytest.raises(EPUBError):
            new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
            epub.resources.rename(resource, new_filename)

        with pytest.raises(EPUBError):
            resource = epub.container_file
            new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
            epub.resources.rename(resource, new_filename)

    def test_generator(self, epub: EPUB):
        assert epub.metadata.get("generator")
        assert epub.metadata.get("epublib version")

        epub.remove_generator_tag()

        assert not epub.metadata.get("generator")
        assert not epub.metadata.get("epublib version")
