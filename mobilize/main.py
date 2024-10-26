#!/usr/bin/env -S /bin/sh -c 'exec "$(dirname $(readlink -f "$0"))/../../.venv/bin/python3" "$0" "$@"'
"""
Workflow borrowed from: https://olano.dev/blog/from-rss-to-my-kindle/
"""
import json
import os
import sys
import traceback
import zipfile
from io import BytesIO
from json import JSONDecodeError
from multiprocessing.dummy import Pool
from os import cpu_count
from pathlib import Path
from subprocess import CalledProcessError, check_output, run
from typing import Iterable, Optional

from .cli import Opts
from .img import process_images
from .model import Article, Image
from .tpl import container_xml, content_opf, make_filename, prepend_source_url

DOT: str = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))


def extract_article(url: str) -> Optional[Article]:
    try:
        out = run(
            [f"{DOT}/../extract_article.js", url],
            env={"NODE_NO_WARNINGS": "1"},
            capture_output=True,
        )
    except CalledProcessError as e:
        print(f"could not extract article, url={url}", e.returncode, e.output, e.stderr)
        return None

    try:
        parsed = json.loads(out.stdout)
        parsed["url"] = url
    except JSONDecodeError as e:
        print(
            f"could not parse extract_article JSON err={e!r}, "
            f"out={out.stdout!r}, err={out.stderr!r}"
        )
        return None

    return parsed


def package_epub(article: Article, images: Iterable[Image]) -> bytes:
    output_buffer = BytesIO()

    with zipfile.ZipFile(output_buffer, "w", compression=zipfile.ZIP_DEFLATED) as _zip:
        _zip.writestr("mimetype", "application/epub+zip")
        _zip.writestr("META-INF/container.xml", container_xml())
        _zip.writestr("content.opf", content_opf(article))
        _zip.writestr("article.html", article["content"])
        for image in images:
            _zip.writestr(image.file_name, image.content)

    return output_buffer.getvalue()


def convert_to_mobi(epub_f: Path, mobi_f: Path) -> bool:
    try:
        check_output(["ebook-convert", str(epub_f), str(mobi_f)], env={"PYTHONPATH": ""})
    except CalledProcessError:
        return False
    return True


def main() -> int:
    opts = Opts.from_args(sys.argv[1:])

    epub_dir, mobi_dir = (opts.out_dir / "epub"), (opts.out_dir / "mobi")
    epub_dir.mkdir(parents=True, exist_ok=True)
    mobi_dir.mkdir(parents=True, exist_ok=True)

    # noinspection PyBroadException
    def process_article(_article_url: str) -> None:
        article = extract_article(_article_url)
        if article is None:
            print(f"failed article extraction, url={_article_url}")
            return

        try:
            article = prepend_source_url(article, _article_url)
            article, images = process_images(article)

            epub_f = epub_dir / f"{make_filename(article)}.epub"
            epub_f.write_bytes(package_epub(article, images))
            print(f"done url={_article_url}, epub={epub_f.absolute()}")

            mobi_f = mobi_dir / epub_f.with_suffix(".mobi").name
            if convert_to_mobi(epub_f, mobi_f):
                print(f"done url={_article_url}, mobi={mobi_f.absolute()}")
            else:
                print(f"failed mobi conversion, url={_article_url}")
        except Exception:
            print(f"general failure, url={_article_url}, err={traceback.format_exc()}")

    with Pool(processes=cpu_count()) as p:
        _ = p.map(process_article, opts.urls)

    print("all done")
    return 0


if __name__ == "__main__":
    main()
