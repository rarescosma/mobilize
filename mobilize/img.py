from copy import deepcopy
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from typing import Iterable, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from .model import Article, Image

LAZY_DATA_ATTRS: list[str] = [
    "data-src",
    "data-lazy-src",
    "data-srcset",
    "data-td-src-property",
]


def process_images(article: Article) -> Tuple[Article, Iterable[Image]]:
    """
    Will attempt to download all the images found in the article and
    also change the image tags to point to the local copies, so they
    make sense when we produce the zip (epub) file later.

    Downloading is parallel.
    """

    soup = BeautifulSoup(article["content"], "lxml")
    for data_attr in LAZY_DATA_ATTRS:
        for img in soup.findAll("img", attrs={data_attr: True}):
            img.attrs = {"src": img[data_attr]}

    image_refs = []
    for img in soup.findAll("img"):
        image_refs.append(img)

    with Pool(processes=cpu_count()) as p:
        processed = p.map(_process_image, (i["src"] for i in image_refs))

    for ref, image in zip(image_refs, processed):
        if image is not None:
            ref["src"] = image.file_name

    # mutating the input is not nice
    ret = deepcopy(article)
    ret["content"] = str(soup)
    return ret, filter(None, processed)


def _process_image(url: str) -> Optional[Image]:
    img_filename = "article_files/" + url.split("/")[-1].split("?")[0]
    response = requests.get(url, timeout=10)

    if not response.ok:
        return None

    _img = Image(file_name=img_filename, content=response.content)
    return _img.webp_to_jpg() if _img.file_name.lower().endswith(".webp") else _img
