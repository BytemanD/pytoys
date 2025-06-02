import dataclasses
import re
from concurrent import futures
from typing import List, Optional, Tuple
from urllib import parse

import bs4
import requests
from loguru import logger
from tqdm.auto import tqdm

from pytoys.common import httpclient


@dataclasses.dataclass
class Media:
    source: str = ""
    year: str = ""
    location: str = ""
    type: str = ""
    name: str = ""
    url: str = ""
    score_imdb: str = ""
    score_douban: str = ""

    def __str__(self):
        return " - ".join([self.year, self.location, self.type, self.name, self.url])

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

    def _find_all_video(self, dom: bs4.BeautifulSoup, exclude_keywords=None, year:str='',
                        name:str ="") -> Tuple[List[Media], str]:                       # fmt: skip
        """get all videos and next page"""
        li_list = dom.find_all("li")
        videos, video_names = [], []
        for li in li_list:
            try:
                a_list = li.find("div").find("div").find_all("a")[:-1]
            except AttributeError:
                continue
            if len(a_list) < 6:
                continue
            video_src = a_list[0].get_text().strip()
            video_year = a_list[1].get_text().strip()
            video_name = a_list[-1].get_text().strip()
            video_type = a_list[3].get_text().strip()
            if "音乐" in video_src:
                continue
            if exclude_keywords and any(
                iter(
                    [s in video_src or s in video_name or s in video_type for s in exclude_keywords]
                )
            ):
                continue
            if year and video_year != year:
                continue
            # 匹配名称，忽略重复
            if (name and name not in video_name) or (video_name in video_names):
                continue
            # 去除 name 内容部分内容
            for s in ["[BT下载]"]:
                video_name = video_name.replace(s, "")
            videos.append(
                Media(
                    source=video_src.replace("[", "").replace("]", ""),
                    year=a_list[1].get_text().strip(),
                    location=a_list[2].get_text().strip(),
                    type=a_list[3].get_text().strip(),
                    name=video_name,
                    url=parse.urljoin(self.client.base_url, a_list[5].get("href").strip()),
                )
            )
            video_names.append(video_name)

        return (sorted(videos, key=lambda x: x.year), self._get_last_page_href(dom))

    def _get_last_page_href(self, dom: bs4.BeautifulSoup) -> str:
        a_pages = dom.find_all("a", attrs={"page-link"})
        return a_pages[-1].get("href")

    def _get_score(self, media: Media) -> Tuple[str, str]:
        try:
            dom_txt = self._get_dom(media.url).text
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError):
            logger.exception("获取评分失败(url={})", media.url)
            return ("-", "-")

        score_imdb, score_douban = "", ""
        matched = re.findall(r"IMDb评分.{0,1}([0-9./]+)", dom_txt)
        score_imdb = matched[0] if matched else "-"
        matched = re.findall(r"豆瓣评分.{0,1}([0-9./]+)", dom_txt)
        score_douban = matched[0] if matched else "-"
        logger.debug("media {} score: imdb={}, douban={}", media.name, 0, 0)
        return (score_imdb or "-", score_douban or "-")

    def walk(self, max_page: int = 1, year: str = "", name: str="", min_items: Optional[int] = None,
             score=False, progress=False, exclude_keywords=None): # fmt: skip
        total_videos, url = [], "/"
        for _ in range(max_page):
            logger.info("查询页面: {}", url)
            videos, url = self._find_all_video(
                self._get_dom(url), exclude_keywords=exclude_keywords or [],
                year=year, name=name)                                                   # fmt: skip
            logger.info("找到 {} 个视频", len(videos))
            total_videos.extend(videos)
            if min_items and len(total_videos) >= min_items:
                break
        logger.info("共找到 {} 个 视频 ...", len(total_videos))
        if score:
            logger.info("查询评分 ({}) ...", len(total_videos))

            def _update_score(media: Media):
                media.score_imdb, media.score_douban = self._get_score(media)

            with futures.ThreadPoolExecutor() as execotor:
                results = execotor.map(_update_score, total_videos)
                with tqdm(total=len(total_videos), desc="查询进度", disable=not progress) as pbr:
                    for _ in results:
                        pbr.update(1)

        return total_videos
