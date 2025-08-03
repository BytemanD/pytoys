import dataclasses
import re
from concurrent import futures
from typing import List

from loguru import logger
from tqdm.auto import tqdm
import requests


from pytoys.common import httpclient
from . import page

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

    def __init__(self, base_url=None):
        self.client = httpclient.HttpClient(base_url or "https://www.1lou.me")

    def _get_dom(self, url: str) -> str:
        resp = self.client.get(url)
        return resp.text

    def _update_score(self, media: Media):
        try:
            resp = self.client.get(media.url)
        except (requests.Timeout, requests.HTTPError):
            logger.exception("获取评分失败(url={})", media.url)
            return
        media_page = page.MediaPage.parse_from_html(resp.text)
        media.score_imdb = media_page.score_imdb
        media.score_douban = media_page.score_douban

    def walk(self, url='/', max_page: int = 1, year: str = "", media_type: str="", name: str="",
             min_items: int=0, score=False, progress=False) -> List[page.Media]: # fmt: skip
        total_videos = []
        for _ in range(max_page):
            logger.info("查询页面: {}", url)
            resp = self.client.get(url)
            media_list_page = page.MediaListPage.parse_from_html(resp.text)
            filter_medias = []
            # TODO
            exclude_keywords=["夸克", "图书", "学习", '无字片源', "音乐"]
            for media in media_list_page.medias:
                if '音乐' in media.source:
                    continue
                if media.source in exclude_keywords or media.type in exclude_keywords:
                    continue
                if year and media.year != year:
                    continue
                # 匹配名称，忽略重复
                if (name and name not in media.name) or (media_type and media.type != media_type):
                    continue
                filter_medias.append(media)

            logger.info("找到 {} 个视频", len(filter_medias))
            total_videos.extend(filter_medias)

            if min_items and len(total_videos) >= min_items:
                break
            url = media_list_page.next_page()
            if not url:
                break

        logger.info("共找到 {} 个 视频 ...", len(total_videos))
        if score:
            logger.info("查询评分 ({}) ...", len(total_videos))
            with futures.ThreadPoolExecutor() as execotor:
                results = execotor.map(self._update_score, total_videos)
                with tqdm(total=len(total_videos), desc="查询进度", disable=not progress) as pbr:
                    for _ in results:
                        pbr.update(1)

        return total_videos

