import dataclasses
import re
from typing import List

import bs4


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


@dataclasses.dataclass
class Pagination:
    href: str
    page: str
    active: bool = False


class MediaListPage:

    def __init__(self):
        self.paginations: List[Pagination] = []
        self.medias: List[Media] = []

    def next_page(self) -> str:
        active_index = 0
        for index, page in enumerate(self.paginations):
            if page.active:
                active_index = index
                break
        return self.paginations[active_index + 1].href

    @classmethod
    def parse_from_html(cls, html: str) -> "MediaListPage":
        page = MediaListPage()
        dom = bs4.BeautifulSoup(html, "html.parser")
        
        # find all paginations
        for a_page in dom.find_all("a", attrs={"class": "page-link"}) or []:
            page.paginations.append(
                Pagination(
                    href=a_page.get("href"),
                    page=a_page.get_text(),
                    active="active" in a_page.get("class", []),
                )
            )
        # find all medias
        li_list = dom.find_all("li", attrs={'class': 'media'})
        videos = []
        for li in li_list:
            if len(li.find('div', attrs={'class': 'subject'}).find_all('a')) <= 4:
                continue

            a_list = li.find_all("a")[:-1]
            if not a_list:
                continue
            if a_list[0].get('title') in ['站务专区', '图书专区']:
                continue
            if len(a_list) < 6:
                continue
            page.medias.append(
                Media(
                    source=a_list[0].get_text().strip().replace("[", "").replace("]", ""),
                    year=a_list[1].get_text().strip(),
                    location=a_list[2].get_text().strip(),
                    type=a_list[3].get_text().strip(),
                    name=a_list[-1].get_text().strip(),
                    url=a_list[5].get("href").strip(),
                )
            )
        return page


class MediaPage:

    def __init__(self):
        self.score_imdb: str = ''
        self.score_douban: str = ''

    @classmethod
    def parse_from_html(cls, html: str) -> "MediaPage":
        page = MediaPage()
        dom = bs4.BeautifulSoup(html, "html.parser")
        matched_imdb = re.findall(r"IMDb评分.{0,1}([0-9./]+)", dom.text)
        if matched_imdb:
            page.score_imdb = matched_imdb[0]
        matched_douban = re.findall(r"豆瓣评分.{0,1}([0-9./]+)", dom.text)
        if matched_douban:
            page.score_douban = matched_douban[0] if matched_douban else ""

        return page
