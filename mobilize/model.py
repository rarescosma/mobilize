from io import BytesIO
from pathlib import Path
from typing import NamedTuple, NotRequired, TypedDict

from PIL import Image as PImage


class Article(TypedDict, total=False):
    """Holds an article."""

    content: str
    url: str
    byline: str
    siteName: str
    title: str
    lang: NotRequired[str]


class Image(NamedTuple):
    """Holds an image."""

    file_name: str
    content: bytes

    def webp_to_jpg(self) -> "Image":
        """Use Pillow to convert ourselves to a JPEG."""
        out = BytesIO()

        jpg_img = PImage.open(BytesIO(self.content)).convert("RGB")
        jpg_img.save(out, format="JPEG")
        file_name = Path(self.file_name).with_suffix(".jpg")

        return Image(file_name=str(file_name), content=out.getvalue())
