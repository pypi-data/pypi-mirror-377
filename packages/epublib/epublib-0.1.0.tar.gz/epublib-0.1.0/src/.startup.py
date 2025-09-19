import re as re
from pathlib import Path as Path

from bs4 import BeautifulSoup as BeautifulSoup

from src.epublib import EPUB as EPUB
from src.epublib.nav.resource import NavigationDocument as NavigationDocument
from src.epublib.ncx.resource import NCXFile as NCXFile
from src.epublib.package.manifest import ManifestItem as ManifestItem
from src.epublib.package.metadata import (
    DublinCoreMetadataItem as DublinCoreMetadataItem,
)
from src.epublib.package.metadata import GenericMetadataItem as GenericMetadataItem
from src.epublib.package.metadata import LinkMetadataItem as LinkMetadataItem
from src.epublib.package.resource import PackageDocument as PackageDocument
from src.epublib.package.spine import SpineItemRef as SpineItemRef
from src.epublib.resources import ContentDocument as ContentDocument
from src.epublib.resources import PublicationResource as PublicationResource
from src.epublib.resources import Resource as Resource
from src.epublib.resources import XMLResource as XMLResource
from src.tests import Samples

book = EPUB(Samples.epub)
