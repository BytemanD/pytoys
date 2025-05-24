"""VSCode extension api from marketplace"""

import dataclasses
import json
from typing import Optional

import prettytable
from loguru import logger

from pytoys.common import httpclient, user_input


@dataclasses.dataclass
class Extension:
    """Extension object"""

    id: str
    name: str
    version: str
    display_name: str
    publisher_id: str
    publisher_name: str
    publisher_display_name: str
    flags: Optional[str] = None

    def filename(self):
        """Get file name"""
        return f"{self.publisher_name}.{self.name}-{self.version}.vsix"


class ExtensionNotFound(Exception):
    """Extension not found exception"""

    def __init__(self, name):
        super().__init__(f'extension "{name}" not found')


class MarketplaceAPI(httpclient.HttpClient):
    """Marketplace API"""

    def __init__(self):
        super().__init__("https://marketplace.visualstudio.com")

    def search(self, name):
        """Search for plugins in the marketplace"""
        data = {
            "filters": [
                {
                    "criteria": [
                        {"filterType": 8, "value": "Microsoft.VisualStudio.Code"},
                        {"filterType": 10, "value": name},
                    ],
                    "pageNumber": 1,
                    "pageSize": 50,
                    "sortBy": 0,
                    "sortOrder": 0,
                }
            ],
        }
        resp = self.post("/_apis/public/gallery/extensionquery", json=data)
        results = json.loads(resp.content).get("results")
        if len(results) < 1:
            return []

        def get_version(extension) -> str:
            for version in extension.get("versions") or []:
                if "version" in version:
                    return version.get("version")
            return ""

        extensions = results[0].get("extensions", [])
        return [
            Extension(
                id=ext.get("extensionId"),
                name=ext.get("extensionName"),
                version=get_version(ext),
                display_name=ext.get("displayName"),
                publisher_display_name=ext.get("publisher", {}).get("displayName"),
                publisher_id=ext.get("publisher", {}).get("publisherId"),
                publisher_name=ext.get("publisher", {}).get("publisherName"),
                flags=ext.get("flags", None),
            )
            for ext in extensions
        ]

    def download_extension(self, ext: Extension, output: Optional[str] = None):
        """Download extension from marketplace"""
        logger.info("download extension: {}({})", ext.display_name, ext.name)
        url = (
            f"/_apis/public/gallery/publishers/{ext.publisher_name}/"
            f"vsextensions/{ext.name}/{ext.version}/vspackage"
        )

        self.download(
            url, default_filename=ext.filename(), progress=True, output=output
        )
        logger.success("download success")

    def search_and_download(self, name, output: Optional[str] = None):
        """Search and download extension"""
        logger.info("search extension: {}", name)
        items = self.search(name)
        if not items:
            raise ExtensionNotFound(name)

        def prerender(dt: prettytable.PrettyTable):
            dt.max_width.update({"插件": 40})
            dt.align.update({"插件": "l", "发布者": "l", "版本": "l", "标签": "l"})

        item = user_input.select_items(
            [dataclasses.asdict(item) for item in items],
            ["display_name", "publisher_display_name", "version", "flags"],
            title={
                "display_name": "插件",
                "publisher_display_name": "发布者",
                "version": "版本",
                "flags": "标签",
            },
            select_msg="查询结果:",
            prerender=prerender,
        )
        if not item:
            return
        self.download_extension(Extension(**item), output=output)
