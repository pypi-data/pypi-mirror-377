import zipfile
from pathlib import Path
from tempfile import TemporaryFile

import pytest

from epublib import EPUB
from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.mediatype import MediaType
from epublib.package.manifest import ManifestItem
from epublib.resources import ContentDocument, PublicationResource
from tests import Samples


class TestEPUBManifest:
    def test_manifest(self, epub: EPUB):
        assert epub.manifest
        assert repr(epub.manifest)

    @pytest.mark.parametrize("i", range(5))
    def test_manifest_get_item(self, epub: EPUB, i: int):
        resources = list(epub.resources.filter(PublicationResource))
        resource = resources[i]
        manifest_item = epub.manifest.get(resource)
        assert manifest_item
        assert manifest_item is epub.manifest.get(resource.filename)
        assert manifest_item.media_type
        assert manifest_item.media_type == str(resource.media_type)

    @pytest.mark.parametrize("i", range(5))
    def test_change_manifest_reference(self, epub: EPUB, i: int):
        manifest_item = epub.manifest.items[i]
        absolute = Path(manifest_item.filename)
        relative = Path(manifest_item.href)

        new_absolute = absolute.parent / "test" / "xpto" / "newname.txt"
        new_relative = relative.parent / "test" / "xpto" / "newname.txt"

        manifest_item.filename = str(new_absolute)
        assert manifest_item.href == str(new_relative)

    def test_manifest_properties(self, epub: EPUB):
        for item in epub.manifest.items:
            item.properties = None
            item.add_property("custom")

        assert all(
            item.properties and "custom" in item.properties
            for item in epub.manifest.items
        )

        assert all(item.has_property("custom") for item in epub.manifest.items)

        for item in epub.manifest.items:
            item.add_property("custom")

        assert all(
            item.properties is not None and len(item.properties) == 1
            for item in epub.manifest.items
        )

        for item in epub.manifest.items:
            item.remove_property("custom")

        assert all(item.properties is None for item in epub.manifest.items)

    def test_update_manifest_properties(self, epub: EPUB):
        for item in epub.manifest.items:
            item.properties = None

        epub.update_manifest_properties()
        assert any(item.properties for item in epub.manifest.items)

    def test_create_manifest_item(self, epub: EPUB):
        path = Path("OEBPS", "Images", "image2-xxx.jpg")

        epub.manifest.add_item(
            ManifestItem(
                name=str(path),
                id=EPUBId(path.name.replace(".", "")),
                media_type=str(MediaType.IMAGE_JPEG),
                manifest_filename=epub.manifest._resource_filename,  # type: ignore[reportPrivateUsage]
            )
        )

        assert epub.package_document.soup.manifest.select('[href$="image2-xxx.jpg"]')
        assert not epub.package_document.soup.manifest.select("[manifest-filename]")

    def test_create_manifest_item_for_existing_file(self, epub: EPUB):
        filename = Path("OEBPS", "Images", "image2-xxx.jpg")
        with TemporaryFile() as f:
            epub.write(f)
            __ = f.seek(0)

            with zipfile.ZipFile(f, "a") as zf:
                zf.write(Samples.image, filename)

            __ = f.seek(0)

            epub = EPUB(f)
            resource = epub.resources.get(filename)
            assert resource
            assert not epub.manifest.get(str(filename))

            resource, manifest_item = epub.resources.add_to_manifest(resource)
            assert resource
            assert manifest_item

            assert epub.manifest.get(str(filename))

            resource = epub.resources.get(filename)
            assert isinstance(resource, PublicationResource)

    def test_duplicate_id_filename_check(self, epub: EPUB):
        item = epub.manifest.items[0]

        with pytest.raises(EPUBError):
            __ = epub.manifest.add_item(item)

        with pytest.raises(EPUBError):
            __ = epub.manifest.add_item(
                ManifestItem(
                    name="name",
                    id=item.id,
                    media_type="text/plain",
                    manifest_filename=epub.package_document.filename,
                )
            )

        with pytest.raises(EPUBError):
            __ = epub.manifest.add_item(
                ManifestItem(
                    name=item.name,
                    id=EPUBId("some-id"),
                    media_type="text/plain",
                    manifest_filename=epub.package_document.filename,
                )
            )
        with pytest.raises(EPUBError):
            __ = epub.resources.add(ContentDocument(b"aham", item.filename))

        with pytest.raises(EPUBError):
            __ = epub.resources.add(
                ContentDocument(b"aham", "text.xhtml"),
                identifier=item.id,
            )

    def test_rename_id(self, epub: EPUB):
        item = epub.manifest.items[0]
        old_id = item.id
        new_id = EPUBId("new-id")
        epub.rename_id(item, new_id)

        assert item.id == new_id
        assert old_id != new_id
        assert not epub.package_document.soup.select(f'[id="{old_id}"]')
        assert epub.package_document.soup.select(f'[id="{new_id}"]')

        ncx = epub.reset_ncx()
        epub.rename_id(ncx, EPUBId("new-id-ncx"))
        assert epub.spine.tag["toc"] == "new-id-ncx"

        spine_item = epub.spine.items[0]
        old_id = spine_item.idref
        new_id = EPUBId("new-id-spine")
        epub.rename_id(spine_item, new_id)

        assert epub.manifest.get(new_id)
