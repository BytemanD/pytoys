import dataclasses
import re
from typing import List, Tuple
from urllib import parse

import bs4
from loguru import logger

from pytoys.common import httpclient


@dataclasses.dataclass
class Media:
    source: str = ""
    year: str = ""
    location: str = ""
    type: str = ""
    name: str = ""
    href: str = ""

    def __str__(self):
        return " - ".join(
            [
                self.year,
                self.location,
                self.type,
                self.name,
                self.href,
            ]
        )

    def get_tuple(self) -> tuple:
        return (self.source, self.year, self.location, self.type, self.name)

    @property
    def size(self) -> str:
        matched = re.findall(r"([0-9]+[0-9.]*[MG]+B*)", self.name)
        return matched[-1] if matched else ""


class Web1louMe:

    def __init__(self):
        self.client = httpclient.HttpClient("https://www.1lou.me/")

    def _get_dom(self, url: str) -> bs4.BeautifulSoup:
        resp = self.client.get(url)
        return bs4.BeautifulSoup(resp.text, "html.parser")

    def _find_all_video(self, dom: bs4.BeautifulSoup,
                        exclude_source=None,
                        year=None) -> Tuple[List[Media], str]:   # fmt: skip
        """get all videos and next page"""
        li_list = dom.find_all("li")
        videos = []
        for li in li_list:
            try:
                a_list = li.find("div").find("div").find_all("a")[:-1]
            except AttributeError:
                continue
            if len(a_list) < 6:
                continue
            # import pdb; pdb.set_trace()
            video_src = a_list[0].get_text().strip()
            video_name = a_list[-1].get_text().strip()
            viddo_href = a_list[5].get("href").strip()
            video_year = a_list[1].get_text().strip()
            if "音乐" in video_src:
                continue
            if exclude_source and any(
                iter([s in video_src or s in video_name for s in exclude_source])
            ):
                continue
            if year and video_year != year:
                continue
            videos.append(
                Media(
                    source=video_src.replace("[", "").replace("]", ""),
                    year=a_list[1].get_text().strip(),
                    location=a_list[2].get_text().strip(),
                    type=a_list[3].get_text().strip(),
                    name=video_name,
                    href=parse.urljoin(self.client.base_url, viddo_href),
                )
            )

        return (sorted(videos, key=lambda x: x.year), self._get_last_page_href(dom))

    def _get_last_page_href(self, dom: bs4.BeautifulSoup) -> str:
        a_pages = dom.find_all("a", attrs={"page-link"})
        return a_pages[-1].get("href")

    def walk(self, page_nums: int = 1, year: str = ""):
        total_videos, url = [], "/"
        for _ in range(page_nums):
            logger.info("查询页面: {}", url)
            dom = self._get_dom(url)
            videos, url = self._find_all_video(
                dom, exclude_source=["夸克", "图书", "学习"], year=year
            )
            logger.info("找到 {} 个视频", len(videos))
            total_videos.extend(videos)
        return total_videos
