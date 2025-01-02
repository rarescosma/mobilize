import re
import textwrap
import unicodedata
from copy import deepcopy
from datetime import datetime
from urllib import parse

from bs4 import BeautifulSoup

from .model import Article

NOW: datetime = datetime.now()


def container_xml() -> str:
    """Just epub things."""
    return textwrap.dedent(
        """
        <?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
        </container>""",
    ).strip()


def content_opf(article: Article) -> str:
    """Just more epub things."""
    return textwrap.dedent(
        f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="3.0" xml:lang="en" unique-identifier="uid" prefix="cc: http://creativecommons.org/ns#">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title id="title">{_short_date()}: {article['title']}</dc:title>
                <dc:creator>{_extract_author(article)}</dc:creator>
                <dc:language>{article.get('lang', '')}</dc:language>
            </metadata>
            <manifest>
                <item id="article" href="article.html" media-type="text/html" />
            </manifest>
            <spine toc="ncx">
                <itemref idref="article" />
            </spine>
        </package>"""
    ).strip()


def make_filename(article: Article) -> str:
    """
    We prefer articles prepended with a short date
    to make them easily distinguishable from actual books on the device.
    """
    return f"{_short_date()}_{_slugify(article['title'])}"


def prepend_metadata(article: Article, url: str, mobi_file: str) -> Article:
    """Prepend a paragraph with metadata to the article. It's nice."""
    soup = BeautifulSoup(article["content"], "lxml")

    first_div = soup.find("div")
    if not first_div:
        return article

    # URL
    b = soup.new_tag("b")
    b.string = "Source: "
    a = soup.new_tag("a", href=url, target="_blank")
    a.string = url

    p = soup.new_tag("p")
    p.append(b)
    p.append(a)

    first_div.insert(0, p)

    # Mobi file
    b, s = soup.new_tag("b"), soup.new_string(mobi_file)
    b.string = "File: "

    p = soup.new_tag("p")
    p.append(b)
    p.append(s)

    first_div.insert(0, p)

    ret = deepcopy(article)
    ret["content"] = str(soup)
    return ret


def _extract_author(article: Article) -> str:
    """If no explicit author in the website, use the domain."""
    ret = article["byline"] or article["siteName"]
    if not ret:
        ret = parse.urlparse(article["url"]).netloc.replace("www.", "")
    return ret


def _slugify(value: str) -> str:
    """
    Shamelessly stolen from the Django source code.

    Source: https://github.com/django/django/blob/stable/5.1.x/django/utils/text.py#L452
    """
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def _short_date(dt: datetime = NOW) -> str:
    """
    Someone might get a time machine and run this from the 90's
    or worse still - this code might make the millennium.
    """
    year = dt.strftime("%Y")
    return dt.strftime("%Y%m%d").removeprefix(year[:2])
