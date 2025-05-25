import dataclasses
from datetime import datetime
from typing import List, Optional
from urllib import parse

from pytoys.common import httpclient


@dataclasses.dataclass
class BingImage:
    title: str
    caption: str
    subtitle: str
    description: str
    bing_url: str
    url: str
    date: str

    def filename(self) -> str:
        parsed = parse.urlparse(self.bing_url)
        image_id = parse.parse_qs(parsed.query).get("id")
        return image_id[0] if image_id else ""


class BingNpanuhinAPI(httpclient.HttpClient):
    """
    https://bing.npanuhin.me/
    """

    def __init__(self):
        super().__init__("https://bing.npanuhin.me", timeout=30)

    def get_bing_images(self, country: str='CN', language: str='zh',
                        date: Optional[str]=None) -> List[BingImage]:        # fmt: skip
        if date:
            year = date.split("-")[0]
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        year = date.split("-")[0]
        resp = self.get(f"/{country}/{language}.{year}.json")
        return [
            BingImage(
                title=data.get("title"),
                caption=data.get("caption"),
                subtitle=data.get("subtitle"),
                description=data.get("description"),
                bing_url=data.get("bing_url"),
                url=data.get("url"),
                date=data.get("date"),
            )
            for data in resp.json()
            if data.get("date", "").startswith(date)
        ]

    def download_image(self, image: BingImage, progress=False):
        self.download(image.bing_url, default_filename=image.filename(), progress=progress)
